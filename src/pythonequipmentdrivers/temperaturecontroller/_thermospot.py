from enum import Enum
from typing import Optional, Union
from ..core import VisaResource


class ThermoSpot(VisaResource):
    def __init__(self, address: str, **kwargs):
        super().__init__(address, **kwargs)

        # check this is the correct device
        is_thermospot = "intest" in self.idn.lower()
        if not is_thermospot:
            raise ValueError(
                f"Instrument at {address} is not a ThermoSpot Temperature Controller"
            )
    
    class StatusBits(Enum):
        SRQ_Enabled_Disabled: int = 0
        Buffer_75_Percent_Full: int = 1
        Buffer_Less_Than_50_Percent_Full: int = 2
        Interval_Complete: int = 3
        Set_Point_Reached: int = 4
        Controlling_Temperature: int = 5
        SRQ_Set: int = 6
        Error: int = 7
    
    class SetupParameters(Enum):
        """
        Enumeration of setup parameters for the ThermoSpot controller.
        """
        # BUG: Some parameters don't work with the SPA command as per manual, need to figure out why that is the case.  For example, Second_Probe_Type in the manual says that DUTK - DUTD are tied to 1-4 but when passed nothing changes.
        PID_Proportional_Term = {'param_id': 0, 'min': 1, 'max': 255, 'default': 5, 'type': int}
        Number_Of_Probes = {'param_id': 1, 'min': 1, 'max': 2, 'default': 2, 'type': int}
        Cold_Valve_Period = {'param_id': 2, 'min': 1, 'max': 10, 'default': 5, 'type': int}
        Baud_Rate = {'param_id': 3, 'options': [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200], 'default': 9600, 'type': int}
        Remote_Mode_Power_On_State = {'param_id': 4, 'options': ['Immediate', 'Program'], 'default': 'Program', 'type': str}
        # F5-F6 Reserved
        # F7 Tune Mode - not implemented
        RS232_Echo = {'param_id': 8, 'options': ['Enabled', 'Disabled'], 'default': 'Enabled', 'type': str}
        GPIB_Address = {'param_id': 9, 'min': 1, 'max': 30, 'default': 1, 'type': int}
        PID_Integral_Term = {'param_id': 10, 'min': 0, 'max': 2000, 'default': 128, 'type': int}
        PID_Differential_Term = {'param_id': 11, 'min': 0, 'max': 8000, 'default': 0, 'type': int}
        # F12-F13 Reserved
        Autostart = {'param_id': 14, 'options': ['On', 'Off'], 'default': 'Off', 'type': str}
        # F15-F16 Reserved
        Probe1_Uncorrected1 = {'param_id': 17, 'min': -60, 'max': 175, 'default': 0, 'type': float}
        Probe1_Corrected1 = {'param_id': 18, 'min': -60, 'max': 175, 'default': 0, 'type': float}
        Probe1_Uncorrected2 = {'param_id': 19, 'min': -60, 'max': 175, 'default': 100, 'type': float}
        Probe1_Corrected2 = {'param_id': 20, 'min': -60, 'max': 175, 'default': 100, 'type': float}
        Probe2_Uncorrected1 = {'param_id': 21, 'min': -60, 'max': 175, 'default': 0, 'type': float}
        Probe2_Corrected1 = {'param_id': 22, 'min': -60, 'max': 175, 'default': 0, 'type': float}
        Probe2_Uncorrected2 = {'param_id': 23, 'min': -60, 'max': 175, 'default': 100, 'type': float}
        Probe2_Corrected2 = {'param_id': 24, 'min': -60, 'max': 175, 'default': 100, 'type': float}
        ThermoSpot_Low_Limit = {'param_id': 25, 'min': -60, 'max': 175, 'default': -60.0, 'type': float}
        ThermoSpot_High_Limit = {'param_id': 26, 'min': -60, 'max': 175, 'default': 200.0, 'type': float}
        DUT_Low_Limit = {'param_id': 27, 'min': -60, 'max': 175, 'default': -50.0, 'type': float}
        DUT_High_Limit = {'param_id': 28, 'min': -60, 'max': 175, 'default': 200.0, 'type': float}
        DUT_Low_Diff_Limit = {'param_id': 29, 'min': 1.0, 'max': 300.0, 'default': 50, 'type': float}
        DUT_High_Diff_Limit = {'param_id': 30, 'min': 1.0, 'max': 300.0, 'default': 50, 'type': float}
        Settling_Band = {'param_id': 31, 'min': 0.1, 'max': 10, 'default': 0.8, 'type': float}
        Settling_Time = {'param_id': 32, 'min': 0, 'max': 59, 'default': 15, 'type': int}
        Minimum_Ramp = {'param_id': 33, 'min': 0, 'max': 500, 'default': 0.0, 'type': float}
        Thermal_Mass = {'param_id': 34, 'min': 1, 'max': 1000, 'default': 32, 'type': int}
        Second_Probe_Type = {'param_id': 35, 'options': ['DUTK', 'DUTR', 'DUTA', 'DUTD'], 'default': 'DUTK', 'type': str}
        # F36 Reserved
        Default_Ramp_Rate = {'param_id': 37, 'min': 0, 'max': 500, 'default': 0, 'type': float}
        Purge_Set_Point = {'param_id': 38, 'min': -20.0, 'max': 50.0, 'default': 35, 'type': float}
        Clear_At_Set_Point = {'param_id': 39, 'min': 0, 'max': 1, 'default': 0, 'type': int}
        Temperature_Control_Mode = {'param_id': 40, 'options': ['DUT', 'Normal'], 'default': 'DUT', 'type': str}
        # Network Parameters (F41-F43 are IP addresses - special handling needed)
        # IP_Address = {'param_id': 41, 'default': '0.0.0.0', 'type': str}
        # IP_Subnet_Mask = {'param_id': 42, 'default': '0.0.0.0', 'type': str}
        # IP_Default_Gateway = {'param_id': 43, 'default': '0.0.0.0', 'type': str}
        GPIB_Timeout = {'param_id': 44, 'min': 0, 'max': 120, 'default': 3, 'type': int}
        Analog_In_Low_Temp = {'param_id': 45, 'min': -250, 'max': 500, 'default': 0, 'type': float}
        Analog_In_High_Temp = {'param_id': 46, 'min': -250, 'max': 500, 'default': 100, 'type': float}
        Temperature_Units = {'param_id': 47, 'options': ['Celsius', 'Fahrenheit'], 'default': 'Celsius', 'type': str}
        DUT_Proportional_Term = {'param_id': 48, 'min': 0.1, 'max': 64.0, 'default': 6.0, 'type': float}
        DUT_Integral_Term = {'param_id': 49, 'min': 0.1, 'max': 64.0, 'default': 0.5, 'type': float}
        # F50-F51 Reserved
        Diode_Ideality_Factor = {'param_id': 52, 'min': 0.0, 'max': 1.250, 'default': 1.000, 'type': float}
        Diode_Resistance = {'param_id': 53, 'min': 0.0, 'max': 5.0, 'default': 0.000, 'type': float}
            
    def reset(self) -> None:
        self.write_resource("RST")
        
    def stop(self) -> None:
        self.write_resource("QU")
        
    def go_to_temp(self, temp: float) -> None:
        """
        Go to the specified temperature immediately.
        
        :param temp: Target temperature in Celsius
        :type temp: float
        """
        self.write_resource(f"GT {temp:.1f}")
        
    def set_f_parameters(self, parameter: SetupParameters, value: Optional[Union[int, float, str]] = None) -> None:
        """
        Set a specific parameter for the ThermoSpot controller.
        
        :param parameter: The parameter to set
        :type parameter: SetupParameters
        :param value: The value to set for the parameter, if left blank uses default for that parameter.
        :type value: Optional[Union[int, float, str]]
        """
        param_config = parameter.value
        param_id = param_config['param_id']
        
        # Use default value if none provided
        if value is None:
            value = param_config['default']
        
        # Validate based on whether it has options or min/max range
        if 'options' in param_config:
            if value not in param_config['options']:
                raise ValueError(
                    f"Parameter {parameter.name} must be one of {param_config['options']}, got {value}"
                )
        elif 'min' in param_config and 'max' in param_config:
            if not (param_config['min'] <= value <= param_config['max']):
                raise ValueError(
                    f"Parameter {parameter.name} must be between {param_config['min']} and {param_config['max']}, got {value}"
                )
        
        self.write_resource(f"SPA {param_id} {value}")
    
    def get_status_byte(self) -> dict[str, int]:
        data = self.query_resource("RSA").split()
        binary_value = format(int(data[1], 16), '08b')
        status_dict = {}
        for i in range(8):
            bit_value = int(binary_value[7-i])  # reverse index since LSB is rightmost
            for field_name, bit_position in self.StatusBits.__members__.items():
                if bit_position.value == i:
                    status_dict[field_name] = bit_value
                    break
        return status_dict
    
    def get_temp(self) -> dict[str, float]:
        data = self.query_resource("PTC")
        lines = data.strip().split('\r\n')
        temps = {line.split()[0]: float(line.split()[1]) 
                 for line in lines if len(line.split()) == 2}
        return temps
