import win32com.client as _win32client
import numpy as _np
import re as _re


class Bode100():
    """
    Class for interfacing with the Bode100 network analyzer

    address: (str) can be used to connect to a specific Bode100 network
             analyzer if multiple device are connected to the same computer. If
             left as None this will scan for the device address and
             automatically connect to the first compatible device found.

    Manufactorers API documentation:
    documentation.omicron-lab.com/BodeAutomationInterface/3.23/index.html
    """

    # return codes are ints, the indecies of this list represent the respective
    # descriptions of each state
    execution_state_names = ['Ok', 'Overload', 'Error', 'DeviceLost',
                             'Cancelled', 'CalibrationMandatory']
    execution_state_desc = ['Measurement successfully completed.',
                            'Overload detected. Check OverloadLevel.',
                            'Unknown error occurred during measurement.',
                            'Device connection lost during measurement.',
                            'Execution stopped by user.',
                            'Calibration mandatory for this measurement mode.',
                            ]

    def __init__(self, address=None):

        api_link = "OmicronLab.VectorNetworkAnalysis.AutomationInterface"

        try:
            self.instrument = _win32client.Dispatch(api_link)
        except _win32client.pywintypes.com_error as err:
            raise ConnectionError(f"Could not load device API: {err}")

        if address is None:
            # get connected devices, filter out incompatible devices
            devices = self.instrument.ScanForFreeDevices()
            pattern = _re.compile(r'^[B,b]ode100')
            devices = list(filter(lambda s: _re.match(pattern, s) is not None,
                                  devices))
            if len(devices) == 0:
                raise ConnectionError("No free devices")

            # automatically connects to the first free compatible device
            self.idn = devices[0]
        else:
            self.idn = address

        # connect & disconnect to assure the device is availible
        self.connection = self.instrument.ConnectWithSerialNumber(self.idn)
        self.connection.ShutDown()

        return

    def __repr__(self):
        return f"{self.idn}"

    def __str__(self):
        return f"{self.idn}"

    def __del__(self):
        try:
            self.connection.ShutDown()

        except AttributeError:
            # if instrument is inaccessible __init__ will raise a Visa Error
            # and instrument wont be initialized thus it can't be closed
            pass
        return None

    def run_frequency_sweep(self, f_start, f_end, n_points, return_db=True,
                            return_rad=False, logarithmic_sweep=True,
                            chan1_atten=-20, chan2_atten=-20,
                            source_level=-30, source_level_unit=0,
                            receiver_bw=1e3, wrap_phase=True):
        """
        run_frequency_sweep(f_start, f_end, n_points, return_db=True,
                            return_rad=False, logarithmic_sweep=True)

        f_start: (float) The starting frequency of the frequency sweep in Hz
        f_end: (float) The final frequency of the frequency sweep in Hz
        n_points: (int) The number of points contained in frequency sweep
                  between the frequencies f_start and f_end.

        return_db: (bool) Optional; sets the format of the returned magnitude
                   response. If true decibels are used otherwise output/input
                   ratios are used. Default is True.
        return_rad: (bool) Optional; sets the format of the returned phase
                    response. If true radians are used otherwise degrees are
                    used. Default is False.
        logarithmic_sweep: (bool) Optional; Determines the spacing between the
                           the frequency points used in the sweep. If true
                           'n_points' are spaced logarithmically from 'f_start'
                           to 'f_end', otherwise they are spaced linearly.
        chan1_atten/chan2_atten: (float) Optional; Attenuation of the channel
                                 1/2 to be used in the sweep in dB. Defaults to
                                 -20dB.
        source_level: (float) Optional; fixed amplitude of the injected signal.
        source_level_unit: (int) units of the source level to use for signal
                           injection. 0 = dBm, 1 = Vpp, 2 = Vrms
        receiver_bw: (float) Optional; Bandwidth of the reciever used
                     in the frequecy sweep in Hz. Defaults to 1 kHz.
        wrap_phase: (bool) Optional; Determines whether or not returned phase
                    data is contained with +/- pi or 180deg, default is True.

        returns:
        freq: (float array) The disturbence frequencies used in the sweep in Hz
        mag: (float array) the magnitude response over frequency, units depend
             on the setting of 'return_dB', either dB or ratio.
        phase: (float array) the phase response over frequency, units depend on
               the setting of 'return_rad', either radians or degrees.

        Configures and runs a measurement gain and phase of the connected
        network over frequency. Returns the data (frequency, gain, phase) as
        three float arrays.

        Ex.
            bode = Bode100()
            freq, mag, phase = bode.run_frequency_sweep(1e3, 1e6, 200)
        """

        # connect to instrument
        self.connection = self.instrument.ConnectWithSerialNumber(self.idn)

        # configure measurement

        measurement = self.connection.Transmission.CreateGainMeasurement()

        # custom bandwidths need to be in milliHertz according to API docs
        measurement.ReceiverBandwidth = int(receiver_bw*1000)
        measurement.Attenuation.Channel1 = chan1_atten
        measurement.Attenuation.Channel2 = chan2_atten

        # reference for unit 'codes'
        # https://documentation.omicron-lab.com/BodeAutomationInterface/3.23/api/OmicronLab.VectorNetworkAnalysis.AutomationInterface.Enumerations.LevelUnit.html?q=LevelUnit
        measurement.SetSourceLevel(float(source_level), int(source_level_unit))

        measurement.ConfigureSweep(f_start, f_end, n_points,
                                   int(logarithmic_sweep))

        # execute measurement
        try:
            state = measurement.ExecuteMeasurement()
        except _win32client.pywintypes.com_error as error:
            self.connection.ShutDown()
            raise Exception(error.excepinfo[2])

        if state == 0:

            freq = _np.array(measurement.Results.MeasurementFrequencies)
            results = measurement.Results
            complex_vals = results.ComplexValues()
            self.connection.ShutDown()

            # format data
            if return_db:
                mag = _np.array([datum.MagnitudeDB for datum in complex_vals])
            else:
                mag = _np.array([datum.Magnitude for datum in complex_vals])

            if wrap_phase:
                phase = _np.array([datum.Phase for datum in complex_vals])
            else:
                phase = _np.array(results.UnwrappedPhase(0))

            if not return_rad:
                phase *= 180/_np.pi

            return freq, mag, phase
        else:
            self.connection.ShutDown()
            self.execution_state_names[state]
            err_msg = "({}) {} - {}".format(self.execution_state_names[state],
                                            state,
                                            self.execution_state_desc[state])
            raise IOError(err_msg)


if __name__ == "__main__":

    config = {'chan1_atten': 0,
              'chan2_atten': 0,
              'source_level': 0.05,
              'source_level_unit': 1,
              }

    bode = Bode100()
    f, mag, phase = bode.run_frequency_sweep(1000, 1e6, 801, **config)
