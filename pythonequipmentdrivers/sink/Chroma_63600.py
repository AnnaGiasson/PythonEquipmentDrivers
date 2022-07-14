from typing import Tuple, Union
from pythonequipmentdrivers import VisaResource


# Look into programming "sequences" and "programs" to the device. See basic
# description in the users manual ~pg 118 (4-32)

# add set/get methods for the current and resistance ranges

class Chroma_63600(VisaResource):
    """
    Chroma_63600(address)

    address : str, address of the connected electronic load

    object for accessing basic functionallity of the Chroma_63600 DC load.
    """

    valid_modes = {'CC', 'CR', 'CV', 'CP', 'CZ', 'CCD', 'CCFS', 'TIM', 'SWD'}

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

        self.write_resource(f"LOAD {1 if state else 0}")

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
                              edge_polarity: str) -> None:
        """
        set_current_slew(slew_rate, edge_polarity)

        Changes the slew-rate setting of the load (for the specified edge
        polarity) in constant current mode.

        Args:
            slew_rate (float): desired slew-rate setting in A/s
            edge_polarity (str): edge to set the slew-rate of.
                       valid options are 'rise', 'fall', and 'both'.
        """

        edge_polarity = edge_polarity.upper()

        if edge_polarity.upper() not in {'BOTH', 'RISE', 'FALL'}:
            raise ValueError(f'Invalid edge_polarity: "{edge_polarity}"')

        slew_rate = float(slew_rate)*(1e-6)  # A/s --> A/us

        if edge_polarity.upper() == 'BOTH':
            self.write_resource(f'CURR:STAT:RISE {slew_rate}')
            self.write_resource(f'CURR:STAT:FALL {slew_rate}')
            return None

        self.write_resource(f'CURR:STAT:{edge_polarity} {slew_rate}')

    def get_current_slew_rate(self, edge_polarity: str
                              ) -> Union[float, Tuple[float]]:
        """
        get_current_slew_rate(edge_polarity)

        Retrives the slew-rate setting of the load (for the specified edge
        polarity) in constant current mode.

        Args:
            edge_polarity (str): edge to set the slew-rate of.
                       valid options are 'rise', 'fall', and 'both'.

        Returns:
            Union[float, Tuple[float]]: slew-rate setting in A/s.
        """

        if edge_polarity.upper() not in {'BOTH', 'RISE', 'FALL'}:
            raise ValueError(f'Invalid edge_polarity: "{edge_polarity}"')

        if edge_polarity.upper() == 'BOTH':
            responses = (self.query_resource('CURR:STAT:RISE?'),
                         self.query_resource('CURR:STAT:FALL?'))
            return tuple(map(lambda r: float(r)*(1e6), responses))

        response = self.query_resource(f'CURR:STAT:{edge_polarity}?')
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
                                 edge_polarity: str) -> None:
        """
        set_dynamic_current_slew(slew, edge_polarity)

        slew: float, desired slew-rate setting in A/s
        edge_polarity: str, edge to set the slew-rate of.
                       valid options are 'rise', 'fall', and 'both'

        changes the slew-rate setting of the load for the specified edge
        polarity in dynamic current mode. if edge_polarity = 'both', both
        polarities will be set to the value specified
        """

        if edge_polarity.upper() not in {"RISE", "FALL", "BOTH"}:
            raise IOError('Invalid option for arg "edge_polarity"')

        # note: load uses current slew rate in units of A/us, hence the
        # conversion
        if edge_polarity.upper() == 'BOTH':
            self.write_resource(f'CURR:DYN:RISE {slew_rate*1e-6}')
            self.write_resource(f'CURR:DYN:FALL {slew_rate*1e-6}')
            return None

        self.write_resource(
            f'CURR:DYN:{edge_polarity.upper()} {slew_rate*1e-6}'
            )

    def get_dynamic_current_slew(self, edge_polarity: str
                                 ) -> Union[float, Tuple[float]]:
        """
        get_dynamic_current_slew(slew, edge_polarity)

        edge_polarity: str, edge to set the slew-rate of.
                       valid options are 'rise', 'fall', and 'both'

        returns:
        slew: float, slew-rate setting in A/us,
              if edge_polarity = 'both' this returns of list of floats
              [rise rate, fall rate]

        returns the slew-rate setting of the load for the specified edge
        polarity in dynamic current mode. if edge_polarity = 'both', both
        polarities will be returned
        """

        if edge_polarity.upper() not in {"RISE", "FALL", "BOTH"}:
            raise IOError('Invalid option for arg "edge_polarity"')

        # note: load uses current slew rate in units of A/us, hence the
        # conversion
        if edge_polarity.upper() == 'BOTH':
            return (float(self.query_resource('CURR:DYN:RISE?')*1e6),
                    float(self.query_resource('CURR:DYN:FALL?')*1e6))

        response = self.query_resource(f'CURR:DYN:{edge_polarity.upper()}?')
        return float(response)*1e6

    def set_dynamic_current_time(self, on_time: float, level: int = 0) -> None:
        """
        set_dynamic_current_time(on_time, level=0)

        on_time: float, desired time to spend at level 'level'
                 min: 10us, max: 100s, resolves to nearest 10us
        level (optional): int, level to change setpoint of.
                          valid options are 0,1,2 (default is 0)

        changes the time that the load spends at the specified level in
        dynamic current mode. if level = 0 both levels will be set to the
        value specified
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

        level : int, level to change setpoint of.
                valid options are 0,1,2

        returns:
        on_time: float, time spent at level 'level'

        returns the time that the load spends at the specified level in
        dynamic current mode. if level = 0 both levels will be returned
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

        resistance: float, desired resistance setpoint in Ohms
        level (optional): int, level to change setpoint of.
                          valid options are 0,1,2 (default is 0)

        changes the resistance setpoint of the load for the specified level in
        constant resistance mode. if level = 0 both levels will be set to the
        value specified
        """

        if level == 0:
            self.write_resource(f'RES:STAT:L1 {resistance}')
            self.write_resource(f'RES:STAT:L2 {resistance}')
        else:
            self.write_resource(f'RES:STAT:L{level} {resistance}')

    def get_resistance(self, level: int) -> float:
        """
        get_resistance(level)

        level: int, level to get setpoint of.
               valid options are 1,2, and 0

        reads the resistance setpoint of the load for the specified level in
        constant resistance mode. if level == 0 then it will return a list
        containing both load levels.
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

    def set_mode(self, channel: int, mode: str,
                 range_setting: str = "M") -> None:
        """
        set_mode(channel, mode, range_setting="M")

        Sets the mode of the specified load card

        Args:
            channel: int, valid options are 1-5

            mode: str, mode / load type to set the desired channel to
                valid options can be accessed via the self.valid_modes
                attribute.

            range_setting: str, range of the given mode. Valid options are:
                "L", "M", and "H" for Low, Medium, and High range respectively
        """

        ranges = {"L", "M", "H"}

        if (mode in self.valid_modes) and (range_setting in ranges):

            self.set_channel(channel)
            self.write_resource(f'MODE {mode}{range_setting}')
        else:
            raise ValueError(
                f"Invalid mode/range combo: ({mode}, {range_setting})"
                )

    def get_mode(self, channel: int) -> Tuple[str, str]:
        """
        get_mode(channel)

        Gets the load mode from specified load channel

        Args:
            channel: int, valid options are 1-5

        Returns:
        Tuple[str, str]:  load mode (mode, range_setting). Mode (str),
            mode/load type to set the desired channel to valid options can be
            accessed via the self.valid_modes attribute.
            range_setting (str), range of the given mode. Valid options are:
            "L", "M", and "H" for Low, Medium, and High range respectiv
        """

        self.set_channel(channel)
        response = self.query_resource('MODE?')

        mode, range_setting = response[0:-1], response[-1]

        return (mode, range_setting)

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

        response = self._resource.query('VOLT:STAT:ILIM?')
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

        response = self._resource.query(f'ADV:SINE:IDC? {flag.upper()}')
        return float(response)

    def clear_errors(self):
        """
        clear_errors()

        Resets status of load and clears errors
        """

        self._resource.write('LOAD:PROT:CLE')
        return None

    def get_errors(self, channel, decode=False):
        """
        get_errors(channel)

        channel: int, valid options are 1-5
        decode: bool, whether to decode the status register in a human-readable
                form

        Returns the status register of the respective load channel. If decode
        is set to True the function returns a list of string descriptions of
        the faults set (default is False). The status register contains 1 Byte
        of possible faults, the bits in the register from bit 0 to 7 corespond
        with the following: 'OTP', 'OVP', 'OCP', 'OPP', 'REV', 'SYNC',
        'MAX_LIM', 'REMOTE_INHIBIT'
        """

        self.set_channel(channel)
        resp = self._resource.query('STAT:CHAN:COND?')
        status = int(resp.strip())
        status &= 255  # 2 Byte response only has 1 Byte of information
        if not decode:
            return status
        else:
            fault_labels = ['OTP', 'OVP', 'OCP', 'OPP',
                            'REV', 'SYNC', 'MAX_LIM', 'REMOTE_INHIBIT']
            errors = []
            for n in range(0, 7):
                if (status & 2**n) >> n:
                    errors.append(fault_labels[n])
            return errors

    def measure_voltage(self):
        """
        measure_voltage()

        returns measurement of the voltage present across the load in Vdc
        returns: float
        """

        response = self._resource.query('MEAS:VOLT?')
        return float(response)

    def measure_current(self):
        """
        measure_current()

        returns measurement of the current through the load in Adc
        returns: float
        """

        response = self._resource.query('MEAS:CURR?')
        return float(response)

    def measure_power(self):
        """
        measure_power()

        returns measurement of the power consumed by the load in W
        returns: float
        """

        response = self._resource.query('FETC:POW?')
        return float(response)

    def measure_total_voltage(self, return_average=False):
        """
        measure_total_voltage()

        return_average: Bool, determines whether a list of the individual load
                        measurements is returned or the average of all
                        measurements (default = False).

        returns measurement of the voltage present across all loads in Vdc
        returns: list of floats or float
        """

        response = self._resource.query('MEAS:ALLV?')
        voltages = list(map(float, response.split(',')))

        if return_average:
            return sum(voltages)/len(voltages)
        else:
            return voltages

    def measure_total_current(self, return_sum=False):
        """
        measure_total_current()

        return_sum: Bool, determines whether a list of the individual load
                    measurements is returned or the sum of all measurements
                    (default = False).

        returns measurement of the current through all loads in Adc
        returns: list of floats or float
        """

        response = self._resource.query('MEAS:ALLC?')
        currents = list(map(float, response.split(',')))

        if return_sum:
            return sum(currents)
        else:
            return currents

    def measure_total_power(self, return_sum=False):
        """
        measure_total_power()

        return_sum: Bool, determines whether a list of the individual load
                    measurements is returned or the sum of all measurements
                    (default = False).

        returns measurement of the power consumed by the all loads in W
        returns: list of floats or float
        """

        response = self._resource.query('MEAS:ALLP?')
        powers = list(map(float, response.split(',')))

        if return_sum:
            return sum(powers)
        else:
            return powers
