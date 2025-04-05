from typing import Iterable, Tuple, Union

from ..core import VisaResource


class Chroma_66204(VisaResource):  # 3 phase + neutral / output
    """
    Chroma_66204(address)

    address : str, address of the connected power meter

    object for accessing basic functionallity of the Chroma_66204 power meter
    """

    def __init__(self, address: str, **kwargs) -> None:
        super().__init__(address, **kwargs)

        # sets units of energy to joules insterad of watt-hours
        self.write_resource("ENER:MODE JOULE")

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

        if query_response.count(",") > 0:  # multiple channels selected
            return tuple(float(x) for x in query_response.split(","))

        return float(query_response)

    def get_voltage_rms(self, channel: int = 0) -> Union[float, Tuple[float]]:
        """
        get_voltage_rms(channel=0)

        Queries the measured value of the RMS voltage for the specified
        channel(s).

        Args:
            channel (int, optional): powermeter channel to to retrive
                measurement info from (1, 2, 3, 4) or 0 to return the measured
                value for all channel. Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the RMS voltage for the
                given channel(s) in Vrms
        """

        if not (0 <= channel <= 4):
            raise ValueError('Invalid value of "channel", must be in [0,4]')

        response = self.query_resource(f"FETC:VOLT:RMS? {channel}")
        return self.format_data(response)

    def get_voltage_peak(
        self, channel: int = 0, use_positive: bool = True
    ) -> Union[float, Tuple[float]]:
        """
        get_voltage_peak(channel=0, use_positive=True)

        Queries the measured value of the peak voltage for the specified
        channel(s).

        Args:
            channel (int, optional): powermeter channel to to retrive
                measurement info from (1, 2, 3, 4) or 0 to return the measured
                value for all channel. Defaults to 0.
            use_positive (bool, optional): If true this will return the
                positive peak voltage otherwise the peak negative voltage will
                be returned. Defaults to True.

        Returns:
            Union[float, Tuple[float]]: Measurement of the Peak voltage for the
                given channel(s) in Volts
        """

        if not (0 <= channel <= 4):
            raise ValueError('Invalid value of "channel", must be in [0,4]')

        response = self.query_resource(
            f'FETC:VOLT:PEAK{"+" if use_positive else "-"}? {channel}'
        )

        return self.format_data(response)

    def get_voltage_dc(self, channel: int = 0) -> Union[float, Tuple[float]]:
        """
        get_voltage_dc(channel=0)

        Queries the measured value of the DC voltage for the specified
        channel(s).

        Args:
            channel (int, optional): powermeter channel to to retrive
                measurement info from (1, 2, 3, 4) or 0 to return the measured
                value for all channel. Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the DC voltage for the
                given channel(s) in Volts
        """

        if not (0 <= channel <= 4):
            raise ValueError('Invalid value of "channel", must be in [0,4]')

        response = self.query_resource(f"FETC:VOLT:DC? {channel}")
        return self.format_data(response)

    def get_voltage_thd(self, channel: int = 0) -> Union[float, Tuple[float]]:
        """
        get_voltage_thd(channel=0)

        Queries the measured value of the voltage THD for the specified
        channel(s).

        Args:
            channel (int, optional): powermeter channel to to retrive
                measurement info from (1, 2, 3, 4) or 0 to return the measured
                value for all channel. Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the voltage THD for the
                given channel(s)
        """

        if not (0 <= channel <= 4):
            raise ValueError('Invalid value of "channel", must be in [0,4]')

        response = self.query_resource(f"FETC:VOLT:THD? {channel}")
        return self.format_data(response)

    def get_current_rms(self, channel: int = 0) -> Union[float, Tuple[float]]:
        """
        get_current_rms(channel=0)

        Queries the measured value of the RMS current for the specified
        channel(s).

        Args:
            channel (int, optional): powermeter channel to to retrive
                measurement info from (1, 2, 3, 4) or 0 to return the measured
                value for all channel. Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the RMS current for the
                given channel(s) in Arms
        """

        if not (0 <= channel <= 4):
            raise ValueError('Invalid value of "channel", must be in [0,4]')

        response = self.query_resource(f"FETC:CURR:RMS? {channel}")
        return self.format_data(response)

    def get_current_peak(
        self, channel: int = 0, use_positive: bool = True
    ) -> Union[float, Tuple[float]]:
        """
        get_current_peak(channel=0, use_positive=True)

        Queries the measured value of the peak current for the specified
        channel(s).

        Args:
            channel (int, optional): powermeter channel to to retrive
                measurement info from (1, 2, 3, 4) or 0 to return the measured
                value for all channel. Defaults to 0.
            use_positive (bool, optional): If true this will return the
                positive peak current otherwise the peak negative voltage will
                be returned. Defaults to True.

        Returns:
            Union[float, Tuple[float]]: Measurement of the Peak current for the
                given channel(s) in Amps
        """

        if not (0 <= channel <= 4):
            raise ValueError('Invalid value of "channel", must be in [0,4]')

        response = self.query_resource(
            f'FETC:CURR:PEAK{"+" if use_positive else "-"}? {channel}'
        )

        return self.format_data(response)

    def get_current_dc(self, channel: int = 0) -> Union[float, Tuple[float]]:
        """
        get_current_dc(channel=0)

        Queries the measured value of the DC current for the specified
        channel(s).

        Args:
            channel (int, optional): powermeter channel to to retrive
                measurement info from (1, 2, 3, 4) or 0 to return the measured
                value for all channel. Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the DC current for the
                given channel(s) in Amps
        """

        if not (0 <= channel <= 4):
            raise ValueError('Invalid value of "channel", must be in [0,4]')

        response = self.query_resource(f"FETC:CURR:DC? {channel}")
        return self.format_data(response)

    def get_current_inrush(self, channel: int = 0) -> Union[float, Tuple[float]]:
        """
        get_current_inrush(channel=0)

        Queries the measured value of the inrush current for the specified
        channel(s).

        Args:
            channel (int, optional): powermeter channel to to retrive
                measurement info from (1, 2, 3, 4) or 0 to return the measured
                value for all channel. Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the inrush current for
                the given channel(s) in Amps
        """

        if not (0 <= channel <= 4):
            raise ValueError('Invalid value of "channel", must be in [0,4]')

        response = self.query_resource(f"FETC:CURR:INR? {channel}")

        return self.format_data(response)

    def get_current_crestfactor(self, channel: int = 0) -> Union[float, Tuple[float]]:
        """
        get_current_crestfactor(channel=0)

        Queries the measured value of the current crest factor for the
        specified channel(s).

        Args:
            channel (int, optional): powermeter channel to to retrive
                measurement info from (1, 2, 3, 4) or 0 to return the measured
                value for all channel. Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the current crest factor
                for the given channel(s)
        """

        if not (0 <= channel <= 4):
            raise ValueError('Invalid value of "channel", must be in [0,4]')

        response = self.query_resource(f"FETC:CURR:CRES? {channel}")
        return self.format_data(response)

    def get_current_thd(self, channel: int = 0) -> Union[float, Tuple[float]]:
        """
        get_current_thd(channel=0)

        Queries the measured value of the current THD for the specified
        channel(s).

        Args:
            channel (int, optional): powermeter channel to to retrive
                measurement info from (1, 2, 3, 4) or 0 to return the measured
                value for all channel. Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the current THD for the
                given channel(s)
        """

        if not (0 <= channel <= 4):
            raise ValueError('Invalid value of "channel", must be in [0,4]')

        response = self.query_resource(f"FETC:CURR:THD? {channel}")
        return self.format_data(response)

    def get_power_real(self, channel: int = 0) -> Union[float, Tuple[float]]:
        """
        get_power_real(channel=0)

        Queries the measured value of the real power for the specified
        channel(s).

        Args:
            channel (int, optional): powermeter channel to to retrive
                measurement info from (1, 2, 3, 4) or 0 to return the measured
                value for all channel. Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the real power for the
                given channel(s) in Watts
        """

        if not (0 <= channel <= 4):
            raise ValueError('Invalid value of "channel", must be in [0,4]')

        response = self.query_resource(f"FETC:POW:REAL? {channel}")
        return self.format_data(response)

    def get_power_reactive(self, channel: int = 0) -> Union[float, Tuple[float]]:
        """
        get_power_reactive(channel=0)

        Queries the measured value of the reactive power for the specified
        channel(s).

        Args:
            channel (int, optional): powermeter channel to to retrive
                measurement info from (1, 2, 3, 4) or 0 to return the measured
                value for all channel. Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the reactive power for
                the given channel(s) in VARs
        """

        if not (0 <= channel <= 4):
            raise ValueError('Invalid value of "channel", must be in [0,4]')

        response = self.query_resource(f"FETC:POW:REAC? {channel}")
        return self.format_data(response)

    def get_power_apparent(self, channel: int = 0) -> Union[float, Tuple[float]]:
        """
        get_power_apparent(channel=0)

        Queries the measured value of the apparent power for the specified
        channel(s).

        Args:
            channel (int, optional): powermeter channel to to retrive
                measurement info from (1, 2, 3, 4) or 0 to return the measured
                value for all channel. Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the apparent power for
                the given channel(s) in VAs
        """

        if not (0 <= channel <= 4):
            raise ValueError('Invalid value of "channel", must be in [0,4]')

        response = self.query_resource(f"FETC:POW:APP? {channel}")
        return self.format_data(response)

    def get_power_factor(self, channel: int = 0) -> Union[float, Tuple[float]]:
        """
        get_power_factor(channel=0)

        Queries the measured value of the power factor for the specified
        channel(s).

        Args:
            channel (int, optional): powermeter channel to to retrive
                measurement info from (1, 2, 3, 4) or 0 to return the measured
                value for all channel. Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the power factor for the
                given channel(s)
        """

        if not (0 <= channel <= 4):
            raise ValueError('Invalid value of "channel", must be in [0,4]')

        response = self.query_resource(f"FETC:POW:PFAC? {channel}")
        return self.format_data(response)

    def get_power_dc(self, channel: int = 0) -> Union[float, Tuple[float]]:
        """
        get_power_dc(channel=0)

        Queries the measured value of the DC power for the specified
        channel(s).

        Args:
            channel (int, optional): powermeter channel to to retrive
                measurement info from (1, 2, 3, 4) or 0 to return the measured
                value for all channel. Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the DC power for the
                given channel(s) in Watts
        """

        if not (0 <= channel <= 4):
            raise ValueError('Invalid value of "channel", must be in [0,4]')

        response = self.query_resource(f"FETC:POW:DC? {channel}")
        return self.format_data(response)

    def get_energy(self, channel: int = 0) -> Union[float, Tuple[float]]:
        """
        get_energy(channel=0)

        Queries the measured value of the Energy for the specified
        channel(s).

        Args:
            channel (int, optional): powermeter channel to to retrive
                measurement info from (1, 2, 3, 4) or 0 to return the measured
                value for all channel. Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the Energy for the
                given channel(s) in Joules
        """

        if not (0 <= channel <= 4):
            raise ValueError('Invalid value of "channel", must be in [0,4]')

        response = self.query_resource(f"FETC:POW:ENER? {channel}")
        return self.format_data(response)

    def get_frequency(self, channel: int = 0) -> Union[float, Tuple[float]]:
        """
        get_frequency(channel=0)

        Queries the measured value of the frequency for the specified
        channel(s).

        Args:
            channel (int, optional): powermeter channel to to retrive
                measurement info from (1, 2, 3, 4) or 0 to return the measured
                value for all channel. Defaults to 0.

        Returns:
            Union[float, Tuple[float]]: Measurement of the frequency for the
                given channel(s) in Hz
        """

        if not (0 <= channel <= 4):
            raise ValueError('Invalid value of "channel", must be in [0,4]')

        response = self.query_resource(f"FETC:FREQ? {channel}")
        return self.format_data(response)

    def get_efficiency(self) -> float:
        """
        get_efficiency()

        Measures the efficiency of a power supply or energy converter. Meaning
        of the result is determined by the wiring configuration of the power
        meter. See user manual for additional information.

        Returns:
            float: efficieny
        """

        response = self.query_resource("FETC:EFF?")
        return self.format_data(response)

    def get_current_harmonics(self, channel: int, mode: str = "value") -> float:
        """
        get_current_harmonics(channel, mode="value")

        Fetches the measured current harmonics (an array of values) for a given
        channel.

        Args:
            channel (int, optional): powermeter channel to to retrive
                measurement info from (1, 2, 3, 4) or 0 to return the measured
                value for all channel. Defaults to 0.
            mode (str, optional): Determines the units of the retrieved
                measurement, valid options are "value" (amplitude in Amps) and
                "percent" (amplitude in percent). Defaults to "value".

        Returns:
            float: array of current harmonics in order starting at the 0th
                (max 101).
        """

        command_str = f"FETC:CURR:HARM:ARR? {mode.upper()},{channel}"
        response = self.query_resource(command_str)
        return self.format_data(response)

    def get_voltage_harmonics(self, channel: int, mode: str = "value") -> float:
        """
        get_voltage_harmonics(channel, mode="value")

        Fetches the measured voltage harmonics (an array of values) for a given
        channel.

        Args:
            channel (int, optional): powermeter channel to to retrive
                measurement info from (1, 2, 3, 4) or 0 to return the measured
                value for all channel. Defaults to 0.
            mode (str, optional): Determines the units of the retrieved
                measurement, valid options are "value" (amplitude in Volts) and
                "percent" (amplitude in percent). Defaults to "value".

        Returns:
            float: array of voltage harmonics in order starting at the 0th
                (max 101).
        """

        command_str = f"FETC:VOLT:HARM:ARR? {mode.upper()},{channel}"
        response = self.query_resource(command_str)
        return self.format_data(response)

    def get_3phase_power_real(self) -> float:
        """
        get_3phase_power_real()

        Queries the measured value of the three-phase real power.
        Interpretation depends on the wiring configuration used.

        Returns:
            float: three-phase real power in Watts
        """

        response = self.query_resource("FETC:SIGM:POW:REAL?")
        return self.format_data(response)

    def get_3phase_power_reactive(self) -> float:
        """
        get_3phase_power_reactive()

        Queries the measured value of the three-phase reactive power.
        Interpretation depends on the wiring configuration used.

        Returns:
            float: three-phase reactive power in VARs
        """

        response = self.query_resource("FETC:SIGM:POW:REAC?")
        return self.format_data(response)

    def get_3phase_power_apparent(self) -> float:
        """
        get_3phase_power_apparent()

        Queries the measured value of the three-phase apparent power.
        Interpretation depends on the wiring configuration used.

        Returns:
            float: three-phase apparent power in VAs
        """

        response = self.query_resource("FETC:SIGM:POW:APP?")
        return self.format_data(response)

    def get_3phase_power_factor(self) -> float:
        """
        get_3phase_power_factor()

        Queries the measured value of the three-phase power_factor.
        Interpretation depends on the wiring configuration used.

        Returns:
            float: three-phase power_factor
        """

        response = self.query_resource("FETC:SIGM:POW:PFAC?")
        return self.format_data(response)

    def set_input_shunt_configuration(self, config: Iterable[bool]) -> None:
        """
        set_input_shunt_configuration(config)

        Sets the configuration for each channels input shunt to use either an
        external shunt or the internal shunt built into the powermeter.

        Args:
            config (Iterable[bool]): a boolean sequence listing the whether
                each channel is configured to use an external shunt.
        """

        command_str = "CONF:INP:SHUN {},{},{},{}"

        self.write_resource(
            command_str.format(
                *("ON" if is_external else "OFF" for is_external in config)
            )
        )

    def get_input_shunt_configuration(self) -> Tuple[bool]:
        """
        get_input_shunt_configuration()

        Queries the configuration of each channels input shunt, whether they
        use an external shunt or the internal shunt built into the powermeter.

        Returns:
            Tuple[bool]: a boolean sequence listing the whether each channels
                is configured to use an external shunt.
        """

        response = self.query_resource("CONF:INP:SHUN?")

        config = tuple(channel_config == "ON" for channel_config in response.split(","))

        return config

    def get_external_shunt_resistances(self) -> Tuple[float]:
        """
        get_external_shunt_resistances()

        Queries the resistence of the external shunt used for each channel when
        the external shunt configuration is used.

        Returns:
            Tuple[float]: Each channels shunt resistance in Ohms
        """

        response = self.query_resource("CONF:INP:SHUN:RESIS?")
        return self.format_data(response)

    def set_external_shunt_resistances(self, resistances: Iterable[float]) -> None:
        """
        set_external_shunt_resistances()

        Sets the resistence of the external shunt used for each channel when
        the external shunt configuration is used.

        Args:
            Iterable[float]: Each channels shunt resistance in Ohms
        """

        command_str = "CONF:INP:SHUN:RESIS {},{},{},{}".format(*resistances)
        self.query_resource(command_str)
