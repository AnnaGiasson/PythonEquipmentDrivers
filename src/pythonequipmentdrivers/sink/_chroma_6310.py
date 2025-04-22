from dataclasses import dataclass
from enum import Enum

from ..core import VisaResource


@dataclass(frozen=True, slots=True)
class _Limits:
    min: float
    max: float

    def get(self) -> tuple[float]:
        return (self.min, self.max)


@dataclass(frozen=True)
class _Module_Base_Config:
    T: _Limits = _Limits(0.000025, 50.0)
    I_L: _Limits = _Limits(0.0, 6.0)
    I_H: _Limits = _Limits(0.0, 60.0)
    R_L: _Limits = _Limits(0.025, 100.0)
    R_H: _Limits = _Limits(1.25, 5000.0)
    P_L: _Limits = _Limits(0.0, 30.0)
    P_H: _Limits = _Limits(0.0, 300.0)
    V_L: _Limits = _Limits(0.0, 16.0)
    V_H: _Limits = _Limits(0.0, 80.0)
    I_SR_L: _Limits = _Limits(0.001, 0.25)  # A/us
    I_SR_H: _Limits = _Limits(0.01, 2.5)  # A/us
    Rd_L: _Limits = _Limits(1.0, 1000.0)
    Rd_H: _Limits = _Limits(10.0, 10000.0)


_SUPPORTED_CONFIGS = {
    "BASE": _Module_Base_Config(),
    "63106A": _Module_Base_Config(
        I_L=_Limits(0.0, 12.0),
        I_H=_Limits(0.0, 120.0),
        R_L=_Limits(12.5e-3, 50),
        R_H=_Limits(0.625, 2.5e3),
        P_L=_Limits(0.0, 60.0),
        P_H=_Limits(0.0, 600.0),
        I_SR_L=_Limits(0.002, 0.5),
        I_SR_H=_Limits(0.02, 5.0),
    ),
    "63112A": _Module_Base_Config(
        I_L=_Limits(0.0, 24.0),
        I_H=_Limits(0.0, 240.0),
        P_L=_Limits(0.0, 120.0),
        P_H=_Limits(0.0, 1200.0),
        R_L=_Limits(6.25e-3, 25),
        R_H=_Limits(0.3125, 1.25e34),
        I_SR_L=_Limits(0.004, 1.0),
        I_SR_H=_Limits(0.04, 10.0),
    ),
}


class Chroma_6310(VisaResource):

    class CCRange(Enum):
        LOW = "CCL"
        HIGH = "CCH"

    class CCEdges(Enum):
        RISE = "rise"
        FALL = "fall"

    def __init__(self, address: str, **kwargs) -> None:
        super().__init__(address, **kwargs)

        # Check connection is valid
        manuf, *desc = self.idn.lower().split(",")

        if manuf != "chroma" or desc[0][:3] != "631":
            raise ValueError(
                f"Instrument at {address} is not a Chroma 6310 based Programmable load."
            )

        # determine hardware config
        channel_identity = self.query_resource("channel:id?").split(",")
        module_name = channel_identity[1]
        if module_name not in _SUPPORTED_CONFIGS:
            self._Module = _SUPPORTED_CONFIGS["BASE"]
        else:
            self._Module = _SUPPORTED_CONFIGS[module_name]

    @staticmethod
    def _limit(x: float, x_min: float, x_max: float) -> float:
        return min((max((x, x_min)), x_max))

    def _current_check(self, current: float) -> float:
        return self._limit(
            current, x_min=self._Module.I_L.min, x_max=self._Module.I_H.max
        )

    def _slew_check(self, slew: float, cc_range: CCRange) -> float:

        if cc_range == self.CCRange.LOW:
            return self._limit(slew, *self._Module.I_SR_L.get())
        else:
            return self._limit(slew, *self._Module.I_SR_H.get())

    def set_state(self, state: bool) -> None:
        """
        set_state(state)

        Enables/disables the input for the load

        Args:
            state (bool): Load state (True == enabled, False == disabled)
        """
        self.write_resource(f'load:state {"on" if state else "off"}')

    def get_state(self) -> bool:
        """
        get_state()

        Returns the current state of the input to the load

        Returns:
            bool: Load state (True == enabled, False == disabled)
        """
        response = self.query_resource("load:state?")
        return response == "1"

    def on(self) -> None:
        """
        on()

        Enables the Load's output; equivalent to set_state(True).
        """
        self.set_state(True)

    def off(self) -> None:
        """
        off()

        Disables the input for the load. Equivalent to set_state(False)
        """
        self.set_state(False)

    def toggle(self) -> None:
        """
        toggle()

        Reverses the current state of the Load.
        """
        self.set_state(not self.get_state())

    def set_current(self, current: float, level: int = 0) -> None:
        """
        set_current(current, level=0)

        Changes the current setpoint of the load for the specified level in
        constant current mode.

        Args:
            current (float): Desired current setpoint in Amps DC.
            level (int, optional): level to change setpoint of valid options
                are 0,1,2; If level = 0 both levels will be set to the
                value specified. Defaults to 0.
        """
        current = self._current_check(current)

        if int(level) == 0:
            self.write_resource(f"current:static:l1 {current}")
            self.write_resource(f"current:static:l2 {current}")
        else:
            self.write_resource(f"current:static:l{level} {current}")

    def get_current(self, level: int) -> float:
        """
        get_current(level)

        Retrives the current setpoint of the load for the specified level used
        in constant current mode. if level == 0 then both load levels will be
        returned.

        Args:
            level (int): level to retrive setpoint of valid options
                are 0,1,2.

        Returns:
            float: Retrivies the current setpoint in Amps DC.
        """
        if level not in (1, 2):
            raise ValueError("Invalid load level (should be 1 or 2)")

        response = self.query_resource(f"current:static:l{level}?")
        return float(response)

    def set_current_range(self, cc_range: CCRange) -> None:
        """
        set_current_range(cc_range)

        Changes the current range of the load

        Args:
            cc_range (CCRange): Enum denoting the desired current range
        """
        self.write_resource(f"mode {cc_range.value}")

    def get_current_range(self) -> CCRange:
        """
        get_current_range()

        Queries the current range of the load

        Returns:
            CCRange: Enum denoting the currently used current range
        """
        cc_range = self.query_resource("mode?")

        try:
            return self.CCRange(cc_range)
        except KeyError:
            raise ValueError("Unknown CC Range")

    def auto_range(self, current: float) -> None:
        """
        auto_range(current)

        Configures the load to be in the correct range for the specified current

        Args:
            current (float): reference current in Amps
        """
        if not (self._Module.I_L.min <= current <= self._Module.I_H.max):
            raise ValueError("Invalid current level")

        if current <= self._Module.I_L.max:
            self.set_current_range(self.CCRange.LOW)
        else:
            self.set_current_range(self.CCRange.HIGH)

    def set_current_slew_rate(self, slew_rate: float, edge: CCEdges) -> None:
        """
        set_current_slew(slew_rate, edge)

        Changes the slew-rate setting of the load (for the specified edge
        polarity) in constant current mode.

        Args:
            slew_rate (float): desired slew-rate setting in A/s
            edge (CCEdges): Enum which determines the edge to set the slew-rate of.
        """

        slew_rate_a_p_us = (
            self._slew_check(slew=slew_rate_a_p_us, cc_range=self.get_current_range())
            * 1e-6
        )  # convert Amp/s to Amp/us

        self.write_resource(f"current:static:{edge.value} {slew_rate_a_p_us}")

    def get_current_slew_rate(self, edge: CCEdges) -> float:
        """
        get_current_slew_rate(edge_polarity)

        Retrives the slew-rate setting of the load (for the specified edge
        polarity) in constant current mode.

        Args:
            edge (CCEdges): Enum which determines the edge to get the slew-rate of.

        Returns:
            float: slew-rate setting in A/s.
        """
        response = self.query_resource(f"current:static:{edge.value}?")
        return float(response) * 1e6  # convert Amp/us to Amp/s
