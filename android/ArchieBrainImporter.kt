package com.bulldawg.ai.importer

import android.content.Context
import android.net.Uri
import java.io.File
import java.io.FileOutputStream
import java.security.MessageDigest
import java.util.UUID
import java.util.zip.ZipInputStream

/**
 * Stages a selected Archie brain ZIP in app-private storage.
 * Does not execute code, replace memory, or activate a model.
 * Call from a background thread after ACTION_OPEN_DOCUMENT.
 */
object ArchieBrainImporter {
    data class Result(val directory: File, val files: Int, val bytes: Long)
    private const val MAX_ZIP_BYTES = 100L * 1024 * 1024
    private const val MAX_UNPACKED_BYTES = 200L * 1024 * 1024
    private const val MAX_FILES = 1000

    fun stage(context: Context, uri: Uri): Result {
        val root = File(context.filesDir, "brain-imports").apply { mkdirs() }
        val staging = File(root, "pending-" + UUID.randomUUID())
        check(staging.mkdir()) { "Unable to create staging directory" }
        var total = 0L
        var compressed = 0L
        var count = 0
        val names = HashSet<String>()
        try {
            val stream = context.contentResolver.openInputStream(uri)
                ?: error("Cannot open selected file")
            stream.use { input ->
                // Count compressed bytes as they are consumed, including headers.
                val limited = object : java.io.FilterInputStream(input) {
                    override fun read(): Int {
                        val b = super.read()
                        if (b != -1 && ++compressed > MAX_ZIP_BYTES) error("ZIP too large")
                        return b
                    }
                    override fun read(b: ByteArray, off: Int, len: Int): Int {
                        val n = super.read(b, off, len)
                        if (n > 0) {
                            compressed += n
                            if (compressed > MAX_ZIP_BYTES) error("ZIP too large")
                        }
                        return n
                    }
                }
                ZipInputStream(limited).use { zip ->
                    val buffer = ByteArray(8192)
                    while (true) {
                        val entry = zip.nextEntry ?: break
                        val name = entry.name.replace('\\', '/')
                        require(name.isNotBlank() && !name.startsWith("/") &&
                            !name.split('/').contains("..") && !name.contains(':') &&
                            !name.contains('\u0000')) { "Unsafe ZIP entry" }
                        require(names.add(name)) { "Duplicate ZIP entry" }
                        if (entry.isDirectory) { zip.closeEntry(); continue }
                        require(++count <= MAX_FILES) { "Too many files" }
                        // Brain packages are data only; never import executable files.
                        val extension = name.substringAfterLast('.', "").lowercase()
                        require(extension in setOf("json", "txt", "md", "csv")) {
                            "Unsupported brain file: $name"
                        }
                        val target = File(staging, name)
                        val canonicalRoot = staging.canonicalPath + File.separator
                        require(target.canonicalPath.startsWith(canonicalRoot)) { "Unsafe path" }
                        target.parentFile?.mkdirs()
                        FileOutputStream(target).use { out ->
                            while (true) {
                                val n = zip.read(buffer)
                                if (n == -1) break
                                total += n
                                require(total <= MAX_UNPACKED_BYTES) { "Unpacked ZIP too large" }
                                out.write(buffer, 0, n)
                            }
                        }
                        zip.closeEntry()
                    }
                }
            }
            require(count > 0) { "ZIP contains no supported files" }
            return Result(staging, count, total)
        } catch (e: Exception) {
            staging.deleteRecursively()
            throw e
        }
    }
}
