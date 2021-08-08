from typing import Union
from pythonequipmentdrivers import Scpi_Instrument


class PPSC_3150AFX(Scpi_Instrument):
    """
    PPSC_3150AFX(address)

    address : str, address of the connected power supply

    object for accessing basic functionallity of the PPSC_3150AFX AC supply

    For additional commands see programmers Manual:
    https://www.caltest.de/produkte/assets/afx_series_power_source_operation_manual-pn150185-10_x11_caltest.pdf
    """

    def __init__(self, address, **kwargs):
        super().__init__(address, **kwargs)
        return None

    def set_state(self, state: bool) -> None:
        """
        set_state(state)

        Enables/disables the output of the supply

        Args:
            state (bool): Supply state (True == enabled, False == disabled)
        """

        self.instrument.write(f"OUTP:STAT {1 if state else 0}")

    def get_state(self) -> bool:
        """
        get_state()

        Retrives the current state of the output of the supply.

        Returns:
            bool: Supply state (True == enabled, False == disabled)
        """

        state = self.instrument.query("OUTP:STAT?")
        return (int(state) == 1)

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

    def toggle(self, return_state=False) -> Union[None, bool]:
        """
        toggle(return_state=False)

        return_state: boolean, whether or not to return the state of the output
                      relay

        reverses the current state of the power supply's output relay

        if return_state = True the boolean state of the relay after toggle() is
        executed will be returned
        """

        self.set_state(self.get_state() ^ True)

        if return_state:
            return self.get_state()

    def sleep(self) -> None:
        """
        sleep()

        Forces the supply to enter sleep mode. If the supply's output is on
        when this command is issued it will be turned off.
        Sleep mode will turn off the internal power supply for the output,
        which will cause a delay in the next subsequent startup as the internal
        supply reboots. Sleep mode will also disable the front panel fans if
        the supply's heatsink is sufficiently cool.
        """

        if self.get_state():
            self.off()

        self.instrument.write("OUTPUT:ALL OFF")

    def set_range(self, voltage_range):
        """
        set_range(voltage_range)

        voltage_range: int, output voltage range of the power supply.
            valid options are 0 (low range) and 1 (high range)

        set the output voltage range of the power supply to the value specifed
        by "voltage_range"
        """

        self.instrument.write(f"RANG {voltage_range}")
        return None

    def get_range(self):
        """
        get_range()

        retrieves the output voltage range of the power supply

        returns: int, 0 for low range and 1 for high range
        """

        response = self.instrument.query("RANG?")
        return int(response)

    def set_voltage(self, voltage, phase=''):
        """
        set_voltage(voltage, phase='')

        voltage: float or int, amplitude to set output to in Vrms
        phase (optional) : int or "", phase to set amplitude of
            valid values are 1,2,3, or "".
            "" is default and will set all three phases to the same value

        set the voltage of one or all phases to specifed value
        """

        self.instrument.write(f"SOUR:VOLT{phase} {voltage}")
        return None

    def get_voltage(self, phase=''):
        """
        get_voltage(phase='')

        phase (optional) : int or "", phase to get amplitude of
            valid values are 1,2,3, or ""

        gets the voltage setpoint of one or all phases (Vrms)
        returns: float / list of floats
        """

        response = self.instrument.query(f'SOUR:VOLT{phase}?')

        if phase == '':
            return [float(x) for x in response.split(',')]
        else:
            return float(response)

    def set_frequency(self, frequency):
        """
        set_frequency(frequency)

        frequency: float or int, frequency to set in Hz

        sets the frequency of the output voltage
        """

        self.instrument.write(f"SOUR:FREQ {frequency}")
        return None

    def get_frequency(self):
        """
        get_frequency()

        returns the frequency setpoint of the power supply

        returns : float
        """

        data = self.instrument.query("SOUR:FREQ?")
        return float(data)

    def measure_voltage_rms(self, phase=''):
        """
        measure_voltage_rms(phase='')

        phase (optional) : int or "", phase to get amplitude of
            valid values are 1,2,3, or ""

        returns measurement of the output voltage of the power supply for the
        specified phase(s) in Vrms
        returns: float / list of floats
        """

        response = self.instrument.query(f'MEAS:VOLT:AC{phase}?')

        if phase == '':
            return [float(x) for x in response.split(',')]
        else:
            return float(response)

    def measure_voltage_line_to_line(self, phase=''):
        """
        measure_voltage_line_to_line(phase='')

        phase (optional) : int or "", phase to get amplitude of
            valid values are 1,2,3, or ""

        returns measurement of the output voltage between phases of the power
        supply for the specified phase(s) in Vrms
        returns: float / list of floats
        """

        response = self.instrument.query(f'MEAS:VLL{phase}?')

        if phase == '':
            return [float(x) for x in response.split(',')]
        else:
            return float(response)

    def measure_voltage_dc(self, phase=''):
        """
        measure_voltage_dc(phase='')

        phase (optional) : int or "", phase to get amplitude of
            valid values are 1,2,3, or ""

        returns measurement of the dc voltage of the power supply for the
        specified phase(s) in Vdc
        returns: float / list of floats
        """

        response = self.instrument.query(f'MEAS:VOLT:DC{phase}?')

        if phase == '':
            return [float(x) for x in response.split(',')]
        else:
            return float(response)

    def measure_frequency(self):
        """
        measure_frequency()

        returns measurement of the output frequency of the power supply in Hz
        returns: float
        """

        response = self.instrument.query('MEAS:FREQ?')
        return float(response)

    def measure_current_rms(self, phase=''):
        """
        measure_current_rms(phase='')

        phase (optional) : int or "", phase to get amplitude of
            valid values are 1,2,3, or ""

        returns measurement of the current of the power supply for the
        specified phase(s) in Arms
        returns: float / list of floats
        """

        response = self.instrument.query(f'MEAS:CURR{phase}?')

        if phase == '':
            return [float(x) for x in response.split(',')]
        else:
            return float(response)

    def measure_current_dc(self, phase=''):
        """
        measure_current_dc(phase='')

        phase (optional) : int or "", phase to get amplitude of
            valid values are 1,2,3, or ""

        returns measurement of the dc current of the power supply for the
        specified phase(s) in Adc
        returns: float / list of floats
        """

        response = self.instrument.query(f'MEAS:CURR:DC{phase}?')

        if phase == '':
            return [float(x) for x in response.split(',')]
        else:
            return float(response)

    def measure_current_peak(self, phase=''):
        """
        measure_current_peak(phase='')

        phase (optional) : int or "", phase to get amplitude of
            valid values are 1,2,3, or ""

        returns measurement of the peak current of the power supply for the
        specified phase(s) in Adc
        returns: float / list of floats
        """

        response = self.instrument.query(f'MEAS:CURR:PEAK{phase}?')

        if phase == '':
            return [float(x) for x in response.split(',')]
        else:
            return float(response)

    def measure_current_crest(self, phase=''):
        """
        measure_current_crest(phase='')

        phase (optional) : int or "", phase to get amplitude of
            valid values are 1,2,3, or ""

        returns measurement of the crest factor of the power supply's output
        current for the specified phase(s)
        returns: float / list of floats
        """

        response = self.instrument.query(f'MEAS:CURR:CREST{phase}?')

        if phase == '':
            return [float(x) for x in response.split(',')]
        else:
            return float(response)

    def measure_power_real(self, phase=''):
        """
        measure_power_real(phase='')

        phase (optional) : int or "", phase to get amplitude of
            valid values are 1,2,3, or ""

        returns measurement of the real power drawn from the power supply for
        the specified phase(s) in W
        returns: float / list of floats
        """

        response = self.instrument.query(f'MEAS:POW{phase}?')

        if phase == '':
            # convert from kW to W
            return [1000*float(x) for x in response.split(',')]
        else:
            return 1000*float(response)

    def measure_power_apparent(self, phase=''):
        """
        measure_power_apparent(phase='')

        phase (optional) : int or "", phase to get amplitude of
            valid values are 1,2,3, or ""

        returns measurement of the complex power drawn from the power supply
        for the specified phase(s) in VA
        returns: float / list of floats
        """

        response = self.instrument.query(f'MEAS:KVA{phase}?')

        if phase == '':
            # convert from kVA to VA
            return [1000*float(x) for x in response.split(',')]
        else:
            return 1000*float(response)

    def measure_power_factor(self, phase=''):
        """
        measure_power_factor(phase='')

        phase (optional) : int or "", phase to get amplitude of
            valid values are 1,2,3, or ""

        returns measurement of the power factor of the power supply for the
        specified phase(s)
        returns: float / list of floats
        """

        response = self.instrument.query(f'MEAS:PF{phase}?')

        if phase == '':
            return [float(x) for x in response.split(',')]
        else:
            return float(response)

    def measure_temperature_ambient(self):
        """
        measure_temperature_ambient()

        returns measurement of the ambient temperature of the power supply in
        degrees Celcuis
        returns: float
        """

        response = self.instrument.query('MEAS:TEMP:AMB?')
        return float(response)

    def store_waveform(self, waveform_number, data):
        """
        store_waveform(waveform_number, data)

        waveform_number: int, index in supply's memory where the waveform will
                         be stored
        data: iterable (array, list, tuple, etc), a list of datapoints that
              define the waveform. must have a length 1024, datapoints should
              be floats, waveforms should be normalized to the range -1:1
        """

        wvfm_str = ','.join([str(x) for x in data])
        command_str = f"WAVEFORM:DEF {waveform_number},{wvfm_str}"
        self.instrument.write(command_str)
        return None

    def run_sequence(self):
        """
        run_sequence()

        executes the currently loaded transient sequence
        """

        self.instrument.write('PROG:TRAN RUN')
        return None

    def build_sequence(self, sequence_list, sequence_num=1,
                       v_steady_state=None, f=50, voltage_range=1):

        """
        build_sequence(sequence_list,
        sequence_num=1, v_steady_state=None, f=50, voltage_range=1)

        sequence_list: list, a list contains voltage-time pairs for each step
                       in the sequence.
        sequence_num (optional): int, index of the stored sequence in the
                                 supplies memory (default=1).
        v_steady_state (optional): float/None, steady-state value of RMS
                                   voltage the supply with default to once the
                                   sequence is completed. Default is None which
                                   will use the value currently set on the
                                   supply.
        f (optional): float/int frequency of the supply's output voltage
                      (in Hz) to be used throughout the sequence, default is 50
                      Hz
        voltage_range (optional): int, output voltage range to use through the
                                  test. Default is 1. valid options are 0
                                  (low range) and 1 (high range)

        Builds and loads a transient sequence based on the info provided in
        sequence_list. sequence_list should be a list containing either tuples
        or lists of length 2 which provide the supply voltage and duration of
        each step (in that order).

        """

        if v_steady_state is None:
            v_steady_state = self.get_voltage(1)

        self.instrument.write(f'PROG:NAME {sequence_num}')

        sequence_str = f"""
                        FORM,3,COUPL,DIRECT,VOLT:MODE,0,
                        CONFIG,0,RANG,{voltage_range},FREQ,{f},
                        VOLT1,{v_steady_state},VOLT2,{v_steady_state},
                        VOLT3,{v_steady_state},
                        VOLT:ALC:STAT,1,CURR:OV,0,
                        CURR:LIM1,41.667,CURR:LIM2,41.667,CURR:LIM3,41.667,
                        IPROT:STAT,0,CURR:PROT:LEV,41.667,IPEAK:LIM,104.000,
                        PHAS2,120.000,PHAS3,240.000,
                        WAVEFORM1,1,WAVEFORM2,1,WAVEFORM3,1,
                        VOLT:DC1,0.000,VOLT:DC2,0.000,VOLT:DC3,0.000,
                        POW:LIM1,5.000,POW:LIM2,5.000,POW:LIM3,5.000,
                        KVA:LIM1,5.000,KVA:LIM2,5.000,KVA:LIM3,5.000,
                        PPROT:STAT,0,POW:PROT:LEV,5.000,KVA:PROT:LEV,5.000,
                        PROT:TDELAY,5,
                        FREQ:SLEW,5.000,VOLT:SLEW,10.000,
                        VOLT:DC:SLEW,10.000,
                        UPDATEPH,0.000,RAMP,0.0002,VPEAK:MARG,100.000,
                        EVENTS,1,AUTORMS,0,
                        """

        sequence_str += f"NSEGS,{int(len(sequence_list))},"

        for idx, step in enumerate(sequence_list, start=1):
            v, t = step
            sequence_str += f"""
                             SEG,{idx},FSEG,{f},
                             VSEG1,{v},VSEG2,{v},VSEG3,{v},
                             VDCSEG1,0.00,VDCSEG2,0.00,VDCSEG3,0.00,
                             PSEG2,120.00,PSEG3,240.00,
                             WFSEG1,1,WFSEG2,1,WFSEG3,1,
                             TSEG,{t},
                             """

        sequence_str += 'LAST'

        sequence_str = sequence_str.replace('\n', '')
        sequence_str = sequence_str.replace('    ', '')

        command_str = f"PROG:DEF {int(sequence_num)},INTERNAL,{sequence_str}"
        self.instrument.write(command_str)
        self.instrument.write(f'PROG:EXEC {int(sequence_num)}')
        return None


if __name__ == '__main__':
    pass
