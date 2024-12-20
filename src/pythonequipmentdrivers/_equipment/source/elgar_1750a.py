from time import sleep
from typing import Any, Dict

from pythonequipmentdrivers.core import VisaResource


class Elgar_1750A(VisaResource):
    """
    Elgar_1750A(address)

    address : str, address of the connected power supply

    object for accessing basic functionallity of the Elgar_1750 AC supply

    Programmers Manual:
    http://www.programmablepower.com/products/SW/downloads/SW_A_and_AE_Series_SCPI_Programing_Manual_M162000-03-RvF.PDF
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

        Reverses the current state of the Supply's output
        """

        self.set_state(self.get_state() ^ True)

    def set_current(self, current: float) -> None:
        self.write_resource("SOUR:CURR {}".format(current))

    def get_current(self) -> float:
        return float(self.query_resource("SOUR:CURR?"))

    def set_frequency(self, frequency: float) -> None:
        self.write_resource("SOUR:FREQ {}".format(frequency))

    def get_frequency(self) -> float:
        return float(self.query_resource("SOUR:FREQ?"))

    def get_phase(self) -> float:
        return float(self.query_resource("SOUR:PHAS?"))

    def set_phase(self, phase: float) -> None:
        # phase in deg
        # wraps phase around 0 to 360 deg
        self.write_resource(f"SOUR:PHAS {phase % 360}")

    def set_voltage(self, voltage: float, change_range: bool = False) -> None:

        if change_range:
            self.auto_range(voltage)

        self.write_resource(f"SOUR:VOLT {voltage}")

    def get_voltage(self) -> float:
        return float(self.query_resource("SOUR:VOLT?"))

    def set_voltage_limit(self, voltage_limit: float) -> None:
        self.write_resource(f"SOUR:VOLT:PROT {voltage_limit}")

    def get_voltage_limit(self) -> float:
        return float(self.query_resource("SOUR:VOLT:PROT?"))

    def set_voltage_range(self, voltage_range: float) -> None:
        self.write_resource(f"SOUR:VOLT:RANG {voltage_range}")

    def get_voltage_range(self) -> None:
        return float(self.query_resource("SOUR:VOLT:RANG?"))

    def generate_sequence(self, *conditions: Dict[str, Any], run: bool = False) -> None:
        """
        conditions should be a list of dictionaries containing the conditions
        of each segment
        """

        # ----- Create Segment 0 -----
        # Clear sequence scratchpad. Take advantage of defaults and only
        # set changed params
        self.write_resource("Edit:seq:clear")

        for index, segment in enumerate(conditions):
            if not ("dur" in segment.keys() or "cycl" in segment.keys()):
                raise ValueError('Segment missing required key: "dur" or "cycl"')

            self.write_resource(f"Edit:seq:seg {index}")
            for key in segment.keys():
                command_str = f'Edit:seq:{key} {f"{segment[key]:3.1f}"}'
                self.write_resource(command_str)

            if not (index + 1 == len(conditions)):
                # Create segment 1. Segment pointer is automatically
                # incremented to seg 1.
                self.write_resource("Edit:seq:insert {}".format(index + 1))
                sleep(0.1)

        # ----- setup sequence execution parameters -----
        # execute sequence once and stop
        self.write_resource("Sour:seq:mode:run single")
        # set output voltage to 0 when seq stops
        self.write_resource("Sour:seq:mode:stop ZERO")
        # load seq scratchpad
        self.write_resource('Sour:seq:load "SCRATCH"')

        if run:
            self.on()
            sleep(1)
            self.write_resource("Source:seq run")  # execute sequence

    def auto_range(self, voltage: float) -> None:
        if voltage > 156:
            self.set_voltage_range(1)
            self.set_voltage_limit(510)
            self.set_current(5)
        else:
            self.set_voltage_range(0)
            self.set_voltage_limit(255)
            self.set_current(13)
