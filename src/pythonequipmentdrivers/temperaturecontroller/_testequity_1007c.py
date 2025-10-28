# The following functions were taken from the F4_python_gpib.py script created by Eric Schonning at TestEquity LLC and modified slightly:
# check_ESR
# check_Modbus_error

from enum import Enum
from ..core import VisaResource


class TestEquity_1007C(VisaResource):
    
    def __init__(self, address: str, **kwargs):
        super().__init__(address, **kwargs)
        
        # check this is the correct device
        is_1007c = ('ics' in self.idn.lower())
        if not is_1007c:
            raise ValueError(
                f"Instrument at {address} is not a TestEquity 1007C Temperature Controller"
            )
        check_error = self.check_ESR()
        if check_error:
            print(check_error)
            
        self.decimal = int(self.query_resource(f"R? {self.Registers.GET_DECIMAL.value}, 1"))  # need to read the decimal point first before setting and reading temperatures
    
    def check_ESR(self) -> str | None:  # see table 3-1 in ICS 4899A manual, ESR bit definitions
        esr = int(self.query_resource("*ESR?"))
        message = None
        if esr == 0:
            return None
        if esr != 0:
            message = f"ESR = {esr}"
        if esr & 4:
            message = "Read Operation Error"
        if esr & 8:
            message = "Flash Data Corrupted"
        if esr & 16:
            message = "Execution Error"
        if esr & 32:
            message = "Command Error"
        if esr & 64:
            message = self.check_Modbus_error()
        if esr & 128:
            message = "Power cycle event"
        return message
    
    def check_Modbus_error(self) -> str:   # see table 3-5 in ICS 4899A manual, E? value returns
        e = int(self.query_resource("E?"))
        message = None
        if e == 1:
            message = "Illegal Function"
        elif e == 2:
            message = "Illegal Register Address"
        elif e == 3:
            message = "Illegal Data Value"
        elif e == 4:
            message = "Error processing request, possible invalid address or value"
        elif e == 100:
            message = "CRC Error"
        elif e == 101:
            message = "Timeout Error"
        elif e >= 200:
            e = e - 200
            message = f"Partial or Corrupted Message, bytes received = {e}"
        else:
            message = f"E? = {e}"
        return "Modbus Error, " + message
    
    class Registers(Enum):
        CHAMBER_TEMP = 100
        CURRENT_SET_TEMP = 300
        SP1_LOW_LIMIT = 602
        SP1_HIGH_LIMIT = 603
        GET_DECIMAL = 606
        CHAMBER_ON_OFF = 2000
        
    def GetBaudRate(self) -> str:
        return self.query_resource(":SYST:COMM:SER:BAUD?")
        
    def RunChamber(self) -> None:
        """
        This doesn't work with our chamber, there is no connection to the EVENT1 Digital Output.  Should work if the chamber being used has it connected.
        """
        self.write_resource(f"W {self.Registers.CHAMBER_ON_OFF.value}, 1")  # Turn chamber on
        
    def StopChamber(self) -> None:
        """
        This doesn't work with our chamber, there is no connection to the EVENT1 Digital Output.  Should work if the chamber being used has it connected.
        """
        self.write_resource(f"W {self.Registers.CHAMBER_ON_OFF.value}, 0")  # Turn chamber off

    def SetTemp(self, temp: float) -> None:
        value = int(temp * (10 ** self.decimal))
        self.write_resource(f"W {self.Registers.CURRENT_SET_TEMP.value}, {value}")
        
    def GetTempSetpoint(self) -> float:
        raw_value = int(self.query_resource(f"R? {self.Registers.CURRENT_SET_TEMP.value}, 1"))
        return float(raw_value / (10 ** self.decimal))
    
    def GetTempMeasurement(self) -> float:
        raw_value = int(self.query_resource(f"R? {self.Registers.CHAMBER_TEMP.value}, 1"))
        return float(raw_value / (10 ** self.decimal))
    
    def SetLimits(self, low_limit: float, high_limit: float) -> None:
        raw_low = int(low_limit * (10 ** self.decimal))
        raw_high = int(high_limit * (10 ** self.decimal))
        self.write_resource(f"W {self.Registers.SP1_LOW_LIMIT.value}, {raw_low}")
        self.write_resource(f"W {self.Registers.SP1_HIGH_LIMIT.value}, {raw_high}")
    
    def GetLimits(self) -> tuple[float, float]:
        raw_low = int(self.query_resource(f"R? {self.Registers.SP1_LOW_LIMIT.value}, 1"))
        raw_high = int(self.query_resource(f"R? {self.Registers.SP1_HIGH_LIMIT.value}, 1"))
        low_limit = float(raw_low / (10 ** self.decimal))
        high_limit = float(raw_high / (10 ** self.decimal))
        return (low_limit, high_limit)
    
    def Close(self):
        self.close_resource()