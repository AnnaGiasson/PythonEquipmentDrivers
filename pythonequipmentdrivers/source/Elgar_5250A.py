from ..core import VisaResource


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

        self.write_resource(f"OUTP:STAT {1 if state else 0}")

    def get_state(self) -> bool:
        """
        get_state()

        Retrives the current state of the output of the supply.

        Returns:
            bool: Supply state (True == enabled, False == disabled)
        """

        response = self.query_resource("OUTP:STAT?")
        return "1" in response

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
        toggle()

        reverses the current state of the power supply's output relay
        """

        self.set_state(self.get_state() ^ True)

    def set_voltage(self, voltage: float, phase: int = 0) -> None:
        self.write_resource(f"SOUR{phase}:VOLT {voltage}")

    def get_voltage(self, phase: int = 1) -> float:
        response = self.query_resource(f"SOUR{phase}:VOLT?")
        return float(response)

    def set_current(self, current: float, phase: int = 0) -> None:
        self.write_resource(f"SOUR{phase}:CURR {current}")

    def get_current(self, phase: int = 1) -> float:
        response = self.query_resource(f"SOUR{phase}:CURR?")
        return float(response)

    def set_frequency(self, frequency: float) -> None:
        self.write_resource(f"SOUR:FREQ {frequency}")

    def get_frequency(self) -> float:
        response = self.query_resource("SOUR:FREQ?")
        return float(response)

    def set_voltage_limit(self, voltage_limit: float) -> None:
        self.write_resource(f"SOUR:VOLT:PROT {voltage_limit}")

    def get_voltage_limit(self) -> float:
        response = self.query_resource("SOUR:VOLT:PROT?")
        return float(response)

    def set_voltage_range(self, voltage_range: float) -> None:
        self.write_resource(f"SOUR:VOLT:RANG {voltage_range}")

    def get_voltage_range(self) -> float:
        response = self.query_resource("SOUR:VOLT:RANG?")
        return float(response)
