from typing import Union
from pythonequipmentdrivers import Scpi_Instrument
from time import sleep
import numpy as np


class Keithley_2231A(Scpi_Instrument):
    """
    Keithley_2231A(address)

    address : str, address of the connected power supply

    object for accessing basic functionallity of the Keithley DC supply
    """

    def __init__(self, address, **kwargs) -> None:
        super().__init__(address, **kwargs)
        self.set_access_remote('remote')

    def __del__(self) -> None:
        if hasattr(self, 'instrument'):
            self.set_access_remote('local')
        super().__del__()

    def set_access_remote(self, mode) -> None:
        """
        set_access_remote(mode)

        mode: str, interface method either 'remote' or 'local'

        set access to the device inferface to 'remote' or 'local'
        """

        if mode.lower() == 'remote':
            self.instrument.write('SYSTem:RWLock')
        elif mode.lower() == 'local':
            self.instrument.write('SYSTem:LOCal')

    def set_channel(self, channel):  # check
        """
        set_channel(channel)

        channel: int, index of the channel to control.
                 valid options are 1-3

        Selects the specified Channel to use for software control

        """

        self.instrument.write(f'INST:NSEL {channel}')
        return None

    def get_channel(self):  # check
        """
        get_channel()

        Get current selected Channel

        returns: int
        """

        resp = self.instrument.query('INST:NSEL?')
        channel = int(resp)
        return channel

    def set_state(self, state: bool, channel: int) -> None:
        """
        set_state(state, channel)

        Enables/disables the output of the supply

        Args:
            state (bool): Supply state (True == enabled, False == disabled)
            channel (int): Index of the channel to control. valid options
                are 1-3
        """

        self.set_channel(channel)
        self.instrument.write(f"CHAN:OUTP {1 if state else 0}")

    def get_state(self, channel: int) -> bool:
        """
        get_state(channel)

        Retrives the current state of the output of the supply.

        Args:
            channel (int): index of the channel to control. Valid options
                are 1-3

        Returns:
            bool: Supply state (True == enabled, False == disabled)
        """

        self.set_channel(channel)
        response = self.instrument.query("CHAN:OUTP?")
        if response.rstrip('\n') not in ("ON", '1'):
            return False
        return True

    def on(self, channel: int) -> None:
        """
        on(channel)

        Enables the relay for the power supply's output equivalent to
        set_state(True).

        Args:
            channel (int): Index of the channel to control. Valid options
                are 1-3
        """

        self.set_state(True, channel)

    def off(self, channel: int) -> None:
        """
        off(channel)

        Disables the relay for the power supply's output equivalent to
        set_state(False).

        Args:
            channel (int): Index of the channel to control. Valid options
                are 1-3
        """

        self.set_state(False, channel)

    def toggle(self, channel: int,
               return_state: bool = False) -> Union[None, bool]:
        """
        toggle(channel, return_state=False)

        Reverses the current state of the Supply's output
        If return_state = True the boolean state of the supply after toggle()
        is executed will be returned.

        Args:
            channel (int): Index of the channel to control. Valid options
                are 1-3
            return_state (bool, optional): Whether or not to return the state
                of the supply after changing its state. Defaults to False.

        Returns:
            Union[None, bool]: If return_state == True returns the Supply state
                (True == enabled, False == disabled), else returns None
        """

        self.set_state(self.get_state() ^ True, channel)

        if return_state:
            return self.get_state(channel)

    def set_voltage(self, voltage, channel):
        """
        set_voltage(voltage)

        voltage: float or int, amplitude to set output to in Vdc

        channel: int, the index of the channel to set. Valid options are 1,2,3.

        set the output voltage setpoint of channel "channel" specified by
        "voltage"
        """

        self.set_channel(channel)
        self.instrument.write(f"SOUR:VOLT {voltage}")
        return None

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
        return None

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
        sleep(duration)
        self.set_voltage(start_level, channel)
        return None

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

        for v in np.linspace(start, stop, int(n)):
            self.set_voltage(v, channel)
            sleep(dt)
        return None

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
        sleep(dwell)
        self.ramp(stop, start, channel, n=int(n/2), dt=dt)
        return None


if __name__ == '__main__':
    pass
