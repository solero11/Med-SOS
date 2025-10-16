package com.intamia.sos

import android.content.Context
import com.intamia.sos.BuildConfig
import android.net.Uri
import androidx.core.content.FileProvider
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.asRequestBody
import org.json.JSONObject
import java.io.File
import java.net.HttpURLConnection
import java.net.InetSocketAddress
import java.net.URL
import java.security.MessageDigest
import java.util.concurrent.TimeUnit
import javax.net.ssl.HttpsURLConnection

/**
 * Minimal client that reaches out to the Windows orchestrator.
 *
 * Preferred transport is HTTPS with bearer token authentication. WebRTC hooks are left
 * as future work; until then we fall back to a synchronous WAV upload.
 */
object OrchestratorClient {
    private val trustManager = SSLUtils.trustAllManager()
    private val http = OkHttpClient.Builder()
        .connectTimeout(5, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .sslSocketFactory(SSLUtils.trustAllFactory(), trustManager)
        .hostnameVerifier { _, _ -> true }
        .build()

    private const val HEALTH_PATH = "/health"
    private const val TURN_PATH = "/turn"
    private const val MANIFEST_PATH = "/updates/manifest.json"

    private fun baseUrl(): String = TokenStore.baseUrl.trimEnd('/')
    private fun buildUrl(path: String) = baseUrl() + path

    fun updateConfiguration(url: String?, token: String?) {
        url?.let { TokenStore.baseUrl = it }
        token?.let { TokenStore.token = it }
    }

    suspend fun handleUserTap(logs: MutableList<String>) = withContext(Dispatchers.IO) {
        WebRTCService.discoverOrchestrator()?.let { endpoint: InetSocketAddress ->
            TokenStore.baseUrl = "https://${endpoint.hostString}:${endpoint.port}"
        }
        val healthUrl = buildUrl(HEALTH_PATH)
        logs += "Checking orchestrator health…"
        if (!connectSecurely(healthUrl)) {
            logs += "❌ Unable to reach orchestrator at $healthUrl"
            return@withContext
        }
        logs += "✅ Orchestrator reachable"

        if (WebRTCService.isSupported()) {
            logs += "Starting WebRTC session…"
            WebRTCService.start(baseUrl())
        } else {
            logs += "WebRTC unavailable. Capturing WAV fallback…"
            val wavFile = AudioUtils.captureWavFile(seconds = 5)
            logs += "Uploading ${wavFile.name}…"
            val response = sendWav(buildUrl(TURN_PATH), wavFile)
            logs += "Reply: ${response.take(96)}"
        }
    }

    suspend fun checkForAndroidUpdate(manifestUrl: String = buildUrl(MANIFEST_PATH)): AndroidUpdateInfo? =
        withContext(Dispatchers.IO) {
            return@withContext try {
                val request = Request.Builder()
                    .url(manifestUrl)
                    .get()
                    .build()
                http.newCall(request).execute().use { response ->
                    if (!response.isSuccessful) return@use null
                    val body = response.body?.string().orEmpty()
                    val json = JSONObject(body)
                    val info = json.optJSONObject("android") ?: return@use null
                    val remoteCode = info.optInt("versionCode", 0)
                    if (remoteCode <= BuildConfig.VERSION_CODE) {
                        return@use null
                    }
                    AndroidUpdateInfo(
                        versionCode = remoteCode,
                        versionName = info.optString("versionName", remoteCode.toString()),
                        downloadUrl = info.optString("download_url"),
                        sha256 = info.optString("sha256"),
                        notes = info.optString("notes")
                    )
                }
            } catch (e: Exception) {
                null
            }
        }

    suspend fun downloadAndroidUpdate(info: AndroidUpdateInfo): File = withContext(Dispatchers.IO) {
        val dir = OrchestratorAppContext.get().getExternalFilesDir("updates")
            ?: OrchestratorAppContext.get().filesDir
        val target = File(dir, "SOS_${info.versionName}.apk")
        val request = Request.Builder().url(info.downloadUrl).get().build()
        http.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                throw IllegalStateException("Download failed: ${response.code}")
            }
            response.body?.byteStream().use { stream ->
                target.outputStream().use { out ->
                    stream?.copyTo(out)
                }
            }
        }
        if (info.sha256.isNotBlank()) {
            val hash = sha256(target)
            if (!hash.equals(info.sha256, ignoreCase = true)) {
                target.delete()
                throw IllegalStateException("APK hash mismatch")
            }
        }
        return@withContext target
    }

    fun promptInstall(context: Context, apk: File) {
        val authority = "${BuildConfig.APPLICATION_ID}.fileprovider"
        val uri: Uri = FileProvider.getUriForFile(context, authority, apk)
        val intent = Intent(Intent.ACTION_VIEW).apply {
            setDataAndType(uri, "application/vnd.android.package-archive")
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_GRANT_READ_URI_PERMISSION
        }
        context.startActivity(intent)
    }

    private fun sha256(file: File): String {
        val digest = MessageDigest.getInstance("SHA-256")
        file.inputStream().use { input ->
            val buffer = ByteArray(1 shl 16)
            var read: Int
            while (input.read(buffer).also { read = it } != -1) {
                digest.update(buffer, 0, read)
            }
        }
        return digest.digest().joinToString("") { "%02x".format(it) }
    }

    private suspend fun connectSecurely(url: String): Boolean = withContext(Dispatchers.IO) {
        return@withContext try {
            val urlObj = URL(url)
            val connection = when (urlObj.protocol.lowercase()) {
                "https" -> {
                    (urlObj.openConnection() as HttpsURLConnection).apply {
                        sslSocketFactory = SSLUtils.trustAllFactory()
                        hostnameVerifier = { _, _ -> true }
                    }
                }
                else -> urlObj.openConnection() as HttpURLConnection
            }
            TokenStore.token?.let { connection.setRequestProperty("Authorization", "Bearer $it") }
            connection.connectTimeout = 2000
            connection.readTimeout = 2000
            connection.inputStream.use { }
            connection.disconnect()
            true
        } catch (e: Exception) {
            false
        }
    }

    private suspend fun sendWav(url: String, wavFile: File): String = withContext(Dispatchers.IO) {
        val body = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart(
                name = "audio",
                filename = wavFile.name,
                body = wavFile.asRequestBody("audio/wav".toMediaType())
            )
            .build()

        val requestBuilder = Request.Builder()
            .url(url)
            .post(body)
        TokenStore.token?.let { requestBuilder.addHeader("Authorization", "Bearer $it") }

        http.newCall(requestBuilder.build()).execute().use { response ->
            if (!response.isSuccessful) {
                throw IllegalStateException("turn() failed: ${response.code}")
            }
            val payload = response.body?.string().orEmpty()
            AudioUtils.playFromReply(JSONObject(payload))
            payload
        }
    }
}

data class AndroidUpdateInfo(
    val versionCode: Int,
    val versionName: String,
    val downloadUrl: String,
    val sha256: String,
    val notes: String?
)
