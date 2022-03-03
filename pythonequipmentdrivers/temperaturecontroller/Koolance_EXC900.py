from pythonequipmentdrivers import Scpi_Instrument
import numpy as np
from time import sleep
from typing import Literal, Union, Tuple


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
        "usr_temp_sp_liq": (14, 2, 1, 0, 500),
        "usr_temp_sp_ext": (14, 2, 1, 0, 1000),
        "usr_temp_sp_liq_amb": (14, 2, 1, 0, 1500),
        "usr_temp_sp_ext_amb": (14, 2, 1, 0, 2000),
        "usr_pump_sp": (16, 2, 1, 0, 0),
        "usr_flow_sp": (18, 2, 1, 0, 0),
        # units
        "units": (44, 2, 1, 0, 0),
    }

    def __init__(self, address, **kwargs):
        super().__init__(address, **kwargs)

    def _read_data(self) -> bytes:
        """Read binary data from the device and return bytes"""
        data_request_command = [0xCF, 0x01, 0x08]
        self.instrument.write_raw(bytes(data_request_command))
        return self.instrument.read_bytes(51)

    def _write_data(self, data: bytes) -> None:
        """Write bytes to the device"""
        self.instrument.write_raw(data)

    def read_settings(self, data: bytes = None) -> dict:
        """
        Read data from the device and output values of supported parameters
        in a dictionary format



        Returns:
            dict: dict of parameter name and the real value
        """
        data = data if data else self._read_data()
        out_dict = {}
        for name, (offs, n_bytes, m, r, b) in self.DATA_REGISTER_MAP.items():
            selected = data[offs : offs + n_bytes]
            val = int.from_bytes(selected, "big")
            val = (1 / m) * (val * 10 ** (-1 * r) - b)
            out_dict[name] = val
        return out_dict

    def update_settings(self, **kwargs) -> None:
        """
        Update settings to the values provided

        Each kwarg should correspond to a supported parameter name as defined in
        Koolance_EXC900.DATA_REGISTER_MAP

        """
        data = bytearray(self._read_data())
        for name, value in kwargs.items():
            try:
                offs, n_bytes, m, r, b = self.DATA_REGISTER_MAP[name]
            except KeyError:
                raise TypeError(f"{name} is not a valid setting name")
            value = round((m * value + b) * 10 ** r)
            val_bytes = value.to_bytes(n_bytes, "big")
            data[offs : offs + n_bytes] = val_bytes

        data[0:2] = [0xCF, 0x04]  # configure the command bytes for a write
        data[2:14] = 12 * [0]  # set read-only locations to 0
        data[50] = sum(data[:50]) % 0x64  # compute the checksum
        self._write_data(bytes(data))

    def get_temperature(self) -> float:
        data = self._read_data()  # prefetch the data once to save time
        for sensor_config in ("liq", "ext", "liq_amb", "ext_amb"):
            val = self.read_settings(data)[f"usr_temp_sp_{sensor_config}"]
            if val:
                return val

    def set_temperature(
        self,
        temp: float,
        sensor_config: Literal["liq", "ext", "liq_amb", "ext_amb"] = "liq",
    ) -> None:
        if sensor_config not in {"liq", "ext", "liq_amb", "ext_amb"}:
            raise ValueError(f"sensor_config={sensor_config} is not a valid option")
        self.update_settings(**{f"usr_temp_sp_{sensor_config}": temp})

    def measure_temperature(self, sensor: Literal["liq", "ext", "amb"] = "liq"):
        try:
            return self.read_settings()[f"mon_{sensor}_temp"]
        except KeyError:
            raise ValueError(f"sensor={sensor} is not a valid option")

    def get_units(self) -> str:
        units_val = self.read_settings()["units"]
        return "C" if units_val == 1 else "F"

    def set_units(self, unit: Literal["C", "F"]):
        if unit not in {"C", "F"}:
            raise ValueError(f"unit={unit} is not a valid option")
        units_val = 1 if unit == "C" else 2
        self.update_settings(units=units_val)
