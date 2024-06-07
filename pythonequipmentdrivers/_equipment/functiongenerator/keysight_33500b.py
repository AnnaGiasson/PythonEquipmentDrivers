from typing import Generator, Iterable, List, Tuple, Union

from ...core import VisaResource


class Keysight_33500B(VisaResource):
    """
    Keysight_33500B(address)

    address : str, address of the connected function generator

    object for accessing basic functionallity of the Keysight_33500B function
    generator

    For additional commands see programmers Manual:
    https://literature.cdn.keysight.com/litweb/pdf/33500-90901.pdf
    """

    valid_wave_types = (
        "ARB",
        "DC",
        "NOIS",
        "PRBS",
        "PULSE",
        "RAMP",
        "SIN",
        "SQU",
        "TRI",
    )

    def set_waveform_config(self, source: int = 1, **kwargs) -> None:
        """
        set_waveform_config(self, source, **kwargs)

        Sets multiple parameters to configure a waveform in one command.
        Parameters configured depend on the passed keyword arguements.

        Kwargs:
            wave_type (str, optional): Waveform type, valid options include
                'arb' (arbitrary), 'dc' (DC), 'nois' (noise), 'prbs' (?),
                'pulse' (pulse), 'ramp' (ramp), 'sin' (sine), 'squ' (square),
                and 'tri' (triangle).
            frequency (float, optional): Frequency of the waveform in Hz.
            amplitude (float, optional): Peak-to-peak amplitude of the waveform
                in Volts DC.
            offset (float, optional): DC offset voltage of the waveform in
                Volts DC.
            source (int, optional): Channel to configure (1,2). Defaults to 1.

        """

        wave_type = kwargs.get("wave_type", self.get_wave_type(source))
        frequency = kwargs.get("frequency", self.get_frequency(source))
        amplitude = kwargs.get("amplitude", self.get_voltage(source))
        offset = kwargs.get("offset", self.get_voltage_offset(source))

        self.write_resource(
            "SOUR{}:APPL:{} {}, {}, {}".format(
                source, wave_type, frequency, amplitude, offset
            )
        )

    def get_waveform_config(self, source: int = 1):
        response = self.query_resource(f"SOUR{source}:APPL?")

        response = response.replace('"', "")

        wave_type, wave_info = response.split()

        wave_type = wave_type.lower()
        freq, amp, off = map(float, wave_info.split(","))
        return (wave_type, freq, amp, off)

    def set_voltage_amplitude(self, amplitude: float, source: int = 1) -> None:
        self.write_resource(f"SOUR{source}:VOLT:AMPL {amplitude}")

    def get_voltage_amplitude(self, source: int = 1) -> float:
        response = self.query_resource(f"SOUR{source}:VOLT:AMPL?")
        return float(response)

    def set_voltage_offset(self, voltage: float, source: int = 1) -> None:
        self.write_resource(f"SOUR{source}:VOLT:OFFS {voltage}")

    def get_voltage_offset(self, source: int = 1) -> float:
        response = self.query_resource(f"SOUR{source}:VOLT:OFFS?")
        return float(response)

    def set_voltage_high(self, voltage: float, source: int = 1) -> None:
        self.write_resource(f"SOUR{source}:VOLT:HIGH {voltage}")

    def get_voltage_high(self, source: int = 1) -> float:
        response = self.query_resource(f"SOUR{source}:VOLT:HIGH?")
        return float(response)

    def set_voltage_low(self, voltage: float, source: int = 1) -> None:
        self.write_resource(f"SOUR{source}:VOLT:LOW {voltage}")

    def get_voltage_low(self, source: int = 1) -> float:
        response = self.query_resource(f"SOUR{source}:VOLT:LOW?")
        return float(response)

    def set_frequency(self, frequency: float, source: int = 1) -> None:
        self.write_resource(f"SOUR{source}:FREQ {frequency}")

    def get_frequency(self, source: int = 1) -> float:
        response = self.query_resource(f"SOUR{source}:FREQ?")
        return float(response)

    def set_wave_type(self, wave_type: str, source: int = 1) -> None:
        self.write_resource(f"SOUR{source}:FUNC {wave_type}")

    def get_wave_type(self, source: int = 1) -> str:
        response = self.query_resource(f"SOUR{source}:FUNC?")
        return response.lower()

    def set_pulse_dc(self, duty_cycle, source: int = 1) -> None:
        dc = round(duty_cycle, 2)
        self.write_resource(f"SOUR{source}:FUNC:PULSE:DCYC {dc}")

    def get_pulse_dc(self, source: int = 1) -> float:
        response = self.query_resource(f"SOUR{source}:FUNC:PULSE:DCYC?")
        return float(response)

    def set_pulse_width(self, width: float, source: int = 1) -> None:
        self.write_resource(f"SOUR{source}:FUNC:PULSE:WIDT {width}")

    def get_pulse_width(self, source: int = 1) -> float:
        response = self.query_resource(f"SOUR{source}:FUNC:PULSE:WIDT?")
        return float(response)

    def set_pulse_period(self, period: float, source: int = 1) -> None:
        self.write_resource(f"SOUR{source}:FUNC:PULSE:PER {period}")

    def get_pulse_period(self, source: int = 1) -> float:
        response = self.query_resource(f"SOUR{source}:FUNC:PULSE:PER?")
        return float(response)

    def set_pulse_edge_time(
        self, time: float, which: str = "both", source: int = 1
    ) -> None:

        which = which.upper()
        if which == "BOTH":
            self.write_resource(f"SOUR{source}:FUNC:PULSE:TRAN {time}")

        elif which in ["RISE", "RISING", "R", "LEAD", "LEADING"]:
            self.write_resource(f"SOUR{source}:FUNC:PULSE:TRAN:LEAD {time}")

        elif which in ["FALL", "FALLING", "F", "TRAIL", "TRAILING"]:
            self.write_resource(f"SOUR{source}:FUNC:PULSE:TRAN:TRA {time}")
        else:
            raise ValueError('Invalid arguement for arg "which"')

    def get_pulse_edge_time(self, which: str = "both", source: int = 1):
        cmd_str = f"SOUR{source}:FUNC:PULSE:TRAN"
        which = which.upper()
        if which == "BOTH":
            response = [
                self.query_resource(f"{cmd_str}LEAD?"),
                self.query_resource(f"{cmd_str}TRA?"),
            ]
        elif which in {"RISE", "RISING", "R", "LEAD", "LEADING"}:
            response = self.query_resource(f"{cmd_str}LEAD?")
        elif which in {"FALL", "FALLING", "F", "TRAIL", "TRAILING"}:
            response = self.query_resource(f"{cmd_str}TRA?")
        else:
            raise ValueError('Invalid option for "which" arg')

        if isinstance(response, list):
            return tuple(map(float, response))
        return float(response)

    def set_pulse_hold(self, param: str, source: int = 1) -> None:
        param = param.upper()
        if param not in ["DCYC", "WIDT"]:
            raise ValueError(f"Invalid param {param}, must by 'DCYC'/'WIDT'")
        self.write_resource(f"SOUR{source}:FUNC:PULSE:HOLD {param}")

    def get_pulse_hold(self, source: int = 1) -> str:
        response = self.query_resource(f"SOUR{source}:FUNC:PULSE:HOLD?")
        return response.lower()

    def set_square_dc(self, duty_cycle: float, source: int = 1) -> None:
        self.write_resource(f"SOUR{source}:FUNC:SQU:DCYC {duty_cycle}")

    def get_square_dc(self, source: int = 1) -> float:
        response = self.query_resource(f"SOUR{source}:FUNC:SQU:DCYC?")
        return float(response)

    def set_square_period(self, period: float, source: int = 1) -> None:
        self.write_resource(f"SOUR{source}:FUNC:SQU:PER {period}")

    def get_square_period(self, source: int = 1) -> float:
        response = self.query_resource(f"SOUR{source}:FUNC:SQU:PER?")
        return float(response)

    def set_burst_mode(self, mode: str, source: int = 1) -> None:
        mode = mode.upper()
        burst_modes = ("TRIG", "GAT")
        if mode not in burst_modes:
            raise ValueError(f"Invalid mode, valid modes are: {burst_modes}")
        self.write_resource(f"SOUR{source}:BURS:MODE {mode}")

    def get_burst_mode(self, source: int = 1) -> str:
        response = self.query_resource(f"SOUR{source}:BURS:MODE?")
        return response.lower()

    def set_burst_gate_polarity(self, polarity: str, source: int = 1) -> None:
        polarity = polarity.upper()
        if polarity not in ["NORM", "INV"]:
            raise ValueError('Invalid mode, valid modes are "NORM"/"INV"')
        self.write_resource(f"SOUR{source}:BURS:GATE:POL {polarity}")

    def get_burst_gate_polarity(self, source: int = 1) -> str:
        response = self.query_resource(f"SOUR{source}:BURS:GATE:POL?")
        return response.lower()

    def set_burst_ncycles(self, ncycles: int, source: int = 1) -> None:
        str_options = ["INF", "MIN", "MAX"]
        if isinstance(ncycles, int):
            self.write_resource(f"SOUR{source}:BURS:NCYC {ncycles}")
        elif isinstance(ncycles, str) and (ncycles.upper() in str_options):
            self.write_resource(f"SOUR{source}:BURS:NCYC {ncycles.upper()}")
        else:
            raise ValueError("invalid entry for ncycles")

    def get_burst_ncycles(self, source: int = 1) -> int:
        response = self.query_resource(f"SOUR{source}:BURS:NCYC?")
        return int(float(response))

    def set_burst_phase(self, phase: float, source: int = 1) -> None:
        str_options = ["MIN", "MAX"]
        if isinstance(phase, (float, int)):
            self.write_resource(f"SOUR{source}:BURS:PHASE {phase}")
        elif isinstance(phase, str) and (phase.upper() in str_options):
            self.write_resource(f"SOUR{source}:BURS:PHASE {phase.upper()}")
        else:
            raise ValueError("invalid entry for phase")

    def get_burst_phase(self, source: int = 1) -> float:
        response = self.query_resource(f"SOUR{source}:BURS:PHASE?")
        return float(response)

    def set_burst_state(self, state: bool, source: int = 1) -> None:
        self.write_resource(f"SOUR{source}:BURS:STAT {1 if state else 0}")

    def get_burst_state(self, source: int = 1) -> bool:
        response = self.query_resource(f"SOUR{int(source)}:BURS:STAT?")
        return bool(int(response))

    def trigger(self, source: int = 1) -> None:
        self.write_resource(f"TRIG{int(source)}")

    def get_trigger_count(self, source: int = 1) -> int:
        response = self.query_resource(f"TRIG{source}:COUN?")
        return int(float(response))

    def set_trigger_delay(self, delay: Union[float, int, str], source: int = 1) -> None:
        str_options = ["MIN", "MAX"]
        if isinstance(delay, (float, int)):
            self.write_resource(f"TRIG{source}:DEL {delay}")
        elif isinstance(delay, str) and (delay.upper() in str_options):
            self.write_resource(f"TRIG{source}:DEL {delay.upper()}")
        else:
            raise ValueError("invalid entry for delay")

    def get_trigger_delay(self, source: int = 1) -> float:
        response = self.query_resource(f"TRIG{source}:DEL?")
        return float(response)

    def set_trigger_source(self, trig_source: str, source: int = 1) -> None:
        trig_opts = {"IMM", "IMMEDIATE", "EXT", "EXTERNAL", "TIM", "TIMER", "BUS"}
        trig_source = trig_source.upper()
        if trig_source in trig_opts:
            self.write_resource(f"TRIG{source}:SOUR {trig_source}")
        else:
            raise ValueError(f"Invalid arg for trig_source ({trig_opts})")

    def get_trigger_source(self, source: int = 1) -> str:
        response = self.query_resource(f"TRIG{source}:SOUR?")
        return response.lower()

    @property
    def angle_unit(self) -> str:
        return self.query_resource("UNIT:ANGL?").strip().lower()

    def set_voltage_display_mode(self, mode: str) -> None:
        mode = mode.upper()
        if mode in {"AMPL", "HIGH", "AMPLITUDEOFF", "HIGHLOW"}:
            self.write_resource(f"DISP:UNIT:VOLT {mode}")
        else:
            raise ValueError('Invalid value for arg "mode"')

    @property
    def voltage_display_mode(self) -> str:
        response = self.query_resource("DISP:UNIT:VOLT?")
        return response.lower()

    def set_pulse_duration_display_mode(self, mode: str) -> None:
        mode = mode.upper()
        if mode in {"WIDT", "WIDTH", "DUTY"}:
            self.write_resource(f"DISP:UNIT:PULS {mode}")
        else:
            raise ValueError('Invalid value for arg "mode"')

    @property
    def pulse_duration_display_mode(self) -> str:
        response = self.query_resource("DISP:UNIT:PULS?")
        return response.lower()

    def set_horizontal_display_mode(self, mode: str) -> None:
        mode = mode.upper()
        if mode in {"FREQ", "FREQUENCY", "PER", "PERIOD"}:
            self.write_resource(f"DISP:UNIT:RATE {mode}")
        else:
            raise ValueError('Invalid value for arg "mode"')

    @property
    def horizontal_display_mode(self) -> str:
        response = self.query_resource("DISP:UNIT:RATE?")
        return response.lower()

    def set_output_state(self, state: bool, source: int = 1) -> None:
        self.write_resource(f"OUTP{source} {1 if state else 0}")

    def get_output_state(self, source: int = 1) -> bool:
        response = self.query_resource(f"OUTP{int(source)}?")
        return bool(int(response))

    def set_output_impedance(self, impedance, source: int = 1) -> None:
        """Valid options are 1-10k, min, max, and inf"""
        self.write_resource(f"OUTP{source}:LOAD {impedance}")

    def get_output_impedance(self, source: int = 1) -> float:
        response = self.query_resource(f"OUTP{source}:LOAD?")
        return float(response)

    def set_display_text(self, text: str) -> None:
        self.write_resource(f'DISP:TEXT "{text}"')

    def get_display_text(self) -> str:
        response = self.query_resource("DISP:TEXT?")
        return response.replace('"', "")

    def clear_display_text(self):
        return self.set_display_text("")

    @staticmethod
    def _clip_signal(
        data: Iterable[float], val_min: float, val_max: float
    ) -> Generator[float, None, None]:
        """
        _clip_signal(data, val_min, val_max)

        Clips the values of the iterable data to the range [val_min, val_max].
        values within this range are passed unmodifed.

        Args:
            data (Iterable[float]): A series of values to clip
            val_min (float): minimum value of output
            val_max (float): maximum value of output

        Yields:
            Generator[float, None, None]: input sequence clipped to the
                specified range.
        """

        for x in data:
            yield min(max(x, val_min), val_max)

    @staticmethod
    def _normalize(data: Iterable[float]) -> Generator[float, None, None]:
        """
        _normalize(data)

        Normalized the input sequence to the range +/- 1.

        Args:
            data (Iterable[float]): series of values to normalize

        Yields:
            Generator[float, None, None]: normalized sequence
        """

        val_min = min(data)
        val_max = max(data)

        norm_val = max(abs(val_min), abs(val_max))
        mid_val = (val_max + val_min) / 2

        for x in data:
            yield (x - mid_val) / (norm_val + mid_val)

    def store_arbitrary_waveform(self, data: Iterable[float], arb_name: str) -> None:
        """

        Stores an arbitrary waveform to the volatile memory of the function
        generator. The waveform will be stored as a normalized sequence (-1,
        1), its amplitude can be adjusted using the amplitude/offset or
        high/low settings of the waveform. Sequence should be between 8 and
        65535 samples.

        Args:
            data (Iterable[float]): arbitrary waveform sequence
            arb_name (str): alias used to access the saved waveform
        """

        if not (8 < len(data) < 65536):
            raise ValueError("data must be between 8 and 65536 samples")

        # send data
        self.write_resource(
            "SOUR:DATA:ARB1 {},{}".format(
                arb_name,
                ",".join(map(str, self._clip_signal(self._normalize(data), -1, 1))),
            )
        )

    def get_stored_waveform_names(self, source: int = 1) -> List[str]:
        """
        get_stored_waveform_names(source=1)

        Returns a list of aliases for arbitrary waveforms stored in the
        function generators volatile memory for the given channel.

        Args:
            source (int, optional): Channel to configure (1,2). Defaults to 1.

        Returns:
            List[str]: list of aliases
        """

        response = self.query_resource(f"SOUR{source}:DATA:VOL:CAT?")
        return response.replace('"', "").split(",")

    def clear_stored_waveforms(self) -> None:
        """
        clear_stored_waveforms()

        Clears the volatile memory of the function generator of all arbitrary
        waveforms and sequences.
        """

        self.write_resource("DATA:VOL:CLE")

    def set_arbitrary_waveform(self, arb_name: str, source: int = 1) -> None:
        """
        set_arbitrary_waveform(arb_name, source)

        Sets the arbitrary waveform file used by the function generator when
        the given channel is configured to use the ARB wave type.

        Args:
            arb_name (str): Alias of arbitrary waveform stored in the function
                generator
            source (int, optional): Channel to configure (1,2). Defaults to 1.
        """
        self.write_resource(f"SOUR{source}:FUNC:ARB {arb_name}")

    def get_arbitrary_waveform(self, source: int = 1) -> str:
        """
        get_arbitrary_waveform(source)

        Returns the arbitrary waveform file used by the function generator when
        the given channel is configured to use the ARB wave type.

        Args:
            source (int, optional): Channel to configure (1,2). Defaults to 1.

        Returns:
            str: Alias of arbitrary waveform stored in the function generator
        """

        return self.query_resource(f"SOUR{source}:FUNC:ARB?").replace('"', "")

    def set_arbitrary_waveform_sample_rate(
        self, sample_rate: float, source: int = 1
    ) -> None:
        """
        set_arbitrary_waveform_sample_rate(sample_rate, source=1)

        Sets the sample rate used for arbitrary waveforms on the given channel.

        Args:
            sample_rate (float): Sample rate in samples/sec
            source (int, optional): Channel to configure (1,2). Defaults to 1.
        """

        self.write_resource(f"SOUR{source}:FUNC:ARB:SRATE {sample_rate}")

    def get_arbitrary_waveform_sample_rate(self, source: int = 1) -> float:
        """
        get_arbitrary_waveform_sample_rate(source=1)

        Retrives the sample rate used for arbitrary waveforms on the specifed
        channel.

        Args:
            source (int, optional): Channel to configure (1,2). Defaults to 1.
        Returns:
            float: Sample rate in samples/sec
        """

        response = self.query_resource(f"SOUR{source}:FUNC:ARB:SRATE?")
        return float(response)

    def read_error_queue(self) -> List[Tuple[int, str]]:
        """
        read_error_queue()

        Reads the error queue of the function generator, return the queue as
        list. Errors are returned in the same order as the were logged within
        the function generator. Note: using this method to read the error queue
        will clear the error queue in the function generator.

        Returns:
            List[Tuple[int, str]]: error_code, error_message tuples for each
                error logged. If no errors have occured this list will be
                empty.
        """

        error_queue: List[Tuple[int, str]] = []

        while True:
            response = self.query_resource("SYST:ERR?")

            error_code, error_string = response.split(",")
            error_code = int(error_code)

            if error_code == 0:  # no error
                break

            error_queue.append((error_code, error_string))

        return error_queue
