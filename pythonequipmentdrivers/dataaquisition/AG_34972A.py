from pythonequipmentdrivers import Scpi_Instrument as _Scpi_Instrument
import time


class AG_34972A(_Scpi_Instrument):
    """
    AG_34972A()

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

    def __init__(self, address, **kwargs):
        super().__init__(address)
        self.ch_change_time = kwargs.get('ch_change_time', float(0.050))
        self.modes = {'VOLT': 'VOLT',
                      'CURR': 'CURR',
                      'V': 'VOLT',
                      'A': 'CURR',
                      'FREQ': 'FREQ',
                      'F': 'FREQ',
                      'OHMS': 'RES',
                      'O': 'RES',
                      'DIOD': 'DIOD',
                      'D': 'DIOD',
                      'DIODE': 'DIOD',
                      'CONT': 'CONT',
                      'C': 'CONT',
                      'PER': 'PER',
                      'P': 'PER'
                      }
        self.acdc = {'DC': 'DC',
                     'AC': 'AC'}
        self.signal_ranges = {'AUTO': '',
                              'MIN': 'MIN,',
                              'MAX': 'MAX,',
                              'DEF': 'DEF,',
                              0.1: '0.1,',
                              1: '1,',
                              10: '10,',
                              100: '100,',
                              300: '300,'}
        self.nplc = {'0.02': '0.02,',
                     '0.2': '0.2,',
                     '1': '1,',
                     '2': '2,',
                     '10': '10,',
                     '20': '20,',
                     '100': '100,',
                     '200': '200,',
                     'MIN': 'MIN,',
                     'MAX': 'MAX,',
                     0.02: '0.02,',
                     0.2: '0.2,',
                     1: '1,',
                     2: '2,',
                     10: '10,',
                     20: '20,',
                     100: '100,',
                     200: '200,'}
        self.trigger = {'BUS': 'BUS',
                        'IMMEDIATE': 'IMMediate',
                        'EXTERNAL': 'EXTernal',
                        'ALARM1': 'ALARm1',
                        'ALARM2': 'ALARm2',
                        'ALARM3': 'ALARm3',
                        'ALARM4': 'ALARm4',
                        'TIMER': 'TIMer'}
        return None

    def resp_format(self, response, type: type = int):
        response = response.strip()
        start = response.find('@')
        response = list(map(type, response[start+1:-1].split(',')))
        if len(response) == 1:
            return response[0]
        return response

    def set_mode(self, mode):
        """
        set_mode(mode)

        mode: str, type of measurement to be done
            valid modes are: 'VDC', 'VAC', 'ADC', 'AAC', 'FREQ', 'OHMS',
                             'DIOD', 'CONT', 'PER'
            which correspond to DC voltage, AC voltage, DC current, AC current,
            frequency, resistence, diode voltage, continuity, and period
            respectively (not case sensitive)

        Configures the dac to perform the specified measurement
        """

        mode = mode.upper()
        if mode in self.modes:
            self.instrument.write(f"CONF:{self.modes[mode]}")
        else:
            raise ValueError("Invalid mode option")
        return

    def get_mode(self):
        """
        get_mode()

        retrives type of measurement the dac is current configured to
        perform.

        returns: str
        """
        response = self.instrument.query("FUNC?")
        response = response.rstrip().replace('"', '')
        return response

    def set_trigger(self, trigger):
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
            self.instrument.write(f"TRIG:{self.valid_trigger[trigger]}")
        else:
            raise ValueError("Invalid trigger option")
        return

    def get_scan_list(self):
        """
        get_scan_list()

        determine which channels are currently in the scan list,
        you can send the ROUTe:SCAN? query command.
        instrument data comes back raw such as: '#210(@101,102)\n'

        returns:
            list (int): channel numbers in scanlist
        """
        response = self.instrument.query("ROUT:SCAN?")
        response = response.strip()
        start = response.find('@')
        self.scanlist = list(map(int, response[start+1:-1].split(',')))
        return self.scanlist

    def set_scan_list(self, ch):
        """
        set_scan_list(ch)

        Aguments:
            ch (int)[list]: list of channels to include in new
            scan list.  Note that scan list is overwritten every time

        returns:
            None
        """
        self.scanlist = ",".join(map(str, ch))
        self.instrument.write(f'ROUT:SCAN (@{self.scanlist})')
        return None

    def measure(self, ch):
        """
        measure(ch)
        performs an immediate sweep of the given scan_list and
        returns the data to the output buffer directly

        Aguments:
            ch (int)[list]: list of channels to include in new
            scan list.  Note that scan list is overwritten every time

        Returns:
            list (float): channel measurements
        """
        scanlist = ",".join(map(str, ch))
        response = self.instrument.query(f'MEASure? (@{scanlist})')
        # response = response.strip()
        # start = response.find('@')
        # response = list(map(int, response[start+1:-1].split(',')))
        return self.resp_format(response, type=float)

    def read(self, ch: None):
        """
        measure(ch)
        performs an immediate sweep of the scan_list and
        returns the data to the output buffer directly

        Aguments:
            ch (int)[list]: optional list of channels to include in new
            scan list.  Note that scan list is overwritten every time
            If not passed in, uses existing list (recommended)

        Returns:
            list (float): channel measurements
        """
        if ch is not None:
            scanlist = ",".join(map(str, ch))
            response = self.instrument.query(f'READ? (@{scanlist})')
        else:
            response = self.instrument.query('READ?')
        # response = response.strip()
        # start = response.find('@')
        # response = list(map(int, response[start+1:-1].split(',')))
        return self.resp_format(response, type=float)

    def initiate(self, ch: list = None):
        """
        measure(ch)
        performs an immediate sweep of the scan_list and
        returns the data to the internal memory
        Use FETCh to get the data.

        Aguments:
            ch (int)[list]: optional list of channels to include in new
            scan list.  Note that scan list is overwritten every time
            If not passed in, uses existing list (recommended)

        Returns:
            list (float): channel measurements
        """
        if ch is not None:
            scanlist = ",".join(map(str, ch))
            self.instrument.write(f'INITiate (@{scanlist})')
        else:
            self.instrument.write('INITiate')
        init_done = [int(0)]
        while init_done[0] == 0:
            status = self.instrument.query('*OPC?')
            statusint = list(map(int, status.split(',')))
            init_done[0] = 0x01 & statusint[0]
        response = self.instrument.query('FETCh?')
        # response = response.strip()
        # start = response.find('@')
        # response = list(map(int, response[start+1:-1].split(',')))
        return self.resp_format(response, type=float)

    def configure(self, mode: str = 'volt', acdc: str = 'dc',
                  signal_range: type = int,
                  ch: list = None):
        return

    def config_chan(self, chan, mode='volt', acdc='dc',
                    signal_range='auto', resolution=None,
                    nplc=0.02, **kwargs):
        """config_chan(#)

        Args:
            chan (int or str or list): channel number or list to apply
                                       settings to
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
        Raises:
            ValueError: if a parameter isn't allowed
        Returns:
            None
        """
        if isinstance(chan, list):
            chanstr = ",".join(map(str, chan))
            chanlist = chan
        elif isinstance(chan, str):
            temp = chan.strip()
            chanlist = list(map(int, temp[+1:-1].split(',')))
        else:
            chanlist = [chan]
        mode = mode.upper()
        if mode in self.modes:
            mode = self.modes[mode]
        else:
            raise ValueError("Invalid mode option")
            return

        acdc = acdc.upper()
        if acdc in self.acdc:
            acdc = self.acdc[acdc]
        else:
            raise ValueError("Invalid acdc option")
            return

        # if range is not provided, cannot use nplc
        if signal_range.upper() == 'AUTO':
            signal_range = False
        else:
            try:
                signal_range = signal_range.upper()
            except AttributeError:
                pass
            try:
                signal_range = self.signal_ranges[signal_range]
            except (ValueError, KeyError):
                if kwargs.get('verbose', False):
                    print("signal_range not in list, using max")
                signal_range = self.signal_ranges['MAX']

        try:
            nplc = nplc.upper()
        except AttributeError:
            pass
        if nplc in self.nplc:
            nplc = self.nplc[nplc]
        else:
            raise ValueError("Invalid nplc option")

        if resolution and signal_range:
            string = (f"CONF:{mode}"
                      f":{acdc} "
                      f"{signal_range}"
                      f"{resolution}"
                      f"(@{chanstr})")
            if kwargs.get('verbose', False):
                print(string)
            self.instrument.write(string)
        elif signal_range:
            string = (f"CONF:{mode}"
                      f":{acdc} "
                      f"{signal_range}"
                      f"{nplc}"
                      f"(@{chanstr})")
            if kwargs.get('verbose', False):
                print(string)
            self.instrument.write(string)
        else:
            for i in range(len(chanlist)):
                string = (f"CONF:{mode}"
                          f":{acdc} "
                          f"(@{chanlist[i]})")
                x = 'RES ' if resolution else 'NPLC '
                string2 = (f"SENS:{mode}"
                           f":{acdc}:"
                           f"{x}"
                           f"{resolution if resolution else nplc}"
                           f"(@{chanlist[i]})")
                if kwargs.get('verbose', False):
                    print(string)
                    print(string2)
                self.instrument.write(string)
                self.instrument.write(string2)

        if kwargs.get('verbose', False):
            print(string)
        self.instrument.write(string)

        return

    def close_chan(self, ch):
        """Close relay on channel #
        Args:
            ch (int): Channel to close
        """
        self.instrument.write(f"ROUT:CLOS (@{ch})")
        return

    def open_chan(self, ch):
        """Open relay on channel #
        Args:
            ch (int): Channel to Open
        """
        self.instrument.write(f"ROUT:OPEN (@{ch})")
        return

    def monitor(self, ch):
        """
        monitor(ch)
        sets the mux to monitor the ch given and reads in realtime

        Aguments:
            ch (int)[list]:  channel to monitor in realtime

        Returns:
            None
        """
        scanlist = str(ch)
        self.instrument.write(f'ROUT:MON (@{scanlist})')
        time.sleep(self.ch_change_time)
        return None

    def mon_data(self, ch: int = None):
        """
        mon_data(ch)
        sets the mux to monitor the optional ch given and reads in realtime
        if ch is not provided it only gets the data (faster)

        Aguments:
            ch (int):  optional channel to monitor in realtime

        Returns:
            float: ch data
        """
        if ch is not None:
            scanlist = str(ch)
            self.instrument.write(f'ROUT:MON (@{scanlist})')
            time.sleep(self.ch_change_time)
        response = self.instrument.query('ROUT:MON:DATA?')
        return self.resp_format(response, type=float)

    def measure_voltage(self):
        """
        measure_voltage()

        returns float, measurement in Volts DC

        Measure the voltage present at the DC voltage measurement terminals.
        If the meter is not configured to measure DC voltage this will raise an
        exception. This can be remedied by setting the meaurement mode with the
        set_mode method.

        """
        if self.get_mode() != 'VOLT':
            raise IOError("dac is not configured to measure voltage")
        else:
            response = self.instrument.query("MEAS:VOLT:DC?")
            return float(response)

    def measure_voltage_rms(self):
        """
        measure_voltage_rms()

        returns float, measurement in Volts rms

        Measure the voltage present at the AC voltage measurement terminals.
        If the meter is not configured to measure AC voltage this will raise an
        exception. This can be remedied by setting the meaurement mode with the
        set_mode method.

        """
        if self.get_mode() != 'VOLT:AC':
            raise IOError("dac is not configured to measure AC voltage")
        else:
            response = self.instrument.query("MEAS:VOLT:AC?")
            return float(response)

    def measure_current(self):
        """
        measure_current()

        returns float, measurement in Amperes DC

        Measure the current present through the DC current measurement
        terminals. If the meter is not configured to measure DC current this
        will raise an exception. This can be remedied by setting the meaurement
        mode with the set_mode method.

        """
        if self.get_mode() != 'CURR':
            raise IOError("dac is not configured to measure current")
        else:
            response = self.instrument.query("MEAS:CURR:DC?")
            return float(response)

    def measure_current_rms(self):
        """
        measure_current_rms()

        returns float, measurement in Amperes rms

        Measure the current present through the AC current measurement
        terminals. If the meter is not configured to measure AC current this
        will raise an exception. This can be remedied by setting the meaurement
        mode with the set_mode method.

        """
        if self.get_mode() != 'CURR:AC':
            raise IOError("dac is not configured to measure AC current")
        else:
            response = self.instrument.query("MEAS:CURR:AC?")
            return float(response)

    def measure_resistance(self):
        """
        measure_resistance()

        returns float, measurement in Ohms

        Measure the resistance present at the resistance measurement terminals.
        If the meter is not configured to measure resistance this will raise an
        exception. This can be remedied by setting the meaurement mode with the
        set_mode method.

        """
        if self.get_mode() != 'RES':
            raise IOError("dac is not configured to measure resistance")
        else:
            response = self.instrument.query("MEAS:RES?")
            return float(response)

    def measure_frequency(self):
        """
        measure_frequency()

        returns float, measurement in Hertz

        Measure the frequency present at the frequency measurement terminals.
        If the meter is not configured to measure frequency this will raise an
        exception. This can be remedied by setting the meaurement mode with the
        set_mode method.

        """
        if self.get_mode() != 'FREQ':
            raise IOError("dac is not configured to measure frequency")
        else:
            response = self.instrument.query("MEAS:FREQ?")
            return float(response)
