from ..core import VisaResource


class Keysight_RP7900(VisaResource):
    def __init__(self, address: str, **kwargs) -> None:
        super().__init__(address, **kwargs)

        # check valid connection
        is_7935a = ('keysight' in self.idn.lower()) and ('rp79' in self.idn.lower())
        if not is_7935a:
            raise ValueError(
                f"Instrument at {address} is not a Keysight 7935A Power Supply"
            )
            
    def set_state(self, state: bool) -> None:
        """
        set_state(state)

        Enables/disables the output of the supply

        Args:
            state (bool): Supply state (True == enabled, False == disabled)
        """

        self.write_resource(f"OUTP:STAT {1 if state else 0}")

    def get_state(self) -> bool:
        """
        get_state()

        Retrives the current state of the output of the supply.

        Returns:
            bool: Supply state (True == enabled, False == disabled)
        """

        response = self.query_resource("OUTP:STAT?").rstrip("\n")
        return int(response) == 1

    def on(self) -> None:
        """
        on()

        Enables the relay for the power supply's output equivalent to
        set_state(True).
        """

        self.set_state(True)

    def off(self) -> None:
        """
        off()

        Disables the relay for the power supply's output equivalent to
        set_state(False).
        """

        self.set_state(False)

    def toggle(self) -> None:
        """
        toggle()

        reverses the current state of the power supply's output relay
        """

        self.set_state(self.get_state() ^ True)
        
    def set_priority_to_voltage(self) -> None:
        """
        set_priority_to_voltage()

        Sets the control priority of the power supply to voltage mode.
        In voltage mode the power supply will adjust current to maintain
        the set voltage level up to the current limit.
        """

        self.write_resource("SOUR:FUNC VOLT")

    def set_voltage(self, voltage: float) -> None:
        """
        set_voltage(voltage)

        voltage: float or int, amplitude to set output to in Vdc

        set the output voltage setpoint specified by "voltage"
        """

        self.write_resource(f"SOUR:VOLT:LEV {voltage}")

    def get_voltage(self) -> float:
        """
        get_voltage()

        gets the output voltage setpoint in Vdc

        returns: float
        """

        response = self.query_resource("SOUR:VOLT:LEV?")
        return float(response)
    
    def set_priority_to_current(self) -> None:
        """
        set_priority_to_current()

        Sets the control priority of the power supply to current mode.
        In current mode the power supply will adjust voltage to maintain
        the set current level up to the voltage limit.
        """

        self.write_resource("SOUR:FUNC CURR")

    def set_current(self, current: float) -> None:
        """
        set_current(current)

        current: float/int, current limit setpoint in Adc

        sets the current limit setting for the power supply in Adc
        """

        self.write_resource(f"SOUR:CURR:LEV {current}")

    def get_current(self) -> float:
        """
        get_current()

        gets the current limit setting for the power supply in Adc

        returns: float
        """

        response = self.query_resource("SOUR:CURR:LEV?")
        return float(response)
    
    def set_current_limit(self, current: float) -> None:
        """
        set_current_limit(current)

        current: float, current limit in Adc

        Sets the positive current limit setpoint for the power supply's output in Adc.
        Only applies when the power supply is in voltage priority mode.
        """

        self.write_resource(f"SOUR:CURR:LIM {current}")
        
    def get_current_limit(self) -> float:
        """
        get_current_limit()

        returns: current_limit: float, current limit in Adc

        Returns the positive current limit setpoint for the power supply's output in Adc.
        """

        resp = self.query_resource("SOUR:CURR:LIM?")
        return float(resp)
    
    def set_voltage_limit(self, voltage: float) -> None:
        """
        set_voltage_limit(voltage)

        voltage: float, voltage limit in Vdc

        Sets the voltage setpoint limit for the power supply's output
        voltage in Vdc. This only applies when the power supply is in current
        priority mode.
        """

        self.write_resource(f"SOUR:VOLT:LIM {voltage}")

    def get_voltage_limit(self) -> float:
        """
        get_voltage_limit()

        returns: v_limit: float, voltage limit in Vdc

        Returns the voltage setpoint limit for the power supply's output
        voltage in Vdc. This level can only be set manually through the
        potentiometer on the front panel
        """

        resp = self.query_resource("SOUR:VOLT:PROT?")
        return float(resp)

    def set_ocp_state(self, state: bool) -> None:
        """
        set_ocp_state(state)

        Enables or Disables the Over-Current Protection of the supply's output.
        With OCP active the output will be shut off it the current level is
        exceeded.

        Args:
            state (bool): Whether or not Over-Current Protection is active
        """

        self.write_resource(f"SOUR:CURR:PROT:STATE {1 if state else 0}")

    def get_ocp_state(self) -> bool:
        """
        get_ocp_state()

        Returns whether the Over-Current Protection of the supply is Enabled
        or Disabled. With OCP active the output will be shut off it the current
        level is exceeded.

        Args:
            state (bool): Whether or not Over-Current Protection is active
        """
        response = self.query_resource("SOUR:CURR:PROT:STATE?")
        return int(response) == 1

    def measure_voltage(self) -> float:
        """
        measure_voltage()

        returns measurement of the dc voltage of the power supply in Vdc

        returns: float
        """

        response = self.query_resource("MEAS:VOLT?")
        return float(response)

    def measure_current(self) -> float:
        """
        measure_current()

        returns measurement of the dc current of the power supply in Adc
        returns: float
        """

        response = self.query_resource("MEAS:CURR?")
        return float(response)