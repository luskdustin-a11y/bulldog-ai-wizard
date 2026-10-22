"""Deterministic simulated distributed-unit integration; no real radios or network."""
from dataclasses import dataclass
from archer_simulator import run_simulation

DEPARTMENTS = ("Shop AI","VAL","Hunting","Property","Hotshot","Finances","Stocks","Supervisor")
@dataclass
class Unit:
    authorized: bool = True
    online: bool = True

class VirtualFleet:
    def __init__(self):
        self.units = {name:Unit() for name in ("Phone","VAL","Android Radio","Garmin Fenix 8","Garmin Venu 3S")}
        self.cellular = self.hotspot = self.bluetooth = self.home_internet = True
        self.distance_miles = 100
        self.pending = []
        self.received = []
        self.sequence = 0
        self.vpn_connected = True
        self.data_allowed = True
        self.power_available = True
        self.delivered_ids = set()

    def reachable(self, source):
        if not self.units[source].online or not self.home_internet or not self.power_available: return False
        if not self.vpn_connected or not self.data_allowed: return False
        if not self.units["Phone"].online or not self.cellular: return False
        if source == "Android Radio": return self.hotspot
        if source.startswith("Garmin"): return self.bluetooth
        return True

    def send(self, source, department, payload):
        if source not in self.units or department not in DEPARTMENTS: return "DENIED"
        if not self.units[source].authorized: return "DENIED"
        self.sequence += 1
        packet = (self.sequence, source, department, payload)
        if not self.reachable(source):
            self.pending.append(packet)
            return "QUEUED"
        return self._deliver(packet)

    def _deliver(self, packet):
        seq, source, department, payload = packet
        if seq in self.delivered_ids: return "DUPLICATE"
        if not self.units[source].authorized: return "DENIED"
        if not self.reachable(source): return "QUEUED"
        self.delivered_ids.add(seq)
        self.received.append(packet)
        return "DELIVERED"

    def recover(self):
        remaining = []
        delivered = 0
        for packet in self.pending:
            outcome = self._deliver(packet)
            if outcome == "DELIVERED": delivered += 1
            elif outcome == "QUEUED": remaining.append(packet)
        self.pending = remaining
        return delivered

def simulation_report():
    base = run_simulation()
    fleet = VirtualFleet()
    scenarios = {}
    scenarios["eight_departments"] = base["passed"] == base["total"] == 8
    scenarios["truck_100_miles"] = fleet.distance_miles == 100 and fleet.send("VAL","VAL","EGT warning") == "DELIVERED"
    fleet.cellular = False
    scenarios["offline_queue"] = fleet.send("VAL","VAL","status") == "QUEUED" and fleet.recover() == 0
    fleet.cellular = True
    scenarios["reconnection"] = fleet.recover() == 1 and fleet.recover() == 0
    fleet.hotspot = False
    scenarios["radio_hotspot_loss"] = fleet.send("Android Radio","Supervisor","status") == "QUEUED"
    fleet.hotspot = True
    scenarios["radio_recovery"] = fleet.recover() == 1
    fleet.bluetooth = False
    scenarios["watch_bluetooth_loss"] = fleet.send("Garmin Fenix 8","Supervisor","status") == "QUEUED"
    fleet.bluetooth = True
    scenarios["watch_recovery"] = fleet.recover() == 1
    fleet.cellular = False
    fleet.send("VAL","VAL","pending")
    fleet.units["VAL"].authorized = False
    fleet.cellular = True
    scenarios["revocation_blocks_replay"] = fleet.recover() == 0
    scenarios["unauthorized_denied"] = fleet.send("VAL","VAL","status") == "DENIED"
    scenarios["unknown_unit_denied"] = fleet.send("intruder","VAL","status") == "DENIED"
    fleet.vpn_connected = False
    scenarios["vpn_outage_queues"] = fleet.send("VAL","VAL","status") == "QUEUED"
    fleet.vpn_connected = True
    scenarios["vpn_recovery"] = fleet.recover() == 1
    fleet.data_allowed = False
    scenarios["data_outage_queues"] = fleet.send("VAL","VAL","status") == "QUEUED"
    fleet.data_allowed = True
    scenarios["data_recovery"] = fleet.recover() == 1
    fleet.power_available = False
    scenarios["power_outage_queues"] = fleet.send("VAL","VAL","status") == "QUEUED"
    fleet.power_available = True
    scenarios["power_recovery"] = fleet.recover() == 1
    return {"simulation_only":True,"physical_devices_tested":False,"passed":sum(scenarios.values()),"total":len(scenarios),"scenarios":scenarios}
