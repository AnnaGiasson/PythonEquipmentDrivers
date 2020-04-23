from pythonequipmentdrivers import Scpi_Instrument as _Scpi_Instrument
import struct as _struct
import numpy as _np


class Tektronix_MSO5xxx(_Scpi_Instrument):
    """
    Tektronix_MSO5xxx(address)

    address : str, address of the connected oscilloscope

    object for accessing basic functionallity of the Tektronix_MSO5xxx
    Family of Oscilloscopes
    """

    def __init__(self, address):
        super().__init__(address)

        # get image formatting
        self.instrument.write('EXP:FORM PNG')  # image is a .png file
        self.instrument.write('HARDC:PORT FILE')  # image is stored as a file
        self.instrument.write('HARDC:PALE COLOR')  # color image (alt INKS)
        self.instrument.write('HARDC:LAY LAN')  # landscape image
        self.instrument.write('HARDC:VIEW FULLNO')  # no menu, full-screen wvfm
        return

    def select_channel(self, channel, state):
        """
        select_channel(channel)

        channel: int, channel number of channel
                    valid options are 1,2,3, and 4

        state: int, whether or not the respective channel is
                selected/visable on the screen. Valid options are 0 or 1

        selects the specified channel. This is allow the specified channel
        to be seen on top of the others in the display. With a given
        channel selected any cursor measurements will then correspond to
        the selected channel.
        """

        cmd_str = f'SEL:CH{channel} '
        if state == 1:
            cmd_str += "ON"
        elif state == 0:
            cmd_str += "OFF"
        else:
            raise ValueError(f"Invalid arguement 'state': {state}")
        self.instrument.write(cmd_str)
        return

    # investigate using faster data encoding scheme     # check
    def get_channel_data(self, channel, start_percent=0, stop_percent=100):
        """
        get_channel_data(channel, start_percent=None, stop_percent=None)

        channel: int, channel number of the waveform to be transferred.
            valid options are 1,2,3, and 4
        start_percent (optional): int, point in time to begin the waveform
                                    transfer number represents percent of the
                                    record length. Valid settings are 0-100.
                                    Default is 0%
        stop_percent (optional): int, point in time to end the waveform
                                    transfer number represents percent of the
                                    record length. Valid settings are 0-100.
                                    Default is 100%

        returns: tuple, (time array, amplitude array), both arrays are of
                    floats

        returns waveform data from the oscilloscope on the specified
        channel. Optionally points to start / stop the transfer can be
        given. start_percent and stop_percent can be set independently, the
        waveform returned will always start from the smaller of the two and
        go to the largest. By default the entire waveform will be
        transferred.
        """

        # get data to define waveform capture with indexes
        record_len = self.get_record_length()

        #   enforce valid start/stop points
        start_percent = int(_np.clip(start_percent, 0, 100))
        stop_percent = int(_np.clip(stop_percent, 0, 100))

        start_idx = int(start_percent/100*record_len)
        stop_idx = int(stop_percent/100*record_len)

        # configure data transfer
        self.instrument.write(f'DATA:START {start_idx}')  # array start pos
        self.instrument.write(f'DATA:STOP {stop_idx}')  # array stop pos
        self.instrument.write(f'DATA:SOU CH{channel}')  # data source
        #   byte enc. (signe int little-endian)
        self.instrument.write('DATA:ENC SRP')

        # get info to convert bytes to an analog waveform
        #   number of counts corresponding to amp of 0
        bytes_offset = float(self.instrument.query("WFMPRE:YOFF?"))

        #   conversion between counts and amp
        bytes_amp_scale = float(self.instrument.query("WFMPRE:YMULT?"))

        #   offset of the waveform on the scope
        wvfrm_offset = float(self.instrument.query("WFMPRE:YZERO?"))

        #   sampling time
        dt = float(self.instrument.query("WFMPRE:XINCR?"))

        # get the data
        self.instrument.write('CURVE?')
        data = self.instrument.read_raw()

        #   strip off header
        header_len = 2 + int(data[1])
        adc_wave = data[header_len:-1]

        # convert from byte-string to array (counts)
        adc_wave = _np.array(_struct.unpack('%sB' % len(adc_wave),
                                            adc_wave))

        # convert to analog waveform
        amplitude_array = (adc_wave - bytes_offset)*bytes_amp_scale
        amplitude_array += wvfrm_offset

        time_array = _np.arange(0, dt*len(amplitude_array), dt)

        # accounting for trigger position
        trig_percent = self.get_trigger_position()
        trig_idx = int(trig_percent/100*record_len)
        time_array -= (trig_idx - min([start_idx, stop_idx]))*dt

        return time_array, amplitude_array

    def set_channel_label(self, channel, label):
        """
        set_channel_label(channel, label)

        channel: int/list, channel number or list of channel numbers to
                    update label of.
        label: str/list, text label or list of text labels to assign to
                each channel listed in "channel"

        updates the text label on a channel specified by "channel" with the
        value given in "label". Alternatively, lists can be passed for each
        channel and label to set multiple labels at once. List inputs
        should be the same length for both inputs
        """

        if type(channel) == list and type(label) == list:
            if len(channel) != len(label):
                raise ValueError("Lengths of 'channel' and 'label' are "
                                 + "mismatched")
            for chan, lab in zip(channel, label):
                self.instrument.write(f'CH{chan}:LAB:NAM "{lab}"')

        elif type(channel) == int and type(label) == str:
            self.instrument.write(f'CH{channel}:LAB:NAM "{label}"')

        else:
            raise ValueError("Channel should be int or list of ints, label"
                             + " should be string or list of strings")
        return

    def get_channel_label(self, channel):
        """
        get_channel_label(channel)

        channel: int channel number to get label of.

        retrives the label currently used by the channel specified by
        'channel'

        returns string
        """
        response = self.instrument.query(f"CH{channel}:LAB:NAM?")
        return response.strip().replace('"', '')

    def set_channel_label_position(self, channel, rel_coords):
        """
        set_channel_label_position(channel, rel_coords)

        channel: int, channel number of channel whose bandwidth setting
                    will be adjusted. valid options are 1, 2, 3, and 4.

        re_coords is a tuple (float, float) of the relative x,y positon of
        the channel label w.r.t. the numerical label in # of divisions
        """
        x_coord, y_coord = rel_coords
        self.instrument.write(f'CH{channel}:LAB:XPOS {x_coord}')
        self.instrument.write(f'CH{channel}:LAB:YPOS {y_coord}')
        return

    def get_channel_label_position(self, channel):
        """
        get_channel_label_position(channel)

        channel: int, channel number of channel whose bandwidth setting
                    will be adjusted. valid options are 1, 2, 3, and 4.

        returns a tuple (float, float) of the relative x,y positon of the
        channel label w.r.t. the numerical label in # of divisions
        """
        x_coord = float(self.instrument.write(f'CH{channel}:LAB:XPOS?'))
        y_coord = float(self.instrument.write(f'CH{channel}:LAB:YPOS?'))
        return x_coord, y_coord

    def set_channel_bandwidth(self, channel, bandwidth):
        """
        set_channel_bandwidth(channel, bandwidth)

        channel: int, channel number of channel whose bandwidth setting
                    will be adjusted. valid options are 1, 2, 3, and 4.
        bandwidth: int or float, desired bandwidth setting for "channel"
                    in Hz

        sets the bandwidth limiting of "channel" to the value specified by
        "bandwidth".

        Note: different probes have different possible bandwidth settings,
        if the value specified in this function isn't availible on the
        probe connected to the specified input it will likely round UP to
        the nearest availible setting
        """
        if type(bandwidth) == str:
            if bandwidth.upper() == 'FULL':
                self.instrument.write(f"CH{channel}:BAN FULL")
        else:
            self.instrument.write(f"CH{channel}:BAN {bandwidth}")
        return

    def get_channel_bandwidth(self, channel):
        """
        get_channel_bandwidth(channel)

        channel: int, channel number of channel
                    valid options are 1,2,3, and 4

        retrived bandwidth limiting setting used by the specified channel
        in Hz.

        returns float
        """

        response = self.instrument.query(f"CH{channel}:BAN?")
        return float(response)

    def set_channel_scale(self, channel, scale):
        """
        set_channel_scale(channel, scale)

        channel: int, channel number of channel
                    valid options are 1,2,3, and 4

        scale: int/float, scale of the channel amplitude across one
        vertical division on the display.

        sets the scale of vertical divisons for the specified channel
        """

        self.instrument.write(f"CH{channel}:SCA {scale}")
        return

    def get_channel_scale(self, channel):
        """
        get_channel_scale(channel)

        channel: int, channel number of channel
                    valid options are 1,2,3, and 4

        retrives the scale for vertical divisons for the specified channel

        returns: float
        """

        response = self.instrument.query(f"CH{channel}:SCA?")
        return float(response)

    def set_channel_offset(self, channel, offset):
        """
        set_channel_offset(channel, offset)

        channel: int, channel number of channel
            valid options are 1,2,3, and 4

        offset: int/float, offset added to the channels waveform on the
                display.

        sets the vertical offset for the display of the specified channel.
        """

        self.instrument.write(f"CH{channel}:OFFS {offset}")
        return

    def get_channel_offset(self, channel):
        """
        get_channel_offset(channel)

        channel: int, channel number of channel
                    valid options are 1,2,3, and 4

        retrives the vertical offset for the display of the specified
        channel.

        returns: float
        """

        response = self.instrument.query(f"CH{channel}:OFFS?")
        return float(response)

    def set_channel_position(self, channel, position):
        """
        set_channel_position(channel, position)

        channel: int, channel number of channel
                    valid options are 1,2,3, and 4

        position: int/float, vertical postion of the 0 point for 'channel'

        sets the vertical postion for the 0 point of the waveform
        specified by 'channel'
        position is represented by +/- number of division from the middle
        of the screen.
        """

        self.instrument.write(f"CH{channel}:POS {position}")
        return

    def get_channel_position(self, channel):
        """
        get_channel_position(channel)

        channel: int, channel number of channel
                    valid options are 1,2,3, and 4

        retrieves the vertical postion for the 0 point of the waveform
        specified by 'channel' position is represented by +/- number of
        division from the middle of the screen.

        returns: float
        """

        response = self.instrument.query(f"CH{channel}:POS?")
        return float(response)

    def set_channel_coupling(self, channel, coupling):
        """
        set_channel_coupling(channel, coupling)

        channel: int, channel number of channel
                    valid options are 1,2,3, and 4
        coupling: (str) coupling mode, valid options are "DC", "AC", "GND",
                    and "DC REJ". (not case-sensitive)

        sets the coupling used on a the specified channel.
        """

        coupling = coupling.upper()
        if coupling not in ["DC", "AC", "GND", "DCREJ"]:
            raise ValueError(f"Invalid Coupling option: {coupling}")
        self.instrument.write(f"CH{channel}:COUP {coupling}")
        return

    def get_channel_coupling(self, channel):
        """
        get_channel_coupling(channel)

        channel: int, channel number of channel
                    valid options are 1,2,3, and 4

        returns:
        coupling: (str) coupling mode, valid options are "DC", "AC", "GND",
                    and "DC REJ". (not case-sensitive)

        gets the coupling used on a the specified channel.
        """

        resp = self.instrument.query(f"CH{channel}:COUP?")
        return resp.strip()

    def set_trigger_acquire_state(self, state):
        """
        set_trigger_acquire_state(state)

        state: (int) acquire state, valid arguements are 0 (stop) and
                1 (run/acquire)

        sets the state of the oscilloscopes acquision mode, whether its
        currently acquiring new data (run / 1) or not (stop / 0).
        """

        self.instrument.write(f"ACQ:STATE {state}")
        return

    def get_trigger_acquire_state(self):
        """
        get_trigger_acquire_state()

        returns:
        state: (int) acquire state, valid arguements are 0 (stop) and
                1 (run/acquire)

        gets the state of the oscilloscopes acquision mode, whether its
        currently acquiring new data (run / 1) or not (stop / 0).
        """

        resp = self.instrument.query("ACQ:STATE?")
        return int(resp)

    def trigger_run(self):
        """
        trigger_run()

        sets the state of the oscilloscopes acquision mode to acquire new
        data. equivalent to set_trigger_acquire_state(1).
        """

        self.set_trigger_acquire_state(1)
        return

    def trigger_stop(self):
        """
        trigger_stop()

        sets the state of the oscilloscopes acquision mode to stop
        acquiring new data. equivalent to set_trigger_acquire_state(0).
        """
        self.set_trigger_acquire_state(0)
        return

    def trigger_force(self):
        """
        trigger_force()

        forces a trigger event to occur
        """

        self.instrument.write("TRIG FORC")
        return

    def trigger_single(self):
        """
        trigger_single()

        arms the oscilloscope to capture a single trigger event.
        """

        self.set_trigger_acquire_state(1)
        self.instrument.write("ACQ:STOPA SEQ")
        return

    def set_trigger_source(self, channel):
        """
        set_trigger_source(channel)

        channel: int, channel number of channel
                    valid options are 1,2,3, and 4

        sets the trigger source to the indicated channel number
        """

        self.instrument.write(f'TRIGger:A:EDGE:SOUrce CH{channel}')
        return

    def get_trigger_source(self):
        """
        get_trigger_source()


        returns:
        channel: int, channel number of channel
                    valid options are 1,2,3, and 4

        gets the channel number for the trigger source
        """

        resp = self.instrument.query('TRIGger:A:EDGE:SOUrce?')
        channel = int(resp.replace('CH', ''))
        return channel

    def set_trigger_position(self, percent):
        """
        set_trigger_position(percent)

        percent: (int) percent of the horizontal capture window valid
                    values are between 0-100

        Sets the horizontal position of the trigger point as a percentage
        of the capture window.
        """

        self.instrument.write(f"HOR:POS {percent}")
        return

    def get_trigger_position(self):
        """
        get_trigger_position()

        returns:
        percent: (int) percent of the horizontal capture window valid
                    values are between 0-100

        gets the horizontal position of the trigger point as a percentage
        of the capture window.
        """

        return float(self.instrument.query("HOR:POS?"))

    def set_trigger_slope(self, slope):
        """
        set_trigger_slope(slope)

        slope: str, trigger edge polarity. Valid options are 'rise', 'fall', or
        'either'

        sets the edge polarity of the acquistion trigger
        """

        slope = slope.upper()
        self.instrument.write(f'TRIGger:A:EDGE:SLOpe {slope}')
        return

    def get_trigger_slope(self):
        """
        get_trigger_slope()

        returns:
        slope: str, trigger edge polarity. Valid options are 'rise', 'fall', or
        'either'

        gets the edge polarity of the acquistion trigger
        """

        resp = self.instrument.query('TRIGger:A:EDGE:SLOpe?')
        slope = resp.rstrip('\n').lower()

        return slope

    def set_trigger_mode(self, mode):
        """
        set_mode(mode)

        mode: (str) trigger mode. Valid modes are "AUTO" and "NORM"

        sets the mode of the trigger in the oscilloscopes acquisition. In
        the AUTO mode the scope will periodically automatically trigger and
        the waveform buffers will update. In the NORM mode the trigger
        needs to be actively asserted for this to take place.
        """

        mode = mode.upper()
        if mode not in ["AUTO", "NORM", "NORMAL"]:
            raise ValueError(f"Invalid mode: {mode}")
        self.instrument.write(f"TRIG:A:MOD {mode}")
        return

    def get_trigger_mode(self):
        """
        get_mode()

        returns:
        mode: (str) trigger mode. Valid modes are "AUTO" and "NORM"

        Gets the mode of the trigger in the oscilloscopes acquisition. In
        the AUTO mode the scope will periodically automatically trigger and
        the waveform buffers will update. In the NORM mode the trigger
        needs to be actively asserted for this to take place.
        """

        response = self.instrument.query("TRIG:A:MOD?")
        return response.rstrip("\n")

    def set_trigger_level(self, level):
        """
        set_level(level)

        level: (float) vertical position of the trigger, units depend on
                the signal being triggered on.

        Sets the vertical position of the trigger point in the units of the
        triggering waveform
        """

        self.instrument.write(f"TRIG:A:LEV {level}")
        return

    def get_trigger_level(self):
        """
        get_level()

        returns
        level: (float) vertical position of the trigger, units depend on
                the signal being triggered on.

        Gets the vertical position of the trigger point in the units of the
        triggering waveform
        """

        return float(self.instrument.query("TRIG:A:LEV?"))

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
        return

    def get_measure_method(self):
        """
        get_measure_method()

        returns:
        method: (str) measurement method, valid options are 'HISTOGRAM',
                'MEAN', and 'MINMAX'. Arguement is not case-sensitive.

        Gets the method used to calculate the 0% and 100% reference levels.
        """

        resp = self.instrument.query(f'MEASU:METH?')
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
        return

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

        return

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

        measurement_types = ['AMPLITUDE', 'AREA', 'BURST', 'CAREA',
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
                             'SNRATIO', 'STDDEV', 'UNDEFINED', 'WAVEFORMS']

        meas_type = meas_type.upper()
        if meas_type not in measurement_types:
            raise ValueError("Measurement Type not supported")

        self.clear_measure(meas_idx)
        self.instrument.write(f'MEASU:MEAS{meas_idx}:SOU CH{channel}')
        self.instrument.write(f'MEASU:MEAS{meas_idx}:TYP {meas_type}')
        self.instrument.write(f'MEASU:MEAS{meas_idx}:STATE ON')
        return

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
        return

    def get_measure_data(self, meas_idx):
        """
        get_measure_data(meas_idx)

        meas_idx: (int) measurement number to assign to the measurement
                    described by the above parameters. Can be 1-8.

        Returns the value of the measurement 'meas_idx' as a float.
        """

        resp = self.instrument.query(f'MEASU:MEAS{meas_idx}:VAL?')
        return float(resp)

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
        return

    def enable_measure_statistics(self):
        """
        enable_measure_statistics()

        enables the calculation of statistics on a measurement
        """

        self.instrument.write('MEASU:STATI:MODE ALL')
        return

    def disable_measure_statistics(self):
        """
        disable_measure_statistics()

        disables the calculation of statistics on a measurement
        """

        self.instrument.write('MEASU:STATI:MODE OFF')
        return

    def get_image(self, image_title):
        """
        This scope does not have a function to directly stream the image data
        from the screen buffer to a remote connection, however there are
        commands to save to internal memory and transfer saved files over the
        remote connection. This function saves the scope image to a temporary
        file on the scope, transfers the file over the remote connection, then
        deletes the copy in the scopes internal memory.

        automatically adds .png to the end of image_title
        """

        image_buffer_path = r'C:\TekScope\Screen Captures\temp.png'

        self.instrument.write(f'HARDCopy:FILEName "{image_buffer_path}"')
        self.instrument.write('HARDCopy STARt')

        # SAVE:IMAGE is an OPC generating command. Wait for instrument to
        # finish writing the screenshot to disk by querying *OPC?
        self.instrument.write('*OPC?')

        self.instrument.write(f'FILESystem:READFile "{image_buffer_path}"')

        # Read back the data sent from the instrument and write the data
        # (un-altered) it to a .png file on your local system.
        raw_data = self.instrument.read_raw()

        fid = open(f"{image_title}.png", 'wb')
        fid.write(raw_data)
        fid.close()

        self.instrument.write(f'FILESystem:DELEte "{image_buffer_path}"')
        return

    def set_record_length(self, length):
        """
        set_record_length(length)

        length: int, number of points to capture in the waveform buffer per
                scope trigger

        changes the length of the waveform buffer to the value specified by
        'length'. Note: different scopes have different possible record length
        options, if the value specified in this function isn't availible on the
        scope connected round to the nearest availible setting.
        """

        self.instrument.write(f"HOR:RECO {length}")
        return

    def get_record_length(self):
        """
        get_record_length()

        retrives the current length of the waveform buffer.

        returns: float
        """

        return float(self.instrument.query("HOR:RECO?"))

    def set_horizontal_scale(self, scale):
        """
        set_horizontal_scale(scale)

        scale: int/float, time scale across one horizontal division on the
               display in seconds.

        sets the scale of horizontal divisons (for all channels) to the
        specified value in seconds.
        """

        self.instrument.write(f"HOR:SCA {scale}")
        return

    def get_horizontal_scale(self):
        """
        get_horizontal_scale()

        retrieves the scale of horizontal divisons in seconds.

        returns: float
        """

        return float(self.instrument.query("HOR:SCA?"))

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

        return

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
        return

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
        return

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

        return

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
        return

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
        return

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
