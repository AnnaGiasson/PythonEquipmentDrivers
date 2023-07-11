from typing import Any, Dict, List, Tuple

from pythonequipmentdrivers import VisaResource


class Chroma_62000P(VisaResource):
    """
    Chroma_62000P(address)

    address : str, address of the connected power supply

    object for accessing basic functionallity of the Chroma_62000P DC supply
    """

    def set_state(self, state: bool) -> None:
        """
        set_state(state)

        Enables/disables the output of the supply

        Args:
            state (bool): Supply state (True == enabled, False == disabled)
        """

        self.write_resource(f"CONF:OUTP {1 if state else 0}")

    def get_state(self) -> bool:
        """
        get_state()

        Retrives the current state of the output of the supply.

        Returns:
            bool: Supply state (True == enabled, False == disabled)
        """

        response = self.query_resource("CONF:OUTP?").rstrip('\n')
        return ("ON" in response)

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

    def toggle(self) -> None:
        """
        toggle()

        Reverses the current state of the Supply's output
        """

        self.set_state(self.get_state() ^ True)

    def set_voltage(self, voltage: float) -> None:
        """
        set_voltage(voltage)

        Sets the output voltage setpoint for the supply.

        Args:
            voltage (float): output voltage setpoint in Volts DC.
        """

        self.write_resource(f"SOUR:VOLT {voltage}")

    def get_voltage(self) -> float:
        """
        get_voltage()

        Retrives the current value output voltage setpoint.

        Returns:
            float: Output voltage setpoint in Volts DC.
        """

        response = self.query_resource("SOUR:VOLT?")
        return float(response)

    def set_current(self, current: float) -> None:
        """
        set_current(current)

        Sets the current limit threshold for the power supply.

        Args:
            current (float): Current Limit setpoint in Amps DC.
        """

        self.write_resource(f"SOUR:CURR {current}")

    def get_current(self) -> float:
        """
        get_current()

        Retrives the current limit threshold for the power supply.

        Returns:
            float: Current Limit setpoint in Amps DC.
        """

        response = self.query_resource("SOUR:CURR?")
        return float(response)

    def set_current_slew_rate(self, slew_rate: float) -> None:
        """
        set_current_slew_rate(slew_rate)

        Sets the current slew rate for the power supply's output current in
        A/ms

        Args:
            slew_rate (float): current slew rate in A/ms
        """

        self.write_resource(f"SOUR:CURR:SLEW {slew_rate}")

    def get_current_slew_rate(self) -> float:
        """
        get_current_slew_rate()

        gets the current slew rate for the power supply's output current

        Returns:
            float: current slew rate in A/ms
        """

        response = self.query_resource("SOUR:CURR:SLEW?")
        return float(response)

    def set_voltage_slew_rate(self, slew_rate: float) -> None:
        """
        set_voltage_slew_rate(slew_rate)

        Sets the voltage slew rate for the power supply's output voltage

        Args:
            slew_rate (float): voltage slew rate in V/ms
        """

        self.write_resource(f"SOUR:VOLT:SLEW {slew_rate}")

    def get_voltage_slew_rate(self):
        """
        get_voltage_slew_rate()

        Gets the voltage slew rate for the power supply's output voltage

        Returns:
            float: voltage slew rate in V/ms
        """

        response = self.query_resource("SOUR:VOLT:SLEW?")
        return float(response)

    def set_voltage_limit(self, v_limit: float) -> None:
        """
        set_voltage_limit(v_limit)

        Sets the voltage setpoint limit for the power supply's output voltage
        in Vdc

        Args:
            v_limit (float): voltage limit in Vdc

        """

        self.write_resource(f'SOUR:VOLT:LIM:HIGH {v_limit}')

    def get_voltage_limit(self) -> float:
        """
        get_voltage_limit()

        Returns the voltage setpoint limit for the power supply's output
        voltage in Vdc

        Returns:
            v_limit (float): voltage limit in Vdc
        """

        response = self.query_resource('SOUR:VOLT:LIM:HIGH?')
        return float(response)

    def measure_voltage(self) -> float:
        """
        measure_voltage()

        Retrives measurement of the voltage present across the supply's output.

        Returns:
            float: Measured Voltage in Volts DC
        """

        response = self.query_resource("FETC:VOLT?")
        return float(response)

    def measure_current(self) -> float:
        """
        measure_current()

        Retrives measurement of the current present through the supply.

        Returns:
            float: Measured Current in Amps DC.
        """

        response = self.query_resource("FETC:CURR?")
        return float(response)

    def measure_power(self) -> float:
        """
        measure_power()

        Retrives measurement of the power drawn from the supply.

        Returns:
            float: Measured power in Watts.
        """

        response = self.query_resource("FETC:POW?")
        return float(response)

    def get_status(self) -> Tuple[str, bool, str]:
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

        response = self.query_resource("FETC:STAT?")

        message_code, state, mode = response.split(',')

        message_code = int(message_code)
        messages = []
        for n, msg in enumerate(message_responses):
            if message_code & (1 << n):
                messages.append(msg)

        messages = ','.join(messages)

        output_state = (state == 'ON')

        return (messages, output_state, mode)

    def set_program_type(self, program_type: str) -> None:

        valid_program_types = {'STEP', 'LIST', 'CP'}

        if program_type.upper() not in valid_program_types:
            raise ValueError('Invalid program type'
                             f', use: {valid_program_types}')

        self.write_resource(f'PROG:MODE {program_type}')

    def set_program(self, n: int) -> None:
        self.write_resource(f'PROG:SEL {int(n)}')

    def get_program_type(self) -> str:

        response = self.query_resource('PROG:MODE?')
        return response.lower()

    def build_program(self, *sequence: Dict[str, Any], **kwargs) -> None:
        """
        build_program(*sequence, **kwargs)

        Creates a program and stores it on the source to be executed later
        (see run_program method). The program consists of a series of
        sequences that are executed in order until the end of the program. Each
        sequence is passed as a dictionary with the following possible keys:

            "type" (str, optional): Type of sequence, valid types are "auto",
                "manual", "trigger", and "skip". In the Auto mode the sequence
                is executed, then after amount of "time" the program moves to
                the get sequence. In the Manual mode the sequence executes
                before waiting for the user to press the 'enter' button on the
                front panel to continue the program. In the Trigger mode, the
                source waits for a rising/falling edge on rear IO pin 8 to
                continue the program. In Skip mode the sequence is skipped and
                does not execute. Defaults to "auto".
            "voltage" (float, optional): Voltage to set at the beginning of the
                sequence in Volts DC. Defaults to 0.
            "current" (float, optional): Current to set at the beginning of the
                sequence in Amps DC. Defaults to 0.
            "time" (float, optional): During of the sequence in seconds.
                Defaults to 0.
            "voltage_slew" (float, optional): Slew-rate using when
                transitioning the voltage between setpoints during the sequence
                in V/s. Defaults to 1000.
            "current_slew" (Union[float, str], optional): Slew-rate using when
                responding to loads current during the sequence in A/s, or
                alternatively the str "inf" to set to the max slew-rate.
                Defaults to "inf".
            "ttl" (int, optional): State of the digital output pins at the rear
                of the source. TTL represents an 8-bit number whose binary
                representation sets the state of the 8 digital output pins
                (pin 12[LSB] - pin 19[MSB]). Defaults to 0.

        A valid program must consist at least 1 sequence but cannot exceed 100
        sequences (limitation of source). As every sequence arugement has
        default values programs can be quickly build by suppling a spare set of
        sequences.
        Programs can be further modified using the keyword arguements listed
        below.

        Kwargs:
            program_number (int, optional): Location to store the resulting
                program. The source can store up to 10 programs numbered 1-10.
                Defaults to 1.
            clear (bool, optional): Whether or not to clear the existing
                contents of the specified program before loading in the new
                program.  Defaults to True.
            link (int, optional): Program number to jump to after the new
                program completes. If set to 0 the program does not jump to
                another program after finish execution. Defaults to 0.
            count (int, optional): Number of times to run the program before
                finishing execution. Repeats are performed before jumping to
                another program. Defaults to 1.
            save (bool, optional): Whether or not to save the program to
                non-volitile memory. Will only be saved if no errors occur when
                building the program. Defaults to False.
        """

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
            self.write_resource(cmd)

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
                self.write_resource(cmd)
        else:
            if kwargs.get('save', False):
                self.write_resource('PROG:SAVE')

    def get_program(self, program_type: str,
                    program_number: int
                    ) -> Tuple[Dict[str, int], List[Dict[str, Any]]]:

        # select specified program
        self.set_program_type(program_type)
        self.set_program(program_number)

        # get program metadata
        N = int(self.query_resource('PROG:MAX?'))  # number of sequences

        options = {'program_number': program_number,
                   'count': int(self.query_resource('PROG:COUNT?')),
                   'link': int(self.query_resource('PROG:LINK?'))}

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
            self.write_resource(f'PROG:SEQ:SEL {n}')  # select sequence

            response = self.query_resource('PROG:SEQ?')
            type_, volt, volt_sr, curr, curr_sr, ttl, t = response.split(',')

            # decode into same format used in self.build_program
            seq['type'] = valid_sequence_types[int(type_)]  # index into a list

            seq['voltage'] = float(volt)
            seq['voltage_slew'] = float(volt_sr)*1e3  # convert to V/s for user

            seq['current'] = float(curr)
            if ('INF' in curr_sr):
                seq['current_slew'] = 'INF'
            else:
                seq['current_slew'] = float(curr_sr)

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

        self.write_resource('PROG:RUN ON')

    def halt_program(self) -> None:
        """
        halt_program()

        Ends execution of the current program if one is running.
        """
        self.write_resource('PROG:RUN OFF')

    def get_program_state(self) -> bool:

        response = self.query_resource('PROG:RUN?')

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
            self.write_resource(cmd)

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
            self.write_resource(cmd)

    def get_system_errors(self):

        response = self.query_resource('SYST:ERR?')

        error_status = response.split(',')

        error_code = int(error_status[0])
        error_message = error_status[1].replace('"', '')

        return (error_code, error_message)
