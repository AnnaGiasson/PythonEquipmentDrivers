from .HP_34401A import HP_34401A as _HP_34401A


# TOdO: Add in additional measurement functionallity not written in the
# original HP_34401A Class. Look into adding functionallity for adjusting the
# triggering settings


class Keysight_34461A(_HP_34401A):
    """
    Keysight_34461A()

    address: str, address of the connected multimeter

    factor: float, multiplicitive scale for all measurements defaults to 1.

    Object for accessing basic functionallity of the Keysight_34461A multimeter
    The factor term allows for measurements to be multiplied by some number
    before being returned. For example, in the case of measuring the voltage
    across a current shunt this factor can represent the conductance of the
    shunt. This factor defaults to 1 (no effect on measurement).

    Additional Information:
    https://literature.cdn.keysight.com/litweb/pdf/34460-90901.pdf
    """
    valid_ranges = {'AUTO': '',
                    'MIN': 'MIN,',
                    'MAX': 'MAX,',
                    'DEF': 'DEF,',
                    0.1: '0.1,',
                    1: '1,',
                    10: '10,',
                    100: '100,',
                    1000: '1000,',
                    '0.1': '0.1,',
                    '1': '1,',
                    '10': '10,',
                    '100': '100,',
                    '1000': '1000,'}
    valid_cranges = {'AUTO': '',
                     'MIN': 'MIN,',
                     'MAX': 'MAX,',
                     'DEF': 'DEF,',
                     0.0001: '0.0001,',
                     0.001: '0.001,',
                     0.01: '0.01,',
                     0.1: '0.1,',
                     1: '1,',
                     3: '3,',
                     '0.0001': '0.0001,',
                     '0.001': '0.001,',
                     '0.01': '0.01,',
                     '0.1': '0.1,',
                     '1': '1,',
                     '3': '3,'}
    valid_Rranges = {'AUTO': '',
                     'MIN': 'MIN,',
                     'MAX': 'MAX,',
                     'DEF': 'DEF,',
                     100: '100,',
                     1E3: '1E3,',
                     10E3: '10E3,',
                     100E3: '100E3,',
                     1E6: '1E6,',
                     10E6: '10E6,',
                     100E6: '100E6,',
                     '100': '100,',
                     '1E3': '1E3,',
                     '10E3': '10E3,',
                     '100E3': '100E3,',
                     '1E6': '1E6,',
                     '10E6': '10E6,',
                     '100E6': '100E6,'}

    def set_display_text(self, text: str):
        self.instrument.write(f'DISP:TEXT "{text}"')
        return None

    def get_display_text(self):
        response = self.instrument.query('DISP:TEXT?')
        text = response.strip().replace('"', '')
        return text

    def clear_display_text(self):
        return self.set_display_text("")

    def set_display_state(self, state: int):
        if state:
            self.instrument.write('DISP ON')
        else:
            self.instrument.write('DISP OFF')
        return None

    def get_display_state(self):
        response = self.instrument.query('DISP?')
        return int(response)

    def set_display_mode(self, mode: str):
        mode = mode.upper()
        if mode not in ['NUM', 'HIST', 'TCH', 'MET']:
            raise ValueError(f'Invalid mode for arg "mode" ({mode})')
        self.instrument.write(f'DISP:VIEW {mode}')
        return None

    def get_display_mode(self):
        response = self.instrument.query('DISP:VIEW?')
        return response.strip()

    def set_label_text(self, label: str):
        self.instrument.write(f'SYSTEM:LABEL "{label}"')
        return None

    def get_label_text(self):
        response = self.instrument.query('SYSTEM:LABEL?')
        label = response.strip().replace('"', '')
        return label

    def clear_label_text(self):
        self.set_label_text('')
        return None


if __name__ == '__main__':
    pass
