from pythonequipmentdrivers import Scpi_Instrument
import numpy as np
from time import sleep
from typing import List, Union


class Sorensen_SGA(Scpi_Instrument):
    """
    Sorensen_SGA(address)

    address : str, address of the connected power supply

    object for accessing basic functionallity of the Sorensen_SGA DC supply
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

    def set_voltage(self, voltage: float) -> None:
        """
        set_voltage(voltage)

        Sets the output voltage setpoint for the supply.

        Args:
            voltage (float): output voltage setpoint in Volts DC.
        """

        self.instrument.write(f'SOUR:VOLT {float(voltage)}')

    def get_voltage(self) -> float:
        """
        get_voltage()

        Retrives the current value output voltage setpoint.

        Returns:
            float: Output voltage setpoint in Volts DC.
        """

        response = self.instrument.query('SOUR:VOLT?')
        return float(response)

    def set_current(self, current: float) -> None:
        """
        set_current(current)

        Sets the current limit threshold for the power supply.

        Args:
            current (float): Current Limit setpoint in Amps DC.
        """

        self.instrument.write(f'SOUR:CURR {float(current)}')

    def get_current(self) -> float:
        """
        get_current()

        Retrives the current limit threshold for the power supply.

        Returns:
            float: Current Limit setpoint in Amps DC.
        """

        response = self.instrument.query('SOUR:CURR?')
        return float(response)

    def measure_voltage(self) -> float:
        """
        measure_voltage()

        Retrives measurement of the voltage present across the supply's output.

        Returns:
            float: Measured Voltage in Volts DC
        """

        response = self.instrument.query('MEAS:VOLT?')
        return float(response)

    def measure_current(self) -> float:
        """
        measure_current()

        Retrives measurement of the current present through the supply.

        Returns:
            float: Measured Current in Amps DC.
        """

        response = self.instrument.query('MEAS:CURR?')
        return float(response)

    def measure_power(self) -> float:
        """
        measure_power()

        Retrives measurement of the power drawn from the supply.
        Note: This command is only supported in the SGI Version of the supply.

        Returns:
            float: Measured power in Watts.
        """

        response = self.instrument.query('MEAS:POW?')
        return float(response)

    def set_over_voltage_protection(self, voltage: float) -> None:
        """
        set_over_voltage_protection(voltage)

        Configures the OVP setpoint of the supply.

        Args:
            voltage (float): Over voltage protection set-point in Volts DC.
        """

        self.instrument.write(f'SOUR:VOLT:PROT {float(voltage)}')

    def get_over_voltage_protection(self) -> float:
        """
        get_over_voltage_protection(voltage)

        Retrives the current value of the OVP setpoint of the supply.

        Returns:
            float: Over voltage protection set-point in Volts DC.
        """

        response = self.instrument.query('SOUR:VOLT:PROT?')
        return float(response)

    def set_over_current_protection(self, current: float) -> None:
        """
        set_over_current_protection(current)

        Configures the OCP setpoint of the supply.

        Args:
            current (float): Over current protection set-point in Amps DC.
        """

        self.instrument.write(f'SOUR:CURR:LIM {float(current)}')

    def get_over_current_protection(self) -> float:
        """
        get_over_current_protection(current)

        Retrives the current value of the OCP setpoint of the supply.

        Returns:
            float: Over current protection set-point in Amps DC.
        """

        response = self.instrument.query('SOUR:CURR:LIM?')
        return float(response)

    def pop_error_queue(self) -> Union[str, None]:
        """
        pop_error_queue()

        Retrieves a summary information of the error at the front of the error
        queue (FIFO). Information consists of an error number and some
        descriptive text. If the error queue is empty this function returns
        None. To clear the queue either repeatedly pop elements off the queue
        until it is empty or call the self.cls() method.

        Returns:
            Union[str, None]: Error summary information for the first item in
                the error queue or None if the queue is empty.
        """

        response = self.instrument.query('SYST:ERR?')
        if response[0] == '0':
            return None
        return response.strip()

    def error_queue(self) -> List:
        """
        error_queue()

        Retrieves the summary information for all errors currently in the error
        queue (FIFO), clearing it in the process. Information for each error
        consists of an error number and some descriptive text. If the error
        queue is empty this function returns an empty list.

        Returns:
            Union[str, None]: Error summary information for the first item in
                the error queue or None if the queue is empty.
        Returns:
            List: a list of error summary information for the errors in the
                error queue. Ordered by occurance.
        """

        queue = []
        while True:
            error = self.pop_error_queue()
            if error is None:
                break
            queue.append(error)

        return queue

    def set_local(self, state: bool) -> None:
        """
        set_local(state)

        Forces the supply to local or remote state.

        Args:
            state (bool): local state, if True the supply can be locally
                operated through the front panel else the front panel is locked
                from manual use and the supply must be adjusted remotely.
        """

        self.instrument.write(f'SYST:LOCAL {1 if state else 0}')

    def get_local(self) -> bool:
        """
        get_local()

        Returns whether the supply is in a local or remote state.

        Returns:
            bool: local state, if True the supply can be locally operated
                through the front panel else the front panel is locked from
                manual use and the supply must be adjusted remotely.
        """

        response = self.instrument.query('SYST:LOCAL?')
        return ('ON' in response)

    def pulse(self, level: float, duration: float) -> None:
        """
        pulse(level, duration)

        Generates a square pulse with height and duration specified by level
        and duration. The supply will start and return to the previous voltage
        level set on the supply before the execution of pulse(). "level" can be
        less than or greater than the previous voltage setpoint.

        Args:
            level (float): Voltage level of pulse in Volts DC
            duration (float): Duration of the pulse in seconds
        """

        start_level = self.get_voltage()
        self.set_voltage(level)
        sleep(duration)
        self.set_voltage(start_level)

    def ramp(self, start: float, stop: float,
             n: int = 100, dt: float = 0.01) -> None:
        """
        ramp(start, stop, n=100, dt=0.01)

        Generates a linear ramp on the supply's voltage specified by the
        parameters start, stop, n, and dt.
        The input of the supply should be enabled before executing this
        command. "start" can be higher than "stop" or vise-versa. The minimum
        dt is limited by the communication speed of the interface used to
        communicate with this device.

        Args:
            start (float): Initial voltage setpoint of the ramp in Volts DC.
            stop (float): Final voltage setpoint of the ramp in Volts DC.
            n (int, optional): Number of points in the ramp between "start" and
                "stop". Defaults to 100.
            dt (float, optional): Time between changes in the value of the
                setpoint in seconds. Defaults to 0.01.
        """

        for v in np.linspace(float(start), float(stop), int(n)):
            self.set_voltage(v)
            sleep(dt)

    def slew(self, start: float, stop: float, n: int = 100,
             dt: float = 0.01, dwell: float = 0) -> None:
        """
        slew(start, stop, n=100, dt=0.01, dwell=0, channel=0)

        Generates a triangular waveform on the supply's voltage specified by
        the parameters start, stop, n, and dt.
        Optionally, a dwell acan be added at the top of the waveform to create
        a trapezoidal voltage shape.
        The input of the supply should be enabled before executing this
        command. "start" can be higher than "stop" or vise-versa. The minimum
        dt is limited by the communication speed of the interface used to
        communicate with this device.

        Args:
            start (float): Initial voltage setpoint of the ramp in Volts DC.
            stop (float): Midpoint voltage setpoint of the ramp in Volts DC.
            n (int, optional): Number of points in the ramp between "start" and
                "stop". Defaults to 100.
            dt (float, optional): Time between changes in the value of the
                setpoint in seconds. Defaults to 0.01.
            dwell (float, optional): Time to dwell at the "stop" value before
                ramping back to "start". Defaults to 0.
        """

        self.ramp(start, stop, n=n, dt=dt)
        sleep(dwell)
        self.ramp(stop, start, n=n, dt=dt)
