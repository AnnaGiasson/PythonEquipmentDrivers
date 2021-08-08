from typing import Union
from pythonequipmentdrivers import Scpi_Instrument


class CaliforniaInstruments_CSW5550(Scpi_Instrument):
    """
    Programmers Manual
    http://www.programmablepower.com/products/SW/downloads/SW_A_and_AE_Series_SCPI_Programing_Manual_M162000-03-RvF.PDF
    """

    def set_state(self, state: bool) -> None:
        """
        set_state(state)

        Enables/disables the output of the supply.
        A delay of 1 second is required after changing the relay state before
        any program command is sent

        Args:
            state (bool): Supply state (True == enabled, False == disabled)

        """

        self.instrument.write(f"OUTP {1 if state else 0}")

    def get_state(self) -> bool:
        """
        get_state()

        Retrives the current state of the output of the supply.

        Returns:
            bool: Supply state (True == enabled, False == disabled)
        """

        response = self.instrument.query("OUTP?")
        return (int(response) == 1)

    def on(self) -> None:
        """
        on()

        Enables the relay for the power supply's output equivalent to
        set_state(True).
        """

        self.set_state(True)

    def off(self) -> None:
        """
        off()

        Disables the relay for the power supply's output equivalent to
        set_state(False).
        """

        self.set_state(False)

    def toggle(self, return_state=False) -> Union[None, bool]:
        """
        toggle(return_state=False)

        Reverses the current state of the Supply's output
        If return_state = True the boolean state of the supply after toggle()
        is executed will be returned.

        Args:
            return_state (bool, optional): Whether or not to return the state
                of the supply after changing its state. Defaults to False.

        Returns:
            Union[None, bool]: If return_state == True returns the Supply state
                (True == enabled, False == disabled), else returns None
        """

        self.set_state(self.get_state() ^ True)

        if return_state:
            return self.get_state()

    def set_voltage_range(self, voltage_range):
        if voltage_range > 156:
            self.instrument.write("VOLT:RANG 312")
        else:
            self.instrument.write("VOLT:RANG 156")
        return None

    def get_voltage_range(self):
        return float(self.instrument.query("VOLT:RANG?"))

    def set_voltage(self, voltage):
        self.instrument.write(f"VOLT {voltage}")
        return None

    def get_voltage(self):
        return float(self.instrument.query("VOLT?"))

    def set_current(self, current):
        self.instrument.write(f"CURR {current}")
        return None

    def get_current(self):
        return float(self.instrument.query("CURR?"))

    def set_frequency(self, frequency):
        self.instrument.write(f"FREQ {frequency}")
        return None

    def get_frequency(self):
        return float(self.instrument.query("FREQ?"))

    def set_phase(self, phase):
        self.instrument.write(f"PHAS {phase}")
        return None

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
