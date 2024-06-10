from collections import deque
from enum import Enum
from time import sleep
from typing import Iterable, List, Tuple, Union

from ...core import VisaResource


class ChannelModes(Enum):
    """
    Valid measurement modes for a DAQ channel
    """

    VOLT = "VOLT"
    CURR = "CURR"
    FREQ = "FREQ"
    OHMS = "RES"
    RES = "RES"
    DIODE = "DIOD"
    CONT = "CONT"
    PERIOD = "PER"


class NPLC_Options(Enum):
    """
    Number of Power Line Cycle to use per measurement
    """

    N0p02 = "0.02"
    N0p2 = "0.2"
    N1 = "1"
    N2 = "2"
    N10 = "10"
    N20 = "20"
    N100 = "100"
    N200 = "200"
    MIN = "MIN"
    MAX = "MAX"


class TriggerOptions(Enum):
    BUS = "BUS"
    IMMEDIATE = "IMMediate"
    IMM = "IMMediate"
    EXTERNAL = "EXTernal"
    EXT = "EXT"
    ALARM1 = "ALARm1"
    ALARM2 = "ALARm2"
    ALARM3 = "ALARm3"
    ALARM4 = "ALARm4"
    TIMER = "TIMer"


class Agilent_34972A(VisaResource):
    """
    Agilent_34972A()

    address: str, address of the connected data aquisition dac
    ch_change_time, optional: mux switching time
    object for accessing basic functionallity of the AG_34972A data aquisition
    dac.

    Additional Information:
    functions based on 34972-90001.pdf at
    https://literature.cdn.keysight.com/litweb/pdf/34972-90001.pdf
    Ted Kus, tkus@vicr.com

    recommend channels be passed in a list
    """

    channel_modes = ChannelModes
    nplc_options = NPLC_Options
    trigger_options = TriggerOptions

    valid_volt_ranges = {"AUTO", "MIN", "MAX", "DEF", "0.1", "1", "10", "100", "300"}

    valid_curr_ranges = {"AUTO", "MIN", "MAX", "DEF", "0.01", "0.1", "1"}

    valid_res_ranges = {
        "AUTO",
        "MIN",
        "MAX",
        "DEF",
        "100",
        "1E3",
        "10E3",
        "100E3",
        "1E6",
        "10E6",
        "100E6",
    }

    valid_resolutions = {
        "MIN": 0.0001,  # lookup based on nplc
        "MAX": 0.00000022,  # this * range = resolution
        "0.02": 0.0001,
        "0.2": 0.00001,
        "1": 0.000003,
        "2": 0.0000022,
        "10": 0.000001,
        "20": 0.0000008,
        "100": 0.0000003,
        "200": 0.00000022,
    }

    def __init__(
        self,
        address: str,
        ch_change_time: float = 0.05,
        line_frequency: float = 60.0,
        reset: bool = False,
    ) -> None:

        super().__init__(address)
        if reset:
            self.clear_status()

        self.ch_change_time = ch_change_time
        # measure_time = n * nplc * (1 / 50) + 0.02  # 50Hz assumption + buffer

        self.nplc_default = 1  # power line cycles to average
        self.line_frequency = line_frequency  # Hz

        self.scan_list = self.get_scan_list()
        self.set_measure_time()
        self.trigger_mode = self.get_trigger_source()

    def _split_response(self, response: str) -> List[str]:
        """_split_response(response)

        Args:
            response (str): string of data to parse

        Returns:
            List[str]: a list of the individual values in each the response
                split by delimiters with header/footer characters removed.
        """

        if "@" in response:
            start = response.find("@")  # note this returns -1 if not found
            stop = -1
        else:
            start = -1
            stop = None
        # that works out OK because data needs to be parsed from the first
        # character anyway, so this is not an error, but I don't like
        # that it isn't explicitly trying to find the correct character

        return response[(start + 1) : stop].split(",")

    def set_mode(self, chan: int, mode: ChannelModes) -> None:
        """
        set_mode(mode)

        Configures the dac to perform the specified measurement. RANGe will be
        AUTO, NPLC/RESOLUTION will be DEFAULT (usually 5.5d)

        chan (int): channels to apply to
        mode (ChannelModes): type of measurement to be done (Enum)
            see self.valid_modes for options
        """

        chan_str = self._format_channel_str(chan)
        self.write_resource(f"CONF:{mode.value} (@{chan_str})")

    def get_mode(self, chan: Union[int, Iterable[int]]) -> ChannelModes:
        """
        get_mode(chan)

        retrives type of measurement the dac is current configured to
        perform.

        returns: ChannelModes Enum for the current channel config
        """

        response = self.query_resource(f"FUNC? (@{self._format_channel_str(chan)})")

        return self.channel_modes[response.replace('"', "")]

    def get_error_queue(self, **kwargs) -> List[Tuple[int, str]]:
        """
        get_error_queue()

        Queries the error queue, if the queue is empty this returns an
        empty list.

        Returns:
            List[Tuple[int, str]]: Reads back the Error queue, returning each
                error in order of occurance. Each error is returned in a tuple
                of "error code" "error name"
        """

        error_queue = []
        error_code = None  # None so loop executes at least once

        while error_code != 0:  # 0 means no error
            response = self.query_resource("SYSTem:ERRor?", **kwargs)

            error_info = self._split_response(response)

            error_code = int(error_info[0])
            error_message = error_info[1].replace("'", "").replace('"', "")

            if error_code != 0:
                error_queue.append((error_code, error_message))

        return error_queue

    def set_trigger_source(
        self, trigger: TriggerOptions = TriggerOptions.IMMEDIATE
    ) -> None:
        """
        set_trigger(trigger)

        trigger: TriggerOptions Enum, type of trigger to be done
            valid modes are: 'BUS', 'IMMEDIATE', 'EXTERNAL'
            which correspond to 'BUS', 'IMMEDIATE', 'EXTERNAL'
            respectively (not case sensitive). See self.trigger_options.

        Configures the multimeter to trigger as specified
        """

        self.write_resource(f"TRIG:SOUR {trigger.value}")
        self.trigger_mode = trigger

    def get_trigger_source(self) -> TriggerOptions:
        response = self.query_resource("TRIG:SOUR?")
        self.trigger_mode = self.trigger_options[response]
        return self.trigger_mode

    def set_trigger_count(self, count: int, **kwargs) -> None:
        """
        set_trigger_count(count)

        Args:
            count (int): how many readings to take when triggered
        """

        self.write_resource(f"TRIG:COUN {count}", **kwargs)

    def get_trigger_count(self) -> int:
        response = self.query_resource("TRIG:COUN?")
        return round(float(response))

    def set_trigger_timer(self, delaytime: Union[int, float], **kwargs):
        """set_trigger_count(delaytime)

        Args:
            delaytime (Union[int, float]): delay between scanlist readings when
                triggered note, entire scanlist is measured each time then the
                delay runs, then the scanlist again...
        """

        self.write_resource(f"TRIG:TIM {delaytime}", **kwargs)

    def get_trigger_timer(self):
        response = self.query_resource("TRIG:TIM?")
        return float(response)

    def trigger(self, wait: bool = True, **kwargs) -> None:
        """
        trigger(wait=True)

        If the unit is setup to BUS trigger, sends trigger

        Args:
            wait (bool, optional): Does not return to caller until scantime
                                   is complete.  Prevents Trigger Ignored
                                   errors (-211). Defaults to True.
        """
        if self.trigger_mode == TriggerOptions.BUS:
            self.write_resource("*TRG", **kwargs)
        else:
            raise ValueError(
                f"Trigger not configured, set as: {self.trigger_mode}" " should be BUS"
            )

        if wait:
            # it should also wait nplc time per channel
            # need to make a function to track nplc time
            # if nplc is longer than 1, then this will fail, if shorter
            # then this will take way too long
            sleep(self.measure_time)  # should work most of the time.

    def get_scan_list(self, **kwargs):
        """
        get_scan_list()

        determine which channels are currently in the scan list,
        you can send the ROUTe:SCAN? query command.
        instrument data comes back raw such as: '#210(@101,102)\n'

        returns:
            list (int): channel numbers in scanlist
        """
        response = self.query_resource("ROUT:SCAN?", **kwargs)
        self.scan_list = list(map(int, self._split_response(response)))

        return self.scan_list

    def _format_channel_str(self, chan: Union[int, Iterable[int]]) -> str:

        if isinstance(chan, int):
            return str(chan)

        return ",".join(map(str, chan))

    def set_scan_list(self, chan: Iterable[int], relay_time: bool = False) -> None:
        """
        set_scan_list(chan)

        sets the list of channels to scan, the meter will scan them once
        immediately!

        Aguments:
            chan (Iterable[int]): list of channels to include in new
                scan list.  Note that scan list is overwritten every time
            relay_time (bool): ch_change_time delay before return.
        """

        chan_str = self._format_channel_str(chan)
        self.scan_list = list(chan)

        self.write_resource(f"ROUT:SCAN (@{chan_str})")

        if relay_time:
            self.relay_delay(n=len(self.scan_list))

    def measure(self, chan: Iterable[int], **kwargs) -> List[float]:
        """
        measure(chan)
        performs an immediate sweep of the given scan_list and
        returns the data to the output buffer directly

        Aguments:
            chan (int)[list]: list of channels to include in new
            scan list.  Note that scan list is overwritten every time

        Returns:
            List[float]: channel measurement data
        """

        chan_str = self._format_channel_str(chan)
        response = self.query_resource(f"MEASure? (@{chan_str})")

        try:
            data = list(map(float, self._split_response(response)))

        except ValueError as err:  # usually when that channel can't do that!
            raise ValueError(
                err,
                f"channel {chan_str} unable! Return 0.0"
                f"{self.query_resource('SYSTem:ERRor?')}",
                *kwargs.items(),
            )

        return data

    def read(self, chan=None) -> List[float]:
        """
        measure(chan)

        performs an immediate sweep of the scan_list and
        returns the data to the output buffer directly

        Aguments:
            chan (int)[list]: optional list of channels to include in new scan
                list.  Note that scan list is overwritten every time. If not
                passed in, uses existing list (recommended)

        Returns:
             List[float]: channel measurements
        """

        if chan is not None:
            response = self.query_resource(f"READ? (@{self._format_channel_str(chan)})")
        else:
            response = self.query_resource("READ?")

        return list(map(float, self._split_response(response)))

    def init(self, **kwargs) -> None:
        """
        init()

        Initialize the meter, used with BUS trigger typically
        Use fetch_data to query the data.
        """
        self.write_resource("INITiate", **kwargs)

    def fetch_data(self, **kwargs) -> float:
        """
        fetch_data

        Queries measurement data from DAQ

        Returns:
            List[float]: data in meter memory resulting from all scans
        """

        response = self.query_resource("FETC?", **kwargs)
        data = self._split_response(response)

        return list(map(float, data))

    def config_channel(
        self,
        chan: int,
        mode=ChannelModes.VOLT,
        is_dc: bool = True,
        signal_range: str = "auto",
        resolution=None,
        nplc: NPLC_Options = NPLC_Options.N1,
    ) -> None:
        """
        config_channel(chan, mode=ChannelModes.VOLT, is_dc=True,
                       signal_range='auto', resolution=None,
                       nplc=NPLC_Options.N1)

        Configures the measurement settings for the specified channel.

        Args:
            chan (int): channel number to apply configuration to
            mode (ChannelModes, optional): channel measurement mode.
                Defaults to ChannelModes.VOLT.
            is_dc (bool, optional): Whether the measurement is to be configured
                as a DC measurement (True) or an AC measurement (False).
                Defaults to True.
            signal_range (str, optional): measurement range. Defaults to 'auto'
            resolution (str, optional): 4.5, 5.5 or 6.5, if None uses nplc
                nplc is recommended because script timing is more
                deterministic. Defaults to None.
            nplc (NPLC_Options, optional): power line cycles to average.
                Defaults to NPLC_Options.N1 (1 cycle).
        """

        # Set channel measurement range. if range is not provided, cannot use
        # nplc in CONF command
        signal_range = signal_range.upper()
        auto_range = signal_range == "AUTO"

        if (mode == self.channel_modes.CURR) and (
            signal_range not in self.valid_curr_ranges
        ):
            raise ValueError("Invalid Range option")
        elif (mode == self.channel_modes.RES) and (
            signal_range not in self.valid_res_ranges
        ):
            raise ValueError("Invalid Range option")
        elif signal_range not in self.valid_volt_ranges:
            raise ValueError("Invalid Range option")

        # set up number of power line cycles per measurement

        use_freq = mode == self.channel_modes.FREQ
        nplc_str = nplc.value if not use_freq else ""

        if not use_freq:
            acdc = ":DC" if is_dc else ":AC"
        else:
            acdc = ""

        # build command strings
        cmd_queue = deque([])  # command queue
        if resolution and not auto_range:
            cmd_queue.append(
                f"CONF:{mode.value}{acdc} {signal_range},{resolution}(@{chan})"
            )
        else:
            cmd_queue.append(
                "CONF:{}{} {}(@{})".format(
                    mode.value, acdc, f"{signal_range}," if not auto_range else "", chan
                )
            )

            if nplc_str:
                cmd_queue.append(
                    "SENS:{}{}:{} {},(@{})".format(
                        mode.value,
                        acdc,
                        "RES" if resolution else "NPLC",
                        resolution if resolution else nplc_str,
                        chan,
                    )
                )

        # write data to device
        while cmd_queue:
            self.write_resource(cmd_queue.popleft())

    def config_channels(
        self,
        channels: Iterable[int],
        mode: ChannelModes = ChannelModes.VOLT,
        is_dc: bool = True,
        signal_range="auto",
        resolution=None,
        nplc: NPLC_Options = NPLC_Options.N1,
    ) -> None:
        """
        config_channels(channels: Iterable[int], mode=ChannelModes.VOLT,
                        is_dc: bool = True, signal_range='auto',
                        resolution=None, nplc=NPLC_Options.N1)

        Configures multiple channels with the same common settings

        Args:
            channels (Iterable[int]): list of channel numbers to apply
                common settings.
            mode (ChannelModes, optional): channel measurement mode.
                Defaults to ChannelModes.VOLT.
            is_dc (bool, optional): Whether the measurement is to be configured
                as a DC measurement (True) or an AC measurement (False).
                Defaults to True.
            signal_range (str, optional): measurement range. Defaults to 'auto'
            resolution (str, optional): 4.5, 5.5 or 6.5, if None uses nplc
                nplc is recommended because script timing is more
                deterministic. Defaults to None.
            nplc (NPLC_Options, optional): power line cycles to average.
                Defaults to NPLC_Options.N1 (1 cycle).
        """

        for chan in channels:
            self.config_channel(
                chan=chan,
                mode=mode,
                is_dc=is_dc,
                signal_range=signal_range,
                resolution=resolution,
                nplc=nplc,
            )

    def close_chan(self, chan: int) -> None:
        """
        close_chan(chan)

        Close relay on channel #

        Args:
            chan (int): Channel to close
        """

        self.write_resource(f"ROUT:CLOS (@{chan})")

    def open_chan(self, chan: int, **kwargs) -> None:
        """
        Open relay on channel #

        Args:
            chan (int): Channel to Open
        """
        self.write_resource(f"ROUT:OPEN (@{chan})", **kwargs)

    def relay_delay(self, n: int = 1, ch_change_time=0.05) -> None:
        """relay_delay(n)
        relays need time to switch, this provides that time.

        Args:
            n (int, optional): number of relay delay periods. Defaults to 1.
            ch_change_time (float, optional): relay switching time, defaults to
                                             0.050 seconds
        """
        if self.ch_change_time != ch_change_time:
            self.ch_change_time = ch_change_time
        sleep(n * self.ch_change_time)

    def monitor(self, chan: int = None) -> None:
        """
        monitor(chan)
        sets the mux to monitor the chan given and reads in realtime

        Aguments:
            chan (int):  channel to monitor in realtime.
        """

        self.write_resource(f"ROUT:MON (@{chan})")

    def mon_data(self, chan: int = None, **kwargs) -> List[float]:
        """
        mon_data(chan)
        sets the mux to monitor the optional chan given and reads in realtime
        if chan is not provided it only gets the data (faster)

        Arguments:
            chan (int):  optional channel to monitor in realtime

        Returns:
            float: chan data
        """
        if chan is not None:
            self.write_resource(f"ROUT:MON (@{chan})", **kwargs)
            self.relay_delay()

        try:
            response = self.query_resource("ROUT:MON:DATA?", **kwargs)

        except IOError as err:  # usually when channel not configured
            raise IOError(
                err,
                f"channel {chan} not configured",
                f"{self.query_resource('SYSTem:ERRor?')}",
                *kwargs.items(),
            )

        return list(map(float, self._split_response(response)))

    def abort(self, **kwargs) -> None:
        """
        abort()

        Send VISA ABORt, stop the scan!!
        Returns:
            None
        """

        self.write_resource("ABORt", **kwargs)

    def set_source(self, chan, voltage: float = None, **kwargs):
        """set_source(chan, voltage)

        Args:
            chan (int, list): Channels to set voltage output on
            voltage (float, optional): Voltage to command from DAC.
                                       Defaults to None.

        Returns:
            [list of float or float]: Voltage now output
        """
        chan_str = self._format_channel_str(chan)
        if voltage is None:
            return self.get_source(chan, **kwargs)
        else:
            self.write_resource(f"SOUR:VOLT {voltage},(@{chan_str})", **kwargs)
            return voltage

    def get_source(self, chan, **kwargs) -> List[float]:
        """get_source(chan)

        Args:
            chan (int, list): Channels to set voltage output on

        Returns:
            [list of float or float]: Voltage now output
        """

        chan_str = self._format_channel_str(chan)
        response = self.query_resource(f"SOUR:VOLT? (@{chan_str})", **kwargs)

        return list(map(float, self._split_response(response)))

    def set_measure_time(self, measure_time: float = None):
        if measure_time is None:
            self.measure_time = (
                len(self.scan_list) * self.nplc_default * (1 / self.line_frequency)
                + self.ch_change_time
            )
        else:
            self.measure_time = measure_time

    def set_local(self, **kwargs) -> None:
        self.write_resource("SYSTem:LOCal", **kwargs)


# Agilent 34970A/72A Command Reference
# Keysight 34970A/34972A
# Commands by Subsystem
# ABORt
# FETCh?
# INITiate
# INPut:IMPedance:AUTO
# R?
# READ?
# UNIT:TEMPerature
# CALCulate_Subsystem
# CALCulate:AVERage:AVERage?
# CALCulate:AVERage:CLEar
# CALCulate:AVERage:COUNt?
# CALCulate:AVERage:MAXimum?
# CALCulate:AVERage:MAXimum:TIME?
# CALCulate:AVERage:MINimum?
# CALCulate:AVERage:MINimum:TIME?
# CALCulate:AVERage:PTPeak?
# CALCulate:COMPare:DATA
# CALCulate:COMPare:MASK
# CALCulate:COMPare:STATe
# CALCulate:COMPare:TYPE
# CALCulate:LIMit:LOWer
# CALCulate:LIMit:LOWer:STATe
# CALCulate:LIMit:UPPer
# CALCulate:LIMit:UPPer:STATe
# CALCulate:SCALe:GAIN
# CALCulate:SCALe:OFFSet
# CALCulate:SCALe:OFFSet:NULL
# CALCulate:SCALe:STATe
# CALCulate:SCALe:UNIT
# CALibration_Subsystem
# CALibration?
# CALibration:COUNt?
# CALibration:SECure:CODE
# CALibration:SECure:STATe
# CALibration:STRing
# CALibration:VALue
# CONFigure_Subsystem
# CONFigure?
# CONFigure:CURRent:AC
# CONFigure:CURRent:DC
# CONFigure:DIGital:BYTE
# CONFigure:FREQuency
# CONFigure:FRESistance
# CONFigure:PERiod
# CONFigure:RESistance
# CONFigure:TEMPerature
# CONFigure:TOTalize
# CONFigure:VOLTage:AC
# CONFigure:VOLTage:DC
# DATA_Subsystem
# DATA:LAST?
# DATA:POINts?
# DATA:POINts:EVENt:THReshold
# DATA:REMove?
# DIAGnostic_Subsystem
# DIAGnostic:DMM:CYCLes?
# DIAGnostic:DMM:CYCLes:CLEar
# DIAGnostic:PEEK:SLOT:DATA?
# DIAGnostic:POKE:SLOT:DATA
# DIAGnostic:RELay:CYCLes?
# DIAGnostic:RELay:CYCLes:CLEar
# DISPlay_Subsystem
# DISPlay
# DISPlay:TEXT
# DISPlay:TEXT:CLEar
# FORMat_Subsystem
# FORMat:READing:ALARm
# FORMat:READing:CHANnel
# FORMat:READing:TIME
# FORMat:READing:TIME:TYPE
# FORMat:READing:UNIT
# IEEE-488_Commands
# *CLS
# *ESE
# *ESR?
# *IDN?
# *OPC
# *OPC?
# *PSC
# *RCL
# *RST
# *SAV
# *SRE
# *STB?
# *TRG
# *TST?
# *WAI
# INSTrument_Subsystem
# INSTrument:DMM
# INSTrument:DMM:INSTalled?
# LXI_Subsystem
# LXI:IDENtify[:STATe]
# LXI:RESet
# LXI:RESTart
# MEASure_Subsystem
# MEASure:CURRent:AC?
# MEASure:CURRent:DC?
# MEASure:DIGital:BYTE?
# MEASure:FREQuency?
# MEASure:FRESistance?
# MEASure:PERiod?
# MEASure:RESistance?
# MEASure:TEMPerature?
# MEASure:TOTalize?
# MEASure:VOLTage:AC?
# MEASure:VOLTage:DC?
# MEMory_Subsystem
# MEMory:NSTates?
# MEMory:STATe:DELete
# MEMory:STATe:NAME
# MEMory:STATe:RECall:AUTO
# MEMory:STATe:VALid?
# MMEMory_Subsytem
# MMEMory:EXPort?
# MMEMory:FORMat:READing:CSEParator
# MMEMory:FORMat:READing:RLIMit
# MMEMory:IMPort:CATalog?
# MMEMory:IMPort:CONFig?
# MMEMory:LOG[:ENABle]
# OUTPut_Subsystem
# OUTPut:ALARm:CLEar:ALL
# OUTPut:ALARm:MODE
# OUTPut:ALARm:SLOPe
# OUTPut:ALARm{1|2|3|4}:CLEar
# OUTPut:ALARm{1|2|3|4}:SOURce
# ROUTe_Subsystem
# ROUTe:CHANnel:ADVance:SOURce
# ROUTe:CHANnel:DELay
# ROUTe:CHANnel:DELay:AUTO
# ROUTe:CHANnel:FWIRe
# ROUTe:CLOSe
# ROUTe:CLOSe:EXCLusive
# ROUTe:DONE?
# ROUTe:MONItor
# ROUTe:MONItor:DATA?
# ROUTe:MONItor:STATe
# ROUTe:OPEN
# ROUTe:SCAN
# ROUTe:SCAN:SIZE?
# SENSe_Subsystem
# [SENSe:]CURRent:AC:BANDwidth
# [SENSe:]CURRent:AC:RANGe
# [SENSe:]CURRent:AC:RANGe:AUTO
# [SENSe:]CURRent:AC:RESolution
# [SENSe:]CURRent:DC:APERture
# [SENSe:]CURRent:DC:NPLC
# [SENSe:]CURRent:DC:RANGe
# [SENSe:]CURRent:DC:RANGe:AUTO
# [SENSe:]CURRent:DC:RESolution
# [SENSe:]DIGital:DATA:{BYTE|WORD}?
# [SENSe:]FREQuency:APERture
# [SENSe:]FREQuency:RANGe:LOWer
# [SENSe:]FREQuency:VOLTage:RANGe
# [SENSe:]FREQuency:VOLTage:RANGe:AUTO
# [SENSe:]FRESistance:APERture
# [SENSe:]FRESistance:NPLC
# [SENSe:]FRESistance:OCOMpensated
# [SENSe:]FRESistance:RANGe
# [SENSe:]FRESistance:RANGe:AUTO
# [SENSe:]FRESistance:RESolution
# [SENSe:]FUNCtion
# [SENSe:]PERiod:APERture
# [SENSe:]PERiod:VOLTage:RANGe
# [SENSe:]PERiod:VOLTage:RANGe:AUTO
# [SENSe:]RESistance:APERture
# [SENSe:]RESistance:NPLC
# [SENSe:]RESistance:OCOMpensated
# [SENSe:]RESistance:RANGe
# [SENSe:]RESistance:RANGe:AUTO
# [SENSe:]RESistance:RESolution
# [SENSe:]TEMPerature:APERture
# [SENSe:]TEMPerature:NPLC
# [SENSe:]TEMPerature:RJUNction?
# [SENSe:]TEMPerature:TRANsducer:FRTD:OCOMpensated
# [SENSe:]TEMPerature:TRANsducer:FRTD:RESistance[:REFerence]
# [SENSe:]TEMPerature:TRANsducer:FRTD:TYPE
# [SENSe:]TEMPerature:TRANsducer:RTD:OCOMpensated
# [SENSe:]TEMPerature:TRANsducer:RTD:RESistance[:REFerence]
# [SENSe:]TEMPerature:TRANsducer:RTD:TYPE
# [SENSe:]TEMPerature:TRANsducer:TCouple:CHECk
# [SENSe:]TEMPerature:TRANsducer:TCouple:RJUNction
# [SENSe:]TEMPerature:TRANsducer:TCouple:RJUNction:TYPE
# [SENSe:]TEMPerature:TRANsducer:TCouple:TYPE
# [SENSe:]TEMPerature:TRANsducer:THERmistor:TYPE
# [SENSe:]TEMPerature:TRANsducer:TYPE
# [SENSe:]TOTalize:CLEar:IMMediate
# [SENSe:]TOTalize:DATA?
# [SENSe:]TOTalize:SLOPe
# [SENSe:]TOTalize:STARt[:IMMediate]
# [SENSe:]TOTalize:STOP[:IMMediate]
# [SENSe:]TOTalize:TYPE
# [SENSe:]VOLTage:AC:BANDwidth
# [SENSe:]VOLTage:AC:RANGe
# [SENSe:]VOLTage:AC:RANGe:AUTO
# [SENSe:]VOLTage:DC:APERture
# [SENSe:]VOLTage:DC:NPLC
# [SENSe:]VOLTage:DC:RANGe
# [SENSe:]VOLTage:DC:RANGe:AUTO
# [SENSe:]VOLTage:DC:RESolution
# [SENSe:]ZERO:AUTO
# SOURce_Subsystem
# SOURce:DIGital:DATA[:{BYTE|WORD}]
# SOURce:DIGital:STATe?
# SOURce:VOLTage
# STATus_Subsystem
# STATus:ALARm:CONDition?
# STATus:ALARm:ENABle
# STATus:ALARm[:EVENt]?
# STATus:OPERation:CONDition?
# STATus:OPERation:ENABle
# STATus:OPERation[:EVENt]?
# STATus:PRESet
# STATus:QUEStionable:CONDition?
# STATus:QUEStionable:ENABle
# STATus:QUEStionable[:EVENt]?
# STATus Subsystem Introduction
# SYSTem_Subsystem
# LAN_Config
# SYSTem:COMMunicate:LAN:CONTrol?
# SYSTem:COMMunicate:LAN:DHCP
# SYSTem:COMMunicate:LAN:DNS
# SYSTem:COMMunicate:LAN:DOMain
# SYSTem:COMMunicate:LAN:GATEway
# SYSTem:COMMunicate:LAN:HOSTname
# SYSTem:COMMunicate:LAN:IPADdress
# SYSTem:COMMunicate:LAN:MAC?
# SYSTem:COMMunicate:LAN:SMASk
# SYSTem:COMMunicate:LAN:TELNet:PROMpt
# SYSTem:COMMunicate:LAN:TELNet:WMESsage
# SYSTem:COMMunicate:LAN:UPDate
# SYSTem:ALARm?
# SYSTem:CPON
# SYSTem:CTYPe?
# SYSTem:DATE
# SYSTem:ERRor?
# SYSTem:INTerface
# SYSTem:LANGuage
# SYSTem:LFRequency?
# SYSTem:LOCal
# SYSTem:LOCK:NAME?
# SYSTem:LOCK:OWNer?
# SYSTem:LOCK:RELease
# SYSTem:LOCK:REQuest?
# SYSTem:PRESet
# SYSTem:RWLock
# SYSTem:SECurity[:IMMediate]
# SYSTem:TIME
# SYSTem:TIME:SCAN?
# SYSTem:VERSion?
# TRIGger_Subsystem
# TRIGger:COUNt
# TRIGger:SOURce
# TRIGger:TIMer
