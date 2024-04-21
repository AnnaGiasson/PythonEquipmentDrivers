import unittest
from unittest.mock import MagicMock, patch

import pythonequipmentdrivers as ped


class TestFunctions(unittest.TestCase):

    @patch.object(ped.core.rm, "list_resources")
    def test_find_visa_resources(self, list_resources_patch: MagicMock):
        return_value = (
            "ASRL1::INSTR",
            "GPIB::1::0::INSTR",
            "USB::0x1234::125::A22-5::INSTR",
        )
        list_resources_patch.return_value = return_value
        self.assertEqual(return_value, ped.find_visa_resources())
