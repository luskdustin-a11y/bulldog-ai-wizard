"""VAL -> Archie event bridge: validated messages, deduplication and acknowledgements.

Transport-independent: a caller delivers event dictionaries to ArchieBridge.receive.
No network or vehicle connection is claimed by this module.
"""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional
import json

ALLOWED_KINDS = {"power", "fault", "maintenance", "component_update", "health"}

@dataclass(frozen=True)
class ValEvent:
    event_id: str
    kind: str
    component: str
    status: str
    details: dict
    source: str = "simulation"
    timestamp: Optional[str] = None

    def validate(self):
        if not self.event_id or not self.component or self.kind not in ALLOWED_KINDS:
            raise ValueError("invalid VAL event identity, component or kind")
        if self.source not in {"sensor", "estimate", "simulation", "manual"}:
            raise ValueError("invalid evidence source")
        if self.status not in {"healthy", "warning", "failed", "unknown"}:
            raise ValueError("invalid status")
        if not isinstance(self.details, dict):
            raise ValueError("details must be an object")
        return self

    def encode(self):
        self.validate()
        data = asdict(self)
        data["timestamp"] = self.timestamp or datetime.now(timezone.utc).isoformat()
        return json.dumps(data, sort_keys=True)

class ArchieBridge:
    """In-memory receive boundary; plug durable storage/network transport in later."""
    def __init__(self):
        self.events = {}
        self.latest_by_component = {}

    def receive(self, payload):
        data = json.loads(payload) if isinstance(payload, str) else payload
        if not isinstance(data, dict):
            raise ValueError("expected event object")
        event = ValEvent(**data).validate()
        if event.event_id in self.events:
            if self.events[event.event_id] != data:
                raise ValueError("event ID reused with different payload")
            return {"event_id": event.event_id, "accepted": True, "duplicate": True}
        self.events[event.event_id] = dict(data)
        self.latest_by_component[event.component] = dict(data)
        return {"event_id": event.event_id, "accepted": True, "duplicate": False}

    def component_state(self, component):
        return self.latest_by_component.get(component)
