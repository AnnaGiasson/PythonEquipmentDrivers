from typing import List, Union

from pythonequipmentdrivers import VisaResource


class Yokogawa_760401(VisaResource):  # single phase
    """
    Programmers Manual:
    https://www.yokogawa.com/pdf/provide/E/GW/IM/0000027039/0/IMWT310-17EN.pdf
    """

    def __init__(self, address: str, **kwargs) -> None:
        super().__init__(address, **kwargs)

    def get_measurement_type(self, item_number: int) -> str:

        response = self.query_resourcey("NUM?")
        resp_args = [arg for arg in response.split(";") if "ITEM" in arg]

        for arg in resp_args:
            if int(arg.split(" ")[0].replace("ITEM", "")) == item_number:
                return arg.split(" ")[1].split(",")[0]

        raise IndexError(
            'Could not find a measurement type at the given item_number'
            )

    def get_measurement(self, item_number: int) -> Union[float, List[float]]:

        if isinstance(item_number, int):
            response = self.query_resource("NUM:VAL?")
            return float(response.split(",")[item_number - 1])

        elif isinstance(item_number, list):
            meas = []
            for item in item_number:
                meas.append(self.get_measurement(item))
            return meas
