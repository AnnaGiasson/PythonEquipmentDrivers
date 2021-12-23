from pythonequipmentdrivers import Scpi_Instrument
import numpy as np
from typing import Union, Tuple
from pathlib import Path


class Lecroy_WR8xxx(Scpi_Instrument):
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

    def __init__(self, address: str, **kwargs) -> None:
        super().__init__(address, **kwargs)
        self.instrument.clear()
        self.set_comm_header('short')

    def select_channel(self, channel: int, state: bool) -> None:
        """
        select_channel(channel, state)

        Selects the specified channel on the front panel display.

        Args:
            channel (int): Channel number to select
            state (bool): Whether or not the respective channel is
                selected/visable on the screen.
        """

        cmd_str = f"C{int(channel)}:TRACE {'ON' if state else 'OFF'}"
        self.instrument.write(cmd_str)

    def set_channel_scale(self, channel: int, scale: float) -> None:
        """
        set_channel_scale(channel, scale)

        sets the scale of vertical divisons for the specified channel

        Args:
            channel (int): channel number to configure
            scale (float): scale of the channel amplitude across one
                vertical division on the display.
        """

        self.instrument.write(f'C{int(channel)}:VDIV {float(scale)}')

    def get_channel_scale(self, channel: int) -> float:
        """
        get_channel_scale(channel)

        Retrives the scale for vertical divisons for the specified channel

        Args:
            channel (int): channel number to query information on

        Returns:
            (float): vertical scale
        """

        response = self.instrument.query(f'C{int(channel)}:VDIV?')
        val = response.split()[1]
        return float(val)

    def set_channel_offset(self, channel: int, off: float, **kwargs) -> None:
        """
        set_channel_offset(channel, off, **kwargs)

        Sets the vertical offset for the display of the specified channel.

        Args:
            channel (int): Channel number to query
            off (float): vertical/amplitude offset
        Kwargs
            use_divisions (bool, optional): Whether or not the offset is
                treated as a number of vertical divisions instead of an
                amplltude. Defaults to False.
        """

        if kwargs.get('use_divisions', False):
            off = float(off)*self.get_channel_scale(int(channel))
        self.instrument.write(f"C{int(channel)}:OFFSET {float(off)}")

    def get_channel_offset(self, channel: int) -> float:
        """
        get_channel_offset(channel)

        Retrives the vertical offset for the display of the specified channel.

        Args:
            channel (int): Channel number to query

        Returns:
            float: vertical/amplitude offset
        """

        response = self.instrument.query(f"C{int(channel)}:OFFSET?")
        val = response.split()[1]
        return float(val)

    def set_channel_coupling(self, channel: int, coupling: str) -> None:
        """
        set_channel_coupling(channel, coupling)

        Sets the coupling used on a the specified channel. For this
        oscilloscope the following coupling options are supported:
        "dc" == "dc_1meg", "dc_50", "ac" == "ac_1meg", and "gnd".

        Args:
            channel (int): channel number to adjust
            coupling (str): coupling mode
        """

        coupling_map = {'dc_1meg': 'D1M', "dc": 'D1M',
                        'dc_50': 'D50',
                        'ac_1meg': 'A1M', 'ac': 'A1M',
                        'gnd': 'gnd'}

        coupling = str(coupling).lower()
        if coupling not in coupling_map.keys():
            raise ValueError(f"Invalid Coupling option: {coupling}. "
                             f"Suuport options are: {coupling_map.keys()}")

        cmd_str = f"C{int(channel)}:COUPLING {coupling_map[coupling]}"
        self.instrument.write(cmd_str)

    def get_channel_coupling(self, channel: int) -> str:
        """
        get_channel_coupling(channel)

        Retirives the coupling used on a the specified channel. For this
        oscilloscope the following coupling options are supported:
        "dc", "dc_50", "ac", and "gnd".

        Args:
            channel (int): channel number to query

        Returns:
            str: coupling mode
        """

        coupling_map = {'D1M': 'dc', 'D50': 'dc_50',
                        'A1M': 'ac', 'gnd': 'gnd'}

        response = self.instrument.query(f"C{int(channel)}:COUPLING?")
        return coupling_map[response.split()[-1]]

    def set_horizontal_scale(self, scale: float) -> None:
        """
        set_horizontal_scale(scale)

        sets the scale of horizontal divisons (for all channels) to the
        specified value in seconds.

        Args:
            scale (float): time scale across one horizontal division on the
                display in seconds.
        """

        self.instrument.write(f'TIME_DIV {float(scale)}')

    def get_horizontal_scale(self) -> float:
        """
        get_horizontal_scale()

        Retrieves the horizontal scale used to accquire waveform data.

        Returns:
            float: horizontal scale in seconds per division.
        """

        response = self.instrument.query('TIME_DIV?')
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

    def get_measure_data(self, *meas_idx: int) -> Union[float, tuple]:
        """
        get_measure_data(*meas_idx)

        Returns the current value of the requesed measurement(s) reference by
        the provided index(s).

        Args:
            meas_idx (int): measurement index(s) for the measurement(s) to
                query. Can be a signal index or an arbitrary sequence of
                indices.

        Returns:
            float: Current value of the requested measurement. If no value as
                been assigned to the measurement yet the returned value is nan.
        """

        data = []
        for idx in meas_idx:

            q_str = f"VBS? 'return=app.Measure.P{int(idx)}.Out.Result.Value' "
            response = self.instrument.query(q_str)

            try:
                data.append(float(response.split()[-1]))
            except ValueError:
                data.append(float('nan'))

        if len(data) == 1:
            return data[0]
        return tuple(data)

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
        return None

    def clear_all_measure(self):
        self.instrument.write('PACL')
        return None

    def trigger_run(self) -> None:
        """
        trigger_run()

        sets the state of the oscilloscopes acquision mode to acquire new
        data.
        """

        self.instrument.write("ARM")
        self.instrument.write("TRMD NORM")

    def trigger_single(self) -> None:
        """
        trigger_single()

        arms the oscilloscope to capture a single trigger event.
        """

        self.instrument.write("ARM")
        self.instrument.write("TRMD SINGLE")

    def trigger_stop(self) -> None:
        """
        trigger_stop()

        sets the state of the oscilloscopes acquision mode to stop
        acquiring new data. equivalent to set_trigger_acquire_state(0).
        """
        self.instrument.write('STOP')

    def trigger_force(self) -> None:
        """
        trigger_force()

        forces a trigger event to occur
        """

        self.instrument.write("ARM")
        self.instrument.write("FRTR")

    def trigger_auto(self) -> None:
        """
        trigger_auto()

        Sets the state of the oscilloscopes acquision mode to acquire new
        data automatically.
        """

        self.instrument.write("ARM")
        self.instrument.write("TRMD AUTO")

    def get_trigger_mode(self) -> str:
        """
        get_trigger_mode()

        Gets the mode of the trigger used for data acquisition.

        Returns:
            str: trigger mode.
        """

        response = self.instrument.query('TRMD?')
        return response.split()[-1].lower()

    def set_trigger_source(self, channel: int) -> None:
        """
        set_trigger_source(channel)

        Sets the trigger source to the indicated source channel

        Args:
            channel (int): channel number to configure
        """

        response = self.instrument.query('TRSE?')  # get current trigger config

        # extract indecies that bound the current trigger source
        i_start = response.index('SR,') + 3
        i_end = response.index(',', i_start)

        # replace source with new source, send to device
        write_cmd = f'{response[:i_start]}C{int(channel)}{response[i_end:]}'
        self.instrument.write(write_cmd)

    def get_trigger_source(self) -> int:
        """
        get_trigger_source()

        Gets the channel number for the trigger source

        Returns:
            int: channel number used for the trigger source
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

    def set_trigger_level(self, level: float, **kwargs) -> None:
        """
        set_trigger_level(level, **kwargs)

        Sets the vertical position of the trigger point in the units of the
        triggering waveform

        Args:
            level (float): vertical position of the trigger, units depend on
                the signal being triggered on.
        Kwargs:
            source (int): channel number to set the trigger level for. If not
                provided the default behavior is to use whichever channel is
                currently being used for triggering.
        """

        source = kwargs.get('source', self.get_trigger_source())
        self.instrument.write(f'C{int(source)}:TRLV {float(level)}\n')

    def get_trigger_level(self, **kwargs) -> float:
        """
        get_level(**kwargs)

        Returns the vertical position of the trigger level in the units of the
        triggering waveform

        Kwargs:
            source (int): channel number to set the trigger level for. If not
                provided the default behavior is to use whichever channel is
                currently being used for triggering.

        Returns:
            float: vertical position of the trigger, units depend on
                the signal being triggered on
        """

        source = kwargs.get('source', self.get_trigger_source())

        read_cmd = f'C{int(source)}:TRLV'
        response = self.instrument.query(f'{read_cmd}?')

        return float(response.lstrip(read_cmd).split()[0])

    def set_trigger_slope(self, slope: str, **kwargs) -> None:
        """
        set_trigger_slope(slope, **kwargs)

        Sets the edge polarity of the acquistion trigger. Valid options for
        this oscilloscope are 'rise'/'pos' or 'fall'/'neg'.

        Args:
            slope (str): trigger edge polarity.
        Kwargs:
            source (int): channel number to set the trigger level for. If not
                provided the default behavior is to use whichever channel is
                currently being used for triggering.
        """

        valid_options = {'POS': 'POS', 'RISE': 'POS',
                         'NEG': 'NEG', 'FALL': 'NEG'}

        source = kwargs.get('source', self.get_trigger_source())

        slope = str(slope).upper()
        if slope not in valid_options.keys():
            raise ValueError('Invalid option for Arg "slope".'
                             f' Valid option are {valid_options.keys()}')

        self.instrument.write(f'C{int(source)}:TRSL {valid_options[slope]}')

    def get_trigger_slope(self, **kwargs) -> str:
        """
        get_trigger_slope(**kwargs)

        Retrives the edge polarity of the acquistion trigger. Valid options for
        this oscilloscope are 'rise'/'pos' or 'fall'/'neg'.

        Kwargs:
            source (int): channel number to set the trigger level for. If not
                provided the default behavior is to use whichever channel is
                currently being used for triggering.

        Returns:
            str: trigger edge polarity
        """

        source = kwargs.get('source', self.get_trigger_source())

        response = self.instrument.query(f'C{source}:TRSL?')
        return response.split()[-1].lower()

    def set_trigger_position(self, offset: float, **kwargs) -> None:
        """
        set_trigger_position(offset)

        Sets the horizontal position of the trigger point which represents the
        t=0 point of the data capture.

        Args:
            offset (float): Horizontal position of the trigger. Represents a
                time offset in seconds. If use_divisions=True then it can be
                interpreted a number of horizontal divisions in the capture
                window.
        Kwargs:
            use_divisions (bool, optional): Whether to interpret offset as a
                time (False) or a number of horizontal division (True).
                Defaults to False.
        """

        if kwargs.get('use_divisions', False):
            scale = self.get_horizontal_scale()
        else:
            scale = 1

        self.instrument.write(f'TRDL {float(offset)*scale}')

    def get_trigger_position(self) -> float:
        """
        get_trigger_position()

        Retrives the horizontal position of the trigger point which
        representing the t=0 point of the data capture.

        Returns:
            float: Horizontal position of the trigger. Represents a time offset
                in seconds
        """

        response = self.instrument.query('TRDL?')
        return float(response.split()[1].lower())

    def get_image(self, image_title: Union[str, Path], **kwargs) -> None:
        """
        get_image(image_title, **kwargs)

        Saves the screen image to the location specified by "image_title".
        "image_title" can contain path information to the desired save
        directory. Specifying an extension is not nessary, a file extension
        will be automatically be added based on the image format used (default:
        PNG)

        Args:
            image_title (Union[str, Path]): Path name of image, file extension
                will be added automatically
        Kwargs:
            image_format (str, optional): File extention to save the image
                with, valid options are png, and 'tiff'. Defaults to png.
            image_orientation (str, optional): Orientation of the resulting
                image, valid options are 'portrait' and 'landscape'. Defaults
                to landscape'.
            bg_color (str, optional): Grid background color to use for saving
                the image, valid options are 'black' and 'white'. Defaults to
                black.
            screen_area (str, optional): Area of the screen to capture as an
                image, valid options are 'dsowindow', 'gridareaonly', and
                'fullscreen'. Defaults to dsowindow.
        """
        # valid image settings
        valid_formats = ('BMP', 'JPEG', 'PNG', 'TIFF')
        valid_orientations = ('PORTRAIT', 'LANDSCAPE')
        valid_bg_colors = ('BLACK', 'WHITE')
        valid_screen_areas = ('DSOWINDOW', 'GRIDAREAONLY', 'FULLSCREEN')

        # handle kwargs
        xfer_ext = str(kwargs.get('image_format', 'PNG')).upper()
        image_orient = kwargs.get('image_orientation', 'LANDSCAPE').upper()
        bg_color = kwargs.get('bg_color', 'BLACK').upper()
        screen_area = kwargs.get('screen_area', 'DSOWINDOW').upper()
        port = 'NET'  # no support for others atm

        if xfer_ext not in valid_formats:
            raise ValueError('Invalid option for kwarg "image_format"')
        elif image_orient not in valid_orientations:
            raise ValueError('Invalid option for kwarg "image_orientation"')
        elif bg_color not in valid_bg_colors:
            raise ValueError('Invalid option for kwarg "bg_color"')
        elif screen_area not in valid_screen_areas:
            raise ValueError('Invalid option for kwarg "screen_area"')

        # add file extension to final filepath
        write_ext = xfer_ext.lower() if xfer_ext != 'JPEG' else 'jpg'
        if isinstance(image_title, Path):
            f_name = f'{image_title.name}.{write_ext}'
            file_path = image_title.parent.joinpath(f_name)
        elif isinstance(image_title, str):
            file_path = f"{image_title}.{write_ext}"
        else:
            raise ValueError('image_title must be a str or path-like object')

        # initiate transfer
        template = (r'HARDCOPY_SETUP DEV, {}, FORMAT, {}, '
                    r'BCKG, {}, AREA, {}, PORT, {}')
        write_cmd = template.format(xfer_ext, image_orient, bg_color,
                                    screen_area, port)
        self.instrument.write(write_cmd)
        self.instrument.write('SCREEN_DUMP')

        # read back raw image data
        screen_data = self.instrument.read_raw()

        # save to file
        with open(file_path, 'wb+') as file:
            file.write(screen_data)

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

    def get_channel_data(self, *channels: int,
                         **kwargs) -> Union[Tuple[np.ndarray], np.ndarray]:
        """
        get_channel_data(*channels, return_time=True, dtype=np.float32)

        Retrieves waveform data from the oscilloscope on the specified
        channel(s). A sparse representation of each waveform and be returned by
        setting the sparsing factor, "sparsing", to a values > 1.

        Args:
            *channels: (int, Iterable[int]) or sequence of ints, channel
                number(s) of the waveform(s) to be transferred.

        Kwargs:
            sparsing (int, optional): sparsing factor, every n-th point of the
                waveform will be returned.
            return_time (bool, optional): Whether or not to return the time
                array with the rest of the waveform data. Defaults to True.
            dtype (type, optional): data type to be used for waveform data.
                Defaults to float32.

        Returns:
            Union[tuple, numpy.array]: waveform data. if len(channels) > 1 or
                or if return_time is true this is a tuple of numpy arrays. If
                time information is returned it will always be the first value,
                any additional waveforms will be returned in the same order
                they were passed. In the case of len(channels) == 1 and
                return_time is False a single numpy array is returned
        """

        # formatting info
        sparsing = int(kwargs.get('sparsing', 1))
        dtype = kwargs.get('dtype', np.float32)

        # set up scope for data transfer
        #   format: (sparsing, num_points, first_point, seg_num)
        self.instrument.write(f'WAVEFORM_SETUP SP,{sparsing},NP,0,FP,0,SN,0')
        #   for now only sparsing is supported (defaults to no sparsing)

        waves = []
        for channel in channels:
            # get waveform metadata
            desc = self.get_waveform_description(channel)
            y_offset = desc['vertical_offset']
            y_scale = desc['vertical_gain']

            # get raw data, strip header
            self.instrument.write(f'C{channel}:WF? DAT1')
            raw_data = self.instrument.read_raw()[22:-1]

            data = np.frombuffer(raw_data, np.byte, count=len(raw_data))

            # decode into measured value using waveform metadata
            wave = data*y_scale - y_offset
            waves.append(wave.astype(dtype))

        if kwargs.get('return_time', True):
            t_div, t_off = desc['horiz_interval'], desc['horiz_offset']
            # all waveforms assumed to have same duration (just use last)
            t = np.arange(len(wave), dtype=dtype)*t_div*sparsing + t_off

            return (t, *waves)
        else:
            if len(waves) == 1:
                return waves[0]
            return tuple(waves)

    def set_channel_label(self, channel: int, label: str) -> None:
        """
        set_channel_label(channel, label)

        updates the text label on a channel specified by "channel" with the
        value given in "label".

        Args:
            channel (int): channel number to update label of.
            label (str): text label to assign to the specified
        """

        q_str = f"""vbs 'app.acquisition.C{channel}.LabelsText = "{label}" '"""
        self.instrument.write(q_str)

    def get_channel_label(self, channel: int) -> str:
        """
        get_channel_label(channel)

        Queries the text label of the channel specified by "channel".

        Args:
            channel (int): channel number to query label of.
        Returns:
            (str): text label to assigned to the specified channel
        """

        q_str = f"""vbs? 'return = app.acquisition.C{channel}.LabelsText'"""

        response = self.instrument.query(q_str)

        return ' '.join(response.strip().split()[1:])

    def set_channel_label_position(self, channel: int, position=0) -> None:
        """
        set_channel_label_position(channel, position)

        updates the text label position on a channel specified by "channel"
        with the position given in "position".

        Args:
            channel (int): channel number to update label of.
            position (int): position trigger relative to place label
        """

        q_str = (f"""vbs 'app.acquisition.C{channel}.LabelsPosition = """ +
                 f""""{position}" '""")
        self.instrument.write(q_str)

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

    def get_persistence_state(self):

        response = self.instrument.query('PERSIST?')
        response = response.split()[1]

        if response == 'ON':
            return True
        return False

    def set_persistence_time(self, duration: Union[float, str]) -> None:
        """
        set_persistence_time(duration)

        sets the persistence of the waveform buffers to include all captures
        within a time window specified by "duration"

        Args:
            duration (Union[float, str]): The exposure time for the
                oscilloscope capture display in seconds. Valid values are
                positive numbers or "inf" to set the maximum exposure time
        """
        valid_durs = (0.5, 1, 2, 5, 1, 20, 'inf')

        if isinstance(duration, str):
            duration = duration.lower()

        if duration in valid_durs:
            self.instrument.write(f'PESU {duration},ALL')
        else:
            raise ValueError('Invalid duration, valid times (s): ' +
                             ', '.join(map(str, valid_durs)))

    def get_persistence_time(self) -> Union[float, str]:
        """
        get_persistence_time()

        Retrives the persistence time set for the waveform buffers.

        Returns:
            (Union[float, str]): persistence time
        """

        response = self.instrument.query('PESU?')
        dur = response.split()[1].split(',')[0]

        if response.isnumeric():
            return float(dur)
        return 'inf'

    def set_comm_header(self, header: str) -> None:
        """
        set_comm_header(header)

        Sets the header type used in the response of query commands. Valid
        options are 'long', 'short', and 'off'. An example of each is noted
        below.

            Query : C1:OFFSET?  # returns the vertical offset used by channel 1

            response with 'long': 'C1:OFFSET -50 V\n'
            response with 'short': 'C1:OFST -50 V\n'
            response with 'off': '-50\n'


        This class was written assuming that the short or long formats
        are in use. Therefore by default it is set to short. Changes to this
        format may result in issues with other commands.


        Args:
            header (str): query header format name. valid values are 'long',
                'short', and 'off'
        """

        header = str(header).upper()

        if header not in ('OFF', 'SHORT', 'LONG'):
            raise ValueError('Invalid option for arg "header"')

        self.instrument.write(f'CHDR {header}')

    def get_comm_header(self) -> str:
        """
        get_comm_header()

        Rreturns the header type used in the response of query commands.
        Response is either 'long', 'short', and 'off'. An example of each is
        noted below.

            Query : C1:OFFSET?  # returns the vertical offset used by channel 1

            response with 'long': 'C1:OFFSET -50 V\n'
            response with 'short': 'C1:OFST -50 V\n'
            response with 'off': '-50\n'

        Returns:
            header (str): query header format name. valid values are 'long',
                'short', and 'off'
        """

        response = self.instrument.query('CHDR?')
        if ' ' in response:
            header = response.split()[-1]
        else:
            header = response

        header = header.strip().lower()

        return header


if __name__ == '__main__':
    pass
