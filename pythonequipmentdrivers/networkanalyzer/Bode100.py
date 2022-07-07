from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Union

import win32com.client

API_LINK = "OmicronLab.VectorNetworkAnalysis.AutomationInterface"


GainPhaseResult = Tuple[Tuple[float], Tuple[float], Tuple[float]]


class LevelUnit(Enum):
    dBm = 0
    Vpp = 1
    Vrms = 2


class Bode100():
    """
    Class for interfacing with the Bode100 network analyzer

    Manufactorers API documentation:
    documentation.omicron-lab.com/BodeAutomationInterface/3.25/index.html
    """

    def __init__(self) -> None:

        self._measurement = None

        try:
            self._automation_interface = win32com.client.Dispatch(API_LINK)
        except win32com.client.pywintypes.com_error as error:
            raise ConnectionError(f"Could not load device API: {error}")

        if not self._automation_interface.ScanForFreeDevices():
            raise IOError("No devices availble")

        try:
            self._connection = self._automation_interface.Connect()
        except win32com.client.pywintypes.com_error as error:
            self._connection = None
            raise ConnectionError("Unable to connect to an availble device",
                                  error)

        self.serial_number = self._connection.serialNumber

    def __del__(self) -> None:

        self.clear_measurement()
        self.disconnect()
        self._automation_interface.Dispose()

    def reconnect(self) -> None:

        if self._connection is not None:
            raise IOError('Device is already connected')

        self._connection = self._automation_interface.ConnectWithSerialNumber(self.serial_number)

    def disconnect(self) -> None:

        if self._connection is None:
            raise IOError('Cannot disconnect and nonexistant connection')

        self._connection.ShutDown()
        self._connection = None

    # data structures
    class _ExecutionState(Enum):
        OK = 0
        OVERLOAD = 1
        ERROR = 2
        DEVICE_LOST = 3
        CANCELLED = 4
        CALIBRATION_MANDATORY = 5

    class _ExecutionStateDescriptions(Enum):
        OK = 'Measurement successfully completed.'
        OVERLOAD = 'Overload detected. Check OverloadLevel.'
        ERROR = 'Unknown error occurred during measurement. Check the Log for further information.'
        DEVICE_LOST = 'Device connection lost during measurement.'
        CANCELLED = 'Execution stopped by user.'
        CALIBRATION_MANDATORY = 'Calibration mandatory for this measurement mode.'

    # not made as a subclass so it can be reference within GainPhaseConfig
    LevelUnit = LevelUnit

    @dataclass
    class GainPhaseConfig:
        attenuation_channel1: int = -20  # (0, -10, -20, -30, -40)
        attenuation_channel2: int = -20
        probe_channel1: float = 1.0  # probe scaling factor (i.e 1:1, 1:10)
        probe_channel2: float = 1.0
        use_50ohm_termination_channel1: bool = False
        use_50ohm_termination_channel2: bool = False
        receiver_bandwidth: int = 1000  # Hz
        dut_settling_time: float = 0.0  # time in sec (converted to ms in class for the API)
        start_frequency: float = 1000.0  # Hz
        stop_frequency: float = 1e6  # Hz
        number_of_points: int = 401
        use_log_spacing: bool = True
        level_unit: LevelUnit = LevelUnit.Vpp
        source_level: Union[float, Tuple[Tuple[float, float]]] = 0.1

    def configure_gain_phase_measurement(self,
                                         config: GainPhaseConfig) -> None:

        # check for connection and create measurement object
        if self._connection is None:
            self._measurement = None
            raise IOError("No connection to a device")

        self._measurement = self._connection.Transmission.CreateGainMeasurement()

        # configure channel 1/2
        self._measurement.ExternalProbeChannel1 = config.probe_channel1
        self._measurement.ExternalProbeChannel2 = config.probe_channel2
        self._measurement.Attenuation.Channel1 = config.attenuation_channel1
        self._measurement.Attenuation.Channel2 = config.attenuation_channel2
        #   API Enum value for 50 Ohm = 0, 1 = 1 MOhm
        self._measurement.TerminationChannel1 = 0 if config.use_50ohm_termination_channel1 else 1
        self._measurement.TerminationChannel2 = 0 if config.use_50ohm_termination_channel2 else 1

        # configure reciever
        self._measurement.ReceiverBandwidth = config.receiver_bandwidth*1e3  # convert from Hz to mHz
        self._measurement.DutSettlingTime = config.dut_settling_time*1e3  # convert from sec to ms

        # configure signal injection
        if isinstance(config.source_level, (tuple, list)):  # shaped level

            shaping_interface = self._measurement.Shaping.SourceShaping
            shaping_interface.IsEnabled = True
            shaping_interface.LevelUnit = config.level_unit.value

            shaping_interface.Clear()  # remove any existing settings
            for (freq, level) in config.source_level:
                shaping_interface.Add(freq, level)

        else:  # fixed level
            self._measurement.SetSourceLevel(config.source_level, config.level_unit.value)

        self._measurement.ConfigureSweep(config.start_frequency,
                                         config.stop_frequency,
                                         config.number_of_points,
                                         1 if config.use_log_spacing else 0  # called "SweepMode" in API
                                         )
        #   SweepMode Enum: 0=Linearspacing, 1=LogSpacing, 2=Custom points (not implemented here)

    def clear_measurement(self) -> None:
        if self._measurement is None:
            return None
        self._measurement.Dispose()
        self._measurement = None

    @property
    def measurement_duration(self) -> float:
        if self._measurement is None:
            return float('nan')
        return self._measurement.CalculateMeasurementTime()

    def execute_measurement(self) -> None:

        if self._measurement is None:
            raise ValueError('No measurement configured')

        try:
            status_code = self._measurement.ExecuteMeasurement()
        except win32com.client.pywintypes.com_error as error:
            self.stop_execution()
            raise IOError(error.excepinfo[2])

        state = self._ExecutionState(status_code)

        if state != self._ExecutionState.OK:
            raise Exception(state.name,
                            self._ExecutionStateDescriptions[state.name].value)

    def stop_execution(self) -> None:
        if self._measurement is not None:
            self._measurement.StopCurrentExecution()

    def read_gain_phase_results(self,
                                use_db: bool = True, use_deg: bool = True,
                                wrap_phase: bool = True) -> GainPhaseResult:
        # Error check
        if self._measurement is None:
            raise ValueError('No measurement configured')

        results = self._measurement.Results

        if results.Count == 0:
            raise ValueError('No measurement executed')

        # get data
        freq = results.MeasurementFrequencies
        mag = results.Magnitude(0 if use_db else 1)
        if wrap_phase:
            phase = results.Phase(1 if use_deg else 0)
        else:
            phase = results.UnwrappedPhase(1 if use_deg else 0)

        return (freq, mag, phase)
