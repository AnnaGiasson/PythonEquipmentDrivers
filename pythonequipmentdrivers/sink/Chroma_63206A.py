from pythonequipmentdrivers import Scpi_Instrument as _Scpi_Instrument
import numpy as _np
from time import sleep as _sleep


class Chroma_63206A(_Scpi_Instrument):  # 6 kW
    """
    Chroma_63206A(address)

    address : str, address of the connected electronic load

    object for accessing basic functionallity of the Chroma_63206A DC load
    """

    def __init__(self, address):
        super().__init__(address)
        self.supported_modes = ("CC", "CR", "CP", "CCD")
        return

    def set_state(self, state):
        """
        set_state(state)

        state: int, 1 or 0 for on and off respectively

        enables/disables the input for the load
        """

        self.instrument.write(f"LOAD {state}")
        return

    def get_state(self):
        """
        get_state()

        returns the current state of the input to the load

        returns: int
        1: enabled, 0: disabled
        """

        if self.instrument.query("LOAD?").rstrip('\n') == "ON":
            return 1
        return 0

    def on(self):
        """
        on()

        enables the input for the load
        equivalent to set_state(1)
        """

        self.set_state(1)
        return

    def off(self):
        """
        off()

        disables the input for the load
        equivalent to set_state(0)
        """

        self.set_state(0)
        return

    def toggle(self, return_state=False):
        """
        toggle(return_state=False)

        return_state: boolean, whether or not to return the state load's input

        reverses the current state of the load's input

        if return_state = True the boolean state of the load after toggle() is
        executed will be returned
        """

        if self.get_state():
            self.off()
        else:
            self.on()

        if return_state:
            return self.get_state()
        return

    def set_short_state(self, state):
        """
        set_short_state(state)

        state: int, 1 or 0 for on and off respectively

        enables/disables the short circuit simulation for the load
        """

        self.instrument.write(f"LOAD:SHOR {int(state)}")
        return

    def get_short_state(self):
        """
        get_short_state()

        returns the current state of the loads short circuit simulation

        returns: int
        1: enabled, 0: disabled
        """

        response = self.instrument.query("LOAD:SHOR?")
        return int(response)

    def set_mode(self, mode, range_setting=2):
        """
        set_mode(mode, range_setting=0)

        range_setting (optional): int, range of the desired mode setting
            valid options are 0, 1, and 2 for low, medium, and high
            respectively. Default is 0

        Sets the desired load configuration. Currently supported options in
        this library are
        "CC", "CR", "CP", and "CCD".
        """

        if range_setting in range(0, 3):
            range_string = ["L", "M", "H"][range_setting]

        self.instrument.write(f"MODE {mode}{range_string}")
        return

    def get_mode(self):
        """
        get_mode(self)

        Returns the current configuration of the electronic load
        """

        response = self.instrument.query("MODE?")
        return response.rstrip('\n')

    def set_current(self, current, channel=0):
        """
        set_current(current, channel=0)

        current: float, desired current setpoint
        channel (optional): int, channel to change setpoint of.
            valid options are 0,1,2 (default is 0)

        changes the current setpoint of the load for the specified channel in
        constant current mode. if channel = 0 both channels will be set to the
        value specified
        """

        if channel == 0:
            self.instrument.write(f'CURR:STAT:L1 {float(current)}')
            self.instrument.write(f'CURR:STAT:L2 {float(current)}')
        else:
            command_str = f'CURR:STAT:L{int(channel)} {float(current)}'
            self.instrument.write(command_str)
        return

    def get_current(self, channel):
        """
        get_current(channel)

        channel: int, channel to get setpoint of.
            valid options are 1,2

        reads the current setpoint of the load for the specified channel in
        constant current mode
        """

        response = self.instrument.query(f'CURR:STAT:L{int(channel)}?')
        return float(response)

    def set_dynamic_current(self, current, channel=0):
        """
        set_dynamic_current(current, channel=0)

        current: float, desired current setpoint
        channel (optional): int, channel to change setpoint of.
            valid options are 0,1,2 (default is 0)

        changes the current setpoint of the load for the specified channel in
        dynamic current mode. if channel = 0 both channels will be set to the
        value specified
        """

        if channel == 0:
            self.instrument.write(f'CURR:DYN:L1 {float(current)}')
            self.instrument.write(f'CURR:DYN:L2 {float(current)}')
        else:
            self.instrument.write(f'CURR:DYN:L{int(channel)} {float(current)}')
        return

    def get_dynamic_current(self, channel):
        """
        get_current(channel)

        channel: int, channel to get setpoint of.
            valid options are 1,2

        reads the current setpoint of the load for the specified channel in
        dynamic current mode
        """

        response = self.instrument.query(f'CURR:DYN:L{int(channel)}?')
        return float(response)

    def set_dynamic_current_time(self, t, channel):
        """
        set_dynamic_current_time(t, channel=0)

        t: float, desired duration of dynamic setpoint in seconds.
        channel (optional): int, channel to change setpoint of.
            valid options are 0,1,2 (default is 0)

        changes the duration of the dynamic current setpoint of the load for
        the specified channel in dynamic current mode.
        if channel = 0 both channels will be set to the value specified
        """
        if channel == 0:
            self.instrument.write(f'CURR:DYN:T1 {float(t)}')
            self.instrument.write(f'CURR:DYN:T2 {float(t)}')
        else:
            self.instrument.write(f'CURR:DYN:T{int(channel)} {float(t)}')
        return

    def get_dynamic_current_time(self, channel):
        """
        get_dynamic_current_time(channel)

        channel: int, channel to get duration of.
            valid options are 1,2

        reads the duration of the dynamic current setpoint of the load for the
        specified channel in dynamic current mode.
        """

        response = self.instrument.query(f'CURR:DYN:T{int(channel)}?')
        return float(response)

    def set_dynamic_current_repeat(self, n):
        """
        set_dynamic_current_repeat(n)

        n: int, desired number of cycles to repeat the two dyanmic current
        setpoints.

        changes the number of cycles to alternate between the two dynamic
        current setpoints before turning off. Cycles begin when the output of
        the load is enabled, after completion load will automatically turn
        itself off. if n = 0 the load will indefinately cycle between the two
        setpoints.
        """

        self.instrument.write(f"CURR:DYN:REP {int(n)}")
        return

    def get_dynamic_current_repeat(self):
        """
        get_dynamic_current_repeat()

        returns the number of cycles to alternate between the two dynamic
        current setpoints before turning off. Cycles begin when the output of
        the load is enabled, after completion load will automatically turn
        itself off. if n = 0 the load will indefinately cycle between the two
        setpoints.
        """

        response = self.instrument.query("CURR:DYN:REP?")
        return int(response)

    def set_dynamic_current_rise_rate(self, slew_rate):
        """
        set_dynamic_current_rise_rate(slew_rate)

        slew_rate: float, slew rate of the rising edge of current setpoint
                   transitions, A/us

        sets the slew rate for the rising edge between the two dynamic current
        setpoint in dynamic current mode.
        """
        self.instrument.write(f"CURR:DYN:RISE {float(slew_rate)}")
        return

    def get_dynamic_current_rise_rate(self):
        """
        get_dynamic_current_rise_rate()

        returns the slew rate for the rising edge between the two dynamic
        current setpoint in dynamic current mode.
        """
        response = self.instrument.query("CURR:DYN:RISE?")
        return float(response)

    def set_dynamic_current_fall_rate(self, slew_rate):
        """
        set_dynamic_current_fall_rate(slew_rate)

        slew_rate: float, slew rate of the falling edge of current setpoint
        transitions, A/us

        sets the slew rate for the falling edge between the two dynamic current
        setpoint in
        dynamic current mode.
        """
        self.instrument.write(f"CURR:DYN:FALL {float(slew_rate)}")
        return

    def get_dynamic_current_fall_rate(self):
        """
        get_dynamic_current_fall_rate()

        returns the slew rate for the falling edge between the two dynamic
        current setpoint in dynamic current mode.
        """
        response = self.instrument.query("CURR:DYN:FALL?")
        return float(response)

    def set_resistance(self, resistance, channel=0):
        """
        set_resistance(resistance, channel=0)

        resistance: float, desired resistance setpoint
        channel (optional): int, channel to change setpoint of.
            valid options are 0,1,2 (default is 0)

        changes the resistance setpoint of the load for the specified channel
        in constant resistance mode. if channel = 0 both channels will be set
        to the value specified
        """

        if channel == 0:
            self.instrument.write(f"RES:STAT:L1 {float(resistance)}")
            self.instrument.write(f"RES:STAT:L2 {float(resistance)}")
        else:
            command_str = f"RES:STAT:L{int(channel)} {float(resistance)}"
            self.instrument.write(command_str)
        return

    def get_resistance(self, channel):
        """
        get_resistance(channel)

        channel: int, channel to get setpoint of.
            valid options are 1,2

        reads the resistance setpoint of the load for the specified channel in
        constant resistance mode
        """

        response = self.instrument.query(f"RES:STAT:L{int(channel)}?")
        return float(response)

    def set_voltage(self, voltage, channel=0):
        """
        set_voltage(voltage, channel=0)

        voltage: float, desired voltage setpoint
        channel (optional): int, channel to change setpoint of.
            valid options are 0,1,2 (default is 0)

        changes the voltage setpoint of the load for the specified channel in
        constant voltage mode if channel = 0 both channels will be set to the
        value specified
        """
        if channel == 0:
            self.instrument.write(f"VOLT:STAT:L1 {float(voltage)}")
            self.instrument.write(f"VOLT:STAT:L2 {float(voltage)}")
        else:
            command_str = f"VOLT:STAT:L{int(channel)} {float(voltage)}"
            self.instrument.write(command_str)
        return

    def get_voltage(self, channel):
        """
        get_voltage(channel)

        channel: int, channel to get setpoint of.
            valid options are 1,2

        reads the voltage setpoint of the load for the specified channel in
        constant voltage mode
        """

        response = self.instrument.query(f"VOLT:STAT:L{int(channel)}?")
        return float(response)

    def set_cv_current(self, current):
        """
        set_cv_current(current)

        current: float, desired current setpoint

        changes the current setpoint of the load in constant voltage mode
        """

        self.instrument.write(f"VOLT:STAT:ILIM {float(current)}")
        return

    def get_cv_current(self):
        """
        get_cv_current()

        reads the current setpoint of the load in constant voltage mode
        """

        response = self.instrument.query(f"VOLT:STAT:ILIM?")
        return float(response)

    def set_power(self, power, channel=0):
        """
        set_power(power, channel=0)

        power: float, desired power setpoint
        channel (optional): int, channel to change setpoint of.
            valid options are 0,1,2 (default is 0)

        changes the power setpoint of the load for the specified channel in
        constant power mode. if channel = 0 both channels will be set to the
        value specified
        """

        if channel == 0:
            self.instrument.write(f'POW:STAT:L1 {float(power)}')
            self.instrument.write(f'POW:STAT:L2 {float(power)}')
        else:
            self.instrument.write(f'POW:STAT:L{int(channel)} {power}')
        return

    def get_power(self, channel):
        """
        get_power(channel)

        channel: int, channel to get the setpoint of.
            valid options are 1,2

        reads the power setpoint of the load for the specified channel in
        constant power mode
        """

        response = self.instrument.query(f'POW:STAT:L{int(channel)}?')
        return float(response)

    def measure_voltage(self):
        """
        measure_voltage_rms()

        returns measurement of the voltage present across the load in Vdc
        returns: float
        """

        response = self.instrument.query('FETC:VOLT?')
        return float(response)

    def measure_current(self):
        """
        measure_current()

        returns measurement of the current through the load in Adc
        returns: float
        """

        response = self.instrument.query('FETC:CURR?')
        return float(response)

    def measure_power(self):
        """
        measure_power()

        returns measurement of the power consumed by the load in W
        returns: float
        """

        response = self.instrument.query('FETC:POW?')
        return float(response)

    def pulse(self, level, duration):
        """
        pulse(level, duration)

        level: float/int, current level of "high" state of the pulse in Amps
        duration: float/int, duration of the "high" state of the pulse in
                  seconds

        generates a square pulse with height and duration specified by level
        and duration. will start and return to the previous current level set
        on the load before the execution of pulse(). level can be less than or
        greater than the previous current setpoint
        """

        start_level = self.get_current(1)
        self.set_current(level)
        _sleep(duration)
        self.set_current(start_level)
        return

    def ramp(self, start, stop, n=100, dt=0.01):
        """
        ramp(start, stop, n=100, dt=0.01)

        start: float/int, starting current setpoint of the ramp in Adc
        stop: float/int, ending current setpoint of the ramp in Adc
        n (optional): int, number of points in the ramp between start and stop
            default is 100
        dt (optional): float/int, time between changes in the value of the
                       setpoint in seconds. default is 0.01 sec

        generates a linear ramp on the loads current specified by the
        parameters start, stop, n, and dt. input of the load should be enabled
        before executing this command. contrary to what this documentation may
        imply, start can be higher than stop or vise-versa. minimum dt is
        limited by the communication speed of the interface used to communicate
        with this device
        """

        for i in _np.linspace(start, stop, int(n)):
            self.set_current(i)
            _sleep(dt)
        return

    def slew(self, start, stop, n=100, dt=0.01, dwell=0):
        """
        slew(start, stop, n=100, dt=0.01, dwell=0)

        start: float/int, "low" current setpoint of the ramp in Adc
        stop: float/int, "high" current setpoint of the ramp in Adc
        n (optional): int, number of points in the ramp between start and stop
            default is 100
        dt (optional): float/int, time between changes in the value of the
                       setpoint in seconds. default is 0.01 sec
        dwell (optional): float/int, time to dwell at the "stop" value before
                          the ramp back to "start". default is 0 sec (no dwell)

        generates a triangular waveform on the loads current specified by the
        parameters start, stop, n, and dt. optionally, a dwell acan be added at
        the top of the waveform to create a trapezoidal load shape. input of
        the load should be enabled before executing this command. contrary to
        what this documentation may imply, start can be higher than stop or
        vise-versa. minimum dt is limited by the communication speed of the
        interface used to communicate with this device
        """

        self.ramp(start, stop, n=int(n), dt=dt)
        _sleep(dwell)
        self.ramp(stop, start, n=int(n), dt=dt)
        return
