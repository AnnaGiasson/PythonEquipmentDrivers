from pathlib import Path
import time
from typing import Any, Iterable, List, Protocol, Union
from dataclasses import dataclass
from test_environment import SMPS_Environment, Test_Environment
from pythonequipmentdrivers import connect_equipment
from pythonequipmentdrivers.utility import create_test_log, log_data


@dataclass(frozen=True, )
class Operating_Point:
    v_in: Union[int, float]
    i_out: Union[int, float]


class Experiment(Protocol):
    environment: SMPS_Environment

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

    def log_message(*messages: str) -> None:
        """User feedback"""
        ...


class EfficiencyTest:
    idle_load: float = 1.0
    idle_time: float = 5.0

    def __init__(self,
                 environment: SMPS_Environment,
                 v_in_conditions: Iterable[Union[int, float]],
                 i_out_conditions: Iterable[Union[int, float]],
                 output_dir: Path) -> None:

        self.environment = environment
        self.v_in_conditions = v_in_conditions
        self.i_out_conditions = i_out_conditions

        # output files
        self.export_dir = create_test_log(output_dir, test_name='Efficiency',
                                          v_in_conditions=v_in_conditions,
                                          i_out_conditions=i_out_conditions)

        self.log_file = self.export_dir.joinpath('message_log.txt')
        self.log_file.touch(exist_ok=False)
        self.data_log = self.export_dir.joinpath('efficiency_data')

        # Begin message and data logs
        self.log_message('Created Directory for Efficiency data:',
                         f'\t{self.export_dir.as_posix()}',
                         'Logging console output to file:',
                         f'\t{self.log_file.as_posix()}')

        self.columns = ('v_in_set', 'i_out_set',  # operating point
                        'v_in', 'i_in', 'v_out', 'i_out',  # measurements
                        'p_out', 'p_in', 'eff')  # calculations
        log_data(self.data_log, *self.columns)

    def iterate_conditions(self) -> Operating_Point:

        for v_in_set in self.v_in_conditions:
            for i_out_set in self.i_out_conditions:

                yield Operating_Point(v_in_set, i_out_set)

    def setup_measurement(self, op: Operating_Point) -> None:

        if abs(self.environment.v_in - op.v_in) > 0.5:
            self.environment.v_in = op.v_in

        self.environment.i_out = op.i_out

        time.sleep(self.idle_time)  # wait to stabilize

    def calculate_metrics(self, raw_data: List[float]) -> List[float]:
        v_in, i_in, v_out, i_out = raw_data

        p_out = v_out*i_out
        p_in = v_in*i_in
        eff = p_out/p_in

        raw_data.extend((p_out, p_in, eff))
        return raw_data

    def perform_measurement(self):
        data = [self.environment.v_in,
                self.environment.i_in,
                self.environment.v_out,
                self.environment.i_out]

        data = self.calculate_metrics(data)
        return data

    def execute(self) -> None:
        try:
            self.log_message('Initializing environment')
            self.environment.initialize()

            for op in self.iterate_conditions():

                self.log_message('Setting Operating Point:',
                                 f'\tv_in_set: {op.v_in} V',
                                 f'\ti_out_set: {op.i_out} A')
                self.setup_measurement(op)

                measurements = self.perform_measurement()
                measurements = [op.v_in, op.i_out, *measurements]  # add op
                self.log_message('Collected data:',
                                 '\n'.join(f'\t{n}: {v}' for n, v in zip(self.columns, measurements)))
                log_data(self.data_log, *measurements)

                self.log_message(f'Reducing Load to {self.idle_load} A',
                                 f'Allowing DUT to cool ({self.idle_time} s)')
                self.environment.i_out = self.idle_load
                time.sleep(self.idle_time)

        except Exception as e:
            self.log_message('An Error Occured while testing', e)

        else:
            self.log_message('Test Finished Successfully')

        finally:
            self.log_message('Shutting down environment')
            self.environment.shut_down()

    def log_message(self, *messages: str) -> None:

        with open(self.log_file, 'a') as file:
            for message in messages:
                file.write(str(message) + '\n')

        print(*messages, sep='\n')


def main() -> None:
    script_dir = Path(__file__).parent.resolve()  # path to this script

    equipment = connect_equipment(config=script_dir / 'equipment.config',
                                  init=True)
    env = Test_Environment(equipment)

    # location to save experiment results
    results_dir = script_dir.joinpath('results')
    results_dir.mkdir(exist_ok=True)

    # queue up test sequence
    experiments: List[Experiment] = []
    experiments.append(EfficiencyTest(env,
                                      v_in_conditions=(40, 48, 54, 60),
                                      i_out_conditions=range(0, 21, 1),
                                      output_dir=results_dir)
                       )

    for experiment in experiments:
        experiment.execute()


if __name__ == '__main__':
    main()
