from ...core import VisaResource


class Agilent_33250A(VisaResource):
    """
    Agilent_33250A(address)

    address : str, address of the connected function generator

    object for accessing basic functionallity of the Agilent_33250A function
    generator
    """

    valid_wave_types = ("SIN", "SQU", "RAMP", "PULSE", "NOIS", "DC", "USER")

    def set_output_state(self, state: bool) -> None:
        self.write_resource(f"OUTP {1 if state else 0}")

    def get_output_state(self) -> bool:
        response = self.query_resource("OUTP?")
        return bool(int(response))

    def set_output_impedance(self, impedance) -> None:
        """
        Valid options are 1-10k, min, max, and inf
        """

        valid_str = ("MIN", "MAX", "INF")

        if isinstance(impedance, (float, int)):
            z = min((max((impedance, 10)), 10e3))
            self.write_resource(f"OUTP:LOAD {z}")
        elif isinstance(impedance, str) and (impedance.upper() in valid_str):
            self.write_resource(f"OUTP:LOAD {impedance.upper()}")

    def get_output_impedance(self) -> float:
        response = self.query_resource("OUTP:LOAD?")
        return float(response)

    def set_waveform_type(self, waveform: str) -> None:

        wave = str(waveform).upper()
        if wave in self.valid_wave_types:
            self.write_resource(f"FUNC {wave}")
        else:
            raise ValueError(
                "Invalide Waveform type. " f"Supported: {self.valid_wave_types}"
            )

    def get_waveform_type(self) -> str:
        response = self.query_resource("FUNC?")
        return response.upper()

    def set_voltage_amplitude(self, voltage: float) -> None:
        self.write_resource(f"VOLT {float(voltage)}")

    def get_voltage_amplitude(self) -> float:
        response = self.query_resource("VOLT?")
        return float(response)

    def set_voltage_offset(self, voltage: float) -> None:
        self.write_resource(f"VOLT:OFFS {float(voltage)}")

    def get_voltage_offset(self) -> float:
        response = self.query_resource("VOLT:OFFS?")
        return float(response)

    def set_voltage_high(self, voltage: float) -> None:
        self.write_resource(f"VOLT:HIGH {float(voltage)}")

    def get_voltage_high(self) -> float:
        response = self.query_resource("VOLT:HIGH?")
        return float(response)

    def set_voltage_low(self, voltage: float) -> None:
        self.write_resource(f"VOLT:LOW {float(voltage)}")

    def get_voltage_low(self) -> float:
        response = self.query_resource("VOLT:LOW?")
        return float(response)

    def set_frequency(self, frequency: float) -> None:
        self.write_resource(f"FREQ {float(frequency)}")

    def get_frequency(self) -> float:
        response = self.query_resource("FREQ?")
        return float(response)

    def set_voltage_auto_range(self, state: bool) -> None:
        self.write_resource(f"VOLT:RANG:AUTO {'ON' if state else 'OFF'}")

    def get_voltage_auto_range(self) -> bool:
        response = self.query_resource("VOLT:RANG:AUTO?")
        return "1" in response

    def set_burst_state(self, state: bool) -> None:
        self.write_resource(f"BURS:STAT {1 if state else 0}")

    def set_pulse_period(self, period: float) -> None:
        self.write_resource(f"PULSE:PER {period}")

    def get_pulse_period(self):
        response = self.query_resource("PULSE:PER?")
        return float(response)

    def set_pulse_width(self, width: float) -> None:
        self.write_resource(f"PULSE:WIDT {width}")

    def get_pulse_width(self) -> float:
        response = self.query_resource("PULSE:WIDT?")
        return float(response)

    def set_square_duty_cycle(self, dc: float) -> None:
        self.write_resource(f"FUNC:SQU:DCYCLE {dc}")

    def get_square_duty_cycle(self) -> float:
        response = self.query_resource("FUNC:SQU:DCYCLE?")
        return float(response)

    def get_burst_state(self, source: int = 1) -> bool:
        response = self.query_resource(f"SOUR{source}:BURS:STAT?")
        return bool(int(response))

    def set_burst_mode(self, mode: str) -> None:
        mode = mode.upper()
        burst_modes = ("TRIG", "GAT")
        if mode not in burst_modes:
            raise ValueError(f"Invalid mode, valid modes are: {burst_modes}")
        self.write_resource(f"BURS:MODE {mode}")

    def get_burst_mode(self) -> str:
        response = self.query_resource("BURS:MODE?")
        return response.lower()

    def set_burst_ncycles(self, ncycles: int) -> None:
        str_options = ["INF", "MIN", "MAX"]
        if isinstance(ncycles, int):
            self.write_resource(f"BURS:NCYC {ncycles}")
        elif isinstance(ncycles, str) and (ncycles.upper() in str_options):
            self.write_resource(f"BURS:NCYC {ncycles.upper()}")
        else:
            raise ValueError("invalid entry for ncycles")

    def get_burst_ncycles(self):
        response = self.query_resource("BURS:NCYC?")
        return int(float(response))

    def trigger(self) -> None:
        self.write_resource("TRIG")
