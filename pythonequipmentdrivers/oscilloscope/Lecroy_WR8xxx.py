from pythonequipmentdrivers import Scpi_Instrument as _Scpi_Instrument


class Lecroy_WR8xxx(_Scpi_Instrument):
    """
    Lecroy_WR8xxx(address)

    address : str, address of the connected oscilloscope

    object for accessing basic functionallity of the Lecroy_WR8xxx
    Family of Oscilloscopes

    Addtional information on the remote control capabilities of the scope can
    be accessed at:
    http://cdn.teledynelecroy.com/files/manuals/maui-remote-control-and-automation-manual.pdf#page=223&zoom=100,72,65
    """

    valid_trigger_states = ['AUTO', 'NORM', 'SINGLE', 'STOP']
    valid_trigger_slopes = {'POS': 'POS', 'RISE': 'POS',
                            'NEG': 'NEG', 'FALL': 'NEG'}

    def __init__(self, address):
        super().__init__(address)
        self.instrument.clear()
        return

    def set_channel_scale(self, channel, scale):
        """
        set_channel_scale(channel, scale)

        channel: int, channel number of channel
                    valid options are 1-8

        scale: int/float, scale of the channel amplitude across one
        vertical division on the display.

        sets the scale of vertical divisons for the specified channel
        """

        self.instrument.write(f"C{channel}:VDIV {scale}\n")
        return

    def get_channel_scale(self, channel):
        """
        get_channel_scale(channel)

        channel: int, channel number of channel
                    valid options are 1-8

        retrives the scale for vertical divisons for the specified channel

        returns: float
        """
        read_cmd = f"C{channel}:VDIV"
        response = self.instrument.query(f"{read_cmd}?")
        val = response.lstrip(read_cmd).split()[0]
        return float(val)

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


if __name__ == '__main__':
    pass
