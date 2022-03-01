from pythonequipmentdrivers import Scpi_Instrument
import numpy as np
from time import sleep
from typing import Union, Tuple


class Koolance_EXC900(Scpi_Instrument):
    DATA_REGISTER_MAP = {
        # kwarg, offset, width, m, r, b
        # TODO: implement more of the map
        # monitoring data
        "mon_liq_temp": (2, 2, 10, 0, 2000),
        "mon_ext_temp": (4, 2, 10, 0, 2000),
        "mon_amb_temp": (6, 2, 10, 0, 2000),
        "mon_fan_rpm": (8, 2, 1, 0, 0),
        "mon_pump_rpm": (10, 2, 1, 0, 0),
        "mon_flow_meter": (12, 2, 1, 1, 0),
        # user mode settings
        "usr_temp_sp": (14, 2, 1, 0, 500),
        "usr_pump_sp": (16, 2, 1, 0, 0),
        "usr_flow_sp": (18, 2, 1, 0, 0),
        # units
        "units": (44, 2, 1, 0, 0),
    }

    def __init__(self, address, **kwargs):
        super().__init__(address, **kwargs)

    def _read_data(self) -> bytes:
        data_request_command = [0xCF, 0x01, 0x08]
        self.instrument.write_raw(bytes(data_request_command))
        return self.instrument.read_bytes(51)

    def _write_data(self, data: bytes) -> None:
        self.instrument.write_raw(data)

    def get_settings(self) -> dict:
        data = self._read_data()
        out_dict = {}
        for name, (offs, n_bytes, m, r, b) in self.DATA_REGISTER_MAP.items():
            selected = data[offs : offs + n_bytes]
            val = int.from_bytes(selected, "big")
            val = (1 / m) * (val * 10 ** (-1 * r) - b)
            out_dict[name] = val
        return out_dict

    def set_settings(self, **kwargs) -> dict:
        data = bytearray(self._read_data())
        for name, value in kwargs.items():
            offs, n_bytes, m, r, b = self.DATA_REGISTER_MAP[name]
            value = round((m * value + b) * 10 ** r)
            val_bytes = value.to_bytes(n_bytes, "big")
            data[offs : offs + n_bytes] = val_bytes

        data[0:2] = [0xCF, 0x04]
        data[2:14] = 12 * [0]
        data[50] = sum(data[:50]) % 0x64
        self._write_data(bytes(data))
