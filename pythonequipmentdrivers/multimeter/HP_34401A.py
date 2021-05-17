from pythonequipmentdrivers import Scpi_Instrument as _Scpi_Instrument


class HP_34401A(_Scpi_Instrument):
    """
    HP_34401A()

    address: str, address of the connected multimeter

    factor: float, multiplicitive scale for all measurements defaults to 1.

    object for accessing basic functionallity of the HP_34401A multimeter.
    The factor term allows for measurements to be multiplied by some number
    before being returned. For example, in the case of measuring the voltage
    across a current shunt this factor can represent the conductance of the
    shunt. This factor defaults to 1 (no effect on measurement).

    Additional Information:
    http://ecee.colorado.edu/~mathys/ecen1400/pdf/references/HP34401A_BenchtopMultimeter.pdf
    """

    def __init__(self, address, **kwargs):
        super().__init__(address, **kwargs)
        self.factor = kwargs.get('factor', 1.0)
        self.valid_modes = {'VDC': "VOLT:DC",
                            'VAC': "VOLT:AC",
                            'ADC': "CURR:DC",
                            'AAC': "CURR:AC",
                            'FREQ': "FREQ",
                            'OHMS': "RES",
                            'DIOD': "DIOD",
                            'CONT': "CONT",
                            'PER': "PER"}
        return None

    def set_mode(self, mode):
        """
        set_mode(mode)

        mode: str, type of measurement to be done
            valid modes are: 'VDC', 'VAC', 'ADC', 'AAC', 'FREQ', 'OHMS',
                             'DIOD', 'CONT', 'PER'
            which correspond to DC voltage, AC voltage, DC current, AC current,
            frequency, resistence, diode voltage, continuity, and period
            respectively (not case sensitive)

        Configures the multimeter to perform the specified measurement
        """

        mode = mode.upper()
        if mode in self.valid_modes:
            self.instrument.write(f"CONF:{self.valid_modes[mode]}")
        else:
            raise ValueError("Invalid mode option")
        return None

    def get_mode(self):
        """
        get_mode()

        retrives type of measurement the multimeter is current configured to
        perform.

        returns: str
        """
        response = self.instrument.query("FUNC?")
        response = response.rstrip().replace('"', '')
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
        if self.get_mode() != 'VOLT':
            raise IOError("Multimeter is not configured to measure voltage")
        else:
            response = self.instrument.query("MEAS:VOLT:DC?")
            return self.factor*float(response)

    def measure_voltage_rms(self):
        """
        measure_voltage_rms()

        returns float, measurement in Volts rms

        Measure the voltage present at the AC voltage measurement terminals.
        If the meter is not configured to measure AC voltage this will raise an
        exception. This can be remedied by setting the meaurement mode with the
        set_mode method.

        """
        if self.get_mode() != 'VOLT:AC':
            raise IOError("Multimeter is not configured to measure AC voltage")
        else:
            response = self.instrument.query("MEAS:VOLT:AC?")
            return self.factor*float(response)

    def measure_current(self):
        """
        measure_current()

        returns float, measurement in Amperes DC

        Measure the current present through the DC current measurement
        terminals. If the meter is not configured to measure DC current this
        will raise an exception. This can be remedied by setting the meaurement
        mode with the set_mode method.

        """
        if self.get_mode() != 'CURR':
            raise IOError("Multimeter is not configured to measure current")
        else:
            response = self.instrument.query("MEAS:CURR:DC?")
            return self.factor*float(response)

    def measure_current_rms(self):
        """
        measure_current_rms()

        returns float, measurement in Amperes rms

        Measure the current present through the AC current measurement
        terminals. If the meter is not configured to measure AC current this
        will raise an exception. This can be remedied by setting the meaurement
        mode with the set_mode method.

        """
        if self.get_mode() != 'CURR:AC':
            raise IOError("Multimeter is not configured to measure AC current")
        else:
            response = self.instrument.query("MEAS:CURR:AC?")
            return self.factor*float(response)

    def measure_resistance(self):
        """
        measure_resistance()

        returns float, measurement in Ohms

        Measure the resistance present at the resistance measurement terminals.
        If the meter is not configured to measure resistance this will raise an
        exception. This can be remedied by setting the meaurement mode with the
        set_mode method.

        """
        if self.get_mode() != 'RES':
            raise IOError("Multimeter is not configured to measure resistance")
        else:
            response = self.instrument.query("MEAS:RES?")
            return float(response)

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
            response = self.instrument.query("MEAS:FREQ?")
            return float(response)
