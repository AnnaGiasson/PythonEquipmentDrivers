import logging
from dataclasses import dataclass
from time import time
from typing import Literal

from ..core import VisaResource

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Register:
    offset: int
    n_bytes: int
    m: int
    r: int
    b: int

    def float_to_mrb(self, value: float) -> int:
        n = round((self.m * value + self.b) * 10**self.r)
        return n

    def mrb_to_float(self, n: int) -> float:
        value = (1 / self.m) * (n * 10 ** (-1 * self.r) - self.b)
        return value


class Koolance_EXC900(VisaResource):
    """
    Koolance_EXC900(address)

    address : str, address of the connected device

    object for accessing basic functionality of the Koolance_EXC900 Chiller
    """

    DATA_REGISTER_MAP = {
        # monitoring data
        "mon_liq_temp": Register(2, n_bytes=2, m=10, r=0, b=2000),
        "mon_ext_temp": Register(4, n_bytes=2, m=10, r=0, b=2000),
        "mon_amb_temp": Register(6, n_bytes=2, m=10, r=0, b=2000),
        "mon_fan_rpm": Register(8, n_bytes=2, m=1, r=0, b=0),
        "mon_pump_rpm": Register(10, n_bytes=2, m=1, r=0, b=0),
        "mon_flow_meter": Register(12, n_bytes=2, m=1, r=1, b=0),
        # user mode settings
        "usr_temp_sp_liq": Register(14, n_bytes=2, m=1, r=0, b=500),
        "usr_temp_sp_ext": Register(14, n_bytes=2, m=1, r=0, b=1000),
        "usr_temp_sp_liq_amb": Register(14, n_bytes=2, m=1, r=0, b=1500),
        "usr_temp_sp_ext_amb": Register(14, n_bytes=2, m=1, r=0, b=2000),
        "usr_pump_sp": Register(16, n_bytes=2, m=1, r=0, b=0),
        "usr_flow_sp": Register(18, n_bytes=2, m=1, r=0, b=0),
        # units
        "units": Register(44, n_bytes=2, m=1, r=0, b=0),
    }

    def __init__(self, address: str, **kwargs):
        super().__init__(address, **kwargs)

        self._last_read_data: bytes = None
        self._last_read_data_time = None
        self._read_data_max_age = kwargs.get("max_read_data_age", 1.0)

    def _is_cached_data_stale(self) -> bool:

        if self._last_read_data_time is None:
            return True

        time_since_last_read = time() - self._last_read_data_time
        return time_since_last_read > self._read_data_max_age

    def _read_data(self) -> bytes:
        """
        Read binary data from the device and return bytes
        Since the serial commands are slow, the read data is buffered and only
        refreshed when the age of the buffered data > _read_data_max_age or
        when a write has occured.
        """
        DATA_REQUEST_COMMAND = bytes([0xCF, 0x01, 0x08])

        if self._is_cached_data_stale():

            self.write_resource_raw(DATA_REQUEST_COMMAND)

            self._last_read_data = self.read_resource_bytes(51)
            self._last_read_data_time = time()

            logger.debug("fetched new data from the device")

        return self._last_read_data

    def _write_data(self, data: bytes) -> None:
        """Write bytes to the device"""

        self._last_read_data_time = None  # trigger a refresh on the next read
        self.write_resource_raw(data)

    def read_settings(self) -> dict[str, float]:
        """
        read_settings()

        Read data from the device and output values of supported parameters
        in a "key: value" format

        Returns:
            dict[str, float]: dict of parameter names and their values
        """

        data = self._read_data()
        out_dict: dict[str, float] = {}

        for name, reg in self.DATA_REGISTER_MAP.items():
            value = data[reg.offset : reg.offset + reg.n_bytes]
            n = int.from_bytes(value, byteorder="big")

            out_dict[name] = reg.mrb_to_float(n)

        return out_dict

    def update_settings(self, **kwargs) -> None:
        """
        update_settings(**kwargs)

        Update settings to the values provided leaving other parameters
        unchanged. Using this method is the most efficient way to update
        several parameters at once.

        args:
            kwargs: Each kwarg should correspond to a writeable supported
            parameter name as defined in Koolance_EXC900.DATA_REGISTER_MAP
            eg:
            update_settings(usr_temp_sp_liq=10) - set the setpoint to 10 deg
            update_settings(units=1) - set the units used to C
        """

        data = bytearray(self._read_data())

        for name, value in kwargs.items():

            try:
                reg = self.DATA_REGISTER_MAP[name.lower()]
            except KeyError:
                raise TypeError(f"{name} is not a valid setting name")

            n = reg.float_to_mrb(value)

            val_bytes = n.to_bytes(reg.n_bytes, "big")
            data[reg.offset : reg.offset + reg.n_bytes] = val_bytes

        data[0:2] = [0xCF, 0x04]  # configure the command bytes for a write
        data[2:14] = 12 * [0]  # set read-only locations to 0
        data[50] = sum(data[:50]) % 0x64  # compute the checksum
        self._write_data(bytes(data))

    def get_temperature(self) -> float:
        """
        get_temperature()

        Returns the current setpoint of the device. Attempts to descern

        Returns:
            float: current setpoint of the device
        """

        current_settings = self.read_settings()

        for sensor_config in ("liq", "ext", "liq_amb", "ext_amb"):
            val = current_settings[f"usr_temp_sp_{sensor_config}"]
            if val > 0.0:
                return val

    def set_temperature(
        self,
        temp: float,
        sensor_config: str = Literal["liq", "ext"],
        use_ambient: bool = False,
    ) -> None:
        """
        set_temperature(temp, sensor_config="liq", use_ambient=False)

        Args:
            temp (float): Temperature setpoint
            sensor_config (Literal["liq", "ext"]):
                Temperature sensor configuration to use. Defaults to "liq".
            use_ambient (bool): whether or not to use the ambient sensor for
                temperature setting. Defaults to False.
        """
        if sensor_config not in {"liq", "ext"}:  # , "liq_amb", "ext_amb"}:
            raise ValueError(f"sensor_config={sensor_config} is not a valid option")

        sensor_setting = f"usr_temp_sp_{sensor_config}"
        if use_ambient:
            sensor_setting += "_amb"

        self.update_settings(**{sensor_setting: temp})

    def measure_temperature(
        self, sensor: Literal["liq", "ext", "amb"] = "liq"
    ) -> float:
        """
        measure_temperature()

        Return the measured temperature from the device

        Args:
            sensor Literal['liq', 'ext', 'amb']: Optionally specify which
            sensor to return the measurement of. Defaults to "liq".

        Returns:
            float: measured temperature
        """

        try:
            return self.read_settings()[f"mon_{sensor}_temp"]
        except KeyError:
            raise ValueError(f"sensor={sensor} is not a valid option")

    def get_units(self) -> Literal["C", "F"]:
        """
        get_units()

        Return the units setting of the device

        Returns:
            Literal['C', 'F']: temperature unit, either Celcuis 'C', or
                Fahrenheit 'F'
        """

        units_val = self.read_settings()["units"]
        return "C" if units_val == 1 else "F"

    def set_units(self, unit: Literal["C", "F"]) -> None:
        """
        set_units(unit)

        Set the units used by the device

        Args:
            unit (Literal['C', 'F']): temperature unit, either Celcuis 'C', or
                Fahrenheit 'F'
        """

        if unit not in {"C", "F"}:
            raise ValueError(f"unit={unit} is not a valid option")

        self.update_settings(units=(1 if unit == "C" else 2))
