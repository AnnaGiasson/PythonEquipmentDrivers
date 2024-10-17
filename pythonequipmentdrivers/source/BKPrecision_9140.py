from .Keithley_2231A import Keithley_2231A


# acts as an alias of Keithley_2231A
class BKPrecision_9140(Keithley_2231A):
    """
    BKPrecision_9140(address)

    address : str, address of the connected power supply

    object for accessing basic functionallity of the B&K Precision 9140 DC supply
    """

    def set_access_remote(self, mode: str) -> None:
        """
        set_access_remote(mode)

        mode: str, interface method either 'remote' or 'RWLock' or 'local'
        note that 'RWLock' will lock the front panel keys.

        set access to the device inferface to 'remote' or 'RWLock' or 'local'
        """

        if mode.lower() == "remote":
            self.write_resource("SYSTem:REMote")
        elif mode.lower() == "rwlock":
            self.write_resource("SYSTem:RWLock")
        elif mode.lower() == "local":
            self.write_resource("SYSTem:LOCal")
        else:
            raise ValueError(
                'Unknown option for arg "mode", should be "remote" or "local"'
            )

    def set_channel(self, channel: int) -> None:
        """
        set_channel(channel)

        channel: int, index of the channel to control.
                 valid options are 0-2 coresponding to 1-3

        Selects the specified Channel to use for software control
        """

        self.write_resource(f"INST:SEL {channel}")

    def _update_channel(self, override_channel):
        """Handles updating the device channel setting"""

        if override_channel is not None:
            self.set_channel(override_channel - 1)
        elif self.channel is not None:
            self.set_channel(self.channel - 1)
        else:
            raise TypeError(
                "Channel number must be provided if it is not provided during"
                + "initialization"
            )
        return

    def get_channel(self) -> int:
        """
        get_channel()

        Get current selected Channel

        returns: int
        """

        response = self.query_resource("INST:SEL?")
        return int(response) + 1

    def set_state(self, state: bool, channel: int = None) -> None:
        """
        set_state(state, channel)

        Enables/disables the output of the supply

        Args:
            state (bool): Supply state (True == enabled, False == disabled)
            channel (int): Index of the channel to control. valid options
                are 1-3
        """

        self._update_channel(channel)
        self.write_resource(f"OUTP:STAT {1 if state else 0}")

    def get_state(self, channel: int = None) -> bool:
        """
        get_state(channel)

        Retrives the current state of the output of the supply.

        Args:
            channel (int): index of the channel to control. Valid options
                are 1-3

        Returns:
            bool: Supply state (True == enabled, False == disabled)
        """

        self._update_channel(channel)
        response = self.query_resource("OUTP:STAT?")
        if response not in ("ON", "1"):
            return False
        return True

    def all_get_state(self) -> bool:
        """
        all_get_state(channel)

        Retrives the current state of the output of the supply.

        Args:
            None

        Returns:
            bool: Supply state (True == enabled, False == disabled)
        """

        response = self.query_resource("OUTP:ALL?")
        if response not in ("ON", "1"):
            return False
        return True

    def all_on(self) -> None:
        """
        all_on()

        Enables the relay for ALL the power supply's outputs equivalent to
        set_state(True).

        Args:
            None
        """

        self.write_resource(f"OUTP:ALL {1}")

    def all_off(self) -> None:
        """
        all_off()

        Disables the relay for ALL the power supply's outputs equivalent to
        set_state(False).

        Args:
            None
        """

        self.write_resource(f"OUTP:ALL {0}")

    def all_toggle(self) -> None:
        """
        all_toggle()

        Reverses the current state of ALL the Supply's outputs

        Args:
            None
        """

        if self.all_get_state():
            self.all_off()
        else:
            self.all_on()

    def set_slewrate(self, slewrate: float, channel: int = None) -> None:
        """
        set_slewrate(current)

        slewrate: float/int, slew rate setpoint in volts per second. Valid options are 0.001 to 3200.0 V/s.

        channel: int=None, the index of the channel to set. Valid options are 1,2,3.

        sets the slew rate setting for the power supply in V/s
        """
        if 0.001 < slewrate:
            slewrate = 0.001
        elif slewrate > 3200:
            slewrate = 3200

        self._update_channel(channel)
        self.write_resource(f"VOLT:SLOP {slewrate}")

    def get_slewrate(self, channel: int = None) -> float:
        """
        get_slewrate()

        channel: int=None, the index of the channel to get. Valid options are 1,2,3.

        gets the slew rate setting for the power supply in V/s

        returns: float
        """

        self._update_channel(channel)
        response = self.query_resource("VOLT:SLOP?")
        return float(response)

    def set_current_slewrate(self, slewrate: float, channel: int = None) -> None:
        """
        set_current_slewrate(current)

        slewrate: float/int, slew rate setpoint in Amps per second. Valid options are 1 to 800.0 A/s.

        channel: int=None, the index of the channel to set. Valid options are 1,2,3.

        sets the current slew rate setting for the power supply in A/s
        """
        if 1 < slewrate:
            slewrate = 1
        elif slewrate > 800:
            slewrate = 800

        self._update_channel(channel)
        self.write_resource(f"CURR:SLOP {slewrate}")

    def get_current_slewrate(self, channel: int = None) -> float:
        """
        get_current_slewrate()

        channel: int=None, the index of the channel to get. Valid options are 1,2,3.

        gets the current slew rate setting for the power supply in A/s

        returns: float
        """

        self._update_channel(channel)
        response = self.query_resource("VOLT:SLOP?")
        return float(response)
