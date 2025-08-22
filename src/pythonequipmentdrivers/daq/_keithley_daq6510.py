
from enum import Enum
from itertools import batched
from ..core import VisaResource


class Keithley_DAQ6510(VisaResource):

    def __init__(self, address, clear = False, **kwargs):
        super().__init__(address, clear, **kwargs)

        # check this is the correct device
        is_daq6510 = ('keithley' in self.idn.lower()) and ('daq6510' in self.idn.lower())
        if not is_daq6510:
            raise ValueError(
                f"Instrument at {address} is not a Keithley DAQ6510 data acquision system"
            )

        self.write_resource('*LANG SCPI')

        # Open all relays, start in a safe known state
        self.write_resource('ROUT:OPEN:ALL')

    def clear_registers(self) -> None:
        self.reset()
        self.clear()
        self.write_resource('STATus:PRESet')  # Clears event registers
        self.clear_buffer()

    def clear_buffer(self) -> None:
        self.write_resource('TRAC:CLE')

    def get_status(self) -> list[str]:  # TODO: Validate response under different status flags
        status_reg = int(self.query_resource('STAT:OPER:COND?'))

        bit_decoding = (
            "Measurement Summary", # B0
            "N/A",  # B1
            "Error Availible",
            "Questionable Summary",
            "Message Availible",
            "Event Summary",
            "Request for Service",  # B6
            "Operation Summary",  # B7
        )

        status_flags = []
        for n in range(len(bit_decoding)):
            if (status_reg >> n) & 0b1:
                status_flags.append(bit_decoding[n])

        return status_flags

    # def set_measurement_type(self, channel: int, type: Measurement_Type) -> None:
    #     self.write_resource(f'SENSe:FUNCtion "{type.value}", (@{channel})')

    class Measurement_Type(Enum):
        VOLTAGE_DC = "VOLT:DC"
        RESISTANCE = "RES"
        TEMPERATURE = "TEMP"
        VOLTAGE_AC = "VOLT:AC"
        CONTINUITY = "CONT"
        CURRENT_DC = "CURR:DC"
        DIODE = "DIOD"
        FREQUENCY = "FREQ:VOLT"
        CURRENT_AC = "CURR:AC"
        CAPACITANCE = "CAP"
        PERIOD = "PER:VOLT"
        NONE = "NONE"

    def set_function(self, function: Measurement_Type, *channels:int) -> None:

        function_str = function.value

        self.write_resource(f'FUNC "{function_str}", (@{",".join(map(str, channels))})')

    def get_function(self, *channels:int) -> tuple[Measurement_Type]:

        response = self.query_resource(f'Sense:Function? (@{",".join(map(str, channels))})')

        return tuple(
            self.Measurement_Type(channel_func) for channel_func in response.split(';')
        )

    def set_scan_channels(self, *channels: int) -> None:
        '''
        :param channel: simple channel 101 or range of channels (@101:120)
        '''
        self.write_resource(f'ROUT:SCAN (@{",".join(map(str, channels))})')

    def get_scan_channels(self) -> tuple[int]:
        response = self.query_resource('ROUT:SCAN?')
        str_channels = response[2:-1]  # strip off formatting characters

        if len(str_channels) == 0:  # no channels
            return tuple()

        if ":" not in str_channels:  # non contiguous channels
            return tuple(map(int, str_channels.split(',')))

        channel_list: list[int] = []
        for grouping in str_channels.split(','):
            if ':' not in grouping:
               channel_list.extend(map(int, grouping))
               continue

            start_channel, end_channel = map(int, grouping.split(':'))
            channel_list.extend(range(start_channel, end_channel+1, 1))

        return tuple(channel_list)

    def run_scan(self, count:int|None = None) -> None:

        if count is not None:
            self.set_scan_count(count)

        self.write_resource('INIT')

    def set_scan_count(self, count:int) -> None:
        self.write_resource(f'Route:scan:count:scan {count}')

    def get_scan_count(self) -> int:
        response = self.query_resource(f'Route:scan:count:scan?')
        return int(response)

    def fetch_scan_data(self,
        return_sample_time: bool = False
    ) -> dict[int, float|tuple[float,float]|list[float|tuple[float,float]]]:

        n_channels = len(self.get_scan_channels())
        n_samples = self.get_scan_count()

        START_INDEX = 1 # min value of 1
        BUFFER_NAME = "defbuffer1"
        read_type = 'chan,rel,read' if return_sample_time else 'chan,read'
        response = self.query_resource(f'trace:data? {START_INDEX}, {n_samples*n_channels}, "{BUFFER_NAME}", {read_type}')

        batched_data = batched(
            response.split(','),
            3 if return_sample_time else 2
        )

        data = {}
        for meas in batched_data:

            chan = int(meas[0])
            datum = tuple(map(float, meas[1:])) if return_sample_time else float(meas[1])

            if n_samples == 1:
                data[chan] = datum
                continue

            if chan not in data.keys():
                data[chan] = []

            data[chan].append(datum)
        return data


    def get_scan_status(self) -> dict[str, str|int]:  # TODO: Validate functionallity
        response = self.query_resource('ROUTe:scan:state?')

        state, scan_count, step_count = response.split(';')
        scan_count = int(scan_count)
        step_count = int(step_count)

        return {
            'state': state,
            'scan_count': scan_count,
            'step_count': step_count,
        }

    # TODO: Add method for adjusting range
    # TODO: Add method for adjusting aperture time
