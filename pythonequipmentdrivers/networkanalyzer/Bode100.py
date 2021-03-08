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
    execution_state_names = ('Ok', 'Overload', 'Error', 'DeviceLost',
                             'Cancelled', 'CalibrationMandatory',)
    execution_state_desc = ('Measurement successfully completed.',
                            'Overload detected. Check OverloadLevel.',
                            'Unknown error occurred during measurement.',
                            'Device connection lost during measurement.',
                            'Execution stopped by user.',
                            'Calibration mandatory for this measurement mode.',
                            )

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

    def configure_gain_phase_setup(self, measurement, **config):

        """
        configure_gain_phase_setup(measurement, **config)

        configurations a gain phase measurement on of the Bode 100. This
        function is run automatically by the gain_phase_measurement method.

        Args:
            measurement: gain phase measurement instance to be configured on
                         the connected Bode 100.

        Kwargs:
            logarithmic_sweep (bool, optional): Determines the spacing between
                the frequency points used in the sweep. If True 'n_points' are
                spaced logarithmically from 'f_start' to 'f_end', otherwise
                they are spaced linearly. Defaults to True.

            gain_unit (str, optional): The unit of the returned gain vector.
                Valid options are 'db' or 'linear'. Defaults to 'db'.
            phase_unit (str, optional): The unit of the returned phase vector.
                Valid options are 'radians' or 'degrees'. Defaults to 'degrees'
            wrap_phase (bool, optional): Whether or not the returned phase data
                is contained with +/- pi or 180 deg. Defaults to True.

            chan1_atten (int, optional): Attenuation of the channel 1 to be
                used in the sweep in dB. Defaults to -20 dB.
            chan2_atten (int, optional): Attenuation of the channel 2 to be
                used in the sweep in dB. Defaults to -20 dB.

            source_level (int or iterable, optional): if this is an int it
                represents a fixed amplitude of the injected signal over
                frequency. If the type is an iterable then it is a lists of
                freq/level pairs to construct a shaped level,
                    ex. [(1e3, 0), (100e3, 0), (1e6, -20)]
                Defaults to -30.
            source_units (str, optional): units of 'source_level'; Valid
                options are dbm, vpp, and vrms. Defaults to 'dbm'.

            receiver_bw (float, optional): Bandwidth of the reciever used
                in the frequecy sweep in Hz. Defaults to 1 kHz.

        Raises:
            ValueError: Raised if invalid options are passed for kwargs

        Returns:
            gain_measurement instance: measurement instance to the configured
                measurement on the connected Bode 100.
        """

        # source configuration
        src_unit_lut = ('dbm', 'vpp', 'vrms')
        src_unit = config.get('source_units', 'dbm')
        if src_unit not in src_unit_lut:
            raise ValueError('Invalid option for argument "source_units"')

        if isinstance(config.get('source_level', -30), int):
            measurement.SetSourceLevel(float(config.get('source_level', -30)),
                                       src_unit_lut.index(src_unit))

        elif isinstance(config.get('source_level', -30), (list, tuple)):

            measurement.SourceShaping.IsEnabled = True
            measurement.SourceShaping.LevelUnit = src_unit_lut.index(src_unit)
            measurement.SourceShaping.Clear()

            for freq, level in config.get('source_level'):
                measurement.SourceShaping.Add(float(freq), float(level))
        else:
            raise ValueError('Invalid Type for option "source_level"')

        # probe configuration
        measurement.Attenuation.Channel1 = config.get('chan1_atten', -20)
        measurement.Attenuation.Channel2 = config.get('chan2_atten', -20)

        # custom bandwidths need to be in milliHertz according to API docs
        measurement.ReceiverBandwidth = int(config.get('receiver_bw', 1e3)*1e3)

        return measurement

    def gain_phase_measurement(self, f_start, f_end, n_points, **kwargs):

        """
        gain_phase_measurement(f_start, f_end, n_points, **kwargs)

        Configures and runs a measurement gain and phase of the connected
        network over frequency. Returning the meausurment frequencies, gain,
        and phase.

        Ex.
            bode = Bode100()
            freq, mag, phase = bode.gain_phase_measurement(1e3, 1e6, 200)

        Args:
            f_start (float): The starting frequency of the frequency sweep in
                             Hz
            f_end (float): The final frequency of the frequency sweep in Hz
            n_points (int): The number of points contained in frequency sweep
                            between the frequencies f_start and f_end.

        Kwargs:
            logarithmic_sweep (bool, optional): Determines the spacing between
                the frequency points used in the sweep. If True 'n_points' are
                spaced logarithmically from 'f_start' to 'f_end', otherwise
                they are spaced linearly. Defaults to True.

            gain_unit (str, optional): The unit of the returned gain vector.
                Valid options are 'db' or 'linear'. Defaults to 'db'.
            phase_unit (str, optional): The unit of the returned phase vector.
                Valid options are 'radians' or 'degrees'. Defaults to 'degrees'
            wrap_phase (bool, optional): Whether or not the returned phase data
                is contained with +/- pi or 180 deg. Defaults to True.

            chan1_atten (int, optional): Attenuation of the channel 1 to be
                used in the sweep in dB. Defaults to -20 dB.
            chan2_atten (int, optional): Attenuation of the channel 2 to be
                used in the sweep in dB. Defaults to -20 dB.

            source_level (int or iterable, optional): if this is an int it
                represents a fixed amplitude of the injected signal over
                frequency. If the type is an iterable then it is a lists of
                freq/level pairs to construct a shaped level,
                    ex. [(1e3, 0), (100e3, 0), (1e6, -20)]
                Defaults to -30.
            source_units (str, optional): units of 'source_level'; Valid
                options are dbm, vpp, and vrms. Defaults to 'dbm'.

            receiver_bw (float, optional): Bandwidth of the reciever used
                in the frequecy sweep in Hz. Defaults to 1 kHz.
        Raises:
            Exception: If the C dll for the Bode 100 raises an error it will be
                       raised as in exception in Python.
            IOError: raised if a configuraion within the Bode 100 caused it to
                     produce a measurement error, e.g. overload, device lost,
                     calibration needed.
            ValueError: Raised if invalid options are passed for kwargs.

        Returns:
            tuple of np.array: The frequency, gain, and phase measurement
                               vectors resulting from the frequency sweep.
                               (frequency, magnitude, phase)
        """

        # connect to instrument
        self.connection = self.instrument.ConnectWithSerialNumber(self.idn)

        # configure measurement
        measurement = self.connection.Transmission.CreateGainMeasurement()
        measurement = self.configure_gain_phase_setup(measurement, **kwargs)
        measurement.ConfigureSweep(f_start, f_end, n_points,
                                   int(kwargs.get('logarithmic_sweep', True)))

        # execute measurement
        try:
            state = measurement.ExecuteMeasurement()
        except _win32client.pywintypes.com_error as error:
            self.connection.ShutDown()
            raise Exception(error.excepinfo[2])

        if state == 0:  # success
            # get raw data
            freq = _np.array(measurement.Results.MeasurementFrequencies)
            results = measurement.Results
            complex_vals = results.ComplexValues()
            self.connection.ShutDown()

            # format data
            if kwargs.get('gain_unit', 'db').lower() == 'db':
                mag = _np.array([datum.MagnitudeDB for datum in complex_vals])
            elif kwargs.get('gain_unit', 'db').lower() == 'linear':
                mag = _np.array([datum.Magnitude for datum in complex_vals])
            else:
                raise ValueError('Invalid option for argument "gain_unit"')

            if kwargs.get('wrap_phase', True):
                phase = _np.array([datum.Phase for datum in complex_vals])
            else:
                phase = _np.array(results.UnwrappedPhase(0))

            if kwargs.get('phase_unit', 'degrees').lower() == 'degrees':
                phase *= 180/_np.pi
            elif kwargs.get('phase_unit', 'degrees').lower() != 'radians':
                raise ValueError('Invalid option for argument "phase_unit"')

            return freq, mag, phase

        else:  # something unexpected occured
            self.connection.ShutDown()
            self.execution_state_names[state]
            err_msg = "({}) {} - {}".format(self.execution_state_names[state],
                                            state,
                                            self.execution_state_desc[state])
            raise IOError(err_msg)


if __name__ == "__main__":

    config = {'chan1_atten': 0,
              'chan2_atten': 0,
              'source_level': 0,
              'source_units': 'dbm',
              }

    bode = Bode100()
    f, mag, phase = bode.gain_phase_measurement(1000, 1e6, 801, **config)
