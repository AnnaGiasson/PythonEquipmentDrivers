from pythonequipmentdrivers import Scpi_Instrument
import struct
import numpy as np
from time import sleep
from typing import Union


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
        return None

    # investigate using faster data encoding scheme
    def get_channel_data(self, *channels: int, **kwargs) -> tuple:
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
                number(s) of the waveform(s) to be transferred. valid options
                are 1-4

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
        N = self.get_record_length()  # number of samples
        x_offset = int(self.get_trigger_position()/100*N)

        # formatting info
        dtype = kwargs.get('dtype', np.float32)
        start_idx = np.clip(kwargs.get('start_percent', 0), 0, 100)/100*N
        stop_idx = np.clip(kwargs.get('stop_percent', 100), 0, 100)/100*N

        waves = []
        for channel in channels:
            # set up scope for data transfer
            self.instrument.write(f'DATA:SOU CH{channel}')  # Set data source
            self.instrument.write('DATA:WIDTH 1')  # ?? used in example
            self.instrument.write('DATA:ENC RPB')  # Set data encoding type
            self.instrument.write(f'DATA:START {int(start_idx)}')
            self.instrument.write(f'DATA:STOP {int(stop_idx)}')

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
        else:
            if kwargs.get('return_time', True):
                # generate time vector / account for trigger position
                # all waveforms assumed to have same duration (just use last)

                t = np.arange(0, dt*len(wave), dt, dtype=dtype)
                t -= (x_offset - min([start_idx, stop_idx]))*dt

                return (t, *waves)
            else:
                if len(waves) == 1:
                    return waves[0]
                return waves

    def set_channel_label(self, channel: int, label: str) -> None:
        """
        set_channel_label(channel, label)

        updates the text label on a channel specified by "channel" with the
        value given in "label".

        Args:
            channel (int): channel number to update label of.
            label (str): text label to assign to the specified
        """

        self.instrument.write(f'CH{int(channel)}:LAB "{label}"')
        return None

    def get_channel_label(self, channel: int) -> str:
        """
        get_channel_label(channel)

        retrives the label currently used by the specified channel

        Args:
            channel (int): channel number to get label of.

        Returns:
            (str): specified channel label
        """

        response = self.instrument.query(f'CH{int(channel)}:LAB?')
        return response.rstrip('\n')

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
        return None

    def get_channel_scale(self, channel: int) -> float:
        """
        get_channel_scale(channel)

        Retrives the scale for vertical divisons for the specified channel

        Args:
            channel (int): channel number to query information on

        Returns:
            (float): scale of the channel amplitude across one
                vertical division on the display.
        """

        response = self.instrument.query(f'CH{int(channel)}:SCA?')
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

        if isinstance(duration, str) and (duration.lower() == 'inf'):
            val = 'INFI'
        elif isinstance(duration, (float, int)):
            val = float(duration) if duration > 0 else -1
        else:
            raise ValueError('invalid persistence option')

        self.instrument.write(f'DIS:PERS {val}')

        return None

    def get_persistence_time(self) -> float:
        """
        get_persistence_time()

        Retrives the persistence time set for the waveform buffers.

        Returns:
            (float): persistence time
        """

        response = self.instrument.query('DIS:PERS?')
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
        return None

    def get_horizontal_scale(self) -> float:
        """
        get_horizontal_scale()

        retrieves the scale of horizontal divisons in seconds.

        Returns:
            (float): horizontal scale
        """

        response = self.instrument.query('HOR:SCA?')
        return float(response)


if __name__ == "__main__":
    pass
