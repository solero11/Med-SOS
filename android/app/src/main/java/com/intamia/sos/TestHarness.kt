package com.intamia.sos

import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking
import kotlin.math.roundToInt
import kotlin.system.measureTimeMillis

/**
 * Simple latency harness that invokes the fallback HTTP upload several times.
 * Developers can run this from an Android instrumentation test or debug button.
 */
object TestHarness {
    fun runStressTest(iterations: Int = 6) = runBlocking {
        val latencies = mutableListOf<Long>()
        repeat(iterations) {
            val elapsed = measureTimeMillis {
                OrchestratorClient.handleUserTap(mutableListOf())
            }
            latencies += elapsed
            delay(400)
        }
        if (latencies.isNotEmpty()) {
            val mean = latencies.average()
            val p95Index = ((latencies.size - 1) * 0.95).roundToInt().coerceAtMost(latencies.size - 1)
            val p95 = latencies.sorted()[p95Index]
            println("Android stress mean=${mean / 1000.0}s p95=${p95 / 1000.0}s")
        }
    }
}
