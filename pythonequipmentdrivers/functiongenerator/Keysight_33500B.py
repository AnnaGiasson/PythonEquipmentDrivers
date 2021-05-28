from pythonequipmentdrivers import Scpi_Instrument
import numpy as np


class Keysight_33500B(Scpi_Instrument):
    """
    Keysight_33500B(address)

    address : str, address of the connected function generator

    object for accessing basic functionallity of the Keysight_33500B function
    generator

    For additional commands see programmers Manual:
    https://literature.cdn.keysight.com/litweb/pdf/33500-90901.pdf
    """

    valid_wave_types = ('ARB', 'DC', 'NOIS', 'PRBS', 'PULSE', 'RAMP', 'SIN',
                        'SQU', 'TRI')

    def set_waveform_config(self, source: int = 1, **kwargs):
        """[summary]

        Args:
            wave_type (str, optional): [description]
            frequency (float, optional): [description]
            amplitude (float, optional): [description]
            offset (float, optional): [description]
            source (int, optional): [description]. Defaults to 1.

        """
        wave_type = kwargs.get('wave_type', self.get_wave_type(source))
        frequency = kwargs.get('frequency', self.get_frequency(source))
        amplitude = kwargs.get('amplitude', self.get_voltage(source))
        offset = kwargs.get('offset', self.get_voltage_offset(source))

        self.instrument.write('SOUR{}:APPL:{} {}, {}, {}'.format(source,
                                                                 wave_type,
                                                                 frequency,
                                                                 amplitude,
                                                                 offset))
        return None

    def get_waveform_config(self, source: int = 1):
        response = self.instrument.query(f'SOUR{source}:APPL?')

        response = response.strip().replace('"', '')

        wave_type, wave_info = response.split()

        wave_type = wave_type.lower()
        freq, amp, off = map(float, wave_info.split(','))
        return (wave_type, freq, amp, off)

    def set_voltage(self, voltage: float, source: int = 1):
        self.instrument.write(f'SOUR{source}:VOLT {voltage}')
        return None

    def get_voltage(self, source: int = 1):
        response = self.instrument.query(f'SOUR{source}:VOLT?')
        return float(response)

    def set_voltage_offset(self, offset: float, source: int = 1):
        self.instrument.write(f'SOUR{source}:VOLT:OFFS {offset}')
        return None

    def get_voltage_offset(self, source: int = 1):
        response = self.instrument.query(f'SOUR{source}:VOLT:OFFS?')
        return float(response)

    def set_voltage_high(self, voltage: float, source: int = 1):
        self.instrument.write(f'SOUR{source}:VOLT:HIGH {voltage}')
        return None

    def get_voltage_high(self, source: int = 1):
        response = self.instrument.query(f'SOUR{source}:VOLT:HIGH?')
        return float(response)

    def set_voltage_low(self, voltage: float, source: int = 1):
        self.instrument.write(f'SOUR{source}:VOLT:LOW {voltage}')
        return None

    def get_voltage_low(self, source: int = 1):
        response = self.instrument.query(f'SOUR{source}:VOLT:LOW?')
        return float(response)

    def set_frequency(self, frequency: float, source: int = 1):
        self.instrument.write(f'SOUR{source}:FREQ {frequency}')
        return None

    def get_frequency(self, source: int = 1):
        response = self.instrument.query(f'SOUR{source}:FREQ?')
        return float(response)

    def set_wave_type(self, wave_type: str, source: int = 1):
        self.instrument.write(f'SOUR{source}:FUNC {wave_type}')
        return None

    def get_wave_type(self, source: int = 1):
        response = self.instrument.query(f'SOUR{source}:FUNC?')
        return response.strip().lower()

    def set_pulse_dc(self, duty_cycle, source: int = 1):
        self.instrument.write(f'SOUR{source}:FUNC:PULSE:DCYC {duty_cycle}')
        return None

    def get_pulse_dc(self, source: int = 1):
        response = self.instrument.query(f'SOUR{source}:FUNC:PULSE:DCYC?')
        return float(response)

    def set_pulse_width(self, width, source: int = 1):
        self.instrument.write(f'SOUR{source}:FUNC:PULSE:WIDT {width}')
        return None

    def get_pulse_width(self, source: int = 1):
        response = self.instrument.query(f'SOUR{source}:FUNC:PULSE:WIDT?')
        return float(response)

    def set_pulse_period(self, period, source: int = 1):
        self.instrument.write(f'SOUR{source}:FUNC:PULSE:PER {period}')
        return None

    def get_pulse_period(self, source: int = 1):
        response = self.instrument.query(f'SOUR{source}:FUNC:PULSE:PER?')
        return float(response)

    def set_pulse_edge_time(self, time, which: str = 'both', source: int = 1):
        which = which.upper()
        if which == 'BOTH':
            self.instrument.write(f'SOUR{source}:FUNC:PULSE:TRAN {time}')
        elif which in ['RISE', 'RISING', 'R', 'LEAD', 'LEADING']:
            self.instrument.write(f'SOUR{source}:FUNC:PULSE:TRAN:LEAD {time}')
        elif which in ['FALL', 'FALLING', 'F', 'TRAIL', 'TRAILING']:
            self.instrument.write(f'SOUR{source}:FUNC:PULSE:TRAN:TRA {time}')
        return None

    def get_pulse_edge_time(self, which: str = 'both', source: int = 1):
        cmd_str = f'SOUR{source}:FUNC:PULSE:TRAN'
        which = which.upper()
        if which == 'BOTH':
            response = [self.instrument.query(cmd_str + 'LEAD?'),
                        self.instrument.query(cmd_str + 'TRA?')]
        elif which in ['RISE', 'RISING', 'R', 'LEAD', 'LEADING']:
            response = self.instrument.query(cmd_str + 'LEAD?')
        elif which in ['FALL', 'FALLING', 'F', 'TRAIL', 'TRAILING']:
            response = self.instrument.query(cmd_str + 'TRA?')
        else:
            raise ValueError('Invalid option for "which" arg')
        if isinstance(response, list):
            return tuple(map(float, response))
        else:
            return float(response)

    def set_pulse_hold(self, param: str, source: int = 1):
        param = param.upper()
        if param not in ['DCYC', 'WIDT']:
            raise ValueError(f"Invalid param {param}, must by 'DCYC'/'WIDT'")
        self.instrument.write(f'SOUR{source}:FUNC:PULSE:HOLD {param}')
        return None

    def get_pulse_hold(self, source: int = 1):
        response = self.instrument.query(f'SOUR{source}:FUNC:PULSE:HOLD?')
        return response.strip().lower()

    def set_square_dc(self, duty_cycle, source: int = 1):
        self.instrument.write(f'SOUR{source}:FUNC:SQU:DCYC {duty_cycle}')
        return None

    def get_square_dc(self, source: int = 1):
        response = self.instrument.query(f'SOUR{source}:FUNC:SQU:DCYC?')
        return float(response)

    def set_square_period(self, period, source: int = 1):
        self.instrument.write(f'SOUR{source}:FUNC:SQU:PER {period}')
        return None

    def get_square_period(self, source: int = 1):
        response = self.instrument.query(f'SOUR{source}:FUNC:SQU:PER?')
        return float(response)

    def set_burst_mode(self, mode: str, source: int = 1):
        mode = mode.upper()
        if mode not in ['TRIG', 'GAT']:
            raise ValueError('Invalid mode, valid modes are "TRIG"/"GAT"')
        self.instrument.write(f'SOUR{source}:BURS:MODE {mode}')
        return None

    def get_burst_mode(self, source: int = 1):
        response = self.instrument.query(f'SOUR{source}:BURS:MODE?')
        return response.strip().lower()

    def set_burst_gate_polarity(self, polarity: str, source: int = 1):
        polarity = polarity.upper()
        if polarity not in ['NORM', 'INV']:
            raise ValueError('Invalid mode, valid modes are "NORM"/"INV"')
        self.instrument.write(f'SOUR{source}:BURS:GATE:POL {polarity}')
        return None

    def get_burst_gate_polarity(self, source: int = 1):
        response = self.instrument.query(f'SOUR{source}:BURS:GATE:POL?')
        return response.strip().lower()

    def set_burst_ncycles(self, ncycles: int, source: int = 1):
        str_options = ['INF', 'MIN', 'MAX']
        if isinstance(ncycles, int):
            self.instrument.write(f'SOUR{source}:BURS:NCYC {ncycles}')
        elif isinstance(ncycles, str) and (ncycles.upper() in str_options):
            self.instrument.write(f'SOUR{source}:BURS:NCYC {ncycles.upper()}')
        else:
            raise ValueError('invalid entry for ncycles')
        return None

    def get_burst_ncycles(self, source: int = 1):
        response = self.instrument.query(f'SOUR{source}:BURS:NCYC?')
        return int(float(response))

    def set_burst_phase(self, phase: float, source: int = 1):
        str_options = ['MIN', 'MAX']
        if isinstance(phase, (float, int)):
            self.instrument.write(f'SOUR{source}:BURS:PHASE {phase}')
        elif isinstance(phase, str) and (phase.upper() in str_options):
            self.instrument.write(f'SOUR{source}:BURS:PHASE {phase.upper()}')
        else:
            raise ValueError('invalid entry for phase')
        return None

    def get_burst_phase(self, source: int = 1):
        response = self.instrument.query(f'SOUR{source}:BURS:PHASE?')
        return float(response)

    def set_burst_state(self, state: int, source: int = 1):
        self.instrument.write(f'SOUR{source}:BURS:STAT {state}')
        return None

    def get_burst_state(self, source: int = 1):
        response = self.instrument.query(f'SOUR{source}:BURS:STAT?')
        return int(response)

    def trigger(self, source: int = 1):
        self.instrument.write(f'TRIG{source}')
        return None

    def get_trigger_count(self, source: int = 1):
        response = self.instrument.query(f'TRIG{source}:COUN?')
        return int(float(response))

    def set_trigger_delay(self, delay, source: int = 1):
        str_options = ['MIN', 'MAX']
        if isinstance(delay, (float, int)):
            self.instrument.write(f'TRIG{source}:DEL {delay}')
        elif isinstance(delay, str) and (delay.upper() in str_options):
            self.instrument.write(f'TRIG{source}:DEL {delay.upper()}')
        else:
            raise ValueError('invalid entry for delay')
        return None

    def get_trigger_delay(self, source: int = 1):
        response = self.instrument.query(f'TRIG{source}:DEL?')
        return float(response)

    def set_trigger_source(self, trig_source, source: int = 1):
        trig_opts = ['IMM', 'IMMEDIATE', 'EXT', 'EXTERNAL',
                     'TIM', 'TIMER', 'BUS']
        trig_source = trig_source.upper()
        if trig_source in trig_opts:
            self.instrument.write(f'TRIG{source}:SOUR {trig_source}')
        else:
            raise ValueError(f'Invalid arg for trig_source ({trig_opts})')
        return None

    def get_trigger_source(self, source: int = 1):
        response = self.instrument.query(f'TRIG{source}:SOUR?')
        return response.strip().lower()

    @property
    def angle_unit(self):
        return self.instrument.query('UNIT:ANGL?').strip().lower()

    def set_voltage_display_mode(self, mode: str):
        mode = mode.upper()
        if mode in ['AMPL', 'HIGH', 'AMPLITUDEOFF', 'HIGHLOW']:
            self.instrument.write(f'DISP:UNIT:VOLT {mode}')
        else:
            raise ValueError('Invalid value for arg "mode"')
        return None

    @property
    def voltage_display_mode(self):
        response = self.instrument.query('DISP:UNIT:VOLT?')
        return response.strip().lower()

    def set_pulse_duration_display_mode(self, mode: str):
        mode = mode.upper()
        if mode in ['WIDT', 'WIDTH', 'DUTY']:
            self.instrument.write(f'DISP:UNIT:PULS {mode}')
        else:
            raise ValueError('Invalid value for arg "mode"')
        return None

    @property
    def pulse_duration_display_mode(self):
        response = self.instrument.query('DISP:UNIT:PULS?')
        return response.strip().lower()

    def set_horizontal_display_mode(self, mode: str):
        mode = mode.upper()
        if mode in ['FREQ', 'FREQUENCY', 'PER', 'PERIOD']:
            self.instrument.write(f'DISP:UNIT:RATE {mode}')
        else:
            raise ValueError('Invalid value for arg "mode"')
        return None

    @property
    def horizontal_display_mode(self):
        response = self.instrument.query('DISP:UNIT:RATE?')
        return response.strip().lower()

    def set_output_state(self, state: int, source: int = 1):
        self.instrument.write(f"OUTP{source} {state}")
        return None

    def get_output_state(self, source: int = 1):
        response = self.instrument.query(f"OUTP{source}?")
        return int(response)

    def set_output_impedance(self, impedance, source=1):
        """Valid options are 1-10k, min, max, and inf"""
        self.instrument.write(f'OUTP{source}:LOAD {impedance}')
        return None

    def get_output_impedance(self, source=1):
        response = self.instrument.query(f'OUTP{source}:LOAD?')
        return float(response)

    def set_display_text(self, text: str):
        self.instrument.write(f'DISP:TEXT "{text}"')
        return None

    def get_display_text(self):
        response = self.instrument.query('DISP:TEXT?')
        text = response.strip().replace('"', '')
        return text

    def clear_display_text(self):
        return self.set_display_text("")

    def store_arbitrary_waveform(self, data, arb_name):
        if not (8 < len(data) < 65536):
            raise ValueError('data must be between 8 and 65536 samples')

        data = np.array(data)

        data -= data.mean()  # symmetric
        data /= data.max()  # spans +/- 1
        data *= 32767  # spans +/- 32767
        data = data.astype(int)

        # send data
        cmd_str = "SOUR:DATA:ARB1:DAC"
        self.instrument.write('{} {},{}'.format(cmd_str,
                                                arb_name,
                                                ",".join(map(str, data))))

        return None


if __name__ == "__main__":
    pass
