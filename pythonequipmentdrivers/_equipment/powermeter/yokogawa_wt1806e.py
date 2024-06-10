from typing import Tuple, Union

from .yokogawa_760203 import MeasurementTypes, Yokogawa_760203


class Yokogawa_WT1806E(Yokogawa_760203):  # 6 channel
    """
    Yokogawa_WT1806E(address)

    address : str, address of the connected power meter

    object for accessing basic functionallity of the Yokogawa_WT1806E power
    meter (inherits from Yokogawa_760203)

    For additional commands see programmers Manual:
    https://cdn.tmi.yokogawa.com/IMWT1801E-17EN.pdf
    """

    def __init__(self, address: str, **kwargs) -> None:
        super().__init__(address, **kwargs)
        self.three_phase_channel_names = {"sigma_a": 7, "sigma_b": 8, "sigma_c": 9}

    def get_channel_data(
        self, channel: Union[int, str], measurment: MeasurementTypes
    ) -> float:

        if channel in self.three_phase_channel_names.keys():
            channel = self.three_phase_channel_names[channel]

        index = self._CHANNEL_DATA_SEPARATION_INDEX * (channel - 1)
        index += measurment.value
        response = self.query_resource(f"NUM:VAL? {index}")

        return float(response)

    def set_harmonic_order(self, order_min: int, order_max: int) -> None:
        self.write_resource(f"HARM1:ORD {order_min},{order_max}")

    def get_harmonic_order(self) -> Tuple[int]:
        response = self.query_resource("HARM1:ORD?")
        response = response.split(" ")[-1].rstrip("\n")

        return tuple(map(int, response.split(",")))
