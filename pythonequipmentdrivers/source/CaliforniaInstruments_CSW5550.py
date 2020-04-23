from pythonequipmentdrivers import Scpi_Instrument as _Scpi_Instrument


class CaliforniaInstruments_CSW5550(_Scpi_Instrument):
    """
    Programmers Manual
    http://www.programmablepower.com/products/SW/downloads/SW_A_and_AE_Series_SCPI_Programing_Manual_M162000-03-RvF.PDF
    """

    def __init__(self, address):
        super().__init__(address)
        return

    def set_state(self, state):
        """
        a delay of 1 second is required after changing the relay state before
        any program command is sent
        """
        self.instrument.write(f"OUTP {state}")
        return

    def get_state(self):
        return int(self.instrument.query("OUTP?"))

    def on(self):
        self.set_state(1)
        return

    def off(self):
        self.set_state(0)
        return

    def toggle(self, return_state=False):
        if not(self.get_state()):
            self.on()
        else:
            self.off()

        if return_state:
            return self.get_state()
        return

    def set_voltage_range(self, voltage_range):
        if voltage_range > 156:
            self.instrument.write("VOLT:RANG 312")
        else:
            self.instrument.write("VOLT:RANG 156")
        return

    def get_voltage_range(self):
        return float(self.instrument.query("VOLT:RANG?"))

    def set_voltage(self, voltage):
        self.instrument.write(f"VOLT {voltage}")
        return

    def get_voltage(self):
        return float(self.instrument.query("VOLT?"))

    def set_current(self, current):
        self.instrument.write(f"CURR {current}")
        return

    def get_current(self):
        return float(self.instrument.query("CURR?"))

    def set_frequency(self, frequency):
        self.instrument.write(f"FREQ {frequency}")
        return

    def get_frequency(self):
        return float(self.instrument.query("FREQ?"))

    def set_phase(self, phase):
        self.instrument.write(f"PHAS {phase}")
        return

    def get_phase(self):
        return float(self.instrument.query("PHAS?"))

    def measure_voltage(self):
        return float(self.instrument.query("MEAS:VOLT?"))

    def measure_current(self):
        return float(self.instrument.query("MEAS:CURR?"))

    def measure_power(self):
        return float(self.instrument.query("MEAS:POW?"))

    def measure_frequency(self):
        return float(self.instrument.query("MEAS:FREQ?"))
