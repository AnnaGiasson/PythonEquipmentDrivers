from pythonequipmentdrivers import Scpi_Instrument
import struct
import numpy as np
from time import sleep


class Tektronix_DPO4xxx(Scpi_Instrument):
    """
    Tektronix_DPO4xxx(address)

    address : str, address of the connected oscilloscope

    object for accessing basic functionallity of the Tektronix_DPO4xxx
    Family of Oscilloscopes
    """

    # todo:
    #   write further documentation on class methods
    #   add additional functionality for setting / getting scope measurements
    #   look into different encoding schemes to speed up
    #   self.channel.get_data() method

    def __init__(self, address, **kwargs):
        super().__init__(address, **kwargs)
        return None

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
        return None

    # investigate using faster data encoding scheme
    def get_channel_data(self, channel, start_percent=None, stop_percent=None):
        """
        get_channel_data(channel, start_percent=None, stop_percent=None)

        channel: int, channel number of the waveform to be transferred.
            valid options are 1,2,3, and 4
        start_percent (optional): int, point in time to begin the waveform
                                    transfer number represents percent of the
                                    record length. Valid settings are 0-100.
                                    Default is None which will select 0%
        stop_percent (optional): int, point in time to end the waveform
                                    transfer number represents percent of the
                                    record length. Valid settings are 0-100.
                                    Default is None which will select 0%

        returns: tuple, (time array, amplitude array), both arrays are of
                    floats

        returns waveform data from the oscilloscope on the specified
        channel. Optionally points to start / stop the transfer can be
        given. start_percent and stop_percent can be set independently, the
        waveform returned will always start from the smaller of the two and
        go to the largest. By default the entire waveform will be
        transferred.
        """

        # set up scope for data transfer
        self.instrument.write(f"DATA:SOU CH{channel}")  # Set data source
        self.instrument.write("DATA:WIDTH 1")  # ?? used in example
        self.instrument.write("DATA:ENC RPB")  # Set data encoding type

        # get waveform metadata
        bytes_offset = float(self.instrument.query("WFMPRE:YOFF?"))
        bytes_amp_scale = float(self.instrument.query("WFMPRE:YMULT?"))

        wvfrm_offset = float(self.instrument.query("WFMPRE:YZERO?"))
        dt = float(self.instrument.query("WFMPRE:XINCR?"))  # sampling time

        trig_percent = self.get_trigger_position()
        record_len = self.get_record_length()

        # configure data transfer
        if start_percent is None:
            start_percent = 0
        else:
            start_percent = int(np.clip(start_percent, 0, 100))

        if stop_percent is None:
            stop_percent = 100
        else:
            stop_percent = int(np.clip(stop_percent, 0, 100))

        start_idx = int(start_percent/100*record_len)
        stop_idx = int(stop_percent/100*record_len)

        self.instrument.write(f"DATA:START {start_idx}")
        self.instrument.write(f"DATA:STOP {stop_idx}")

        # get data and format
        self.instrument.write("CURVE?")
        data = self.instrument.read_raw()
        header_len = 2 + int(data[1])

        adc_wave = data[header_len:-1]
        adc_wave = np.array(struct.unpack(f'{len(adc_wave)}B', adc_wave))
        amplitude_array = (adc_wave - bytes_offset)*bytes_amp_scale
        amplitude_array += wvfrm_offset

        time_array = np.arange(0, dt*len(amplitude_array), dt)
        # accounting for trigger position
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
                self.instrument.write(f'CH{chan}:LAB "{lab}"')

        elif type(channel) == int and type(label) == str:
            self.instrument.write(f'CH{channel}:LAB "{label}"')

        else:
            raise ValueError("Channel should be int or list of ints, label"
                             + " should be string or list of strings")
        return None

    def get_channel_label(self, channel):
        """
        get_channel_label(channel)

        channel: int channel number to get label of.

        retrives the label currently used by the channel specified by
        'channel'

        returns string
        """
        response = self.instrument.query(f"CH{channel}:LAB?")
        return response.rstrip("\n")

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

        self.instrument.write(f"CH{channel}:BAN {bandwidth}")
        return None

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
        return None

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
        return None

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
        return None

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

    def trigger_run_stop(self):
        self.instrument.write("FPANEL:PRESS RUnstop")
        return None

    def trigger_force(self):
        self.instrument.write("TRIG FORC")
        return None

    def trigger_single(self):
        self.instrument.write("FPANEL:PRESS SING")
        return None

    def set_trigger_position(self, percent):
        self.instrument.write(f"HOR:POS {percent}")
        return None

    def get_trigger_position(self):  # returns percent of record len
        return float(self.instrument.query("HOR:POS?"))

    def set_trigger_mode(self, mode):
        """Valid modes are "AUTO" and "NORM" """
        if not(mode in ["AUTO", "NORM"]):
            self.instrument.write("TRIG:A:MOD NORM")
        self.instrument.write(f"TRIG:A:MOD {mode}")
        return None

    def get_trigger_mode(self):
        response = self.instrument.query("TRIG:A:MOD?")
        return response.rstrip("\n")

    def set_trigger_level(self, level):
        self.instrument.write(f"TRIG:A:LEV {level}")
        return None

    def get_trigger_level(self):
        return float(self.instrument.query("TRIG:A:LEV?"))

    def set_zoom_mode(self, state):
        if state:
            self.instrument.write("ZOO:MODE ON")
        else:
            self.instrument.write("ZOO:MODE OFF")
        return None

    def get_zoom_mode(self):
        response = self.instrument.query("ZOO:MODE?")
        return response.rstrip("\n")

    def set_zoom_position(self, position):
        # position is a % of the record length
        self.instrument.write(f"ZOO:ZOOM:POS {position}")
        return None

    def get_zoom_position(self):
        response = self.instrument.query("ZOO:ZOOM:POS?")
        return float(response)

    def set_zoom_scale(self, scale):  # scale is the time/div
        self.instrument.write(f"ZOO:ZOOM:SCA {scale}")
        return None

    def get_zoom_scale(self):
        response = self.instrument.query("ZOO:ZOOM:SCA?")
        return float(response)

    def get_measure_data(self, index):
        response = self.instrument.query(f"MEASU:MEAS{index}:VAL?")
        return float(response)

    def get_image(self, image_title, buffering_delay=0):
        """
        get_image(image_title, buffering_delay=0)

        image_title: str, path name of image
        buffering_delay (optional): int/float, delay before reading back image
        data in seconds (default is 0s). Depending on the oscilloscope
            settings conversion of the data to an image may take longer than
            expected, this delay gives the scope more time to buffer the image.
        saves current oscillocope image to file at the path specified by
        image_title. image will be saved as .png. If no path information is
        included in image_title the image will be saved in the current
        execution directory
        """

        self.instrument.write("SAVE:IMAG:FILEF PNG")
        self.instrument.write("HARDCOPY START")
        self.instrument.write('*OPC?')
        sleep(buffering_delay)

        raw_data = self.instrument.read_raw()

        fid = open(f"{image_title}.png", 'wb')
        fid.write(raw_data)
        fid.close()
        return None

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
        return None

    def get_record_length(self):
        """
        get_record_length()

        retrives the current length of the waveform buffer.

        returns: float
        """

        return float(self.instrument.query("HOR:RECO?"))

    def set_persistence(self, exposure_time):
        """
        set_persistence(exposure_time)

        exposure_time: float or str, the exposure time for the oscilloscope
        capture display in seconds.
            valid values are positive numbers, if "max" is passed the maximum
            exposure time will be set

        sets the persistence of the waveform buffers to include all captures
        within a time window specified by "exposure_time"
        """

        if type(exposure_time) is str:
            if exposure_time.lower() == "max":
                self.instrument.write("DIS:PERS INFI")
            else:
                raise ValueError('invalid presistence option')

        elif type(exposure_time) in (float, int):
            if exposure_time > 0:
                self.instrument.write(f"DIS:PERS {exposure_time}")
            else:
                self.instrument.write("DIS:PERS -1")

        else:
            raise ValueError('invalid presistence option')
        return None

    def get_persistence(self):
        """
        get_persistence()

        retrives the persistence setting of the waveform buffers.

        returns: float
        """

        response = self.instrument.query("DIS:PERS?")
        return max([float(response), 0.0])

    def set_cursor_vertical_position(self, cursor, position):
        # """
        # set_cursor_vertical_position(cursor, position)

        # cursor: int, cursor number to adjust
        # \tvalid options are 1 or 2
        # position: vertical position
        # """

        self.instrument.write(f"CURS:HBA:POSITION{cursor} {position}")
        return None

    def set_horizontal_scale(self, scale):
        """
        set_horizontal_scale(scale)

        scale: int/float, time scale across one horizontal division on the
               display in seconds.

        sets the scale of horizontal divisons (for all channels) to the
        specified value in seconds.
        """

        self.instrument.write(f"HOR:SCA {scale}")
        return None

    def get_horizontal_scale(self):
        """
        get_horizontal_scale()

        retrieves the scale of horizontal divisons in seconds.

        returns: float
        """

        return float(self.instrument.query("HOR:SCA?"))


if __name__ == "__main__":
    pass
