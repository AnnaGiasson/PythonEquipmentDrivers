from typing import Set, Tuple, Union
from pythonequipmentdrivers import VisaResource
from enum import Enum


# Look into programming "sequences" and "programs" to the device. See basic
# description in the users manual ~pg 118 (4-32)

# add set/get methods for the current and resistance ranges

class Chroma_63600(VisaResource):
    """
    Chroma_63600(address)

    address : str, address of the connected electronic load

    object for accessing basic functionallity of the Chroma_63600 DC load.
    """

    class ValidModes(Enum):
        CC = 'CC'
        CR = 'CR'
        CV = 'CV'
        CP = 'CP'
        CZ = 'CZ'
        CCD = 'CCD'
        CCFS = 'CCFS'
        TIM = 'TIM'
        SWD = 'SWD'

    class Errors(Enum):
        OTP = 0
        OVP = 1
        OCP = 2
        OPP = 3
        REV = 4
        SYNC = 5
        MAX_LIM = 6
        REMOTE_INHIBIT = 7

    @staticmethod
    def _channel_index(channel: int, reverse: bool = False) -> int:
        """
        _channel_index(channel, reverse=False)

        This module assumes that the Chroma mainframe used has the higher-power
        variant of 636xxx family load modules; these are assigned 2 addresses
        (e.x. the load in physical position 2 has addr=3,4), but only the first
        (odd) address is used. This method reindexes the channel numbers sent
        to the device so other methods in this module can be writen such that
        software address represents the physcial location.

        Args:
            channel (int): bay index number for the physical location of the
                load on the load mainframe.
            reverse (bool, optional): If True the indexing operation is
                reversed. Defaults to False.

        Returns:
            int: software address offset sent to the load
        """

        if reverse:
            return int((channel + 1)/2)

        if (channel > 5) and (channel < 1):
            raise ValueError("Invalid Channel Number")
        return 2*channel - 1

    def set_state(self, state: bool) -> None:
        """
        set_state(state)

        Enables/disables the input for the load

        Args:
            state (bool): Load state (True == enabled, False == disabled)
        """

        self.write_resource(f"LOAD {'1' if state else '0'}")

    def get_state(self) -> bool:
        """
        get_state()

        Returns the current state of the input to the load

        Returns:
            bool: Load state (True == enabled, False == disabled)
        """

        return (self.query_resource("LOAD?") == "ON")

    def on(self) -> None:
        """
        on()

        Enables the relay for the Load's output; equivalent to set_state(True).
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

        Reverses the current state of the Load's input.
        """

        self.set_state(self.get_state() ^ True)

    def set_current(self, current: float, level: int = 0) -> None:
        """
        set_current(current, level=0)

        Changes the current setpoint of the load for the specified level in
        constant current mode.

        Args:
            current (float): Desired current setpoint in Amps DC.
            level (int, optional): level to change setpoint of valid options
                are 0,1,2; If level = 0 both levels will be set to the
                value specified. Defaults to 0.
        """

        if level == 0:
            self.write_resource(f'CURR:STAT:L1 {current}')
            self.write_resource(f'CURR:STAT:L2 {current}')
        else:
            self.write_resource(f'CURR:STAT:L{level} {current}')

    def get_current(self, level: int) -> Union[float, Tuple[float]]:
        """
        get_current(level)

        Retrives the current setpoint of the load for the specified level used
        in constant current mode. if level == 0 then both load levels will be
        returned.

        Args:
            level (int, optional): level to retrive setpoint of valid options
                are 0,1,2; If level = 0 the value of both levels will be
                retrived. Defaults to 0.

        Returns:
            float: Retrivies the current setpoint in Amps DC.
        """

        if level == 0:
            return (float(self.query_resource('CURR:STAT:L1?')),
                    float(self.query_resource('CURR:STAT:L2?')))

        response = self.query_resource(f'CURR:STAT:L{level}?')
        return float(response)

    def set_current_slew_rate(self, slew_rate: float,
                              set_rising_edge: bool = True) -> None:
        """
        set_current_slew(slew_rate, set_rising_edge)

        Changes the slew-rate setting of the load (for the specified edge
        polarity) in constant current mode.

        Args:
            slew_rate (float): desired slew-rate setting in A/s
            set_rising_edge (bool): determines which edge to set the slew-rate
                of. if true, sets the rising edge, otherwise sets the falling
                edge slew-rate. Defaults to True.
        """

        slew_rate = float(slew_rate)*(1e-6)  # A/s --> A/us

        self.write_resource(
            f'CURR:STAT:{"RISE" if set_rising_edge else "FALL"} {slew_rate}'
        )

    def get_current_slew_rate(self, get_rising_edge: bool = True) -> float:
        """
        get_current_slew_rate(edge_polarity)

        Retrives the slew-rate setting of the load (for the specified edge
        polarity) in constant current mode.

        Args:
            get_rising_edge (bool): determines which edge to get the slew-rate
                of. if true, gets the rising edge, otherwise gets the falling
                edge slew-rate. Defaults to True.

        Returns:
            float: slew-rate setting in A/s.
        """

        response = self.query_resource(
            f'CURR:STAT:{"RISE" if get_rising_edge else "FALL"}?'
        )
        return float(response)*(1e6)  # A/us --> A/s

    def set_dynamic_current(self, current: float, level: int = 0) -> None:
        """
        set_dynamic_current(current, level=0)

        current: float, desired current setpoint
        level (optional): int, level to change setpoint of.
                          valid options are 0,1,2 (default is 0)

        changes the current setpoint of the load for the specified level in
        dynamic current mode. if level = 0 both levels will be set to the
        value specified
        """

        if level == 0:
            self.write_resource(f'CURR:DYN:L1 {current}')
            self.write_resource(f'CURR:DYN:L2 {current}')
        else:
            self.write_resource(f'CURR:DYN:L{level} {current}')

    def get_dynamic_current(self, level: int) -> Union[float, Tuple[float]]:
        """
        get_dynamic_current(level)

        level: int, level to get setpoint of.
               valid options are 1,2, and 0

        reads the current setpoint of the load for the specified level in
        dynamic current mode. if level == 0 then it will return a list
        containing both load levels.
        """

        if level == 0:
            return (float(self.query_resource('CURR:DYN:L1?')),
                    float(self.query_resource('CURR:DYN:L2?')))
        else:
            response = self.query_resource(f'CURR:DYN:L{level}?')
            return float(response)

    def set_dynamic_current_slew(self, slew_rate: float,
                                 set_rising_edge: bool = True) -> None:
        """
        set_dynamic_current_slew(slew, set_rising_edge)

        changes the slew-rate setting of the load for the specified edge
        polarity in dynamic current mode.

        slew: float, desired slew-rate setting in A/s
            set_rising_edge (bool): determines which edge to set the slew-rate
                of. if true, sets the rising edge, otherwise sets the falling
                edge slew-rate. Defaults to True.
        """

        sr_a_per_s = slew_rate*1e-6
        # note: load uses current slew rate in units of A/us, hence the
        # conversion

        self.write_resource(
            f'CURR:DYN:{"RISE" if set_rising_edge else "FALL"} {sr_a_per_s}'
            )

    def get_dynamic_current_slew(self, get_rising_edge: bool = True
                                 ) -> float:
        """
        get_dynamic_current_slew(slew, get_rising_edge)

        returns the slew-rate setting of the load for the specified edge
        polarity in dynamic current mode.

        get_rising_edge (bool): determines which edge to get the slew-rate
            of. if true, gets the rising edge, otherwise gets the falling
            edge slew-rate. Defaults to True.

        Returns:
        slew: float, slew-rate setting in A/s,
        """

        response = self.query_resource(
            f'CURR:DYN:{"RISE" if get_rising_edge else "FALL"}?'
        )

        # note: load uses current slew rate in units of A/us, hence the
        # conversion

        return float(response)*1e6

    def set_dynamic_current_time(self, on_time: float, level: int = 0) -> None:
        """
        set_dynamic_current_time(on_time, level=0)

        changes the time that the load spends at the specified level in
        dynamic current mode. if level = 0 both levels will be set to the
        value specified

        on_time: float, desired time to spend at level 'level'
                 min: 10us, max: 100s, resolves to nearest 10us
        level (optional): int, level to change setpoint of.
                          valid options are 0,1,2 (default is 0)
        """

        if level == 0:
            self.write_resource(f'CURR:DYN:T1 {on_time}')
            self.write_resource(f'CURR:DYN:T2 {on_time}')
        else:
            self.write_resource(f'CURR:DYN:T{level} {on_time}')

    def get_dynamic_current_time(self, level: int
                                 ) -> Union[float, Tuple[float]]:
        """
        get_dynamic_current_time(level)

        returns the time that the load spends at the specified level in
        dynamic current mode. if level = 0 both levels will be returned

        level : int, level to change setpoint of.
                valid options are 0,1,2

        Returns:
            on_time: float, time spent at level 'level'
        """

        if level == 0:
            return (float(self.query_resource('CURR:DYN:T1?')),
                    float(self.query_resource('CURR:DYN:T2?')))

        return float(self.query_resource(f'CURR:DYN:T{level}?'))

    def set_dynamic_current_repeat(self, count: int) -> None:
        """
        set_dynamic_current_repeat(count)

        count: int, number of cycles. max: 65535, min: 0, res: 1

        sets the number of times to cycle through the two dynamic current
        set-points
        """

        self.write_resource(f'CURR:DYN:REP {count}')

    def get_dynamic_current_repeat(self) -> int:
        """
        get_dynamic_current_repeat()

        returns:
        count: int, number of cycles. max: 65535, min: 0, res: 1

        returns the number of times to cycle through the two dynamic current
        set-points
        """

        response = self.query_resource('CURR:DYN:REP?')
        return int(response)

    def set_resistance(self, resistance: float, level: int = 0) -> None:
        """
        set_resistance(resistance, level=0)

        changes the resistance setpoint of the load for the specified level in
        constant resistance mode. if level = 0 both levels will be set to the
        value specified

        resistance: float, desired resistance setpoint in Ohms
        level (optional): int, level to change setpoint of.
                          valid options are 0,1,2 (default is 0)
        """

        if level == 0:
            self.write_resource(f'RES:STAT:L1 {resistance}')
            self.write_resource(f'RES:STAT:L2 {resistance}')
        else:
            self.write_resource(f'RES:STAT:L{level} {resistance}')

    def get_resistance(self, level: int) -> Union[Tuple[float], float]:
        """
        get_resistance(level)

        reads the resistance setpoint of the load for the specified level in
        constant resistance mode. if level == 0 then it will return a list
        containing both load levels.

        level: int, level to get setpoint of.
               valid options are 1,2, and 0
        """

        if level == 0:
            return (float(self.query_resource('RES:STAT:L1?')),
                    float(self.query_resource('RES:STAT:L2?')))
        else:
            response = self.query_resource(f'RES:STAT:L{level}?')
            return float(response)

    def set_channel(self, channel: int) -> None:
        """
        set_channel(channel)

        channel: int, index of the channel to control.
                 valid options are 1-5

        Selects the specified Channel to use for software control
        """

        idx = self._channel_index(channel)
        self.write_resource(f'CHAN {idx}')

    def get_channel(self) -> int:
        """
        get_channel()

        Get current selected Channel

        returns: int
        """

        response = self.query_resource('CHAN?')
        channel = self._channel_index(int(response), reverse=True)
        return channel

    def set_mode(self, channel: int, mode: ValidModes,
                 range_setting: str = "M") -> None:
        """
        set_mode(channel, mode, range_setting="M")

        Sets the mode of the specified load card

        Args:
            channel: int, valid options are 1-5

            mode: ValidModes, mode/load type to set the desired channel to
                valid options can be accessed via the self.ValidModes
                attribute.

            range_setting: str, range of the given mode. Valid options are:
                "L", "M", and "H" for Low, Medium, and High range respectively
        """

        if range_setting not in {"L", "M", "H"}:
            raise ValueError(f"Invalid range: {range_setting}")

        self.set_channel(channel)
        self.write_resource(f'MODE {mode.value}{range_setting}')

    def get_mode(self, channel: int) -> Tuple[ValidModes, str]:
        """
        get_mode(channel)

        Gets the load mode from specified load channel

        Args:
            channel: int, valid options are 1-5

        Returns:
        Tuple[ValidModes, str]:  load mode (mode, range_setting). Mode
            (ValidModes), mode/load type to set the desired channel to valid
            options can be accessed via the self.ValidModes attribute.
            range_setting (str), range of the given mode. Valid options are:
            "L", "M", and "H" for Low, Medium, and High range respectiv
        """

        self.set_channel(channel)
        response = self.query_resource('MODE?')

        mode, range_setting = response[0:-1], response[-1]

        return (self.ValidModes[mode], range_setting)

    def set_parallel_state(self, state: bool) -> None:
        """
        set_parallel_state(state)

        Enables/Disables parallel mode operation of individual channels within
        the load.

        Args:
            state: bool, parallel state.
        """

        self.write_resource(f'CONF:PARA:INIT {1 if state else 0}')

    def get_parallel_state(self) -> bool:
        """
        get_parallel_state()

        Returns the loads parallel operation state.

        Returns:
            bool: parallel operation state
        """

        response = self.query_resource('CONF:PARA:INIT?')

        if response not in {"ON", "OFF"}:
            raise IOError(f"Unknown response: {response}")

        return response == "ON"

    def set_parallel_mode(self, channel: int, mode: str) -> None:
        """
        set_parallel_mode(channel, mode)

        Sets parallel mode for each channel

        Args:
            channel: int, valid options are 1-5

            mode: str,  the parallel mode of the respective channel. Valid
                options are: "None", "Master", and "Slave" (case-insensitive)
        """

        modes = {"none": 0, 'master': 1, 'slave': 2}

        if mode.lower() not in modes.keys():
            raise ValueError(
                f'Invalid mode, valid options are {modes.keys()}'
                )

        self.set_channel(channel)
        self.write_resource(f'CONF:PARA:MODE {modes[mode.lower()]}')

    def get_parallel_mode(self, channel: int) -> str:
        """
        get_parallel_mode(channel)

        channel: int, valid options are 1-5

        Returns the parallel mode configuration of the respective channel
        (int).

        Valid return values are:
                    0: None
                    1: Master
                    2: Slave
        """

        modes = {"none", 'master', 'slave'}

        self.set_channel(channel)
        response = self.query_resource('CONF:PARA:MODE?')

        if response not in modes:
            raise IOError(f"Unknown response: {response}")
        return response.lower()

    def set_channel_state(self, channel: int, state: bool) -> None:
        """
        set_channel_state(channel, state)

        Enables/disables the respective load channel

        Args:
            channel (int): valid options are 1-5
            state (bool): channel state
        """

        self.set_channel(channel)
        self.write_resource(f'CHAN:ACT {1 if state else 0}')

    def get_channel_state(self, channel: int) -> bool:
        """
        get_channel_state(channel)

        returns the state of the output of the specified channel

        Args:
            channel (int): valid options are 1-5

        Returns:
            bool: whether or not the respective load channel is Enabled
        """

        self.set_channel(channel)
        response = self.query_resource('CHAN:ACT?')

        if response not in {"ON", "OFF"}:
            raise IOError(f"Unknown response: {response}")

        return (response == "ON")

    # # need to investigate what this function actually does
    # def set_sync_mode(self, channel: int, state) -> None:
    #     """
    #     Set sync mode for each channel
    #     """
    #     self.set_channel(channel)
    #     self.write_resource(f'CONF:SYNC:MODE {state}')

    def set_voltage(self, voltage: float, level: int = 0) -> None:
        """
        set_voltage(voltage, level=0)

        changes the voltage setpoint of the load for the specified level in
        constant voltage mode. if level = 0 both levels will be set to the
        value specified

        Args:
            voltage (float): desired voltage setpoint in Vdc
            level (int): level to change setpoint of. valid options
                are 0,1,2 (default is 0).
        """

        if level == 0:
            self.write_resource(f'VOLT:STAT:L1 {voltage}')
            self.write_resource(f'VOLT:STAT:L2 {voltage}')
        else:
            self.write_resource(f'VOLT:STAT:L{level} {voltage}')

    def get_voltage(self, level: int) -> float:
        """
        get_voltage(level)

        Reads the voltage setpoint of the load for the specified level in
        constant voltage mode. if level == 0 then it will return a list
        containing both load levels.

        Args:
            level (int): level to get setpoint of. valid options are 1,2, and 0
        """

        if level == 0:
            return (float(self.query_resource('VOLT:STAT:L1?')),
                    float(self.query_resource('VOLT:STAT:L2?')))
        else:
            response = self.query_resource(f'VOLT:STAT:L{level}?')
            return float(response)

    def set_cv_current_limit(self, current: float) -> None:
        """
        set_cv_current_limit(current)

        Changes the current setpoint of the load for the specified level in
        constant voltage mode.

        Returns:
            float: setpoint current in Amps
        """

        self.write_resource(f'VOLT:STAT:ILIM {current}')

    def get_cv_current_limit(self) -> float:
        """
        get_cv_current_limit()

        Retries the current setpoint of the load for the in constant voltage
        mode.

        Returns:
            float:  setpoint current in Adc
        """

        response = self.query_resource('VOLT:STAT:ILIM?')
        return float(response)

    def set_dynamic_sine_frequency(self, frequency: float) -> None:

        """
        set_dynamic_sine_frequency(frequency)

        Sets the frequency of the sine wave current used in the
        'advanced sine-wave' mode of operation in Hz. Min/Max setting can be
        determined using the get_dynamic_sine_frequency method with the min/max
        flag.

        Args:
            frequency (float): desired frequency in Hz
        """

        self.write_resource(f'ADV:SINE:FREQ {frequency}')

    def get_dynamic_sine_frequency(self, flag='') -> float:
        """
        get_dynamic_sine_frequency(flag='')

        Returns the frequency of the sine wave current used in the
        'advanced sine-wave' mode of operation in Hz. Can also return the
        Min/Max possible setting with the min/max flag.

        Kwargs:
            flag (str): flag used to determine the frequency limits of the
                electronic loads sine-wave capabiity. Valid options are 'Min',
                'Max', and '' for the minimum, maximum, and current settings
                respectively (Not case-sensitive, default: {''}).

        Returns:
            float: current frequency setpoint (or limit) in Hz.
        """

        if (flag != '') and (flag.upper() not in {'MIN', 'MAX'}):
            raise ValueError(f'Invalid value {flag} for arg "flag"')

        response = self.query_resource(f'ADV:SINE:FREQ? {flag.upper()}')
        return float(response)

    def set_dynamic_sine_amplitude_ac(self, amplitude: float) -> None:

        """
        set_dynamic_sine_amplitude_ac(amplitude)

        Sets the amplitude of the sine wave current used in the
        'advanced sine-wave' mode of operation in A_DC. Min/Max setting can be
        determined using the get_dynamic_sine_amplitude_ac method with the
        min/max flag.

        Args:
            amplitude (float): desired amplitude in A_DC
        """

        amp_peak2peak = amplitude*2  # convert Amplitude to peak-to-peak
        self.write_resource(f'ADV:SINE:IAC {amp_peak2peak}')

    def get_dynamic_sine_amplitude_ac(self, flag: str = '') -> float:

        """
        get_dynamic_sine_amplitude_ac(flag='')

        Returns the amplitude of the sine wave current used in the
        'advanced sine-wave' mode of operation in A_DC. Can also return the
        Min/Max possible setting with the min/max flag.

        Kwargs:
            flag (str): flag used to determine the amplitude limits of the
                electronic loads sine-wave capabiity. Valid options are 'Min',
                'Max', and '' for the minimum, maximum, and current settings
                respectively; Not case-insensitive. Defaults to ''.

        Returns:
            float: current amplitude setpoint (or limit) in A_DC.
        """

        if flag.upper() not in {'MIN', 'MAX', ''}:
            raise ValueError(f'Invalid value {flag} for arg "value"')

        response = self.query_resource(f'ADV:SINE:IAC? {flag.upper()}')
        amp_peak2peak = float(response)
        return amp_peak2peak/2  # convert peak-to-peak to Amplitude

    def set_dynamic_sine_dc_offset(self, offset: float) -> None:
        """
        set_dynamic_sine_dc_offset(offset)

        Sets the DC level of the sine wave current used in the
        'advanced sine-wave' mode of operation in A_DC. Min/Max setting can be
        determined using the get_dynamic_sine_dc_level method with the
        min/max flag.

        Arguments:
            freq (float): desired DC offset in A_DC
        """

        self.write_resource(f'ADV:SINE:IDC {offset}')

    def get_dynamic_sine_dc_level(self, flag: str = '') -> float:
        """
        get_dynamic_sine_dc_level(flag='')

        Returns the DC level of the sine wave current used in the
        'advanced sine-wave' mode of operation in A_DC. Can also return the
        Min/Max possible setting with the min/max flag.

        Kwargs:
            flag (str): flag used to determine the DC level limits of the
                electronic loads sine-wave capabiity. Valid options are 'Min',
                'Max', and '' for the minimum, maximum, and current settings
                respectively; case-insensitive. Defaults to ''.

        Returns:
            float: current DC level setpoint (or limit) in A_DC.
        """

        if (flag != '') and (flag.upper() not in {'MIN', 'MAX'}):
            raise ValueError(f'Invalid value {flag} for arg "flag"')

        response = self.query_resource(f'ADV:SINE:IDC? {flag.upper()}')
        return float(response)

    def clear_errors(self) -> None:
        """
        clear_errors()

        Resets status of load and clears errors
        """

        self.write_resource('LOAD:PROT:CLE')

    def get_errors(
        self,
        channel: int
    ) -> Set[Errors]:
        """
        get_errors(channel)

        channel: int, valid options are 1-5

        Returns the tripped errors registered in the status register of the
        respective load channel. The status register contains 1 Byte of
        possible faults, the bits in the register from bit 0 to 7 corespond
        with the following: 'OTP', 'OVP', 'OCP', 'OPP', 'REV', 'SYNC',
        'MAX_LIM', 'REMOTE_INHIBIT'
        """

        self.set_channel(channel)
        response = self.query_resource('STAT:CHAN:COND?')
        status = int(response) & 0xff  # 2B response only has 1B of info

        errors = {self.Errors(n) for n in range(0, 7) if (status & 2**n) >> n}
        return errors

    def measure_voltage(self) -> float:
        """
        measure_voltage()

        returns measurement of the voltage present across the load in Vdc
        returns: float
        """

        response = self.query_resource('MEAS:VOLT?')
        return float(response)

    def measure_current(self) -> float:
        """
        measure_current()

        returns measurement of the current through the load in Adc
        returns: float
        """

        response = self.query_resource('MEAS:CURR?')
        return float(response)

    def measure_power(self) -> float:
        """
        measure_power()

        returns measurement of the power consumed by the load in W
        returns: float
        """

        response = self.query_resource('FETC:POW?')
        return float(response)

    def measure_module_voltages(self) -> Tuple[float]:
        """
        measure_module_voltages()

        returns measurement of the voltage present across all loads in Vdc
        returns: tuple of floats
        """

        response = self.query_resource('MEAS:ALLV?')
        voltages = tuple(map(float, response.split(',')))

        return voltages

    def measure_module_currents(self) -> Tuple[float]:
        """
        measure_module_currents()

        returns measurement of the current through all loads in Adc
        returns: list of floats or float
        """

        response = self.query_resource('MEAS:ALLC?')
        currents = tuple(map(float, response.split(',')))

        return currents

    def measure_module_power(self) -> Tuple[float]:
        """
        measure_total_power()

        returns measurement of the power consumed by the all loads in W
        returns: list of floats or float
        """

        response = self.query_resource('MEAS:ALLP?')
        powers = tuple(map(float, response.split(',')))

        return powers
