from ..core import VisaResource


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

        self.write_resource(f"OUTP {1 if state else 0}")

    def get_state(self) -> bool:
        """
        get_state()

        Retrives the current state of the output of the supply.

        Returns:
            bool: Supply state (True == enabled, False == disabled)
        """

        response = self.query_resource("OUTP?")
        return int(response) == 1

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

    def toggle(self) -> None:
        """
        toggle(return_state=False)

        Reverses the current state of the Supply's output
        """

        self.set_state(self.get_state() ^ True)

    def set_voltage_range(self, voltage_range: float) -> None:
        if voltage_range > 156:
            self.write_resource("VOLT:RANG 312")
        else:
            self.write_resource("VOLT:RANG 156")

    def get_voltage_range(self) -> float:
        return float(self.query_resource("VOLT:RANG?"))

    def set_voltage(self, voltage: float) -> None:
        self.write_resource(f"VOLT {voltage}")

    def get_voltage(self) -> float:
        return float(self.query_resource("VOLT?"))

    def set_current(self, current: float) -> None:
        self.write_resource(f"CURR {current}")

    def get_current(self) -> float:
        return float(self.query_resource("CURR?"))

    def set_frequency(self, frequency: float) -> None:
        self.write_resource(f"FREQ {frequency}")

    def get_frequency(self) -> float:
        return float(self.query_resource("FREQ?"))

    def set_phase(self, phase: float) -> None:
        self.write_resource(f"PHAS {phase}")

    def get_phase(self) -> float:
        return float(self.query_resource("PHAS?"))

    def measure_voltage(self) -> float:
        return float(self.query_resource("MEAS:VOLT?"))

    def measure_current(self) -> float:
        return float(self.query_resource("MEAS:CURR?"))

    def measure_power(self) -> float:
        return float(self.query_resource("MEAS:POW?"))

    def measure_frequency(self) -> float:
        return float(self.query_resource("MEAS:FREQ?"))
