package com.intamia.sos

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.core.content.ContextCompat
import com.intamia.sos.TokenStore
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {

    private val permissions = arrayOf(
        Manifest.permission.RECORD_AUDIO,
        Manifest.permission.ACCESS_WIFI_STATE,
        Manifest.permission.ACCESS_NETWORK_STATE
    )

    private val permissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) { _ -> }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        maybeRequestPermissions()
        if (TokenStore.token.isNullOrBlank()) {
            println("⚠️  No authentication token configured. Set via TokenStore.token or UI before connecting.")
        }

        setContent {
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
                    val logLines = remember { mutableStateListOf<String>() }
                    val scope = remember { CoroutineScope(Dispatchers.Main) }
                    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        SOSButton(
                            logs = logLines,
                            onTap = {
                                scope.launch {
                                    OrchestratorClient.handleUserTap(logLines)
                                }
                            }
                        )
                    }
                }
            }
        }
    }

    private fun maybeRequestPermissions() {
        val missing = permissions.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        if (missing.isNotEmpty()) {
            permissionLauncher.launch(missing.toTypedArray())
        }
    }
}
