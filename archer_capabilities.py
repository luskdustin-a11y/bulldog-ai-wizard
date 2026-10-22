"""ARCHER capability registry: honest status, priorities and release gates.

No network connections or hardware operations are performed by this module.
"""
from dataclasses import dataclass, asdict
from typing import Literal

Status = Literal["prototype", "planned", "blocked"]
@dataclass(frozen=True)
class Capability:
    id: str
    name: str
    status: Status
    next_step: str
    verification: str
    requires_owner_approval: bool = False

CAPABILITIES = (
    Capability("brain", "AI model and contextual memory", "blocked", "Connect opt-in local model adapter", "Real model conversation, offline fallback and hallucination tests", True),
    Capability("voice", "Two-way speech", "prototype", "Add local microphone speech recognition", "Latency, microphone permissions and noise testing", True),
    Capability("security", "Private login, encryption and backups", "blocked", "Implement authenticated encrypted storage", "Recovery, key rotation and unauthorized access tests", True),
    Capability("windows", "Windows touchscreen dashboard", "prototype", "Integrate conversational brain and run Windows GUI smoke tests", "Real laptop interaction and packaging tests"),
    Capability("android", "Android APK", "planned", "Create native Android project and CI build", "Install and exercise APK on actual Android device", True),
    Capability("sync", "Private device synchronization", "blocked", "Design encrypted paired-device transport", "Conflict resolution and offline sync tests", True),
    Capability("shop", "Shop AI and VAL diagnostics", "planned", "Build read-only verified adapter interfaces", "Vehicle-specific simulated and real read-only DTC tests", True),
    Capability("hunting", "Trail-camera deer analysis", "planned", "Build export import and deduplication", "Labeled deer dataset accuracy and metadata tests", True),
    Capability("business", "Property, hotshot, finances and stocks", "planned", "Build local workflows without live accounts", "Accounting reconciliation and workflow test fixtures", True),
    Capability("supervisor", "Monitoring, recovery and backups", "prototype", "Add health probes and safe restart policies", "Fault injection, restore and recovery tests"),
    Capability("performance", "Fast responsive interface", "planned", "Benchmark cold start and UI navigation", "Repeatable timing on Windows and Android"),
    Capability("watch", "Smartwatch companion", "planned", "Define read-only Wear OS companion", "Pairing, privacy and battery tests", True),
)

def report():
    return [asdict(capability) for capability in CAPABILITIES]

def get_capability(identifier: str):
    return next((c for c in CAPABILITIES if c.id == identifier), None)

def ready_for_release() -> bool:
    # No component is considered production-ready without a separately verified release record.
    return False
