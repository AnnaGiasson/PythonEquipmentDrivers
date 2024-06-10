from typing import Tuple

from ...core import VisaResource


class Intepro_PSI9000(VisaResource):
    """
    note: with this supply, the device must be locked before it will respond to
          commands
    manual:
    https://www.inteproate.com/wp-content/uploads/2016/11/Intepro-ModBus-SCPI-User-Manual-A4-new-edits-6_2017.pdf
    """

    def __init__(self, address: str, **kwargs) -> None:
        super().__init__(address, **kwargs)
        self.set_lock(True)

    def __del__(self) -> None:
        self.set_lock(False)
        super().__del__()

    def set_lock(self, state: bool) -> None:
        self.write_resource(f"SYST:LOCK {1 if state else 0}")

    def get_lock(self) -> True:

        response = self.query_resource("SYST:LOCK:OWN?")
        return response == "REMOTE"

    def set_state(self, state: bool) -> None:
        """
        set_state(state)

        Enables/disables the output of the supply

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
        return response == "ON"

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

    def set_voltage(self, voltage: float) -> None:
        self.write_resource(f"VOLT {voltage}")

    def get_voltage(self) -> float:
        return float(self.query_resource("VOLT?").strip("V"))

    def set_current(self, current: float) -> None:
        self.write_resource(f"CURR {current}")

    def get_current(self) -> float:
        return float(self.query_resource("CURR?").strip("A"))

    def set_power(self, power: float) -> None:
        self.write_resource(f"POW {power}")

    def get_power(self) -> float:
        return float(self.query_resource("POW?").strip("W"))

    def measure_voltage(self) -> float:
        return float(self.query_resource("MEAS:VOLT?").strip("V"))

    def measure_current(self) -> float:
        return float(self.query_resource("MEAS:CURR?").strip("A"))

    def measure_power(self) -> float:
        return float(self.query_resource("MEAS:POW?").strip("W"))

    def measure_array(self) -> Tuple[float, float, float]:
        response = self.query_resource("MEAS:ARR?")
        v, i, p = response.split(",")

        v = float(v.strip(" V"))
        i = float(i.strip(" A"))
        p = float(p.strip(" W"))

        return v, i, p

    def set_ovp(self, voltage: float) -> None:
        self.write_resource(f"SOUR:VOLT:PROT {voltage}")

    def get_ovp(self) -> float:
        return float(self.query_resource("SOUR:VOLT:PROT?").strip("V"))

    def set_ocp(self, current: float) -> None:
        self.write_resource(f"SOUR:CURR:PROT {current}")

    def get_ocp(self) -> float:
        return float(self.query_resource("SOUR:CURR:PROT?").strip("A"))

    def set_opp(self, power: float) -> None:
        self.write_resource(f"SOUR:POW:PROT {power}")

    def get_opp(self) -> float:
        return float(self.query_resource("SOUR:POW:PROT?").strip("W"))
