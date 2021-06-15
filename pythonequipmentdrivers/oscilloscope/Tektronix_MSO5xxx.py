from pythonequipmentdrivers import Scpi_Instrument
import struct
import numpy as np
from pathlib import Path
from typing import Union, Tuple


class Tektronix_MSO5xxx(Scpi_Instrument):
    """
    Tektronix_MSO5xxx(address)

    address : str, address of the connected oscilloscope

    object for accessing basic functionallity of the Tektronix_MSO5xxx
    Family of Oscilloscopes
    """

    def __init__(self, address: str, **kwargs) -> None:
        super().__init__(address, **kwargs)

        # get image formatting
        self.instrument.write('EXP:FORM PNG')  # image is a .png file
        self.instrument.write('HARDC:PORT FILE')  # image is stored as a file
        self.instrument.write('HARDC:PALE COLOR')  # color image (alt INKS)
        self.instrument.write('HARDC:LAY LAN')  # landscape image
        self.instrument.write('HARDC:VIEW FULLNO')  # no menu, full-screen wvfm

    def select_channel(self, channel: int, state: bool) -> None:
        """
        select_channel(channel)

        channel: int, channel number of channel
                    valid options are 1,2,3, and 4

        state: bool, whether or not the respective channel is
                selected/visable on the screen.

        selects the specified channel. This is allow the specified channel
        to be seen on top of the others in the display. With a given
        channel selected any cursor measurements will then correspond to
        the selected channel.
        """

        cmd_str = f"SEL:CH{int(channel)} {'ON' if state else 'OFF'}"
        self.instrument.write(cmd_str)

    def get_channel_data(self, *channels: int, **kwargs) -> Tuple:
        """
        get_channel_data(*channels, start_percent=0, stop_percent=100,
                         return_time=True, dtype=np.float32)

        Retrieves waveform data from the oscilloscope on the specified
        channel(s). Optionally points to start / stop the transfer can be
        given. start_percent and stop_percent can be set independently, the
        waveform returned will always start from the smaller of the two and
        go to the largest.

        Args:
            *channels: (int, Iterable[int]) or sequence of ints, channel
                number(s) of the waveform(s) to be transferred.

        Kwargs:
            start_percent (int, optional): point in time to begin the waveform
                transfer number represents percent of the record length. Valid
                settings are 0-100. Defaults to 0.
            stop_percent (int, optional): point in time to begin the waveform
                transfer number represents percent of the record length. Valid
                settings are 0-100. Defaults to 100.
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

        # get record window metadata
        N = self.get_record_length()
        x_offset = int(self.get_trigger_position()/100*N)

        # formatting info
        dtype = kwargs.get('dtype', np.float32)
        start_idx = np.clip(kwargs.get('start_percent', 0), 0, 100)/100*N
        stop_idx = np.clip(kwargs.get('stop_percent', 100), 0, 100)/100*N

        waves = []
        for channel in channels:

            # configure data transfer
            self.instrument.write(f'DATA:START {start_idx}')  # data range
            self.instrument.write(f'DATA:STOP {stop_idx}')
            self.instrument.write(f'DATA:SOU CH{channel}')  # data source
            self.instrument.write('DATA:ENC SRP')  # encoding, int little-end

            # get waveform metadata
            dt = float(self.instrument.query('WFMPRE:XINCR?'))  # sampling time
            y_offset = float(self.instrument.query('WFMPRE:YOFF?'))
            y_scale = float(self.instrument.query('WFMPRE:YMULT?'))

            adc_offset = float(self.instrument.query('WFMPRE:YZERO?'))

            # get raw data, strip header
            self.instrument.write('CURVE?')
            raw_data = self.instrument.read_raw()

            header_len = 2 + int(raw_data[1])
            raw_data = raw_data[header_len:-1]

            data = np.array(struct.unpack(f'{len(raw_data)}B', raw_data),
                            dtype=dtype)

            # decode into measured value using waveform metadata
            wave = (data - y_offset)*y_scale + adc_offset
            waves.append(wave)

        if kwargs.get('return_time', True):
            # generate time vector / account for trigger position
            # all waveforms assumed to have same duration (just use last)
            t = np.arange(0, dt*len(wave), dt, dtype=dtype)
            t -= (x_offset - min([start_idx, stop_idx]))*dt

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

        self.instrument.write(f'CH{int(channel)}:LAB:NAM "{label}"')

    def get_channel_label(self, channel: int) -> str:
        """
        get_channel_label(channel)

        retrives the label currently used by the specified channel

        Args:
            channel (int): channel number to get label of.

        Returns:
            (str): specified channel label
        """

        response = self.instrument.query(f'CH{channel}:LAB:NAM?')
        return response.strip().replace('"', '')

    def set_channel_label_position(self, channel: int, pos: tuple) -> None:
        """
        set_channel_label_position(channel, pos)

        Configures the placement of label text relative to the 0 amplitude
        point on the display for a given channel.

        Args:
            channel (int): channel number to adjust
            pos (Tuple[float, float]): the relative x, y positon of
                the channel label with respect to the waveform as number of
                divisions.
        """

        if (not isinstance(pos, (tuple, list))) or (len(pos) != 2):
            raise ValueError('Arg "pos" must be an iterable of length 2')

        x_coord, y_coord = pos

        self.instrument.write(f'CH{int(channel)}:LAB:XPOS {float(x_coord)}')
        self.instrument.write(f'CH{int(channel)}:LAB:YPOS {float(y_coord)}')

    def get_channel_label_position(self, channel: int) -> Tuple[float, float]:
        """
        get_channel_label_position(channel)

        Retrivies the configuration of the placement of label text relative to
        the 0 amplitude point on the display for a given channel.

        Args:
            channel (int): hannel number to query

        Returns:
            Tuple[float, float]: the relative x, y positon of the channel label
                with respect to the waveform as a number of divisions.
        """

        x_coord = float(self.instrument.query(f'CH{int(channel)}:LAB:XPOS?'))
        y_coord = float(self.instrument.query(f'CH{int(channel)}:LAB:YPOS?'))

        return (x_coord, y_coord)

    def set_channel_bandwidth(self, channel: int, bandwidth: float) -> None:
        """
        set_channel_bandwidth(channel, bandwidth)

        Sets the bandwidth limiting of "channel" to the value specified by
        "bandwidth". Note: different probes have different possible bandwidth
        settings, if the value specified in this function isn't availible on
        the probe connected to the specified input it will likely round UP to
        the nearest availible setting

        Args:
            channel (int): channel number to configure
            bandwidth (float): desired bandwidth setting for "channel" in Hz
        """

        if isinstance(bandwidth, str) and (bandwidth.upper() == 'FULL'):
            self.instrument.write(f"CH{int(channel)}:BAN FULL")
        else:
            self.instrument.write(f"CH{int(channel)}:BAN {float(bandwidth)}")

    def get_channel_bandwidth(self, channel: int) -> float:
        """
        get_channel_bandwidth(channel)

        Retrives the bandwidth setting used by the specified channel in Hz.

        Args:
            channel (int): channel number to query information on

        Returns:
            float: channel bandwidth setting
        """

        response = self.instrument.query(f"CH{int(channel)}:BAN?")
        return float(response)

    def set_channel_scale(self, channel: int, scale: float) -> None:
        """
        set_channel_scale(channel, scale)

        sets the scale of vertical divisons for the specified channel

        Args:
            channel (int): channel number to query information on
            scale (float): scale of the channel amplitude across one
                vertical division on the display.
        """

        self.instrument.write(f'CH{int(channel)}:SCA {float(scale)}')

    def get_channel_scale(self, channel):
        """
        get_channel_scale(channel)

        Retrives the scale for vertical divisons for the specified channel

        Args:
            channel (int): channel number to query information on

        Returns:
            (float): vertical scale
        """

        response = self.instrument.query(f'CH{int(channel)}:SCA?')
        return float(response)

    def set_channel_offset(self, channel: int, off: float) -> None:
        """
        set_channel_offset(channel, off)

        Sets the vertical offset for the display of the specified channel.

        Args:
            channel (int): Channel number to query
            off (float): vertical/amplitude offset
        """

        self.instrument.write(f"CH{int(channel)}:OFFS {float(off)}")

    def get_channel_offset(self, channel: int) -> float:
        """
        get_channel_offset(channel)

        Retrives the vertical offset for the display of the specified channel.

        Args:
            channel (int): Channel number to query

        Returns:
            float: vertical/amplitude offset
        """

        response = self.instrument.query(f"CH{int(channel)}:OFFS?")
        return float(response)

    def set_channel_position(self, channel: int, position: float) -> None:
        """
        set_channel_position(channel, position)

        Sets the vertical postion of the 0 amplitude line in the display of the
        specified channel's waveform. The veritcal position is represented a
        number of vertical division on the display (from the center). Can be
        positive negative or fractional.

        Args:
            channel (int): Channel number to query
            position (float): vertical postion of the 0 amplitude position in
                the display of the specified channel waveform.
        """

        self.instrument.write(f"CH{int(channel)}:POS {float(position)}")

    def get_channel_position(self, channel: int) -> float:
        """
        get_channel_position(channel)

        Retrieves the vertical postion of the 0 amplitude line used in the
        display of the specified channel's waveform. The veritcal position is
        represented a number of vertical division on the display (from the
        center). Can be positive negative or fractional.

        Args:
            channel (int): Channel number to query

        Returns:
            float: vertical postion of the 0 amplitude position in the display
                of the specified channel waveform.
        """

        response = self.instrument.query(f"CH{int(channel)}:POS?")
        return float(response)

    def set_channel_coupling(self, channel: int, coupling: str) -> None:
        """
        set_channel_coupling(channel, coupling)

        Sets the coupling used on a the specified channel. For this
        oscilloscope the following coupling options are supported: "DC", "AC",
        "GND", and "DC REJ"

        Args:
            channel (int): channel number to adjust
            coupling (str): coupling mode
        """

        valid_modes = ("DC", "AC", "GND", "DCREJ")

        coupling = str(coupling).upper()
        if coupling not in valid_modes:
            raise ValueError(f"Invalid Coupling option: {coupling}. "
                             f"Suuport options are: {valid_modes}")

        self.instrument.write(f"CH{int(channel)}:COUP {coupling}")

    def get_channel_coupling(self, channel: int) -> str:
        """
        get_channel_coupling(channel)

        Retirives the coupling used on a the specified channel. For this
        oscilloscope the following coupling options are supported: "DC", "AC",
        "GND", and "DC REJ"

        Args:
            channel (int): channel number to query

        Returns:
            str: coupling mode
        """

        resp = self.instrument.query(f"CH{int(channel)}:COUP?")
        return resp.strip()

    def set_trigger_acquire_state(self, state: bool) -> None:
        """
        set_trigger_acquire_state(state)

        sets the state of the oscilloscopes acquision mode, whether its
        currently acquiring new data.

        Args:
            state (bool): acquisition state, valid arguements are False (stop)
                and True (run/acquire)
        """

        self.instrument.write(f"ACQ:STATE {1 if state else 0}")

    def get_trigger_acquire_state(self) -> bool:
        """
        get_trigger_acquire_state()

        Gets the state of the oscilloscopes acquision mode/whether its
        currently acquiring new data.

        Returns:
            bool: Acquisition state, valid arguements are False (stop) and
                True (run/acquire)
        """

        response = self.instrument.query("ACQ:STATE?")
        return bool(response)

    def trigger_run(self) -> None:
        """
        trigger_run()

        sets the state of the oscilloscopes acquision mode to acquire new
        data. equivalent to set_trigger_acquire_state(True).
        """

        self.set_trigger_acquire_state(True)

    def trigger_stop(self) -> None:
        """
        trigger_stop()

        sets the state of the oscilloscopes acquision mode to stop
        acquiring new data. equivalent to set_trigger_acquire_state(0).
        """
        self.set_trigger_acquire_state(0)

    def trigger_force(self) -> None:
        """
        trigger_force()

        forces a trigger event to occur
        """

        self.instrument.write("TRIG FORC")

    def trigger_single(self) -> None:
        """
        trigger_single()

        arms the oscilloscope to capture a single trigger event.
        """

        self.set_trigger_acquire_state(1)
        self.instrument.write("ACQ:STOPA SEQ")

    def set_trigger_source(self, channel: int) -> None:
        """
        set_trigger_source(channel)

        Sets the trigger source to the indicated source channel

        Args:
            channel (int): channel number to configure
        """

        self.instrument.write(f'TRIGger:A:EDGE:SOUrce CH{int(channel)}')

    def get_trigger_source(self) -> int:
        """
        get_trigger_source()

        Gets the channel number for the trigger source

        Returns:
            int: channel number used for the trigger source
        """

        response = self.instrument.query('TRIGger:A:EDGE:SOUrce?')
        return int(response.replace('CH', ''))

    def set_trigger_position(self, offset: float) -> None:
        """
        set_trigger_position(offset)

        Sets the horizontal position of the trigger point which represents the
        t=0 point of the data capture.

        Args:
            offset (float): Horizontal position of the trigger as a percentage
                of the horizontal capture window. Should be between 0-100.
        """

        if not (0 <= float(offset) <= 100):
            raise ValueError('offset out of the valid range [0-100]')

        self.instrument.write(f"HOR:POS {float(offset)}")

    def get_trigger_position(self) -> float:
        """
        get_trigger_position()

        Retrieves the horizontal position of the trigger point which represents
        the t=0 point of the data capture.

        Returns:
            float: Horizontal position of the trigger as a percentage of the
                horizontal capture window.
        """

        return float(self.instrument.query("HOR:POS?"))

    def set_trigger_slope(self, slope: str) -> None:
        """
        set_trigger_slope(slope)

        Sets the edge polarity of the acquistion trigger. Valid options for
        this oscilloscope are 'rise', 'fall', or 'either'.

        Args:
            slope (str): trigger edge polarity.
        """

        valid_options = ('RISE', 'FALL', 'EITHER')

        slope = str(slope).upper()
        if slope not in valid_options:
            raise ValueError('Invalid option for Arg "slope".'
                             f' Valid option are {valid_options}')

        self.instrument.write(f'TRIGger:A:EDGE:SLOpe {slope}')

    def get_trigger_slope(self) -> str:
        """
        get_trigger_slope()

        Retrives the edge polarity of the acquistion trigger. Valid options for
        this oscilloscope are 'rise', 'fall', or 'either'.

        Returns:
            str: trigger edge polarity.
        """

        response = self.instrument.query('TRIGger:A:EDGE:SLOpe?')
        return response.rstrip('\n').lower()

    def set_trigger_mode(self, mode: str) -> None:
        """
        set_trigger_mode(mode)

        Sets the mode of the trigger used for data acquisition. In the "AUTO"
        mode the scope will periodically trigger automatically to update the
        waveform buffers. In the "NORM" mode the trigger needs to be actively
        asserted by some control signal for this to occur.

        Args:
            mode (str): trigger mode. Valid modes are "AUTO" and "NORM"
        """

        mode = str(mode).upper()
        if mode not in ["AUTO", "NORM", "NORMAL"]:
            raise ValueError(f"Invalid mode: {mode}")
        self.instrument.write(f"TRIG:A:MOD {mode}")

    def get_trigger_mode(self) -> str:
        """
        get_trigger_mode()

        Gets the mode of the trigger used for data acquisition. In the "AUTO"
        mode the scope will periodically trigger automatically to update the
        waveform buffers. In the "NORM" mode the trigger needs to be actively
        asserted by some control signal for this to occur.

        Returns:
            str: trigger mode. Valid modes are "AUTO" and "NORM"
        """

        response = self.instrument.query("TRIG:A:MOD?")
        return response.rstrip("\n").lower()

    def set_trigger_level(self, level: float) -> None:
        """
        set_trigger_level(level)

        Sets the vertical position of the trigger level in the units of the
        triggering waveform

        Args:
            level (float): vertical position of the trigger, units depend on
                the signal being triggered on.
        """

        self.instrument.write(f"TRIG:A:LEV {float(level)}")

    def get_trigger_level(self) -> float:
        """
        get_trigger_level()

        Returns the vertical position of the trigger level in the units of the
        triggering waveform

        Returns:
            float: vertical position of the trigger, units depend on the signal
                being triggered on.
        """

        response = self.instrument.query("TRIG:A:LEV?")
        return float(response)

    def set_measure_method(self, method):
        """
        set_measure_method(method)

        method: (str) measurement method, valid options are 'HISTOGRAM',
                'MEAN', and 'MINMAX'. Arguement is not case-sensitive.

        Sets the method used to calculate the 0% and 100% reference levels.
        """

        method = method.upper()
        if method in ['HISTOGRAM', 'MEAN', 'MINMAX']:
            self.instrument.write(f'MEASU:METH {method}')
        else:
            raise ValueError("Invalid Method")
        return None

    def get_measure_method(self):
        """
        get_measure_method()

        returns:
        method: (str) measurement method, valid options are 'HISTOGRAM',
                'MEAN', and 'MINMAX'. Arguement is not case-sensitive.

        Gets the method used to calculate the 0% and 100% reference levels.
        """

        resp = self.instrument.query('MEASU:METH?')
        return resp.strip('\n')

    def set_measure_reference_method(self, method):
        """
        set_measure_reference_method(method)

        method: (str) reference method, valid options are 'ABSOLUTE',
                and 'PERCENT'. Arguement is not case-sensitive.

        Sets the reference level units used for measurement calculations.
        """

        method = method.upper()
        if method in ['ABSOLUTE', 'PERCENT']:
            self.instrument.write(f'MEASU:REFL:METH {method}')
        else:
            raise ValueError("Invalid Method")
        return None

    def get_measure_reference_method(self):
        """
        get_measure_reference_method()

        returns:
        method: (str) reference method, valid options are 'ABSOLUTE',
                and 'PERCENT'. Arguement is not case-sensitive.

        Gets the reference level units used for measurement calculations.
        """

        resp = self.instrument.query('MEASU:REFL:METH?')
        return resp.strip('\n')

    def set_measure_ref_level(self, method, level, threshold):
        """
        set_measure_ref_level(method, level, threshold)

        method: (str) reference method, valid options are 'ABSOLUTE',
                and 'PERCENT'. Arguement is not case-sensitive.
        level: (str) reference level to adjust, valid options are 'HIGH',
                'MID', and 'LOW'. Arguement is not case-sensitive.
        threshold: (float) threshold to set the desired measurement
                    reference at; either in V or % depending on method.

        Sets the percent/voltage that is used to calculate the low/mid/high
        reference levels when the reference method is set to Percent or
        absolute. This command affects the results of rise and fall
        measurements.
        """

        method = method.upper()
        level = level.upper()
        if method not in ['ABSOLUTE', 'PERCENT']:
            ValueError("Invalid Method")
        if level not in ['HIGH', 'MID', 'LOW']:
            ValueError("Invalid level")

        self.instrument.write(f'MEASU:REFL:{method}:{level} {threshold}')

        return None

    def get_measure_ref_level(self, method, level):
        """
        get_measure_ref_level(method, level)

        method: (str) reference method, valid options are 'ABSOLUTE',
                and 'PERCENT'. Arguement is not case-sensitive.
        level: (str) reference level to adjust, valid options are 'HIGH',
                'MID', and 'LOW'. Arguement is not case-sensitive.

        returns:
        threshold: (float) threshold to set the desired measurement
                    reference at; either in V or % depending on method.

        Gets the percent/voltage that is used to calculate the low/mid/high
        reference levels when the reference method is set to Percent or
        absolute.
        """

        method = method.upper()
        level = level.upper()
        if method not in ['ABSOLUTE', 'PERCENT']:
            ValueError("Invalid Method")
        if level not in ['HIGH', 'MID', 'LOW']:
            ValueError("Invalid level")

        resp = self.instrument.query(f'MEASU:REFL:{method}:{level}?')

        return float(resp.strip('\n'))

    def set_measure_config(self, channel, meas_type, meas_idx):
        """
        set_measure_config(channel, meas_type, meas_idx)

        channel: (int) channel to provide the source of the measurement
                    Should be 1-4.
        meas_type: (str) the type of measurement to perform.

        meas_idx: (int) measurement number to assign to the
                    measurement described by the above parameters.
                    Can be 1-8.

        valid measurements are:
        AMPLITUDE, AREA, BURST, CAREA, CMEAN, CRMS, DELAY, FALL,
        FREQUENCY, HIGH, HITS, LOW, MAXIMUM, MEAN, MEDIAN, MINIMUM,
        NDUTY, NOVERSHOOT, NWIDTH, PDUTY, PEAKHITS, PERIOD, PHASE,
        PK2PK, POVERSHOOT, PTOP, PWIDTH, QFACTOR, RISE, RMS, SIGMA1,
        SIGMA2, SIGMA3, SNRATIO, STDDEV, UNDEFINED

        Arguement is not case-sensitive

        Sets up a measurement on the desired channel.
        """

        measurement_types = ('AMPLITUDE', 'AREA', 'BURST', 'CAREA',
                             'CMEAN', 'CRMS', 'DELAY', 'DISTDUTY',
                             'EXTINCTDB', 'EXTINCTPCT', 'EXTINCTRATIO',
                             'EYEHEIGHT', 'EYEWIDTH', 'FALL', 'FREQUENCY',
                             'HIGH', 'HITS', 'LOW', 'MAXIMUM', 'MEAN',
                             'MEDIAN', 'MINIMUM', 'NCROSS', 'NDUTY',
                             'NOVERSHOOT', 'NWIDTH', 'PBASE', 'PCROSS',
                             'PCTCROSS', 'PDUTY', 'PEAKHITS', 'PERIOD',
                             'PHASE', 'PK2PK', 'PKPKJITTER', 'PKPKNOISE',
                             'POVERSHOOT', 'PTOP', 'PWIDTH', 'QFACTOR',
                             'RISE', 'RMS', 'RMSJITTER', 'RMSNOISE',
                             'SIGMA1', 'SIGMA2', 'SIGMA3', 'SIXSIGMAJIT',
                             'SNRATIO', 'STDDEV', 'UNDEFINED', 'WAVEFORMS')

        meas_type = meas_type.upper()
        if meas_type not in measurement_types:
            raise ValueError("Measurement Type not supported")

        self.clear_measure(meas_idx)
        self.instrument.write(f'MEASU:MEAS{meas_idx}:SOU CH{channel}')
        self.instrument.write(f'MEASU:MEAS{meas_idx}:TYP {meas_type}')
        self.instrument.write(f'MEASU:MEAS{meas_idx}:STATE ON')
        return None

    def get_measure_config(self, meas_idx):
        """
            get_measure_config(meas_idx)

            meas_idx: (int) measurement number to assign to the
                        measurement described by the above parameters.
                        Can be 1-8.

            returns:
            channel: (int) channel to provide the source of the measurement
                        Should be 1-4.
            meas_type: (str) the type of measurement to perform.

            returns the setup information of measurement # meas_idx.
        """

        meas_type = self.instrument.query(f'MEASU:MEAS{meas_idx}:TYP?')
        meas_type = meas_type.strip('\n')

        if meas_type == 'UNDEFINED':
            channel = None
        else:
            channel = self.instrument.query(f'MEASU:MEAS{meas_idx}:SOU?')
            channel = int(channel.strip('\n').lstrip('CH3'))

        return meas_type, channel

    def clear_measure(self, meas_idx):
        """
        clear_measure(meas_idx)

        meas_idx: (int) measurement number to assign to the measurement
                    described by the above parameters. Can be 1-8.

        Clears measurement settings from the oscilloscopes memory and
        removes the measurement from the screeen
        """
        self.instrument.write(f'MEASU:MEAS{meas_idx}:STATE OFF')
        self.instrument.write(f'MEASU:MEAS{meas_idx}:TYP UNDEFINED')
        return None

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

            query_cmd = f"MEASU:MEAS{int(idx)}:VAL?"
            response = self.instrument.query(query_cmd)

            try:
                data.append(float(response))
            except ValueError:
                data.append(float('nan'))

        if len(data) == 1:
            return data[0]
        return tuple(data)

    def get_measure_statistics(self, meas_idx):
        """
        get_measure_statistics(meas_idx)

        meas_idx: (int) measurement number to assign to the measurement
                    described by the above parameters. Can be 1-8.

        returns:
        stats: dictionary containing measurement statistics

        Querys the statistics for a measurement. dictionaty containing the
        stats has the following keys: 'mean' (float), 'min' (float),
        'max' (float), 'std' (float), and 'count' (int).
        """

        stats = {}

        resp = self.instrument.query(f'MEASU:MEAS{meas_idx}:MEAN?')
        stats['mean'] = float(resp)

        resp = self.instrument.query(f'MEASU:MEAS{meas_idx}:MINI?')
        stats['min'] = float(resp)

        resp = self.instrument.query(f'MEASU:MEAS{meas_idx}:MAX?')
        stats['max'] = float(resp)

        resp = self.instrument.query(f'MEASU:MEAS{meas_idx}:COUNT?')
        stats['count'] = float(resp)

        resp = self.instrument.query(f'MEASU:MEAS{meas_idx}:STD?')
        stats['std'] = float(resp)

        return stats

    def reset_measure_statistics(self):
        """
        reset_measure_statistics()

        resets the accumlated measurements used to calculate statistics
        """
        self.instrument.write('MEASU:STATI:COUN RESET')
        return None

    def enable_measure_statistics(self):
        """
        enable_measure_statistics()

        enables the calculation of statistics on a measurement
        """

        self.instrument.write('MEASU:STATI:MODE ALL')
        return None

    def disable_measure_statistics(self):
        """
        disable_measure_statistics()

        disables the calculation of statistics on a measurement
        """

        self.instrument.write('MEASU:STATI:MODE OFF')
        return None

    def get_image(self, image_title: Union[str, Path], **kwargs) -> None:
        """
        get_image(image_title, **kwargs)

        Saves current oscillocope image to file at the path specified by
        "image_title". The Image will be saved as .png. If no path information
        is included in "image_title" the image will be saved in the current
        execution directory.

        Args:
            image_title (Union[str, Path]): path name of image, file extension
                will be added automatically
        Kwargs:
            save_to_device (bool): Determines which computer the image is
                stored on. If True "image_title" is assumed to be a path on the
                oscilloscope itself and the image will be stroed there.
                Otherwise if False the image is transfered to the remote
                machine and it is stored there at "image_title".
                Defaults to False.
        """

        # add file extension
        if isinstance(image_title, Path):
            file_path = image_title.parent.joinpath(image_title.name + '.png')
        elif isinstance(image_title, str):
            file_path = f"{image_title}.png"
        else:
            raise ValueError('image_title must be a str or path-like object')

        if kwargs.get('save_to_device', False):
            # save to location on scope
            self.instrument.write(f'HARDCopy:FILEName "{file_path}"')
            self.instrument.write('HARDCopy STARt')
        else:

            # save to temp location on scope
            buffer_path = r'C:\TekScope\Screen Captures\temp.png'

            self.instrument.write(f'HARDCopy:FILEName "{buffer_path}"')
            self.instrument.write('HARDCopy STARt')
            self.instrument.write('*OPC?')  # done yet?

            # transfer file to computer
            self.instrument.write(f'FILESystem:READFile "{buffer_path}"')
            raw_data = self.instrument.read_raw()

            # save image
            with open(file_path, 'wb') as file:
                file.write(raw_data)

    def set_record_length(self, length: int) -> None:
        """
        set_record_length(length)

        Changes the length of the waveform buffer to the value specified by
        'length'. Note: different scopes have different possible record length
        options, if the value specified in this function isn't availible on the
        scope connected round to the nearest availible setting.

        Args:
            length (int): number of points to capture in the waveform buffer
                per scope trigger
        """

        self.instrument.write(f"HOR:RECO {int(length)}")

    def get_record_length(self) -> int:
        """
        get_record_length()

        retrives the current length of the waveform buffer.

        Returns:
            int: len of the waveform buffer
        """

        return int(self.instrument.query("HOR:RECO?"))

    def set_horizontal_scale(self, scale: float) -> None:
        """
        set_horizontal_scale(scale)

        sets the scale of horizontal divisons (for all channels) to the
        specified value in seconds.

        Args:
            scale (float): time scale across one horizontal division on the
                display in seconds.
        """

        self.instrument.write(f'HOR:SCA {float(scale)}')

    def get_horizontal_scale(self) -> float:
        """
        get_horizontal_scale()

        Retrieves the horizontal scale used to accquire waveform data.

        Returns:
            float: horizontal scale in seconds per division.
        """

        response = self.instrument.query('HOR:SCA?')
        return float(response)

    def set_horizontal_roll_mode(self, mode):
        """
        set_horizontal_roll_mode(mode)

        mode: str or int, roll mode

        Sets the horizontal roll mode of the scope acquisition, valid arguments
        are 'on', 'off', or 'auto' (not case sensitive). options 'on' and 'off'
        can alternatively be set with the int values 1 and 0.
        """

        if type(mode) == int:
            if mode in [0, 1]:
                options = ["OFF", "ON"]
                self.instrument.write(f'HOR:ROLL {options[mode]}')
        elif type(mode) == str:
            mode = mode.upper()
            if mode in ["OFF", "ON", "AUTO"]:
                self.instrument.write(f'HOR:ROLL {mode}')
        else:
            raise ValueError(f"invalid value {mode} for arg 'mode'")

        return None

    def get_horizontal_roll_mode(self):
        """
        get_horizontal_roll_mode()

        returns:
            mode: str, roll mode

        Queries the horizontal roll mode of the scope acquisition,
        valid return values are 'on', 'off', or 'auto'
        """

        resp = self.instrument.query('HOR:ROLL?')
        resp = resp.strip()

        return resp

    def set_cursor_state(self, state):
        """
        set_cursor_state(state)

        state: int, 1 or 0

        Enables or Disables the visabiltiy of cursors on the oscilloscope
        display. Sets cursors on if state = 1 and off if state = 0
        """

        self.instrument.write(f'CURS:STATE {state}')
        return None

    def get_cursor_state(self):
        """
        get_cursor_state()

        returns:
            state: int, 1 or 0

        Returns the state of the visabiltiy of cursors on the oscilloscope
        display. Cursors are on if state = 1 and off if state = 0
        """

        resp = self.instrument.query('CURS:STATE?')
        state = int(resp)
        return state

    def set_cursor_source(self, channel):
        """
        set_cursor_source(channel)

        channel: int, channel number of channel

        sets the source of the cursors data to the channel specified by
        'channel'
        """

        self.instrument.write(f'CURS:SOU CH{channel}')
        return None

    def get_cursor_source(self):
        """
        get_cursor_source()

        returns:
            source: str, cursor source

        returns the source used for the cursors data
        """

        resp = self.instrument.query('CURS:SOU?')
        source = resp.strip()
        return source

    def set_cursor_function(self, function):
        """
        set_cursor_function(function)

        function: str, cursor function. Valid options are: OFF, HBA, VBA,
                  SCREEN, WAVE. Not case-sensitive.

        Sets the function of the cursors, below is a description of each
        function:
            OFF: Cursors are off
            HBA: Cursors show horizontal information only
            VBA: Cursors show vertical information only
            SCREEN: Cursors show information based on where they are on the
                 visable part of the captured data
            WAVE: Cursors show information only for the waveform they're
                  assigned to.
        """

        function = function.upper()
        if function in ['OFF', 'HBA', 'VBA', 'SCREEN', 'WAVE']:
            self.instrument.write(f'CURS:FUNC {function}')
        else:
            raise ValueError(f"invalid value {function} for arg 'function'")

        return None

    def get_cursor_function(self):
        """
        get_cursor_function()

        returns:
            function: str, cursor function. Valid options are: OFF, HBA, VBA,
                    SCREEN, WAVE. Not case-sensitive.

        returns the function used by the cursors, below is a description of
        each function:
            OFF: Cursors are off
            HBA: Cursors show horizontal information only
            VBA: Cursors show vertical information only
            SCREEN: Cursors show information based on where they are on the
                 visable part of the captured data
            WAVE: Cursors show information only for the waveform they're
                  assigned to.
        """

        resp = self.instrument.query('CURS:FUNC?')
        function = resp.strip()
        return function

    def set_cursor_x_position(self, cursor_num, position):
        """
        set_cursor_x_position(cursor_num, position)

        cursor_num: int, 1 or 2 index of the cursor to adjust
        position: float, trigger time

        sets the horizontal position of the cursor specified by 'cursor_num' to
        the position 'position' which is the capture time relative to the
        trigger.
        """

        self.instrument.write(f'CURS:SCREEN:XPOSITION{cursor_num} {position}')
        return None

    def get_cursor_x_position(self, cursor_num):
        """
        get_cursor_x_position(cursor_num)

        cursor_num: int, 1 or 2 index of the cursor to adjust

        returns:
            position: float, trigger time

        gets the horizontal position of the cursor specified by 'cursor_num'.
        Position is the capture time relative to the trigger.
        """

        resp = self.instrument.query(f'CURS:SCREEN:XPOSITION{cursor_num}?')
        position = float(resp)
        return position

    def set_cursor_y_position(self, cursor_num, position):
        """
        set_cursor_y_position(cursor_num, position)

        cursor_num: int, 1 or 2 index of the cursor to adjust
        position: float, channel specific

        sets the vertical position of the cursor specified by 'cursor_num' to
        the position 'position', the units of position depend on the units of
        the observed waveform
        """

        self.instrument.write(f'CURS:SCREEN:YPOSITION{cursor_num} {position}')
        return None

    def get_cursor_y_position(self, cursor_num):
        """
        get_cursor_y_position(cursor_num)

        cursor_num: int, 1 or 2 index of the cursor to adjust
        position: float, channel specific

        gets the vertical position of the cursor specified by 'cursor_num'.
        The units of position depend on the units of the observed waveform.
        """

        resp = self.instrument.query(f'CURS:SCREEN:YPOSITION{cursor_num}?')
        position = float(resp)
        return position

    def get_acquisition_number(self):
        """
        get_acquisition_number()

        returns:
            acquisition_number: int, the number of acquisition

        returns the number of times the scope has acquired data from a trigger
        event since it started acquisition. For example, this should return 1
        after being successfully single-triggered.
        """

        resp = self.instrument.query('ACQ:NUMAC?')
        acq_num = int(resp)
        return acq_num


if __name__ == '__main__':
    pass
