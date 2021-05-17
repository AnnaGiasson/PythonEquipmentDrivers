from .Yokogawa_760203 import Yokogawa_760203


class Yokogawa_WT1806E(Yokogawa_760203):  # 6 channel
    """
    Yokogawa_WT1806E(address)

    address : str, address of the connected power meter

    object for accessing basic functionallity of the Yokogawa_WT1806E power
    meter (inherits from Yokogawa_760203)

    For additional commands see programmers Manual:
    https://cdn.tmi.yokogawa.com/IMWT1801E-17EN.pdf
    """

    def __init__(self, address, **kwargs):
        super().__init__(address, **kwargs)
        self.three_phase_channel_names = {'sigma_a': 7,
                                          'sigma_b': 8,
                                          'sigma_c': 9}
        return None

    def get_channel_data(self, channel, measurment_type):
        if channel in self.three_phase_channel_names.keys():
            channel = self.three_phase_channel_names[channel]

        index = self._channel_data_separation_index*(channel - 1)
        index += self._channel_measurement_codes[measurment_type]
        response = self.instrument.query(f"NUM:VAL? {index}")

        return float(response)

    def set_harmonic_order(self, order_min, order_max):
        self.instrument.write(f"HARM1:ORD {order_min},{order_max}")
        return None

    def get_harmonic_order(self):
        response = self.instrument.query("HARM1:ORD?")
        response = response.split(' ')[-1].rstrip('\n')

        return [int(x) for x in response.split(',')]
