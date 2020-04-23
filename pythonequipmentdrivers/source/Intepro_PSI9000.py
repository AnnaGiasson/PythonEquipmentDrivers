from pythonequipmentdrivers import Scpi_Instrument as _Scpi_Instrument


class Intepro_PSI9000(_Scpi_Instrument):
    """
    note: with this supply, the device must be locked before it will respond to
          commands
    manual:
    https://www.inteproate.com/wp-content/uploads/2016/11/Intepro-ModBus-SCPI-User-Manual-A4-new-edits-6_2017.pdf
    """

    def __init__(self, address):
        super().__init__(address)
        return

    def __del__(self):
        self.set_lock(0)
        self.instrument.close()
        return

    def set_lock(self, state):
        self.instrument.write(f"SYST:LOCK {state}")
        return

    def get_lock(self):
        query = self.instrument.query("SYST:LOCK:OWN?")
        if query.strip('\n') == 'REMOTE':
            return 1
        return 0

    def set_state(self, state):
        self.instrument.write(f"OUTP {state}")
        return

    def get_state(self):
        query = self.instrument.query("OUTP?")
        if query.strip('\n') == "ON":
            return True
        return False

    def on(self):
        self.set_state(1)
        return

    def off(self):
        self.set_state(0)
        return

    def toggle(self, return_state=False):
        if not self.get_state():  # logic inverted so the default state is off
            self.on()
        else:
            self.off()

        if return_state:
            return self.get_state()
        return

    def set_voltage(self, voltage):
        self.instrument.write(f"VOLT {voltage}")
        return

    def get_voltage(self):
        return float(self.instrument.query("VOLT?").strip("V\n"))

    def set_current(self, current):
        self.instrument.write(f"CURR {current}")
        return

    def get_current(self):
        return float(self.instrument.query("CURR?").strip("A\n"))

    def set_power(self, power):
        self.instrument.write(f"POW {power}")
        return

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
        return

    def get_ovp(self):
        return float(self.instrument.query("SOUR:VOLT:PROT?").strip("V\n"))

    def set_ocp(self, current):
        self.instrument.write(f"SOUR:CURR:PROT {current}")
        return

    def get_ocp(self):
        return float(self.instrument.query("SOUR:CURR:PROT?").strip("A\n"))

    def set_opp(self, power):
        self.instrument.write(f"SOUR:POW:PROT {power}")
        return

    def get_opp(self):
        return float(self.instrument.query("SOUR:POW:PROT?").strip("W\n"))
