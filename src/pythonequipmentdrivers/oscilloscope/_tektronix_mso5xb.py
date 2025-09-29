from dataclasses import dataclass
from enum import Enum
from time import sleep

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
        self.write_resource("horizontal:scale {}".format(timescale))
        self.write_resource("horizontal:position {}".format(position))

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
        self.write_resource("horizontal:mode {}".format(mode))
        self.write_resource("horizontal:mode:manual:configure {}".format(configure))
        self.write_resource("horizontal:mode:samplerate {}".format(sample_rate))
        self.write_resource("horizontal:mode:recordlength {}".format(record_length))

    def configure_channel(
        self,
        channel: int,
        scale: float,
        coupling: str,
        position: float,
        bandwidth="FULL",
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
        if enabled is True:
            channel_state = "ON"
        else:
            channel_state = "OFF"
        self.write_resource("ch{}:scale {}".format(channel, scale))
        self.write_resource("ch{}:coupling {}".format(channel, coupling))
        self.write_resource("ch{}:position {}".format(channel, position))
        self.write_resource("ch{}:bandwidth {}".format(channel, bandwidth))
        self.write_resource(
            "display:global:ch{}:state {}".format(channel, channel_state)
        )
        if label_name is not None:
            self.write_resource('ch{}:label:name "{}"'.format(channel, label_name))
        else:
            self.write_resource('ch{}:label:name ""'.format(channel))

    def configure_digital_channel(
        self, channel: int, digital_channel: int, threshold: float, enabled: bool = True
    ) -> None:
        """
        :param channel: Channel number digital probe is connected to
        :param digital_channel: Digital channel being configured, 0-7
        :param threshold: Voltage trigger threshold for digital channel
        :param enabled: Turn the digital channel on or off
        """
        if enabled is True:
            channel_state = "ON"
        else:
            channel_state = "OFF"
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
        self.write_resource("trigger:a:edge:source ch{}".format(source))
        self.write_resource("trigger:a:edge:slope {}".format(slope))
        self.write_resource("trigger:a:level:ch{} {}".format(source, level))
        self.write_resource("trigger:a:mode {}".format(mode))

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
        self.write_resource("trigger:a:timeout:source ch{}".format(source))
        self.write_resource("trigger:a:timeout:polarity {}".format(polarity))
        self.write_resource("trigger:a:timeout:time {}".format(time_limit))
        self.write_resource("trigger:a:level:ch{} {}".format(source, level))
        self.write_resource("trigger:a:mode {}".format(mode))

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
        if continuous is True:
            self.write_resource("acquire:stopafter runstop")
        else:
            self.write_resource("acquire:stopafter sequence")

    def start_stop_acquisition(self, acquire: bool) -> None:
        """
        :param acquire: This command starts or stops acquisitions.  If the last acquisition was a single acquisition
            sequence, a new single sequence acquisition will be started. If the last acquisition was continuous, a new
            continuous acquisition will be started.
        """
        if acquire is True:
            self.write_resource("acquire:state run")
        else:
            self.write_resource("acquire:state stop")

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

    def measure_mean(self, channel: int) -> float:
        """
        :param channel: Channel that measurement will be taken from
        :return: The mean measurement of mean
        """
        self.write_resource("measurement:addmeas mean")
        self.write_resource("measurement:meas1:source CH{}".format(channel))
        sleep(1)
        result = self.query_resource("measurement:meas1:results:allacqs:mean?")
        self.write_resource('measurement:delete "meas1"')
        return float(result)

    def measure_maximum(self, channel: int) -> float:
        """
        :param channel: Channel that measurement will be taken from
        :return: The mean measurement of maximum
        """
        self.write_resource("measurement:addmeas maximum")
        self.write_resource("measurement:meas1:source CH{}".format(channel))
        sleep(1)
        result = self.query_resource("measurement:meas1:results:allacqs:maximum?")
        self.write_resource('measurement:delete "meas1"')
        return float(result)

    def measure_minimum(self, channel: int) -> float:
        """
        :param channel: Channel that measurement will be taken from
        :return: The mean measurement of maximum
        """
        self.write_resource("measurement:addmeas minimum")
        self.write_resource("measurement:meas1:source CH{}".format(channel))
        sleep(1)
        result = self.query_resource("measurement:meas1:results:allacqs:minimum?")
        self.write_resource('measurement:delete "meas1"')
        return float(result)

    def measure_falltime(self, channel: int) -> float:
        """
        :param channel: Channel that measurement will be taken from
        :return: The mean measurement of falltime
        """
        self.write_resource("measurement:addmeas falltime")
        self.write_resource("measurement:meas1:source CH{}".format(channel))
        sleep(1)
        result = self.query_resource("measurement:meas1:results:allacqs:mean?")
        self.write_resource('measurement:delete "meas1"')
        return float(result)

    def measure_risetime(self, channel: int) -> float:
        """
        :param channel: Channel that measurement will be taken from
        :return: The mean measurement of risetime
        """
        self.write_resource("measurement:addmeas risetime")
        self.write_resource("measurement:meas1:source CH{}".format(channel))
        sleep(1)
        result = self.query_resource("measurement:meas1:results:allacqs:mean?")
        self.write_resource('measurement:delete "meas1"')
        return float(result)

    def measure_rising_slew_rate(self, channel: int) -> float:
        """
        :param channel: Channel that measurement will be taken from
        :return: The mean measurement of rising slew rate
        """
        self.write_resource("measurement:addmeas riseslewrate")
        self.write_resource("measurement:meas1:source CH{}".format(channel))
        sleep(1)
        result = self.query_resource("measurement:meas1:results:allacqs:mean?")
        self.write_resource('measurement:delete "meas1"')
        return float(result)

    def measure_falling_slew_rate(self, channel: int) -> float:
        """
        :param channel: Channel that measurement will be taken from
        :return: The mean measurement of falling slew rate
        """
        self.write_resource("measurement:addmeas fallslewrate")
        self.write_resource("measurement:meas1:source CH{}".format(channel))
        sleep(1)
        result = self.query_resource("measurement:meas1:results:allacqs:mean?")
        self.write_resource('measurement:delete "meas1"')
        return float(result)

    def measure_frequency(self, channel: int) -> float:
        """
        :param channel: Channel that measurement will be taken from
        :return: The mean measurement of frequency
        """
        self.write_resource("measurement:addmeas frequency")
        self.write_resource("measurement:meas1:source CH{}".format(channel))
        sleep(1)
        result = self.query_resource("measurement:meas1:results:allacqs:mean?")
        self.write_resource('measurement:delete "meas1"')
        return float(result)

    def measure_positive_duty(self, channel: int) -> float:
        """
        :param channel: Channel that measurement will be taken from
        :return: The mean measurement of positive duty cycle
        """
        self.write_resource("measurement:addmeas pduty")
        self.write_resource("measurement:meas1:source CH{}".format(channel))
        sleep(1)
        result = self.query_resource("measurement:meas1:results:allacqs:mean?")
        self.write_resource('measurement:delete "meas1"')
        return float(result)

    def measure_period(self, channel: int) -> float:
        """
        :param channel: Channel that measurement will be taken from
        :return: The mean measurement of period
        """
        self.write_resource("measurement:addmeas period")
        self.write_resource("measurement:meas1:source CH{}".format(channel))
        sleep(1)
        result = self.query_resource("measurement:meas1:results:allacqs:mean?")
        self.write_resource('measurement:delete "meas1"')
        return float(result)

    def measure_positive_width(self, channel: int) -> float:
        """
        :param channel: Channel that measurement will be taken from
        :return: The mean measurement of positive pulse width
        """
        self.write_resource("measurement:addmeas pwidth")
        self.write_resource("measurement:meas1:source CH{}".format(channel))
        sleep(1)
        result = self.query_resource("measurement:meas1:results:allacqs:mean?")
        self.write_resource('measurement:delete "meas1"')
        return float(result)

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
        self.write_resource(
            "bus:B{}:parallel:bit{}source {}".format(number, bit_number, bit_source)
        )
        self.write_resource(
            "bus:B{}:parallel:bit{}source:threshold {}".format(
                number, bit_number, bit_threshold
            )
        )

    def delete_bus(self, number: int) -> None:
        """
        :param number: Bus Channel Number
        """
        self.write_resource('bus:delete "B{}"'.format(number))

    def add_bustable(self, number: int) -> None:
        """
        :param number: Bus Table Number
        """
        self.write_resource('bustable:addnew "Table{}"'.format(number))

    def save_bustable(self, location: str, name: str) -> None:
        """
        :param location: Location csv file will be saved on the user's PC
        :param name: Name of the .csv file
        """
        self.write_resource('save:eventtable:bus "C:/Temp.csv"')
        filename = "{}/{}.csv".format(location, name)
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
        self.write_resource('bustable:delete "Table{}"'.format(number))

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
        if enabled is True:
            state = "on"
        else:
            state = "off"
        if linked is True:
            mode = "track"
        else:
            mode = "independent"
        self.write_resource("display:select:view waveview1")
        self.write_resource("display:waveview1:cursor:cursor1:state {}".format(state))
        self.write_resource("display:waveview1:cursor:cursor1:mode {}".format(mode))
        self.write_resource(
            "display:waveview1:cursor:cursor1:asource CH{}".format(asource)
        )
        self.write_resource(
            "display:waveview1:cursor:cursor1:bsource CH{}".format(bsource)
        )

    def set_waveform_cursor_position(
        self, aposition: float = 0.0, bposition: float = 0.0
    ) -> None:
        """
        :param aposition: Time axis position of the A part of the cursor, example 1.0e-6 = 1.0us on the time axis
        :param bposition: Time axis position of the B part of the cursor, example 1.0e-6 = 1.0us on the time axis
        """
        self.write_resource(
            "display:waveview1:cursor:cursor1:waveform:aposition {}".format(aposition)
        )
        self.write_resource(
            "display:waveview1:cursor:cursor1:waveform:bposition {}".format(bposition)
        )

    def get_waveform_cursor_vertical_positions(self) -> tuple[str, str]:
        """
        :return: Returns the vertical positions (Voltage) of the A and B parts of the cursor, A position is first number
        B position is second number
        """
        aposition = self.query_resource(
            "display:waveview1:cursor:cursor1:hbars:aposition?"
        )
        bposition = self.query_resource(
            "display:waveview1:cursor:cursor1:hbars:bposition?"
        )
        return aposition[0:-1], bposition[0:-1]

    def save_waveform(
        self,
        source_type: str,
        source: int,
        location: str,
        name: str,
        gating_type: str = "none",
        resample_rate: int = 0,
    ):
        """
        :param source_type: Determines the source type of the waveform being saved to a CSV file, valid inputs are: CH,
            MATH, REF
        :param source: Number of the source being saved, ex. inputting 1 can be CH1, MATH1 or REF1
        :param location: Location CSV file will be saved on the user's PC
        :param name: Name of the CSV file
        :param gating_type: Specifies what parts of the waveform to save, valid inputs are:
            none - saves the full waveform data,
            cursors - save the waveform data located between the vertical cursors,
            screen - save the waveform data on the screen,
            resample - save the waveform data at a sample interval
        :param resample_rate: Sample rate that the waveform will be saved at if doing a resample, if at a rate of 2 then
            only every other data point is used, 3 would be every 3rd point etc.
        """
        self.write_resource("save:waveform:gating {}".format(gating_type))
        if gating_type == "resample":
            self.write_resource(
                "save:waveform:gating:resamplerate {}".format(resample_rate)
            )
        self.write_resource(
            'save:waveform {}{}, "C:/Temp.csv"'.format(source_type, source)
        )
        filename = "{}/{}.csv".format(location, name)
        self.query_resource("*OPC?")
        self.write_resource('filesystem:readfile "C:/Temp.csv"')
        imgdata = self.read_resource_raw(1024 * 1024)
        with open(filename, "wb") as file:
            file.write(imgdata)
        self.write_resource('filesystem:delete "C:/Temp.csv"')
