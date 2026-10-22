"""ARCHER local orchestrator: real routing and memory, not an LLM."""
import re
from dataclasses import dataclass
import bulldawg_core as core
from archer_persona import build_system_prompt, ResponseContext

KEYWORDS = {
    "Shop AI": ("repair", "engine", "diagnostic", "transmission", "mechanic", "parts"),
    "VAL": ("truck", "ford", "f250", "vehicle", "boost", "egt"),
    "Hunting": ("deer", "camera", "buck", "hunting", "blind", "food plot"),
    "Property": ("property", "house", "renovation", "land", "rental"),
    "Hotshot": ("hotshot", "trailer", "load", "dispatch", "delivery"),
    "Finances": ("budget", "expense", "accounting", "invoice", "tax"),
    "Stocks": ("stock", "portfolio", "shares", "market", "ticker"),
    "Supervisor": ("system", "backup", "health", "security", "status"),
}
SENSITIVE = ("brake", "injury", "emergency", "danger", "financial", "bank", "password", "security")

@dataclass(frozen=True)
class Reply:
    department: str
    text: str
    mode: str

def route(message: str) -> str:
    words = message.lower()
    scores = {d: sum(bool(re.search(r"\b" + re.escape(term) + r"\b", words)) for term in terms)
              for d, terms in KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else "Supervisor"

def respond(message: str) -> Reply:
    if not message.strip():
        raise ValueError("Message required")
    dept = route(message)
    serious = any(re.search(r"\b" + re.escape(word) + r"\b", message.lower()) for word in SENSITIVE)
    # Prompt is ready for a future, explicitly configured model adapter.
    build_system_prompt(ResponseContext(safety_critical=serious))
    if message.strip().lower() in ("health", "system health", "status"):
        data = core.health()
        return Reply("Supervisor", f'Local core: {data["status"]}; notes: {data["notes"]}; AI model connected: no.', "serious")
    return Reply(dept, f'Routing this to {dept}. I can save local notes now, but live {dept} tools and an AI model are not connected yet.', "serious" if serious else "normal")

def remember(department: str, text: str) -> None:
    core.add_note(department, text)

def recall(department: str):
    return core.list_notes(department)
