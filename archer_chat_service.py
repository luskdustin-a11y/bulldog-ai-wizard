"""Offline-first ARCHER response integration. No remote model fallback."""
from archer_brain import respond
from archer_model import chat, ModelUnavailable, local_models
from archer_persona import ResponseContext, build_system_prompt

def answer(message, *, use_local_ai=False, model="llama3.2", chat_fn=chat, models_fn=local_models):
    """Use a verified locally listed model; fail closed when none is installed."""
    routed = respond(message)
    if not use_local_ai:
        return routed
    prompt = build_system_prompt(ResponseContext(safety_critical=routed.mode == "serious"))
    try:
        installed = models_fn()
        if not installed:
            raise ModelUnavailable("No local models installed")
        chosen = model if model in installed else next((m for m in installed if m.split(":")[0] == model), installed[0])
        if chosen.lower().endswith(":cloud"):
            raise ModelUnavailable("Cloud models not allowed")
        result = chat_fn(message, prompt, model=chosen)
    except ModelUnavailable:
        return type(routed)(routed.department, routed.text + " Local AI unavailable.", routed.mode)
    return type(routed)(routed.department, result, routed.mode)
