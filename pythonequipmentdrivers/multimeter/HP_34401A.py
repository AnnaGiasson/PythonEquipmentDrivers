from pythonequipmentdrivers import Scpi_Instrument
import time


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

    def __init__(self, address, **kwargs):
        super().__init__(address, **kwargs)
        self.factor = kwargs.get('factor', 1.0)
        self.valid_modes = {'VDC': "VOLT:DC",
                            'VAC': "VOLT:AC",
                            'ADC': "CURR:DC",
                            'AAC': "CURR:AC",
                            'FREQ': "FREQ",
                            'OHMS': "RES",
                            'DIOD': "DIOD",
                            'CONT': "CONT",
                            'PER': "PER"}
        self.valid_trigger = {'BUS': 'BUS',
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
        self.nplc_default = 1  # power line cycles to average
        self.line_frequency = kwargs.get('line_frequency', float(50))  # Hz
        self.sample_count = self.get_sample_count()
        self.measure_time = self.set_measure_time()
        self.trigger_mode = self.get_trigger_source()
        return None

    def set_mode(self, mode):
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

        mode = mode.upper()
        if mode in self.valid_modes:
            self.instrument.write(f"CONF:{self.valid_modes[mode]}")
        else:
            raise ValueError("Invalid mode option")
        return None

    def get_mode(self):
        """
        get_mode()

        retrives type of measurement the multimeter is current configured to
        perform.

        returns: str
        """
        response = self.instrument.query("FUNC?")
        response = response.rstrip().replace('"', '')
        return response

    def set_trigger(self, trigger, **kwargs):
        """
        set_trigger(trigger)

        trigger: str, type of trigger to be done
            valid modes are: 'BUS', 'IMMEDIATE', 'EXTERNAL'
            which correspond to 'BUS', 'IMMEDIATE', 'EXTERNAL'
            respectively (not case sensitive)

        Configures the multimeter to trigger as specified
        The TRIGger subsystem configures the triggering that controls
        measurement acquisition.
        Recommendation: All triggered measurements should be made using an
        appropriate fixed manual range. That is, turn autorange off
        ([SENSe:]<function>:RANGe:AUTO OFF) or set a fixed range using the
        [SENSe:]<function>:RANGe, CONFigure, or MEASure command.

        """
        if 'delay' in kwargs:
            delay = kwargs['delay'].upper()
            self.instrument.write(f"TRIG:DELay {delay}")
        else:
            raise ValueError("Invalid trigger option")
        if 'count' in kwargs:
            count = kwargs['count'].upper()
            self.instrument.write(f"TRIG:COUNt {count}")
        else:
            raise ValueError("Invalid trigger option")
        if 'level' in kwargs:
            level = kwargs['level'].upper()
            self.instrument.write(f"TRIG:LEVel {level}")
        else:
            raise ValueError("Invalid trigger option")
        if 'slope' in kwargs:
            slope = kwargs['slope'].upper()
            self.instrument.write(f"TRIG:SLOPe {slope}")
        else:
            raise ValueError("Invalid trigger option")

        trigger = trigger.upper()
        if trigger in self.valid_trigger:
            self.instrument.write(f"TRIG:{self.valid_trigger[trigger]}")
        else:
            raise ValueError("Invalid trigger option")

        return

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
            self.instrument.write(f"TRIG:SOUR {self.trigger_mode}", **kwargs)
        else:
            raise ValueError("Invalid trigger option")
        return

    def get_trigger_source(self, **kwargs):
        self.trigger_mode = self.valid_trigger[self.resp_format(
            self.instrument.query("TRIG:SOUR?", **kwargs), str)]
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
            self.instrument.write(f"TRIG:COUN {count}", **kwargs)
        else:
            raise ValueError("Invalid trigger count number type, use int")
        return

    def get_trigger_count(self, **kwargs):
        return int(self.resp_format(self.instrument.query(f"TRIG:COUN?",
                                                          **kwargs), float))

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

    def init(self, **kwargs):
        """
        Initialize the meter, used with BUS trigger typically
        Use fetch_data (FETCh) to get the data.
        Returns:
            None
        """
        self.instrument.write('INITiate', **kwargs)
        return None

    def cls(self, **kwargs):
        """cls()
        Send VISA *CLS, clear visa bus
        Returns:
            None
        """
        self.instrument.write('*CLS', **kwargs)
        return None

    def abort(self, **kwargs):
        """abort()
        Send VISA ABORt, stop the scan!!
        Returns:
            None
        """
        self.instrument.write('ABORt', **kwargs)
        return None

    def rst(self, **kwargs):
        """rst()
        Send VISA *RST, reset the instrument
        Returns:
            None
        """
        self.instrument.write('*RST', **kwargs)
        return None

    def trigger(self, wait=True, **kwargs):
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
            self.instrument.write('*TRG', **kwargs)
        else:
            print(f"Trigger not configured, set as: {self.trigger_mode}"
                  f" should be {self.valid_trigger['BUS']}")
            pass
        if wait:
            time.sleep(self.measure_time)  # should work most of the time.
            # it should also wait nplc time per channel
            # need to make a function to track nplc time
            # if nplc is longer than 1, then this will fail, if shorter
            # then this will take way too long
        return None

    def set_sample_count(self, count: int = None, **kwargs):
        if count is None:
            return self.get_sample_count()
        else:
            self.instrument.write(f"SAMP:COUN {count}", **kwargs)
        return

    def get_sample_count(self, **kwargs):
        self.sample_count = int(self.resp_format(
            self.instrument.query("SAMP:COUN?", **kwargs), float))
        return self.sample_count

    def config(self, mode='volt', acdc='dc',
               signal_range='auto', resolution=None,
               nplc=0.02, verbose: bool = False, **kwargs):
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
        Raises:
            ValueError: if a parameter isn't allowed
        Returns:
            None
        """

        mode = mode.upper()
        if mode in self.valid_modes:
            mode = self.valid_modes[mode]
        else:
            raise ValueError("Invalid mode option")

        usefreq = mode == self.valid_modes['FREQ']
        acdc = acdc.upper()
        if usefreq:
            acdc = ''  # frequency doesn't use this
        elif acdc in self.acdc:
            acdc = self.acdc[acdc]
        else:
            raise ValueError("Invalid acdc option")

        # if range is not provided, cannot use nplc in CONF command
        if signal_range.upper() == 'AUTO':
            signal_range = False
        else:
            try:
                signal_range = signal_range.upper()
            except AttributeError:
                pass
            try:
                signal_range = self.valid_ranges[signal_range]
            except (ValueError, KeyError):
                if verbose:
                    print("signal_range not in list, using max")
                signal_range = self.valid_ranges['MAX']

        try:
            nplc = nplc.upper()
        except AttributeError:
            pass
        if nplc in self.nplc:
            nplc = self.nplc[nplc]
            if usefreq:
                # if resolution is not None:
                #     pass
                # else:
                #     # TypeError: can't multiply sequence by
                #     # non-int of type 'float'
                #     # didn't finish, had to abandon this special case due to
                #     # complexity and time constraints
                #     resolution = (self.valid_resolutions[nplc] *
                #                   signal_range if signal_range else 300)
                nplc = ''  # frequency doens't use this either
        else:
            raise ValueError("Invalid nplc option")

        if resolution and signal_range:
            string = (f"CONF:{mode}"
                      f"{acdc} "
                      f"{signal_range}"
                      f"{resolution}")
            if kwargs.get('verbose', False):
                print(string)
            self.instrument.write(string, **kwargs)
        elif signal_range:
            string = (f"CONF:{mode}"
                      f"{acdc} "
                      f"{signal_range}"
                      f"{nplc}")
            if verbose:
                print(string)
            self.instrument.write(string, **kwargs)
        else:

            string = (f"CONF:{mode}"
                      f"{acdc}")
            self.instrument.write(string, **kwargs)
            if verbose:
                print(string)
            if not usefreq:
                x = ':RES ' if resolution else ':NPLC '
                string2 = (f"SENS:{mode}"
                           f"{acdc}"
                           f"{x}"
                           f"{resolution if resolution else nplc}")
                self.instrument.write(string2, **kwargs)
                if verbose:
                    print(string2)

        return

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

    def set_local(self, **kwargs):
        self.instrument.write("SYSTem:LOCal", **kwargs)
        return
