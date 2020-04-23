from pythonequipmentdrivers import Scpi_Instrument as _Scpi_Instrument


class Fluke_DMM(_Scpi_Instrument):
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

    def __init__(self, address, factor=1):
        super().__init__(address)
        self.factor = float(factor)
        self.valid_modes = ('AAC', 'ADC', 'VAC', 'VDC',
                            'OHMS', 'FREQ', 'CONT')

    def _measure_signal(self):
        """
        _measure_signal(self)

        returns the value of the current measurement selected on the multimeter
        display

        returns: float
        """

        response = self.instrument.query("VAL1?")
        return self.factor*float(response)

    def set_range(self, n, auto_range=False):
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
            self.instrument.write("AUTO")

        if n in range(0, 7):
            self.instrument.write(f"RANGE {n}")
        else:
            raise ValueError("Invalid range option, should be 1-7")

        return

    def get_range(self):
        """
        get_range()

        Retrieve the current range setting used for measurements.
        Return value is an index from 1 to 7, meaning of the index depends
        on which measurement is being performed.

        returns: int
        """

        response = self.instrument.query("RANGE1?")
        return int(response)

    def set_rate(self, rate):
        """
        set_rate(rate)

        rate: str, speed of sampling
              valid options are 'S','M', or 'F' for slow, medium, and fast
        respectively (not case sensitive)

        adjusts the sampling rate for multimeter measurements
        """

        rate = rate.upper()
        if rate in ['S', 'M', 'F']:
            self.instrument.write(f"RATE {rate}")
        else:
            raise ValueError("Invalid rate option, should be 'S', 'M', or 'F'")
        return

    def get_rate(self):
        """
        get_rate()

        Retrives the sampling rate setting for multimeter measurements
        returns: str
        """

        response = self.instrument.query("RATE?")
        return response

    def set_mode(self, mode):
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
            self.instrument.write(f"FUNC1 {mode}")
        else:
            raise ValueError("Invalid mode option, valid options are: "
                             + f"{', '.join(self.valid_modes)}")
        return

    def get_mode(self):
        """
        get_mode()

        retrives type of measurement the multimeter is current configured to
        perform.

        returns: str
        """

        response = self.instrument.query("FUNC1?")
        return response

    def measure_voltage(self):
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
        else:
            return self._measure_signal()

    def measure_voltage_rms(self):
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
        else:
            return self._measure_signal()

    def measure_current(self):
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
        else:
            return self._measure_signal()

    def measure_current_rms(self):
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
        else:
            return self._measure_signal()

    def measure_resistance(self):
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
        else:
            return self._measure_signal()

    def measure_frequency(self):
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
        else:
            return self._measure_signal()
