from pythonequipmentdrivers import Scpi_Instrument as _Scpi_Instrument


class Yokogawa_760203(_Scpi_Instrument):  # 3 phase
    """
    Yokogawa_760203(address)

    address : str, address of the connected power meter

    object for accessing basic functionallity of the Yokogawa_760203 powermeter

    For additional commands see programmers Manual:
    https://cdn.tmi.yokogawa.com/IM760201-17E.pdf
    """

    def __init__(self, address, **kwargs):
        super().__init__(address, **kwargs)

        self.set_numeric_data_format('ascii')
        self.set_numeric_data_pattern(1)
        self.set_numeric_list_data_pattern(1)
        self.set_harmonic_order(0, 50)

        self._channel_measurement_codes = {'v_rms': 1,
                                           'i_rms': 2,
                                           'p': 3,
                                           's': 4,
                                           'q': 5,
                                           'lambda': 6,
                                           'phi': 7,
                                           'fu': 8,
                                           'fi': 9,
                                           'unused': 10,
                                           }

        self._channel_data_separation_index = 10

        self._list_measurement_codes = {'voltage': 1,
                                        'current': 2,
                                        'power': 3,
                                        }
        self._list_data_separation_index = 3
        return None

    def set_numeric_data_format(self, option):
        """
        set_numeric_data_format(option)

        option: str, return datatype of queries to the meter
            valid options are "ascii" and "float"

        configures the datatype returned by queries to the meter
        """

        if option.lower() == "ascii":
            self.instrument.write('NUM:FORM ASC')
        elif option.lower() == "float":
            self.instrument.write('NUM:FORM FLO')
        else:
            raise AttributeError
        return None

    def get_numeric_data_format(self):
        """
        get_numeric_data_format()

        returns the configuration the datatype returned by queries to the meter

        return: str
        """

        response = self.instrument.query('NUM:FORM?')

        data_format = response.split(' ')[-1]
        data_format = data_format.rstrip('\n')

        if data_format == "ASC":
            return "ascii"
        elif data_format == "FLO":
            return "float"
        else:
            return 'error'

    def set_numeric_data_pattern(self, pattern_number):
        """
        valid presents are 1-4 (see datasheet page 5-91) constructer sets to 1
        """
        self.instrument.write(f'NUM:NORM:PRES {pattern_number}')
        return None

    def set_numeric_list_data_pattern(self, pattern_number):
        """
        valid presents are 1-4 (see datasheet page 5-91) constructer sets to 1
        """
        self.instrument.write(f'NUM:LIST:PRES {pattern_number}')
        return None

    def set_harmonic_pll_source(self, channel, source_type):
        source_codes = {'voltage': 'U',
                        'current': 'I'}

        command_str = f"HARM:PLLS {source_codes[source_type]}{channel}"
        self.instrument.write(command_str)
        return None

    def get_channel_data(self, channel, measurment_type):
        if channel == 'sigma':
            channel = 4

        index = self._channel_data_separation_index*(channel - 1)
        index += self._channel_measurement_codes[measurment_type]
        response = self.instrument.query(f"NUM:VAL? {index}")

        return float(response)

    def get_harmonic_pll_source(self):
        response = self.instrument.query("HARM:PLLS?")
        return response.split(' ')[-1].rstrip('\n')

    def set_harmonic_order(self, order_min, order_max):
        self.instrument.write(f"HARM:ORD {order_min},{order_max}")
        return None

    def get_harmonic_order(self):
        response = self.instrument.query("HARM:ORD?")
        response = response.split(' ')[-1].rstrip('\n')

        return [int(x) for x in response.split(',')]

    def get_harmonic_data(self, channel, harmonic_type, return_total=False):
        """
        get_harmonic_data(channel, harmonic_type, return_total=False)

        returns "harmonic_type" harmonics from specified channel
            valid options for harmonic_type are: 'voltage', 'current' or
            'power' if 'return_total' it will return a tuple
            (harmoincs, total) :: (list, float), else will just return the list
            of harmonics
        """

        # set harmonic source to correct channels voltage/current
        self.set_harmonic_pll_source(channel, harmonic_type)

        # get data
        index = self._list_data_separation_index*(channel - 1)
        index += self._list_measurement_codes[harmonic_type]
        response = self.instrument.query(f"NUM:LIST:VAL? {index}")

        harmonics = [float(x) for x in response.split(',')]
        if return_total:
            return harmonics[1:], harmonics[0]
        else:
            return harmonics[1:]

    def set_current_range(self, current):
        """
        set_current_range(current)

        current: int, current range in amps

        set the current range of all phases to use for current measurements.
        'current' parameter corresponds with the current level for the top of
        the range. The Yokogawa meter only has a discrete set of ranges, if the
        value specified by current doesn't correspond to one of these ranges
        the meter will select the closest valid range, this may result in the
        range not changing after this command
        is sent.
        """

        self.instrument.write(f'CURR:RANG:ALL {int(current)}')
        return None

    def get_current_range(self):
        """
        get_current_range(current)

        returns: current_ranges, tuple corresponding with the current ranges
                 used by each phase in order.

        get the current range of all phases to use for current measurements.
        each range returns the current level for the top of the range.
        """
        resp = self.instrument.query('CURR:RANG?')
        current_ranges = [float(chan.split()[-1]) for chan in resp.split(';')]
        return tuple(current_ranges)

    def get_voltage_rms(self, channel):
        """
        get_voltage_rms(channel)

        channel: int, channel to measure

        measures voltage present on "channel" in Vrms
        """

        v_rms = self.get_channel_data(channel, 'v_rms')
        return v_rms

    def get_current_rms(self, channel):
        i_rms = self.get_channel_data(channel, 'i_rms')
        return i_rms

    def get_power_real(self, channel):
        p_real = self.get_channel_data(channel, 'p')
        return p_real

    def get_power_apparent(self, channel):
        p_apparent = self.get_channel_data(channel, 's')
        return p_apparent

    def get_power_reactive(self, channel):
        p_reactive = self.get_channel_data(channel, 'q')
        return p_reactive

    def get_power_factor(self, channel):
        pf = self.get_channel_data(channel, 'lambda')
        return pf

    def get_phase_angle(self, channel):
        phase_angle = self.get_channel_data(channel, 'phi')
        return phase_angle

    def get_frequency_voltage(self, channel):
        frequency = self.get_channel_data(channel, 'fu')
        return frequency

    def get_frequency_current(self, channel):
        frequency = self.get_channel_data(channel, 'fi')
        return frequency

    def get_voltage_harmonics(self, channel, return_total=False):
        v_harm = self.get_harmonic_data(channel, 'voltage',
                                        return_total=return_total)
        return v_harm

    def get_current_harmonics(self, channel, return_total=False):
        i_harm = self.get_harmonic_data(channel, 'current',
                                        return_total=return_total)
        return i_harm

    def get_power_harmonics(self, channel, return_total=False):
        p_harm = self.get_harmonic_data(channel, 'power',
                                        return_total=return_total)
        return p_harm
