from ..core import BareVisaResource


class SUN_ECO1(BareVisaResource):

    def __init__(self, address: str, **kwargs):
        super().__init__(address, **kwargs)
        self.idn = "SUN,EC01"

    def __del__(self) -> None:
        if hasattr(self, "_resource"):
            self._resource.close()

    def set_max_temp(self, temp: float) -> None:
        """
        set_max_temp(temp)

        Adjusts the max allowed tempertature limit for the chambers tempeature control system

        Args:
            temp (float): maximum allowed temperature, degrees Celcuis
        """
        self.write_resource(f"{temp} UTL")

    def set_temp(self, temp: float) -> None:
        """
        set_temp(temp)

        Updates the chambers temperature setpoint

        Args:
            temp (float): Temperature Setpoint in degrees Celcius
        """
        self.write_resource(f"{temp:.1f}C")

    def get_temp(self) -> float:
        """
        get_temp()

        Updates the chambers temperature setpoint

        Returns:
            float: Temperature setpoint in degrees Celcius
        """
        response = self.query_resource("C")
        return float(response)

    def measure_temp(self) -> float:
        """
        measure_temp()

        Fetches the measured temperature within the chamber using the embedded thermocouple

        Returns:
            float: measured temperature, degrees Celcuis
        """

        response = self.query_resource("T")
        return float(response)

    def set_state(self, state: bool) -> None:
        """
        set_state(state)

        Updates the status of the chambers temperature control system.
        True --> ON
        False --> OFF

        Args:
            state (bool): Enable state of the temperature control system
        """
        self.write_resource("ON" if state else "OFF")

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
