from pythonequipmentdrivers import Scpi_Instrument as _Scpi_Instrument
import numpy as np


class Lecroy_WR8xxx(_Scpi_Instrument):
    """
    Lecroy_WR8xxx(address)

    address : str, address of the connected oscilloscope

    object for accessing basic functionallity of the Lecroy_WR8xxx
    Family of Oscilloscopes

    Addtional information on the remote control capabilities of the scope can
    be accessed at:
    http://cdn.teledynelecroy.com/files/manuals/maui-remote-control-and-automation-manual.pdf
    """

    valid_trigger_states = ['AUTO', 'NORM', 'SINGLE', 'STOP']
    valid_trigger_slopes = {'POS': 'POS', 'RISE': 'POS',
                            'NEG': 'NEG', 'FALL': 'NEG'}

    def __init__(self, address):
        super().__init__(address)
        self.instrument.clear()
        return

    def select_channel(self, channel, state):
        """
        select_channel(channel)

        channel: int, channel number of channel
                    valid options are 1,2,3, and 4

        state: int, whether or not the respective channel is
                selected/visable on the screen. Valid options are 0 or 1

        Enables/disables the display of the specified channel.
        """

        cmd_str = f'C{channel}:TRACE '
        if state == 1:
            cmd_str += "ON"
        elif state == 0:
            cmd_str += "OFF"
        else:
            raise ValueError(f"Invalid arguement 'state': {state}")
        self.instrument.write(cmd_str)
        return

    def set_channel_scale(self, channel, scale):
        """
        set_channel_scale(channel, scale)

        channel: int, channel number of channel

        scale: int/float, scale of the channel amplitude across one
        vertical division on the display.

        sets the scale of vertical divisons for the specified channel
        """

        self.instrument.write(f"C{channel}:VDIV {scale}")
        return

    def get_channel_scale(self, channel):
        """
        get_channel_scale(channel)

        channel: int, channel number of channel

        retrives the scale for vertical divisons for the specified channel

        returns: float
        """

        response = self.instrument.query(f"C{channel}:VDIV?")
        val = response.split()[1]
        return float(val)

    def set_channel_offset(self, channel, offset, use_divisions=False):
        """
        set_channel_offset(channel, offset)

        channel: int, channel number of channel

        offset: int/float, offset added to the channels waveform on the
                display.
        use_divisions: bool, if true offset will be treated as a number of
                       vertical divisions

        sets the vertical offset for the display of the specified channel.
        """
        if use_divisions:
            offset *= self.get_channel_scale(channel)
        self.instrument.write(f"C{channel}:OFFSET {offset}")
        return

    def get_channel_offset(self, channel):
        """
        get_channel_offset(channel)

        channel: int, channel number of channel

        retrives the vertical offset for the display of the specified
        channel.

        returns: float
        """

        response = self.instrument.query(f"C{channel}:OFFSET?")
        val = response.split()[1]
        return float(val)

    def set_channel_coupling(self, channel, coupling):
        """
        valid options are 'dc_1meg' == 'dc', 'dc_50', 'ac_1meg' == 'ac', 'gnd'
        """
        coupling_map = {'dc_1meg': 'D1M', "dc": 'D1M',
                        'dc_50': 'D50',
                        'ac_1meg': 'A1M', 'ac': 'A1M',
                        'gnd': 'gnd'}
        coupling = coupling_map[coupling.lower()]
        self.instrument.write(f"C{channel}:COUPLING {coupling}")
        return None

    def get_channel_coupling(self, channel):
        coupling_map = {'D1M': 'dc_1meg', 'D50': 'dc_50',
                        'A1M': 'ac_1meg', 'gnd': 'gnd'}
        response = self.instrument.query("C1:COUPLING?")
        coupling = response.split()[-1]
        return coupling_map[coupling]

    def set_horizontal_scale(self, scale):
        """
        set_horizontal_scale(scale)

        scale: int/float, time scale across one horizontal division on the
               display in seconds.

        sets the scale of horizontal divisons (for all channels) to the
        specified value in seconds.
        """

        self.instrument.write(f"TIME_DIV {scale}")
        return None

    def get_horizontal_scale(self):
        """
        get_horizontal_scale()

        retrieves the scale of horizontal divisons in seconds.

        returns: float
        """
        response = self.instrument.query("TIME_DIV?")
        val = response.split()[1]
        return float(val)

    def set_measure_config(self, channel, meas_type, meas_idx,
                           source_type='channel'):
        """
        AMPL, AREA, BASE, DLY, DUTY, FALL, FALL82, FREQ, MAX, MEAN, MIN, NULL,
        OVSN, OVSP, PKPK, PER, PHASE, RISE, RISE28, RMS, SDEV, TOP, WID, WIDN,
        AVG, CYCL, DDLY, DTRIG, DUR, FRST, FWHM, HAMPL, HBASE, HMEAN, HMEDI,
        HRMS, HTOP, LAST, LOW, MAXP, MEDI, MODE, NCYCLE, PKS, PNTS, RANGE,
        SIGMA, TOTP, XMAX, XMIN, XAPK, TOP
        """

        source_mapping = {'channel': 'C', 'math': 'F', 'zoom': 'Z'}
        src_code = source_mapping[source_type.lower()]

        self.instrument.write('PACU {},{},{}{}'.format(meas_idx,
                                                       meas_type,
                                                       src_code,
                                                       channel))
        return None

    def get_measure_config(self, meas_idx):
        response = self.instrument.query(f'PACU? {meas_idx}')
        info = response.split()[-1]
        resp_fields = ['index', 'type', 'source', 'status']
        return {k: v for k, v in zip(resp_fields, info.split(','))}

    def get_measure_data(self, *meas_idx):
        data = []
        for idx in meas_idx:
            q_str = f"VBS? 'return=app.Measure.P{idx}.Out.Result.Value' "
            response = self.instrument.query(q_str)
            try:
                data.append(float(response.split()[-1]))
            except ValueError:
                data.append(float('nan'))
        if len(data) == 1:
            return data[0]
        return data

    def get_measure_statistics(self, meas_idx, stat_filter=''):

        query_str = f'PAST? CUST,,P{meas_idx}'

        response = self.instrument.query(query_str)

        # strip out header info about measurement
        data = response[response.index(',') + 1:].strip().split(',')
        data = data[3:]

        keys = map(str.lower, data[::2])
        vals = data[1::2]

        rename_map = {'avg': 'mean', 'high': 'max', 'low': 'min',
                      'last': 'last', 'sigma': 'stdev', 'sweeps': 'n'}
        stats = {}
        for k, v in zip(keys, vals):
            if v != 'UNDEF':
                value = float(v.split()[0])  # remove units
            else:
                value = None

            stats[rename_map[k]] = value

        if (stat_filter != ''):
            if (stat_filter in stats.keys()):
                return stats[stat_filter.lower()]
            else:
                raise ValueError(f'Invalid option stat_filter = {stat_filter},'
                                 f' valid options are: {tuple(stats.keys())}')
        return stats

    def enable_measure_statistics(self, histogram=False):
        if histogram:
            self.instrument.write('PARM CUST,BOTH')
        else:
            self.instrument.write('PARM CUST,STAT')
        return None

    def disable_measure_statistics(self):
        self.instrument.write('PARM CUST,OFF')
        return None

    def reset_measure_statistics(self):
        """
        reset_measure_statistics()

        resets the accumlated measurements used to calculate statistics
        """
        self.instrument.write("VBS 'app.ClearSweeps' ")
        return

    def clear_all_measure(self):
        self.instrument.write('PACL')
        return None

    def trigger_run(self):
        """
        trigger_run()

        sets the state of the oscilloscopes acquision mode to acquire new
        data.
        """

        self.instrument.write("ARM")
        self.instrument.write("TRMD NORM")
        return

    def trigger_single(self):
        """
        trigger_single()

        arms the oscilloscope to capture a single trigger event.
        """

        self.instrument.write("ARM")
        self.instrument.write("TRMD SINGLE")
        return

    def trigger_stop(self):
        """
        trigger_stop()

        sets the state of the oscilloscopes acquision mode to stop
        acquiring new data. equivalent to set_trigger_acquire_state(0).
        """
        self.instrument.write('STOP')
        return

    def trigger_force(self):
        """
        trigger_force()

        forces a trigger event to occur
        """

        self.instrument.write("ARM")
        self.instrument.write("FRTR")
        return

    def trigger_auto(self):
        """
        trigger_auto()

        sets the state of the oscilloscopes acquision mode to acquire new
        data automatically.
        """

        self.instrument.write("ARM")
        self.instrument.write("TRMD AUTO")
        return

    def get_trigger_mode(self):
        response = self.instrument.query('TRMD?')
        return response.split()[-1].lower()

    def set_trigger_source(self, channel):
        """
        set_trigger_source(channel)

        channel: int, channel number of channel
                    valid options are 1-8

        sets the trigger source to the indicated channel number
        """

        response = self.instrument.query('TRSE?')  # get current trigger config

        # extract indecies that bound the current trigger source
        i_start = response.index('SR,') + 3
        i_end = response.index(',', i_start)

        # replace source with new source, send to device
        write_cmd = f'{response[:i_start]}C{channel}{response[i_end:]}'
        self.instrument.write(write_cmd)
        return

    def get_trigger_source(self):
        """
        get_trigger_source()


        returns:
        channel: int, channel number of channel
                    valid options are 1-8

        gets the channel number for the trigger source
        """

        response = self.instrument.query('TRSE?')  # get current trigger config

        # extract indecies that bound the current trigger source
        i_start = response.index('SR,') + 3
        i_end = response.index(',', i_start)

        channel = response[i_start:i_end].lstrip('C')
        return int(channel)

    def set_trigger_acquire_state(self, state):
        """
        set_trigger_acquire_state(state)

        state: (str) trigger state, valid arguements are listed in
               self.valid_trigger_states

        sets the state of the oscilloscopes trigger, whether its
        currently acquiring new data or not and which method is used for
        triggering additional acquision events.
        """

        state = state.upper()
        if state in self.valid_trigger_states:
            self.instrument.write(f"TRMD {state}")
        else:
            raise ValueError("invalid option for arg 'state'")

        return None

    def get_trigger_acquire_state(self):
        """
        get_trigger_acquire_state()

        returns:
        state: (str) acquire state, valid arguements are listed in
               self.valid_trigger_states

        returns the state of the oscilloscopes trigger, whether its
        currently acquiring new data or not and which method is used for
        triggering additional acquision events.
        """

        response = self.instrument.query('TRMD?')
        response = response.strip().split()[-1]  # strip newline and CMD name
        return response

    def set_trigger_level(self, level, source=None):
        """
        set_trigger_level(level)

        level: (float) vertical position of the trigger, units depend on
                the signal being triggered on.
        source: (int, or None) channel number to set the trigger level for. If
                None the channel currently used for triggering will be used
                (default = None)

        Sets the vertical position of the trigger point in the units of the
        triggering waveform
        """

        if source is None:
            source = self.get_trigger_source()

        self.instrument.write(f'C{source}:TRLV {float(level)}\n')
        return

    def get_trigger_level(self, source=None):
        """
        get_level()

        returns
        level: (float) vertical position of the trigger, units depend on
                the signal being triggered on.
        source: (int, or None) channel number to get the trigger level for. If
                None the channel currently used for triggering will be used
                (default = None)

        Gets the vertical position of the trigger point in the units of the
        triggering waveform
        """

        if source is None:
            source = self.get_trigger_source()

        read_cmd = f'C{source}:TRLV'
        response = self.instrument.query(f'{read_cmd}?')

        value = response.lstrip(read_cmd).split()[0]
        return float(value)

    def set_trigger_slope(self, slope, source=None):
        """
        set_trigger_slope(slope)

        slope: (str) trigger edge polarity. Valid options are 'rise'/'pos' or
               'fall'/'neg'.

        source: (int, or None) channel number to set the trigger slope for. If
                None the channel currently used for triggering will be used
                (default = None)

        sets the edge polarity of the acquistion trigger
        """

        if source is None:
            source = self.get_trigger_source()

        slope = slope.upper()
        if slope in self.valid_trigger_slopes:
            slope = self.valid_trigger_slopes[slope]
            self.instrument.write(f'C{source}:TRSL {slope}')
        else:
            raise ValueError("invalid option for arg 'slope'")
        return

    def get_trigger_slope(self, source=None):
        """
        get_trigger_slope()

        source: (int, or None) channel number to get the trigger slope for. If
                None the channel currently used for triggering will be used
                (default = None)

        returns:
        slope: (str) trigger edge polarity. Valid options are 'POS' or
               'NEG'.

        gets the edge polarity of the acquistion trigger
        """

        if source is None:
            source = self.get_trigger_source()

        response = self.instrument.query(f'C{source}:TRSL?')
        slope = response.split()[-1]

        return slope

    def set_trigger_position(self, offset, use_divisions=False):
        if use_divisions:
            offset *= self.get_horizontal_scale()
        self.instrument.write(f'TRDL {offset}')
        return

    def get_trigger_position(self):
        response = self.instrument.query('TRDL?')
        return float(response.split()[1].lower())

    def get_image(self, image_title, **kwargs):
        """
        get_image(image_title)

        Saves the screen image to the location specified by "image_title".
        "image_title" can contain path information to the desired save
        directory. Specifying an extension is not nessary, a file extension
        will be automatically be added based on the image format used (default:
        PNG)

        Args: image_title (str): path to save the image to, you do not need to
              include file extension it will be added automatically

        Kwargs:
            img_format (str): file extention to save the image with, valid
                       options are 'png', and 'tiff'
                       (default: 'png').

            img_orient (str): orientation of the image, valid options are
                       'portrait' and 'landscape' (default: 'landscape').

            bg_color (str): grid background color to use for saving the image,
                     valid options are 'black' and 'white' (default: 'black').

            screen_area (str): area of the screen to capture as an image, valid
                        options are 'dsowindow', 'gridareaonly', and
                        'fullscreen' (default: 'dsowindow').

            None of the keyword arguements are case-sensitive.

        Returns: None
        """

        # setup hardcopy
        write_cmd = "HARDCOPY_SETUP "

        # get optional arguements
        img_format = kwargs.get('img_format', 'PNG').upper()
        if img_format not in ['BMP', 'JPEG', 'PNG', 'TIFF']:
            raise ValueError('Invalid option for kwarg "img_format"')
        else:
            write_cmd += f'DEV, {img_format}, '

        if img_format == 'JPEG':
            img_format = 'jpg'  # lecroy was dumb in naming their option
            # need to correct it here for the file extension

        img_orient = kwargs.get('img_orient', 'LANDSCAPE').upper()
        if img_orient not in ['PORTRAIT', 'LANDSCAPE']:
            raise ValueError('Invalid option for kwarg "img_orient"')
        else:
            write_cmd += f'FORMAT, {img_orient}, '

        bg_color = kwargs.get('bg_color', 'BLACK').upper()
        if bg_color not in ['BLACK', 'WHITE']:
            raise ValueError('Invalid option for kwarg "bg_color"')
        else:
            write_cmd += f'BCKG, {bg_color}, '

        screen_area = kwargs.get('screen_area', 'DSOWINDOW').upper()
        if screen_area not in ['DSOWINDOW', 'GRIDAREAONLY', 'FULLSCREEN']:
            raise ValueError('Invalid option for kwarg "screen_area"')
        else:
            write_cmd += f'AREA, {screen_area}, '

        write_cmd += 'PORT, NET'
        self.instrument.write(write_cmd)

        # initiate transfer
        self.instrument.write('SCREEN_DUMP')

        # read back raw image data
        screen_data = self.instrument.read_raw()

        # save to file
        with open(f'{image_title}.{img_format.lower()}', 'wb+') as file:
            file.write(screen_data)

        return None

    def get_waveform_description(self, channel):
        response = self.instrument.query(f'C{channel}:INSP? "WAVEDESC"')
        description = {}
        for item in response.splitlines()[2:-1]:
            idx = item.index(':')
            key = item[:idx].strip().lower()
            value = item[idx+1:].strip().lower()
            try:
                value = float(value)
                if value.is_integer():
                    value = int(value)
            except ValueError:  # wasn't numeric
                pass
            description[key] = value
        return description

    def get_channel_data(self, *channels, sparsing=1, return_time=True):

        # setup transfer (sparsing, num_points, first_point, seg_num)
        # for now only sparsing is supported (defaults to no sparsing)
        self.instrument.write(f"WAVEFORM_SETUP SP,{sparsing},NP,0,FP,0,SN,0")

        waves = []
        for i, channel in enumerate(channels):
            # parameters required for reconstruction
            desc = self.get_waveform_description(channel)
            v_div = desc['vertical_gain']
            v_off = desc['vertical_offset']

            # get raw data
            self.instrument.write(f"C{channel}:WF? DAT1")
            response = self.instrument.read_raw()[22:-1]
            # response = self.instrument.read_raw()

            # process data
            adc_counts = np.frombuffer(response, np.byte, -1)
            wave = adc_counts*v_div - v_off
            waves.append(wave.astype(np.float32))

            if (i == 0) and return_time:
                t_div = desc['horiz_interval']
                t_off = desc['horiz_offset']
                t = np.arange(len(wave))*t_div*sparsing + t_off
                t = t.astype(np.float32)

        if return_time:
            return t, *waves
        if len(waves) == 1:
            return waves[0]
        return waves

    def set_channel_label(self, channel, label):
        q_str = f"""vbs 'app.acquisition.C{channel}.LabelsText = "{label}" '"""
        self.instrument.write(q_str)
        return None

    def set_channel_display(self, channel, mode):
        # mode = "true" or "false"
        q_str = f"""vbs 'app.acquisition.C{channel}.View = {mode} '"""
        self.instrument.write(q_str)
        return None

    def set_persistence_state(self, state):
        if state:
            self.instrument.write('PERSIST ON')
        else:
            self.instrument.write('PERSIST OFF')
        return None

    def get_persistence_state(self, state):

        response = self.instrument.query('PERSIST?')
        response = response.split()[1]

        if response == 'ON':
            return True
        return False

    def set_persistence_time(self, duration):
        valid_durs = [0.5, 1, 2, 5, 1, 20, 'inf']

        if isinstance(duration, str):
            duration = duration.lower()

        if duration in valid_durs:
            self.instrument.write(f'PESU {duration},ALL')
        else:
            raise ValueError('Invalid duration, valid times (s): ' +
                             ', '.join(map(str, valid_durs)))
        return None

    def get_persistence_time(self):

        response = self.instrument.query('PESU?')
        dur = response.split()[1].split(',')[0]

        if response.isnumeric():
            return float(dur)
        return 'inf'


if __name__ == '__main__':
    pass
