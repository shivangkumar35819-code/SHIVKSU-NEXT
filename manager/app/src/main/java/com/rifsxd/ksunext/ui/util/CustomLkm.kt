package com.rifsxd.ksunext.ui.util

import android.os.Build
import com.rifsxd.ksunext.ksuApp
import java.io.File

/** Drivers built to trust this manager's signing certificate. */
internal object CustomLkm {
    private const val ROOT = "custom-lkm"
    private const val SUFFIX = "_kernelsu.ko"

    private fun directory() = "$ROOT/${Build.SUPPORTED_ABIS.firstOrNull().orEmpty()}"

    fun isConfigured(): Boolean = !ksuApp.assets.list(ROOT).isNullOrEmpty()

    fun supportedKmis(): List<String> = ksuApp.assets.list(directory()).orEmpty()
        .filter { it.endsWith(SUFFIX) }
        .map { it.removeSuffix(SUFFIX) }
        .sorted()

    fun extract(kmi: String): File {
        require(kmi in supportedKmis()) { "No matching SHIVKSU-NEXT driver for $kmi" }
        val file = File.createTempFile("shivksu-lkm-", ".ko", ksuApp.cacheDir)
        try {
            ksuApp.assets.open("${directory()}/$kmi$SUFFIX").use { input ->
                file.outputStream().use { output -> input.copyTo(output) }
            }
            return file
        } catch (error: Exception) {
            file.delete()
            throw error
        }
    }
}
