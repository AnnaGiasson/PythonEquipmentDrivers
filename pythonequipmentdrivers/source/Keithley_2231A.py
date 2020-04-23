from pythonequipmentdrivers import Scpi_Instrument as _Scpi_Instrument
from time import sleep as _sleep
import numpy as _np


class Keithley_2231A(_Scpi_Instrument):
    """
    Keithley_2231A(address)

    address : str, address of the connected power supply

    object for accessing basic functionallity of the Keithley DC supply
    """

    def __init__(self, address):
        super().__init__(address)
        self.set_access_remote('remote')
        return

    def __del__(self):
        self.set_access_remote('local')
        super().__del__()

    def set_access_remote(self, mode):
        """
        set_access_remote(mode)

        mode: str, interface method either 'remote' or 'local'

        set access to the device inferface to 'remote' or 'local'
        """

        if mode.lower() == 'remote':
            self.instrument.write('SYSTem:RWLock')
        elif mode.lower() == 'local':
            self.instrument.write('SYSTem:LOCal')

        return

    def set_channel(self, channel):  # check
        """
        set_channel(channel)

        channel: int, index of the channel to control.
                 valid options are 1-3

        Selects the specified Channel to use for software control

        """

        self.instrument.write(f'INST:NSEL {channel}')
        return

    def get_channel(self):  # check
        """
        get_channel()

        Get current selected Channel

        returns: int
        """

        resp = self.instrument.query('INST:NSEL?')
        channel = int(resp)
        return channel

    def set_state(self, state, channel):  # check
        """
        set_state(state, channel)

        state: int, 1 or 0 for on and off respectively

        channel: int, index of the channel to control.
                 valid options are 1-3

        enables/disables the state for the power supply's output
        """

        self.set_channel(channel)
        self.instrument.write(f"CHAN:OUTP {state}")
        return

    def get_state(self, channel):  # check
        """
        get_state(channel)

        channel: int, index of the channel to control.
                 valid options are 1-3

        returns the current state of the output relay,

        returns: int
        1: enabled, 0: disabled
        """

        self.set_channel(channel)
        resp = self.instrument.query("CHAN:OUTP?").rstrip('\n')
        if resp != "ON":
            return 0
        return 1

    def on(self, channel):
        """
        on(channel)

        channel: int, index of the channel to control.
                 valid options are 1-3

        enables the relay for the power supply's output
        equivalent to set_state(1)
        """

        self.set_state(1, channel)
        return

    def off(self, channel):
        """
        off(channel)

        channel: int, index of the channel to control.
                 valid options are 1-3

        disables the relay for the power supply's output
        equivalent to set_state(0)
        """

        self.set_state(0, channel)
        return

    def toggle(self, channel, return_state=False):
        """
        toggle(return_state=False)

        return_state (optional): boolean, whether or not to return the state
        of the output relay.

        reverses the current state of the power supply's output relay

        if return_state = True the boolean state of the relay after toggle() is
        executed will be returned
        """

        # logic inverted so the default state is off
        if not self.get_state(channel):
            self.on(channel)
        else:
            self.off(channel)

        if return_state:
            return self.get_state(channel)
        return

    def set_voltage(self, voltage, channel):  # check
        """
        set_voltage(voltage)

        voltage: float or int, amplitude to set output to in Vdc

        channel: int, the index of the channel to set. Valid options are 1,2,3.

        set the output voltage setpoint of channel "channel" specified by
        "voltage"
        """

        self.set_channel(channel)
        self.instrument.write(f"SOUR:VOLT {voltage}")
        return

    def get_voltage(self, channel):  # check
        """
        get_voltage()

        channel: int, the index of the channel to set. Valid options are 1,2,3.

        gets the output voltage setpoint in Vdc

        returns: float
        """

        self.set_channel(channel)
        resp = self.instrument.query("SOUR:VOLT?")
        return float(resp)

    def set_current(self, current, channel):  # check
        """
        set_current(current)

        current: float/int, current limit setpoint in Adc

        channel: int, the index of the channel to set. Valid options are 1,2,3.

        sets the current limit setting for the power supply in Adc
        """

        self.set_channel(channel)
        self.instrument.write(f"SOUR:CURR {current}")
        return

    def get_current(self, channel):  # check
        """
        get_current()

        channel: int, the index of the channel to set. Valid options are 1,2,3.

        gets the current limit setting for the power supply in Adc

        returns: float
        """

        self.set_channel(channel)
        resp = self.instrument.query("SOUR:CURR?")
        return float(resp)

    def measure_voltage(self, channel):
        """
        measure_voltage()

        returns measurement of the output voltage of the specified channel in
        Vdc.

        returns: float
        """

        self.set_channel(channel)
        resp = self.instrument.query('MEAS:VOLT?')
        return float(resp)

    def measure_current(self, channel):
        """
        measure_current()

        returns measurement of the output current of the specified channel in
        Adc.

        returns: float
        """

        self.set_channel(channel)
        resp = self.instrument.query('MEAS:CURR?')
        return float(resp)

    def pulse(self, level, duration, channel):
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

        start_level = self.get_voltage(channel)
        self.set_voltage(level, channel)
        _sleep(duration)
        self.set_voltage(start_level, channel)
        return

    def ramp(self, start, stop, channel, n=100, dt=0.01):
        """
        ramp(start, stop, n=100, dt=0.01)

        start: float/int, starting voltage setpoint of the ramp in Vdc
        stop: float/int, ending voltage setpoint of the ramp in Vdc
        channel: int, the index of the channel to set. Valid options are 1,2,3.
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

        for v in _np.linspace(start, stop, int(n)):
            self.set_voltage(v, channel)
            _sleep(dt)
        return

    def slew(self, start, stop, channel, n=100, dt=0.01, dwell=0):
        """
        slew(start, stop, n=100, dt=0.01, dwell=0)

        start: float/int, "low" voltage setpoint of the ramp in Vdc
        stop: float/int, "high" voltage setpoint of the ramp in Vdc
        channel: int, the index of the channel to set. Valid options are 1,2,3.
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

        self.ramp(start, stop, channel, n=int(n/2), dt=dt)
        _sleep(dwell)
        self.ramp(stop, start, channel, n=int(n/2), dt=dt)
        return


if __name__ == '__main__':
    pass
