from pythonequipmentdrivers import Scpi_Instrument


class Yokogawa_760401(Scpi_Instrument):  # single phase
    """
    Programmers Manual:
    https://www.yokogawa.com/pdf/provide/E/GW/IM/0000027039/0/IMWT310-17EN.pdf
    """

    def __init__(self, address, **kwargs):
        super().__init__(address, **kwargs)
        return None

    def get_measurement_type(self, item_number):
        response = self.instrument.query("NUM?")
        resp_args = [arg for arg in response.split(";") if "ITEM" in arg]
        for arg in resp_args:
            if int(arg.split(" ")[0].replace("ITEM", "")) == item_number:
                return arg.split(" ")[1].split(",")[0]
        return None

    def get_measurement(self, item_number):
        if type(item_number) == int:
            response = self.instrument.query("NUM:VAL?")
            return float(response.split(",")[item_number - 1])
        elif type(item_number) == list:
            meas = []
            for item in item_number:
                meas.append(self.get_measurement(item))
            return meas
