from pythonequipmentdrivers import VisaResource


class Chroma_66204(VisaResource):  # 3 phase + neutral / output
    """
    Chroma_66204(address)

    address : str, address of the connected power meter

    object for accessing basic functionallity of the Chroma_66204 power meter
    """

    def __init__(self, address, **kwargs):
        super().__init__(address, **kwargs)
        return None

    def format_data(self, data):
        """
        type-casts query data to float
        if data is a comma-separated list it will split the data typecast to
        float and return a list
        """

        try:
            data = float(data)

        except ValueError:  # multiple channels selected
            data = [float(x) for x in data.split(',')]

        return data

    def get_voltage_rms(self, channel=0):
        v_rms = self.instrument.query(f'FETC:VOLT:RMS? {channel}')

        return self.format_data(v_rms)

    def get_voltage_peak(self, channel=0, polarity='positive'):

        if polarity == 'positive':
            v_pk = self.instrument.query(f'FETC:VOLT:PEAK+? {channel}')
        elif polarity == 'negative':
            v_pk = self.instrument.query(f'FETC:VOLT:PEAK-? {channel}')
        else:
            raise ValueError("invalid option for polarity"
                             + "(should be 'positive' or 'negative')")

        return self.format_data(v_pk)

    def get_voltage_dc(self, channel=0):
        v_dc = self.instrument.query(f'FETC:VOLT:DC? {channel}')

        return self.format_data(v_dc)

    def get_voltage_thd(self, channel=0):
        v_thd = self.instrument.query(f'FETC:VOLT:THD? {channel}')

        return self.format_data(v_thd)

    def get_current_rms(self, channel=0):
        i_rms = self.instrument.query(f'FETC:CURR:RMS? {channel}')

        return self.format_data(i_rms)

    def get_current_peak(self, channel=0, polarity='positive'):

        if polarity == 'positive':
            i_pk = self.instrument.query(f'FETC:CURR:PEAK+? {channel}')
        elif polarity == 'negative':
            i_pk = self.instrument.query(f'FETC:CURR:PEAK-? {channel}')
        else:
            raise ValueError("invalid option for polarity"
                             + "(should be 'positive' or 'negative')")

        return self.format_data(i_pk)

    def get_current_dc(self, channel=0):
        i_dc = self.instrument.query(f'FETC:CURR:DC? {channel}')

        return self.format_data(i_dc)

    def get_current_inrush(self, channel=0):
        i_inrush = self.instrument.query(f'FETC:CURR:INR? {channel}')

        return self.format_data(i_inrush)

    def get_current_crestfactor(self, channel=0):
        i_crestfactor = self.instrument.query(f'FETC:CURR:CRES? {channel}')

        return self.format_data(i_crestfactor)

    def get_current_thd(self, channel=0):
        i_thd = self.instrument.query(f'FETC:CURR:THD? {channel}')

        return self.format_data(i_thd)

    def get_power_real(self, channel=0):
        p_real = self.instrument.query(f'FETC:POW:REAL? {channel}')

        return self.format_data(p_real)

    def get_power_reactive(self, channel=0):
        p_reactive = self.instrument.query(f'FETC:POW:REAC? {channel}')

        return self.format_data(p_reactive)

    def get_power_apparent(self, channel=0):
        p_apparent = self.instrument.query(f'FETC:POW:APP? {channel}')

        return self.format_data(p_apparent)

    def get_power_factor(self, channel=0):
        pf = self.instrument.query(f'FETC:POW:PFAC? {channel}')

        return self.format_data(pf)

    def get_power_dc(self, channel=0):
        p_dc = self.instrument.query(f'FETC:POW:DC? {channel}')

        return self.format_data(p_dc)

    def get_power_energy(self, channel=0):
        p_energy = self.instrument.query(f'FETC:POW:ENER? {channel}')

        return self.format_data(p_energy)

    def get_frequency(self, channel=0):
        frequency = self.instrument.query(f'FETC:FREQ? {channel}')

        return self.format_data(frequency)

    def get_efficiency(self):
        eff = self.instrument.query('FETC:EFF?')

        return self.format_data(eff)

    def get_current_harmonics(self, channel, mode='VALUE'):
        """
        get_current_harmonics(self, channel, mode='VALUE')
        channel: 1-4, int
        mode: VALUE (returns amps), PERCENT (returns percent)
        returns array of current harmonics in order starting at the 0th
        (max 101)
        """
        command_str = f"FETC:CURR:HARM:ARR? {str(mode).upper()},{int(channel)}"
        harmoincs = self.instrument.query(command_str)

        return self.format_data(harmoincs)

    def get_voltage_harmonics(self, channel, mode='VALUE'):
        """
        get_voltage_harmonics(self, channel, mode='VALUE')
        channel: 1-4, int
        mode: VALUE (returns volts), PERCENT (returns percent)
        returns array of voltage harmonics in order starting at the 0th
        (max 101)
        """

        command_str = f"FETC:VOLT:HARM:ARR? {str(mode).upper()},{int(channel)}"
        harmoincs = self.instrument.query(command_str)

        return self.format_data(harmoincs)

    def get_3phase_power_real(self):
        p_real = self.instrument.query('FETC:SIGM:POW:REAL?')

        return self.format_data(p_real)

    def get_3phase_power_reactive(self):
        p_reactive = self.instrument.query('FETC:SIGM:POW:REAC?')

        return self.format_data(p_reactive)

    def get_3phase_power_apparent(self):
        p_apparent = self.instrument.query('FETC:SIGM:POW:APP?')

        return self.format_data(p_apparent)

    def get_3phase_power_factor(self):
        pf = self.instrument.query('FETC:SIGM:POW:PFAC?')

        return self.format_data(pf)

    def set_input_shunt_configuration(self, configuration):

        for idx, chan in enumerate(configuration):
            if type(chan) in [bool, int]:
                if chan:
                    configuration[idx] = "ON"
                else:
                    configuration[idx] = "OFF"

        command_str = 'CONF:INP:SHUN {},{},{},{}'.format(*configuration)
        self.instrument.write(command_str)
        return None

    def get_input_shunt_configuration(self):
        resp = self.instrument.query('CONF:INP:SHUN?')
        resp = resp.rstrip('\n')
        resp = resp.split(',')

        config = ['']*4

        for idx, chan in enumerate(resp):
            if chan == "ON":
                config[idx] = True
            elif chan == "OFF":
                config[idx] = False
            else:
                config[idx] = None

        return config

    def get_external_input_shunt_res(self):
        resistance = self.instrument.query('CONF:INP:SHUN:RESIS?')

        return self.format_data(resistance)

    def set_external_input_shunt_res(self, resistance):

        command_str = 'CONF:INP:SHUN:RESIS {},{},{},{}'.format(*resistance)
        self.instrument.write(command_str)
        return None
