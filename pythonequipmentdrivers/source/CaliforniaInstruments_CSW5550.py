from typing import Union
from pythonequipmentdrivers import VisaResource


class CaliforniaInstruments_CSW5550(VisaResource):
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

        self._resource.write(f"OUTP {1 if state else 0}")

    def get_state(self) -> bool:
        """
        get_state()

        Retrives the current state of the output of the supply.

        Returns:
            bool: Supply state (True == enabled, False == disabled)
        """

        response = self._resource.query("OUTP?")
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
            self._resource.write("VOLT:RANG 312")
        else:
            self._resource.write("VOLT:RANG 156")
        return None

    def get_voltage_range(self):
        return float(self._resource.query("VOLT:RANG?"))

    def set_voltage(self, voltage):
        self._resource.write(f"VOLT {voltage}")
        return None

    def get_voltage(self):
        return float(self._resource.query("VOLT?"))

    def set_current(self, current):
        self._resource.write(f"CURR {current}")
        return None

    def get_current(self):
        return float(self._resource.query("CURR?"))

    def set_frequency(self, frequency):
        self._resource.write(f"FREQ {frequency}")
        return None

    def get_frequency(self):
        return float(self._resource.query("FREQ?"))

    def set_phase(self, phase):
        self._resource.write(f"PHAS {phase}")
        return None

    def get_phase(self):
        return float(self._resource.query("PHAS?"))

    def measure_voltage(self):
        return float(self._resource.query("MEAS:VOLT?"))

    def measure_current(self):
        return float(self._resource.query("MEAS:CURR?"))

    def measure_power(self):
        return float(self._resource.query("MEAS:POW?"))

    def measure_frequency(self):
        return float(self._resource.query("MEAS:FREQ?"))
