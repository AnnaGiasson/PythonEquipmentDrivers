"""
Matrix_Test

Runs through a matrix of operating points capturing data of the transient
response at each point. Several oscilloscope measurements as well as the scope
image are logged.

The device under test (a VRM) is loaded by an analog CC electronic load that is
driven by a function generator. The output voltage setpoint is controlled via a
PWM waveform from the function generator. An Onsemi controller takes a 2V
667kHz square wave as its input.

The Model-View-Controller Architure is used in this script to make the code
more easily reusable.

    The "Model" is the Test_Environment class which controls the equipment used
    in the test and has abstracted methods which can be called by the
    controlller.

    The "View" is the User_Feedback class, which essentially is just print
    statements that are written in abstracted methods so can be called by the
    controlller. This is abstracted into its own class so that, for example, if
    you want to use a GUI or change the information printed to the terminal you
    can change out the View instead of making numerous changes to the
    Controller or the test itself.

    The "Controller" is the Matrix_Test class which defines control flow of the
    test, handles user prompts from the View, issues commands to the Model, and
    manages the files and data which result from this test.

"""

import pythonequipmentdrivers as ped
from pathlib import Path
import json
from time import sleep
from itertools import product
import sys


class Test_Environment():

    g_i_drive = 200
    g_i_mon = 2000
    k_ratio = 48

    def __init__(self, equipment_config, **kwargs) -> None:

        init = kwargs.get("initialize", False)
        self.env = ped.EnvironmentSetup(equipment_config, init_devices=init)

    def set_operating_point(self, **op_point):

        if op_point.get('v_dr', False):
            self.set_v_dr(op_point.get('v_dr'))

        if op_point.get('v_out', False):
            self.set_v_out(op_point.get('v_out'))

        if op_point.get('v_in', False):
            self.set_v_in(op_point.get('v_in'))

        if op_point.get('i_out', False):
            self.set_i_out(op_point.get('i_out'))

        return None

    def set_v_in(self, voltage, **kwargs):

        # set levels
        self.env.source.set_voltage(voltage)

        # enable/disable
        if kwargs.get("enable", False):
            if not self.env.source.get_state():
                self.env.source.on()

        elif kwargs.get("disable", True):
            if self.env.source.get_state():
                self.env.source.off()

        return None

    @staticmethod
    def __onsemi_v_ref_to_dc(v_ref):
        """
        determines the duty cycle needed to provide a specific reference
        voltage to the Onsemi controller
        """

        # more accurate equation determined through regression
        return min([max([102.71584607*v_ref - 32.04081548, 2]), 98])

    def set_v_out(self, voltage, **kwargs):

        channel = kwargs.get('v_ref_chan', 2)

        # set levels
        dc = round(self.__onsemi_v_ref_to_dc(voltage), 2)
        self.env.function_gen.set_pulse_dc(dc, source=channel)

        # enable/disable
        if kwargs.get("enable", False):
            if not self.env.function_gen.get_output_state(source=channel):
                self.env.function_gen.set_output_state(1, source=channel)

        elif kwargs.get("disable", True):
            if self.env.function_gen.get_output_state(source=channel):
                self.env.function_gen.set_output_state(0, source=channel)

        return None

    def set_i_out(self, current, **kwargs):

        channel = kwargs.get('i_drive_chan', 1)

        # set levels
        self.env.function_gen.set_voltage_high(current/self.g_i_drive,
                                               source=channel)

        if kwargs.get("current_low", False):
            v_drive = kwargs.get("current_low")/self.g_i_drive
            self.env.function_gen.set_voltage_low(v_drive,
                                                  source=channel)

        # enable/disable
        if kwargs.get("enable", False):
            if not self.env.function_gen.get_output_state(source=channel):
                self.env.function_gen.set_output_state(1, source=channel)

        elif kwargs.get("disable", True):
            if self.env.function_gen.get_output_state(source=channel):
                self.env.function_gen.set_output_state(0, source=channel)

        return None

    def set_v_dr(self, voltage=5.1, channel=1, **kwargs):

        # set levels
        self.env.aux_source.set_voltage(voltage, channel)

        # enable/disable
        if kwargs.get("enable", False):
            if not self.env.aux_source.get_output_state(channel):
                self.env.aux_source.set_output_state(1, channel)

        elif kwargs.get("disable", True):
            if self.env.aux_source.get_output_state(channel):
                self.env.aux_source.set_output_state(0, channel)

        return None

    def initialize(self, v_in=40, v_out=0.8, i_out=10, **kwargs):

        self.set_v_dr(enable=True)
        sleep(0.5)  # give time for controller to wake up

        self.set_v_out(v_out, enable=True)
        self.set_i_out(i_out, current_low=0, enable=True)
        self.set_v_in(v_in, enable=True)

        sleep(0.5)  # let DUT boot

        return None

    def shut_down(self):

        self.set_v_in(0, disable=True)
        sleep(0.5)  # to allow output to discharge

        self.set_v_dr(0, disable=True)

        self.set_v_out(0, disable=True)
        self.set_i_out(10, current_low=0, disable=True)

        return None

    def idle(self):
        self.set_i_out(10, current_low=0)
        return None

    def adjust_scope(self, **op_point):

        if op_point.get('v_out', False):

            v_o = op_point.get('v_out')

            self.env.oscilloscope.set_channel_offset(3, -v_o)
            self.env.oscilloscope.set_channel_offset(4, -v_o*self.k_ratio)

        if op_point.get('v_in', False):

            self.env.oscilloscope.set_channel_offset(1, -op_point.get('v_in'))

        if op_point.get('i_out', False):

            i_o = op_point.get('i_out')

            self.env.oscilloscope.set_channel_scale(5, (i_o/self.g_i_mon)/7)
            self.env.oscilloscope.set_channel_offset(5, -4, use_divisions=True)
            self.env.oscilloscope.set_channel_scale(7, i_o/self.g_i_drive/7)
            self.env.oscilloscope.set_channel_offset(7, -4, use_divisions=True)

            self.env.oscilloscope.set_trigger_level(0.5*i_o/self.g_i_drive)

        return None

    def collect_data(self, **kwargs):

        # trigger environment

        sleep(0.5)  # let op point settle
        self.env.oscilloscope.trigger_single()

        sleep(2)  # scope arming
        self.env.function_gen.trigger()

        sleep(kwargs.get('meas_delay', 0))

        # get data & scope image

        datum = self.env.oscilloscope.get_measure_data(*range(1, 13))

        self.env.oscilloscope.get_image(kwargs.get('image_name', 'capture'))

        return datum


class User_Feedback():

    def write(self, stream):
        sys.stdout.write(stream)
        return None

    def initialization(self, directory, images, raw_data):

        self.write('Test environment initialized\n')

        self.write(f'Created test directory: {directory}\n')
        if images:
            self.write("Saving images\n"
                       f"\tdirectory: {Path(directory) / 'images'}\n")
        if raw_data:
            self.write("Saving raw data\n"
                       f"\tdirectory: {Path(directory) / 'raw_data'}\n")
        self.write('\n')

        return None

    def test_start(self):
        self.write('\n***** Starting Test *****\n\n')
        return None

    def test_progress(self, **op_point):

        self.write('Testing Op point ')
        for key, val in op_point.items():
            self.write(f'|  {key} = {val}  |')

        self.write('\n')

        return None

    def test_finish(self):
        self.write("\n***** Test Complete *****\n\n")
        return None

    def test_error(self, error):
        self.write('\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
                   'An error has occured which interrupted testing'
                   '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n')
        self.write(f'Error: {error}\n')
        return None

    def test_data_logged(self, image_name):
        self.write('\tMeasurement data saved to file.\n')
        self.write(f'\tScope image saved to file: {Path(image_name).name}\n')
        return None

    def idling(self):
        self.write('\tCooling Down .....\n\n')
        return None


class Matrix_Test():

    # Vout needs to be converted to mV before use
    image_template = r"Vout{}mV_Vin{}V_Iout{}A"

    def __init__(self, test_env: Test_Environment, test_config, **kwargs):

        # Using MVC architecture, this class is the Controller
        self.test_env = test_env  # Model
        self.ux = User_Feedback()  # View

        # get parameters that define the test
        if isinstance(test_config, (str, Path)):
            with open(test_config, 'r') as f:
                self.test_config = json.load(f)
        elif isinstance(test_config, dict):
            self.test_config = test_config
        else:
            raise ValueError("Test configuration are unspecified")

        # set up file structure
        self.base_directory = kwargs.get("base_directory", Path('.').resolve())

        save_images = kwargs.get('images', False)
        save_raw_data = kwargs.get('raw_data', False)
        self.test_dir = ped.utility.create_test_log(self.base_directory,
                                                    images=save_images,
                                                    raw_data=save_raw_data,
                                                    **self.test_config)

        self.ux.initialization(self.test_dir, save_images, save_raw_data)

        # create data table / add header row
        self.data_file = kwargs.get('file_name', 'data')
        ped.utility.log_data(self.test_dir, self.data_file,
                             *self.test_config.get("data_columns", []),
                             init=True)

        return None

    def run(self):

        try:

            # temp/reused variables
            v_out_list = self.test_config.get('v_out_list')
            v_in_list = self.test_config.get('v_in_list')
            i_out_list = self.test_config.get('i_out_list')
            i_out_max = max(i_out_list)

            meas_delay = self.test_config.get('meas_delay', 0.5)

            # begin test
            self.ux.test_start()
            self.test_env.initialize(v_in=v_in_list[0],
                                     v_out=v_out_list[0],
                                     i_out=i_out_list[0])

            # main test loop
            for (v_o, v_i, i_o) in product(v_out_list, v_in_list, i_out_list):

                # prepare setup
                self.ux.test_progress(v_out=v_o, v_in=v_i, i_out=i_o)
                self.test_env.set_operating_point(v_out=v_o, v_in=v_i,
                                                  i_out=i_o)

                self.test_env.adjust_scope(v_out=v_o, v_in=v_i, i_out=i_o)

                # get data
                image_name = self.image_template.format(int(1e3*v_o), int(v_i),
                                                        int(i_o))
                image_name = self.test_dir / 'images' / image_name

                datum = self.test_env.collect_data(meas_delay=meas_delay,
                                                   image_name=image_name)
                self.ux.test_data_logged(image_name)

                ped.utility.log_data(self.test_dir, self.data_file,
                                     v_o, v_i, i_o, *datum)

                # prepare for next iteration
                self.test_env.idle()
                self.ux.idling()
                sleep(20*i_o/i_out_max)  # cool down after full load

        except ped.VisaIOError as error:
            self.ux.test_error(error)

        else:
            self.ux.test_finish()

        finally:
            self.test_env.shut_down()

        return None


if __name__ == "__main__":
    cwd = Path(__file__).parent

    test = Matrix_Test(Test_Environment(cwd / 'equipment_configuration.json',
                                        initialize=True),
                       test_config=cwd/'test_configuration.json')
    test.run()
