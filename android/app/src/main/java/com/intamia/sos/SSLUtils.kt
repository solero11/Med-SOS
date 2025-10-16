package com.intamia.sos

import java.security.SecureRandom
import javax.net.ssl.*

object SSLUtils {
    fun trustAllManager(): X509TrustManager {
        return object : X509TrustManager {
            override fun checkClientTrusted(chain: Array<java.security.cert.X509Certificate>, authType: String) {}
            override fun checkServerTrusted(chain: Array<java.security.cert.X509Certificate>, authType: String) {}
            override fun getAcceptedIssuers(): Array<java.security.cert.X509Certificate> = arrayOf()
        }
    }

    fun trustAllFactory(): SSLSocketFactory {
        val context = SSLContext.getInstance("TLS")
        val manager = trustAllManager()
        context.init(null, arrayOf<TrustManager>(manager), SecureRandom())
        return context.socketFactory
    }
}
