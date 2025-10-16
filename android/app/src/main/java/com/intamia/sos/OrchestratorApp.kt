package com.intamia.sos

import android.app.Application
import android.content.Context
import java.lang.ref.WeakReference

class OrchestratorApp : Application() {
    override fun onCreate() {
        super.onCreate()
        OrchestratorAppContext.init(this)
    }
}

object OrchestratorAppContext {
    private var reference: WeakReference<Context>? = null

    fun init(ctx: Context) {
        reference = WeakReference(ctx.applicationContext)
    }

    fun get(): Context {
        return reference?.get()
            ?: throw IllegalStateException("Application context not initialised.")
    }
}
