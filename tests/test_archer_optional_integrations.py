import unittest
from archer_optional_integrations import inspect_integrations

class OptionalIntegrationTests(unittest.TestCase):
    def test_no_dependency_falsely_marked_working(self):
        results = inspect_integrations(which=lambda _: None)
        self.assertTrue(all(not item["installed_and_working"] for item in results.values()))
        self.assertFalse(results["ollama"]["available_on_path"])

    def test_binary_discovery_does_not_install(self):
        results = inspect_integrations(which=lambda _: "/opt/local/bin/ollama")
        self.assertTrue(results["ollama"]["available_on_path"])
        self.assertFalse(results["ollama"]["installed_and_working"])
