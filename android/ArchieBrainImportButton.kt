package com.bulldawg.ai.importer

import android.net.Uri
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/** Place ArchieBrainImportButton() inside the existing Compose screen. */
@Composable
fun ArchieBrainImportButton() {
    val context = androidx.compose.ui.platform.LocalContext.current
    val scope = rememberCoroutineScope()
    var busy by remember { mutableStateOf(false) }
    var status by remember { mutableStateOf("Select a brain ZIP to stage for review") }
    val picker = rememberLauncherForActivityResult(
        ActivityResultContracts.OpenDocument()
    ) { uri: Uri? ->
        if (uri == null) return@rememberLauncherForActivityResult
        scope.launch {
            busy = true
            try {
                val result = withContext(Dispatchers.IO) {
                    ArchieBrainImporter.stage(context, uri)
                }
                status = "Staged ${result.files} files (${result.bytes} bytes). Not activated."
            } catch (e: Exception) {
                status = "Import failed: ${e.message ?: "Invalid package"}"
            } finally {
                busy = false
            }
        }
    }
    Column(modifier = Modifier.padding(16.dp)) {
        Button(enabled = !busy, onClick = {
            picker.launch(arrayOf("application/zip", "application/octet-stream"))
        }) { Text("Import Archie's Brain") }
        if (busy) CircularProgressIndicator()
        Text(status)
    }
}
