from pythonequipmentdrivers import Scpi_Instrument
import numpy as np


class Agilent_33250A(Scpi_Instrument):
    """
    Agilent_33250A(address)

    address : str, address of the connected function generator

    object for accessing basic functionallity of the Agilent_33250A function
    generator
    """

    valid_wave_types = ('SIN', 'SQU', 'RAMP', 'PULSE', 'NOIS', 'DC', 'USER')

    def set_output_state(self, state: bool) -> None:
        self.instrument.write(f"OUTP {1 if state else 0}")

    def get_output_state(self) -> bool:
        response = self.instrument.query("OUTP?")
        return bool(int(response))

    def set_output_impedance(self, impedance) -> None:
        """
        Valid options are 1-10k, min, max, and inf
        """

        valid_str = ('MIN', 'MAX', 'INF')

        if isinstance(impedance, (float, int)):
            z = np.clip(impedance, 10, 10e3)
            self.instrument.write(f'OUTP:LOAD {z}')
        elif isinstance(impedance, str) and (impedance.upper() in valid_str):
            self.instrument.write(f'OUTP:LOAD {impedance.upper()}')

    def get_output_impedance(self) -> float:
        response = self.instrument.query('OUTP:LOAD?')
        return float(response)

    def set_waveform_type(self, waveform: str) -> None:

        wave = str(waveform).upper()
        if (wave in self.valid_wave_types):
            self.instrument.write(f'FUNC {wave}')
        else:
            raise ValueError('Invalide Waveform type. '
                             f'Supported: {self.valid_wave_types}')

    def get_waveform_type(self) -> str:
        response = self.instrument.query('FUNC?')
        wave = response.strip()
        return wave.upper()

    def set_voltage_amplitude(self, voltage: float) -> None:
        self.instrument.write(f'VOLT {float(voltage)}')

    def get_voltage_amplitude(self) -> float:
        response = self.instrument.query('VOLT?')
        return float(response)

    def set_voltage_offset(self, voltage: float) -> None:
        self.instrument.write(f'VOLT:OFFS {float(voltage)}')

    def get_voltage_offset(self) -> float:
        response = self.instrument.query('VOLT:OFFS?')
        return float(response)

    def set_voltage_high(self, voltage: float) -> None:
        self.instrument.write(f'VOLT:HIGH {float(voltage)}')

    def get_voltage_high(self) -> float:
        response = self.instrument.query('VOLT:HIGH?')
        return float(response)

    def set_voltage_low(self, voltage: float) -> None:
        self.instrument.write(f'VOLT:LOW {float(voltage)}')

    def get_voltage_low(self) -> float:
        response = self.instrument.query('VOLT:LOW?')
        return float(response)

    def set_frequency(self, frequency: float) -> None:
        self.instrument.write(f'FREQ {float(frequency)}')

    def get_frequency(self) -> float:
        response = self.instrument.query('FREQ?')
        return float(response)

    def set_voltage_auto_range(self, state: bool) -> None:
        self.instrument.write(f"VOLT:RANG:AUTO {'ON' if state else 'OFF'}")

    def get_voltage_auto_range(self) -> bool:
        response = self.instrument.query('VOLT:RANG:AUTO?')
        if '1' in response:
            return True
        return False

    def set_burst_state(self, state: bool) -> None:
        self.instrument.write('BURS:STAT {}'.format(1 if state else 0))

    def set_pulse_period(self, period: float) -> None:
        self.instrument.write(f'PULSE:PER {float(period)}')

    def get_pulse_period(self):
        response = self.instrument.query('PULSE:PER?')
        return float(response)

    def set_pulse_width(self, width) -> None:
        self.instrument.write(f'PULSE:WIDT {float(width)}')

    def get_pulse_width(self) -> float:
        response = self.instrument.query('PULSE:WIDT?')
        return float(response)

    def set_square_duty_cycle(self, dc) -> None:
        self.instrument.write(f'FUNC:SQU:DCYCLE {float(dc)}')

    def get_square_duty_cycle(self) -> float:
        response = self.instrument.query('FUNC:SQU:DCYCLE?')
        return float(response)

    def get_burst_state(self, source: int = 1) -> bool:
        response = self.instrument.query(f'SOUR{int(source)}:BURS:STAT?')
        return bool(int(response))

    def set_burst_mode(self, mode: str) -> None:
        mode = mode.upper()
        burst_modes = ('TRIG', 'GAT')
        if mode not in burst_modes:
            raise ValueError(f'Invalid mode, valid modes are: {burst_modes}')
        self.instrument.write(f'BURS:MODE {mode}')

    def get_burst_mode(self) -> str:
        response = self.instrument.query('BURS:MODE?')
        return response.strip().lower()

    def set_burst_ncycles(self, ncycles: int) -> None:
        str_options = ['INF', 'MIN', 'MAX']
        if isinstance(ncycles, int):
            self.instrument.write(f'BURS:NCYC {ncycles}')
        elif isinstance(ncycles, str) and (ncycles.upper() in str_options):
            self.instrument.write(f'BURS:NCYC {ncycles.upper()}')
        else:
            raise ValueError('invalid entry for ncycles')

    def get_burst_ncycles(self):
        response = self.instrument.query('BURS:NCYC?')
        return int(float(response))

    def trigger(self) -> None:
        self.instrument.write('TRIG')
