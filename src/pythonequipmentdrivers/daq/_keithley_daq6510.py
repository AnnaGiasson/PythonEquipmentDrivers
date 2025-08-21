
from enum import Enum
from itertools import batched
from ..core import VisaResource

class Measurement_Type(Enum):
    VOLTAGE_DC = "VOLTage[:DC]"
    RESISTANCE = "RESistance"
    TEMPERATURE = "TEMPerature"
    VOLTAGE_AC = "VOLTage:AC"
    CONTINUITY = "CONTinuity"
    CURRENT_DC = "CURRent[:DC]"
    DIODE = "DIODe"
    FREQUENCY = "FREQuency[:VOLTage]"
    CURRENT_AC = "CURRent:AC"
    CAPACITANCE = "CAPacitance"
    PERIOD = "PERiod[:VOLTage]"


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

    def select_function(self, function: str, *channels:int) -> None:  # TODO: update function arg to use Enum
        '''
        :param function: { VOLTage[:DC] | VOLTage:AC | CURRent[:DC] | CURRent:AC
                            | RESistance | FRESistance | TEMPerature | FREQuency
                            | PERiod | CONTinuity }
        :type function: string
        :param channel: simple channel 101 or range of channels (@101:120)
        :type channel: string
        '''
        self.write_resource(f'FUNC "{function}", (@{",".join(map(str, channels))})')

    def set_scan_channels(self, *channels: int) -> None:
        '''
        :param channel: simple channel 101 or range of channels (@101:120)
        '''
        self.write_resource(f'ROUT:SCAN (@{",".join(map(str, channels))})')

    def run_scan(self) -> None:
        self.write_resource('INIT')

    def set_scan_count(self, count:int) -> None:
        self.write_resource(f'Route:scan:count:scan {count}')

    def fetch_scan_data(self,
        n_samples: int,
        n_channels: int,
        return_sample_time: bool = False
    ) -> dict[int, list[float|list[float]]]:
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
    # TODO: Add method for configuring relay settings
