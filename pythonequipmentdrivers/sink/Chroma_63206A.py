from typing import Tuple, Union

from pythonequipmentdrivers import VisaResource


class Chroma_63206A(VisaResource):  # 6 kW
    """
    Chroma_63206A(address)

    address : str, address of the connected electronic load

    object for accessing basic functionallity of the Chroma_63206A DC load
    """

    supported_modes = {"CC", "CR", "CP", "CCD"}

    def set_state(self, state: bool) -> None:
        """
        set_state(state)

        Enables/disables the input for the load

        Args:
            state (bool): Load state (True == enabled, False == disabled)
        """

        self.write_resource(f"LOAD {1 if state else 0}")

    def get_state(self) -> bool:
        """
        get_state()

        Returns the current state of the input to the load

        Returns:
            bool: Load state (True == enabled, False == disabled)
        """

        response = self.query_resource("LOAD?")

        return (response == "ON")

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

        if self.get_state():
            self.off()
        else:
            self.on()

    def set_short_state(self, state: bool) -> None:
        """
        set_short_state(state)

        Enables/Disables the short circuit feature for the load.

        Args:
            state (bool): True == Enable, False == Disable
        """

        self.write_resource(f"LOAD:SHOR {1 if state else 0}")

    def get_short_state(self) -> bool:
        """
        get_short_state()

        Retrives the current state of the loads short circuit feature.

        Returns:
            bool: True == Enabled, False == Disabled
        """

        response = self.query_resource("LOAD:SHOR?")
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

        self.write_resource(f"MODE {mode}{range_string}")

    def get_mode(self) -> Tuple[str, str]:
        """
        get_mode()

        Retrives the current load configuration, two strings representing the
        mode and range current in use.

        Returns:
            Tuple[str, str]: description of the mode and range curreently in
                use. Currently supported modes using this library are "CC",
                "CR", "CP", and "CCD".
        """

        response = self.query_resource("MODE?")

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
            self.write_resource(f'CURR:STAT:L1 {current}')
            self.write_resource(f'CURR:STAT:L2 {current}')
        else:
            cmd_str = f'CURR:STAT:L{channel} {current}'
            self.write_resource(cmd_str)

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
            response1 = self.query_resource('CURR:STAT:L1?')
            response2 = self.query_resource('CURR:STAT:L2?')
            return (float(response1), float(response2))
        else:
            response = self.query_resource(f'CURR:STAT:L{channel}?')
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
            self.write_resource(f'CURR:DYN:L1 {current}')
            self.write_resource(f'CURR:DYN:L2 {current}')
        else:
            self.write_resource(f'CURR:DYN:L{channel} {current}')

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
            response1 = self.query_resource('CURR:DYN:L1?')
            response2 = self.query_resource('CURR:DYN:L2?')
            return (float(response1), float(response2))
        else:
            response = self.query_resource(f'CURR:DYN:L{channel}?')
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
            self.write_resource(f'CURR:DYN:T1 {t}')
            self.write_resource(f'CURR:DYN:T2 {t}')
        else:
            self.write_resource(f'CURR:DYN:T{channel} {t}')

    def get_dynamic_current_time(self, channel: int
                                 ) -> Union[float, Tuple[float]]:
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
            response1 = self.query_resource('CURR:DYN:T1?')
            response2 = self.query_resource('CURR:DYN:T2?')
            return (float(response1), float(response2))
        else:
            response = self.query_resource(f'CURR:DYN:T{channel}?')
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

        self.write_resource(f"CURR:DYN:REP {n}")

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

        response = self.query_resource("CURR:DYN:REP?")
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
        self.write_resource(f"CURR:DYN:RISE {slew_rate/1e6}")

    def get_dynamic_current_rise_rate(self) -> float:
        """
        get_dynamic_current_rise_rate()

        Retrives the slew-rate for the rising edge between the two dynamic
        current setpoint in dynamic current mode.

        Returns:
            float: Slew-rate in Amps/sec.
        """

        response = self.query_resource("CURR:DYN:RISE?")

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
        self.write_resource(f"CURR:DYN:FALL {slew_rate/1e6}")

    def get_dynamic_current_fall_rate(self) -> float:
        """
        get_dynamic_current_fall_rate()

        Retrives the slew-rate for the falling edge between the two dynamic
        current setpoint in dynamic current mode.

        Returns:
            float: Slew-rate in Amps/sec.
        """

        response = self.query_resource("CURR:DYN:FALL?")

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
            self.write_resource(f"RES:STAT:L1 {resistance}")
            self.write_resource(f"RES:STAT:L2 {resistance}")
        else:
            cmd_str = f"RES:STAT:L{channel} {resistance}"
            self.write_resource(cmd_str)

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
            response1 = self.query_resource("RES:STAT:L1?")
            response2 = self.query_resource("RES:STAT:L2?")
            return (float(response1), float(response2))
        else:
            response = self.query_resource(f"RES:STAT:L{channel}?")
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
            self.write_resource(f"VOLT:STAT:L1 {voltage}")
            self.write_resource(f"VOLT:STAT:L2 {voltage}")
        else:
            self.write_resource(f"VOLT:STAT:L{channel} {voltage}")

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
            response1 = self.query_resource("VOLT:STAT:L1?")
            response2 = self.query_resource("VOLT:STAT:L2?")
            return (float(response1), float(response2))
        else:
            response = self.query_resource(f"VOLT:STAT:L{channel}?")
            return float(response)

    def set_cv_current(self, current: float) -> None:
        """
        set_cv_current(current)

        Changes the current setpoint of the load in constant voltage mode

        Args:
            current (float): Desired current setpoint in Amps DC.
        """

        self.write_resource(f"VOLT:STAT:ILIM {current}")

    def get_cv_current(self) -> float:
        """
        get_cv_current()

        Reads the current setpoint of the load in constant voltage mode

        Returns:
            float: Current set-point in Amps DC.
        """

        response = self.query_resource("VOLT:STAT:ILIM?")
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
            self.write_resource(f'POW:STAT:L1 {power}')
            self.write_resource(f'POW:STAT:L2 {power}')
        else:
            self.write_resource(f'POW:STAT:L{channel} {power}')

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
            response1 = self.query_resource('POW:STAT:L1?')
            response2 = self.query_resource('POW:STAT:L2?')
            return (float(response1), float(response2))
        else:
            response = self.query_resource(f'POW:STAT:L{channel}?')
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

        response = self.query_resource(f'{"FETC" if fetch else "MEAS"}:VOLT?')
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

        response = self.query_resource(f'{"FETC" if fetch else "MEAS"}:CURR?')
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

        response = self.query_resource(f'{"FETC" if fetch else "MEAS"}:POW?')
        return float(response)
