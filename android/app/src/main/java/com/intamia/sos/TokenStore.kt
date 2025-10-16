package com.intamia.sos

import android.content.Context
import android.content.SharedPreferences

object TokenStore {
    private const val PREFS_NAME = "sos_prefs"
    private const val KEY_TOKEN = "auth_token"
    private const val KEY_BASE_URL = "base_url"
    private val prefs: SharedPreferences by lazy {
        OrchestratorAppContext.get().getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    }

    var token: String?
        get() = prefs.getString(KEY_TOKEN, null)
        set(value) {
            prefs.edit().putString(KEY_TOKEN, value).apply()
        }

    var baseUrl: String
        get() = prefs.getString(KEY_BASE_URL, "https://10.0.0.2:8000") ?: "https://10.0.0.2:8000"
        set(value) {
            prefs.edit().putString(KEY_BASE_URL, value).apply()
        }
}
