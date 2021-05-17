from pythonequipmentdrivers import Scpi_Instrument as _Scpi_Instrument
from time import sleep as _sleep


class Elgar_1750A(_Scpi_Instrument):
    """
    Elgar_1750A(address)

    address : str, address of the connected power supply

    object for accessing basic functionallity of the Elgar_1750 AC supply

    Programmers Manual:
    http://www.programmablepower.com/products/SW/downloads/SW_A_and_AE_Series_SCPI_Programing_Manual_M162000-03-RvF.PDF
    """

    def __init__(self, address, **kwargs):
        super().__init__(address, **kwargs)
        return None

    def set_state(self, state):
        """
        set_state(state)

        state: int, 1 or 0 for on and off respectively

        enables/disables the state for the power supply's output
        """

        self.instrument.write(f"OUTP:STAT {state}")
        return None

    def get_state(self):
        """
        get_state()

        returns the current state of the output relay,

        returns: int
        1: enabled, 0: disabled
        """

        response = int(self.instrument.query("OUTP:STAT?").rstrip('\n'))

        return response

    def on(self):
        """
        on()

        enables the relay for the power supply's output
        equivalent to set_state(1)
        """

        self.set_state(1)
        return None

    def off(self):
        """
        off()

        disables the relay for the power supply's output
        equivalent to set_state(0)
        """

        self.set_state(0)
        return None

    def toggle(self, return_state=False):
        """
        toggle(return_state=False)

        return_state (optional): boolean, whether or not to return the state
        of the output relay.

        reverses the current state of the power supply's output relay

        if return_state = True the boolean state of the relay after toggle() is
        executed will be returned
        """

        if not self.get_state():  # logic inverted so the default state is off
            self.on()
        else:
            self.off()

        if return_state:
            return self.get_state()
        return None

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
                _sleep(0.1)

        # ----- setup sequence execution parameters -----
        # execute sequence once and stop
        self.instrument.write('Sour:seq:mode:run single')
        # set output voltage to 0 when seq stops
        self.instrument.write('Sour:seq:mode:stop ZERO')
        # load seq scratchpad
        self.instrument.write('Sour:seq:load "SCRATCH"')

        if run:
            self.on()
            _sleep(1)
            self.instrument.write('Source:seq run')  # execute sequence

        return True

    def auto_range(self, vin):
        if vin > 156:
            self.set_voltage_range(1)
            self.set_voltage_limit(510)
            self.set_current(5)
        else:
            self.set_voltage_range(0)
            self.set_voltage_limit(255)
            self.set_current(13)
        return None


if __name__ == '__main__':
    pass
