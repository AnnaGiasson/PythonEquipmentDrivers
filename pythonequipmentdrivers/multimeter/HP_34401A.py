from pythonequipmentdrivers import Scpi_Instrument
from time import sleep


class HP_34401A(Scpi_Instrument):
    """
    HP_34401A()

    address: str, address of the connected multimeter

    factor: float, multiplicitive scale for all measurements defaults to 1.

    object for accessing basic functionallity of the HP_34401A multimeter.
    The factor term allows for measurements to be multiplied by some number
    before being returned. For example, in the case of measuring the voltage
    across a current shunt this factor can represent the conductance of the
    shunt. This factor defaults to 1 (no effect on measurement).

    Additional Information:
    http://ecee.colorado.edu/~mathys/ecen1400/pdf/references/HP34401A_BenchtopMultimeter.pdf
    """

    valid_modes = {'VDC': "VOLT:DC",
                   'VOLT': 'VOLT',
                   'VAC': "VOLT:AC",
                   'ADC': "CURR:DC",
                   'AAC': "CURR:AC",
                   'CURR': 'CURR',
                   'V': 'VOLT',
                   'A': 'CURR',
                   'FREQ': "FREQ",
                   'F': 'FREQ',
                   'OHMS': "RES",
                   'O': 'RES',
                   'RES': 'RES',
                   'FRES': 'FRES',
                   'DIOD': "DIOD",
                   'D': 'DIOD',
                   'CONT': "CONT",
                   'PER': "PER",
                   'P': 'PER'}

    valid_ranges = {'AUTO', 'MIN', 'MAX', 'DEF',
                    '0.1', '1', '10', '100', '300'}

    valid_cranges = {'AUTO', 'MIN', 'MAX', 'DEF',
                     '0.01', '0.1', '1', '3'}

    valid_Rranges = {'AUTO', 'MIN', 'MAX', 'DEF',
                     '100', '1E3', '10E3', '100E3', '1E6', '10E6', '100E6'}

    nplc = {'0.02', '0.2', '1', '2', '10', '20', '100', '200', 'MIN', 'MAX'}

    valid_resolutions = {'0.02': 0.0001,  # lookup based on nplc
                         '0.2': 0.00001,  # this * range = resolution
                         '1': 0.000003,
                         '2': 0.0000022,
                         '10': 0.000001,
                         '20': 0.0000008,
                         '100': 0.0000003,
                         '200': 0.00000022,
                         'MIN': 0.0001,
                         'MAX': 0.00000022}

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

    def __init__(self, address: str, **kwargs) -> None:
        super().__init__(address, **kwargs)
        self.factor = kwargs.get('factor', 1.0)
        self.nplc_default = 1  # power line cycles to average
        self.line_frequency = kwargs.get('line_frequency', float(50))  # Hz
        self.sample_count = self.get_sample_count()
        self.measure_time = self.set_measure_time()
        self.trigger_mode = self.get_trigger_source()

    def __del__(self) -> None:
        self.set_local()
        super().__del__()

    def set_mode(self, mode: str) -> None:
        """
        set_mode(mode)

        mode: str, type of measurement to be done
            valid modes are: 'VDC', 'VAC', 'ADC', 'AAC', 'FREQ', 'OHMS',
                             'DIOD', 'CONT', 'PER'
            which correspond to DC voltage, AC voltage, DC current, AC current,
            frequency, resistence, diode voltage, continuity, and period
            respectively (not case sensitive)

        Configures the multimeter to perform the specified measurement
        """

        mode = str(mode).upper()
        if not (mode in self.valid_modes):
            raise ValueError("Invalid mode option")

        self.instrument.write(f"CONF:{self.valid_modes[mode]}")

    def get_mode(self) -> str:
        """
        get_mode()

        retrives type of measurement the multimeter is current configured to
        perform.

        returns: str
        """

        response = self.instrument.query("FUNC?")
        return response.rstrip().replace('"', '')

    def get_error(self, **kwargs) -> str:
        """
        get_error

        Returns:
            [list]: last error in the buffer
        """
        response = self.instrument.query('SYSTem:ERRor?', **kwargs)
        return self.resp_format(response, str)

    def set_trigger(self, trigger: str, **kwargs) -> None:
        """
        set_trigger(trigger)

        Configures the multimeter to trigger as specified
        The TRIGger subsystem configures the triggering that controls
        measurement acquisition.
        Recommendation: All triggered measurements should be made using an
        appropriate fixed manual range. That is, turn autorange off
        ([SENSe:]<function>:RANGe:AUTO OFF) or set a fixed range using the
        [SENSe:]<function>:RANGe, CONFigure, or MEASure command.

        trigger: str, type of trigger to be done
            valid modes are: 'BUS', 'IMMEDIATE', 'EXTERNAL'.
        """

        valid_delay = {'MIN', 'MINIMUM', 'MAX', 'MAXIMUM'}
        valid_count = {'MIN', 'MINIMUM', 'MAX', 'MAXIMUM', 'INF', 'INFINITE'}

        if kwargs.get('delay', False):

            if isinstance(kwargs['delay'], str):
                delay = kwargs['delay'].upper()
            else:
                delay = kwargs['delay']

            if not ((delay in valid_delay) or isinstance(delay, (int, float))):
                raise ValueError(f"Invalid trigger delay. Use: {valid_delay}")

            self.instrument.write(f"TRIG:DELay {delay}")

        if kwargs.get('count', False):

            if isinstance(kwargs['count'], str):
                count = kwargs['count'].upper()
            else:
                count = kwargs['count']

            if not ((count in valid_count) or isinstance(count, int)):
                # note: if count is not an int the 2nd condition wont execute
                if isinstance(count, int) and (1 <= count <= 50000):
                    pass
                else:
                    raise ValueError('Invalid trigger count.'
                                     f' Use: {valid_count} or an int within'
                                     ' the range [1, 50000]')

            self.instrument.write(f"TRIG:COUNt {count}")

        trigger = str(trigger).upper()
        if not (trigger in self.valid_trigger):
            raise ValueError("Invalid trigger option")
        self.instrument.write(f"TRIG:{self.valid_trigger[trigger]}")

    def set_trigger_source(self, trigger: str = 'IMMEDIATE', **kwargs) -> None:
        """
        set_trigger(trigger)

        Configures the multimeter to trigger as specified

        trigger: str, type of trigger to be done
            valid modes are: 'BUS', 'IMMEDIATE', 'EXTERNAL'.
        """

        trigger = str(trigger).upper()
        if trigger not in self.valid_trigger:
            raise ValueError("Invalid trigger option")

        self.trigger_mode = self.valid_trigger[trigger]
        self.instrument.write(f"TRIG:SOUR {self.trigger_mode}", **kwargs)

    def get_trigger_source(self, **kwargs) -> str:

        response = self.instrument.query("TRIG:SOUR?", **kwargs)
        fmt_resp = self.resp_format(response, str)

        self.trigger_mode = self.valid_trigger[fmt_resp]
        return self.trigger_mode

    def set_trigger_count(self, count: int, **kwargs) -> None:
        """
        set_trigger_count(count)

        Args:
            count (int): how many readings to take when triggered
        """
        valid_count = {'MIN', 'MINIMUM', 'MAX', 'MAXIMUM', 'INF', 'INFINITE'}

        count = count.upper() if isinstance(count, str) else count

        if not ((count in valid_count) or isinstance(count, int)):
            # note: if count is not an int the 2nd condition wont execute
            if isinstance(count, int) and (1 <= count <= 50000):
                pass
            else:
                raise ValueError('Invalid trigger count.'
                                 f' Use: {valid_count} or an int within'
                                 ' the range [1, 50000]')

        self.instrument.write(f"TRIG:COUNt {count}", **kwargs)

    def get_trigger_count(self, **kwargs) -> int:
        response = self.instrument.query("TRIG:COUN?", **kwargs)
        return int(self.resp_format(response, float))

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
            raise IOError("Multimeter is not configured to measure voltage")
        else:
            response = self.instrument.query("MEAS:VOLT:DC?")
            return self.factor*float(response)

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
            raise IOError("Multimeter is not configured to measure AC voltage")
        else:
            response = self.instrument.query("MEAS:VOLT:AC?")
            return self.factor*float(response)

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
            raise IOError("Multimeter is not configured to measure current")
        else:
            response = self.instrument.query("MEAS:CURR:DC?")
            return self.factor*float(response)

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
            raise IOError("Multimeter is not configured to measure AC current")
        else:
            response = self.instrument.query("MEAS:CURR:AC?")
            return self.factor*float(response)

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
            raise IOError("Multimeter is not configured to measure resistance")
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
            raise IOError("Multimeter is not configured to measure frequency")
        else:
            response = self.instrument.query("MEAS:FREQ?")
            return float(response)

    def init(self, **kwargs) -> None:
        """
        init(**kwargs)

        Initialize the meter, used with BUS trigger typically
        Use fetch_data (FETCh) to get the data.
        """

        self.instrument.write('INITiate', **kwargs)

    def fetch_data(self, **kwargs) -> float:
        """
        fetch_data(**kwargs)

        Returns:
            [list, float]: data in meter memory resulting from all scans
        """
        response = self.instrument.query('FETC?', **kwargs)
        return self.resp_format(response, float)

    def abort(self, **kwargs) -> None:
        """
        abort()

        Send VISA ABORt, stop the scan!!
        """
        self.instrument.write('ABORt', **kwargs)

    def trigger(self, wait: bool = True, **kwargs) -> None:
        """
        trigger(wait=True)

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
            self.instrument.write('*TRG', **kwargs)
        else:
            print(f"Trigger not configured, set as: {self.trigger_mode}"
                  f" should be {self.valid_trigger['BUS']}")

        if wait:
            sleep(self.measure_time)  # should work most of the time.
            # it should also wait nplc time per channel
            # need to make a function to track nplc time
            # if nplc is longer than 1, then this will fail, if shorter
            # then this will take way too long

    def set_sample_count(self, count: int, **kwargs) -> None:
        self.instrument.write(f"SAMP:COUN {int(count)}", **kwargs)

    def get_sample_count(self, **kwargs):
        response = self.instrument.query("SAMP:COUN?", **kwargs)
        self.sample_count = int(self.resp_format(response, float))
        return self.sample_count

    def config(self, mode='volt', acdc='dc',
               signal_range='auto', resolution=None,
               nplc=0.02, **kwargs) -> None:
        """config_chan(#)

        Args:
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

        mode = str(mode).upper()
        if mode not in self.valid_modes:
            raise ValueError("Invalid mode option")
        mode = self.valid_modes[mode]

        usefreq = (mode == self.valid_modes['FREQ'])
        usecurrent = (mode == self.valid_modes['CURR'])
        useres = (mode == self.valid_modes['RES'])

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
            cmds.append(f"CONF:{mode}{acdc} {signal_range},{resolution}")
        else:
            if signal_range:
                cmds.append(f"CONF:{mode}{acdc} {signal_range}")
            else:
                cmds.append(f"CONF:{mode}{acdc}")

            if (resolution or nplc) and (not usefreq):
                cmds.append(f"SENS:{mode}{acdc}"
                            f"{':RES ' if resolution else ':NPLC '}"
                            f"{resolution if resolution else nplc}")

        for cmd_str in cmds:
            if kwargs.get('verbose', False):
                print(cmd_str)
            self.instrument.write(cmd_str, **kwargs)

    def resp_format(self, response, resp_type: type = int):
        """resp_format(response(str data), type(int/float/etc))

        Args:
            response (str): string of data to parse
            type (type, optional): what type to output. Defaults to int.

        Returns:
            list[type], or type: return is a list if more than 1 element
                                 otherwise returns the single element as type
        """
        response = response.strip()
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

    def set_measure_time(self, measure_time: float = None):
        if measure_time is None:
            self.measure_time = (self.sample_count * self.nplc_default *
                                 (1 / self.line_frequency) + 0.01)
        else:
            self.measure_time = measure_time
        return self.measure_time

    def set_local(self, **kwargs) -> None:
        self.instrument.write("SYSTem:LOCal", **kwargs)
