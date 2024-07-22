import unittest
from importlib import import_module


class pythonequipmentdrivers_TestCase(unittest.TestCase):
    def test_package_import(self):
        """
        check that all attrs expected to be exposed at the package level exist
        """

        package = import_module("pythonequipmentdrivers")

        for sub_package in package.__all__:
            with self.subTest(sub_package=sub_package):
                self.assertTrue(hasattr(package, sub_package))
