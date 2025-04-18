import re
from dataclasses import dataclass

from ..core import VisaResource


@dataclass(frozen=True, slots=True)
class _Module:
    name: str
    v_max: float
    i_max: float


_SUPPORTED_MODULES = {
    "N6731B": _Module(name="N6731B", v_max=5.1, i_max=10.2),
    "N6733B": _Module(name="N6733B", v_max=20.4, i_max=2.55),
    "N6751A": _Module(name="N6751A", v_max=51.0, i_max=5.1),
    "N6755A": _Module(name="N6755A", v_max=20.4, i_max=51),
    "N6775A": _Module(name="N6775A", v_max=61.2, i_max=5.1),
}


class Keysight_N6700(VisaResource):

    def __init__(self, address: str, **kwargs) -> None:
        super().__init__(address, **kwargs)

        # check valid connection
        manuf, model, *_ = self.idn.split(",")  # self.idn defined in VisaResource
        if model[:3] != "N67":
            raise ValueError(
                f"Instrument at {address} is not a Keysight/Agilent N67xx type DC supply/power analyzer."
            )

        # read configuration from instrument
        self._channel_config: dict[int, _Module] = (
            dict()
        )  # channel number: (v_max, i_max)
        self._read_channel_config()

    def _read_channel_config(self) -> None:
        """
        An internal function, should not be used by interfacing file.
        :param module: Detected module
        :return: Returns the voltage and current limits
        """

        response = self.query_resource("*RDT?")

        # note: regex below captures index number and module type (needs to start with N67) for each channel
        for chan_idx, module_name in re.findall(r"chan (\d*):(N67\w*)", response):

            if module_name not in _SUPPORTED_MODULES:
                raise ValueError(
                    f'Module "{module_name}" is not currently supported by this driver.'
                )

            self._channel_config[int(chan_idx)] = _SUPPORTED_MODULES[module_name]

    def _check_valid_channel(self, channel: int) -> None:
        if channel not in self._channel_config:
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
        self.set_state(state=True, channel=channel)

    def off(self, channel: int) -> None:
        """
        off(channel)

        Disables the relay for the power supply's output equivalent to
        set_state(False, channel).

        Args:
            channel (int): Index of the channel to control.
        """

        self.set_state(state=False, channel=channel)

    def toggle(self, channel: int) -> None:
        """
        toggle(channel)

        Reverses the current state of the Supply's output

        Args:
            channel (int): Index of the channel to command.
        """

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
        channel = self._channel_config[channel]

        if voltage > channel.v_max:
            raise ValueError(
                f"Tried to set voltage out of supply range ({channel.v_max} V)"
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
        channel = self._channel_config[channel]

        if current > channel.i_max:
            raise ValueError(
                f"Tried to set current out of supply range ({channel.i_max} V)"
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

    def measure_power(self, channel: int) -> float:
        """
        measure_power()

        returns measurement of the output power of the specified channel in
        W.

        Args:
            channel (int): Index of the channel to query.

        returns: float
        """

        self._check_valid_channel(channel)
        channel = self._channel_config[channel]

        # check if module supports this feature
        if not re.match(r"N67[68]\wA", channel.name):
            raise ValueError(
                "Power measurements only supported on N676xA and N678xA modules"
            )

        # read power
        response = self.query_resource(f"meas:pow? (@{channel})")
        return float(response)
