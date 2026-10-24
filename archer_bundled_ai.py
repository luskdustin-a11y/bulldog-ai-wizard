"""Start the bundled local inference engine only after owner unlock."""
import os
import subprocess
import sys
import time
from pathlib import Path
from archer_model import local_model_status

def start_bundled_ai(wait_seconds=20):
    if local_model_status().get("ready"):
        return True
    if os.name != "nt":
        return False
    install_dir = Path(sys.executable).resolve().parent
    engine = install_dir / "ollama" / "ollama.exe"
    models = Path(os.environ.get("PROGRAMDATA", "C:/ProgramData")) / "BulldawgAI" / "models"
    if not engine.is_file() or not models.is_dir():
        return False
    env = os.environ.copy()
    env["OLLAMA_HOST"] = "127.0.0.1:11434"
    env["OLLAMA_MODELS"] = str(models)
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        process = subprocess.Popen([str(engine), "serve"], cwd=str(engine.parent),
                                   env=env, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   creationflags=flags)
    except OSError:
        return False
    deadline = time.monotonic() + wait_seconds
    while time.monotonic() < deadline:
        if local_model_status().get("ready"):
            return True
        if process.poll() is not None:
            return False
        time.sleep(0.5)
    return False
