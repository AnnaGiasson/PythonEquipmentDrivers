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

import json
from itertools import product
from pathlib import Path
from time import sleep
from typing import Tuple, Union

import pythonequipmentdrivers as ped


class Test_Environment:

    g_i_drive: float = 200
    g_i_mon: float = 2000

    """
    Test_Environment(equipment_setup, **kwargs)

    This module provides an abstraction for performing generic test environment
    functions by handling the function calls needed to control specific test
    equipment.

    By seperating the control of specific instruments from the general test you
    can easily write or change the test routine to work with different test
    equipment, or alternatively, easily use same equipment setup for a variaty
    of tests.

    Args:
        equipment_setup (str, Path, dict): equipment config information to
            instatiate an EnvironmentSetup object. See
            help(pythonequipmentdrivers.EnvironmentSetup) for more information.

    Kwargs:
        init (bool, optional): If true the Test_Environment object will attempt
            to run any initialization sequences for equipment that are present
            in "equipment_setup". Defaults to False.
    """

    def __init__(self, config: Union[str, Path, dict], init: bool = False) -> None:

        self.equipment = ped.connect_resources(config=config, init=init)

    def set_operating_point(self, **op_point) -> None:

        if op_point.get("v_dr", False) is not None:
            self.set_v_aux(op_point.get("v_dr"))

        if op_point.get("v_out", False) is not None:
            self.set_v_out(op_point.get("v_out"))

        if op_point.get("v_in", False) is not None:
            self.set_v_in(op_point.get("v_in"))

        if op_point.get("i_out", False) is not None:
            self.set_i_out(op_point.get("i_out"))

    def set_v_in(self, voltage, **kwargs) -> None:
        """
        set_v_in(self, voltage, **kwargs)

        Sets the level, or toggles on/off, the voltage source present at the
        Vin connection of the test environment.

        Args:
            voltage (float, int): voltage level to set in Volts DC.

        Kwargs:
            enable (bool, optional): If true, enables the output of the voltage
                source after setting the requested output voltage level.
                Defaults to False.

            disable (bool, optional): If true, enables the output of the
                voltage source after setting the requested output voltage
                level. Defaults to False.
        """

        # set levels
        self.equipment.source.set_voltage(voltage)

        # enable/disable
        if kwargs.get("enable", False):
            if not self.equipment.source.get_state():
                self.equipment.source.on()

        elif kwargs.get("disable", False):
            if self.equipment.source.get_state():
                self.equipment.source.off()

    @staticmethod
    def __onsemi_v_ref_to_dc(v_ref: float) -> float:
        """
        determines the duty cycle needed to provide a specific reference
        voltage to the Onsemi controller
        """

        # more accurate equation determined through regression
        return min([max([102.71584607 * v_ref - 32.04081548, 2.0]), 98.0])

    def set_v_out(self, voltage: float, **kwargs) -> None:
        """
        set_v_out(self, voltage, **kwargs)

        Sets the level, or toggles on/off, the voltage source present at the
        Vout connection of the test environment.

        Args:
            voltage (float): voltage level to set in Volts DC.

        Kwargs:
            enable (bool, optional): If true, enables the output of the voltage
                source after setting the requested output voltage level.
                Defaults to False.

            disable (bool, optional): If true, enables the output of the
                voltage source after setting the requested output voltage
                level. Defaults to False.
        """

        func_gen = self.equipment.function_gen
        channel = kwargs.get("v_ref_chan", 2)

        # set levels
        v_drive = self.__onsemi_v_ref_to_dc(voltage)
        func_gen.set_pulse_dc(v_drive, source=channel)

        # enable/disable
        if kwargs.get("enable", False):
            device_state = func_gen.get_output_state(source=channel)
            if not device_state:
                func_gen.set_output_state(True, source=channel)

        elif kwargs.get("disable", False):
            device_state = func_gen.get_output_state(source=channel)
            if device_state:
                func_gen.set_output_state(False, source=channel)

    def set_i_out(self, current, **kwargs) -> None:
        """
        set_i_out(self, current, **kwargs)

        Sets the level, or toggles on/off, the current source present at the
        Iout connection of the test environment.

        Args:
            current (float, int): current level to set in Amps DC.

        Kwargs:
            enable (bool, optional): If true, enables the output of the current
                source after setting the requested output current level.
                Defaults to False.

            disable (bool, optional): If true, enables the output of the
                current source after setting the requested output current
                level. Defaults to False.
        """

        func_gen = self.equipment.function_gen
        channel = kwargs.get("i_drive_chan", 1)

        # set levels
        func_gen.set_voltage_high(current / self.g_i_drive, source=channel)

        if kwargs.get("current_low", False):
            v_drive = kwargs.get("current_low") / self.g_i_drive
            func_gen.set_voltage_low(v_drive, source=channel)

        # enable/disable
        if kwargs.get("enable", False):
            device_state = func_gen.get_output_state(source=channel)
            if not device_state:
                func_gen.set_output_state(True, source=channel)

        elif kwargs.get("disable", False):
            device_state = func_gen.get_output_state(source=channel)
            if device_state:
                func_gen.set_output_state(False, source=channel)

    def set_v_aux(self, voltage=5.1, channel=1, **kwargs) -> None:
        """
        set_v_aux(self, voltage, **kwargs)

        Sets the level, or toggles on/off, the voltage source present at the
        Vaux connection of the test environment.

        Args:
            voltage (float, int): voltage level to set in Volts DC.

        Kwargs:
            enable (bool, optional): If true, enables the output of the voltage
                source after setting the requested output voltage level.
                Defaults to False.

            disable (bool, optional): If true, enables the output of the
                voltage source after setting the requested output voltage
                level. Defaults to False.
        """

        # set levels
        self.aux_source.set_voltage(voltage, channel)

        # enable/disable
        if kwargs.get("enable", False):
            if not self.aux_source.get_output_state(channel):
                self.aux_source.set_output_state(1, channel)

        elif kwargs.get("disable", False):
            if self.aux_source.get_output_state(channel):
                self.aux_source.set_output_state(0, channel)

    def initialize(self, **kwargs) -> None:

        self.set_v_aux(enable=True)
        sleep(0.5)  # give time for controller to wake up

        self.set_v_out(kwargs.get("v_out", 0.8), enable=True)
        self.set_i_out(kwargs.get("i_out", 10), current_low=0, enable=True)
        self.set_v_in(kwargs.get("v_in", 40), enable=True)

        sleep(0.5)  # let DUT boot

    def shut_down(self) -> None:

        self.set_v_in(0, disable=True)
        sleep(0.5)  # to allow output to discharge

        self.set_v_aux(0, disable=True)

        self.set_v_out(0, disable=True)
        self.set_i_out(10, current_low=0, disable=True)

    def idle(self) -> None:
        self.set_i_out(10, current_low=0)

    def adjust_scope(self, **op_point) -> None:

        scope = self.equipment.oscilloscope

        if op_point.get("v_out", False):

            v_o = op_point["v_out"]
            k_ratio = 48  # ratio between the intermidiate and output voltages

            scope.set_channel_offset(3, -v_o)
            scope.set_channel_offset(4, -v_o * k_ratio)

        if op_point.get("v_in", False):
            scope.set_channel_offset(1, -op_point["v_in"])

        if op_point.get("i_out", False):

            i_o = op_point["i_out"]

            scope.set_channel_scale(5, (i_o / self.g_i_mon) / 7)
            scope.set_channel_offset(5, -4, use_divisions=True)
            scope.set_channel_scale(7, i_o / self.g_i_drive / 7)
            scope.set_channel_offset(7, -4, use_divisions=True)

            scope.set_trigger_level(0.5 * i_o / self.g_i_drive)

    def collect_data(self, **kwargs) -> Tuple[float]:

        # trigger environment

        sleep(0.5)  # let op point settle
        self.equipment.oscilloscope.trigger_single()

        sleep(2)  # scope arming
        self.equipment.function_gen.trigger()

        sleep(kwargs.get("meas_delay", 0))

        # get data & scope image

        datum = self.equipment.oscilloscope.get_measure_data(*range(1, 13))

        image_path = kwargs.get("image_name", "capture")
        self.equipment.oscilloscope.get_image(image_path)

        return datum


class User_Feedback:

    @staticmethod
    def initialization(directory, images, raw_data) -> None:

        print("Test environment initialized")

        print(f"Created test directory: {directory}")
        if images:
            print("Saving images\n" f"\tdirectory: {Path(directory) / 'images'}")
        if raw_data:
            print("Saving raw data\n" f"\tdirectory: {Path(directory) / 'raw_data'}")
        print("")

    @staticmethod
    def test_start() -> None:
        print("\n***** Starting Test *****\n")

    @staticmethod
    def test_progress(**op_point) -> None:

        print("Testing Op point ", end="")
        for key, val in op_point.items():
            print(f"|  {key} = {val}  |", end="")
        print("")

    @staticmethod
    def test_finish() -> None:
        print("\n***** Test Complete *****\n")

    @staticmethod
    def test_error(error) -> None:
        print(
            "\n!!!!!!!!!!!!!!!!!!!!!!!! "
            "An error has occured which interrupted testing"
            " !!!!!!!!!!!!!!!!!!!!!!!!\n"
        )
        print(f"Error: {error}\n")

    @staticmethod
    def test_data_logged(file_name: Path) -> None:
        print("\tMeasurement data saved to file.")
        print(f"\tScope image saved to file: {Path(file_name).name}")

    @staticmethod
    def idling() -> None:
        print("\tCooling Down .....\n")


class Matrix_Test:

    def __init__(self, test_env: Test_Environment, test_config, **kwargs) -> None:

        # Using MVC architecture, this class is the Controller
        self.test_env = test_env  # Model
        self.user_fb = User_Feedback()  # View

        self.read_test_config(test_config)  # parameters that define the test

        # set up file structure
        self.base_directory = kwargs.get("base_directory", Path(".").resolve())

        save_images = kwargs.get("images", False)
        save_raw_data = kwargs.get("raw_data", False)
        self.test_dir = ped.utility.create_test_log(
            self.base_directory,
            images=save_images,
            raw_data=save_raw_data,
            **self.test_config,
        )

        self.user_fb.initialization(self.test_dir, save_images, save_raw_data)

        # create data table / add header row
        self.data_file = kwargs.get("file_name", "data")
        if self.test_config.get("data_columns", False):
            ped.utility.log_to_csv(
                self.test_dir.joinpath(self.data_file),
                *self.test_config["data_columns"],
                init=True,
            )

    def read_test_config(self, test_config: Union[str, Path]) -> None:
        if isinstance(test_config, (str, Path)):
            with open(test_config, "r") as f:
                self.test_config = json.load(f)
        elif isinstance(test_config, dict):
            self.test_config = test_config
        else:
            raise ValueError("Test configuration are unspecified")

    def run(self) -> None:

        # Vout needs to be converted to mV before use
        fname_template = r"Vout{}mV_Vin{}V_Iout{}A"

        try:

            # temp/reused variables
            v_out_list = self.test_config.get("v_out_list")
            v_in_list = self.test_config.get("v_in_list")
            i_out_list = self.test_config.get("i_out_list")
            i_out_max = max(i_out_list)

            meas_delay = self.test_config.get("meas_delay", 0.5)

            # begin test
            self.user_fb.test_start()
            self.test_env.initialize(
                v_in=v_in_list[0], v_out=v_out_list[0], i_out=i_out_list[0]
            )

            # main test loop
            for v_o, v_i, i_o in product(v_out_list, v_in_list, i_out_list):

                # prepare setup
                self.user_fb.test_progress(v_out=v_o, v_in=v_i, i_out=i_o)
                self.test_env.set_operating_point(v_out=v_o, v_in=v_i, i_out=i_o)

                self.test_env.adjust_scope(v_out=v_o, v_in=v_i, i_out=i_o)

                # get data
                fpath = fname_template.format(int(1e3 * v_o), int(v_i), int(i_o))
                fpath = self.test_dir / "images" / fpath

                datum = self.test_env.collect_data(
                    meas_delay=meas_delay, image_name=fpath
                )

                # save data to file
                ped.utility.log_to_csv(
                    self.test_dir.joinpath(self.data_file), v_o, v_i, i_o, *datum
                )
                self.user_fb.test_data_logged(fpath)

                # prepare for next iteration
                self.test_env.idle()
                self.user_fb.idling()
                sleep(20 * i_o / i_out_max)  # cool down after full load

        except ped.VisaIOError as error:
            self.user_fb.test_error(error)

        else:
            self.user_fb.test_finish()

        finally:
            self.test_env.shut_down()


if __name__ == "__main__":
    cwd = Path(__file__).parent
    env = Test_Environment(config=cwd / "equipment.config", init=True)
    test = Matrix_Test(env, test_config=cwd / "test_configuration.json")
    test.run()
