from typing import Union

import pyvisa
from pyvisa.constants import BufferOperation
from pythonequipmentdrivers import VisaResource
from pythonequipmentdrivers.core import rm


class Fluke45SerialError(Exception):
    """
    Exception class for the Fluke45's serial specific errors
    """


class Fluke_45(VisaResource):
    """
    Fluke_45(address, factor=1)

    address : str, address of the connected multimeter

    factor: float, multiplicitive scale for all measurements defaults to 1.

    object for accessing basic functionallity of the Fluke 45 Multimeter.
    The factor term allows for measurements to be multiplied by some number
    before being returned. For example, in the case of measuring the voltage
    across a current shunt this factor can represent the conductance of the
    shunt. This factor defaults to 1 (no effect on measurement).

    For additional commands see programmers Manual:
    http://www.ece.ubc.ca/~eng-services/files/manuals/Man_DMM_fluke45.pdf
    """

    valid_modes = ("AAC", "ADC", "VAC", "VDC", "OHMS", "FREQ", "CONT")
    ranges = (
        (
            {"VDC", "VAC"},
            (
                ({"M", "F"}, ((0.3, 1), (3, 2), (30, 3), (300, 4), (1000, 5))),
                ({"S"}, ((0.1, 1), (1, 2), (10, 3), (100, 4), (1000, 5))),
            ),
        ),
        (
            {"ADC", "AAC"},
            (
                ({"M", "F"}, ((0.03, 1), (0.1, 2), (10, 3))),
                ({"S"}, ((0.01, 1), (0.1, 2), (10, 3))),
            ),
        ),
        (
            {"OHMS"},
            (
                (
                    {"M", "F"},
                    (
                        (300, 1),
                        (3e3, 2),
                        (3e4, 3),
                        (3e5, 4),
                        (3e6, 5),
                        (3e7, 6),
                        (3e8, 7),
                    ),
                ),
                (
                    {"S"},
                    (
                        (100, 1),
                        (1e3, 2),
                        (1e4, 3),
                        (1e5, 4),
                        (1e6, 5),
                        (1e7, 6),
                        (1e8, 7),
                    ),
                ),
            ),
        ),
        (
            {"FREQ"},
            (({"S", "M", "F"}, ((1e3, 1), (1e4, 2), (1e5, 3), (1e6, 4), (1e7, 5))),),
        ),
    )

    def __init__(self, address: str, legacy_ranges=True, **kwargs) -> None:
        # must be set before calling parent constructor
        self._is_serial = True if "asrl" in address.lower() else False
        self._legacy_ranges = legacy_ranges
        super().__init__(address, **kwargs)
        self.factor = kwargs.get("factor", 1.0)

        # now do the rest of the preparations for a serial Fluke 45
        if self._is_serial:
            # self._flush_receive_buffer()
            visa_resource = self._get_visa_resource()
            visa_resource.flush(BufferOperation.discard_receive_buffer)
            visa_resource.write_termination = "\r\n"
            visa_resource.read_termination = "\r\n"

    def _check_serial_response(self, message: str, resp: str) -> None:
        if resp == "=>":
            return
        elif resp == "?>":
            raise Fluke45SerialError(f"{repr(message)} resulted in a command error")
        elif resp == "!>":
            raise Fluke45SerialError(f"{repr(message)} resulted in an execution error")
        else:
            raise Fluke45SerialError(f"{repr(message)} resulted in an unknown error")

    def _get_visa_resource(self) -> pyvisa.resources.Resource:
        """Obtain the device's visa resource without accessing protected members of parent class"""
        for resource in rm.list_opened_resources():
            if resource.resource_name == self.address:
                return resource
        raise RuntimeError("Unable to find a resource matching the device")

    def _flush_receive_buffer(self):
        """alternate method for flushing the receive buffer"""
        # ensure RS232 buffer is empty
        try:
            # ensure exit of loop, not sure if the read buffer is even big
            # enough for 256 query responses
            max_reads = 256
            read_cnt = 0
            while read_cnt <= max_reads:
                self.read_resource()
                read_cnt += 1

        # meter will not respond to reads if the buffer is empty
        except IOError:
            pass  # emptied

    def write_resource(self, message: str, **kwargs) -> None:
        """
        Fluke45 specific write_resource function
        takes care of serial response if the device uses serial
        """
        super().write_resource(message, **kwargs)
        if self._is_serial:
            self._check_serial_response(message, self.read_resource())

    def query_resource(self, message: str, **kwargs) -> str:
        """
        Fluke45 specific query_resource function
        takes care of serial response if the device uses serial
        """
        response = super().query_resource(message, **kwargs)
        if self._is_serial:
            self._check_serial_response(message, self.read_resource())
        return response

    def fetch_data(self) -> float:
        """
        fetch_data()

        returns the value of the current measurement selected on the
        multimeter display

        returns: float
        """

        response = self.query_resource("VAL?")

        return self.factor * float(response)

    def enable_cmd_emulation_mode(self) -> None:
        """
        enable_cmd_emulation_mode()

        For use with a Fluke 8845A. Enables the Fluke 45 command set emulation
        mode.
        """
        self.write_resource("L2")

    def set_local(self):
        """
        set_local()

        Set the DMM to local mode
        """
        if self._is_serial:
            # there is a specific serial command
            self.write_resource("LOCS")
        else:
            # use the GPIB method
            super().set_local()

    def _get_range_number(self, value, reverse_lookup=False):
        mode = self.get_mode()
        rate = self.get_rate()
        for valid_modes, rates_list in self.ranges:
            if mode not in valid_modes:
                continue
            for valid_rates, max_values in rates_list:
                if rate not in valid_rates:
                    continue
                for range_, command in max_values:
                    if value <= range_ and not reverse_lookup:
                        return command
                    elif command == value and reverse_lookup:
                        return range_
                raise ValueError(f"{value=} is greater than highest range")

    def set_range(self, n: Union[int, float], auto_range: bool = False) -> None:
        """
        set_range(n, auto_range=False)

        n: int, range mode to set
        auto_range: bool, whether to enable autoranging (default is False)

        Set the current range setting used for measurements.
            valid settings are the integers 1 through 7, meaning of the index
            depends on which measurement is being performed.
        if the auto_range flag is set to True the device will automaticly
        determine which range to be in base on the signal level default is
        False.
        """

        if auto_range:
            self.write_resource("AUTO")
            return

        if not self._legacy_ranges:
            n = self._get_range_number(n)

        if n in range(0, 7):
            self.write_resource(f"RANGE {n}")
        else:
            raise ValueError("Invalid range option, should be 1-7")

    def get_range(self) -> int:
        """
        get_range()

        Retrieve the current range setting used for measurements.
        Return value is an index from 1 to 7, meaning of the index depends
        on which measurement is being performed.

        returns: int
        """

        n = int(self.query_resource("RANGE1?"))
        if not self._legacy_ranges:
            n = self._get_range_number(n, reverse_lookup=True)
        return n

    def set_rate(self, rate: str) -> None:
        """
        set_rate(rate)

        rate: str, speed of sampling
            valid options are 'S','M', or 'F' for slow, medium, and fast
            respectively (not case sensitive)

        adjusts the sampling rate for multimeter measurements
        """

        rate = rate.upper()
        if rate in {"S", "M", "F"}:
            self.write_resource(f"RATE {rate}")

        else:
            raise ValueError("Invalid rate option, should be 'S','M', or 'F'")

    def get_rate(self) -> str:
        """
        get_rate()

        Retrives the sampling rate setting for multimeter measurements
        returns: str
        """

        response = self.query_resource("RATE?")

        return response

    def set_mode(self, mode: str) -> None:
        """
        set_mode(mode)

        mode: str, type of measurement to be done
            valid modes are 'AAC', 'ADC','VAC', 'VDC','OHMS', 'FREQ', 'CONT'
            which correspond to AC current, DC current, AV voltage, DC voltage,
            resistence, frequency, and continuity respectively (not case
            sensitive)

        Configures the multimeter to perform the specified measurement
        """

        mode = mode.upper()
        if mode in self.valid_modes:
            self.write_resource(f"{mode}")

        else:
            raise ValueError(
                "Invalid mode option, valid options are: "
                + f"{', '.join(self.valid_modes)}"
            )

    def get_mode(self) -> str:
        """
        get_mode()

        retrives type of measurement the multimeter is current configured to
        perform.

        returns: str
        """

        response = self.query_resource("FUNC1?")

        return response

    def measure_voltage(self) -> float:
        """
        measure_voltage()

        returns float, measurement in Volts DC

        Measure the voltage present at the DC voltage measurement terminals.
        If the meter is not configured to measure DC voltage this will raise an
        exception. This can be remedied by setting the meaurement mode with the
        set_mode method.
        """

        if self.get_mode() != "VDC":
            raise IOError("Multimeter is not configured to measure voltage")
        return self.fetch_data()

    def measure_voltage_rms(self) -> float:
        """
        measure_voltage_rms()

        returns float, measurement in Volts rms

        Measure the voltage present at the AC voltage measurement terminals.
        If the meter is not configured to measure AC voltage this will raise an
        exception. This can be remedied by setting the meaurement mode with the
        set_mode method.
        """

        if self.get_mode() != "VAC":
            raise IOError("Multimeter is not configured to measure AC voltage")
        return self.fetch_data()

    def measure_current(self) -> float:
        """
        measure_current()

        returns float, measurement in Amperes DC

        Measure the current present through the DC current measurement
        terminals. If the meter is not configured to measure DC current this
        will raise an exception. This can be remedied by setting the meaurement
        mode with the set_mode method.
        """

        if self.get_mode() != "ADC":
            raise IOError("Multimeter is not configured to measure current")
        return self.fetch_data()

    def measure_current_rms(self) -> float:
        """
        measure_current_rms()

        returns float, measurement in Amperes rms

        Measure the current present through the AC current measurement
        terminals. If the meter is not configured to measure AC current this
        will raise an exception. This can be remedied by setting the meaurement
        mode with the set_mode method.
        """

        if self.get_mode() != "AAC":
            raise IOError("Multimeter is not configured to measure AC current")
        return self.fetch_data()

    def measure_resistance(self) -> float:
        """
        measure_resistance()

        returns float, measurement in Ohms

        Measure the resistance present at the resistance measurement terminals.
        If the meter is not configured to measure resistance this will raise an
        exception. This can be remedied by setting the meaurement mode with the
        set_mode method.
        """

        if self.get_mode() != "OHMS":
            raise IOError("Multimeter is not configured to measure resistance")
        return self.fetch_data()

    def measure_frequency(self) -> float:
        """
        measure_frequency()

        returns float, measurement in Hertz

        Measure the frequency present at the frequency measurement terminals.
        If the meter is not configured to measure frequency this will raise an
        exception. This can be remedied by setting the meaurement mode with the
        set_mode method.
        """

        if self.get_mode() != "FREQ":
            raise IOError("Multimeter is not configured to measure frequency")
        return self.fetch_data()

    def set_trigger_source(self, trigger: str) -> None:
        """
        set_trigger_source(trigger)

        Configure the meter trigger source

        source (str): { INTernal or EXTernal }

        Caution: if external trigger is configured and a read of the meter is
        requested but no measurement is present, the remote interface will
        crash/lockup and you will have to reboot the meter manually ¯\_(ツ)_/¯
        """
        trigger_type_num = 2 if "ext" in trigger.lower() else 1
        self.write_resource(f"TRIGGER {trigger_type_num}")

    def trigger(self) -> None:
        """
        trigger()

        Send the trigger commmand
        """
        self.write_resource("*TRG")

    def config(self, mode: str, rate: str, range_: Union[int, float]):
        """
        config(mode, rate, signal_range, range_n)

        A one stop shop to configure the most common operating parameters

        Args:
            mode (str): type of measurement to be done
                valid modes are 'AAC', 'ADC','VAC', 'VDC','OHMS', 'FREQ', 'CONT'
                which correspond to AC current, DC current, AV voltage, DC voltage,
                resistence, frequency, and continuity respectively (not case
                sensitive)
            rate (str): speed of sampling
                valid options are 'S','M', or 'F' for slow, medium, and fast
                respectively (not case sensitive)
            signal_range (float, optional): measurement range. Defaults to 'auto'
            range_n (float, optional): Set the current range setting used for measurements.
                valid settings are the integers 1 through 7, meaning of the index
                depends on which measurement is being performed.
        """
        self.set_mode(mode)
        self.set_range(range_)
        self.set_rate(rate)
