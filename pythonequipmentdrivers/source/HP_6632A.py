from pythonequipmentdrivers import Scpi_Instrument as _Scpi_Instrument
from time import sleep as _sleep
import numpy as _np


class HP_6632A(_Scpi_Instrument):
    """
    HP_6632A(address)

    address : str, address of the connected power supply

    object for accessing basic functionallity of the Hewlett Packard 6632A
    DC supply
    """

    def __init__(self, address):
        super().__init__(address)
        return

    def set_state(self, state):
        """
        set_state(state)

        state: int, 1 or 0 for on and off respectively

        enables/disables the state for the power supply's output
        """

        self.instrument.write(f"OUTP:STAT {state}")
        return

    def get_state(self):
        """
        get_state()

        returns the current state of the output relay,

        returns: int
        1: enabled, 0: disabled
        """

        response = self.instrument.query("OUTP:STAT?").rstrip('\n')
        return int(response)

    def on(self):
        """
        on()

        enables the relay for the power supply's output
        equivalent to set_state(1)
        """

        self.set_state(1)
        return

    def off(self):
        """
        off()

        disables the relay for the power supply's output
        equivalent to set_state(0)
        """

        self.set_state(0)
        return

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
        return

    def set_voltage(self, voltage):
        """
        set_voltage(voltage)

        voltage: float or int, amplitude to set output to in Vdc

        set the output voltage setpoint specified by "voltage"
        """

        self.instrument.write(f"SOUR:VOLT:LEV {voltage}")
        return

    def get_voltage(self):
        """
        get_voltage()

        gets the output voltage setpoint in Vdc

        returns: float
        """

        response = self.instrument.query("SOUR:VOLT:LEV?")
        return float(response)

    def set_current(self, current):
        """
        set_current(current)

        current: float/int, current limit setpoint in Adc

        sets the current limit setting for the power supply in Adc
        """
        self.instrument.write(f"SOUR:CURR:LEV {current}")
        return

    def get_current(self):
        """
        get_current()

        gets the current limit setting for the power supply in Adc

        returns: float
        """

        response = self.instrument.query("SOUR:CURR:LEV?")
        return float(response)

    def get_voltage_limit(self):
        """
        get_voltage_limit()

        returns: v_limit: float, voltage limit in Vdc

        Returns the voltage setpoint limit for the power supply's output
        voltage in Vdc. This level can only be set manually through the
        potentiometer on the front panel
        """

        resp = self.instrument.query('SOUR:VOLT:PROT?')
        return float(resp)

    def set_ocp_state(self, state):
        """
        set_ocp_state(state)

        Enables or Disables the Over-Current Protection of the supply's output.
        With OCP active the output will be shut off it the current level is
        exceeded.

        Args:
            state (bool): Whether or not Over-Current Protection is active
        """

        state = 1 if bool(state) else 0
        self.instrument.write(f'SOUR:CURR:PROT:STATE {state}')
        return None

    def get_ocp_state(self):
        """
        get_ocp_state()

        Returns whether the Over-Current Protection of the supply is Enabled
        or Disabled. With OCP active the output will be shut off it the current
        level is exceeded.

        Args:
            state (bool): Whether or not Over-Current Protection is active
        """
        response = self.instrument.query('SOUR:CURR:PROT:STATE?')
        return int(response)

    def measure_voltage(self):
        """
        measure_voltage()

        returns measurement of the dc voltage of the power supply in Vdc

        returns: float
        """

        response = self.instrument.query("MEAS:VOLT?")
        return float(response)

    def measure_current(self):
        """
        measure_current()

        returns measurement of the dc current of the power supply in Adc
        returns: float
        """

        response = self.instrument.query("MEAS:CURR?")
        return float(response)

    def pulse(self, level, duration):
        """
        pulse(level, duration)

        level: float/int, voltage level of "high" state of the pulse in Volts
        duration: float/int, duration of the "high" state of the pulse in
                  seconds

        generates a square pulse with height and duration specified by level
        and duration. will start and return to the previous voltage level set
        on the source before the execution of pulse(). level can be less than
        or greater than the previous voltage setpoint
        """

        start_level = self.get_voltage()
        self.set_voltage(level)
        _sleep(duration)
        self.set_voltage(start_level)
        return

    def ramp(self, start, stop, n=100, dt=0.01):
        """
        ramp(start, stop, n=100, dt=0.01)

        start: float/int, starting voltage setpoint of the ramp in Vdc
        stop: float/int, ending voltage setpoint of the ramp in Vdc
        n (optional): int, number of points in the ramp between start and stop
            default is 100
        dt (optional): float/int, time between changes in the value of the
                       setpoint in seconds. default is 0.01 sec

        generates a linear ramp on the sources voltage specified by the
        parameters start, stop, n, and dt. output of the source should be
        enabled before executing this command. contrary to what this
        documentation may imply, start can be higher than stop or vise-versa.
        minimum dt is limited by the communication speed of the interface used
        to communicate with this device and the connected electrical network.
        """

        for i in _np.linspace(start, stop, int(n)):
            self.set_voltage(i)
            _sleep(dt)
        return

    def slew(self, start, stop, n=100, dt=0.01, dwell=0):
        """
        slew(start, stop, n=100, dt=0.01, dwell=0)

        start: float/int, "low" voltage setpoint of the ramp in Vdc
        stop: float/int, "high" voltage setpoint of the ramp in Vdc
        n (optional): int, number of points in the ramp between start and stop
            default is 100
        dt (optional): float/int, time between changes in the value of the
                       setpoint in seconds. default is 0.01 sec
        dwell (optional): float/int, time to dwell at the "stop" value before
                          the ramp back to "start". default is 0 sec (no dwell)

        generates a triangular waveform on the sources voltage specified by the
        parameters start, stop, n, and dt. optionally, a dwell acan be added at
        the top of the waveform to create a trapezoidal voltage shape. The
        output of the load should be enabled before executing this command.
        contrary to what this documentation may imply, start can be higher than
        stop or vise-versa. minimum dt is limited by the communication speed of
        the interface used to communicate with this device and the connected
        electrical network.
        """

        self.ramp(start, stop, n=int(n/2), dt=dt)
        _sleep(dwell)
        self.ramp(stop, start, n=int(n/2), dt=dt)
        return


if __name__ == '__main__':
    pass
