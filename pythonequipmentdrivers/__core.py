import pyvisa
from pyvisa import VisaIOError
from importlib import import_module
import json
from pathlib import Path


# Globals
rm = pyvisa.ResourceManager()


# Utility Functions
def get_devices_addresses():
    """
    returns a list of the addresses of peripherals connected to the computer
    """
    return rm.list_resources()


def identify_devices(verbose=False):
    """
    identify_connections(verbose=False)

    verbose (optional): bool, if True address and identicaion information is
    printed to the screen in addition to return the data in a structure,
    default behavior is to print the information.

    Queries devices connected for IDN response
    appends addresses with valid responses to a tuple with its response

    returns:
        ((address_1, idn_response_1),
         (address_2, idn_response_2),
         ...
         (address_n, idn_response_n))
    """

    scpi_devices = []
    for address in rm.list_resources():
        try:
            device = rm.open_resource(address)
            response = device.query("*IDN?")
            scpi_devices.append((address, response))
            device.close()

            if verbose:
                print(f"{len(scpi_devices)-1}:")
                print(f"\taddress: {address}")
                print(f"\tresponse: {response}\n")

        except pyvisa.Error:
            if verbose:
                print(f"Invalid IDN query reponse from address {address}\n")
            device.close()
            continue

    return scpi_devices


class Scpi_Instrument():

    def __init__(self, address, **kwargs):
        self.address = address
        self.instrument = rm.open_resource(self.address)
        self.timeout = kwargs.get('timeout', 1000)
        return None

    @property
    def idn(self):
        """
        idn

        Identify Query

        Returns a string that uniquely identifies the instrument. The IDN query
        sent to the instrument is one of the IEEE 488.2 Common Commands and
        should be supported by all SCPI compatible instruments.

        Returns:
            str: uniquely identifies the instrument
        """
        return self.instrument.query('*IDN?')

    def cls(self):
        """
        cls()

        Clear Status Command

        Clears the instrument status byte by emptying the error queue and
        clearing all event registers. Also cancels any preceding *OPC command
        or query. The CLS command sent to the instrument is one of the
        IEEE 488.2 Common Commands and should be supported by all SCPI
        compatible instruments.

        Returns:
            None
        """

        self.instrument.write('*CLS')
        return None

    def rst(self):
        """
        rst()

        Reset Command

        Executes a device reset and cancels any pending *OPC command or query.
        The RST command sent to the instrument is one of the IEEE 488.2 Common
        Commands and should be supported by all SCPI compatible instruments.

        Returns:
            None
        """

        self.instrument.write('*RST')
        return None

    @property
    def timeout(self):

        return self.instrument.timeout

    @timeout.setter
    def timeout(self, timeout):
        self.instrument.timeout = timeout
        return None

    def __del__(self):
        try:
            # if connection has been estabilished terminate it
            if hasattr(self, 'instrument'):
                self.instrument.close()
        except VisaIOError:
            # if connection not connection has been estabilished (such as if an
            # error is throw in __init__) do nothing
            pass
        return None

    def __repr__(self):

        def_str = f"{self.__class__.__name__}"
        def_str += f"({self.address}, timeout={self.timeout})"

        return def_str

    def __str__(self):
        return f'Instrument ID: {self.idn}\nAddress: {self.address}'

    def __eq__(self, obj):

        """
        __eq__(obj)

        Args:
            obj (object): object to compare

        Returns:
            bool: True if the objects are both instances of Scpi_Instrument
                (or any class that inherits from Scpi_Instrument) and have the
                same address and class name. Otherwise False.
        """

        if not isinstance(obj, Scpi_Instrument):
            return False

        if not (self.address == obj.address):
            return False

        if not (self.__class__.__name__ == obj.__class__.__name__):
            return False

        return True

    def __ne__(self, obj):
        """
        __ne__(obj)

        Args:
            obj (object): object to compare

        Returns:
            bool: whether or not to object are not equal. Defined as the
                inverse of the result from __eq__
        """

        return not self.__eq__(obj)

    def send_raw_scpi(self, command_str, **kwargs):
        """
        send_raw_scpi(command_str)

        Pass-through function which forwards the contents of 'command_str' to
        the device. This function is intended to be used for API calls for
        functionally that is not currently supported. Can only be used for
        commands, will not return queries.

        Args:
            command_str: string, scpi command to be passed through to the
                device.

        Returns:
            None
        """

        self.instrument.write(command_str, **kwargs)
        return None

    def query_raw_scpi(self, query_str, **kwargs):
        """
        query_raw_scpi(query)

        Pass-through function which forwards the contents of 'query_str' to
        the device, returning the response without any processing. This
        function is intended to be used for API calls for functionally that is
        not currently supported. Only to be used for queries.

        Args:
            query_str: string, scpi query to be passed through to the device.

        """

        return self.instrument.query(query_str, **kwargs)

    def read_raw_scpi(self, **kwargs):
        """
        read_raw_scpi()

        Pass-through function which reads the device, returning the response
        without any processing. This function is intended to be used for API
        calls for functionally that is not currently supported.
        Only to be used for read.
        """

        return self.instrument.read(**kwargs)


class EnvironmentSetup():
    """
    Class for handling the instantiation of generic sets of test equipment
    based on addressing data from file. Can blindly connect to all equipment in
    the provided file or dictionary (equipment_setup) and can optionally verify
    that a specific set of equipment is in file (based on object_mask)

    # Add expected/assumed format of json file
    Expected JSON file format

    "device_name_1": {
                      "object": "Class_Name_1",
                      "definition": "Object_Definition_1",
                      "address": "Device_Address_1"
                      },
    "device_name_2": {
                      "object": "Class_Name_2",
                      "definition": "Object_Definition_2",
                      "address": "Device_Address_2"
                      },
        .
        .
        .

    "device_name_n": {
                      "object": "Class_Name_n",
                      "definition": "Object_Definition_n",
                      "address": "Device_Address_n"
                      }

    The "device_name" of each dictionary represents the name of the instance
    of class "object" to be connected to at address "address". The location to
    the definition of the class "object" needs to be provided using the key
    "definition". An example of this is shown below:

    "source_v_in": {
                    "object": "Chroma_62012P",
                    "definition": "pythonequipmentdrivers.source",
                    "address": "USB0::0x1698::0x0837::002000000655::INSTR",
                    "kwargs": {}
                    },

    If this device is connected and availible this will create an instance of
    the Chroma_62012P at the provided address. The source is defined in the
    pythonequipmentdrivers.source sub-module. This instance can be accessed
    using EnvironmentSetup('path_to_json file'). i.e. self.source_v_in
    There is an optional argument for each device "kwargs", if present the
    arugements contained in kwargs will be passed as keyword arguements in the
    instantation of the device, if not needed this can be omitted.

    The "object_mask" arguement can be used to connect to a sub-set of devices
    described in the JSON file. If used, object_mask should be an iterable
    containing the names of the devices in the JSON file that are desired.
    If all names contained in object_mask are not present in the JSON file an
    exception will be raised. Otherwise, this object will connect exculsively
    to the devices specified in object_mask.

    If init_devices is True than this object will search the JSON file for an
    array named "init" which defines a sequence of commands to initialize the
    device. For example:

    "source_v_in": {
                    "object": "Chroma_62012P",
                    "definition": "pythonequipmentdrivers.source",
                    "address": "USB0::0x1698::0x0837::002000000655::INSTR"
                    "init": [
                             ["set_voltage", {"voltage": 0}],
                             ["off", {}],
                             ]
                    },

    In this example, If init_devices is True and the device was successfully
    connected, this object will successively iterate through the array of
    command, arguement pairs; calling the commands listed using arguements (if
    any) provided. The commands listed must be valid methods of the device
    object, all arguements used will be passed as keyword arguements and
    therefore need to be named.
    """

    def __init__(self, equipment_setup, object_mask=None, init_devices=False,
                 **kwargs):

        # init
        self.object_mask = object_mask

        if isinstance(equipment_setup, (str, Path)):
            self.equipment_json_path = equipment_setup

            # read equipment info from file
            with open(self.equipment_json_path, 'rb') as read_file:
                self.configuration = json.load(read_file)

        elif isinstance(equipment_setup, dict):
            self.equipment_json_path = None
            self.configuration = equipment_setup
        else:
            raise ValueError('Unsupported type for arguement "equipment_setup"'
                             ' should a str/Path object to a JSON file or a'
                             ' dictionary')

        # check that required items are present in file
        if self.object_mask is not None:

            self.object_mask = set(self.object_mask)
            equipment_in_file = set(self.configuration)
            common_equipment = equipment_in_file.intersection(self.object_mask)

            if common_equipment != self.object_mask:

                missing_items = self.object_mask.difference(common_equipment)
                print("Required equipment not found in configuration file")
                print(f"Missing items: {', '.join(missing_items)}")
                raise IOError("Required Equipment Missing")

        self.__make_connections(init_devices=init_devices,
                                verbose=kwargs.get('verbose', True))
        return None

    def __make_connections(self, init_devices=False, verbose=True):
        """
        Establishs connections to the equipment specified in equipment_json
        """

        if self.object_mask is not None:
            device_list = list(self.configuration.keys())
            for device_name in device_list:
                if device_name not in self.object_mask:
                    self.configuration.pop(device_name)

        for device_name in self.configuration:

            device_info = self.configuration[device_name]

            try:
                # get object to instantate from config file
                class_ = getattr(import_module(device_info['definition']),
                                 device_info['object'])

                # get any kwargs for instanciation
                kwargs = device_info.get('kwargs', {})

                # creates instance named 'device_name' of class
                # 'device_info['object']'
                vars(self)[device_name] = class_(device_info['address'],
                                                 **kwargs)

                if verbose:
                    print(f'[CONNECTED] {device_name}')

                if ('init' in device_info) and init_devices:
                    # get the instance in question
                    inst = getattr(self, device_name)
                    initiaize_device(inst, device_info['init'])
                    if verbose:
                        print('\tInitialzed')

            except (VisaIOError, ConnectionError) as error:

                if verbose:
                    print(f'[FAILED CONNECTION] {device_name}')

                if self.object_mask is not None:
                    # if the failed connection is for a piece of required
                    # equipment stop instantations
                    print(error)
                    raise ConnectionError(f"Failed connection: {device_name}")

            except (ModuleNotFoundError, AttributeError) as error:

                if verbose:
                    print(f'[UNSUPPORTED DEVICE] {device_name}\t{error}')

                if self.object_mask is not None:
                    # if the failed connection is for a piece of required
                    # equipment stop instantations
                    print(error)
                    raise ConnectionError(f"Failed connection: {device_name}")
        return None

    # def __del__(self):
    #     # something to consider... when python exits, should equipment
    #     # be automatically released? (mode to local etc)
    #     return None

def get_callable_methods(instance):
    """
    get_callable_methods(instance)

    Returns a tuple of all callable methods of an object or instance that are
    not "dunder"/"magic"/"private" methods

    Args:
        instance (object): object or instance of an object to get methods of

    Returns:
        tuple: collection of callable methods.
    """

    # get items in __dir__() that are callable (will include sub-classes)
    valid_cmds = filter(lambda method: (callable(getattr(instance, method))),
                        instance.__dir__())

    # filter out ignore dunders
    valid_cmds = filter(lambda func_name: ('__' not in func_name), valid_cmds)
    return tuple(valid_cmds)


def initiaize_device(inst, initialization_sequence):
    """
    initiaize_device(inst, initialization_sequence)

    inst: (obj) instance of object to initialize

    initialization_sequence: (list) list of lists containing valid methods of
                             "inst" with a dict of arguements to pass as kwargs

                             Will run in the order given
    ex: sequence = [
                    ["set_voltage", {"voltage": 0}],
                    ["off", {}],
                   ]

    Here "inst" has the two methods "set_voltage", and "off". The first of
    which requires the arguement voltage and the second of which has no args.
    """

    # get possible instance methods
    valid_cmds = get_callable_methods(inst)

    # for cmd in initialization_sequence:
    for cmd, args in initialization_sequence:
        if cmd in valid_cmds:
            try:
                # call instance method with kwargs in passed dict
                getattr(inst, cmd)(**args)
                # getattr(inst, cmd)(**initialization_sequence[cmd])
            except TypeError as error:  # invalid kwargs
                print(f"\tError with initialization command\t{error}")

    return None


def get_equip(ped, jsonfile, equipment, init_devices=False, errors=True):
    """get_equip(ped, jsonfile, equipment)

    Args:
        ped : pythonequipmentdrivers instance
        jsonfile (file): setup file for pythonequipmentdrivers listing the
                         equipment available to connect with
        equipment (list or tuple): equipment to make connection to
        init_devices (bool, optional): Send init commands to equipment.
                                       Defaults to False. False leaves the
                                       present settings in the equipment
        errors (bool, optional): if False, ignore errors and return None
    Returns:
        env: instance of ped with your equipment ready for commands
    Example:
        import pythonequipmentdrivers as ped
        jsonfile = 'bench.json'
        equipment = ['multimeter_01', 'dac_01']
        env = ped.get_equip(ped, jsonfile, equipment)
        env.multimeter_01.measure_voltage()
    """
    if equipment is None:
        print("warning, no equipment requested!")
    try:
        env = ped.EnvironmentSetup(jsonfile,
                                   object_mask=equipment,
                                   init_devices=False)
    except ConnectionError:
        if errors:
            raise
        else:
            print("no equipment found, running without!")
            return None
    return env


# Testing Errors
class LowVinError(Exception):
    def __init__(self, message="Vin measured below lower threshold"):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class LowVoutError(Exception):
    def __init__(self, message="Vout measured below lower threshold"):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


if __name__ == "__main__":
    pass
