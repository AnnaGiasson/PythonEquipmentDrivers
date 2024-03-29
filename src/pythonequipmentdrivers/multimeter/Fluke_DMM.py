from typing import Set

from ..core import VisaResource


class Fluke_DMM(VisaResource):
    """
    Fluke_DMM(address, factor=1)

    address: str, address of the connected multimeter

    factor: float, multiplicitive scale for all measurements defaults to 1.

    object for accessing basic functionallity of the Fluke_DMM multimeter.
    The factor term allows for measurements to be multiplied by some number
    before being returned. For example, in the case of measuring the voltage
    across a current shunt this factor can represent the conductance of the
    shunt. This factor defaults to 1 (no effect on measurement).
    """

    def __init__(self, address: str, **kwargs) -> None:
        super().__init__(address, **kwargs)
        self.factor: float = kwargs.get('factor', 1.0)
        self.valid_modes: Set[str] = {
            'AAC', 'ADC', 'VAC', 'VDC', 'OHMS', 'FREQ', 'CONT'
            }

    def _measure_signal(self) -> float:
        """
        _measure_signal(self)

        returns the value of the current measurement selected on the multimeter
        display

        returns: float
        """

        response = self.query_resource("VAL1?")
        return self.factor*float(response)

    def set_range(self, n: int, auto_range: bool = False) -> None:
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

        returns: int
        """

        if auto_range:
            self.write_resource("AUTO")

        if 0 <= n < 7:
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

        response = self.query_resource("RANGE1?")
        return int(response)

    def set_rate(self, rate: str) -> None:
        """
        set_rate(rate)

        rate: str, speed of sampling
              valid options are 'S','M', or 'F' for slow, medium, and fast
        respectively (not case sensitive)

        adjusts the sampling rate for multimeter measurements
        """

        rate = rate.upper()
        if rate in {'S', 'M', 'F'}:
            self.write_resource(f"RATE {rate}")
        else:
            raise ValueError("Invalid rate option, should be 'S', 'M', or 'F'")

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
            self.write_resource.write(f"FUNC1 {mode}")
        else:
            raise ValueError("Invalid mode option, valid options are: "
                             + ', '.join(self.valid_modes))

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

        if self.get_mode() != 'VDC':
            raise IOError("Multimeter is not configured to measure voltage")
        return self._measure_signal()

    def measure_voltage_rms(self) -> float:
        """
        measure_voltage_rms()

        returns float, measurement in Volts rms

        Measure the voltage present at the AC voltage measurement terminals.
        If the meter is not configured to measure AC voltage this will raise an
        exception. This can be remedied by setting the meaurement mode with the
        set_mode method.
        """

        if self.get_mode() != 'VAC':
            raise IOError("Multimeter is not configured to measure AC voltage")
        return self._measure_signal()

    def measure_current(self) -> float:
        """
        measure_current()

        returns float, measurement in Amperes DC

        Measure the current present through the DC current measurement
        terminals. If the meter is not configured to measure DC current this
        will raise an exception. This can be remedied by setting the meaurement
        mode with the set_mode method.

        """
        if self.get_mode() != 'ADC':
            raise IOError("Multimeter is not configured to measure current")
        return self._measure_signal()

    def measure_current_rms(self) -> float:
        """
        measure_current_rms()

        returns float, measurement in Amperes rms

        Measure the current present through the AC current measurement
        terminals. If the meter is not configured to measure AC current this
        will raise an exception. This can be remedied by setting the meaurement
        mode with the set_mode method.

        """
        if self.get_mode() != 'AAC':
            raise IOError("Multimeter is not configured to measure AC current")
        return self._measure_signal()

    def measure_resistance(self) -> float:
        """
        measure_resistance()

        returns float, measurement in Ohms

        Measure the resistance present at the resistance measurement terminals.
        If the meter is not configured to measure resistance this will raise an
        exception. This can be remedied by setting the meaurement mode with the
        set_mode method.
        """

        if self.get_mode() != 'OHMS':
            raise IOError("Multimeter is not configured to measure resistance")
        return self._measure_signal()

    def measure_frequency(self) -> float:
        """
        measure_frequency()

        returns float, measurement in Hertz

        Measure the frequency present at the frequency measurement terminals.
        If the meter is not configured to measure frequency this will raise an
        exception. This can be remedied by setting the meaurement mode with the
        set_mode method.
        """

        if self.get_mode() != 'FREQ':
            raise IOError("Multimeter is not configured to measure frequency")
        return self._measure_signal()
