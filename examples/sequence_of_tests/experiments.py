from time import sleep
from typing import Any, Iterable, List, Protocol, Union
from dataclasses import dataclass
from test_environment import SMPS_Environment


@dataclass(frozen=True)
class Operating_Point:
    v_in: Union[int, float]
    i_out: Union[int, float]


class Experiment(Protocol):
    enviroment: SMPS_Environment

    def iterate_conditions() -> Operating_Point:
        """generator that yields the next operating point for the experiment"""
        ...

    def setup_measurement(op: Operating_Point) -> None:
        """
        does any setup for the enviroment to perform a measurement at the
        operating point
        """
        ...

    def perform_measurement() -> Any:
        """performs a measurement for the experiment and returns the data"""
        ...

    def execute() -> None:
        """run the experiement at all conditions"""
        ...

    def export() -> None:
        """saves the data collected in the experiment to file"""
        ...


@dataclass
class EfficiencyTest:
    enviroment: SMPS_Environment
    v_in_conditions: Iterable[Union[int, float]]
    i_out_conditions: Iterable[Union[int, float]]

    def iterate_conditions(self) -> Operating_Point:
        for v_in in self.v_in_conditions:
            for i_out in self.i_out_conditions:
                yield v_in, i_out

    def setup_measurement(self, op: Operating_Point) -> None:

        if abs(self.enviroment.v_in - op.v_in) > 0.5:
            self.enviroment.v_in = op.v_in

        self.enviroment.i_out = op.i_out
        sleep(0.5)  # wait to stabilize

    def calculate_metrics(self, raw_data: List[float]) -> List[float]:
        v_in, i_in, v_out, i_out = raw_data

        p_out = v_out*i_out
        p_in = v_in*i_in
        eff = p_out/p_in

        raw_data.extend((p_out, p_in, eff))
        return raw_data

    def perform_measurement(self):
        data = [self.enviroment.v_in,
                self.enviroment.i_in,
                self.enviroment.v_out,
                self.enviroment.i_out]

        data = self.calculate_metrics(data)
        return data

    def execute(self) -> None:
        self.enviroment.initialize()

        for op in self.iterate_conditions():
            self.setup_measurement(op)
            measurement = self.perform_measurement()
            self.log_measurement(measurement)

        self.enviroment.shut_down()

    def export(self) -> None:
        pass
