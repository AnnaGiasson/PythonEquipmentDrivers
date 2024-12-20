from pythonequipmentdrivers.core import VisaResource


class HP_6632A(VisaResource):
    """
    HP_6632A(address)

    address : str, address of the connected power supply

    object for accessing basic functionallity of the Hewlett Packard 6632A
    DC supply
    """

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
