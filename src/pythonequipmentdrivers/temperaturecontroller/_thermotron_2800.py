"""
Created on Wed Feb 10 11:53:18 2021

@author: DS_TestStation
"""

from ..core import VisaResource


class Thermotron_2800(VisaResource):

    def __init__(self, address: str, **kwargs):
        super().__init__(address, **kwargs)
        self.write_resource(
            "LKS 1"
        )  # lock keyboard - should happen automatically, but we'll assert anyway... =)

    def __del__(self) -> None:
        self.write_resource("LKS 0")  # unlock keyboard before closing session
        super().__del__()

    def set_state(self, state: bool) -> None:
        """
        set_state(state)

        Updates the status of the chambers temperature control system.
        True --> ON
        False --> OFF

        Args:
            state (bool): Enable state of the temperature control system
        """
        self.write_resource("RM" if state else "S")

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
    #     self.write_resource("RM")     # Enter "Run Manual" state to follow single set point

    # def stop_chamber(self) -> None:
    #     self.write_resource("S")      # Stop chamber output

    def set_temp(self, temp: float) -> None:
        self.write_resource(f"LTS {temp:.1f}")

    def get_temp(self) -> float:
        return self._resource.query_ascii_values("DTS")[-1]

    def measure_temp(self) -> float:
        return self._resource.query_ascii_values("DTV")[-1]
