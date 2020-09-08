from pythonequipmentdrivers import Scpi_Instrument as _Scpi_Instrument


class Keysight_33500B(_Scpi_Instrument):
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

    def set_waveform(self, wave_type, freq, amplitude, offset, source=1):
        self.instrument.write('SOUR{}:APPL:{} {}, {}, {}'.format(source,
                                                                 wave_type,
                                                                 freq,
                                                                 amplitude,
                                                                 offset))
        return None

    def get_waveform(self, source=1):
        response = self.instrument.query(f'SOUR{source}:APPL?')

        response = response.strip().replace('"', '')

        wave_type, wave_info = response.split()

        wave_type = wave_type.lower()
        freq, amp, off = map(float, wave_info.split(','))
        return (wave_type, freq, amp, off)

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


if __name__ == "__main__":
    pass
