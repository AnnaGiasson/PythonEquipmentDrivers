from pythonequipmentdrivers import Scpi_Instrument as _Scpi_Instrument
import numpy as _np
from time import sleep as _sleep


class Kikusui_PLZ1004WH(_Scpi_Instrument):  # 1 kW
    """
    Programmers Manual:
    http://www.kikusui.co.jp/kiku_manuals/P/PLZ4W/i_f_manual/english/sr_sys1_sour.html

    need to update:
        logic
        documenation
    """

    def __init__(self, address):
        super().__init__(address)
        return

    def set_state(self, state):
        """
        set_state(state)

        state: int, 1 or 0 for on and off respectively

        enables/disables the input for the load
        """

        self.instrument.write(f"OUTP {state}")
        return

    def get_state(self):
        """
        get_state()

        returns the current state of the input to the load

        returns: int
        1: enabled, 0: disabled
        """

        if int(self.instrument.query("OUTP?")) == 1:
            return True
        return False

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

        return_state (optional): boolean, whether or not to return the state
                                 load's input

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

        return

    def get_mode(self):
        """
        get_mode()

        returns current configuration of the electronic load.
        """
        response = self.instrument.query("FUNC?")
        return response.rstrip("\n")

    def set_voltage(self, voltage):
        """
        set_voltage(voltage)

        voltage: float, voltage setpoint for CV mode

        sets the constant voltage setpoint if the load is in constant current
        mode or any mode that includes a CV option
        """

        self.instrument.write(f"VOLT {voltage}")
        return

    def get_voltage(self):
        """
        get_voltage()

        gets the constant voltage setpoint used in a CV mode in Vdc
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
        return

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

        return

    def get_cr_range(self):
        """
        get_cr_range()

        returns the current range of allowable conductances for CR mode.
        """

        response = self.instrument.query("COND:RANG?")
        return response.rstrip('\n')

    def set_slew(self, slew_rate):
        """
        set_slew(slew_rate)

        slew_rate: float/str, value of the slew rate to be set in Amps/uS
           valid options are either: positive real floats, the strings "MAX"
           or positive real ints

        adjusts the slew rate of the load according to the value specified by
        "slew_rate"
        """

        if type(slew_rate) in (float, int):
            self.instrument.write(f"CURR:SLEW {slew_rate}")
        elif (type(slew_rate) is str) and (slew_rate.upper() == "MAX"):
            self.instrument.write(f"CURR:SLEW {slew_rate}")
        else:
            raise ValueError("Invalid option")

        return

    def get_slew(self):
        """
        get_slew()

        returns the current slew rate setting of the electronic load in Amps/uS
        """

        response = self.instrument.query("CURR:SLEW?")
        return float(response)

    def set_current(self, current):
        """
        set_current(current)

        current: float, desired current setpoint

        changes the current setpoint of the load
        """

        self.instrument.write(f"CURR {current}")
        return

    def get_current(self):
        """
        get_current()

        reads the current setpoint of the load in Adc
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
        return

    def get_conductance(self):
        """
        get_conductance()

        reads the conductance setpoint of the load in Siemiens

        returns: float
        """
        response = self.instrument.query(f"COND?")
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
        return

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
        return

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
        return

    def get_frequency(self):
        """
        get_frequency()

        gets the frequency used when the switching functionallity of the load
        is enabled in Hz
        """

        response = self.instrument.query("SOUR:PULS:FREQ?")
        return float(response)

    def measure_voltage(self):
        """
        measure_voltage_rms()

        returns measurement of the voltage present across the load in Vdc
        returns: float
        """

        response = self.instrument.query('MEAS:VOLT?')
        return float(response)

    def measure_current(self):
        """
        measure_current()

        returns measurement of the current through the load in Adc
        returns: float
        """
        response = self.instrument.query('MEAS:CURR?')
        return float(response)

    def measure_power(self):
        """
        measure_power()

        returns measurement of the power consumed by the load in W
        returns: float
        """

        response = self.instrument.query('MEAS:POW?')
        return float(response)

    def pulse(self, level, duration):
        """
        pulse(level, duration)

        level: float/int, current level of "high" state of the pulse in Amps
        duration: float/int, duration of the "high" state of the pulse in
                  seconds

        generates a square pulse with height and duration specified by level
        and duration. Will start and return to the previous current level set
        on the load before the execution of pulse(). level can be less than or
        greater than the previous current setpoint
        """

        start_level = self.get_current()
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
        before executing this command contrary to what this documentation may
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
        parameters start, stop, n, and dt optionally, a dwell acan be added at
        the top of the waveform to create a trapezoidal load shape. input of
        the load should be enabled before executing this command contrary to
        what this documentation may imply, start can be higher than stop or
        vise-versa. minimum dt is limited by the communication speed of the
        interface used to communicate with this device
        """

        self.ramp(start, stop, n=int(n), dt=dt)
        _sleep(dwell)
        self.ramp(stop, start, n=int(n), dt=dt)
        return
