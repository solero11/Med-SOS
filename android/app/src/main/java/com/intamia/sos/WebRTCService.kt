package com.intamia.sos

import java.net.InetSocketAddress
import javax.jmdns.JmDNS
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.webrtc.PeerConnectionFactory

/**
 * Placeholder WebRTC implementation.
 *
 * The full SDP/ICE negotiation is outside the scope of this increment.
 * This stub checks that the WebRTC libraries are present and gives a hook
 * for future signalling against the orchestrator's /webrtc endpoints.
 */
object WebRTCService {
    private var factory: PeerConnectionFactory? = null

    fun isSupported(): Boolean = try {
        PeerConnectionFactory.initialize(
            PeerConnectionFactory.InitializationOptions.builder(OrchestratorAppContext.get())
                .createInitializationOptions()
        )
        factory = PeerConnectionFactory.builder().createPeerConnectionFactory()
        true
    } catch (ex: Throwable) {
        false
    }

    fun discoverOrchestrator(): InetSocketAddress? {
        return try {
            val jmDns = JmDNS.create()
            val service = jmDns.list("_sos._tcp.local.").firstOrNull()
            jmDns.close()
            service?.let { srv ->
                val address = srv.inetAddresses.firstOrNull() ?: return null
                InetSocketAddress(address, srv.port)
            }
        } catch (ex: Exception) {
            null
        }
    }

    suspend fun start(baseUrl: String) = withContext(Dispatchers.IO) {
        // TODO: Implement signalling with orchestrator /webrtc endpoints.
        println("WebRTC session requested at $baseUrl (not yet implemented)")
    }
}
