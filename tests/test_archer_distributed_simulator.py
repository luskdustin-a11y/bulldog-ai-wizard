"""End-to-end simulated device network tests; no physical connectivity implied."""
import unittest
from archer_distributed_simulator import VirtualFleet, simulation_report

class DistributedIntegrationTests(unittest.TestCase):
    def test_full_scenarios(self):
        result=simulation_report()
        self.assertTrue(result["simulation_only"])
        self.assertFalse(result["physical_devices_tested"])
        self.assertEqual(result["passed"], result["total"], result["scenarios"])

    def test_no_replay_after_revocation(self):
        fleet=VirtualFleet()
        fleet.cellular=False
        self.assertEqual(fleet.send("VAL","VAL","sensitive"),"QUEUED")
        fleet.units["VAL"].authorized=False
        fleet.cellular=True
        self.assertEqual(fleet.recover(),0)
        self.assertEqual(fleet.received,[])
        self.assertEqual(fleet.pending,[])

    def test_recover_once(self):
        fleet=VirtualFleet()
        fleet.home_internet=False
        self.assertEqual(fleet.send("Phone","Hunting","deer"),"QUEUED")
        fleet.home_internet=True
        self.assertEqual(fleet.recover(),1)
        self.assertEqual(fleet.recover(),0)
        self.assertEqual(len(fleet.received),1)

    def test_all_units(self):
        fleet=VirtualFleet()
        for source in fleet.units:
            self.assertEqual(fleet.send(source,"Supervisor","status"),"DELIVERED")
        self.assertEqual(len(fleet.received),len(fleet.units))

if __name__=="__main__":
    unittest.main()
