
from enum import Enum
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

    def get_status(self) -> list[str]:
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

    def set_measurement_type(self, channel: int, type: Measurement_Type) -> None:
        self.write_resource(f'SENSe:FUNCtion "{type.value}", (@{channel})')