from pythonequipmentdrivers import VisaResource
from typing import Union


class Intepro_PSI9000(VisaResource):
    """
    note: with this supply, the device must be locked before it will respond to
          commands
    manual:
    https://www.inteproate.com/wp-content/uploads/2016/11/Intepro-ModBus-SCPI-User-Manual-A4-new-edits-6_2017.pdf
    """

    def __init__(self, address, **kwargs) -> None:
        super().__init__(address, **kwargs)
        self.set_lock(True)

    def __del__(self) -> None:
        if hasattr(self, 'instrument'):
            self.set_lock(False)
        super().__del__()

    def set_lock(self, state: bool):
        self.instrument.write(f"SYST:LOCK {1 if state else 0}")

    def get_lock(self) -> True:
        query = self.instrument.query("SYST:LOCK:OWN?")
        if query.strip('\n') == 'REMOTE':
            return True
        return False

    def set_state(self, state: bool) -> None:
        """
        set_state(state)

        Enables/disables the output of the supply

        Args:
            state (bool): Supply state (True == enabled, False == disabled)
        """

        self.instrument.write(f"OUTP {1 if state else 0}")

    def get_state(self) -> bool:
        """
        get_state()

        Retrives the current state of the output of the supply.

        Returns:
            bool: Supply state (True == enabled, False == disabled)
        """

        query = self.instrument.query("OUTP?")
        if query.strip('\n') == "ON":
            return True
        return False

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

    def toggle(self, return_state: bool = False) -> Union[None, bool]:
        """
        toggle(return_state=False)

        Reverses the current state of the Supply's output
        If return_state = True the boolean state of the supply after toggle()
        is executed will be returned.

        Args:
            return_state (bool, optional): Whether or not to return the state
                of the supply after changing its state. Defaults to False.

        Returns:
            Union[None, bool]: If return_state == True returns the Supply state
                (True == enabled, False == disabled), else returns None
        """

        self.set_state(self.get_state() ^ True)

        if return_state:
            return self.get_state()

    def set_voltage(self, voltage):
        self.instrument.write(f"VOLT {voltage}")
        return None

    def get_voltage(self):
        return float(self.instrument.query("VOLT?").strip("V\n"))

    def set_current(self, current):
        self.instrument.write(f"CURR {current}")
        return None

    def get_current(self):
        return float(self.instrument.query("CURR?").strip("A\n"))

    def set_power(self, power):
        self.instrument.write(f"POW {power}")
        return None

    def get_power(self):
        return float(self.instrument.query("POW?").strip("W\n"))

    def measure_voltage(self):
        return float(self.instrument.query("MEAS:VOLT?").strip("V\n"))

    def measure_current(self):
        return float(self.instrument.query("MEAS:CURR?").strip("A\n"))

    def measure_power(self):
        return float(self.instrument.query("MEAS:POW?").strip("W\n"))

    def measure_array(self):
        query = self.instrument.query("MEAS:ARR?").strip('\n')
        v, i, p = query.split(',')

        v = float(v.strip(' V'))
        i = float(i.strip(' A'))
        p = float(p.strip(' W'))

        return v, i, p

    def set_ovp(self, voltage):
        self.instrument.write(f"SOUR:VOLT:PROT {voltage}")
        return None

    def get_ovp(self):
        return float(self.instrument.query("SOUR:VOLT:PROT?").strip("V\n"))

    def set_ocp(self, current):
        self.instrument.write(f"SOUR:CURR:PROT {current}")
        return None

    def get_ocp(self):
        return float(self.instrument.query("SOUR:CURR:PROT?").strip("A\n"))

    def set_opp(self, power):
        self.instrument.write(f"SOUR:POW:PROT {power}")
        return None

    def get_opp(self):
        return float(self.instrument.query("SOUR:POW:PROT?").strip("W\n"))
