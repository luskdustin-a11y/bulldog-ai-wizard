"""ARCHER software-only supervisor: deterministic health and dependency checks.

No background services, device commands, or automatic repair actions.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone

COMPONENTS = {
    "brain": (),
    "dashboard": ("brain",),
    "queue": (),
    "local_transport": ("queue",),
    "relay_client": ("queue",),
    "relay_server": (),
    "device_registry": (),
    "shop": ("brain",),
    "val": ("brain", "queue"),
    "hunting": ("brain", "queue"),
    "property": ("brain",),
    "hotshot": ("brain",),
    "finances": ("brain",),
    "stocks": ("brain",),
    "supervisor": (),
}

@dataclass
class Component:
    name: str
    implemented: bool = False
    tested: bool = False
    healthy: bool = False
    details: str = ""

class Supervisor:
    def __init__(self):
        self.components = {name: Component(name) for name in COMPONENTS}
        self.events = []

    def report(self, name, *, implemented, tested, healthy, details=""):
        if name not in self.components:
            raise ValueError("Unknown component")
        if healthy and not (implemented and tested):
            raise ValueError("A component cannot be healthy without implementation and tests")
        self.components[name] = Component(name, implemented, tested, healthy, details)
        self.events.append({"name": name, "healthy": healthy, "timestamp": datetime.now(timezone.utc).isoformat()})

    def status(self):
        results = {}
        for name, deps in COMPONENTS.items():
            item = self.components[name]
            missing = [dep for dep in deps if not self.components[dep].healthy]
            ready = item.implemented and item.tested and item.healthy and not missing
            results[name] = {"ready": ready, "implemented": item.implemented,
                             "tested": item.tested, "healthy": item.healthy,
                             "blocked_by": missing, "details": item.details}
        return {"ready": all(v["ready"] for v in results.values()),
                "ready_count": sum(v["ready"] for v in results.values()),
                "total": len(results), "components": results}

    def required_work(self):
        result = self.status()
        return [name for name, info in result["components"].items() if not info["ready"]]
