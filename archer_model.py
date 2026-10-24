"""Opt-in local Ollama adapter; never sends data to a remote host.

Uses Python standard library only. Local Ollama must be installed and running
separately; this module does not install or start it.
"""
import json
from urllib import request, error
from urllib.parse import urlsplit

def local_model_status(model="llama3.2", base_url="http://127.0.0.1:11434", timeout=3):
    """Read-only local readiness check; never downloads or starts software."""
    endpoint = _local_url(base_url) + "/api/tags"
    try:
        req = request.Request(endpoint, method="GET")
        with request.urlopen(req, timeout=timeout) as response:
            if response.status != 200:
                raise ValueError("Unexpected local server response")
            payload = json.loads(response.read(1024 * 1024))
        names = [item.get("name", "") for item in payload.get("models", []) if isinstance(item, dict)]
        installed = any(name == model or name == model + ":latest" for name in names)
        return {"server_running": True, "model_installed": installed, "model": model, "ready": installed}
    except (OSError, ValueError, TypeError, error.URLError, TimeoutError, json.JSONDecodeError):
        return {"server_running": False, "model_installed": False, "model": model, "ready": False}

class ModelUnavailable(RuntimeError):
    pass

def _local_url(base_url):
    parsed = urlsplit(base_url)
    if parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost", "::1") or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("Only a local HTTP Ollama server is permitted")
    if parsed.path not in ("", "/"):
        raise ValueError("Ollama base URL must not include a path")
    return base_url.rstrip("/")

def chat(message, system_prompt, model="llama3.2", base_url="http://127.0.0.1:11434", timeout=30):
    if not isinstance(message, str) or not message.strip() or len(message) > 20000:
        raise ValueError("Message must contain 1–20,000 characters")
    if not isinstance(system_prompt, str) or not system_prompt:
        raise ValueError("System prompt required")
    if not isinstance(model, str) or not model.strip() or len(model) > 100:
        raise ValueError("Model name required")
    endpoint = _local_url(base_url) + "/api/chat"
    payload = json.dumps({"model": model, "stream": False, "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ]}).encode("utf-8")
    req = request.Request(endpoint, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with request.urlopen(req, timeout=timeout) as response:
            if response.status != 200:
                raise ModelUnavailable(f"Local model HTTP {response.status}")
            result = json.loads(response.read(2_000_000))
    except (OSError, ValueError, error.URLError, TimeoutError) as exc:
        raise ModelUnavailable("Local AI model unavailable or returned invalid data") from exc
    answer = result.get("message", {}).get("content")
    if not isinstance(answer, str) or not answer.strip():
        raise ModelUnavailable("Local AI model returned no answer")
    return answer.strip()
