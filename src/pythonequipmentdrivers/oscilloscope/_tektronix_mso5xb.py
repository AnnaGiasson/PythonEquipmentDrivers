from dataclasses import dataclass
from enum import Enum
from time import sleep
import numpy as np

from ..core import VisaResource


class Tektronix_MSO5xB(VisaResource):

    def __init__(self, address: str, **kwargs) -> None:
        super().__init__(address, **kwargs)

        identity = self.idn.split(",")
        if identity[0] != "TEKTRONIX" or identity[1][:3] != "MSO":
            raise ValueError(
                f"Instrument at {address} is not a Tektronix MSO oscilloscope."
            )

    def close(self) -> None:
        self.__del__()

    def reset(self) -> None:
        self.write_resource("clear")
        self.write_resource("fpanel:press singleseq")
        sleep(1)
        self.write_resource("fpanel:press runstop")
        self.write_resource("fpanel:press runstop")

    def save_screenshot(self, location: str, name: str) -> None:
        """
        :param location: Location screenshot will be saved on the user's PC
        :param name: Name of the .png file
        """

        # save image to temp location on scope
        self.write_resource('save:image "C:/Temp.png"')
        filename = f"{location}/{name}.png"
        self.query_resource("*OPC?")
        self.write_resource('filesystem:readfile "C:/Temp.png"')

        # transfer image to host
        imgdata = self.read_resource_raw(1024 * 1024)
        with open(filename, "wb") as file:
            file.write(imgdata)

        # erase image from scope storage
        self.write_resource('filesystem:delete "C:/Temp.png"')

    def configure_timebase(self, timescale: float, position: int) -> None:
        """
        :param position: Sets the horizontal location for the trigger point, 50 is in middle of screen
        :param timescale: Seconds/division on oscilloscope
        """
        self.write_resource(f"horizontal:scale {timescale}")
        self.write_resource(f"horizontal:position {position}")

    def configure_sample_rate(
        self,
        sample_rate: float,
        record_length: float,
        mode: str = "AUTO",
        configure: str = "recordlength",
    ) -> None:
        """
        :param sample_rate: Sets the sample rate when in MANUAL mode, ex. 1000000000 or 1e9 is 1 GS/s
        :param record_length: Sets the record length when in MANUAL mode, ex. 1000 or 1e3 is 1Kpts
        :param mode: Sets the horizontal mode determining how sample rate is handled, can be either AUTO or MANUAL
        :param configure: Sets whether the sample rate changes either the record length or timescale, input can either
            be HORIZONTALSCALE or RECORDLENGTH
        """
        self.write_resource(f"horizontal:mode {mode}")
        self.write_resource(f"horizontal:mode:manual:configure {configure}")
        self.write_resource(f"horizontal:mode:samplerate {sample_rate}")
        self.write_resource(f"horizontal:mode:recordlength {record_length}")

    def configure_channel(
        self,
        channel: int,
        scale: float,
        coupling: str,
        position: float,
        bandwidth: str = "FULL",
        enabled: bool = True,
        label_name: str = None,
    ) -> None:
        """
        :param channel: Channel number being configured
        :param scale: Vertical scale in either V/div or A/div depending on the probe, -1.0 is -1 divisions
        :param coupling: Input coupling can be DC, AC or DCREJect
        :param position: Position on the vertical scale
        :param bandwidth: Bandwidth of the selected channel, if the full bandwidth is desired pas the string FULL,
            otherwise pass the int value of the desired bandwidth, ex. 20E6 is 20MHz
        :param enabled: Turn the channel on or off
        :param label_name: Sets a label for the channel if a string is passed, if not then the label is set to blank
        """
        self.write_resource(f"ch{channel}:scale {scale}")
        self.write_resource(f"ch{channel}:coupling {coupling}")
        self.write_resource(f"ch{channel}:position {position}")
        self.write_resource(f"ch{channel}:bandwidth {bandwidth}")
        self.write_resource(f"display:global:ch{channel}:state {'ON' if enabled else 'OFF'}")
        self.write_resource(f'ch{channel}:label:name "{label_name if label_name else ""}"')


    def configure_digital_channel(
        self, channel: int, digital_channel: int, threshold: float, enabled: bool = True
    ) -> None:
        """
        :param channel: Channel number digital probe is connected to
        :param digital_channel: Digital channel being configured, 0-7
        :param threshold: Voltage trigger threshold for digital channel
        :param enabled: Turn the digital channel on or off
        """
        channel_state = "ON" if enabled else "OFF"
        self.write_resource(
            "display:waveview1:ch{}_d{}:state {}".format(
                channel, digital_channel, channel_state
            )
        )
        self.write_resource(
            "diggrp{}:d{}:threshold {}".format(channel, digital_channel, threshold)
        )

    def configure_edge_trigger(
        self, source: int, level: float, slope: str = "RISE", mode: str = "AUTO"
    ) -> None:
        """
        :param source: Channel used for trigger source
        :param level: Trigger level, 1 is 1V
        :param slope: Slope type used for trigger
        :param mode: Trigger in Auto or Normal mode
        """
        self.write_resource("trigger:a:type edge")
        self.write_resource(f"trigger:a:edge:source ch{source}")
        self.write_resource(f"trigger:a:edge:slope {slope}")
        self.write_resource(f"trigger:a:level:ch{source} {level}")
        self.write_resource(f"trigger:a:mode {mode}")

    def configure_timeout_trigger(
        self,
        source: int,
        level: float,
        polarity: str = "STAYSHIGH",
        time_limit: float = 4.0e-9,
        mode: str = "AUTO",
    ) -> None:
        """
        :param source: Channel used for trigger source
        :param level: Trigger level, 1 is 1V
        :param polarity: Specifies the polarity that will trigger the scope, can be STAYSHIGH, STAYSLOW or EITHER
        :param time_limit: Specifies the time the signal will be either high or low in order to trigger the scope, time
            is given in seconds
        :param mode: Trigger in Auto or Normal mode
        """
        self.write_resource("trigger:a:type timeout")
        self.write_resource(f"trigger:a:timeout:source ch{source}")
        self.write_resource(f"trigger:a:timeout:polarity {polarity}")
        self.write_resource(f"trigger:a:timeout:time {time_limit}")
        self.write_resource(f"trigger:a:level:ch{source} {level}")
        self.write_resource(f"trigger:a:mode {mode}")
    class TriggerMode(Enum):
        AUTO = "auto"
        NORM = "norm"

    def set_trigger_mode(self, mode: TriggerMode) -> None:
        self.write_resource(f"trigger:A:mode {mode.value}")

    def trigger_single(self) -> None:
        self.write_resource("FPAnel:PRESS SingleSeq")

    def trigger_force(self) -> None:
        self.write_resource("trigger force")

    def is_scope_triggered(self) -> bool:
        # response = self.query_resource('trigger:state?')
        # if response.strip().lower() in {'save', 'auto', 'trigger'}:
        #     return True
        # return False  # other two possible states are: 'ready', 'armed'

        response = self.query_resource("Acquire:NumAcq?")
        num_acquisitions = int(response)
        return num_acquisitions > 0

    def set_acquisition_state(self, state: bool) -> None:
        self.write_resource(f'acquire:state {"on" if state else "off"}')

    def get_acquisition_state(self) -> bool:
        response = self.query_resource("acquire:state?")
        return bool(int(response))

    def continuous_or_single_acquisition(self, continuous: bool = True) -> None:
        """
        :param continuous: Acquisition mode, True for continuous, False for single
        """
        self.write_resource(f"acquire:stopafter {'runstop' if continuous else 'sequence'}")

    def start_stop_acquisition(self, acquire: bool) -> None:
        """
        :param acquire: This command starts or stops acquisitions.  If the last acquisition was a single acquisition
            sequence, a new single sequence acquisition will be started. If the last acquisition was continuous, a new
            continuous acquisition will be started.
        """
        self.write_resource(f"acquire:state {'run' if acquire else 'stop'}")

    class Measurement(Enum):
        MEAN = "mean"
        MAX = "maximum"
        MIN = "minimum"
        RMS = "rms"
        HIGH = "high"
        LOW = "low"
        TOP = "top"
        BASE = "base"
        AMPLITUDE = "amplitude"
        PK2PK = "pk2pk"
        NOVERSHOOT = "novershoot"
        POVERSHOOT = "povershoot"
        FREQ = "frequency"
        PERIOD = "period"
        PDUTY = "pduty"
        NDUTY = "nduty"
        PWIDTH = "pwidth"
        NWIDTH = "nwidth"
        RISESR = "riseslewrate"
        FALLSR = "fallslewrate"
        RISETIME = "risetime"
        FALLTIME = "falltime"
        HIGHTIME = "hightime"
        LOWTIME = "lowtime"

    def add_measurement(
        self, measurement_index: int, channel: int, type: Measurement
    ) -> None:
        self.write_resource(f"measurement:AddNew MEAS{measurement_index}")
        self.write_resource(f"measurement:meas{measurement_index}:source CH{channel}")
        self.write_resource(f"measurement:meas{measurement_index}:type {type.value}")

    def get_measurement_config(self, measurement_index: int) -> tuple[int, Measurement]:
        response_source = self.query_resource(
            f"measurement:meas{measurement_index}:source?"
        )
        response_type = self.query_resource(
            f"measurement:meas{measurement_index}:type?"
        )

        return (
            int(
                response_source.rstrip("\n")[2:]
            ),  ### TODO: check that this works with various measurement sources
            self.Measurement(response_type.rstrip("\n").lower()),
        )

    def get_measurement(self, measurement_index: int) -> float:
        response = self.query_resource(
            f"measurement:meas{measurement_index}:results:CurrentAcq:mean?"
        )  ### TODO:see if theres a better command for this
        return float(response)

    @dataclass(frozen=True, slots=True)
    class StatisticalSummary:
        mean: float
        stdev: float
        min: float
        max: float
        n: int

    def get_measurement_statistics(self, measurement_index: int) -> StatisticalSummary:

        return self.StatisticalSummary(
            mean=float(
                self.query_resource(
                    f"measurement:meas{measurement_index}:results:allacqs:mean?"
                )
            ),
            stdev=float(
                self.query_resource(
                    f"measurement:meas{measurement_index}:results:allacqs:StdDev?"
                )
            ),
            max=float(
                self.query_resource(
                    f"measurement:meas{measurement_index}:results:allacqs:max?"
                )
            ),
            min=float(
                self.query_resource(
                    f"measurement:meas{measurement_index}:results:allacqs:min?"
                )
            ),
            n=int(
                self.query_resource(
                    f"measurement:meas{measurement_index}:results:allacqs:population?"
                )
            ),
        )

    def remove_measurement(self, *measurement_index: int) -> None:
        for idx in measurement_index:
            self.write_resource(f'measurement:delete "meas{idx}"')

    def remove_all_measurements(self) -> None:
        self.write_resource("measurement:DeleteAll")

    def measure_digital_period(self, channel: int, digital_channel: int) -> float:
        """
        :param channel: Channel that measurement will be taken from
        :param digital_channel: Digital measurement that measurement will be taken from, 0-7
        :return: The mean measurement of period
        """
        self.write_resource("measurement:addmeas period")
        self.write_resource(
            "measurement:meas1:source ch{}_d{}".format(channel, digital_channel)
        )
        sleep(1)
        result = self.query_resource("measurement:meas1:results:allacqs:mean?")
        self.write_resource('measurement:delete "meas1"')
        return float(result)

    def measure_digital_frequency(self, channel: int, digital_channel: int) -> float:
        """
        :param channel: Channel that measurement will be taken from
        :param digital_channel: Digital measurement that measurement will be taken from, 0-7
        :return: The mean measurement of frequency
        """
        self.write_resource("measurement:addmeas frequency")
        self.write_resource(
            "measurement:meas1:source ch{}_d{}".format(channel, digital_channel)
        )
        sleep(1)
        result = self.query_resource("measurement:meas1:results:allacqs:mean?")
        self.write_resource('measurement:delete "meas1"')
        return float(result)

    def measure_digital_positive_width(
        self, channel: int, digital_channel: int
    ) -> float:
        """
        :param channel: Channel that measurement will be taken from
        :param digital_channel: Digital measurement that measurement will be taken from, 0-7
        :return: The mean measurement of positive pulse width
        """
        self.write_resource("measurement:addmeas pwidth")
        self.write_resource(
            "measurement:meas1:source ch{}_d{}".format(channel, digital_channel)
        )
        sleep(1)
        result = self.query_resource("measurement:meas1:results:allacqs:mean?")
        self.write_resource('measurement:delete "meas1"')
        return float(result)

    def measure_digital_positive_duty(
        self, channel: int, digital_channel: int
    ) -> float:
        """
        :param channel: Channel that measurement will be taken from
        :param digital_channel: Digital measurement that measurement will be taken from, 0-7
        :return: The mean measurement of positive duty cycle
        """
        self.write_resource("measurement:addmeas pduty")
        self.write_resource(
            "measurement:meas1:source ch{}_d{}".format(channel, digital_channel)
        )
        sleep(1)
        result = self.query_resource("measurement:meas1:results:allacqs:mean?")
        self.write_resource('measurement:delete "meas1"')
        return float(result)

    def measure_digital_burstwidth(self, channel: int, digital_channel: int) -> float:
        self.write_resource("measurement:addmeas burstwidth")
        self.write_resource(
            "measurement:meas1:source ch{}_d{}".format(channel, digital_channel)
        )
        sleep(1)
        result = self.query_resource("measurement:meas1:results:allacqs:mean?")
        self.write_resource('measurement:delete "meas1"')
        return float(result)

    def add_new_bus(
        self,
        number: int,
        clock_source: str,
        bit_source: str,
        clocked: bool = False,
        clock_edge: str = "RISING",
        clock_threshold: float = 0.0,
        display_layout: str = "BUS",
        display_format: str = "HEX",
        bit_threshold: float = 0.0,
    ):
        """
        :param number: Bus Channel Number
        :param clock_source: If the bus is clocked the channel that acts as the clock source, input as a string and can
        be the following input types: CH<x>, CH<x>_D<x>, MATH<x>, REF<x>, REF<x>_D<x>, NONE.  <x> would be the number
        associated with the type of source.
        :param bit_source: The source that is used as the data input, input as a string and can be the following input
        types: CH<x>, CH<x>_D<x>, MATH<x>, REF<x>, REF<x>_D<x>, NONE.  <x> would be the number associated with the type
        of source.
        :param clocked: Asking if the bus is clocked or not, True is Yes False is No.
        :param clock_edge: If the bus is clocked what edge of the clock is the data being referenced to, input as a
        string and can be the following input types: RISING, FALLING, EITHER.
        :param clock_threshold: If the bus is clocked the threshold where the clock changes states, input as a floating
        number that refers to the voltage level.
        :param display_layout: The layout of the bus display on the scope, input as a string and can be the following
        input types: BUS or BUSANDWAVEFORM.
        :param display_format: The format in which the data is displayed, input as a string and can be the following
        input types: HEX or BINARY.
        :param bit_threshold: The threshold where the data bits change states, input as a floating number that refers to
        the voltage level.
        """
        self.write_resource('bus:addnew "B{}"'.format(number))
        self.write_resource("display:waveview1:bus:{}:state on")
        if clocked is True:
            self.write_resource("bus:B{}:parallel:clock:isclocked 1".format(number))
            self.write_resource(
                "bus:B{}:parallel:clocksource {}".format(number, clock_source)
            )
            self.write_resource(
                "bus:B{}:parallel:clock:edge {}".format(number, clock_edge)
            )
            self.write_resource(
                "bus:B{}:parallel:clocksource:threshold {}".format(
                    number, clock_threshold
                )
            )
        else:
            self.write_resource("bus:B{}:parallel:clock:isclocked 0".format(number))
        self.write_resource("bus:B{}:display:layout {}".format(number, display_layout))
        self.write_resource("bus:B{}:display:format {}".format(number, display_format))
        self.write_resource("bus:B{}:parallel:bit1source {}".format(number, bit_source))
        self.write_resource(
            "bus:B{}:parallel:bit1source:threshold {}".format(number, bit_threshold)
        )

    def add_bitsource(
        self, number: int, bit_number: int, bit_source: str, bit_threshold: float = 0.0
    ) -> None:
        """
        :param number: Bus Channel Number
        :param bit_number: Number of the bit this source is connecting with, structure is MSB to LSB.
        :param bit_source: The source that is used as the data input, input as a string and can be the following input
        types: CH<x>, CH<x>_D<x>, MATH<x>, REF<x>, REF<x>_D<x>, NONE.  <x> would be the number associated with the type
        of source.
        :param bit_threshold: The threshold where the data bits change states, input as a floating number that refers to
        the voltage level.
        """
        self.write_resource(f"bus:B{number}:parallel:bit{bit_number}source {bit_source}")
        self.write_resource(f"bus:B{number}:parallel:bit{bit_number}source:threshold {bit_threshold}")

    def delete_bus(self, number: int) -> None:
        """
        :param number: Bus Channel Number
        """
        self.write_resource(f'bus:delete "B{number}"')

    def add_bustable(self, number: int) -> None:
        """
        :param number: Bus Table Number
        """
        self.write_resource(f'bustable:addnew "Table{number}"')

    def save_bustable(self, location: str, name: str) -> None:
        """
        :param location: Location csv file will be saved on the user's PC
        :param name: Name of the .csv file
        """
        self.write_resource('save:eventtable:bus "C:/Temp.csv"')
        filename = f"{location}/{name}.csv"
        self.query_resource("*OPC?")
        self.write_resource('filesystem:readfile "C:/Temp.csv"')
        imgdata = self.read_resource_raw(1024 * 1024)
        with open(filename, "wb") as file:
            file.write(imgdata)
        self.write_resource('filesystem:delete "C:/Temp.csv"')

    def delete_bustable(self, number: int) -> None:
        """
        :param number: Bus Table Number
        """
        self.write_resource(f'bustable:delete "Table{number}"')

    def configure_waveform_cursor(
        self,
        enabled: bool = False,
        linked: bool = True,
        asource: int = 1,
        bsource: int = 1,
    ) -> None:
        """
        :param enabled: Enable or disable the cursor, True = Enabled, False = Disabled
        :param linked: Link the two parts of the cursor or make them independent, True = Linked, False = Independent
        :param asource: Channel source of the A part of the cursor, 1-6 which selects the scope channel
        :param bsource: Channel source of the B part of the cursor, 1-6 which selects the scope channel
        """
        state = "on" if enabled else "off"
        mode = "track" if linked else "independent"

        self.write_resource("display:select:view waveview1")
        self.write_resource(f"display:waveview1:cursor:cursor1:splitmode {'same' if asource == bsource else 'split'}")
        self.write_resource(f"display:waveview1:cursor:cursor1:state {state}")
        self.write_resource(f"display:waveview1:cursor:cursor1:mode {mode}")
        self.write_resource(f"display:waveview1:cursor:cursor1:asource CH{asource}")
        self.write_resource(f"display:waveview1:cursor:cursor1:bsource CH{bsource}")

    def set_waveform_cursor_position(
        self, aposition: float = 0.0, bposition: float = 0.0
    ) -> None:
        """
        :param aposition: Time axis position of the A part of the cursor, example 1.0e-6 = 1.0us on the time axis
        :param bposition: Time axis position of the B part of the cursor, example 1.0e-6 = 1.0us on the time axis
        """
        self.write_resource(f"display:waveview1:cursor:cursor1:waveform:aposition {aposition}")
        self.write_resource(f"display:waveview1:cursor:cursor1:waveform:bposition {bposition}")

    def get_waveform_cursor_vertical_positions(self) -> tuple[float, float]:
        """
        :return: Returns the vertical positions (Voltage) of the A and B parts of the cursor, A position is first number
        B position is second number
        """
        aposition = self.query_resource("display:waveview1:cursor:cursor1:hbars:aposition?")
        bposition = self.query_resource("display:waveview1:cursor:cursor1:hbars:bposition?")
        return float(aposition), float(bposition)

    def get_record_length(self) -> int:
        """
        get_record_length()

        retrives the current length of the waveform buffer.

        Returns:
            int: len of the waveform buffer
        """

        return int(self.query_resource("HOR:RECO?"))

    def get_channel_data(self, *channels: int, start: int = 1, end: int = None, return_time: bool = True) -> np.ndarray|list[np.ndarray]:
        """
        get_channel_data(*channels, start=1, end=None, return_time=True)

        Args:
            *channels (int): channel numbers to retrive data from
            start (int, optional): Start data point of the waveform data. Index of the captured waveform buffer.
                Defaults to 1 (first point).
            end (int, optional): End data point of the waveform data. Index of the captured waveform buffer.
                Defaults to None (last point).
            return_time (bool, optional): Whether to return the time vector. Defaults to True.

        Returns:
            np.ndarray|list[np.ndarray]: If return_time is True, the first element is the time vector, followed by the
                channel data in the order of the input channels. If return_time is False, only the channel data is returned.
                If only one vector is requested, a single np.ndarray is returned instead of a list.
        """

        def single_transfer(channel: int) -> np.ndarray:
            # Setup scope for transfer
            self.write_resource(f'DATa:SOUrce CH{channel}')
            self.write_resource(f'DATa:START {start}')  # in outer function scope for reuse for multiple channels
            self.write_resource(f'DATa:STOP {end}')     # in outer function scope for reuse for multiple channels
            self.write_resource("WFMOutpre:ENCdg BINARY")
            self.write_resource("WFMOutpre:BYT_Nr 1")
            N_points = int(self.query_resource('WFMOutpre:NR_P?'))

            # query data to rescale adc value back to the actual waveform later
            y_scale = float(self.query_resource('WFMOutpre:Ymult?'))
            y_off = float(self.query_resource('WFMOutpre:YZero?'))

            # read/parse data
            self.write_resource("CURVE?")
            raw_data = self.read_resource_raw()

            len_header = int(raw_data[1:2])  # start char, then N bytes in header
            data_start_index = 2 + len_header # skip over N-bytes in header as its just the waveform length (see N_point above)
            data = np.frombuffer(raw_data[data_start_index:-1], dtype=np.byte, count=N_points)

            # rescale data
            return y_scale*data + y_off


        # query horizontal extent and scaling info
        N_points = self.get_record_length()
        end = N_points if end is None else end

        if end > N_points:
            raise ValueError(f"End point {end} exceeds number of points available {N_points}")

        n_off = int(self.query_resource('WFMOutpre:PT_Off?'))
        dx = float(self.query_resource('WFMOutpre:XINcr?'))
        t_off = n_off * dx

        # query data and return
        vectors = []
        if return_time:
            vectors.append(np.arange(start, end+1)*dx - t_off)

        vectors.extend((single_transfer(channel) for channel in channels))

        return vectors if len(vectors) > 1 else vectors[0]
