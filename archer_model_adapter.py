"""Local-first Archer model adapter. Cloud requests are intentionally unsupported."""
import json
import urllib.request

class ModelAdapter:
    def __init__(self, mode="local", model="llama3.2", endpoint="http://127.0.0.1:11434"):
        if mode != "local":
            raise PermissionError("Cloud mode requires a separately reviewed owner-approved implementation")
        if not endpoint.startswith(("http://127.0.0.1:", "http://localhost:")):
            raise ValueError("Only loopback Ollama endpoints are permitted")
        self.model, self.endpoint = model, endpoint.rstrip("/")

    def generate(self, prompt):
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt must be nonempty text")
        data = json.dumps({"model": self.model, "prompt": prompt, "stream": False}).encode()
        request = urllib.request.Request(self.endpoint + "/api/generate", data=data,
                                         headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)["response"]
