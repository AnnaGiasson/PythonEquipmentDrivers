import unittest
from unittest.mock import MagicMock, patch, call
import functools
import itertools


import pythonequipmentdrivers as ped


class Test_Kikusui_PLZ1004WH(unittest.TestCase):
    def setUp(self) -> None:
        # there is a lot that happens is VisaResource.__init__ so it is easier to just
        # mock it
        with patch.object(
            ped.core.VisaResource, "__init__", lambda address, *args, **kwargs: None
        ):
            self.inst = ped.sink.Kikusui_PLZ1004WH("12345")
            self.inst.write_resource = MagicMock(spec=self.inst.write_resource)
            self.inst.query_resource = MagicMock(spec=self.inst.query_resource)
        return super().setUp()

    def test_set_state(self):
        self.inst.set_state(True)
        self.inst.write_resource.assert_called_with("OUTP 1")

    @staticmethod
    def _query_configure_sequence_effect(steps: list, cmd: str):
        idx = int(cmd.split()[-1])
        return steps[idx - 1].current

    def test_configure_sequence(self):

        steps = [self.inst.SequenceStep(n, False) for n in range(10)]
        steps[4].trigger = True
        self.inst.query_resource.side_effect = functools.partial(
            self._query_configure_sequence_effect, steps
        )
        self.inst.configure_sequence(
            steps, current_range="HIGH", step_size=0.001, initialize=False
        )
        expected_write_calls = [
            call("prog:fsp:edit:wave 1,0,1,2,3,4,5,6,7"),
            call("prog:fsp:edit 5,4,1"),
            call("prog:fsp:edit:wave 9,8,9,0,0,0,0,0,0"),
        ]
        expected_query_calls = [
            call("prog:fsp:edit? 5"),
        ]

        self.inst.write_resource.assert_has_calls(expected_write_calls)
        self.inst.query_resource.assert_has_calls(expected_query_calls)

    def test_configure_sequence_init(self):
        steps = [self.inst.SequenceStep(n, False) for n in range(10)]
        steps[4].trigger = True
        self.inst.query_resource.side_effect = functools.partial(
            self._query_configure_sequence_effect, steps
        )
        self.inst.configure_sequence(
            steps, current_range="HIGH", step_size=0.001, initialize=True
        )
        expected_calls = [
            call("prog:name 11"),
            call("prog:mode fcc"),
            call("prog:loop 1"),
            call(f"prog:fsp:time {0.001}"),
            call("prog:cran HIGH"),
            call("prog:fsp:end 10"),
            call("prog:fsp:edit:wave 1,0,1,2,3,4,5,6,7"),
            call("prog:fsp:edit 5,4,1"),
            call("prog:fsp:edit:wave 9,8,9,0,0,0,0,0,0"),
        ]
        expected_query_calls = [
            call("prog:fsp:edit? 5"),
        ]

        self.inst.write_resource.assert_has_calls(expected_calls)
        self.inst.query_resource.assert_has_calls(expected_query_calls)

    @patch.object(ped.sink.Kikusui_PLZ1004WH, "configure_sequence")
    def test_configure_pulse_sequence(self, configure_seq_mock: MagicMock):
        self.inst.configure_pulse_seqeunce(
            pulse_current=10,
            pulse_width=10e-3,
            trig_delay=2e-3,
            step_size=1e-3,
            initial_idle_time=0.01,
            idle_current=0,
            current_range="HIGH",
        )

        steps = list(
            itertools.chain(
                itertools.repeat(self.inst.SequenceStep(0), 10),
                itertools.repeat(self.inst.SequenceStep(10), 10),
                itertools.repeat(self.inst.SequenceStep(0), 1),
            )
        )
        steps[13].trigger = True

        configure_seq_mock.assert_called_once_with(steps, "HIGH", 1e-3)
