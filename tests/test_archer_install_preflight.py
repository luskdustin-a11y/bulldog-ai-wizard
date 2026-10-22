import unittest
from archer_install_preflight import REPORTED_HP, Laptop, simulate_install

class LaptopPreflightTests(unittest.TestCase):
    def test_reported_laptop_is_not_mistaken_for_scanned_device(self):
        result = simulate_install()
        self.assertTrue(result["simulation_only"])
        self.assertFalse(result["device_scanned"])
        self.assertFalse(result["ready_to_install_complete_system"])
        self.assertEqual(result["laptop"]["ram_gb"], 64)
        self.assertEqual(result["laptop"]["ssd_gb"], 4096)
    def test_free_space_check(self):
        laptop = Laptop("Windows 11 Pro", "AMD Ryzen 5 7430U", 64, 4096, True, free_disk_gb=4)
        result = simulate_install(laptop)
        free = next(x for x in result["checks"] if x["component"] == "Free storage")
        self.assertEqual(free["result"], "insufficient")
    def test_missing_features_are_not_marked_working(self):
        result = simulate_install()
        statuses = {x["component"]: x["result"] for x in result["checks"]}
        self.assertEqual(statuses["Android APK"], "not_implemented")
        self.assertEqual(statuses["Private login and encryption"], "not_implemented")
