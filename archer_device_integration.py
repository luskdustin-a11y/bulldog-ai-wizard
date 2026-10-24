"""ARCHER device integration contracts: explicitly approved, read-only adapters.

Real hardware requires separately installed vendor-specific connectors.
No simulated status is presented as live telemetry.
"""
from datetime import datetime, timezone

SUPPORTED = frozenset({"camera", "thermostat", "vehicle_diagnostics", "watercraft_diagnostics"})

class DeviceIntegration:
    def __init__(self):
        self.adapters = {}
        self.approved = set()

    def register(self, device_id, category, reader):
        if not isinstance(device_id, str) or not device_id.strip() or device_id in self.adapters:
            raise ValueError("Unique device ID required")
        if category not in SUPPORTED or not callable(reader):
            raise ValueError("Unsupported category or invalid adapter")
        self.adapters[device_id] = (category, reader)

    def approve(self, device_id):
        if device_id not in self.adapters:
            raise ValueError("Unknown device")
        self.approved.add(device_id)

    def revoke(self, device_id):
        self.approved.discard(device_id)

    def read(self, device_id):
        if device_id not in self.adapters:
            raise ValueError("Unknown device")
        if device_id not in self.approved:
            raise PermissionError("Owner approval required before device access")
        category, reader = self.adapters[device_id]
        result = reader()
        if not isinstance(result, dict):
            raise ValueError("Device adapter must return a telemetry dictionary")
        return {"device_id": device_id, "category": category, "source": "adapter",
                "observed_at": datetime.now(timezone.utc).isoformat(), "data": result}
