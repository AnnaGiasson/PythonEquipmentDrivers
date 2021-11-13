from pathlib import Path
from dataclasses import dataclass
from typing import Any, Callable, Protocol
from time import sleep
from pythonequipmentdrivers import connect_equipment, EquipmentCollection


class SMPS_Environment(Protocol):
    v_in: float
    v_in_state: bool
    i_in: float
    v_out: float
    i_out: float
    i_out_state: bool

    def initialize(self) -> None:
        ...

    def shut_down(self) -> None:
        ...


@dataclass
class Test_Environment:
    equipment: EquipmentCollection

    @property
    def v_in(self) -> float:
        return self.equipment.v_in_meter.measure_voltage()

    @v_in.setter
    def v_in(self, voltage: float) -> None:
        self.equipment.source.set_voltage(voltage)

    @property
    def v_in_state(self) -> bool:
        return self.equipment.source.get_state()

    @v_in_state.setter
    def v_in_state(self, state: bool) -> None:
        return self.equipment.source.set_state(state)

    @property
    def i_in(self) -> float:
        return self.equipment.source.measure_current()

    @property
    def v_out(self) -> float:
        return self.equipment.v_out_meter.measure_voltage()

    @property
    def i_out(self) -> float:
        self.equipment.sink.measure_current()

    @i_out.setter
    def i_out(self, current: float) -> None:
        self.equipment.sink.set_current(current)

    @property
    def i_out_state(self) -> bool:
        return self.equipment.sink.get_state()

    @i_out_state.setter
    def i_out_state(self, state: bool) -> None:
        return self.equipment.sink.set_state(state)

    def initialize(self) -> None:
        self.v_in = 0
        self.v_in_state = True

        self.i_out = 10
        self.i_out_state = True
        self.wait_until_true(func=lambda: self.v_out < 1)
        self.i_out = 0

    def shut_down(self) -> None:
        self.v_in_state = False
        self.v_in = 0

        self.i_out = 10
        self.wait_until_true(func=lambda: self.v_out < 1)
        self.i_out_state = False
        self.i_out = 0

    @staticmethod
    def wait_until_true(func: Callable[[Any], bool]) -> None:

        while not func():
            sleep(0.5)


def enviroment_test() -> Test_Environment:

    cwd = Path(__file__).parent.resolve()
    config_path = cwd.joinpath('equipment.config')

    return Test_Environment(connect_equipment(configuration=config_path,
                                              init=True))


if __name__ == '__main__':
    enviroment_test()
