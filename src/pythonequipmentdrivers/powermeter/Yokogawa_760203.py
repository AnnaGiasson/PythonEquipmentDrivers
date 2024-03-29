from enum import Enum
from typing import List, Tuple, Union

from pythonequipmentdrivers import VisaResource


class MeasurementTypes(Enum):
    v_rms: int = 1
    i_rms: int = 2
    p: int = 3
    s: int = 4
    q: int = 5
    Lambda: int = 6
    phi: int = 7
    fu: int = 8
    fi: int = 9
    unused: int = 10


class HarmonicTypes(Enum):
    voltage: int = 1
    current: int = 2
    power: int = 3


class Yokogawa_760203(VisaResource):  # 3 phase
    """
    Yokogawa_760203(address)

    address : str, address of the connected power meter

    object for accessing basic functionallity of the Yokogawa_760203 powermeter

    For additional commands see programmers Manual:
    https://cdn.tmi.yokogawa.com/IM760201-17E.pdf
    """

    _CHANNEL_DATA_SEPARATION_INDEX: int = 10
    _LIST_DATA_SEPARATION_INDEX: int = 3

    def __init__(self, address: str, **kwargs) -> None:
        super().__init__(address, **kwargs)

        self.set_numeric_data_format('ascii')
        self.set_numeric_data_pattern(1)
        self.set_numeric_list_data_pattern(1)
        self.set_harmonic_order(0, 50)

    def set_numeric_data_format(self, option: str) -> None:
        """
        set_numeric_data_format(option)

        option: str, return datatype of queries to the meter
            valid options are "ascii" and "float"

        configures the datatype returned by queries to the meter
        """

        if option.lower() == "ascii":
            self.write_resource('NUM:FORM ASC')
        elif option.lower() == "float":
            self.write_resource('NUM:FORM FLO')
        else:
            raise ValueError('Unknown Option for Arguement option')

    def get_numeric_data_format(self) -> str:
        """
        get_numeric_data_format()

        returns the configuration the datatype returned by queries to the meter

        return: str
        """

        response = self.query_resource('NUM:FORM?')

        data_format = response.split(' ')[-1]
        data_format = data_format.rstrip('\n')

        if data_format == "ASC":
            return "ascii"
        elif data_format == "FLO":
            return "float"
        else:
            return 'error'

    def set_numeric_data_pattern(self, pattern_number: int) -> None:
        """
        valid presents are 1-4 (see datasheet page 5-91) constructer sets to 1
        """
        self.write_resource(f'NUM:NORM:PRES {pattern_number}')

    def set_numeric_list_data_pattern(self, pattern_number: int) -> None:
        """
        valid presents are 1-4 (see datasheet page 5-91) constructer sets to 1
        """
        self.write_resource(f'NUM:LIST:PRES {pattern_number}')

    def set_harmonic_pll_source(self, channel: int,
                                source_type: HarmonicTypes) -> None:

        if source_type == HarmonicTypes.voltage:
            source_id = 'U'
        elif source_type == HarmonicTypes.current:
            source_id = 'I'
        else:
            raise ValueError(f'Invalid Source type "{source_type}"')

        command_str = f"HARM:PLLS {source_id}{channel}"
        self.write_resource(command_str)

    def get_channel_data(self, channel: Union[int, str],
                         measurment: MeasurementTypes
                         ) -> float:

        if channel == 'sigma':
            channel = 4

        index = self._CHANNEL_DATA_SEPARATION_INDEX*(channel - 1)
        index += measurment.value
        response = self.query_resource(f"NUM:VAL? {index}")

        return float(response)

    def get_harmonic_pll_source(self) -> str:
        response = self.query_resource("HARM:PLLS?")
        return response.split(' ')[-1].rstrip('\n')

    def set_harmonic_order(self, order_min: int, order_max: int) -> None:
        self.write_resource(f"HARM:ORD {order_min},{order_max}")

    def get_harmonic_order(self) -> List[int]:
        response = self.query_resource("HARM:ORD?")
        response = response.split(' ')[-1].rstrip('\n')

        return [int(x) for x in response.split(',')]

    def get_harmonic_data(self, channel: int, harmonic_type: HarmonicTypes,
                          return_total=False
                          ) -> Union[List[float], Tuple[List[float], float]]:
        """
        get_harmonic_data(channel, harmonic_type, return_total=False)

        returns "harmonic_type" harmonics from specified channel
            valid options for harmonic_type are: 'voltage', 'current' or
            'power' if 'return_total' it will return a tuple
            (harmoincs, total) :: (list, float), else will just return the list
            of harmonics
        """

        # set harmonic source to correct channels voltage/current
        self.set_harmonic_pll_source(channel, harmonic_type)

        # get data
        index = self._LIST_DATA_SEPARATION_INDEX*(channel - 1)
        index += harmonic_type.value
        response = self.query_resource(f"NUM:LIST:VAL? {index}")

        harmonics = [float(x) for x in response.split(',')]
        if return_total:
            return harmonics[1:], harmonics[0]
        else:
            return harmonics[1:]

    def set_current_range(self, current: int) -> None:
        """
        set_current_range(current)

        current: int, current range in amps

        set the current range of all phases to use for current measurements.
        'current' parameter corresponds with the current level for the top of
        the range. The Yokogawa meter only has a discrete set of ranges, if the
        value specified by current doesn't correspond to one of these ranges
        the meter will select the closest valid range, this may result in the
        range not changing after this command
        is sent.
        """

        self.write_resource(f'CURR:RANG:ALL {current}')

    def get_current_range(self) -> Tuple[float]:
        """
        get_current_range(current)

        returns: current_ranges, tuple corresponding with the current ranges
                 used by each phase in order.

        get the current range of all phases to use for current measurements.
        each range returns the current level for the top of the range.
        """
        response = self.query_resource('CURR:RANG?')
        return tuple(float(chan.split()[-1]) for chan in response.split(';'))

    def get_voltage_rms(self, channel: int) -> float:
        """
        get_voltage_rms(channel)

        channel: int, channel to measure

        measures voltage present on "channel" in Vrms
        """

        return self.get_channel_data(channel, MeasurementTypes.v_rms)

    def get_current_rms(self, channel: int) -> float:
        return self.get_channel_data(channel, MeasurementTypes.i_rms)

    def get_power_real(self, channel: int) -> float:
        return self.get_channel_data(channel, MeasurementTypes.p)

    def get_power_apparent(self, channel: int) -> float:
        return self.get_channel_data(channel, MeasurementTypes.s)

    def get_power_reactive(self, channel: int) -> float:
        return self.get_channel_data(channel, MeasurementTypes.q)

    def get_power_factor(self, channel: int) -> float:
        return self.get_channel_data(channel, MeasurementTypes.Lambda)

    def get_phase_angle(self, channel: int) -> float:
        return self.get_channel_data(channel, MeasurementTypes.phi)

    def get_frequency_voltage(self, channel: int) -> float:
        return self.get_channel_data(channel, MeasurementTypes.fu)

    def get_frequency_current(self, channel: int) -> float:
        return self.get_channel_data(channel, MeasurementTypes.fi)

    def get_voltage_harmonics(self, channel: int, return_total: bool = False):
        return self.get_harmonic_data(channel, HarmonicTypes.voltage,
                                      return_total=return_total)

    def get_current_harmonics(self, channel: int, return_total: bool = False):
        return self.get_harmonic_data(channel, HarmonicTypes.current,
                                      return_total=return_total)

    def get_power_harmonics(self, channel: int, return_total: bool = False):
        return self.get_harmonic_data(channel, HarmonicTypes.power,
                                      return_total=return_total)
