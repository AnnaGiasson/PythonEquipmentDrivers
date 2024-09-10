import unittest
from unittest.mock import MagicMock, patch, call

import pythonequipmentdrivers as ped


class Test_Kikusui_PLZ1004WH(unittest.TestCase):
    def setUp(self) -> None:
        # there is a lot that happens is VisaResource.__init__ so it is easier to just
        # mock it
        with patch.object(
            ped.core.VisaResource, "__init__", lambda address, *args, **kwargs: None
        ):
            self.inst = ped.sink.Kikusui_PLZ1004WH("12345")
            self.inst.write_resource = MagicMock()
            self.inst.query_resource = MagicMock()
        return super().setUp()

    def test_set_state(self):
        self.inst.set_state(True)
        self.inst.write_resource.assert_called_with("OUTP 1")

    def test_configure_sequence(self):
        def query_resource_side_effect(cmd: str):
            idx = int(cmd.split()[-1])
            return steps[idx - 1].current

        steps = [self.inst.SequenceStep(n, False) for n in range(10)]
        steps[4].trigger = True
        self.inst.query_resource.side_effect = query_resource_side_effect
        self.inst.configure_sequence(
            steps, current_range="HIGH", step_size=0.001, initialize=False
        )
        expected_calls = [
            call("prog:fsp:edit:wave 1,0,1,2,3,4,5,6,7"),
            call("prog:fsp:edit 5,4,1"),
            call("prog:fsp:edit:wave 9,8,9,0,0,0,0,0,0"),
        ]
        self.inst.write_resource.assert_has_calls(expected_calls)

    def test_configure_sequence_init(self):
        steps = []
        self.inst.configure_sequence(
            steps, current_range="HIGH", step_size=0.001, initialize=True
        )
        expected_calls = [
            call("prog:name 11"),
            call("prog:mode fcc"),
            call("prog:loop 1"),
            call(f"prog:fsp:time {0.001}"),
            call("prog:cran HIGH"),
            call("prog:fsp:end 0"),
        ]
        self.inst.write_resource.assert_has_calls(expected_calls)
