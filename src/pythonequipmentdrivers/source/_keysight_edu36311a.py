from dataclasses import dataclass
from ..core import VisaResource


@dataclass(frozen=True, slots=True)
class _Channel:
    v_max: float
    i_max: float
    
_SUPPORTED_CHANNELS = {
    1: _Channel(v_max=6.0, i_max=5.0),
    2: _Channel(v_max=30.0, i_max=1.0),
    3: _Channel(v_max=30.0, i_max=1.0),
}


class Keysight_EDU36311A(VisaResource):

    def __init__(self, address: str, **kwargs) -> None:
        super().__init__(address, **kwargs)

        # check valid connection
        manuf, model, *_ = self.idn.split(",")  # self.idn defined in VisaResource
        if model != "EDU36311A":
            raise ValueError(
                f"Instrument at {address} is not a Keysight EDU36311A DC power supply."
            )
            
    def _check_valid_channel(self, channel: int) -> None:
        if channel not in _SUPPORTED_CHANNELS:
            raise ValueError(f'Unknown Channel Number "{channel}"')
            
    def set_state(self, state: bool, channel: int) -> None:
        """
        set_state(state, channel)

        Enables/disables the output of the supply

        Args:
            state (bool): Supply state (True == enabled, False == disabled)
            channel (int): Index of the channel to control.
        """
        
        self._check_valid_channel(channel)
        self.write_resource(f"output {'on' if state else 'off'}, (@{channel})")

    def get_state(self, channel: int) -> bool:
        """
        get_state(channel)

        Retrives the current state of the output of the supply.

        Args:
            channel (int): index of the channel to control.

        Returns:
            bool: Supply state (True == enabled, False == disabled)
        """

        self._check_valid_channel(channel)
        response = self.query_resource(f"output:state? (@{channel})")
        return "1" in response

    def on(self, channel: int) -> None:
        """
        on(channel)

        Enables the relay for the power supply's output equivalent to
        set_state(True, channel).

        Args:
            channel (int): Index of the channel to control.
        """
        
        self._check_valid_channel(channel)
        self.set_state(state=True, channel=channel)

    def off(self, channel: int) -> None:
        """
        off(channel)

        Disables the relay for the power supply's output equivalent to
        set_state(False, channel).

        Args:
            channel (int): Index of the channel to control.
        """
        
        self._check_valid_channel(channel)
        self.set_state(state=False, channel=channel)

    def toggle(self, channel: int) -> None:
        """
        toggle(channel)

        Reverses the current state of the Supply's output

        Args:
            channel (int): Index of the channel to command.
        """

        self._check_valid_channel(channel)
        self.set_state(state=self.get_state(channel) ^ True, channel=channel)

    def set_voltage(self, voltage: float, channel: int) -> None:
        """
        set_voltage()

        Sets the voltage limit setting for the power supply in Vdc

        Args:
            voltage (float): voltage limit setpoint in Vdc
            channel (int): Index of the channel to command.

        returns: float
        """
        
        self._check_valid_channel(channel)
        if voltage > _SUPPORTED_CHANNELS[channel].v_max:
            raise ValueError(
                f"Tried to set voltage out of supply range ({_SUPPORTED_CHANNELS[channel].v_max} V)"
            )

        self.write_resource(f"volt {voltage},(@{channel})")

    def get_voltage(self, channel: int) -> float:
        """
        get_voltage()

        gets the voltage limit setting for the power supply in Vdc

        Args:
            channel (int): Index of the channel to query.

        returns: float
        """
        
        self._check_valid_channel(channel)
        response = self.query_resource(f"volt? (@{channel})")
        return float(response)

    def set_current(self, current: float, channel: int) -> None:
        """
        set_current()

        Sets the current limit setting for the power supply in Adc

        Args:
            current (float): current limit setpoint in Adc
            channel (int): Index of the channel to command.

        returns: float
        """
        
        self._check_valid_channel(channel)
        if current > _SUPPORTED_CHANNELS[channel].i_max:
            raise ValueError(
                f"Tried to set current out of supply range ({_SUPPORTED_CHANNELS[channel].i_max} A)"
            )

        self.write_resource(f"curr {current},(@{channel})")

    def get_current(self, channel: int) -> float:
        """
        get_current()

        gets the current limit setting for the power supply in Adc

        Args:
            channel (int): Index of the channel to query.

        returns: float
        """
        
        self._check_valid_channel(channel)
        response = self.query_resource(f"curr? (@{channel})")
        return float(response)

    def measure_voltage(self, channel: int) -> float:
        """
        measure_voltage()

        returns measurement of the output voltage of the specified channel in
        Vdc.

        Args:
            channel (int): Index of the channel to query.

        returns: float
        """
        
        self._check_valid_channel(channel)
        response = self.query_resource(f"meas:volt? (@{channel})")
        return float(response)

    def measure_current(self, channel: int) -> float:
        """
        measure_current()

        returns measurement of the output current of the specified channel in
        Adc.

        Args:
            channel (int): Index of the channel to query.

        returns: float
        """
        
        self._check_valid_channel(channel)
        response = self.query_resource(f"meas:curr? (@{channel})")
        return float(response)
