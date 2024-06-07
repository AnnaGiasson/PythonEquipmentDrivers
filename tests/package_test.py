import unittest
from importlib import import_module


class pythonequipmentdrivers_TestCase(unittest.TestCase):
    def test_package_import(self):
        expected_sub_packages = [
            "daq",
            "functiongenerator",
            "multimeter",
            "networkanalyzer",
            "oscilloscope",
            "powermeter",
            "sink",
            "source",
        ]

        package = import_module("pythonequipmentdrivers")

        for sub_package in expected_sub_packages:
            with self.subTest(sub_package=sub_package):
                self.assertTrue(hasattr(package, sub_package))
