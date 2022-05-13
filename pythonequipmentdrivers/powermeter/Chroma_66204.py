from typing import Tuple, Union

from pythonequipmentdrivers import VisaResource


class Chroma_66204(VisaResource):  # 3 phase + neutral / output
    """
    Chroma_66204(address)

    address : str, address of the connected power meter

    object for accessing basic functionallity of the Chroma_66204 power meter
    """

    def __init__(self, address: str, **kwargs) -> None:
        super().__init__(address, **kwargs)

        # sets units of energy to joules insterad of watt-hours
        self.write_resource('ENER:MODE JOULE')

    def format_data(self, query_response: str) -> Union[float, Tuple[float]]:
        """
        format_data(query_response)

        Type-casts data contained in a query response to a float
        if data is a comma-separated list it will split into a series of values
        before then typecasting each

        Args:
            query_response (str): string of ascii characters containing a
                encoded floating point/integer number, or a comma-separated
                list of such values.

        Returns:
            Union[float, Tuple[float]]: The number, or series of numbers that
                were encoded in the input string
        """

        if query_response.count(',') > 0:  # multiple channels selected
            return tuple(float(x) for x in query_response.split(','))

        return float(query_response)

    def get_voltage_rms(self, phase: int = 0) -> Union[float, Tuple[float]]:
        """
        get_voltage_rms(phase=0)

        Queries the measured value of the RMS voltage for the specified
        phase(s).

        Args:
            phase (int, optional): AC phase to to retrive measurement info from
                (1,2,3) or 0 to return the measured value for all phases.
                Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the RMS voltage for the
                given phase(s) in Vrms
        """

        if not (0 <= phase <= 3):
            raise ValueError('Invalid value of "phase", must be within [0,3]')

        response = self.query_resource(f'FETC:VOLT:RMS? {phase}')
        return self.format_data(response)

    def get_voltage_peak(self, phase: int = 0,
                         use_positive: bool = True
                         ) -> Union[float, Tuple[float]]:
        """
        get_voltage_peak(phase=0, use_positive=True)

        Queries the measured value of the peak voltage for the specified
        phase(s).

        Args:
            phase (int, optional): AC phase to to retrive measurement info from
                (1,2,3) or 0 to return the measured value for all phases.
                Defaults to 0.
            use_positive (bool, optional): If true this will return the
                positive peak voltage otherwise the peak negative voltage will
                be returned. Defaults to True.

        Returns:
            Union[float, Tuple[float]]: Measurement of the Peak voltage for the
                given phase(s) in Volts
        """

        if not (0 <= phase <= 3):
            raise ValueError('Invalid value of "phase", must be within [0,3]')

        response = self.query_resource(
            f'FETC:VOLT:PEAK{"+" if use_positive else "-"}? {phase}'
            )

        return self.format_data(response)

    def get_voltage_dc(self, phase: int = 0) -> Union[float, Tuple[float]]:
        """
        get_voltage_dc(phase=0)

        Queries the measured value of the DC voltage for the specified
        phase(s).

        Args:
            phase (int, optional): AC phase to to retrive measurement info from
                (1,2,3) or 0 to return the measured value for all phases.
                Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the DC voltage for the
                given phase(s) in Volts
        """

        if not (0 <= phase <= 3):
            raise ValueError('Invalid value of "phase", must be within [0,3]')

        response = self.query_resource(f'FETC:VOLT:DC? {phase}')
        return self.format_data(response)

    def get_voltage_thd(self, phase: int = 0) -> Union[float, Tuple[float]]:
        """
        get_voltage_thd(phase=0)

        Queries the measured value of the voltage THD for the specified
        phase(s).

        Args:
            phase (int, optional): AC phase to to retrive measurement info from
                (1,2,3) or 0 to return the measured value for all phases.
                Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the voltage THD for the
                given phase(s)
        """

        if not (0 <= phase <= 3):
            raise ValueError('Invalid value of "phase", must be within [0,3]')

        response = self.query_resource(f'FETC:VOLT:THD? {phase}')
        return self.format_data(response)

    def get_current_rms(self, phase: int = 0) -> Union[float, Tuple[float]]:
        """
        get_current_rms(phase=0)

        Queries the measured value of the RMS current for the specified
        phase(s).

        Args:
            phase (int, optional): AC phase to to retrive measurement info from
                (1,2,3) or 0 to return the measured value for all phases.
                Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the RMS current for the
                given phase(s) in Arms
        """

        if not (0 <= phase <= 3):
            raise ValueError('Invalid value of "phase", must be within [0,3]')

        response = self.query_resource(f'FETC:CURR:RMS? {phase}')
        return self.format_data(response)

    def get_current_peak(self, phase: int = 0,
                         use_positive: bool = True
                         ) -> Union[float, Tuple[float]]:

        """
        get_current_peak(phase=0, use_positive=True)

        Queries the measured value of the peak current for the specified
        phase(s).

        Args:
            phase (int, optional): AC phase to to retrive measurement info from
                (1,2,3) or 0 to return the measured value for all phases.
                Defaults to 0.
            use_positive (bool, optional): If true this will return the
                positive peak current otherwise the peak negative voltage will
                be returned. Defaults to True.

        Returns:
            Union[float, Tuple[float]]: Measurement of the Peak current for the
                given phase(s) in Amps
        """

        if not (0 <= phase <= 3):
            raise ValueError('Invalid value of "phase", must be within [0,3]')

        response = self.query_resource(
            f'FETC:CURR:PEAK{"+" if use_positive else "-"}? {phase}'
            )

        return self.format_data(response)

    def get_current_dc(self, phase: int = 0) -> Union[float, Tuple[float]]:
        """
        get_current_dc(phase=0)

        Queries the measured value of the DC current for the specified
        phase(s).

        Args:
            phase (int, optional): AC phase to to retrive measurement info from
                (1,2,3) or 0 to return the measured value for all phases.
                Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the DC current for the
                given phase(s) in Amps
        """

        if not (0 <= phase <= 3):
            raise ValueError('Invalid value of "phase", must be within [0,3]')

        response = self.query_resource(f'FETC:CURR:DC? {phase}')
        return self.format_data(response)

    def get_current_inrush(self, phase: int = 0) -> Union[float, Tuple[float]]:
        """
        get_current_inrush(phase=0)

        Queries the measured value of the inrush current for the specified
        phase(s).

        Args:
            phase (int, optional): AC phase to to retrive measurement info from
                (1,2,3) or 0 to return the measured value for all phases.
                Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the inrush current for
                the given phase(s) in Amps
        """

        if not (0 <= phase <= 3):
            raise ValueError('Invalid value of "phase", must be within [0,3]')

        response = self.query_resource(f'FETC:CURR:INR? {phase}')

        return self.format_data(response)

    def get_current_crestfactor(self,
                                phase: int = 0) -> Union[float, Tuple[float]]:
        """
        get_current_crestfactor(phase=0)

        Queries the measured value of the current crest factor for the
        specified phase(s).

        Args:
            phase (int, optional): AC phase to to retrive measurement info from
                (1,2,3) or 0 to return the measured value for all phases.
                Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the current crest factor
                for the given phase(s)
        """

        if not (0 <= phase <= 3):
            raise ValueError('Invalid value of "phase", must be within [0,3]')

        response = self.query_resource(f'FETC:CURR:CRES? {phase}')
        return self.format_data(response)

    def get_current_thd(self, phase: int = 0) -> Union[float, Tuple[float]]:
        """
        get_current_thd(phase=0)

        Queries the measured value of the current THD for the specified
        phase(s).

        Args:
            phase (int, optional): AC phase to to retrive measurement info from
                (1,2,3) or 0 to return the measured value for all phases.
                Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the current THD for the
                given phase(s)
        """

        if not (0 <= phase <= 3):
            raise ValueError('Invalid value of "phase", must be within [0,3]')

        response = self.query_resource(f'FETC:CURR:THD? {phase}')
        return self.format_data(response)

    def get_power_real(self, phase: int = 0) -> Union[float, Tuple[float]]:
        """
        get_power_real(phase=0)

        Queries the measured value of the real power for the specified
        phase(s).

        Args:
            phase (int, optional): AC phase to to retrive measurement info from
                (1,2,3) or 0 to return the measured value for all phases.
                Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the real power for the
                given phase(s) in Watts
        """

        if not (0 <= phase <= 3):
            raise ValueError('Invalid value of "phase", must be within [0,3]')

        response = self.query_resource(f'FETC:POW:REAL? {phase}')
        return self.format_data(response)

    def get_power_reactive(self, phase: int = 0) -> Union[float, Tuple[float]]:
        """
        get_power_reactive(phase=0)

        Queries the measured value of the reactive power for the specified
        phase(s).

        Args:
            phase (int, optional): AC phase to to retrive measurement info from
                (1,2,3) or 0 to return the measured value for all phases.
                Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the reactive power for
                the given phase(s) in VARs
        """

        if not (0 <= phase <= 3):
            raise ValueError('Invalid value of "phase", must be within [0,3]')

        response = self.query_resource(f'FETC:POW:REAC? {phase}')
        return self.format_data(response)

    def get_power_apparent(self, phase: int = 0) -> Union[float, Tuple[float]]:
        """
        get_power_apparent(phase=0)

        Queries the measured value of the apparent power for the specified
        phase(s).

        Args:
            phase (int, optional): AC phase to to retrive measurement info from
                (1,2,3) or 0 to return the measured value for all phases.
                Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the apparent power for
                the given phase(s) in VAs
        """

        if not (0 <= phase <= 3):
            raise ValueError('Invalid value of "phase", must be within [0,3]')

        response = self.query_resource(f'FETC:POW:APP? {phase}')
        return self.format_data(response)

    def get_power_factor(self, phase: int = 0) -> Union[float, Tuple[float]]:
        """
        get_power_factor(phase=0)

        Queries the measured value of the power factor for the specified
        phase(s).

        Args:
            phase (int, optional): AC phase to to retrive measurement info from
                (1,2,3) or 0 to return the measured value for all phases.
                Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the power factor for the
                given phase(s)
        """

        if not (0 <= phase <= 3):
            raise ValueError('Invalid value of "phase", must be within [0,3]')

        response = self.query_resource(f'FETC:POW:PFAC? {phase}')
        return self.format_data(response)

    def get_power_dc(self, phase: int = 0) -> Union[float, Tuple[float]]:
        """
        get_power_dc(phase=0)

        Queries the measured value of the DC power for the specified
        phase(s).

        Args:
            phase (int, optional): AC phase to to retrive measurement info from
                (1,2,3) or 0 to return the measured value for all phases.
                Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the DC power for the
                given phase(s) in Watts
        """

        if not (0 <= phase <= 3):
            raise ValueError('Invalid value of "phase", must be within [0,3]')

        response = self.query_resource(f'FETC:POW:DC? {phase}')
        return self.format_data(response)

    def get_energy(self, phase: int = 0) -> Union[float, Tuple[float]]:
        """
        get_energy(phase=0)

        Queries the measured value of the Energy for the specified
        phase(s).

        Args:
            phase (int, optional): AC phase to to retrive measurement info from
                (1,2,3) or 0 to return the measured value for all phases.
                Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the Energy for the
                given phase(s) in Joules
        """

        if not (0 <= phase <= 3):
            raise ValueError('Invalid value of "phase", must be within [0,3]')

        response = self.query_resource(f'FETC:POW:ENER? {phase}')
        return self.format_data(response)

    def get_frequency(self, phase: int = 0) -> Union[float, Tuple[float]]:
        """
        get_frequency(phase=0)

        Queries the measured value of the frequency for the specified
        phase(s).

        Args:
            phase (int, optional): AC phase to to retrive measurement info from
                (1,2,3) or 0 to return the measured value for all phases.
                Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the frequency for the
                given phase(s) in Hz
        """

        if not (0 <= phase <= 3):
            raise ValueError('Invalid value of "phase", must be within [0,3]')

        response = self.query_resource(f'FETC:FREQ? {phase}')
        return self.format_data(response)

    def get_efficiency(self):
        eff = self._resource.query('FETC:EFF?')

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
        harmoincs = self._resource.query(command_str)

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
        harmoincs = self._resource.query(command_str)

        return self.format_data(harmoincs)

    def get_3phase_power_real(self):
        p_real = self._resource.query('FETC:SIGM:POW:REAL?')

        return self.format_data(p_real)

    def get_3phase_power_reactive(self):
        p_reactive = self._resource.query('FETC:SIGM:POW:REAC?')

        return self.format_data(p_reactive)

    def get_3phase_power_apparent(self):
        p_apparent = self._resource.query('FETC:SIGM:POW:APP?')

        return self.format_data(p_apparent)

    def get_3phase_power_factor(self):
        pf = self._resource.query('FETC:SIGM:POW:PFAC?')

        return self.format_data(pf)

    def set_input_shunt_configuration(self, configuration) -> None:

        for idx, chan in enumerate(configuration):
            if type(chan) in [bool, int]:
                if chan:
                    configuration[idx] = "ON"
                else:
                    configuration[idx] = "OFF"

        command_str = 'CONF:INP:SHUN {},{},{},{}'.format(*configuration)
        self._resource.write(command_str)

    def get_input_shunt_configuration(self) -> Tuple[Union[bool, None]]:
        resp = self._resource.query('CONF:INP:SHUN?')
        resp = resp.rstrip('\n')
        resp = resp.split(',')

        config: Tuple[Union[bool, None]] = [None, None, None, None]

        for idx, chan in enumerate(resp):
            if chan == "ON":
                config[idx] = True
            elif chan == "OFF":
                config[idx] = False

        return config

    def get_external_input_shunt_res(self):
        resistance = self._resource.query('CONF:INP:SHUN:RESIS?')

        return self.format_data(resistance)

    def set_external_input_shunt_res(self, resistance) -> None:

        command_str = 'CONF:INP:SHUN:RESIS {},{},{},{}'.format(*resistance)
        self._resource.write(command_str)
