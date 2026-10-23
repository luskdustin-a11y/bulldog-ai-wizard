"""Safe PC thermal policy for ARCHER.

Pure decision logic: no hardware commands, no claims of live sensors.
Motherboard/firmware protection always remains authoritative.
"""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class ThermalDecision:
    state: str
    fan_percent: int
    throttle_ai: bool
    request_safe_shutdown: bool

def decide_thermal(cpu_c, gpu_c, *, warning_c=80.0, critical_c=95.0):
    """Evaluate trusted Celsius readings; caller must implement approved actuators."""
    if warning_c <= 0 or critical_c <= warning_c:
        raise ValueError("Invalid thermal thresholds")
    readings = (cpu_c, gpu_c)
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not isfinite(v)
           or v < -20 or v > 150 for v in readings):
        raise ValueError("Invalid or unavailable thermal readings")
    hottest = max(readings)
    if hottest >= critical_c:
        return ThermalDecision("critical", 100, True, True)
    if hottest >= warning_c:
        return ThermalDecision("hot", 100, True, False)
    if hottest >= 65:
        return ThermalDecision("warm", 75, False, False)
    return ThermalDecision("normal", 40, False, False)
