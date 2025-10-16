package com.intamia.sos

import androidx.compose.animation.animateColorAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

@Composable
fun SOSButton(
    logs: List<String>,
    onTap: () -> Unit
) {
    var isBusy by remember { mutableStateOf(false) }
    var status by remember { mutableStateOf("Tap SOS") }
    val background by animateColorAsState(
        targetValue = if (isBusy) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error,
        label = "sos-color"
    )

    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Box(
            modifier = Modifier
                .size(220.dp)
                .clip(CircleShape)
                .background(background)
                .padding(16.dp),
            contentAlignment = Alignment.Center
        ) {
            Button(
                onClick = {
                    isBusy = true
                    status = "Connecting…"
                    onTap()
                    isBusy = false
                    status = "Tap SOS"
                },
                colors = ButtonDefaults.buttonColors(
                    containerColor = Color.Transparent,
                    contentColor = Color.White
                ),
                elevation = ButtonDefaults.buttonElevation(defaultElevation = 0.dp),
                modifier = Modifier.fillMaxSize()
            ) {
                Text(text = "SOS", fontWeight = FontWeight.Bold, style = MaterialTheme.typography.headlineLarge)
            }
        }

        Spacer(modifier = Modifier.height(24.dp))
        Text(text = status, style = MaterialTheme.typography.bodyLarge)

        if (logs.isNotEmpty()) {
            Spacer(modifier = Modifier.height(24.dp))
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 32.dp)
            ) {
                logs.takeLast(4).reversed().forEach { line ->
                    Text(text = line, style = MaterialTheme.typography.bodySmall)
                }
            }
        }
    }
}
