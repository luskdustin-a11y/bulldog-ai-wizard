"""Offline-first ARCHER response integration. No remote model fallback."""
from archer_brain import respond
from archer_model import chat, ModelUnavailable
from archer_persona import ResponseContext, build_system_prompt

def answer(message, *, use_local_ai=False, model="llama3.2", chat_fn=chat):
    """Return an actual model answer only when local model is explicitly enabled."""
    routed = respond(message)
    if not use_local_ai:
        return routed
    prompt = build_system_prompt(ResponseContext(safety_critical=routed.mode == "serious"))
    try:
        result = chat_fn(message, prompt, model=model)
    except ModelUnavailable:
        return type(routed)(routed.department, routed.text + " Local AI unavailable.", routed.mode)
    return type(routed)(routed.department, result, routed.mode)
