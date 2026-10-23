"""Common event path from any enrolled Archie module to Archie's central inbox.

This is an in-process integration adapter, not a live device/network connection.
"""
import json
from archer_department_hub import DEPARTMENTS
from val_to_archie_bridge import ArchieBridge, ValEvent

class ModuleEventRouter:
    def __init__(self):
        self.inbox = ArchieBridge()
        self.permissions = {}

    def enroll(self, module_id, departments):
        allowed = frozenset(departments)
        if not isinstance(module_id, str) or not module_id.strip() or module_id in self.permissions:
            raise ValueError("invalid or duplicate module")
        if not allowed or not allowed <= DEPARTMENTS:
            raise ValueError("invalid department permissions")
        self.permissions[module_id] = allowed

    def revoke(self, module_id):
        self.permissions.pop(module_id, None)

    def deliver(self, module_id, department, event):
        if department not in self.permissions.get(module_id, frozenset()):
            raise PermissionError("module not authorized for department")
        if not isinstance(event, ValEvent):
            raise TypeError("expected validated event")
        # Namespace the component and ID to prevent cross-module collisions.
        event = ValEvent(
            event_id=module_id + ":" + event.event_id,
            kind=event.kind,
            component=department + "/" + module_id + "/" + event.component,
            status=event.status,
            details=dict(event.details),
            source=event.source,
            timestamp=event.timestamp,
        )
        return self.inbox.receive(event.encode())

    def latest(self, department, module_id, component):
        return self.inbox.component_state(department + "/" + module_id + "/" + component)
