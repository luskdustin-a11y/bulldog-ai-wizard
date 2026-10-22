"""Simulation-only device protocol integration into ARCHER department hub.

No physical Bluetooth, USB, OBD, Garmin, Android, or network discovery.
"""
from archer_department_hub import DepartmentHub, Request
from archer_remote_relay import DeviceRegistry

class DeviceBridge:
    def __init__(self, hub=None):
        self.hub=hub or DepartmentHub()
        self.registry=DeviceRegistry()
        self.permissions={}

    def enroll(self, device_id, device_type, departments):
        self.registry.enroll(device_id,device_type)
        try:
            self.hub.enroll(device_id,departments)
        except Exception:
            self.registry.revoke(device_id)
            raise
        self.permissions[device_id]=frozenset(departments)

    def revoke(self, device_id):
        self.registry.revoke(device_id)
        self.hub.revoke(device_id)
        self.permissions.pop(device_id,None)

    def request(self, device_id, department, question):
        if device_id not in self.registry.allowed():
            raise PermissionError("Device not active")
        return self.hub.route(Request(device_id,department,question))

    def inventory(self):
        return [{"device":name,"type":details["type"],"active":details["active"],
                 "departments":sorted(self.permissions.get(name,()))}
                for name,details in sorted(self.registry.devices.items())]
