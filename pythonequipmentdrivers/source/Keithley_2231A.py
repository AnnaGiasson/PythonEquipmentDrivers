from pythonequipmentdrivers import VisaResource


class Keithley_2231A(VisaResource):
    """
    Keithley_2231A(address)

    address : str, address of the connected power supply

    object for accessing basic functionallity of the Keithley DC supply
    """

    def __init__(self, address: str, **kwargs) -> None:
        super().__init__(address, **kwargs)
        self.set_access_remote('remote')

    def __del__(self) -> None:
        self.set_access_remote('local')
        super().__del__()

    def set_access_remote(self, mode: str) -> None:
        """
        set_access_remote(mode)

        mode: str, interface method either 'remote' or 'local'

        set access to the device inferface to 'remote' or 'local'
        """

        if mode.lower() == 'remote':
            self.write_resource('SYSTem:RWLock')
        elif mode.lower() == 'local':
            self.write_resource('SYSTem:LOCal')
        else:
            raise ValueError(
                'Unknown option for arg "mode", should be "remote" or "local"'
                    )

    def set_channel(self, channel: int) -> None:
        """
        set_channel(channel)

        channel: int, index of the channel to control.
                 valid options are 1-3

        Selects the specified Channel to use for software control
        """

        self.write_resource(f'INST:NSEL {channel}')

    def get_channel(self) -> int:
        """
        get_channel()

        Get current selected Channel

        returns: int
        """

        response = self.query_resource('INST:NSEL?')
        return int(response)

    def set_state(self, state: bool, channel: int) -> None:
        """
        set_state(state, channel)

        Enables/disables the output of the supply

        Args:
            state (bool): Supply state (True == enabled, False == disabled)
            channel (int): Index of the channel to control. valid options
                are 1-3
        """

        self.set_channel(channel)
        self.write_resource(f"CHAN:OUTP {1 if state else 0}")

    def get_state(self, channel: int) -> bool:
        """
        get_state(channel)

        Retrives the current state of the output of the supply.

        Args:
            channel (int): index of the channel to control. Valid options
                are 1-3

        Returns:
            bool: Supply state (True == enabled, False == disabled)
        """

        self.set_channel(channel)
        response = self.query_resource("CHAN:OUTP?")
        if response not in ("ON", '1'):
            return False
        return True

    def on(self, channel: int) -> None:
        """
        on(channel)

        Enables the relay for the power supply's output equivalent to
        set_state(True).

        Args:
            channel (int): Index of the channel to control. Valid options
                are 1-3
        """

        self.set_state(True, channel)

    def off(self, channel: int) -> None:
        """
        off(channel)

        Disables the relay for the power supply's output equivalent to
        set_state(False).

        Args:
            channel (int): Index of the channel to control. Valid options
                are 1-3
        """

        self.set_state(False, channel)

    def toggle(self, channel: int) -> None:
        """
        toggle(channel)

        Reverses the current state of the Supply's output

        Args:
            channel (int): Index of the channel to control. Valid options
                are 1-3
        """

        self.set_state(self.get_state() ^ True, channel)

    def set_voltage(self, voltage: float, channel: int) -> None:
        """
        set_voltage(voltage)

        voltage: float or int, amplitude to set output to in Vdc

        channel: int, the index of the channel to set. Valid options are 1,2,3.

        set the output voltage setpoint of channel "channel" specified by
        "voltage"
        """

        self.set_channel(channel)
        self.write_resource(f"SOUR:VOLT {voltage}")

    def get_voltage(self, channel: int) -> float:
        """
        get_voltage()

        channel: int, the index of the channel to set. Valid options are 1,2,3.

        gets the output voltage setpoint in Vdc

        returns: float
        """

        self.set_channel(channel)
        response = self.query_resource("SOUR:VOLT?")
        return float(response)

    def set_current(self, current: float, channel: int) -> None:
        """
        set_current(current)

        current: float/int, current limit setpoint in Adc

        channel: int, the index of the channel to set. Valid options are 1,2,3.

        sets the current limit setting for the power supply in Adc
        """

        self.set_channel(channel)
        self.write_resource(f"SOUR:CURR {current}")

    def get_current(self, channel: int) -> float:
        """
        get_current()

        channel: int, the index of the channel to set. Valid options are 1,2,3.

        gets the current limit setting for the power supply in Adc

        returns: float
        """

        self.set_channel(channel)
        response = self.query_resource("SOUR:CURR?")
        return float(response)

    def measure_voltage(self, channel: int) -> float:
        """
        measure_voltage()

        returns measurement of the output voltage of the specified channel in
        Vdc.

        returns: float
        """

        self.set_channel(channel)
        response = self.query_resource('MEAS:VOLT?')
        return float(response)

    def measure_current(self, channel: int) -> float:
        """
        measure_current()

        returns measurement of the output current of the specified channel in
        Adc.

        returns: float
        """

        self.set_channel(channel)
        response = self.query_resource('MEAS:CURR?')
        return float(response)
