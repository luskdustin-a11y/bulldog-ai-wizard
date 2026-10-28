"""Optional local Ollama model adapter for ARCHER.

No model installation or download. Uses only the locally running Ollama API.
Never sends prompts to a cloud endpoint. Requires explicit user setup.
"""
import json
import urllib.request
import urllib.error

class LocalModelUnavailable(RuntimeError):
    pass

class OllamaEngine:
    def __init__(self, model="llama3.2:3b", endpoint="http://127.0.0.1:11434", timeout=30, opener=None):
        if endpoint not in ("http://127.0.0.1:11434", "http://localhost:11434"):
            raise ValueError("Only local Ollama endpoints are allowed")
        if not isinstance(model,str) or not model.strip() or len(model)>120:
            raise ValueError("Invalid model name")
        self.model=model
        self.endpoint=endpoint
        self.timeout=timeout
        self.opener=opener or urllib.request.urlopen

    def answer(self, question, department):
        if not isinstance(question,str) or not question.strip() or len(question)>10000:
            raise ValueError("Invalid question")
        if not isinstance(department,str) or not department.strip():
            raise ValueError("Invalid department")
        payload={"model":self.model,"stream":False,
                 "messages":[{"role":"system","content":"You are ARCHER, an offline assistant. Department: "+department+". Never claim access to live devices or tools unless connected. Do not execute device commands."},
                             {"role":"user","content":question}]}
        request=urllib.request.Request(self.endpoint+"/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type":"application/json"},method="POST")
        try:
            with self.opener(request,timeout=self.timeout) as response:
                if response.status!=200:
                    raise LocalModelUnavailable("Local model returned HTTP "+str(response.status))
                body=response.read(2_000_001)
        except (urllib.error.URLError,TimeoutError,OSError) as exc:
            raise LocalModelUnavailable("Local Ollama service is not available") from exc
        if len(body)>2_000_000:
            raise LocalModelUnavailable("Model response exceeded size limit")
        try:
            result=json.loads(body)
            answer=result["message"]["content"]
            if not isinstance(answer,str):
                raise ValueError("Invalid response")
            return answer
        except (ValueError,KeyError,TypeError) as exc:
            raise LocalModelUnavailable("Invalid local model response") from exc
