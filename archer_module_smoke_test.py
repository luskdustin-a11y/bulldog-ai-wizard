"""Executable smoke test: VAL event -> module router -> Archie inbox -> acknowledgement."""
from archer_module_event_router import ModuleEventRouter
from val_to_archie_bridge import ValEvent

def main():
    router = ModuleEventRouter()
    router.enroll("val-f250", {"val"})
    event = ValEvent("smoke-1", "power", "battery", "warning",
                     {"voltage": 12.1}, source="simulation",
                     timestamp="2026-10-22T21:00:00+00:00")
    receipt = router.deliver("val-f250", "val", event)
    assert receipt == {"event_id": "val-f250:smoke-1", "accepted": True, "duplicate": False}
    state = router.latest("val", "val-f250", "battery")
    assert state["details"]["voltage"] == 12.1
    assert state["source"] == "simulation"
    assert router.deliver("val-f250", "val", event)["duplicate"]
    print("PASS: VAL -> router -> Archie inbox -> acknowledgement -> duplicate suppression")

if __name__ == "__main__":
    main()
