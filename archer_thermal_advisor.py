"""Archie thermal advisor: recommendations from validated sensor samples.

Advisory only. No direct fan, BIOS, shutdown or OS privileges.
"""
from archer_pc_thermal import decide_thermal

def advise_cooling(cpu_c, gpu_c, *, case_c=None, fan_percent=None):
    decision = decide_thermal(cpu_c, gpu_c)
    advice = []
    if decision.state == "critical":
        advice.append("Request owner-approved safe shutdown; verify vendor thermal limits.")
    elif decision.state == "hot":
        advice.append("Reduce AI workload and check fan response and airflow.")
    elif decision.state == "warm":
        advice.append("Monitor sustained load and fan response.")
    if case_c is not None:
        if isinstance(case_c, bool) or not isinstance(case_c, (int, float)) or not -20 <= case_c <= 100:
            raise ValueError("Invalid case temperature")
        if case_c >= 40:
            advice.append("Case air is warm: inspect dust filters, intake and exhaust airflow.")
    if fan_percent is not None:
        if isinstance(fan_percent, bool) or not isinstance(fan_percent, (int, float)) or not 0 <= fan_percent <= 100:
            raise ValueError("Invalid fan speed percentage")
        if decision.state in ("hot", "critical") and fan_percent < 70:
            advice.append("Cooling response may be insufficient: inspect fan curve and controller compatibility.")
    if decision.state in ("hot", "critical"):
        advice.append("If temperatures stay high after cleaning, evaluate a better CPU cooler or additional case fans.")
    return {"state": decision.state, "suggested_fan_percent": decision.fan_percent,
            "throttle_ai": decision.throttle_ai,
            "request_safe_shutdown": decision.request_safe_shutdown,
            "recommendations": advice,
            "control_mode": "advisory_only"}
