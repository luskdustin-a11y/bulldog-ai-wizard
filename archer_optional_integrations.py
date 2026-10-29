"""Read-only offline dependency detection for optional ARCHER integrations.

No downloads, installations, cloud access, microphone access, or device changes.
"""
import importlib.util
import shutil
from pathlib import Path

COMPONENTS = {
    "ollama": {"binary": "ollama", "purpose": "Local Windows AI server"},
    "llama_cpp": {"binary": "llama-cli", "purpose": "Optional local GGUF inference"},
    "whisper_cpp": {"binary": "whisper-cli", "purpose": "Offline speech recognition"},
    "piper": {"binary": "piper", "purpose": "Offline text to speech"},
    "syncthing": {"binary": "syncthing", "purpose": "Optional device file transport"},
}

def inspect_integrations(which=shutil.which):
    results = {}
    for name, meta in COMPONENTS.items():
        path = which(meta["binary"])
        results[name] = {
            "available_on_path": bool(path),
            "path": str(Path(path).resolve()) if path else None,
            "installed_and_working": False,
            "purpose": meta["purpose"],
        }
    results["sqlcipher"] = {
        "python_binding_available": importlib.util.find_spec("sqlcipher3") is not None,
        "installed_and_working": False,
        "purpose": "Encrypted live database; migration not implemented",
    }
    results["android_llama_cpp"] = {
        "available_on_path": False,
        "installed_and_working": False,
        "purpose": "Android native inference; separate Android build required",
    }
    return results

if __name__ == "__main__":
    import json
    print(json.dumps(inspect_integrations(), indent=2))
