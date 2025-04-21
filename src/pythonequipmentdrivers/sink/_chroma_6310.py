from enum import Enum
from dataclasses import dataclass

from ..core import VisaResource


@dataclass(frozen=True, slots=True)
class _Module_Base_Config:
    T_MIN: float = 0.000025
    T_MAX: float = 50.0
    I_MIN: float = 0.0
    I_LMAX: float = 6.0
    I_HMAX: float = 60.0
    V_MIN: float = 0.0
    V_LMAX: float = 16.0
    V_HMAX: float = 80.0
    R_HMIN: float = 1.25
    R_HMAX: float = 5000.0
    R_LMIN: float = 0.025
    R_LMAX: float = 100.0
    P_LMAX: float = 30.0
    P_HMAX: float = 300.0
    ISR_HMIN: float = 0.01
    ISR_HMAX: float = 2.5
    ISR_LMIN: float = 0.001
    ISR_LMAX: float = 0.25
    Rd_LMIN: float = 1.0
    Rd_LMAX: float = 1000.0
    Rd_HMIN: float = 10.0
    Rd_HMAX: float = 10000.0

_SUPPORTED_CONFIGS = {
    "BASE": _Module_Base_Config(),
    "63106A": _Module_Base_Config(
        I_HMAX = 120.0,
        I_LMAX = 12.0,
        R_HMAX = 2500.0,
        R_HMIN = 0.625,
        R_LMAX = 50.0,
        R_LMIN = 0.0125,
        P_HMAX = 600.0,
        P_LMAX = 60.0,
        ISR_HMIN = 0.02,
        ISR_HMAX = 5.0,
        ISR_LMIN = 0.002,
        ISR_LMAX = 0.5,
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

        if manuf != 'chroma' or desc[0][:3] != '631':
            raise ValueError(f'Instrument at {address} is not a Chroma 6310 based Programmable load.')

        # determine hardware config
        channel_identity = self.query_resource("channel:id?").split(",")
        module_name = channel_identity[1]
        if module_name not in _SUPPORTED_CONFIGS:
            self._Module = _SUPPORTED_CONFIGS["BASE"]
        else:
            self._Module[module_name]

    @staticmethod
    def _limit(x: float, x_min: float, x_max: float) -> float:
        return min(
            (max((x, x_min)), x_max)
        )

    def _current_check(self, current: float) -> float:
        return self._limit(current, x_min=self._Module.I_MIN, x_max=self._Module.I_HMAX)

    def _slew_check(self, slew: float, current: float) -> float:
        if current <= self._Module.I_LMAX:
            return self._limit(slew, x_min=self._Module.ISR_LMIN, x_max=self._Module.ISR_LMAX)
        elif current > self._Module.I_LMAX:
            return self._limit(slew, x_min=self._Module.ISR_HMIN, x_max=self._Module.ISR_HMAX)
        raise ValueError('Invalid current level')

    def set_state(self, state: bool) -> None:
        self.write_resource(f'load:state {"on" if state else "off"}')

    def get_state(self) -> bool:
        response = self.query_resource('load:state?')
        return response == '1'

    def on(self) -> None:
        self.set_state(True)

    def off(self) -> None:
        self.set_state(False)

    def toggle(self) -> None:
        self.set_state(not self.get_state())

    def set_current_range(self, cc_range: CCRange) -> None:
        self.write_resource(f'mode {cc_range.value}')

    def get_current_range(self) -> CCRange:
        cc_range = self.query_resource('mode?')

        try:
            return self.CCRange(cc_range)
        except KeyError:
            raise ValueError('Unknown CC Range')

    def auto_range(self, current: float) -> None:
        if current <= self._Module.I_LMAX:
            self.set_current_range(self.CCRange.LOW)
        else:
            self.set_current_range(self.CCRange.HIGH)

    def set_current(self, current: float, level: int = 0) -> None:
        current = self._current_check(current)

        if int(level) == 0:
            self.write_resource(f'current:static:l1 {current}')
            self.write_resource(f'current:static:l2 {current}')
        else:
            self.write_resource(f'current:static:l{level} {current}')

    def get_current(self, level: int) -> float:

        if level not in (1, 2):
            raise ValueError('Invalid load level (should be 1 or 2)')

        response = self.query_resource(f'current:static:l{level}?')
        return float(response)

    def set_current_slew_rate(self, slew_rate: float, edge: CCEdges) -> None:
        self.write_resource(f'current:static:{edge.value} {slew_rate}')

    def get_current_slew_rate(self, edge: CCEdges) -> float:
        response = self.query_resource(f'current:static:{edge.value}?')
        return float(response)
