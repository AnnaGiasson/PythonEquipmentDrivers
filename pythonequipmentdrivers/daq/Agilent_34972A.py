from pythonequipmentdrivers import VisaResource
from time import sleep


class Agilent_34972A(VisaResource):
    """
    Agilent_34972A()

    address: str, address of the connected data aquisition dac
    ch_change_time, optional: mux switching time
    object for accessing basic functionallity of the AG_34972A data aquisition
    dac.

    Additional Information:
    functions based on 34972-90001.pdf at
    https://literature.cdn.keysight.com/litweb/pdf/34972-90001.pdf
    Ted Kus, tkus@vicr.com

    recommend channels be passed in a list
    """

    valid_modes = {'VOLT': 'VOLT',
                   'CURR': 'CURR',
                   'V': 'VOLT',
                   'A': 'CURR',
                   'FREQ': 'FREQ',
                   'F': 'FREQ',
                   'OHMS': 'RES',
                   'O': 'RES',
                   'RES': 'RES',
                   'DIOD': 'DIOD',
                   'D': 'DIOD',
                   'DIODE': 'DIOD',
                   'CONT': 'CONT',
                   'C': 'CONT',
                   'PER': 'PER',
                   'P': 'PER'
                   }

    valid_ranges = {'AUTO', 'MIN', 'MAX', 'DEF',
                    '0.1', '1', '10', '100', '300'}

    valid_cranges = {'AUTO', 'MIN', 'MAX', 'DEF',
                     '0.01', '0.1', '1'}

    valid_Rranges = {'AUTO', 'MIN', 'MAX', 'DEF',
                     '100', '1E3', '10E3', '100E3', '1E6', '10E6', '100E6'}

    nplc = {'0.02', '0.2', '1', '2', '10', '20', '100', '200', 'MIN', 'MAX'}

    valid_resolutions = {'MIN': 0.0001,  # lookup based on nplc
                         'MAX': 0.00000022,  # this * range = resolution
                         '0.02': 0.0001,
                         '0.2': 0.00001,
                         '1': 0.000003,
                         '2': 0.0000022,
                         '10': 0.000001,
                         '20': 0.0000008,
                         '100': 0.0000003,
                         '200': 0.00000022}
    valid_trigger = {'BUS': 'BUS',
                     'IMMEDIATE': 'IMMediate',
                     'IMM': 'IMMediate',
                     'EXTERNAL': 'EXTernal',
                     'EXT': 'EXTernal',
                     'ALARM1': 'ALARm1',
                     'ALARM2': 'ALARm2',
                     'ALARM3': 'ALARm3',
                     'ALARM4': 'ALARm4',
                     'TIMER': 'TIMer',
                     'TIME': 'TIMer',
                     'TIM': 'TIMer'}

    def __init__(self, address, **kwargs) -> None:
        super().__init__(address)
        if kwargs.get('reset', False):
            self.clear_status()
        self.ch_change_time = kwargs.get('ch_change_time', float(0.050))
        # measure_time = n * nplc * (1 / 50) + 0.02  # 50Hz assumption + buffer
        self.nplc_default = 1  # power line cycles to average
        self.line_frequency = kwargs.get('line_frequency', float(50))  # Hz
        self.scanlist = self.get_scan_list()
        self.measure_time = self.set_measure_time()
        self.trigger_mode = self.get_trigger_source()

    def resp_format(self, response, resp_type: type = int):
        """resp_format(response(str data), type(int/float/etc))

        Args:
            response (str): string of data to parse
            type (type, optional): what type to output. Defaults to int.

        Returns:
            list[type], or type: return is a list if more than 1 element
                                 otherwise returns the single element as type
        """

        if '@' in response:
            start = response.find('@')  # note this returns -1 if not found
            stop = -1
        else:
            start = -1
            stop = None
        # that works out OK because data needs to be parsed from the first
        # character anyway, so this is not an error, but I don't like
        # that it isn't explicitly trying to find the correct character
        try:
            response = list(map(resp_type, response[start+1:stop].split(',')))
        except ValueError:
            raise
        if len(response) == 1:
            return response[0]
        return response

    def set_mode(self, mode, chan, **kwargs):
        """
        set_mode(mode)

        mode (str): type of measurement to be done
            valid modes are: 'VDC', 'VAC', 'ADC', 'AAC', 'FREQ', 'OHMS',
                             'DIOD', 'CONT', 'PER'
            which correspond to DC voltage, AC voltage, DC current, AC current,
            frequency, resistence, diode voltage, continuity, and period
            respectively (not case sensitive)
        chan (list, int, str): channels to apply to
        Configures the dac to perform the specified measurement
        RANGe will be AUTO
        NPLC/RESOLUTION will be DEFAULT (usually 5.5d)
        """

        mode = mode.upper()
        if mode in self.valid_modes:
            chanstr, chanlist = self.format_channel_list(chan)
            self.write_resource(f"CONF:{self.valid_modes[mode]} (@{chanstr})",
                                **kwargs)
        else:
            raise ValueError("Invalid mode option")

    def get_mode(self, chan, **kwargs):
        """
        get_mode(chan)

        retrives type of measurement the dac is current configured to
        perform.

        returns: str
        """
        chanstr, chanlist = self.format_channel_list(chan)
        response = self.query_resource(f"FUNC? (@{chanstr})", **kwargs)
        response = response.replace('"', '')
        return response

    def get_error(self, **kwargs):
        """get_error

        Returns:
            [list]: last error in the buffer
        """
        response = self.query_resource('SYSTem:ERRor?', **kwargs)
        return self.resp_format(response, str)

    def set_trigger_source(self, trigger: str = 'IMMEDIATE', **kwargs):
        """
        set_trigger(trigger)

        trigger: str, type of trigger to be done
            valid modes are: 'BUS', 'IMMEDIATE', 'EXTERNAL'
            which correspond to 'BUS', 'IMMEDIATE', 'EXTERNAL'
            respectively (not case sensitive)

        Configures the multimeter to trigger as specified
        """
        trigger = trigger.upper()
        if trigger in self.valid_trigger:
            self.trigger_mode = self.valid_trigger[trigger]
            self.write_resource(f"TRIG:SOUR {self.trigger_mode}", **kwargs)
        else:
            raise ValueError("Invalid trigger option")
        return

    def get_trigger_source(self, **kwargs):
        self.trigger_mode = self.valid_trigger[self.resp_format(
            self.query_resource("TRIG:SOUR?", **kwargs), str)]
        return self.trigger_mode

    def set_trigger_count(self, count: int = None, **kwargs):
        """set_trigger_count(count)

        Args:
            count ([int]): how many readings to take when triggered

        Raises:
            ValueError: [description]
        """
        if count is None:
            return self.get_trigger_count()
        elif isinstance(count, int):
            self.write_resource(f"TRIG:COUN {count}", **kwargs)
        else:
            raise ValueError("Invalid trigger count number type, use int")
        return

    def get_trigger_count(self, **kwargs):
        return int(self.resp_format(self.query_resource("TRIG:COUN?",
                                                        **kwargs), float))

    def set_trigger_timer(self, delaytime: float = None, **kwargs):
        """set_trigger_count(delaytime)

        Args:
            delaytime ([float]): delay between scanlist readings when triggered
                             note, entire scanlist is measured each time
                             then the delay runs, then the scanlist again...
                             if None is sent, returns count
        Raises:
            ValueError: [description]
        """
        if delaytime is None:
            return self.get_trigger_timer()
        if isinstance(delaytime, (float, int)):
            self.write_resource(f"TRIG:TIM {delaytime}", **kwargs)
        else:
            raise ValueError("Invalid trigger count number type, use int")
        return

    def get_trigger_timer(self, **kwargs):
        return self.resp_format(self.query_resource("TRIG:TIM?",
                                                    **kwargs), float)

    def trigger(self, wait: bool = True, **kwargs) -> None:
        """trigger(wait)
        If the unit is setup to BUS trigger, sends trigger, otherwise pass
        If the unit is not setup to BUS trigger, it will log an error

        Args:
            wait (bool, optional): Does not return to caller until scantime
                                   is complete.  Prevents Trigger Ignored
                                   errors (-211). Defaults to True.
        Returns:
            None
        """
        if self.trigger_mode == self.valid_trigger['BUS']:
            self.write_resource('*TRG', **kwargs)
        else:
            print(f"Trigger not configured, set as: {self.trigger_mode}"
                  f" should be {self.valid_trigger['BUS']}")

        if wait:
            sleep(self.measure_time)  # should work most of the time.
            # it should also wait nplc time per channel
            # need to make a function to track nplc time
            # if nplc is longer than 1, then this will fail, if shorter
            # then this will take way too long

    def get_scan_list(self, **kwargs):
        """
        get_scan_list()

        determine which channels are currently in the scan list,
        you can send the ROUTe:SCAN? query command.
        instrument data comes back raw such as: '#210(@101,102)\n'

        returns:
            list (int): channel numbers in scanlist
        """
        response = self.query_resource("ROUT:SCAN?", **kwargs)
        chanstr, self.scanlist = self.format_channel_list(response)
        # start = response.find('@')
        # self.scanlist = list(map(int, response[start+1:-1].split(',')))
        return self.scanlist

    def format_channel_list(self, chan):
        if isinstance(chan, list):
            chanstr = ",".join(map(str, chan))
            chanlist = chan
        elif isinstance(chan, str):
            chanstr = chan
            temp = chan.strip()
            if ':' in temp:
                # used when someone passes a str with example:
                # chan = '101,103:105,112'
                # chanlist should result as:
                # [101, 103, 104, 105, 112]
                strlist = list(map(str, temp[0:None].split(',')))
                chanrange = []
                chanlist = []
                for i in range(len(strlist)):
                    chanrange.append(list(map(int,
                                              strlist[i][0:None].split(':'))))
                for i in range(len(chanrange)):
                    if len(chanrange[i]) == 2:
                        chanlist.append(list(range(chanrange[i][0],
                                                   chanrange[i][1] + 1)))
                    else:
                        chanlist.append(chanrange[i])
                # got them all, now flatten!
                chanlist = list(item for iter_ in chanlist for item in iter_)
            elif '@' in temp:
                start = temp.find('@')
                chanlist = list(map(int, temp[start+1:-1].split(',')))
            else:
                chanlist = list(map(int, temp[0:None].split(',')))
        else:  # must be an int
            chanstr = f"{chan}"
            chanlist = [chan]
        return chanstr, chanlist

    def set_scan_list(self, chan, relaytime: bool = False, **kwargs) -> None:
        """set_scan_list(chan)
        sets the list of channels to scan, the meter will scan them once
        immediately!
        Aguments:
            chan (int)[list]: list of channels to include in new
            scan list.  Note that scan list is overwritten every time
            relaytime (bool): ch_change_time delay before return.
        returns:
            None
        """
        # need either a string or a list to iterate for channels to setup
        chanstr, self.scanlist = self.format_channel_list(chan)

        # self.scanlist = ",".join(map(str, chan))  # old way
        self.write_resource(f'ROUT:SCAN (@{chanstr})', **kwargs)
        if relaytime:
            self.relay_delay(n=len(self.scanlist))

    def measure(self, chan, **kwargs):
        """
        measure(chan)
        performs an immediate sweep of the given scan_list and
        returns the data to the output buffer directly

        Aguments:
            chan (int)[list]: list of channels to include in new
            scan list.  Note that scan list is overwritten every time

        Returns:
            float or list (float): channel measurement(s)
        """
        chanstr, chanlist = self.format_channel_list(chan)
        response = self.query_resource(f'MEASure? (@{chanstr})', **kwargs)
        # start = response.find('\'')
        try:
            # response = list(map(float, response[start+1:].split(',')))
            response = self.resp_format(response, float)
        except ValueError:  # usually when that channel can't do that!
            print(f"channel {chanstr} unable! Return 0.0")
            print(f"{self.query_resource('SYSTem:ERRor?')}", **kwargs)
            return float(0)

        return response

    def read(self, chan=None, **kwargs):
        """
        measure(chan)
        performs an immediate sweep of the scan_list and
        returns the data to the output buffer directly

        Aguments:
            chan (int)[list]: optional list of channels to include in new
            scan list.  Note that scan list is overwritten every time
            If not passed in, uses existing list (recommended)

        Returns:
            list (float): channel measurements
        """
        if chan is not None:
            chanstr, chanlist = self.format_channel_list(chan)
            response = self.query_resource(f'READ? (@{chanstr})', **kwargs)
        else:
            response = self.query_resource('READ?', **kwargs)
        # start = response.find('@')
        # response = list(map(int, response[start+1:-1].split(',')))
        return self.resp_format(response, float)

    def init(self, **kwargs) -> None:
        """
        Initialize the meter, used with BUS trigger typically
        Use fetch_data (FETCh) to get the data.
        Returns:
            None
        """
        self.write_resource('INITiate', **kwargs)

    def fetch_data(self, **kwargs) -> float:
        """
        fetch_data

        Returns:
            [list, float]: data in meter memory resulting from all scans
        """

        response = self.query_resource('FETC?', **kwargs)
        return self.resp_format(response, float)

    def config_chan(self, chan, mode='volt', acdc='dc',
                    signal_range='auto', resolution=None,
                    nplc=0.02, **kwargs):
        """config_chan(#)

        Args:
            chan (int or str or list): channel number or list to apply
                                       common settings to
            example: chan=101, applies to channel 101 only.
            example: chan='202:207,209,302:308' --> channels 02 through 07
            and 09 on the module in slot 200 and channels 02 through 08 on
            the module in slot 300.
            example: chan=[102,104,205,301]...
            mode (str, optional): meter mode. Defaults to 'volt'.
            acdc (str, optional): ac or dc measurement setting.
                                  Defaults to 'dc'.
            signal_range (str, optional): measurement range. Defaults to 'auto'
            resolution (str, optional): 4.5, 5.5 or 6.5, if None uses nplc
                                        nplc is recommended because script
                                        timing is more deterministic.
                                        Defaults to None.
            nplc (float, optional): power line cycles to average.
                                    Defaults to 0.02.
        Kwargs:
            verbose (bool, optional): Whether or not the command message sent
                to the device is also printed to stdio.out, for debugging
                purposes. Defaults to False.
        """

        valid_acdc = {'DC': ':DC',
                      'AC': ':AC'}

        chanstr, chanlist = self.format_channel_list(chan)

        mode = str(mode).upper()
        if mode not in self.valid_modes:
            raise ValueError("Invalid mode option")
        mode = self.valid_modes[mode]

        usefreq = mode == self.valid_modes['FREQ']
        usecurrent = mode == self.valid_modes['CURR']
        useres = mode == self.valid_modes['RES']

        acdc = str(acdc).upper()
        if not (acdc in valid_acdc):
            raise ValueError("Invalid acdc option")
        acdc = valid_acdc[acdc] if not usefreq else ''

        # if range is not provided, cannot use nplc in CONF command
        signal_range = str(signal_range).upper()
        if signal_range == 'AUTO':
            signal_range = False

        try:
            if usecurrent and signal_range not in self.valid_cranges:
                raise ValueError('Invalid Current Range option')
            elif useres and signal_range not in self.valid_Rranges:
                raise ValueError('Invalid Resistance Range option')
            elif signal_range not in self.valid_ranges:
                raise ValueError('Invalid Range option')

        except ValueError:
            if kwargs.get('verbose', False):
                print("signal_range not in list, using max")
            signal_range = 'MAX'  # same as MAX for current

        nplc = str(nplc).upper()
        if not (nplc in self.nplc):
            raise ValueError("Invalid nplc option")
        nplc = nplc if not usefreq else ''

        cmds = []
        if resolution and signal_range:
            cmds.append(f"CONF:{mode}{acdc} {signal_range},{resolution}"
                        f"(@{chanstr})")
        else:
            if signal_range:
                cmds.append(f"CONF:{mode}{acdc} {signal_range}(@{chanstr})")
            else:
                cmds.append(f"CONF:{mode}{acdc} (@{chanstr})")

            if (resolution or nplc) and (not usefreq):
                for i in range(len(chanlist)):
                    cmds.append(f"SENS:{mode}{acdc}"
                                f"{':RES ' if resolution else ':NPLC '}"
                                f"{resolution if resolution else nplc}"
                                f"(@{chanlist[i]})")

        for cmd_str in cmds:
            if kwargs.get('verbose', False):
                print(cmd_str)
            self.write_resource(cmd_str, **kwargs)

    def close_chan(self, chan, **kwargs):
        """Close relay on channel #
        Args:
            chan (int): Channel to close
        """
        if isinstance(chan, int):
            self.write_resource(f"ROUT:CLOS (@{chan})", **kwargs)
        else:
            chanstr, chanlist = self.format_channel_list(chan)
            chanstr, chanlist = self.format_channel_list(chanlist[0])
            if kwargs.get('verbose', False):
                print(f"unable to close multiple channels, closing: "
                      f"{chanlist[0]}")
            self.write_resource(f"ROUT:CLOS (@{chanstr})", **kwargs)
        return

    def open_chan(self, chan, **kwargs) -> None:
        """
        Open relay on channel #

        Args:
            chan (int): Channel to Open
        """
        self.write_resource(f"ROUT:OPEN (@{chan})", **kwargs)

    def relay_delay(self, n: int = 1, ch_change_time=0.05) -> None:
        """relay_delay(n)
        relays need time to switch, this provides that time.

        Args:
            n (int, optional): number of relay delay periods. Defaults to 1.
            ch_change_time (float, optional): relay switching time, defaults to
                                             0.050 seconds
        """
        if self.ch_change_time != ch_change_time:
            self.ch_change_time = ch_change_time
        sleep(n * self.ch_change_time)

    def monitor(self, chan: int = None, verbose: bool = False, **kwargs):
        """
        monitor(chan)
        sets the mux to monitor the chan given and reads in realtime

        Aguments:
            chan (int)[list]:  channel to monitor in realtime. optional
                               if chan=None, returns the actively monitored
                               channel

        Returns:
            chan (int):  channel being monitored
        """
        if chan is None:
            chanstr, chanlist = self.format_channel_list(
                self.write_resource("ROUT:MON?", **kwargs))
        elif isinstance(chan, int):
            chanstr, chanlist = self.format_channel_list(chan)
            self.write_resource(f"ROUT:MON (@{chanstr})", **kwargs)
        else:
            chanstr, chanlist = self.format_channel_list(chan)
            chanstr, chanlist = self.format_channel_list(chanlist[0])
            if verbose:
                print(f"unable to close multiple channels, closing: "
                      f"{chanlist[0]}")
            self.write_resource(f'ROUT:MON (@{chanstr})', **kwargs)
        return chanlist[0]

    def mon_data(self, chan: int = None, **kwargs):
        """
        mon_data(chan)
        sets the mux to monitor the optional chan given and reads in realtime
        if chan is not provided it only gets the data (faster)

        Aguments:
            ch (int):  optional channel to monitor in realtime

        Returns:
            float: chan data
        """
        if chan is not None:
            chanstr, chanlist = self.format_channel_list(chan)
            self.write_resource(f'ROUT:MON (@{chanstr})', **kwargs)
            self.relay_delay()
        try:
            response = self.query_resource('ROUT:MON:DATA?', **kwargs)
        except IOError:  # usually when channel not configured
            print(f"channel {chanstr} not configured?? Return 0.0")
            print(f"{self.query_resource('SYSTem:ERRor?')}", **kwargs)
            return float(0)
        return self.resp_format(response, float)

    def measure_voltage(self, chan, **kwargs):
        """
        measure_voltage(chan)

        returns float, measurement in Volts DC from channel

        Measure the voltage present at the DC voltage measurement terminals.
        If the meter is not configured to measure DC voltage this will raise an
        exception. This can be remedied by setting the meaurement mode with the
        set_mode method.

        """
        chanstr, chanlist = self.format_channel_list(chan)
        if self.get_mode(chanstr) != 'VOLT':
            raise IOError("dac is not configured to measure voltage")
        else:
            response = self.query_resource(f"MEAS:VOLT:DC? (@{chanstr})",
                                           **kwargs)
            return self.resp_format(response, float)

    def measure_voltage_rms(self, chan, **kwargs):
        """
        measure_voltage_rms()

        returns float, measurement in Volts rms

        Measure the voltage present at the AC voltage measurement terminals.
        If the meter is not configured to measure AC voltage this will raise an
        exception. This can be remedied by setting the meaurement mode with the
        set_mode method.

        """
        chanstr, chanlist = self.format_channel_list(chan)
        if self.get_mode(chanstr) != 'VOLT:AC':
            raise IOError("dac is not configured to measure AC voltage")
        else:
            response = self.query_resource(f"MEAS:VOLT:AC? (@{chanstr})",
                                           **kwargs)
            return self.resp_format(response, float)

    def measure_current(self, chan, **kwargs):
        """
        measure_current()

        returns float, measurement in Amperes DC

        Measure the current present through the DC current measurement
        terminals. If the meter is not configured to measure DC current this
        will raise an exception. This can be remedied by setting the meaurement
        mode with the set_mode method.

        """
        chanstr, chanlist = self.format_channel_list(chan)
        if self.get_mode(chanstr) != 'CURR':
            raise IOError("dac is not configured to measure current")
        else:
            response = self.query_resource(f"MEAS:CURR:DC? (@{chanstr})",
                                           **kwargs)
            return self.resp_format(response, float)

    def measure_current_rms(self, chan, **kwargs):
        """
        measure_current_rms()

        returns float, measurement in Amperes rms

        Measure the current present through the AC current measurement
        terminals. If the meter is not configured to measure AC current this
        will raise an exception. This can be remedied by setting the meaurement
        mode with the set_mode method.

        """
        chanstr, chanlist = self.format_channel_list(chan)
        if self.get_mode(chanstr) != 'CURR:AC':
            raise IOError("dac is not configured to measure AC current")
        else:
            response = self.query_resource(f"MEAS:CURR:AC? (@{chanstr})",
                                           **kwargs)
            return self.resp_format(response, float)

    def measure_resistance(self, chan, **kwargs):
        """
        measure_resistance()

        returns float, measurement in Ohms

        Measure the resistance present at the resistance measurement terminals.
        If the meter is not configured to measure resistance this will raise an
        exception. This can be remedied by setting the meaurement mode with the
        set_mode method.

        """
        chanstr, chanlist = self.format_channel_list(chan)
        if self.get_mode(chanstr) != 'RES':
            raise IOError("dac is not configured to measure resistance")
        else:
            response = self.query_resource(f"MEAS:RES? (@{chanstr})", **kwargs)
            return self.resp_format(response, float)

    def measure_frequency(self, chan, **kwargs):
        """
        measure_frequency()

        returns float, measurement in Hertz

        Measure the frequency present at the frequency measurement terminals.
        If the meter is not configured to measure frequency this will raise an
        exception. This can be remedied by setting the meaurement mode with the
        set_mode method.

        """
        chanstr, chanlist = self.format_channel_list(chan)
        if self.get_mode(chanstr) != 'FREQ':
            raise IOError("dac is not configured to measure frequency")
        else:
            response = self.query_resource(f"MEAS:FREQ? (@{chanstr})",
                                           **kwargs)
            return self.resp_format(response, float)

    def abort(self, **kwargs) -> None:
        """
        abort()

        Send VISA ABORt, stop the scan!!
        Returns:
            None
        """

        self.write_resource('ABORt', **kwargs)

    def set_source(self, chan, voltage: float = None, **kwargs):
        """set_source(chan, voltage)

        Args:
            chan (int, list): Channels to set voltage output on
            voltage (float, optional): Voltage to command from DAC.
                                       Defaults to None.

        Returns:
            [list of float or float]: Voltage now output
        """
        chanstr, chanlist = self.format_channel_list(chan)
        if voltage is None:
            return self.get_source(chan, **kwargs)
        else:
            self.write_resource(f"SOUR:VOLT {voltage},(@{chanstr})", **kwargs)
            return voltage

    def get_source(self, chan, **kwargs):
        """get_source(chan)

        Args:
            chan (int, list): Channels to set voltage output on

        Returns:
            [list of float or float]: Voltage now output
        """
        chanstr, chanlist = self.format_channel_list(chan)
        response = self.query_resource(f"SOUR:VOLT? (@{chanstr})", **kwargs)
        return self.resp_format(response, float)

    def set_measure_time(self, measure_time: float = None):
        if measure_time is None:
            self.measure_time = (len(self.scanlist) * self.nplc_default *
                                 (1 / self.line_frequency) +
                                 self.ch_change_time)
        else:
            self.measure_time = measure_time
        return self.measure_time

    def set_local(self, **kwargs) -> None:
        self.write_resource("SYSTem:LOCal", **kwargs)


if __name__ == '__main__':
    pass

    # Agilent 34970A/72A Command Reference
    # Keysight 34970A/34972A
    # Table of contents
    # Keysight 34970A/72A Command Reference
    # Command Language Introduction
    # Syntax Conventions
    # Command Separators
    # Querying Parameter Settings
    # Command Terminators
    # IEEE-488.2 Common Commands
    # Parameter Types
    # Using Device Clear
    # LAN Port Usage
    # Commands by Subsystem
    # ABORt
    # FETCh?
    # INITiate
    # INPut:IMPedance:AUTO
    # R?
    # READ?
    # UNIT:TEMPerature
    # CALCulate_Subsystem
    # CALCulate:AVERage:AVERage?
    # CALCulate:AVERage:CLEar
    # CALCulate:AVERage:COUNt?
    # CALCulate:AVERage:MAXimum?
    # CALCulate:AVERage:MAXimum:TIME?
    # CALCulate:AVERage:MINimum?
    # CALCulate:AVERage:MINimum:TIME?
    # CALCulate:AVERage:PTPeak?
    # CALCulate:COMPare:DATA
    # CALCulate:COMPare:MASK
    # CALCulate:COMPare:STATe
    # CALCulate:COMPare:TYPE
    # CALCulate:LIMit:LOWer
    # CALCulate:LIMit:LOWer:STATe
    # CALCulate:LIMit:UPPer
    # CALCulate:LIMit:UPPer:STATe
    # CALCulate:SCALe:GAIN
    # CALCulate:SCALe:OFFSet
    # CALCulate:SCALe:OFFSet:NULL
    # CALCulate:SCALe:STATe
    # CALCulate:SCALe:UNIT
    # CALibration_Subsystem
    # CALibration?
    # CALibration:COUNt?
    # CALibration:SECure:CODE
    # CALibration:SECure:STATe
    # CALibration:STRing
    # CALibration:VALue
    # CONFigure_Subsystem
    # CONFigure?
    # CONFigure:CURRent:AC
    # CONFigure:CURRent:DC
    # CONFigure:DIGital:BYTE
    # CONFigure:FREQuency
    # CONFigure:FRESistance
    # CONFigure:PERiod
    # CONFigure:RESistance
    # CONFigure:TEMPerature
    # CONFigure:TOTalize
    # CONFigure:VOLTage:AC
    # CONFigure:VOLTage:DC
    # DATA_Subsystem
    # DATA:LAST?
    # DATA:POINts?
    # DATA:POINts:EVENt:THReshold
    # DATA:REMove?
    # DIAGnostic_Subsystem
    # DIAGnostic:DMM:CYCLes?
    # DIAGnostic:DMM:CYCLes:CLEar
    # DIAGnostic:PEEK:SLOT:DATA?
    # DIAGnostic:POKE:SLOT:DATA
    # DIAGnostic:RELay:CYCLes?
    # DIAGnostic:RELay:CYCLes:CLEar
    # DISPlay_Subsystem
    # DISPlay
    # DISPlay:TEXT
    # DISPlay:TEXT:CLEar
    # FORMat_Subsystem
    # FORMat:READing:ALARm
    # FORMat:READing:CHANnel
    # FORMat:READing:TIME
    # FORMat:READing:TIME:TYPE
    # FORMat:READing:UNIT
    # IEEE-488_Commands
    # *CLS
    # *ESE
    # *ESR?
    # *IDN?
    # *OPC
    # *OPC?
    # *PSC
    # *RCL
    # *RST
    # *SAV
    # *SRE
    # *STB?
    # *TRG
    # *TST?
    # *WAI
    # INSTrument_Subsystem
    # INSTrument:DMM
    # INSTrument:DMM:INSTalled?
    # LXI_Subsystem
    # LXI:IDENtify[:STATe]
    # LXI:RESet
    # LXI:RESTart
    # MEASure_Subsystem
    # MEASure:CURRent:AC?
    # MEASure:CURRent:DC?
    # MEASure:DIGital:BYTE?
    # MEASure:FREQuency?
    # MEASure:FRESistance?
    # MEASure:PERiod?
    # MEASure:RESistance?
    # MEASure:TEMPerature?
    # MEASure:TOTalize?
    # MEASure:VOLTage:AC?
    # MEASure:VOLTage:DC?
    # MEMory_Subsystem
    # MEMory:NSTates?
    # MEMory:STATe:DELete
    # MEMory:STATe:NAME
    # MEMory:STATe:RECall:AUTO
    # MEMory:STATe:VALid?
    # MMEMory_Subsytem
    # MMEMory:EXPort?
    # MMEMory:FORMat:READing:CSEParator
    # MMEMory:FORMat:READing:RLIMit
    # MMEMory:IMPort:CATalog?
    # MMEMory:IMPort:CONFig?
    # MMEMory:LOG[:ENABle]
    # OUTPut_Subsystem
    # OUTPut:ALARm:CLEar:ALL
    # OUTPut:ALARm:MODE
    # OUTPut:ALARm:SLOPe
    # OUTPut:ALARm{1|2|3|4}:CLEar
    # OUTPut:ALARm{1|2|3|4}:SOURce
    # ROUTe_Subsystem
    # ROUTe:CHANnel:ADVance:SOURce
    # ROUTe:CHANnel:DELay
    # ROUTe:CHANnel:DELay:AUTO
    # ROUTe:CHANnel:FWIRe
    # ROUTe:CLOSe
    # ROUTe:CLOSe:EXCLusive
    # ROUTe:DONE?
    # ROUTe:MONItor
    # ROUTe:MONItor:DATA?
    # ROUTe:MONItor:STATe
    # ROUTe:OPEN
    # ROUTe:SCAN
    # ROUTe:SCAN:SIZE?
    # SENSe_Subsystem
    # [SENSe:]CURRent:AC:BANDwidth
    # [SENSe:]CURRent:AC:RANGe
    # [SENSe:]CURRent:AC:RANGe:AUTO
    # [SENSe:]CURRent:AC:RESolution
    # [SENSe:]CURRent:DC:APERture
    # [SENSe:]CURRent:DC:NPLC
    # [SENSe:]CURRent:DC:RANGe
    # [SENSe:]CURRent:DC:RANGe:AUTO
    # [SENSe:]CURRent:DC:RESolution
    # [SENSe:]DIGital:DATA:{BYTE|WORD}?
    # [SENSe:]FREQuency:APERture
    # [SENSe:]FREQuency:RANGe:LOWer
    # [SENSe:]FREQuency:VOLTage:RANGe
    # [SENSe:]FREQuency:VOLTage:RANGe:AUTO
    # [SENSe:]FRESistance:APERture
    # [SENSe:]FRESistance:NPLC
    # [SENSe:]FRESistance:OCOMpensated
    # [SENSe:]FRESistance:RANGe
    # [SENSe:]FRESistance:RANGe:AUTO
    # [SENSe:]FRESistance:RESolution
    # [SENSe:]FUNCtion
    # [SENSe:]PERiod:APERture
    # [SENSe:]PERiod:VOLTage:RANGe
    # [SENSe:]PERiod:VOLTage:RANGe:AUTO
    # [SENSe:]RESistance:APERture
    # [SENSe:]RESistance:NPLC
    # [SENSe:]RESistance:OCOMpensated
    # [SENSe:]RESistance:RANGe
    # [SENSe:]RESistance:RANGe:AUTO
    # [SENSe:]RESistance:RESolution
    # [SENSe:]TEMPerature:APERture
    # [SENSe:]TEMPerature:NPLC
    # [SENSe:]TEMPerature:RJUNction?
    # [SENSe:]TEMPerature:TRANsducer:FRTD:OCOMpensated
    # [SENSe:]TEMPerature:TRANsducer:FRTD:RESistance[:REFerence]
    # [SENSe:]TEMPerature:TRANsducer:FRTD:TYPE
    # [SENSe:]TEMPerature:TRANsducer:RTD:OCOMpensated
    # [SENSe:]TEMPerature:TRANsducer:RTD:RESistance[:REFerence]
    # [SENSe:]TEMPerature:TRANsducer:RTD:TYPE
    # [SENSe:]TEMPerature:TRANsducer:TCouple:CHECk
    # [SENSe:]TEMPerature:TRANsducer:TCouple:RJUNction
    # [SENSe:]TEMPerature:TRANsducer:TCouple:RJUNction:TYPE
    # [SENSe:]TEMPerature:TRANsducer:TCouple:TYPE
    # [SENSe:]TEMPerature:TRANsducer:THERmistor:TYPE
    # [SENSe:]TEMPerature:TRANsducer:TYPE
    # [SENSe:]TOTalize:CLEar:IMMediate
    # [SENSe:]TOTalize:DATA?
    # [SENSe:]TOTalize:SLOPe
    # [SENSe:]TOTalize:STARt[:IMMediate]
    # [SENSe:]TOTalize:STOP[:IMMediate]
    # [SENSe:]TOTalize:TYPE
    # [SENSe:]VOLTage:AC:BANDwidth
    # [SENSe:]VOLTage:AC:RANGe
    # [SENSe:]VOLTage:AC:RANGe:AUTO
    # [SENSe:]VOLTage:DC:APERture
    # [SENSe:]VOLTage:DC:NPLC
    # [SENSe:]VOLTage:DC:RANGe
    # [SENSe:]VOLTage:DC:RANGe:AUTO
    # [SENSe:]VOLTage:DC:RESolution
    # [SENSe:]ZERO:AUTO
    # SOURce_Subsystem
    # SOURce:DIGital:DATA[:{BYTE|WORD}]
    # SOURce:DIGital:STATe?
    # SOURce:VOLTage
    # STATus_Subsystem
    # STATus:ALARm:CONDition?
    # STATus:ALARm:ENABle
    # STATus:ALARm[:EVENt]?
    # STATus:OPERation:CONDition?
    # STATus:OPERation:ENABle
    # STATus:OPERation[:EVENt]?
    # STATus:PRESet
    # STATus:QUEStionable:CONDition?
    # STATus:QUEStionable:ENABle
    # STATus:QUEStionable[:EVENt]?
    # STATus Subsystem Introduction
    # SYSTem_Subsystem
    # LAN_Config
    # SYSTem:COMMunicate:LAN:CONTrol?
    # SYSTem:COMMunicate:LAN:DHCP
    # SYSTem:COMMunicate:LAN:DNS
    # SYSTem:COMMunicate:LAN:DOMain
    # SYSTem:COMMunicate:LAN:GATEway
    # SYSTem:COMMunicate:LAN:HOSTname
    # SYSTem:COMMunicate:LAN:IPADdress
    # SYSTem:COMMunicate:LAN:MAC?
    # SYSTem:COMMunicate:LAN:SMASk
    # SYSTem:COMMunicate:LAN:TELNet:PROMpt
    # SYSTem:COMMunicate:LAN:TELNet:WMESsage
    # SYSTem:COMMunicate:LAN:UPDate
    # SYSTem:ALARm?
    # SYSTem:CPON
    # SYSTem:CTYPe?
    # SYSTem:DATE
    # SYSTem:ERRor?
    # SYSTem:INTerface
    # SYSTem:LANGuage
    # SYSTem:LFRequency?
    # SYSTem:LOCal
    # SYSTem:LOCK:NAME?
    # SYSTem:LOCK:OWNer?
    # SYSTem:LOCK:RELease
    # SYSTem:LOCK:REQuest?
    # SYSTem:PRESet
    # SYSTem:RWLock
    # SYSTem:SECurity[:IMMediate]
    # SYSTem:TIME
    # SYSTem:TIME:SCAN?
    # SYSTem:VERSion?
    # TRIGger_Subsystem
    # TRIGger:COUNt
    # TRIGger:SOURce
    # TRIGger:TIMer
    # Commands A-Z
    # Command Quick Reference
    # Error Messages
    # Factory Reset State
    # Instrument Preset State
    # Plug-in Module Reference Information
    # 34901A Module
    # 34902A Module
    # 34903A Module
    # 34904A Module Summary
    # 34905A/34906A Modules
    # 34907A Module
    # 34908A Module
