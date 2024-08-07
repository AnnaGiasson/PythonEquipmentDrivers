from typing import Union
from dataclasses import dataclass
import itertools

from ..core import VisaResource


@dataclass
class SequenceStep:
    current: float
    trigger: bool


@dataclass
class PulseSeqConfig:
    """
    A class that holds the configuration for a load pulse sequence
    Args:
        pulse_current (float): current setting for the pulse in amps
        pulse_width (float): width of the pulse in seconds, will be rounded to a
            multiple of time_base
        trig_delay (float): delay seconds from the beginning of the pulse to when a
            trigger pulse shoud be emitted
        time_base (float): time duration in seconds of a single step in the sequence
        initial_idle_time (float): time to remain at idle_current before the pulse.
            Provides time for the load to turn on and stabilize in order to provide a
            consistent pulse profile.
        idle_current (float): current setting to go to before and after the pulse, amps

    """

    pulse_current: float
    pulse_width: float
    trig_delay: float
    time_base: float = 1e-3
    initial_idle_time: float = 10e-3
    idle_current: float = 0.0

    def __post_init__(self):
        END_IDLE_TIME = 1e-3
        MAX_NUM_STEPS = 1024
        MIN_TIME_BASE = 100e-6
        MAX_TIME_BASE = 100e-3

        if self.time_base > MAX_TIME_BASE or self.time_base < MIN_TIME_BASE:
            raise ValueError(
                f"time_base is outside of valid range ({MIN_TIME_BASE} - {MAX_TIME_BASE})"
            )

        total_sequence_length = (
            self.initial_idle_time + self.pulse_width + END_IDLE_TIME
        )
        if total_sequence_length / self.time_base > MAX_NUM_STEPS:
            min_time_base = total_sequence_length / MAX_NUM_STEPS
            raise ValueError(
                f"sequence requires too many steps, increase time base > {min_time_base}s"
            )


class Kikusui_PLZ1004WH(VisaResource):  # 1 kW
    """
    Kikusui_PLZ1004WH(address)

    address : str, address of the connected electronic load

    Programmers Manual:
    https://manual.kikusui.co.jp/P/PLZ4W/i_f_manual/english/00-intro.html
    """

    # need to update:
    #     logic
    #     documenation

    def set_state(self, state: bool) -> None:
        """
        set_state(state)

        Enables/disables the input for the load

        Args:
            state (bool): Load state (True == enabled, False == disabled)
        """

        self.write_resource(f"OUTP {1 if state else 0}")

    def get_state(self) -> bool:
        """
        get_state()

        Returns the current state of the input to the load

        Returns:
            bool: Load state (True == enabled, False == disabled)
        """

        response = self.query_resource("OUTP?")
        return int(response) == 1

    def on(self) -> None:
        """
        on()

        Enables the input for the load. Equivalent to set_state(True).
        """

        self.set_state(True)

    def off(self) -> None:
        """
        off()

        Disables the input for the load. Equivalent to set_state(False)
        """

        self.set_state(False)

    def toggle(self) -> None:
        """
        toggle()

        Reverses the current state of the load's input
        """

        self.set_state(self.get_state() ^ True)

    def set_mode(self, mode: str, cv: bool = False) -> None:
        """
        set_mode(mode, cv = False)

        mode: str, load type for the electronic load
            valid options are "CC", "CR", "CV", "CP"
        cv (optional): bool, option to add CV mode in addition to "mode" option
            only works in CC or CR mode

        changes the configuration of the electronic load.
        """

        mode = mode.upper()
        if mode in {"CC", "CR", "CV", "CP"}:

            if (mode in {"CC", "CR"}) and cv:
                self.write_resource(f"FUNC {mode}CV")
            else:
                self.write_resource(f"FUNC {mode}")
        else:
            raise ValueError("Invalid mode option")

    def get_mode(self) -> str:
        """
        get_mode()

        returns current configuration of the electronic load.
        """

        response = self.query_resource("FUNC?")
        return response

    def set_voltage(self, voltage: float) -> None:
        """
        set_voltage(voltage)

        Changes the voltage setpoint of the load in constant voltage.

        Args:
            voltage (float): Desired voltage setpoint in Volts DC.
        """

        self.write_resource(f"VOLT {voltage}")

    def get_voltage(self) -> float:
        """
        get_voltage()

        Reads the voltage setpoint of the load in constant voltage mode.

        Returns:
            float: Voltage setpoint in Volts DC.
        """

        response = self.query_resource("VOLT?")
        return float(response)

    def set_cc_range(self, cc_range: str) -> None:
        """
        set_cc_range(cc_range)

        cc_range: str, range to set for CC mode
            valid ranges are "LOW", "MED", and "HIGH"

        sets the range of allowable currents in CC mode.
        Note: with increased current capability comes decreased setpoint
        accuracy
        """

        cc_range = cc_range.upper()
        if cc_range in {"LOW", "MED", "HIGH"}:
            self.write_resource(f"CURR:RANG {cc_range}")
        else:
            raise ValueError("Invalid range option")

    def get_cc_range(self) -> str:
        """
        get_cc_range()

        returns the current range of allowable currents for CC mode.
        """

        response = self.query_resource("CURR:RANG?")
        return response

    def set_cr_range(self, cr_range: str) -> None:
        """
        set_cr_range(cc_range)

        cr_range: str, range to set for CR mode
            valid ranges are "LOW", "MED", and "HIGH"

        sets the range of allowable conductances in CR mode.
        Note: with increased current capability comes decreased setpoint
        accuracy
        """

        cr_range = cr_range.upper()
        if cr_range in {"LOW", "MED", "HIGH"}:
            self.write_resource(f"COND:RANG {cr_range}")
        else:
            raise ValueError("Invalid range option")

    def get_cr_range(self) -> str:
        """
        get_cr_range()

        returns the current range of allowable conductances for CR mode.
        """

        response = self.query_resource("COND:RANG?")
        return response

    def set_slew_rate(self, slew_rate: Union[float, str]) -> None:
        """
        set_slew_rate(slew_rate)

        Adjusts the slew-rate of the load used when transitioning between
        current setpoints or while trying to regulate the current, voltage,
        power, or resistence under dynamic conditions.

        Args:
            slew_rate (Union[float, str]): slew-rate to use in A/s or the
                string "max".
        """

        if isinstance(slew_rate, (float, int)):
            # set-point needs to be sent in A/us
            self.write_resource(f"CURR:SLEW {slew_rate*1e-6}")
        elif isinstance(slew_rate, str) and (slew_rate.upper() == "MAX"):
            self.write_resource(f"CURR:SLEW {slew_rate}")
        else:
            raise ValueError('slew_rate must be a float or the str "max"')

    def get_slew_rate(self) -> float:
        """
        get_slew_rate()

        Retrives the slew-rate of the load used when transitioning between
        current setpoints or while trying to regulate the current, voltage,
        power, or resistence under dynamic conditions.

        Returns:
            float: slew-rate currently used in A/s
        """

        response = self.query_resource("CURR:SLEW?")
        slew_rate = float(response) * 1e6  # return is in A/us
        return slew_rate

    def set_current(self, current: float) -> None:
        """
        set_current(current)

        Changes the current setpoint of the load in constant current mode.

        Args:
            current (float): Desired current setpoint in Amps DC.
        """

        self.write_resource(f"CURR {current}")

    def get_current(self) -> float:
        """
        get_current()

        Reads the current setpoint of the load in constant current mode.

        Returns:
            float: Current setpoint in Amps DC.
        """

        response = self.query_resource("CURR?")
        return float(response)

    def set_conductance(self, conductance: float) -> None:
        """
        set_conductance(conductance)

        conductance: float, desired conductance setpoint

        changes the conductance setpoint of the load
        """

        self.write_resource(f"COND {conductance}")

    def get_conductance(self) -> float:
        """
        get_conductance()

        reads the conductance setpoint of the load in Siemiens

        returns: float
        """

        response = self.query_resource("COND?")
        return float(response)

    def set_switching_state(self, state: bool) -> None:
        """
        set_switching_state(state)

        enable/disable the switching function on the load

        state: bool, whether to enable the switching functionallity of the load
        """

        self.write_resource(f"SOUR:PULS:STAT {1 if state else 0}")

    def get_switching_state(self) -> bool:
        """
        returns the whether or not the switching functionallity of the load is
        enabled

        returns: bool
        """

        response = self.query_resource("SOUR:PULS:STAT?")
        return int(response) == 1

    def set_duty_cycle(self, duty_cycle: float) -> None:
        """
        set_duty_cycle(duty_cycle)

        duty_cycle: float/int, duty cycle to set in percent
            valid options are in the range 0-100

        sets the duty cycle used when the switching functionallity of the load
        is enabled
        """

        self.write_resource(f"SOUR:PULS:DCYC {duty_cycle}")

    def get_duty_cycle(self) -> float:
        """
        get_duty_cycle()

        returns the duty cycle used when the switching functionallity of the
        load is enabled in percent

        returns: float
        """

        response = self.query_resource("SOUR:PULS:DCYC?")
        return float(response)

    def set_frequency(self, frequency: float) -> None:
        """
        set_frequency(frequency)

        frequency: float/int, frequency to set in Hz

        sets the frequency used when the switching functionallity of the load
        is enabled
        """

        self.write_resource(f"SOUR:PULS:FREQ {frequency}")

    def get_frequency(self) -> float:
        """
        get_frequency()

        gets the frequency used when the switching functionallity of the load
        is enabled in Hz
        """

        response = self.query_resource("SOUR:PULS:FREQ?")
        return float(response)

    def measure_voltage(self) -> float:
        """
        measure_voltage()

        Retrives measurement of the voltage present across the load's input.

        Returns:
            float: Measured Voltage in Volts DC
        """

        response = self.query_resource("MEAS:VOLT?")
        return float(response)

    def measure_current(self) -> float:
        """
        measure_current()

        Retrives measurement of the current present through the load.

        Returns:
            float: Measured Current in Amps DC.
        """

        response = self.query_resource("MEAS:CURR?")
        return float(response)

    def measure_power(self) -> float:
        """
        measure_power()

        Retrives measurement of the power dissipated by the load.

        Returns:
            float: Measured power in Watts.
        """

        response = self.query_resource("MEAS:POW?")
        return float(response)

    def configure_sequence(
        self,
        steps: list[SequenceStep],
        current_range: str = "HIGH",
        step_size: float = 1e-3,
        initialize: bool = True,
    ):
        MIN_STEP_SIZE = 100e-6
        MAX_STEP_SIZE = 100e-3
        VALID_RANGES = {"LOW", "MEDIUM", "MED", "HIGH"}
        MAX_SEQ_LENGTH = 1024

        sequence_len = len(steps)

        if sequence_len > MAX_SEQ_LENGTH:
            raise ValueError(f"sequence length is {sequence_len} > {MAX_SEQ_LENGTH=}")
        if not current_range.upper() in VALID_RANGES:
            raise ValueError(f"{current_range=} is not in {VALID_RANGES=}")
        if step_size > MAX_STEP_SIZE or step_size < MIN_STEP_SIZE:
            raise ValueError(f"step_size must be <{MAX_STEP_SIZE} and >{MIN_STEP_SIZE}")

        if initialize:
            # fast sequence requires 11, select it for editing
            self.write_resource("prog:name 11")
            # set sequence to fast CC mode
            self.write_resource("prog:mode fcc")
            # run the sequence just once
            self.write_resource("prog:loop 1")
            # set the step length
            self.write_resource(f"prog:fsp:time {step_size}")
            # set the current range for the sequence
            self.write_resource(f"prog:cran {current_range}")
            # set the sequence length
            self.write_resource(f"prog:fsp:end {sequence_len}")

        # Write the sequence of currents in chunks of 8 using prog:fsp:edit:wave
        # to reduce number of transactions. Write individual steps only when
        # a trigger pulse is needed
        for steps_chunk, first_step_idx in zip(
            itertools.batched(steps, 8),
            itertools.count(start=1, step=8),
        ):
            currents = [step.current for step in steps_chunk]
            # pad the chunk of currents up to 8 with 0s
            currents += (8 - len(currents)) * [0]
            # write the chunk of currents
            self.write_resource(
                f"prog:fsp:edit:wave {first_step_idx},"
                + ",".join(str(c) for c in currents)
            )

            # set the steps that have triggers
            for offset, step in enumerate(steps_chunk):
                if not step.trigger:
                    continue
                step_idx = first_step_idx + offset
                # store the current of the step
                curr = self.query_resource(f"prog:fsp:edit? {step_idx}")
                # write the step with a trigger
                self.write_resource(f"prog:fsp:edit {step_idx},{curr},1")
