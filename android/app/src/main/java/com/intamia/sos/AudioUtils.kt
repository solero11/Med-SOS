package com.intamia.sos

import android.media.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream
import java.nio.ByteBuffer
import kotlin.math.min

/**
 * Simple utilities to capture microphone audio to WAV and play orchestral TTS replies.
 * The implementations favour clarity over efficiency since this is a reference build.
 */
object AudioUtils {
    private const val SAMPLE_RATE = 16_000
    private const val CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO
    private const val ENCODING = AudioFormat.ENCODING_PCM_16BIT

    suspend fun captureWavFile(seconds: Int): File = withContext(Dispatchers.IO) {
        val bufferSize = AudioRecord.getMinBufferSize(SAMPLE_RATE, CHANNEL_CONFIG, ENCODING)
        val recorder = AudioRecord(MediaRecorder.AudioSource.MIC, SAMPLE_RATE, CHANNEL_CONFIG, ENCODING, bufferSize)
        val pcmData = ByteArray(bufferSize)
        val totalBytes = SAMPLE_RATE * 2 * seconds
        val output = File.createTempFile("sos_capture_", ".pcm")

        recorder.startRecording()
        FileOutputStream(output).use { fos ->
            var recorded = 0
            while (recorded < totalBytes) {
                val read = recorder.read(pcmData, 0, min(pcmData.size, totalBytes - recorded))
                if (read > 0) {
                    fos.write(pcmData, 0, read)
                    recorded += read
                }
            }
        }
        recorder.stop()
        recorder.release()

        // Convert PCM -> WAV
        val wavFile = File(output.parentFile, output.nameWithoutExtension + ".wav")
        pcmToWav(output, wavFile, recordedBytes = totalBytes)
        output.delete()
        return@withContext wavFile
    }

    private fun pcmToWav(pcmFile: File, wavFile: File, recordedBytes: Int) {
        val totalDataLen = recordedBytes + 36
        val totalAudioLen = recordedBytes
        val byteRate = SAMPLE_RATE * 2

        FileOutputStream(wavFile).use { out ->
            val header = ByteBuffer.allocate(44)
            header.put("RIFF".toByteArray())
            header.putInt(totalDataLen)
            header.put("WAVE".toByteArray())
            header.put("fmt ".toByteArray())
            header.putInt(16)
            header.putShort(1)
            header.putShort(1)
            header.putInt(SAMPLE_RATE)
            header.putInt(byteRate)
            header.putShort(2)
            header.putShort(16)
            header.put("data".toByteArray())
            header.putInt(totalAudioLen)
            out.write(header.array())
            pcmFile.inputStream().use { input -> input.copyTo(out) }
        }
    }

    fun playFromReply(payload: JSONObject) {
        val ttsUrl = payload.optString("audio_url", payload.optString("tts_url", ""))
        if (ttsUrl.isBlank()) return

        // TODO: Download WAV and play through AudioTrack
        println("Received TTS URL: $ttsUrl (download & playback not implemented in stub)")
    }
}
