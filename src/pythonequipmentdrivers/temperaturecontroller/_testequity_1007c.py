# The following functions were taken from the F4_python_gpib.py script created by Eric Schonning at TestEquity LLC and modified slightly:
# check_ESR
# check_Modbus_error

from dataclasses import dataclass

from ..core import VisaResource


@dataclass(frozen=True)
class Registers:
    CHAMBER_TEMP: int = 100
    CURRENT_SET_TEMP: int = 300
    SP1_LOW_LIMIT: int = 602
    SP1_HIGH_LIMIT: int = 603
    GET_DECIMAL: int = 606
    CHAMBER_ON_OFF: int = 2000


class TestEquity_1007C(VisaResource):

    def __init__(self, address: str, **kwargs):
        super().__init__(address, **kwargs)

        # check this is the correct device
        is_1007c = "ics" in self.idn.lower()
        if not is_1007c:
            raise ValueError(
                f"Instrument at {address} is not a TestEquity 1007C Temperature Controller"
            )
        check_error = self.check_esr()
        if check_error:
            print(check_error)

        self.exponent = int(
            self.query_resource(f"R? {Registers.GET_DECIMAL}, 1")
        )  # need to read the decimal point first before setting and reading temperatures

    def check_esr(
        self,
    ) -> list[str]:  # see table 3-1 in ICS 4899A manual, ESR bit definitions

        esr_register_value = int(self.query_resource("*ESR?"))

        status_flags = {
            2: "Read Operation Error",
            3: "Flash Data Corrupted",
            4: "Execution Error",
            5: "Command Error",
            6: "Modbus Error",
            7: "Power cycle event",
        }

        messages = []
        for bit, message in status_flags.items():
            if esr_register_value & (1 << bit):
                if bit == 6:
                    messages.extend(self.check_modbus_error())
                else:
                    messages.append(message)

        return messages

    def check_modbus_error(
        self,
    ) -> str | None:  # see table 3-5 in ICS 4899A manual, E? value returns
        modbus_error_value = int(self.query_resource("E?"))

        status_flags = {
            1: "Illegal Function",
            2: "Illegal Register Address",
            3: "Illegal Data Value",
            4: "Error processing request, possible invalid address or value",
            100: "CRC Error",
            101: "Timeout Error",
        }

        # edge cases
        if modbus_error_value == 0:
            return None
        elif modbus_error_value >= 200:
            modbus_error_value = modbus_error_value - 200
            return (
                f"Partial or Corrupted Message, bytes received = {modbus_error_value}"
            )

        # expected messages
        for key, message in status_flags.items():
            if modbus_error_value == key:
                return message
        else:
            return f"E? = {modbus_error_value}"  # unknown error

    def get_baud_rate(self) -> str:
        return self.query_resource(
            ":SYST:COMM:SER:BAUD?"
        )  # TODO: map to int values, need to check return format in manual

    def set_state(self, state: bool) -> None:
        """
        set_state(state)

        Updates the status of the chambers temperature control system.
        True --> ON
        False --> OFF

        Args:
            state (bool): Enable state of the temperature control system
        """
        self.write_resource(f"W {Registers.CHAMBER_ON_OFF}, {1 if state else 0}")

    def on(self) -> None:
        """
        on()

        Equivalent to set_state(True)
        """
        self.set_state(True)

    def off(self) -> None:
        """
        off()

        Equivalent to set_state(False)
        """
        self.set_state(False)

    # def run_chamber(self) -> None:
    #     """
    #     This doesn't work with our chamber, there is no connection to the EVENT1 Digital Output.  Should work if the chamber being used has it connected.
    #     """
    #     self.write_resource(f"W {Registers.CHAMBER_ON_OFF}, 1")  # Turn chamber on

    # def stop_chamber(self) -> None:
    #     """
    #     This doesn't work with our chamber, there is no connection to the EVENT1 Digital Output.  Should work if the chamber being used has it connected.
    #     """
    #     self.write_resource(f"W {Registers.CHAMBER_ON_OFF}, 0")  # Turn chamber off

    def set_temp(self, temp: float) -> None:
        value = int(temp * (10**self.exponent))
        self.write_resource(f"W {Registers.CURRENT_SET_TEMP}, {value}")

    def get_temp(self) -> float:
        raw_value = int(self.query_resource(f"R? {Registers.CURRENT_SET_TEMP}, 1"))
        return float(raw_value / (10**self.exponent))

    def measure_temp(self) -> float:
        raw_value = int(self.query_resource(f"R? {Registers.CHAMBER_TEMP}, 1"))
        return float(raw_value / (10**self.exponent))

    def set_limits(self, low_limit: float, high_limit: float) -> None:
        raw_low = int(low_limit * (10**self.exponent))
        raw_high = int(high_limit * (10**self.exponent))

        self.write_resource(f"W {Registers.SP1_LOW_LIMIT}, {raw_low}")
        self.write_resource(f"W {Registers.SP1_HIGH_LIMIT}, {raw_high}")

    def get_limits(self) -> tuple[float, float]:
        raw_low = int(self.query_resource(f"R? {Registers.SP1_LOW_LIMIT}, 1"))
        raw_high = int(self.query_resource(f"R? {Registers.SP1_HIGH_LIMIT}, 1"))

        low_limit = float(raw_low / (10**self.exponent))
        high_limit = float(raw_high / (10**self.exponent))

        return (low_limit, high_limit)
