"""Explicitly authorized cross-platform communication hub."""
from archer_department_hub import DepartmentHub, Request, DEPARTMENTS

class UniversalHub:
    def __init__(self, engine=None):
        self.departments = DepartmentHub(engine=engine)
        self.devices = {}
        self.adapters = {}

    def enroll(self, device_id, platform, permissions):
        allowed = frozenset(permissions)
        if not isinstance(device_id, str) or not device_id.strip() or device_id in self.devices:
            raise ValueError('Invalid or duplicate device')
        if not isinstance(platform, str) or not platform.strip() or not allowed or not allowed <= DEPARTMENTS:
            raise ValueError('Invalid platform or permissions')
        self.departments.enroll(device_id, allowed)
        self.devices[device_id] = platform

    def revoke(self, device_id):
        self.devices.pop(device_id, None)
        self.departments.revoke(device_id)

    def register_adapter(self, name, handler):
        if not isinstance(name, str) or not name.strip() or not callable(handler):
            raise ValueError('Invalid adapter')
        self.adapters[name] = handler

    def ask(self, device_id, department, question):
        if device_id not in self.devices:
            raise PermissionError('Device not enrolled')
        return self.departments.route(Request(device_id, department, question))

    def send(self, device_id, department, adapter, message):
        if device_id not in self.devices:
            raise PermissionError('Device not enrolled')
        if department not in self.departments._devices.get(device_id, ()):
            raise PermissionError('Department not authorized')
        if adapter not in self.adapters:
            raise LookupError('Adapter not registered')
        if not isinstance(message, str) or not message.strip() or len(message) > 10000:
            raise ValueError('Invalid message')
        return self.adapters[adapter](device_id, department, message)
