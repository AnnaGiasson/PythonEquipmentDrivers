from pythonequipmentdrivers import Scpi_Instrument
import numpy as np
from time import sleep
from typing import Union, Tuple


# custom type, either one float or a tuple of two floats
OneOrMoreFloat = Union[float, Tuple[float, float]]


class Chroma_63206A(Scpi_Instrument):  # 6 kW
    """
    Chroma_63206A(address)

    address : str, address of the connected electronic load

    object for accessing basic functionallity of the Chroma_63206A DC load
    """

    def __init__(self, address: str, **kwargs) -> None:
        super().__init__(address, **kwargs)
        self.supported_modes = ("CC", "CR", "CP", "CCD")

    def set_state(self, state: bool) -> None:
        """
        set_state(state)

        Enables/disables the input for the load

        Args:
            state (bool): Load state (True == enabled, False == disabled)
        """

        self.instrument.write(f"LOAD {1 if state else 0}")

    def get_state(self) -> bool:
        """
        get_state()

        Returns the current state of the input to the load

        Returns:
            bool: Load state (True == enabled, False == disabled)
        """

        response = self.instrument.query("LOAD?")

        if response.rstrip('\n') == "ON":
            return True
        return False

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

    def toggle(self, return_state: bool = False) -> Union[None, bool]:
        """
        toggle(return_state=False)

        Reverses the current state of the load's input
        If return_state = True the boolean state of the load after toggle() is
        executed will be returned

        Args:
            return_state (bool, optional): [description]. Defaults to False.

        Returns:
            Union[None, bool]: If return_state == True returns the Load state
                (True == enabled, False == disabled), else returns None
        """

        if self.get_state():
            self.off()
        else:
            self.on()

        if return_state:
            return self.get_state()

    def set_short_state(self, state: bool) -> None:
        """
        set_short_state(state)

        Enables/Disables the short circuit feature for the load.

        Args:
            state (bool): True == Enable, False == Disable
        """

        self.instrument.write(f"LOAD:SHOR {1 if state else 0}")

    def get_short_state(self) -> bool:
        """
        get_short_state()

        Retrives the current state of the loads short circuit feature.

        Returns:
            bool: True == Enable, False == Disable
        """

        response = self.instrument.query("LOAD:SHOR?")
        if int(response) == 1:
            return True
        return False

    def set_mode(self, mode: str, range_setting: Union[int, str] = 2) -> None:
        """
        set_mode(mode, range_setting=0)

        range_setting (optional): int, range of the desired mode setting
            valid options are 0, 1, and 2 for low, medium, and high
            respectively. Default is 0

        Sets the desired load configuration. Currently supported options in
        this library are
        "CC", "CR", "CP", and "CCD".
        """

        valid_modes = ("CC", "CR", "CP", "CCD")
        valid_ranges = ("L", "M", "H")

        # check arguements
        if str(mode).upper() not in valid_modes:
            raise ValueError('Invalid option for arguement "mode"')

        if isinstance(range_setting, int):
            if int(range_setting) in range(0, 3):
                range_string = valid_ranges[range_setting]
            else:
                raise ValueError('Invalid option for the int "range_setting"')
        elif isinstance(range_setting, str):
            if range_setting.upper() in valid_ranges:
                range_string = range_setting.upper()
            else:
                raise ValueError('Invalid option for the str "range_setting"')

        self.instrument.write(f"MODE {mode}{range_string}")

    def get_mode(self) -> Tuple[str, str]:
        """
        get_mode(self)

        Returns the current configuration of the electronic load
        """

        response = self.instrument.query("MODE?")

        response = response.strip()
        mode = response[:-1]
        range_setting = response.removeprefix(mode)

        return (mode, range_setting)

    def set_current(self, current: float, channel: int = 0) -> None:
        """
        set_current(current, channel=0)

        Changes the current setpoint of the load for the specified channel in
        constant current mode. if channel = 0 both channels will be set to the
        value specified.

        Args:
            current (float): Desired current setpoint
            channel (int, optional): Load Channel to adjust. For this load,
                valid channels are 1, 2, and 0. Defaults to 0.
        """

        if int(channel) == 0:
            self.instrument.write(f'CURR:STAT:L1 {float(current)}')
            self.instrument.write(f'CURR:STAT:L2 {float(current)}')
        else:
            cmd_str = f'CURR:STAT:L{int(channel)} {float(current)}'
            self.instrument.write(cmd_str)

    def get_current(self, channel: int) -> OneOrMoreFloat:
        """
        get_current(channel)

        Reads the current setpoint of the load for the specified channel in
        constant current mode. If channel == 0, then the setpoints for both
        channels will be returned.

        Args:
            channel (int): Channel to query. For this load, valid channels are
                1, 2, and 0.

        Returns:
            OneOrMoreFloat: Desired current setpoint. If channel == 0 then the
                setpoints for both channels will be returned in a tuple ordered
                by channel number.
        """

        if int(channel) == 0:
            response1 = self.instrument.query('CURR:STAT:L1?')
            response2 = self.instrument.query('CURR:STAT:L2?')
            return (float(response1), float(response2))

        else:
            response = self.instrument.query(f'CURR:STAT:L{int(channel)}?')
            return float(response)

    def set_dynamic_current(self, current: float, channel: int = 0) -> None:
        """
        set_dynamic_current(current, channel=0)

        Changes the current setpoint of the load for the specified channel in
        dynamic current mode. if channel = 0 both channels will be set to the
        value specified.

        Args:
            current (float): Desired current setpoint
            channel (int, optional): Load Channel to adjust. For this load,
                valid channels are 1, 2, and 0. Defaults to 0.
        """

        if int(channel) == 0:
            self.instrument.write(f'CURR:DYN:L1 {float(current)}')
            self.instrument.write(f'CURR:DYN:L2 {float(current)}')
        else:
            self.instrument.write(f'CURR:DYN:L{int(channel)} {float(current)}')

    def get_dynamic_current(self, channel: int) -> OneOrMoreFloat:
        """
        get_dynamic_current(channel)

        Reads the current setpoint of the load for the specified channel in
        dynamic current mode. If channel == 0, then the setpoints for both
        channels will be returned.

        Args:
            channel (int): Channel to query. For this load, valid channels are
                1, 2, and 0.

        Returns:
            OneOrMoreFloat: Desired current setpoint. If channel == 0 then the
                setpoints for both channels will be returned in a tuple ordered
                by channel number.
        """

        if int(channel) == 0:
            response1 = self.instrument.query('CURR:DYN:L1?')
            response2 = self.instrument.query('CURR:DYN:L2?')
            return (float(response1), float(response2))

        else:
            response = self.instrument.query(f'CURR:DYN:L{int(channel)}?')
            return float(response)

    def set_dynamic_current_time(self, t: float, channel: int) -> None:
        """
        set_dynamic_current_time(t, channel=0)

        t: float, desired duration of dynamic setpoint in seconds.
        channel (optional): int, channel to change setpoint of.
            valid options are 0,1,2 (default is 0)

        changes the duration of the dynamic current setpoint of the load for
        the specified channel in dynamic current mode.
        if channel = 0 both channels will be set to the value specified
        """
        if int(channel) == 0:
            self.instrument.write(f'CURR:DYN:T1 {float(t)}')
            self.instrument.write(f'CURR:DYN:T2 {float(t)}')
        else:
            self.instrument.write(f'CURR:DYN:T{int(channel)} {float(t)}')

    def get_dynamic_current_time(self, channel: int) -> OneOrMoreFloat:
        """
        get_dynamic_current_time(channel)

        channel: int, channel to get duration of.
            valid options are 1,2

        reads the duration of the dynamic current setpoint of the load for the
        specified channel in dynamic current mode.
        """

        if int(channel) == 0:
            response1 = self.instrument.query('CURR:DYN:T1?')
            response2 = self.instrument.query('CURR:DYN:T2?')
            return (float(response1), float(response2))
        else:
            response = self.instrument.query(f'CURR:DYN:T{int(channel)}?')
            return float(response)

    def set_dynamic_current_repeat(self, n: int) -> None:
        """
        set_dynamic_current_repeat(n)

        n: int, desired number of cycles to repeat the two dyanmic current
        setpoints.

        changes the number of cycles to alternate between the two dynamic
        current setpoints before turning off. Cycles begin when the output of
        the load is enabled, after completion load will automatically turn
        itself off. if n = 0 the load will indefinately cycle between the two
        setpoints.
        """

        self.instrument.write(f"CURR:DYN:REP {int(n)}")

    def get_dynamic_current_repeat(self) -> int:
        """
        get_dynamic_current_repeat()

        returns the number of cycles to alternate between the two dynamic
        current setpoints before turning off. Cycles begin when the output of
        the load is enabled, after completion load will automatically turn
        itself off. if n = 0 the load will indefinately cycle between the two
        setpoints.
        """

        response = self.instrument.query("CURR:DYN:REP?")
        return int(response)

    def set_dynamic_current_rise_rate(self, slew_rate: float) -> None:
        """
        set_dynamic_current_rise_rate(slew_rate)

        slew_rate: float, slew rate of the rising edge of current setpoint
                   transitions, A/us

        sets the slew rate for the rising edge between the two dynamic current
        setpoint in dynamic current mode.
        """
        self.instrument.write(f"CURR:DYN:RISE {float(slew_rate)}")

    def get_dynamic_current_rise_rate(self) -> float:
        """
        get_dynamic_current_rise_rate()

        returns the slew rate for the rising edge between the two dynamic
        current setpoint in dynamic current mode.
        """
        response = self.instrument.query("CURR:DYN:RISE?")
        return float(response)

    def set_dynamic_current_fall_rate(self, slew_rate: float) -> None:
        """
        set_dynamic_current_fall_rate(slew_rate)

        slew_rate: float, slew rate of the falling edge of current setpoint
        transitions, A/us

        sets the slew rate for the falling edge between the two dynamic current
        setpoint in
        dynamic current mode.
        """
        self.instrument.write(f"CURR:DYN:FALL {float(slew_rate)}")

    def get_dynamic_current_fall_rate(self) -> float:
        """
        get_dynamic_current_fall_rate()

        returns the slew rate for the falling edge between the two dynamic
        current setpoint in dynamic current mode.
        """
        response = self.instrument.query("CURR:DYN:FALL?")
        return float(response)

    def set_resistance(self, resistance: float, channel: int = 0) -> None:
        """
        set_resistance(resistance, channel=0)

        resistance: float, desired resistance setpoint
        channel (optional): int, channel to change setpoint of.
            valid options are 0,1,2 (default is 0)

        changes the resistance setpoint of the load for the specified channel
        in constant resistance mode. if channel = 0 both channels will be set
        to the value specified
        """

        if int(channel) == 0:
            self.instrument.write(f"RES:STAT:L1 {float(resistance)}")
            self.instrument.write(f"RES:STAT:L2 {float(resistance)}")
        else:
            cmd_str = f"RES:STAT:L{int(channel)} {float(resistance)}"
            self.instrument.write(cmd_str)

    def get_resistance(self, channel: int) -> float:
        """
        get_resistance(channel)

        channel: int, channel to get setpoint of.
            valid options are 1,2

        reads the resistance setpoint of the load for the specified channel in
        constant resistance mode
        """

        response = self.instrument.query(f"RES:STAT:L{int(channel)}?")
        return float(response)

    def set_voltage(self, voltage: float, channel: int = 0) -> None:
        """
        set_voltage(voltage, channel=0)

        voltage: float, desired voltage setpoint
        channel (optional): int, channel to change setpoint of.
            valid options are 0,1,2 (default is 0)

        changes the voltage setpoint of the load for the specified channel in
        constant voltage mode if channel = 0 both channels will be set to the
        value specified
        """
        if int(channel) == 0:
            self.instrument.write(f"VOLT:STAT:L1 {float(voltage)}")
            self.instrument.write(f"VOLT:STAT:L2 {float(voltage)}")
        else:
            cmd_str = f"VOLT:STAT:L{int(channel)} {float(voltage)}"
            self.instrument.write(cmd_str)

    def get_voltage(self, channel: int) -> float:
        """
        get_voltage(channel)

        channel: int, channel to get setpoint of.
            valid options are 1,2

        reads the voltage setpoint of the load for the specified channel in
        constant voltage mode
        """

        response = self.instrument.query(f"VOLT:STAT:L{int(channel)}?")
        return float(response)

    def set_cv_current(self, current: float) -> None:
        """
        set_cv_current(current)

        current: float, desired current setpoint

        changes the current setpoint of the load in constant voltage mode
        """

        self.instrument.write(f"VOLT:STAT:ILIM {float(current)}")

    def get_cv_current(self) -> float:
        """
        get_cv_current()

        reads the current setpoint of the load in constant voltage mode
        """

        response = self.instrument.query("VOLT:STAT:ILIM?")
        return float(response)

    def set_power(self, power: float, channel: int = 0) -> None:
        """
        set_power(power, channel=0)

        power: float, desired power setpoint
        channel (optional): int, channel to change setpoint of.
            valid options are 0,1,2 (default is 0)

        changes the power setpoint of the load for the specified channel in
        constant power mode. if channel = 0 both channels will be set to the
        value specified
        """

        if int(channel) == 0:
            self.instrument.write(f'POW:STAT:L1 {float(power)}')
            self.instrument.write(f'POW:STAT:L2 {float(power)}')
        else:
            self.instrument.write(f'POW:STAT:L{int(channel)} {power}')

    def get_power(self, channel: int) -> float:
        """
        get_power(channel)

        channel: int, channel to get the setpoint of.
            valid options are 1,2

        reads the power setpoint of the load for the specified channel in
        constant power mode
        """

        response = self.instrument.query(f'POW:STAT:L{int(channel)}?')
        return float(response)

    def measure_voltage(self) -> float:
        """
        measure_voltage()

        Retrives measurement of the voltage present across the load's input.

        Returns:
            float: Measured Voltage in Volts DC
        """

        response = self.instrument.query('FETC:VOLT?')
        return float(response)

    def measure_current(self) -> float:
        """
        measure_current()

        Retrives measurement of the current present through the load.

        Returns:
            float: Measured Current in Amps DC
        """

        response = self.instrument.query('FETC:CURR?')
        return float(response)

    def measure_power(self) -> float:
        """
        measure_power()

        Retrives measurement of the power dissipated by the load.

        Returns:
            float: Measured power in Watts.
        """

        response = self.instrument.query('FETC:POW?')
        return float(response)

    def pulse(self, level: float, duration: float) -> None:
        """
        duration: float/int, duration of the "high" state of the pulse in
                  seconds
        """
        """
        pulse(level, duration)

        Generates a square pulse with height and duration specified by level
        and duration. The load will start and return to the previous current
        level set on the load before the execution of pulse(). "level" can be
        less than or greater than the previous current setpoint.

        Args:
            level (float): current level of pulse in Amps DC
            duration (float): duration of the pulse in seconds
        """

        start_level = self.get_current(1)

        self.set_current(float(level))
        sleep(duration)
        self.set_current(start_level)

    def ramp(self, start: float, stop: float, n: int = 100,
             dt: float = 0.01) -> None:
        """
        ramp(start, stop, n=100, dt=0.01)

        Generates a linear ramp on the loads current specified by the
        parameters start, stop, n, and dt.
        The input of the load should be enabled before executing this command.
        "start" can be higher than "stop" or vise-versa. The minimum dt is
        limited by the communication speed of the interface used to communicate
        with this device.

        Args:
            start (float): initial current setpoint of the ramp in Amps DC.
            stop (float): final current setpoint of the ramp in Amps DC.
            n (int, optional): Number of points in the ramp between "start" and
                "stop". Defaults to 100.
            dt (float, optional): Time between changes in the value of the
                setpoint in seconds. Defaults to 0.01.
        """

        for i in np.linspace(float(start), float(stop), int(n)):
            self.set_current(i)
            sleep(dt)

    def slew(self, start: float, stop: float, n: int = 100,
             dt: float = 0.01, dwell: float = 0) -> None:
        """
        slew(start, stop, n=100, dt=0.01, dwell=0)

        Generates a triangular waveform on the loads current specified by the
        parameters start, stop, n, and dt.
        Optionally, a dwell acan be added at the top of the waveform to create
        a trapezoidal load shape.
        The input of the load should be enabled before executing this command.
        "start" can be higher than "stop" or vise-versa. The minimum dt is
        limited by the communication speed of the interface used to communicate
        with this device.

        Args:
            start (float): initial current setpoint of the ramp in Amps DC.
            stop (float): midpoint current setpoint of the ramp in Amps DC.
            n (int, optional): Number of points in the ramp between "start" and
                "stop". Defaults to 100.
            dt (float, optional): Time between changes in the value of the
                setpoint in seconds. Defaults to 0.01.
            dwell (float, optional): Time to dwell at the "stop" value before
                ramping back to "start". Defaults to 0.
        """

        self.ramp(start, stop, n=int(n), dt=dt)
        sleep(dwell)
        self.ramp(stop, start, n=int(n), dt=dt)


if __name__ == '__main__':
    pass
