from typing import Union
from pythonequipmentdrivers import Scpi_Instrument
import numpy as np
from time import sleep


class Kikusui_PLZ1004WH(Scpi_Instrument):  # 1 kW
    """
    Kikusui_PLZ1004WH(address)

    address : str, address of the connected electronic load

    Programmers Manual:
    https://manual.kikusui.co.jp/P/PLZ4W/i_f_manual/english/00-intro.html
    """
    # need to update:
    #     logic
    #     documenation

    def set_state(self, state: bool) -> None:
        """
        set_state(state)

        Enables/disables the input for the load

        Args:
            state (bool): Load state (True == enabled, False == disabled)
        """

        self.instrument.write(f"OUTP {1 if state else 0}")

    def get_state(self) -> bool:
        """
        get_state()

        Returns the current state of the input to the load

        Returns:
            bool: Load state (True == enabled, False == disabled)
        """

        if int(self.instrument.query("OUTP?")) == 1:
            return True
        return False

    def on(self) -> None:
        """
        on()

        Enables the input for the load. Equivalent to set_state(True).
        """

        self.set_state(True)

    def off(self) -> None:
        """
        off()

        Disables the input for the load. Equivalent to set_state(False)
        """

        self.set_state(False)

    def toggle(self, return_state: bool = False) -> Union[None, bool]:
        """
        toggle(return_state=False)

        Reverses the current state of the load's input
        If return_state = True the boolean state of the load after toggle() is
        executed will be returned

        Args:
            return_state (bool, optional): [description]. Defaults to False.

        Returns:
            Union[None, bool]: If return_state == True returns the Load state
                (True == enabled, False == disabled), else returns None
        """

        if self.get_state():
            self.off()
        else:
            self.on()

        if return_state:
            return self.get_state()

    def set_mode(self, mode, cv=False):
        """
        set_mode(mode, cv = False)

        mode: str, load type for the electronic load
            valid options are "CC", "CR", "CV", "CP"
        cv (optional): bool, option to add CV mode in addition to "mode" option
            only works in CC or CR mode

        changes the configuration of the electronic load.
        """

        mode = mode.upper()
        if mode in ("CC", "CR", "CV", "CP"):

            if (mode in ("CC", "CR")) and cv:
                self.instrument.write(f"FUNC {mode}CV")
            else:
                self.instrument.write(f"FUNC {mode}")
        else:
            raise ValueError("Invalid mode option")

        return None

    def get_mode(self):
        """
        get_mode()

        returns current configuration of the electronic load.
        """
        response = self.instrument.query("FUNC?")
        return response.rstrip("\n")

    def set_voltage(self, voltage: float) -> None:
        """
        set_voltage(voltage)

        Changes the voltage setpoint of the load in constant voltage.

        Args:
            voltage (float): Desired voltage setpoint in Volts DC.
        """

        self.instrument.write(f"VOLT {float(voltage)}")

    def get_voltage(self) -> None:
        """
        get_voltage()

        Reads the voltage setpoint of the load in constant voltage mode.

        Returns:
            float: Voltage setpoint in Volts DC.
        """

        response = self.instrument.query("VOLT?")
        return float(response)

    def set_cc_range(self, cc_range):
        """
        set_cc_range(cc_range)

        cc_range: str, range to set for CC mode
            valid ranges are "LOW", "MED", and "HIGH"

        sets the range of allowable currents in CC mode.
        Note: with increased current capability comes decreased setpoint
        accuracy
        """

        cc_range = cc_range.upper()
        if cc_range in ("LOW", "MED", "HIGH"):
            self.instrument.write(f"CURR:RANG {cc_range}")
        else:
            raise ValueError("Invalid range option")
        return None

    def get_cc_range(self):
        """
        get_cc_range()

        returns the current range of allowable currents for CC mode.
        """

        response = self.instrument.query("CURR:RANG?")
        return response.rstrip('\n')

    def set_cr_range(self, cr_range):
        """
        set_cr_range(cc_range)

        cr_range: str, range to set for CR mode
            valid ranges are "LOW", "MED", and "HIGH"

        sets the range of allowable conductances in CR mode.
        Note: with increased current capability comes decreased setpoint
        accuracy
        """

        cr_range = cr_range.upper()
        if cr_range in ("LOW", "MED", "HIGH"):
            self.instrument.write(f"COND:RANG {cr_range}")
        else:
            raise ValueError("Invalid range option")

        return None

    def get_cr_range(self):
        """
        get_cr_range()

        returns the current range of allowable conductances for CR mode.
        """

        response = self.instrument.query("COND:RANG?")
        return response.rstrip('\n')

    def set_slew_rate(self, slew_rate: Union[float, str]) -> None:
        """
        set_slew_rate(slew_rate)

        Adjusts the slew-rate of the load used when transitioning between
        current setpoints or while trying to regulate the current, voltage,
        power, or resistence under dynamic conditions.

        Args:
            slew_rate (Union[float, str]): slew-rate to use in A/S or the
                string "max".
        """

        if isinstance(slew_rate, (float, int)):
            # set-point needs to be sent in A/us
            self.instrument.write(f"CURR:SLEW {slew_rate*1e-6}")
        elif isinstance(slew_rate, str) and (slew_rate.upper() == "MAX"):
            self.instrument.write(f"CURR:SLEW {slew_rate}")
        else:
            raise ValueError('slew_rate must be a float or the str "max"')

    def get_slew_rate(self) -> float:
        """
        get_slew_rate()

        Retrives the slew-rate of the load used when transitioning between
        current setpoints or while trying to regulate the current, voltage,
        power, or resistence under dynamic conditions.

        Returns:
            float: slew-rate currently used in A/S
        """

        response = self.instrument.query("CURR:SLEW?")
        slew_rate = float(response)*1e6  # return is in A/us
        return slew_rate

    def set_current(self, current: float) -> None:
        """
        set_current(current)

        Changes the current setpoint of the load in constant current mode.

        Args:
            current (float): Desired current setpoint in Amps DC.
        """

        self.instrument.write(f"CURR {float(current)}")

    def get_current(self) -> float:
        """
        get_current()

        Reads the current setpoint of the load in constant current mode.

        Returns:
            float: Current setpoint in Amps DC.
        """

        response = self.instrument.query("CURR?")
        return float(response)

    def set_conductance(self, conductance):
        """
        set_conductance(conductance)

        conductance: float, desired conductance setpoint

        changes the conductance setpoint of the load
        """

        self.instrument.write(f"COND {conductance}")
        return None

    def get_conductance(self):
        """
        get_conductance()

        reads the conductance setpoint of the load in Siemiens

        returns: float
        """
        response = self.instrument.query("COND?")
        return float(response)

    def set_switching_state(self, state):
        """
        set_switching_state(state)

        state: int, whether to enable or disable the switching functionallity
        of the load
            valid options are 1 (to enable) or 0 (to disable)

        enable/disable the switching function on the load
        """
        self.instrument.write(f"SOUR:PULS:STAT {state}")
        return None

    def get_switching_state(self):
        """
        returns the whether or not the switching functionallity of the load is
        enabled or disabled

        returns: int
        """

        response = self.instrument.query("SOUR:PULS:STAT?")
        return int(response)

    def set_duty_cycle(self, duty_cycle):
        """
        set_duty_cycle(duty_cycle)

        duty_cycle: float/int, duty cycle to set in percent
            valid options are in the range 0-100

        sets the duty cycle used when the switching functionallity of the load
        is enabled
        """

        self.instrument.write(f"SOUR:PULS:DCYC {duty_cycle}")
        return None

    def get_duty_cycle(self):
        """
        get_duty_cycle()

        returns the duty cycle used when the switching functionallity of the
        load is enabled in percent

        returns: float
        """

        response = self.instrument.query("SOUR:PULS:DCYC?")
        return float(response)

    def set_frequency(self, frequency):
        """
        set_frequency(frequency)

        frequency: float/int, frequency to set in Hz

        sets the frequency used when the switching functionallity of the load
        is enabled
        """

        self.instrument.write(f"SOUR:PULS:FREQ {frequency}")
        return None

    def get_frequency(self):
        """
        get_frequency()

        gets the frequency used when the switching functionallity of the load
        is enabled in Hz
        """

        response = self.instrument.query("SOUR:PULS:FREQ?")
        return float(response)

    def measure_voltage(self) -> float:
        """
        measure_voltage()

        Retrives measurement of the voltage present across the load's input.

        Returns:
            float: Measured Voltage in Volts DC
        """

        response = self.instrument.query('MEAS:VOLT?')
        return float(response)

    def measure_current(self) -> float:
        """
        measure_current()

        Retrives measurement of the current present through the load.

        Returns:
            float: Measured Current in Amps DC.
        """

        response = self.instrument.query('MEAS:CURR?')
        return float(response)

    def measure_power(self) -> float:
        """
        measure_power()

        Retrives measurement of the power dissipated by the load.

        Returns:
            float: Measured power in Watts.
        """

        response = self.instrument.query('MEAS:POW?')
        return float(response)

    def pulse(self, level: float, duration: float) -> None:
        """
        pulse(level, duration)

        Generates a square pulse with height and duration specified by level
        and duration. The load will start and return to the previous current
        level set on the load before the execution of pulse(). "level" can be
        less than or greater than the previous current setpoint.

        Args:
            level (float): Current level of pulse in Amps DC
            duration (float): Duration of the pulse in seconds
        """

        start_level = self.get_current()

        self.set_current(level)
        sleep(duration)
        self.set_current(start_level)

    def ramp(self, start: float, stop: float,
             n: int = 100, dt: float = 0.01) -> None:
        """
        ramp(start, stop, n=100, dt=0.01)

        Generates a linear ramp on the loads current specified by the
        parameters start, stop, n, and dt.
        The input of the load should be enabled before executing this command.
        "start" can be higher than "stop" or vise-versa. The minimum dt is
        limited by the communication speed of the interface used to communicate
        with this device.

        Args:
            start (float): Initial current setpoint of the ramp in Amps DC.
            stop (float): Final current setpoint of the ramp in Amps DC.
            n (int, optional): Number of points in the ramp between "start" and
                "stop". Defaults to 100.
            dt (float, optional): Time between changes in the value of the
                setpoint in seconds. Defaults to 0.01.
        """

        for i in np.linspace(float(start), float(stop), int(n)):
            self.set_current(i)
            sleep(dt)

    def slew(self, start: float, stop: float, n: int = 100,
             dt: float = 0.01, dwell: float = 0) -> None:
        """
        slew(start, stop, n=100, dt=0.01, dwell=0, channel=0)

        Generates a triangular waveform on the loads current specified by the
        parameters start, stop, n, and dt.
        Optionally, a dwell acan be added at the top of the waveform to create
        a trapezoidal load shape.
        The input of the load should be enabled before executing this command.
        "start" can be higher than "stop" or vise-versa. The minimum dt is
        limited by the communication speed of the interface used to communicate
        with this device.

        Args:
            start (float): Initial current setpoint of the ramp in Amps DC.
            stop (float): Midpoint current setpoint of the ramp in Amps DC.
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
