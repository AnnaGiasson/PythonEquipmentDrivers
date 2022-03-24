import logging
from time import time
from pythonequipmentdrivers import Scpi_Instrument

logger = logging.getLogger(__name__)


class Koolance_EXC900(Scpi_Instrument):
    """
    Koolance_EXC900(address)

    address : str, address of the connected device

    object for accessing basic functionality of the Koolance_EXC900 Chiller
    """

    DATA_REGISTER_MAP = {
        # kwarg name, offset, width, m, r, b
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
        self._last_read_data: bytes = None
        self._last_read_data_time = None
        self._read_data_max_age = kwargs.get("max_read_data_age", 1.0)

    def _read_data(self) -> bytes:
        """
        Read binary data from the device and return bytes
        Since the serial commands are slow, the read data is buffered and only
        refreshed when the age of the buffered data > _read_data_max_age or
        when a write has occured.
        """
        DATA_REQUEST_COMMAND = [0xCF, 0x01, 0x08]
        if (
            self._last_read_data_time is None
            or (time() - self._last_read_data_time) > self._read_data_max_age
        ):
            logger.debug("fetched new data from the device")
            self._last_read_data_time = time()
            self.instrument.write_raw(bytes(DATA_REQUEST_COMMAND))
            self._last_read_data = self.instrument.read_bytes(51)
        return self._last_read_data

    def _write_data(self, data: bytes) -> None:
        """Write bytes to the device"""
        self._last_read_data_time = None  # trigger a refresh on the next read
        self.instrument.write_raw(data)

    def read_settings(self) -> dict:
        """
        read_settings()

        Read data from the device and output values of supported parameters
        in a key: value format

        Returns:
            dict: dict of parameter name and the value
        """
        data = self._read_data()
        out_dict = {}
        for name, (offs, n_bytes, m, r, b) in self.DATA_REGISTER_MAP.items():
            selected = data[offs: offs + n_bytes]
            val = int.from_bytes(selected, "big")
            val = (1 / m) * (val * 10 ** (-1 * r) - b)
            out_dict[name] = val
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
                offs, n_bytes, m, r, b = self.DATA_REGISTER_MAP[name.lower()]
            except KeyError:
                raise TypeError(f"{name} is not a valid setting name")
            value = round((m * value + b) * 10 ** r)
            val_bytes = value.to_bytes(n_bytes, "big")
            data[offs: offs + n_bytes] = val_bytes

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
        for sensor_config in ("liq", "ext", "liq_amb", "ext_amb"):
            val = self.read_settings()[f"usr_temp_sp_{sensor_config}"]
            if val > 0.0:
                return val

    def set_temperature(
        self,
        temp: float,
        sensor_config: str = "liq",
    ) -> None:
        """
        set_temperature(temp)

        Args:
            temp (float): Temperature setpoint
            sensor_config ('liq', 'ext', 'liq_amb', 'ext_amb', optional):
            Temperature sensor configuration to use. Defaults to "liq".
        """
        if sensor_config not in {"liq", "ext", "liq_amb", "ext_amb"}:
            raise ValueError(
                f"sensor_config={sensor_config} is not a valid option")
        self.update_settings(**{f"usr_temp_sp_{sensor_config}": temp})

    def measure_temperature(
        self, sensor: str = "liq"
    ) -> float:
        """
        measure_temperature()

        Return the measured temperature from the device

        Args:
            sensor ('liq', 'ext', 'amb', optional): Optionally specify which
            sensor to return the measurement of. Defaults to "liq".

        Returns:
            float: measured temperature
        """
        try:
            return self.read_settings()[f"mon_{sensor}_temp"]
        except KeyError:
            raise ValueError(f"sensor={sensor} is not a valid option")

    def get_units(self) -> str:
        """
        get_units()

        Return the units setting of the device

        Returns:
            str: 'C' or 'F'
        """
        units_val = self.read_settings()["units"]
        return "C" if units_val == 1 else "F"

    def set_units(self, unit: str) -> None:
        """
        set_units(unit)

        Set the units used by the device

        Args:
            unit ('C', 'F')
        """
        if unit not in {"C", "F"}:
            raise ValueError(f"unit={unit} is not a valid option")
        units_val = 1 if unit == "C" else 2
        self.update_settings(units=units_val)
