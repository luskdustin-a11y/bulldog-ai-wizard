"""Opt-in local Ollama adapter; never sends data to a remote host.

Uses Python standard library only. Local Ollama must be installed and running
separately; this module does not install or start it.
"""
import json
from http.client import HTTPException
from urllib.parse import urlsplit
from archer_platform import http_response

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
    if not isinstance(system_prompt, str) or not system_prompt or len(system_prompt) > 200000:
        raise ValueError("System prompt required")
    if not isinstance(model, str) or not model.strip() or len(model) > 100:
        raise ValueError("Model name required")
    endpoint = _local_url(base_url) + "/api/chat"
    payload = json.dumps({"model": model, "stream": False, "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ]}).encode("utf-8")
    try:
        with http_response(endpoint, method='POST', data=payload,
                           headers={'Content-Type': 'application/json'}, timeout=timeout,
                           allowed_hosts={'127.0.0.1', 'localhost', '::1'},
                           allow_loopback_http=True) as response:
            if response.status != 200:
                raise ModelUnavailable(f"Local model HTTP {response.status}")
            raw = response.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError('Local model response exceeds limit')
        result = json.loads(raw)
    except (OSError, ValueError, HTTPException, RecursionError) as exc:
        raise ModelUnavailable("Local AI model unavailable or returned invalid data") from exc
    if not isinstance(result, dict) or not isinstance(result.get('message'), dict):
        raise ModelUnavailable('Local AI model returned an invalid message')
    answer = result['message'].get('content')
    if not isinstance(answer, str) or not answer.strip():
        raise ModelUnavailable("Local AI model returned no answer")
    return answer.strip()
