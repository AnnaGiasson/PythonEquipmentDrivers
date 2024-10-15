import functools
import itertools
import unittest
from unittest.mock import MagicMock, call, patch

import pyvisa.testsuite.test_highlevel

import pythonequipmentdrivers as ped


class Test_Tektronix_DPO4xxx(unittest.TestCase):
    def setUp(self) -> None:
        # there is a lot that happens is VisaResource.__init__ so it is easier to just
        # mock it
        with patch.object(
            ped.core.VisaResource, "__init__", lambda address, *args, **kwargs: None
        ):
            self.inst = ped.oscilloscope.Tektronix_DPO4xxx("12345")
            self.inst.write_resource = MagicMock(spec=self.inst.write_resource)
            self.inst.query_resource = MagicMock(spec=self.inst.query_resource)
            # self.inst._resource = MagicMock(spec=pyvisa.resources.MessageBasedResource)
        return super().setUp()

    def test_get_measure_data(self):

        self.inst.query_resource.return_value = 4.5

        # immediate measurement
        data = self.inst.get_measure_data(0)
        self.assertEqual(data, 4.5)
        self.inst.query_resource.assert_called_with("MEASU:IMM:VAL?")

        # display measurement
        data = self.inst.get_measure_data(1)
        self.assertEqual(data, 4.5)
        self.inst.query_resource.assert_called_with("MEASU:MEAS1:VAL?")

        # multiple measurements
        self.inst.query_resource.side_effect = [1, 2]

        data = self.inst.get_measure_data(0, 1)
        self.assertEqual(data, (1, 2))
        self.inst.query_resource.assert_has_calls(
            [call("MEASU:IMM:VAL?"), call("MEASU:MEAS1:VAL?")]
        )

    def test_configure_measurement(self):

        # single channel display measurement
        self.inst.configure_measurement(
            measurement=self.inst.MeasurementTypes.AMPLITUDE,
            measurement_number=1,
            channel1=1,
        )
        self.inst.write_resource.assert_has_calls(
            [
                call("MEASU:MEAS1:TYP AMPlitude"),
                call("MEASU:MEAS1:SOU1 CH1"),
            ]
        )
        self.inst.write_resource.reset_mock()

        # single channel immediate measurement
        self.inst.configure_measurement(
            measurement=self.inst.MeasurementTypes.AMPLITUDE,
            measurement_number=0,
            channel1=1,
        )
        self.inst.write_resource.assert_has_calls(
            [
                call("MEASU:IMM:TYP AMPlitude"),
                call("MEASU:IMM:SOU1 CH1"),
            ]
        )
        self.inst.write_resource.reset_mock()

        # dual channel measurement
        self.inst.configure_measurement(
            measurement=self.inst.MeasurementTypes.PHASE,
            measurement_number=0,
            channel1=1,
            channel2=2,
        )
        self.inst.write_resource.assert_has_calls(
            [
                call("MEASU:IMM:TYP PHAse"),
                call("MEASU:IMM:SOU1 CH1"),
                call("MEASU:IMM:SOU2 CH2"),
            ]
        )
        self.inst.write_resource.reset_mock()

        # dual channel measurement without second channel supplied
        with self.assertRaises(ValueError):
            self.inst.configure_measurement(
                measurement=self.inst.MeasurementTypes.PHASE,
                measurement_number=0,
                channel1=1,
            )

    def test_set_clear_annotation(self):
        # test no postion provided
        self.inst.set_annotation("hello")
        self.inst.write_resource.assert_called_with('MESSAGE:SHOW "hello";STATE 1')
        self.inst.write_resource.reset_mock()

        # test with postion
        self.inst.set_annotation("hello", 100, 50)
        self.inst.write_resource.assert_called_with(
            'MESSAGE:SHOW "hello";BOX 100, 50;STATE 1'
        )
        self.inst.write_resource.reset_mock()

        # test clear
        self.inst.clear_annotation()
        self.inst.write_resource.assert_called_with("MESSAGE:CLEAR; STATE 0")
