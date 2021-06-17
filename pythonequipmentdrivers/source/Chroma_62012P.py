from pythonequipmentdrivers import Scpi_Instrument
from time import sleep
import numpy as np
from typing import Tuple, Dict, List


class Chroma_62012P(Scpi_Instrument):
    """
    Chroma_62012P(address)

    address : str, address of the connected power supply

    object for accessing basic functionallity of the Chroma_62012P DC supply
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

        self.instrument.write(f"CONF:OUTP {state}")
        return None

    def get_state(self):
        """
        get_state()

        returns the current state of the output relay,

        returns: int
        1: enabled, 0: disabled
        """

        response = self.instrument.query("CONF:OUTP?").rstrip('\n')
        if response != "ON":
            return 0
        return 1

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

    def set_voltage(self, voltage):
        """
        set_voltage(voltage)

        voltage: float or int, amplitude to set output to in Vdc

        set the output voltage setpoint specified by "voltage"
        """

        self.instrument.write(f"SOUR:VOLT {voltage}")
        return None

    def get_voltage(self):
        """
        get_voltage()

        gets the output voltage setpoint in Vdc

        returns: float
        """

        response = self.instrument.query("SOUR:VOLT?")
        return float(response)

    def set_current(self, current):
        """
        set_current(current)

        current: float/int, current limit setpoint in Adc

        sets the current limit setting for the power supply in Adc
        """
        self.instrument.write(f"SOUR:CURR {current}")
        return None

    def get_current(self):
        """
        get_current()

        gets the current limit setting for the power supply in Adc

        returns: float
        """

        response = self.instrument.query("SOUR:CURR?")
        return float(response)

    def set_current_slew_rate(self, slew_rate):
        """
        set_current_slew_rate(slew_rate)

        slew_rate: float, current slew rate in A/ms

        sets the current slew rate for the power supply's output current in
        A/ms
        """

        self.instrument.write(f"SOUR:CURR:SLEW {slew_rate}")
        return None

    def get_current_slew_rate(self):
        """
        get_current_slew_rate()

        gets the current slew rate for the power supply's output current in
        A/ms

        returns: float
        """

        response = self.instrument.query("SOUR:CURR:SLEW?")
        return float(response)

    def set_voltage_slew_rate(self, slew_rate):
        """
        set_voltage_slew_rate(slew_rate)

        slew_rate: float, voltage slew rate in V/ms

        sets the voltage slew rate for the power supply's output voltage in
        V/ms
        """

        self.instrument.write(f"SOUR:VOLT:SLEW {slew_rate}")
        return None

    def get_voltage_slew_rate(self):
        """
        get_voltage_slew_rate()

        gets the voltage slew rate for the power supply's output voltage in
        V/ms

        returns: float
        """

        response = self.instrument.query("SOUR:VOLT:SLEW?")
        return float(response)

    def set_voltage_limit(self, v_limit):
        """
        set_voltage_limit(v_limit)

        v_limit: float, voltage limit in Vdc

        sets the voltage setpoint limit for the power supply's output voltage
        in Vdc
        """

        self.instrument.write(f'SOUR:VOLT:LIM:HIGH {v_limit}')
        return None

    def get_voltage_limit(self):
        """
        get_voltage_limit()

        returns:
        v_limit: float, voltage limit in Vdc

        Returns the voltage setpoint limit for the power supply's output
        voltage in Vdc
        """

        resp = self.instrument.query('SOUR:VOLT:LIM:HIGH?')
        return float(resp)

    def measure_voltage(self):
        """
        measure_voltage()

        returns measurement of the dc voltage of the power supply in Vdc

        returns: float
        """

        response = self.instrument.query("FETC:VOLT?")
        return float(response)

    def measure_current(self):
        """
        measure_current()

        returns measurement of the dc current of the power supply in Adc
        returns: float
        """

        response = self.instrument.query("FETC:CURR?")
        return float(response)

    def measure_power(self):
        """
        measure_power()

        returns measurement of the power drawn from the power supply in W

        returns: float
        """

        response = self.instrument.query("FETC:POW?")
        return float(response)

    def get_status(self) -> Tuple:
        """
        get_status()

        Fetches and decodes the status reponse register of the source.

        Possible Error messages returned by this source are:
            'OVP'
            'OCP'
            'OPP'
            'Remote_Inhibit'
            'OTP'
            'Fan_Lock'
            'Sense_Fault'
            'Series_Fault'
            'Bus_OVP'
            'AC_Fault'
            'Fold_Back_CV_to_CC'
            'Fold_Back_CC_to_CV'
            'Reserved'
            'Reserved'
            'Reserved'
            'Reserved

        Returns:
            Tuple: (Error_Mesaage, Output_State, Output_Mode),
                Error_Message is a str, if more than one error is present each
                error message str will be returned joined by commas.
                Output_State is a boolean True/False state corresponding to the
                state of the output relay (see self.get_state). Output mode is
                either "CC" or "CV" depending on the configuration of the
                source and its external loading.
        """

        # encoded as a bit mask, elements in this tuple represent the meaning
        # of each bit with the tuple index representing the bit weight.
        message_responses = ('OVP', 'OCP', 'OPP', 'Remote_Inhibit',
                             'OTP', 'Fan_Lock', 'Sense_Fault', 'Series_Fault',
                             'Bus_OVP', 'AC_Fault', 'Fold_Back_CV_to_CC',
                             'Fold_Back_CC_to_CV', 'Reserved', 'Reserved',
                             'Reserved', 'Reserved')

        response = self.instrument.query("FETC:STAT?")
        response = response.strip('\n')

        message_code, state, mode = response.split(',')

        message_code = int(message_code)
        messages = []
        for n, msg in enumerate(message_responses):
            if message_code & (1 << n):
                messages.append(msg)
        messages = ','.join(messages)

        output_state = True if (state == 'ON') else False

        return (messages, output_state, mode)

    def set_program_type(self, program_type: str) -> None:

        valid_program_types = ('STEP', 'LIST', 'CP')

        program_type = str(program_type).upper()
        if program_type not in valid_program_types:
            raise ValueError('Invalid program type'
                             f', use: {valid_program_types}')

        self.instrument.write(f'PROG:MODE {program_type}')

    def set_program(self, n: int) -> None:
        self.instrument.write(f'PROG:SEL {int(n)}')

    def get_program_type(self) -> str:

        response = self.instrument.query('PROG:MODE?')
        return response.lower()

    def build_program(self, *sequence: dict, **kwargs) -> None:

        if not (1 <= len(sequence) <= 100):
            raise ValueError('Program must have between 1-100 Sequences')

        # initialization
        cmds = []
        cmds.append(f'PROG:SEL {int(kwargs.get("program_number", 1))}')

        if kwargs.get('clear', True):
            cmds.append('PROG:CLEAR')

        # 0 links to no program
        cmds.append(f'PROG:LINK {int(kwargs.get("link", 0))}')

        cmds.append(f'PROG:COUNT {int(kwargs.get("count", 1))}')

        for cmd in cmds:
            self.instrument.write(cmd)

        # build program
        valid_sequence_types = ('AUTO',  # move to next sequence after "time"
                                'MANUAL',  # wait until front panel pressed
                                'TRIGGER',  # wait for sine wave on pin 8 of
                                            # analog interface
                                'SKIP')  # skip this sequence and move to next

        for n, seq in enumerate(sequence, start=1):

            if not isinstance(seq, dict):
                raise TypeError('Sequence Must be of Type "dict"')

            cmds.clear()  # clear command queue

            # create new sequence
            cmds.append(f'PROG:ADD {n}')
            cmds.append(f'PROG:SEQ:SEL {n}')

            # set sequence type
            seq_type = str(seq.get('type', 'AUTO')).upper()
            if seq_type not in valid_sequence_types:
                raise ValueError(f'Invalid Sequence type "{seq_type}"')
            cmds.append(f'PROG:SEQ:TYPE {seq_type}')

            # set sequence parameters
            cmds.append(f'PROG:SEQ:VOLT {float(seq.get("voltage", 0))}')  # V
            cmds.append(f'PROG:SEQ:CURR {float(seq.get("current", 0))}')  # A
            cmds.append(f'PROG:SEQ:TIME {float(seq.get("time", 0))}')  # sec

            #   slew-rate arg is in V/s but it actually needs to be sent
            #   in V/ms
            volt_slew = float(seq.get("voltage_slew", 1000))  # V/s
            cmds.append(f'PROG:SEQ:VOLT:SLEW {volt_slew/1e3}')  # V/ms

            curr_slew = seq.get("current_slew", "INF")
            if isinstance(curr_slew, str):
                if (curr_slew.upper() != 'INF'):
                    raise ValueError('Current Slew-rate must be a float or'
                                     'the string "INF"')
                else:
                    cmds.append('PROG:SEQ:CURR:SLEWINF')
            else:
                #   slew-rate arg is in A/s but it actually needs to be sent
                #   in A/ms
                cmds.append(f'PROG:SEQ:CURR:SLEW {float(curr_slew)/1000}')

            #   TTL is an 8-bit number, sets the voltage of 8 of the digitial
            #   pins on the back of the source (pins 12 -> 19, TTL0 -> TTL7).
            #   Uses 5 V Logic
            ttl = int(seq.get("ttl", 0))
            if not (0 <= ttl <= 255):
                raise ValueError('TTL Must be an int in the range 0-255')
            cmds.append(f'PROG:SEQ:TTL {ttl}')

            for cmd in cmds:  # send commands in queue
                self.instrument.write(cmd)
        else:
            if kwargs.get('save', False):
                self.instrument.write('PROG:SAVE')

    def get_program(self, program_type: str,
                    program_number: int) -> Tuple[Dict, List]:

        # select specified program
        self.set_program_type(program_type)
        self.set_program(program_number)

        # get program metadata
        N = int(self.instrument.query('PROG:MAX?'))  # number of sequences

        options = {'program_number': program_number,
                   'count': int(self.instrument.query('PROG:COUNT?')),
                   'link': int(self.instrument.query('PROG:LINK?'))}

        valid_sequence_types = ('AUTO',  # move to next sequence after "time"
                                'MANUAL',  # wait until front panel pressed
                                'TRIGGER',  # wait for sine wave on pin 8 of
                                            # analog interface
                                'SKIP')  # skip this sequence and move to next

        # retrive info on each sequence
        program = []
        seq = {}
        for n in range(1, N+1, 1):
            seq.clear()
            self.instrument.write(f'PROG:SEQ:SEL {n}')  # select sequence

            response = self.instrument.query('PROG:SEQ?')
            response = response.strip()
            type_, volt, volt_sr, curr, curr_sr, ttl, t = response.split(',')

            # decode into same format used in self.build_program
            seq['type'] = valid_sequence_types[int(type_)]  # index into a list

            seq['voltage'] = float(volt)
            seq['voltage_slew'] = float(volt_sr)*1e3  # convert to V/s for user

            seq['current'] = float(curr)
            if ('INF' in curr_sr):
                seq['current_slew'] = 'INF'
            else:
                float(curr_sr)

            # convert to A/s for user output
            if isinstance(seq['current_slew'], float):
                seq['current_slew']*1e3

            seq['ttl'] = int(ttl)

            seq['time'] = float(t)

            program.append(seq.copy())  # add to program list

        # to duplicate this program pass to build_program with "program" as
        # Args and "options" as Kwargs
        return options, program

    def run_program(self, n: int = 0) -> None:

        if n != 0:
            self.set_program(n)

        self.instrument.write('PROG:RUN ON')

    def halt_program(self) -> None:

        self.instrument.write('PROG:RUN OFF')

    def get_program_state(self) -> bool:

        response = self.instrument.query('PROG:RUN?')
        response = response.strip()

        return (response == 'ON')

    def v_step_program(self, start: float, stop: float, t: float) -> None:

        # convert time to h:m:s (max is 99:59:59.99)
        h, m, s = (0, 0, 0)
        while t >= 3600:
            h, t = (h+1, t-3600)
        while t >= 60:
            m, t = (m+1, t-60)
        s += t

        cmds = (f'PROG:STEP:STARTV {float(start)}',
                f'PROG:STEP:ENDV {float(stop)}',
                f'PROG:STEP:TIME {int(h)},{int(m)},{float(s)}')

        for cmd in cmds:
            self.instrument.write(cmd)

    def cp_program(self, voltage: float = 0, current: float = 0,
                   power: float = 0, tracking_speed: int = 50) -> None:

        if not(1 <= int(tracking_speed) <= 100):
            # 1 == least aggressive most stable
            # 100 == most aggressive least stable
            raise ValueError('tracking_speed must be between 1-100')

        cmds = (f'PROG:CP:RESP {int(tracking_speed)}',
                f'PROG:CP:VOLT {float(voltage)}',
                f'PROG:CP:CURR {float(current)}',
                f'PROG:CP:POW {float(power)}')

        for cmd in cmds:
            self.instrument.write(cmd)

    def get_system_errors(self):

        response = self.instrument.query('SYST:ERR?')
        response = response.strip()

        error_status = response.split(',')

        error_code = int(error_status[0])
        error_message = error_status[1].replace('"', '')

        return (error_code, error_message)

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
        sleep(duration)
        self.set_voltage(start_level)
        return None

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

        for i in np.linspace(start, stop, int(n)):
            self.set_voltage(i)
            sleep(dt)
        return None

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
        sleep(dwell)
        self.ramp(stop, start, n=int(n/2), dt=dt)
        return None


if __name__ == '__main__':
    pass
