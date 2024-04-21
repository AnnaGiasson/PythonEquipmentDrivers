import unittest
from importlib import import_module


class pythonequipmentdrivers_TestCase(unittest.TestCase):
    def test_import(self):
        module = import_module("pythonequipmentdrivers")
