from pythonequipmentdrivers import Scpi_Instrument
import struct
import numpy as np
from time import sleep
from pathlib import Path
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

    def select_channel(self, channel: int, state: bool) -> None:
        """
        select_channel(channel, state)

        Selects the specified channel on the front panel display. This is allow
        the specified channel to be seen on top of the others in the display.
        With a given channel selected any cursor measurements will then
        correspond to the selected channel.

        Args:
            channel (int): Channel number to select
            state (bool): Whether or not the respective channel is
                selected/visable on the screen.
        """

        cmd_str = f"SEL:CH{int(channel)} {'ON' if state else 'OFF'}"
        self.instrument.write(cmd_str)

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
        N = self.get_record_length()  # number of samples
        x_offset = int(self.get_trigger_position()/100*N)

        # formatting info
        dtype = kwargs.get('dtype', np.float32)
        start_idx = np.clip(kwargs.get('start_percent', 0), 0, 100)/100*N
        stop_idx = np.clip(kwargs.get('stop_percent', 100), 0, 100)/100*N

        waves = []
        for channel in channels:
            # set up scope for data transfer
            self.instrument.write(f'DATA:SOU CH{int(channel)}')  # Set source
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

    def trigger_run_stop(self):
        self.instrument.write("FPANEL:PRESS RUnstop")
        return None

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
        self.instrument.write("FPANEL:PRESS SING")

    def set_trigger_position(self, percent):
        self.instrument.write(f"HOR:POS {percent}")
        return None

    def get_trigger_position(self):  # returns percent of record len
        return float(self.instrument.query("HOR:POS?"))

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
            buffering_delay (float): delay before reading back image data in
                seconds. Depending on the oscilloscope settings, conversion of
                the data to an image may take longer than the timeout of the
                resource connection; this delay gives the scope more time to
                buffer the image. Defaults to 0.
        """

        # add file extension
        if isinstance(image_title, Path):
            file_path = image_title.parent.joinpath(image_title.name + '.png')
        elif isinstance(image_title, str):
            file_path = f"{image_title}.png"
        else:
            raise ValueError('image_title must be a str or path-like object')

        # initiate transfer
        self.instrument.write("SAVE:IMAG:FILEF PNG")  # set filetype
        self.instrument.write("HARDCOPY START")  # start converting to image
        self.instrument.write('*OPC?')  # done yet?
        sleep(kwargs.get('buffering_delay', 0))

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

    def set_cursor_vertical_level(self, cursor: int, level: float) -> None:
        """
        set_cursor_vertical_level(cursor, level)

        Set the veritcal position of the oscilloscope trigger on the front
        panel display

        Args:
            cursor (int): Cursor number to adjust. Valid options are 1 or 2
            level (float): Vertical position in units of the selected waveform
        """

        self.instrument.write(f"CURS:HBA:POSITION{int(cursor)} {float(level)}")

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
