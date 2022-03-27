from typing import Union
from pythonequipmentdrivers import VisaResource


class Elgar_5250A(VisaResource):
    """
    Programmers Manual
        http://www.programmablepower.com/products/SW/downloads/SW_A_and_AE_Series_SCPI_Programing_Manual_M162000-03-RvF.PDF
        http://elgar.com/products/SW/downloads/SW_A_and_AE_Series_SCPI_Programing_Manual_M162000-03_RevE.pdf
    """

    def set_state(self, state: bool) -> None:
        """
        set_state(state)

        Enables/disables the output of the supply

        Args:
            state (bool): Supply state (True == enabled, False == disabled)
        """

        self.instrument.write(f"OUTP:STAT {1 if state else 0}")

    def get_state(self) -> bool:
        """
        get_state()

        Retrives the current state of the output of the supply.

        Returns:
            bool: Supply state (True == enabled, False == disabled)
        """

        response = self.instrument.query('OUTP:STAT?')
        return ('1' in response)

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

    def toggle(self, return_state: bool = False) -> Union[None, bool]:
        """
        toggle(return_state=False)

        return_state: boolean, whether or not to return the state of the output
                      relay

        reverses the current state of the power supply's output relay

        if return_state = True the boolean state of the relay after toggle() is
        executed will be returned
        """

        self.set_state(self.get_state() ^ True)

        if return_state:
            return self.get_state()

    def set_voltage(self, voltage, phase=0):
        self.instrument.write(f"SOUR{phase}:VOLT {voltage}")
        return None

    def get_voltage(self, phase=1):
        response = self.instrument.query(f"SOUR{phase}:VOLT?")
        return float(response)

    def set_current(self, current, phase=0):
        self.instrument.write(f"SOUR{phase}:CURR {current}")
        return None

    def get_current(self, phase=1):
        response = self.instrument.query(f"SOUR{phase}:CURR?")
        return float(response)

    def set_frequency(self, frequency):
        self.instrument.write(f"SOUR:FREQ {frequency}")
        return None

    def get_frequency(self):
        response = self.instrument.query("SOUR:FREQ?")
        return float(response)

    def set_voltage_limit(self, voltage_limit):
        self.instrument.write(f"SOUR:VOLT:PROT {voltage_limit}")
        return None

    def get_voltage_limit(self):
        response = self.instrument.query("SOUR:VOLT:PROT?")
        return float(response)

    def set_voltage_range(self, voltage_range):
        self.instrument.write(f"SOUR:VOLT:RANG {voltage_range}")
        return None

    def get_voltage_range(self):
        response = self.instrument.query("SOUR:VOLT:RANG?")
        return float(response)
