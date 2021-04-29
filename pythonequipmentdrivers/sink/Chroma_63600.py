from pythonequipmentdrivers import Scpi_Instrument as _Scpi_Instrument
import numpy as _np
from time import sleep as _sleep


# Look into programming "sequences" and "programs" to the device. See basic
# description in the users manual ~pg 118 (4-32)

# add set/get methods for the current and resistance ranges

class Chroma_63600(_Scpi_Instrument):
    """
    Chroma_63600(address)

    address : str, address of the connected electronic load

    object for accessing basic functionallity of the Chroma_63600 DC load. Code
    was adapted from code written by Peter Makrum
    """

    def __init__(self, address):
        super().__init__(address)
        self.valid_modes = ['CC', 'CR', 'CV', 'CP', 'CZ', 'CCD', 'CCFS', 'TIM'
                            'SWD']
        return

    def _channel_index(self, channel, reverse=False):
        """
        _channel_index(channel, reverse=False)

        reverse: Bool

        Reindexes channel numbers sent to the device so the user doesn't have
        to the conversion. If reverse=True the conversion is reversed. Load has
        5 addresses but uses every-other odd number instead of numbering them
        sequentially
        """
        if not reverse:
            if (channel > 5) and (channel < 1):
                raise ValueError("Invalid Channel Number")
            else:
                return 2*channel - 1
        else:
            return int((channel + 1)/2)

    def set_state(self, state):
        """
        set_state(state)

        state: int, 1 or 0 for on and off respectively

        enables/disables the input for the load
        """

        self.instrument.write(f"LOAD {state}")
        return

    def get_state(self):
        """
        get_state()

        returns the current state of the input to the load

        returns: int
        1: enabled, 0: disabled
        """

        if self.instrument.query("LOAD?").rstrip('\n') == "ON":
            return 1
        return 0

    def on(self):
        """
        on()

        enables the input for the load
        equivalent to set_state(1)
        """

        self.set_state(1)
        return

    def off(self):
        """
        off()

        disables the input for the load
        equivalent to set_state(0)
        """

        self.set_state(0)
        return

    def toggle(self, return_state=False):
        """
        toggle(return_state=False)

        return_state: boolean, whether or not to return the state load's input

        reverses the current state of the load's input

        if return_state = True the boolean state of the load after toggle() is
        executed will be returned
        """

        if self.get_state():
            self.off()
        else:
            self.on()

        if return_state:
            return self.get_state()
        return

    def set_current(self, current, level=0):
        """
        set_current(current, level=0)

        current: float, desired current setpoint
        level (optional): int, level to change setpoint of.
                          valid options are 0,1,2 (default is 0)

        changes the current setpoint of the load for the specified level in
        constant current mode. if level = 0 both levels will be set to the
        value specified
        """

        if level == 0:
            self.instrument.write(f'CURR:STAT:L1 {float(current)}')
            self.instrument.write(f'CURR:STAT:L2 {float(current)}')
        else:
            command_str = f'CURR:STAT:L{int(level)} {float(current)}'
            self.instrument.write(command_str)
        return

    def get_current(self, level):
        """
        get_current(level)

        level: int, level to get setpoint of.
               valid options are 1,2, and 0

        reads the current setpoint of the load for the specified level in
        constant current mode. if level == 0 then it will return a list
        containing both load levels.
        """

        if level == 0:
            currents = []
            currents = (float(self.instrument.query('CURR:STAT:L1?')),
                        float(self.instrument.query('CURR:STAT:L2?')))
            return currents
        else:
            response = self.instrument.query(f'CURR:STAT:L{int(level)}?')
            return float(response)

    def set_current_slew(self, slew, edge_polarity):
        """
        set_current_slew(slew, edge_polarity)

        slew: float, desired slew-rate setting in A/us
        edge_polarity: str, edge to set the slew-rate of.
                       valid options are 'rise', 'fall', and 'both'

        changes the slew-rate setting of the load for the specified edge
        polarity in constant current mode. if edge_polarity = 'both', both
        polarities will be set to the value specified
        """

        if edge_polarity == 'rise':
            self.instrument.write(f'CURR:STAT:RISE {slew}')
        elif edge_polarity == 'fall':
            self.instrument.write(f'CURR:STAT:FALL {slew}')
        elif edge_polarity == 'both':
            self.instrument.write(f'CURR:STAT:RISE {slew}')
            self.instrument.write(f'CURR:STAT:FALL {slew}')
        else:
            raise IOError('Invalid option for arg "edge_polarity"')
        return

    def get_current_slew(self, edge_polarity):
        """
        get_current_slew(slew, edge_polarity)

        edge_polarity: str, edge to set the slew-rate of.
                       valid options are 'rise', 'fall', and 'both'

        returns:
        slew: float, desired slew-rate setting in A/us,
              if edge_polarity = 'both' this returns of list of floats
              [rise rate, fall rate]

        returns the slew-rate setting of the load for the specified edge
        polarity in constant current mode. if edge_polarity = 'both', both
        polarities will be returned
        """

        if edge_polarity == 'rise':
            resp = self.instrument.query('CURR:STAT:RISE?')
            return float(resp)

        elif edge_polarity == 'fall':
            resp = self.instrument.query('CURR:STAT:FALL?')
            return float(resp)

        elif edge_polarity == 'both':
            slews = []
            resp = self.instrument.query('CURR:STAT:RISE?')
            slews.append(float(resp))
            resp = self.instrument.query('CURR:STAT:FALL?')
            slews.append(float(resp))
            return slews
        else:
            raise IOError('Invalid option for arg "edge_polarity"')

    def set_dynamic_current(self, current, level=0):
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
            self.instrument.write(f'CURR:DYN:L1 {float(current)}')
            self.instrument.write(f'CURR:DYN:L2 {float(current)}')
        else:
            command_str = f'CURR:DYN:L{int(level)} {float(current)}'
            self.instrument.write(command_str)
        return

    def get_dynamic_current(self, level):
        """
        get_dynamic_current(level)

        level: int, level to get setpoint of.
               valid options are 1,2, and 0

        reads the current setpoint of the load for the specified level in
        dynamic current mode. if level == 0 then it will return a list
        containing both load levels.
        """

        if level == 0:
            currents = (float(self.instrument.query('CURR:DYN:L1?')),
                        float(self.instrument.query('CURR:DYN:L2?')))
            return currents
        else:
            response = self.instrument.query(f'CURR:DYN:L{int(level)}?')
            return float(response)

    def set_dynamic_current_slew(self, slew, edge_polarity):
        """
        set_dynamic_current_slew(slew, edge_polarity)

        slew: float, desired slew-rate setting in A/us
        edge_polarity: str, edge to set the slew-rate of.
                       valid options are 'rise', 'fall', and 'both'

        changes the slew-rate setting of the load for the specified edge
        polarity in dynamic current mode. if edge_polarity = 'both', both
        polarities will be set to the value specified
        """

        if edge_polarity == 'rise':
            self.instrument.write(f'CURR:DYN:RISE {slew}')
        elif edge_polarity == 'fall':
            self.instrument.write(f'CURR:DYN:FALL {slew}')
        elif edge_polarity == 'both':
            self.instrument.write(f'CURR:DYN:RISE {slew}')
            self.instrument.write(f'CURR:DYN:FALL {slew}')
        else:
            raise IOError('Invalid option for arg "edge_polarity"')
        return

    def get_dynamic_current_slew(self, edge_polarity):
        """
        get_dynamic_current_slew(slew, edge_polarity)

        edge_polarity: str, edge to set the slew-rate of.
                       valid options are 'rise', 'fall', and 'both'

        returns:
        slew: float, desired slew-rate setting in A/us,
              if edge_polarity = 'both' this returns of list of floats
              [rise rate, fall rate]

        returns the slew-rate setting of the load for the specified edge
        polarity in dynamic current mode. if edge_polarity = 'both', both
        polarities will be returned
        """

        if edge_polarity == 'rise':
            resp = self.instrument.query('CURR:DYN:RISE?')
            return float(resp)

        elif edge_polarity == 'fall':
            resp = self.instrument.query('CURR:DYN:FALL?')
            return float(resp)

        elif edge_polarity == 'both':
            slews = []
            resp = self.instrument.query('CURR:DYN:RISE?')
            slews.append(float(resp))
            resp = self.instrument.query('CURR:DYN:FALL?')
            slews.append(float(resp))
            return slews
        else:
            raise IOError('Invalid option for arg "edge_polarity"')

    def set_dynamic_current_time(self, on_time, level=0):
        """
        set_dynamic_current_time(on_time, level=0)

        on_time: float, desired time to spend at level 'level'
                 min: 10us, max: 100s, 10us steps
        level (optional): int, level to change setpoint of.
                          valid options are 0,1,2 (default is 0)

        changes the time that the load spends at the specified level in
        dynamic current mode. if level = 0 both levels will be set to the
        value specified
        """

        if level == 0:
            self.instrument.write(f'CURR:DYN:T1 {float(on_time)}')
            self.instrument.write(f'CURR:DYN:T2 {float(on_time)}')
        else:
            command_str = f'CURR:DYN:T{int(level)} {float(on_time)}'
            self.instrument.write(command_str)
        return

    def get_dynamic_current_time(self, level):
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
            times = (float(self.instrument.query('CURR:DYN:T1?')),
                     float(self.instrument.query('CURR:DYN:T2?')))
            return times
        else:
            response = self.instrument.query(f'CURR:DYN:T{int(level)}?')
            return float(response)

    def set_dynamic_current_repeat(self, count):
        """
        set_dynamic_current_repeat(count)

        count: int, number of cycles. max: 65535, min: 0, res: 1

        sets the number of times to cycle through the two dynamic current
        set-points
        """

        self.instrument.write(f'CURR:DYN:REP {count}')
        return

    def get_dynamic_current_repeat(self):
        """
        get_dynamic_current_repeat(count)

        returns:
        count: int, number of cycles. max: 65535, min: 0, res: 1

        returns the number of times to cycle through the two dynamic current
        set-points
        """

        resp = self.instrument.query('CURR:DYN:REP?')

        return int(resp)

    def set_resistance(self, resistance, level=0):
        """
        set_resistance(resistance, level=0)

        resistance: float, desired resistance setpoint in ohm
        level (optional): int, level to change setpoint of.
                          valid options are 0,1,2 (default is 0)

        changes the resistance setpoint of the load for the specified level in
        constant resistance mode. if level = 0 both levels will be set to the
        value specified
        """

        if level == 0:
            self.instrument.write(f'RES:STAT:L1 {float(resistance)}')
            self.instrument.write(f'RES:STAT:L2 {float(resistance)}')
        else:
            command_str = f'RES:STAT:L{int(level)} {float(resistance)}'
            self.instrument.write(command_str)
        return

    def get_resistance(self, level):
        """
        get_resistance(level)

        level: int, level to get setpoint of.
               valid options are 1,2, and 0

        reads the resistance setpoint of the load for the specified level in
        constant resistance mode. if level == 0 then it will return a list
        containing both load levels.
        """

        if level == 0:
            resistances = (float(self.instrument.query('RES:STAT:L1?')),
                           float(self.instrument.query('RES:STAT:L2?')))
            return resistances
        else:
            response = self.instrument.query(f'RES:STAT:L{int(level)}?')
            return float(response)

    def set_channel(self, channel):
        """
        set_channel(channel)

        channel: int, index of the channel to control.
                 valid options are 1-5

        Selects the specified Channel to use for software control

        """
        idx = self._channel_index(channel)
        self.instrument.write(f'CHAN {idx}')
        return

    def get_channel(self):
        """
        get_channel()

        Get current selected Channel

        returns: int
        """
        resp = self.instrument.query('CHAN?')
        channel = self._channel_index(int(resp), reverse=True)
        return channel

    def set_mode(self, channel, mode, range_setting=1):
        """
        set_mode(channel, mode, range_setting=1)

        channel: int, valid options are 1-5

        mode: str, mode / load type to set the desired channel to
              valid options can be accessed via the self.valid_modes attribute.

        range_setting: int, range of the given mode.
                       Valid options are:
                           0: Low range
                           1: Medium range
                           2: High range

        Sets the mode of the specified load card
        """

        if (mode in self.valid_modes) and (range_setting in [0, 1, 2]):
            ranges = ["L", "M", "H"]
            self.set_channel(channel)
            self.instrument.write(f'MODE {mode}{ranges[range_setting]}')
        else:
            err_str = f"Invalid mode/range combo: ({mode}, {range_setting})"
            raise ValueError(err_str)
        return

    def get_mode(self, channel):
        """
        get_mode(channel)

        channel: int, valid options are 1-5

        returns a tuple (mode, range_setting)

        mode: str, mode / load type to set the desired channel to
              valid options can be accessed via the self.valid_modes attribute.

        range_setting: int, range of the given mode.
                       Valid options are:
                           0: Low range
                           1: Medium range
                           2: High range

        Gets the load mode from specified load channel
        """

        ranges = {"L": 0, "M": 1, "H": 2}

        self.set_channel(channel)
        resp = self.instrument.query('MODE?')
        resp = resp.strip()

        mode, range_setting = resp[0:-1], resp[-1]

        return (mode, ranges[range_setting])

    def set_parallel_state(self, state):
        """
        set_parallel_state(state)

        state: int, valid options are 0 and 1.

        Enables/Disables parallel mode operation of individual channels wihin
        the load.
        """

        self.instrument.write(f'CONF:PARA:INIT {state}')
        return

    def get_parallel_state(self):
        """
        get_parallel_state()

        Returns the state of the loads parallel operation.
        """
        resp = self.instrument.query('CONF:PARA:INIT?')
        resp = resp.strip()
        if resp == "ON":
            return True
        elif resp == "OFF":
            return False
        else:
            raise IOError(f"Unknown response: {resp}")

    def set_parallel_mode(self, channel, mode):
        """
        set_parallel_mode(channel, mode)

        channel: int, valid options are 1-5

        mode: int, a code corresponding to the parallel mode of the respective
               channel. Valid options are:
                    0: None
                    1: Master
                    2: Slave

        Sets parallel mode for each channel
        """
        self.set_channel(channel)
        self.instrument.write(f'CONF:PARA:MODE {mode}')
        return

    def get_parallel_mode(self, channel):
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
        self.set_channel(channel)
        resp = self.instrument.query('CONF:PARA:MODE?')
        resp = resp.strip()

        if resp == "NONE":
            return 0
        if resp == "MASTER":
            return 1
        elif resp == "SLAVE":
            return 2
        else:
            raise IOError(f"Unknown response: {resp}")

    def set_channel_state(self, channel, state):
        """
        set_channel_state(channel, state)

        channel: int, valid options are 1-5
        state = 0, 1

        Enables/disables the respective load channel

        """

        self.set_channel(channel)
        self.instrument.write(f'CHAN:ACT {state}')
        return

    def get_channel_state(self, channel):
        """
        get_channel_state(channel)

        channel: int, valid options are 1-5

        Returns whether or not the respective load channel is Enabled/disabled
        (bool)
        """

        self.set_channel(channel)
        resp = self.instrument.query('CHAN:ACT?')
        resp = resp.strip()
        if resp == "ON":
            return True
        elif resp == "OFF":
            return False
        else:
            raise IOError(f"Unknown response: {resp}")

    # # need to investigate what this function actually does
    # def set_sync_mode(self, channel, state):
    #     """
    #     Set sync mode for each channel
    #     """
    #     self.set_channel(channel)
    #     self.visa.write(f'CONF:SYNC:MODE {state}')
    #     return

    def set_voltage(self, voltage, level=0):
        """
        set_voltage(voltage, level=0)

        voltage: float, desired voltage setpoint in Vdc
        level (optional): int, level to change setpoint of.
                          valid options are 0,1,2 (default is 0)

        changes the voltage setpoint of the load for the specified level in
        constant voltage mode. if level = 0 both levels will be set to the
        value specified
        """

        if level == 0:
            self.instrument.write(f'VOLT:STAT:L1 {float(voltage)}')
            self.instrument.write(f'VOLT:STAT:L2 {float(voltage)}')
        else:
            command_str = f'VOLT:STAT:L{int(level)} {float(voltage)}'
            self.instrument.write(command_str)
        return

    def get_voltage(self, level):
        """
        get_voltage(level)

        level: int, level to get setpoint of.
               valid options are 1,2, and 0

        reads the voltage setpoint of the load for the specified level in
        constant voltage mode. if level == 0 then it will return a list
        containing both load levels.
        """

        if level == 0:
            voltages = (float(self.instrument.query('VOLT:STAT:L1?')),
                        float(self.instrument.query('VOLT:STAT:L2?')))
            return voltages
        else:
            response = self.instrument.query(f'VOLT:STAT:L{int(level)}?')
            return float(response)

    def set_cv_current_limit(self, current):
        """
        set_cv_current_limit(current)

        current: float, desired current setpoint

        changes the current setpoint of the load for the specified level in
        constant voltage mode.
        """

        self.instrument.write(f'VOLT:STAT:ILIM {current}')
        return

    def get_cv_current_limit(self):
        """
        get_cv_current_limit()

        returns:
        current: float, current setpoint in Adc

        returns the current setpoint of the load for the in constant voltage
        mode.
        """

        resp = self.instrument.query('VOLT:STAT:ILIM?')

        return float(resp)

    def set_dynamic_sine_frequency(self, freq):

        """
        set_dynamic_sine_frequency(freq)

        Sets the frequency of the sine wave current used in the
        'advanced sine-wave' mode of operation in Hz. Min/Max setting can be
        determined using the get_dynamic_sine_frequency method with the min/max
        flag.

        Arguments:
            freq {float} -- desired frequency in Hz
        """

        self.instrument.write(f'ADV:SINE:FREQ {freq}')
        return

    def get_dynamic_sine_frequency(self, flag=''):

        """
        get_dynamic_sine_frequency(flag='')

        Returns the frequency of the sine wave current used in the
        'advanced sine-wave' mode of operation in Hz. Can also return the
        Min/Max possible setting with the min/max flag.

        Keyword Arguments:
            flag {str} -- flag used to determine the frequency limits of the
            electronic loads sine-wave capabiity. Valid options are 'Min',
            'Max', and '' for the minimum, maximum, and current settings
            respectively (Not case-sensitive, default: {''}).

        Raises:
            ValueError: raised if an invalid flag is passed

        Returns:
            freq {float} -- current frequency setpoint (or limit) in Hz.
        """

        flag = flag.upper()
        if flag not in ['MIN', 'MAX', '']:
            raise ValueError(f'Invalid value {flag} for arg "value"')

        resp = self.instrument.query(f'ADV:SINE:FREQ? {flag}')
        freq = float(resp)
        return freq

    def set_dynamic_sine_amplitude_ac(self, amp):

        """
        set_dynamic_sine_amplitude_ac(amp)

        Sets the amplitude of the sine wave current used in the
        'advanced sine-wave' mode of operation in A_DC. Min/Max setting can be
        determined using the get_dynamic_sine_amplitude_ac method with the
        min/max flag.

        Arguments:
            freq {float} -- desired amplitude in A_DC
        """

        amp_peak2peak = amp*2  # convert Amplitude to peak-to-peak
        self.instrument.write(f'ADV:SINE:IAC {amp_peak2peak}')
        return

    def get_dynamic_sine_amplitude_ac(self, flag=''):

        """
        get_dynamic_sine_amplitude_ac(flag='')

        Returns the amplitude of the sine wave current used in the
        'advanced sine-wave' mode of operation in A_DC. Can also return the
        Min/Max possible setting with the min/max flag.

        Keyword Arguments:
            flag {str} -- flag used to determine the amplitude limits of the
            electronic loads sine-wave capabiity. Valid options are 'Min',
            'Max', and '' for the minimum, maximum, and current settings
            respectively (Not case-sensitive, default: {''}).

        Raises:
            ValueError: raised if an invalid flag is passed

        Returns:
            freq {float} -- current amplitude setpoint (or limit) in A_DC.
        """

        flag = flag.upper()
        if flag not in ['MIN', 'MAX', '']:
            raise ValueError(f'Invalid value {flag} for arg "value"')

        resp = self.instrument.query(f'ADV:SINE:IAC? {flag}')
        amp_peak2peak = float(resp)
        amp = amp_peak2peak/2  # convert peak-to-peak to Amplitude
        return amp

    def set_dynamic_sine_dc_level(self, amp):

        """
        set_dynamic_sine_dc_level(amp)

        Sets the DC level of the sine wave current used in the
        'advanced sine-wave' mode of operation in A_DC. Min/Max setting can be
        determined using the get_dynamic_sine_dc_level method with the
        min/max flag.

        Arguments:
            freq {float} -- desired DC level in A_DC
        """

        self.instrument.write(f'ADV:SINE:IDC {amp}')
        return

    def get_dynamic_sine_dc_level(self, flag=''):

        """
        get_dynamic_sine_dc_level(flag='')

        Returns the DC level of the sine wave current used in the
        'advanced sine-wave' mode of operation in A_DC. Can also return the
        Min/Max possible setting with the min/max flag.

        Keyword Arguments:
            flag {str} -- flag used to determine the DC level limits of the
            electronic loads sine-wave capabiity. Valid options are 'Min',
            'Max', and '' for the minimum, maximum, and current settings
            respectively (Not case-sensitive, default: {''}).

        Raises:
            ValueError: raised if an invalid flag is passed

        Returns:
            freq {float} -- current DC level setpoint (or limit) in A_DC.
        """

        flag = flag.upper()
        if flag not in ['MIN', 'MAX', '']:
            raise ValueError(f'Invalid value {flag} for arg "value"')

        resp = self.instrument.query(f'ADV:SINE:IDC? {flag}')
        amp = float(resp)
        return amp

    def reset(self):
        """
        reset()

        Resets all registers to default settings
        """

        self.instrument.write('*RST')
        return

    def clear_errors(self):
        """
        clear_errors()

        Resets status of load and clears errors
        """

        self.instrument.write('LOAD:PROT:CLE')
        return

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
        resp = self.instrument.query('STAT:CHAN:COND?')
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

        response = self.instrument.query('MEAS:VOLT?')
        return float(response)

    def measure_current(self):
        """
        measure_current()

        returns measurement of the current through the load in Adc
        returns: float
        """

        response = self.instrument.query('MEAS:CURR?')
        return float(response)

    def measure_power(self):
        """
        measure_power()

        returns measurement of the power consumed by the load in W
        returns: float
        """

        response = self.instrument.query('FETC:POW?')
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

        response = self.instrument.query('MEAS:ALLV?')
        voltages = list(map(float, response.split(',')))

        if return_average:
            return _np.mean(voltages)
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

        response = self.instrument.query('MEAS:ALLC?')
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

        response = self.instrument.query('MEAS:ALLP?')
        powers = list(map(float, response.split(',')))

        if return_sum:
            return sum(powers)
        else:
            return powers

    def pulse(self, level, duration):
        """
        pulse(level, duration)

        level: float/int, current level of "high" state of the pulse in Amps
        duration: float/int, duration of the "high" state of the pulse in
                  seconds

        generates a square pulse with height and duration specified by level
        and duration. will start and return to the previous current level set
        on the load before the execution of pulse(). level can be less than or
        greater than the previous current setpoint
        """

        start_level = self.get_current(1)
        self.set_current(level)
        _sleep(duration)
        self.set_current(start_level)
        return

    def ramp(self, start, stop, n=100, dt=0.01):
        """
        ramp(start, stop, n=100, dt=0.01)

        start: float/int, starting current setpoint of the ramp in Adc
        stop: float/int, ending current setpoint of the ramp in Adc
        n (optional): int, number of points in the ramp between start and stop
            default is 100
        dt (optional): float/int, time between changes in the value of the
                       setpoint in seconds. default is 0.01 sec

        generates a linear ramp on the loads current specified by the
        parameters start, stop, n, and dt. input of the load should be enabled
        before executing this command. contrary to what this documentation may
        imply, start can be higher than stop or vise-versa. minimum dt is
        limited by the communication speed of the interface used to communicate
        with this device
        """

        for i in _np.linspace(start, stop, int(n)):
            self.set_current(i)
            _sleep(dt)
        return

    def slew(self, start, stop, n=100, dt=0.01, dwell=0):
        """
        slew(start, stop, n=100, dt=0.01, dwell=0)

        start: float/int, "low" current setpoint of the ramp in Adc
        stop: float/int, "high" current setpoint of the ramp in Adc
        n (optional): int, number of points in the ramp between start and stop
            default is 100
        dt (optional): float/int, time between changes in the value of the
                       setpoint in seconds. default is 0.01 sec
        dwell (optional): float/int, time to dwell at the "stop" value before
                          the ramp back to "start". default is 0 sec (no dwell)

        generates a triangular waveform on the loads current specified by the
        parameters start, stop, n, and dt. optionally, a dwell acan be added at
        the top of the waveform to create a trapezoidal load shape. input of
        the load should be enabled before executing this command. contrary to
        what this documentation may imply, start can be higher than stop or
        vise-versa. minimum dt is limited by the communication speed of the
        interface used to communicate with this device
        """

        self.ramp(start, stop, n=int(n), dt=dt)
        _sleep(dwell)
        self.ramp(stop, start, n=int(n), dt=dt)
        return

    # def config_1Master_xSlave (self, CHROMALOAD_NUMCHUSED, CHROMALOAD_MODE):
    #     """
    #     Reset array, Set Ch1 as master remainder as slave \n
    #     set all channels to one mode as selected \n
    #     Trun ON parallel mode
    #     """
    #     self.reset_all()
    #     for Slave_Ch in range( 3 , CHROMALOAD_NUMCHUSED + 1, 2):
    #         self.set_mode(Slave_Ch, '%s' %CHROMALOAD_MODE)
    #         self.set_parallel_mode(Slave_Ch, 'SLAVE')
    #         self.set_sync_mode(Slave_Ch, 'SLAVE')
    #     self.set_mode(1, '%s' %CHROMALOAD_MODE)
    #     self.set_parallel_mode( 1 , 'MASTER')
    #     self.set_sync_mode( 1 , 'MASTER')
    #     self.set_channel(1)
    #     self.set_parallel_state('ON')
    #     return


if __name__ == '__main__':
    # import pythonequipmentdrivers as ped
    # import numpy as np
    # from time import sleep

    # config_file = "C:/Users/agiasson/Desktop/apps_bench4_config.json"
    # env = ped.EnvironmentSetup(config_file, init_devices=True)
    # sink = Chroma_63600("GPIB0::7::INSTR")
    pass
