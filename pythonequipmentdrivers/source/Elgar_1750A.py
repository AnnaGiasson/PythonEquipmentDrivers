from typing import Union
from pythonequipmentdrivers import VisaResource
from time import sleep


class Elgar_1750A(VisaResource):
    """
    Elgar_1750A(address)

    address : str, address of the connected power supply

    object for accessing basic functionallity of the Elgar_1750 AC supply

    Programmers Manual:
    http://www.programmablepower.com/products/SW/downloads/SW_A_and_AE_Series_SCPI_Programing_Manual_M162000-03-RvF.PDF
    """

    def set_state(self, state: bool) -> None:
        """
        set_state(state)

        Enables/disables the output of the supply

        Args:
            state (bool): Supply state (True == enabled, False == disabled)
        """

        self.instrument.write(f'OUTP:STAT {1 if state else 0}')

    def get_state(self) -> bool:
        """
        get_state()

        Retrives the current state of the output of the supply.

        Returns:
            bool: Supply state (True == enabled, False == disabled)
        """

        response = self.instrument.query('OUTP:STAT?')
        return ('1' in response)

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

    def toggle(self, return_state=False) -> Union[None, bool]:
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

    def set_current(self, current):
        self.instrument.write("SOUR:CURR {}".format(current))
        return None

    def get_current(self):
        return float(self.instrument.query("SOUR:CURR?"))

    def set_frequency(self, frequency):
        self.instrument.write("SOUR:FREQ {}".format(frequency))
        return None

    def get_frequency(self):
        return float(self.instrument.query("SOUR:FREQ?"))

    def get_phase(self):
        return float(self.instrument.query("SOUR:PHAS?"))

    def set_phase(self, phase):  # phase in deg
        # wraps phase around 0 to 360 deg
        self.instrument.write(f"SOUR:PHAS {phase % 360}")
        return None

    def set_voltage(self, voltage, change_range=False):
        if change_range:
            self.auto_range(voltage)
        self.instrument.write(f"SOUR:VOLT {voltage}")
        return None

    def get_voltage(self):
        return float(self.instrument.query("SOUR:VOLT?"))

    def set_voltage_limit(self, voltage_limit):
        self.instrument.write(f"SOUR:VOLT:PROT {voltage_limit}")
        return None

    def get_voltage_limit(self):
        return float(self.instrument.query("SOUR:VOLT:PROT?"))

    def set_voltage_range(self, voltage_range):
        self.instrument.write(f"SOUR:VOLT:RANG {voltage_range}")
        return None

    def get_voltage_range(self):
        return float(self.instrument.query("SOUR:VOLT:RANG?"))

    def generate_sequence(self, conditions, run=False):
        """
        conditions should be a list of dictionaries containing the conditions
        of each segment
        """

        # ----- Create Segment 0 -----
        # Clear sequence scratchpad. Take advantage of defaults and only
        # set changed params
        self.instrument.write('Edit:seq:clear')

        for index, segment in enumerate(conditions):
            if not('dur' in segment.keys() or 'cycl' in segment.keys()):
                return False

            self.instrument.write(f'Edit:seq:seg {index}')
            for key in segment.keys():
                command_str = f'Edit:seq:{key} {f"{segment[key]:3.1f}"}'
                self.instrument.write(command_str)

            if not(index + 1 == len(conditions)):
                # Create segment 1. Segment pointer is automatically
                # incremented to seg 1.
                self.instrument.write('Edit:seq:insert {}'.format(index + 1))
                sleep(0.1)

        # ----- setup sequence execution parameters -----
        # execute sequence once and stop
        self.instrument.write('Sour:seq:mode:run single')
        # set output voltage to 0 when seq stops
        self.instrument.write('Sour:seq:mode:stop ZERO')
        # load seq scratchpad
        self.instrument.write('Sour:seq:load "SCRATCH"')

        if run:
            self.on()
            sleep(1)
            self.instrument.write('Source:seq run')  # execute sequence

        return True

    def auto_range(self, voltage: float) -> None:
        if voltage > 156:
            self.set_voltage_range(1)
            self.set_voltage_limit(510)
            self.set_current(5)
        else:
            self.set_voltage_range(0)
            self.set_voltage_limit(255)
            self.set_current(13)


if __name__ == '__main__':
    pass
