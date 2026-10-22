"""Optional operating-system voice output; no microphone or cloud access."""
import os
import shutil
import subprocess
import sys

def voice_backend():
    if sys.platform == "darwin" and shutil.which("say"):
        return "say"
    if sys.platform.startswith("linux") and shutil.which("espeak"):
        return "espeak"
    if os.name == "nt":
        return "powershell"
    return None

def speak(text: str) -> bool:
    """Speak text via installed OS speech, or return False if unavailable."""
    if not isinstance(text, str) or not text.strip():
        return False
    text = text[:2000]
    backend = voice_backend()
    if backend == "say":
        subprocess.run(["say", text], check=True, timeout=40)
    elif backend == "espeak":
        subprocess.run(["espeak", text], check=True, timeout=40)
    elif backend == "powershell":
        # No interpolated script: user text is passed through standard input.
        script = ("Add-Type -AssemblyName System.Speech; "
                  "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                  "$s.Speak([Console]::In.ReadToEnd())")
        subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                       input=text, text=True, check=True, timeout=40)
    else:
        return False
    return True
