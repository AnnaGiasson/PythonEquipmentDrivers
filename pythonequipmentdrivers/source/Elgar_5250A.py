from pythonequipmentdrivers import Scpi_Instrument as _Scpi_Instrument


class Elgar_5250A(_Scpi_Instrument):
    """
    Programmers Manual
        http://www.programmablepower.com/products/SW/downloads/SW_A_and_AE_Series_SCPI_Programing_Manual_M162000-03-RvF.PDF
        http://elgar.com/products/SW/downloads/SW_A_and_AE_Series_SCPI_Programing_Manual_M162000-03_RevE.pdf
    """

    def __init__(self, address):
        super().__init__(address)
        return

    def set_state(self, state):
        """
        set_state(state)

        state: int, 1 or 0 for on and off respectively

        enables/disables the state for the power supply's output
        """

        self.instrument.write(f"OUTP:STAT {int(state)}")
        return

    def get_state(self):
        """
        get_state()

        returns the current state of the output relay,

        returns: int
        1: enabled, 0: disabled
        """

        response = self.instrument.query("OUTP:STAT?")
        return int(response)

    def on(self):
        """
        on()

        enables the relay for the power supply's output
        equivalent to set_state(1)
        """

        self.set_state(1)
        return

    def off(self):
        """
        off()

        disables the relay for the power supply's output
        equivalent to set_state(0)
        """

        self.set_state(0)
        return

    def toggle(self, return_state=False):
        """
        toggle(return_state=False)

        return_state: boolean, whether or not to return the state of the output
                      relay

        reverses the current state of the power supply's output relay

        if return_state = True the boolean state of the relay after toggle() is
        executed will be returned
        """

        if self.get_state():
            self.off()
        else:
            self.on()

        if return_state:
            return self.get_state()
        return

    def set_current(self, current, phase=0):
        self.instrument.write(f"SOUR{phase}:CURR {current}")
        return

    def get_current(self, phase=1):
        response = self.instrument.query(f"SOUR{phase}:CURR?")
        return float(response)

    def set_frequency(self, frequency):
        self.instrument.write(f"SOUR:FREQ {frequency}")
        return

    def get_frequency(self):
        response = self.instrument.query("SOUR:FREQ?")
        return float(response)

    def set_voltage(self, voltage, phase=0):
        self.instrument.write(f"SOUR{phase}:VOLT {voltage}")
        return

    def get_voltage(self, phase=1):
        response = self.instrument.query(f"SOUR{phase}:VOLT?")
        return float(response)

    def set_voltage_limit(self, voltage_limit):
        self.instrument.write(f"SOUR:VOLT:PROT {voltage_limit}")
        return

    def get_voltage_limit(self):
        response = self.instrument.query("SOUR:VOLT:PROT?")
        return float(response)

    def set_voltage_range(self, voltage_range):
        self.instrument.write(f"SOUR:VOLT:RANG {voltage_range}")
        return

    def get_voltage_range(self):
        response = self.instrument.query("SOUR:VOLT:RANG?")
        return float(response)
