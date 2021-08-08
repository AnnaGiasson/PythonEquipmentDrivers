from pythonequipmentdrivers import Scpi_Instrument
import numpy as np
from time import sleep
from typing import Union, Tuple


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
            return_state (bool, optional): Whether or not to return the state
                of the load after changing its state. Defaults to False.

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
            bool: True == Enabled, False == Disabled
        """

        response = self.instrument.query("LOAD:SHOR?")
        return (int(response) == 1)

    def set_mode(self, mode: str, range_setting: Union[int, str] = 2) -> None:
        """
        set_mode(mode, range_setting=2)

        Sets the desired load configuration. Currently supported modes using
        this library are "CC", "CR", "CP", and "CCD". Additionally the range of
        the mode used (interpretation is mode dependant) can be adjusted with
        the "range_setting" arguement.

        Args:
            mode (str): Mode to operate the load in, currently only "CC", "CR",
                "CP", and "CCD" are supported with this library.
            range_setting (Union[int, str], optional): Index or name of the
                range to use for the given mode, 0/"L" for Low, 1/"M" for
                Medium and 2/"H" for High. Defaults to 2.
        """

        valid_ranges = ("L", "M", "H")

        # check arguements
        if str(mode).upper() not in self.supported_modes:
            raise ValueError('Invalid option for arguement "mode"')

        if isinstance(range_setting, int):
            if range_setting in range(0, 3):
                range_string = valid_ranges[range_setting]
            else:
                raise ValueError('Invalid option for the int "range_setting"')
        elif isinstance(range_setting, str):
            if range_setting.upper() in valid_ranges:
                range_string = range_setting.upper()
            else:
                raise ValueError('Invalid option for the str "range_setting"')
        else:
            raise TypeError('Expected range_setting to be of type str or int')

        self.instrument.write(f"MODE {mode}{range_string}")

    def get_mode(self) -> Tuple[str, str]:
        """
        set_mode(mode, range_setting=2)

        Retrives the current load configuration, two strings representing the
        mode and range current in use.

        Returns:
            Tuple[str, str]: description of the mode and range curreently in
                use. Currently supported modes using this library are "CC",
                "CR", "CP", and "CCD".
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
            current (float): Desired current setpoint in Amps DC.
            channel (int, optional): Channel number to adjust or 0 to adjust
                both channels. For this load, valid channels are 1, and 2.
                Defaults to 0.
        """

        if int(channel) == 0:
            self.instrument.write(f'CURR:STAT:L1 {float(current)}')
            self.instrument.write(f'CURR:STAT:L2 {float(current)}')
        else:
            cmd_str = f'CURR:STAT:L{int(channel)} {float(current)}'
            self.instrument.write(cmd_str)

    def get_current(self, channel: int) -> Union[float, Tuple[float]]:
        """
        get_current(channel)

        Reads the current setpoint of the load for the specified channel in
        constant current mode. If channel == 0, then the setpoints for both
        channels will be returned.

        Args:
            channel (int): Channel number to query or 0 to query both signals.
                For this load, valid channels are 1, and 2.

        Returns:
            Union[float, Tuple[float]]: Current setpoint in Amps DC. If
                channel == 0 then the setpoints for both channels will be
                returned in a tuple ordered by channel number.
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
            current (float): Desired current setpoint in Amps DC.
            channel (int, optional): Channel number to adjust or 0 to adjust
                both channels. For this load, valid channels are 1, and 2.
                Defaults to 0.
        """

        if int(channel) == 0:
            self.instrument.write(f'CURR:DYN:L1 {float(current)}')
            self.instrument.write(f'CURR:DYN:L2 {float(current)}')
        else:
            self.instrument.write(f'CURR:DYN:L{int(channel)} {float(current)}')

    def get_dynamic_current(self, channel: int) -> Union[float, Tuple[float]]:
        """
        get_dynamic_current(channel)

        Reads the current setpoint of the load for the specified channel in
        dynamic current mode. If channel == 0, then the setpoints for both
        channels will be returned.

        Args:
            channel (int): Channel number to query or 0 to query both signals.
                For this load, valid channels are 1, and 2.

        Returns:
            Union[float, Tuple[float]]: Desired current setpoint in Amps DC. If
                channel == 0 then the setpoints for both channels will be
                returned in a tuple ordered by channel number.
        """

        if int(channel) == 0:
            response1 = self.instrument.query('CURR:DYN:L1?')
            response2 = self.instrument.query('CURR:DYN:L2?')
            return (float(response1), float(response2))
        else:
            response = self.instrument.query(f'CURR:DYN:L{int(channel)}?')
            return float(response)

    def set_dynamic_current_time(self, t: float, channel: int = 0) -> None:
        """
        set_dynamic_current_time(t, channel=0)

        changes the duration of the dynamic current setpoint of the load for
        the specified channel in dynamic current mode.
        if channel = 0 both channels will be set to the value specified

        Args:
            t (float): Desired duration of dynamic setpoint in seconds.
            channel (int, optional): Channel number to adjust or 0 to adjust
                both channels. For this load, valid channels are 1, and 2.
                Defaults to 0.
        """

        if int(channel) == 0:
            self.instrument.write(f'CURR:DYN:T1 {float(t)}')
            self.instrument.write(f'CURR:DYN:T2 {float(t)}')
        else:
            self.instrument.write(f'CURR:DYN:T{int(channel)} {float(t)}')

    def get_dynamic_current_time(self,
                                 channel: int) -> Union[float, Tuple[float]]:
        """
        get_dynamic_current_time(channel)

        Reads the duration of the current setpoint of the load for the
        specified channel in dynamic current mode.

        Args:
            channel (int): Channel number to query or 0 to query both signals.
                For this load, valid channels are 1, and 2.

        Returns:
            Union[float, Tuple[float]]: The duration of one or more of the
                dynamic current setpoints in seconds. If channel == 0 then the
                setpoints for both channels will be returned in a tuple ordered
                by channel number.
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

        Changes the number of cycles to alternate between the two dynamic
        current setpoints before turning off. Cycles begin when the output of
        the load is enabled, after completion load will automatically turn
        itself off. if n = 0 the load will indefinately cycle between the two
        setpoints.

        Args:
            n (int): Desired number of periods of the dynamic current waveform.
        """

        self.instrument.write(f"CURR:DYN:REP {int(n)}")

    def get_dynamic_current_repeat(self) -> int:
        """
        get_dynamic_current_repeat()

        Returns the number of cycles to alternate between the two dynamic
        current setpoints before turning off. Cycles begin when the output of
        the load is enabled, after completion load will automatically turn
        itself off. if n = 0 the load will indefinately cycle between the two
        setpoints.

        Returns:
            int: Number of periods of the dynamic current waveform.
        """

        response = self.instrument.query("CURR:DYN:REP?")
        return int(response)

    def set_dynamic_current_rise_rate(self, slew_rate: float) -> None:
        """
        set_dynamic_current_rise_rate(slew_rate)

        Sets the slew-rate for the rising edge between the two dynamic current
        setpoint in dynamic current mode.

        Args:
            slew_rate (float): Slew-rate of the rising edge of current setpoint
                   transitions in Amps/sec.
        """

        # actually needs to be sent in A/us
        self.instrument.write(f"CURR:DYN:RISE {float(slew_rate)/1e6}")

    def get_dynamic_current_rise_rate(self) -> float:
        """
        get_dynamic_current_rise_rate()

        Retrives the slew-rate for the rising edge between the two dynamic
        current setpoint in dynamic current mode.

        Returns:
            float: Slew-rate in Amps/sec.
        """

        response = self.instrument.query("CURR:DYN:RISE?")

        # actually returned in A/us
        return float(response)*1e6

    def set_dynamic_current_fall_rate(self, slew_rate: float) -> None:
        """
        set_dynamic_current_fall_rate(slew_rate)

        Sets the slew-rate for the falling edge between the two dynamic current
        setpoint in dynamic current mode.

        Args:
            slew_rate (float): Slew-rate of the falling edge of current
                setpoint transitions in Amps/sec.
        """

        # actually needs to be sent in A/us
        self.instrument.write(f"CURR:DYN:FALL {float(slew_rate)/1e6}")

    def get_dynamic_current_fall_rate(self) -> float:
        """
        get_dynamic_current_fall_rate()

        Retrives the slew-rate for the falling edge between the two dynamic
        current setpoint in dynamic current mode.

        Returns:
            float: Slew-rate in Amps/sec.
        """

        response = self.instrument.query("CURR:DYN:FALL?")

        # actually returned in A/us
        return float(response)*1e6

    def set_resistance(self, resistance: float, channel: int = 0) -> None:
        """
        set_resistance(resistance, channel=0)

        Changes the resistance setpoint of the load for the specified channel
        in constant resistance mode. If channel = 0 both channels will be set
        to the value specified

        Args:
            resistance (float): Desired resistance setpoint in Ohms.
            channel (int, optional): Channel number to adjust or 0 to adjust
                both channels. For this load, valid channels are 1, and 2.
                Defaults to 0.
        """

        if int(channel) == 0:
            self.instrument.write(f"RES:STAT:L1 {float(resistance)}")
            self.instrument.write(f"RES:STAT:L2 {float(resistance)}")
        else:
            cmd_str = f"RES:STAT:L{int(channel)} {float(resistance)}"
            self.instrument.write(cmd_str)

    def get_resistance(self, channel: int) -> Union[float, Tuple[float]]:
        """
        get_resistance(channel)

        Retrives the resistance setpoint of the load for the specified channel
        in constant resistance mode.

        Args:
            channel (int): Channel number to query or 0 to query both channels.
                For this load, valid channels are 1, and 2.

        Returns:
            Union[float, Tuple[float]]: Resistence setpoint in Ohms. If
                channel == 0 then the setpoints for both channels will be
                returned in a tuple ordered by channel number.
        """

        if int(channel) == 0:
            response1 = self.instrument.query("RES:STAT:L1?")
            response2 = self.instrument.query("RES:STAT:L2?")
            return (float(response1), float(response2))
        else:
            response = self.instrument.query(f"RES:STAT:L{int(channel)}?")
            return float(response)

    def set_voltage(self, voltage: float, channel: int = 0) -> None:
        """
        set_voltage(voltage, channel=0)

        Changes the voltage setpoint of the load for the specified channel in
        constant voltage mode if channel = 0 both channels will be set to the
        value specified.

        Args:
            voltage (float): Desired voltage setpoint in Volts DC.
            channel (int, optional): Channel number to adjust or 0 to adjust
                both channels. For this load, valid channels are 1, and 2.
                Defaults to 0.
        """

        if int(channel) == 0:
            self.instrument.write(f"VOLT:STAT:L1 {float(voltage)}")
            self.instrument.write(f"VOLT:STAT:L2 {float(voltage)}")
        else:
            cmd_str = f"VOLT:STAT:L{int(channel)} {float(voltage)}"
            self.instrument.write(cmd_str)

    def get_voltage(self, channel: int) -> Union[float, Tuple[float]]:
        """
        get_voltage(channel)

        Reads the voltage setpoint of the load for the specified channel in
        constant voltage mode.

        Args:
            channel (int): Channel number to query or 0 to query both channels.
                For this load, valid channels are 1, and 2.

        Returns:
            Union[float, Tuple[float]]: Voltage setpoint in Volts DC. If
                channel == 0 then the setpoints for both channels will be
                returned in a tuple ordered by channel number.
        """

        if int(channel) == 0:
            response1 = self.instrument.query("VOLT:STAT:L1?")
            response2 = self.instrument.query("VOLT:STAT:L2?")
            return (float(response1), float(response2))
        else:
            response = self.instrument.query(f"VOLT:STAT:L{int(channel)}?")
            return float(response)

    def set_cv_current(self, current: float) -> None:
        """
        set_cv_current(current)

        Changes the current setpoint of the load in constant voltage mode

        Args:
            current (float): Desired current setpoint in Amps DC.
        """

        self.instrument.write(f"VOLT:STAT:ILIM {float(current)}")

    def get_cv_current(self) -> float:
        """
        get_cv_current()

        Reads the current setpoint of the load in constant voltage mode

        Returns:
            float: Current set-point in Amps DC.
        """

        response = self.instrument.query("VOLT:STAT:ILIM?")
        return float(response)

    def set_power(self, power: float, channel: int = 0) -> None:
        """
        set_power(power, channel=0)

        Changes the power setpoint of the load for the specified channel in
        constant power mode. if channel = 0 both channels will be set to the
        value specified.

        Args:
            power (float): Desired power setpoint in Watts.
            channel (int, optional): Channel number to adjust or 0 to adjust
                both channels. For this load, valid channels are 1, and 2.
                Defaults to 0.
        """

        if int(channel) == 0:
            self.instrument.write(f'POW:STAT:L1 {float(power)}')
            self.instrument.write(f'POW:STAT:L2 {float(power)}')
        else:
            self.instrument.write(f'POW:STAT:L{int(channel)} {float(power)}')

    def get_power(self, channel: int) -> Union[float, Tuple[float]]:
        """
        get_power(channel)

        Reads the power setpoint of the load for the specified channel in
        constant power mode

        Args:
            channel (int): Channel number to query or 0 for to query both
                channels.

        Returns:
            Union[float, Tuple[float]]: Power setpoint in Watts DC. If
                channel == 0 then the setpoints for both channels will be
                returned in a tuple ordered by channel number.
        """

        if int(channel) == 0:
            response1 = self.instrument.query('POW:STAT:L1?')
            response2 = self.instrument.query('POW:STAT:L2?')
            return (float(response1), float(response2))
        else:
            response = self.instrument.query(f'POW:STAT:L{int(channel)}?')
            return float(response)

    def measure_voltage(self, fetch: bool = True) -> float:
        """
        measure_voltage()

        Retrives measurement of the voltage present across the load's input.

        Args:
            fetch (bool): If True this will cause the load to issue a trigger
                for a new sample of the power and return the result. Otherwise
                returns the current contents of the measurement buffer.
                Defaults to True.
        Returns:
            float: Measured Voltage in Volts DC
        """

        if fetch:
            response = self.instrument.query('FETC:VOLT?')
        else:
            response = self.instrument.query('MEAS:VOLT?')

        return float(response)

    def measure_current(self, fetch: bool = True) -> float:
        """
        measure_current()

        Retrives measurement of the current present through the load.

        Args:
            fetch (bool): If True this will cause the load to issue a trigger
                for a new sample of the power and return the result. Otherwise
                returns the current contents of the measurement buffer.
                Defaults to True.
        Returns:
            float: Measured Current in Amps DC.
        """

        if fetch:
            response = self.instrument.query('FETC:CURR?')
        else:
            response = self.instrument.query('MEAS:CURR?')

        return float(response)

    def measure_power(self, fetch: bool = True) -> float:
        """
        measure_power()

        Retrives measurement of the power dissipated by the load.

        Args:
            fetch (bool): If True this will cause the load to issue a trigger
                for a new sample of the power and return the result. Otherwise
                returns the current contents of the measurement buffer.
                Defaults to True.
        Returns:
            float: Measured power in Watts.
        """

        if fetch:
            response = self.instrument.query('FETC:POW?')
        else:
            response = self.instrument.query('MEAS:POW?')

        return float(response)

    def pulse(self, level: float, duration: float, channel: int = 0) -> None:
        """
        pulse(level, duration, channel=0)

        Generates a square pulse with height and duration specified by level
        and duration. The load will start and return to the previous current
        level set on the load before the execution of pulse(). "level" can be
        less than or greater than the previous current setpoint.

        Args:
            level (float): Current level of pulse in Amps DC
            duration (float): Duration of the pulse in seconds
            channel (int, optional): Channel number to adjust or 0 to adjust
                both channels. For this load, valid channels are 1, and 2.
                Defaults to 0.
        """

        start_level = self.get_current(int(channel))

        self.set_current(float(level), channel=int(channel))
        sleep(duration)
        if isinstance(start_level, (float, int)):
            self.set_current(start_level)
        elif isinstance(start_level, tuple):
            self.set_current(start_level[0], channel=1)
            self.set_current(start_level[1], channel=2)
        else:
            raise TypeError('Expected start_level to be a float or tuple')

    def ramp(self, start: float, stop: float, n: int = 100,
             dt: float = 0.01, channel: int = 0) -> None:
        """
        ramp(start, stop, n=100, dt=0.01, channel=0)

        Generates a linear ramp on the loads current specified by the
        parameters start, stop, n, and dt.
        The input of the load should be enabled before executing this command.
        "start" can be higher than "stop" or vise-versa. The minimum dt is
        limited by the communication speed of the interface used to communicate
        with this device.

        Args:
            start (float): Initial current setpoint of the ramp in Amps DC.
            stop (float): Final current setpoint of the ramp in Amps DC.
            n (int, optional): Number of points in the ramp between "start" and
                "stop". Defaults to 100.
            dt (float, optional): Time between changes in the value of the
                setpoint in seconds. Defaults to 0.01.
            channel (int, optional): Channel number to adjust or 0 to adjust
                both channels. For this load, valid channels are 1, and 2.
                Defaults to 0.
        """

        for i in np.linspace(float(start), float(stop), int(n)):
            self.set_current(i, channel=int(channel))
            sleep(dt)

    def slew(self, start: float, stop: float, n: int = 100,
             dt: float = 0.01, dwell: float = 0, channel: int = 0) -> None:
        """
        slew(start, stop, n=100, dt=0.01, dwell=0, channel=0)

        Generates a triangular waveform on the loads current specified by the
        parameters start, stop, n, and dt.
        Optionally, a dwell acan be added at the top of the waveform to create
        a trapezoidal load shape.
        The input of the load should be enabled before executing this command.
        "start" can be higher than "stop" or vise-versa. The minimum dt is
        limited by the communication speed of the interface used to communicate
        with this device.

        Args:
            start (float): Initial current setpoint of the ramp in Amps DC.
            stop (float): Midpoint current setpoint of the ramp in Amps DC.
            n (int, optional): Number of points in the ramp between "start" and
                "stop". Defaults to 100.
            dt (float, optional): Time between changes in the value of the
                setpoint in seconds. Defaults to 0.01.
            dwell (float, optional): Time to dwell at the "stop" value before
                ramping back to "start". Defaults to 0.
            channel (int, optional): Channel number to adjust or 0 to adjust
                both channels. For this load, valid channels are 1, and 2.
                Defaults to 0.
        """

        self.ramp(start, stop, n=n, dt=dt, channel=channel)
        sleep(dwell)
        self.ramp(stop, start, n=n, dt=dt, channel=channel)
