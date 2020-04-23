import visa
from visa import VisaIOError
from importlib import import_module as _import_module
import json


# Globals
rm = visa.ResourceManager()


# Utility Functions
def get_devices_addresses():
    """
    returns a list of the addresses of peripherals connected to the computer
    """
    return rm.list_resources()


def identify_devices(omit_print=False):
    """
    identify_connections(omit_print=False)

    omit_print (optional): bool, if true address and identicaion information is
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

            if not omit_print:
                print(f"{len(scpi_devices)-1}:")
                print(f"\taddress: {address}")
                print(f"\tresponse: {response}\n")

        except visa.Error:
            if not omit_print:
                print(f"Invalid IDN query reponse from address {address}\n")
            device.close()
            continue

    return scpi_devices


class Scpi_Instrument():
    def __init__(self, address, timeout=1000):
        self.address = address
        self.instrument = rm.open_resource(address)
        self.timeout = timeout
        self.instrument.timeout = self.timeout

        self.idn = self.instrument.query('*IDN?')

    def __del__(self):
        try:
            self.instrument.close()

        except AttributeError:
            # if instrument is inaccessible __init__ will raise a Visa Error
            # and instrument wont be initialized thus it can't be closed
            pass
        return

    def __repr__(self):

        def_str = f"{self.__class__.__name__}"
        def_str += f"({self.address}, timeout={self.timeout})"

        return def_str

    def __str__(self):
        return f'Instrument ID: {self.idn}\nAddress: {self.address}'

    def __eq__(self, obj):
        comp = (self.address == obj.address)
        comp &= (self.__class__.__name__ == obj.__class__.__name__)

        return comp

    def send_raw_scpi(self, command_str):
        """
        send_raw_scpi(command_str)

        command_str: string, scpi command to be passed through to the device.

        Pass-through function which forwards the contents of 'command_str' to
        the device. This function is intended to be used for API calls for
        functionally that is not currently supported. Can only be used for
        commands, will not return queries.
        """

        self.instrument.write(command_str)
        return


class EnvironmentSetup():
    """
    Class for handling the instantiation of generic sets of test equipment
    based on addressing data from file. Can blindly connect to all equipment in
    the provided file (equipment_json) or optionally can varify that a specific
    set of equipment is in file (based on object_mask)

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

    def __init__(self, equipment_json, object_mask=None, init_devices=False):

        # init
        self.equipment_json_path = equipment_json
        self.object_mask = object_mask

        # read equipment info from file
        with open(self.equipment_json_path, 'rb') as read_file:
            self.configuration = json.load(read_file)

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

        self._make_connections(init_devices=init_devices)
        return

    def _make_connections(self, init_devices=False):
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
                class_ = getattr(_import_module(device_info['definition']),
                                 device_info['object'])

                # get any kwargs for instanciation
                kwargs = device_info.get('kwargs', {})

                # creates instance named 'device_name' of class
                # 'device_info['object']'
                vars(self)[device_name] = class_(device_info['address'],
                                                 **kwargs)

                print(f'[CONNECTED] {device_name}')

                if ('init' in device_info) and init_devices:
                    # get the instance in question
                    inst = getattr(self, device_name)
                    initiaize_device(inst, device_info['init'])

            except (VisaIOError, ConnectionError) as error:

                print(f'[FAILED CONNECTION] {device_name}')

                if self.object_mask is not None:
                    # if the failed connection is for a piece of required
                    # equipment stop instantations
                    print(error)
                    raise ConnectionError(f"Failed connection: {device_name}")

            except (ModuleNotFoundError, AttributeError) as error:

                print(f'[UNSUPPORTED DEVICE] {device_name}\t{error}')

                if self.object_mask is not None:
                    # if the failed connection is for a piece of required
                    # equipment stop instantations
                    print(error)
                    raise ConnectionError(f"Failed connection: {device_name}")


def get_callable_instance_methods(instance):

    # get items in __dir__() that are callable (will include sub-classes)
    valid_cmds = filter(lambda meth: (callable(getattr(instance, meth))),
                        instance.__dir__())

    # filter out ignore dunders
    valid_cmds = filter(lambda m: ('__' not in m), valid_cmds)
    return list(valid_cmds)


def initiaize_device(inst, initialization_sequence):
    """
    initiaize_device(inst, initialization_sequence)

    inst: (obj) instance of object to initialize

    initialization_sequence: (list) list of lists containing valid methods of
                             "inst" with a dict of arguements to pass as kwargs

                             Will run in the order given
    ex: seq = [
               ["set_voltage", {"voltage": 0}],
               ["off", {}],
               ]

    Here "inst" has the two methods "set_voltage", and "off". The first of
    which requires the arguement voltage and the second of which has no args.
    """
    # get possible instance methods
    valid_cmds = get_callable_instance_methods(inst)

    # for cmd in initialization_sequence:
    for cmd, args in initialization_sequence:
        if cmd in valid_cmds:
            try:
                # call instance method with kwargs in passed dict
                getattr(inst, cmd)(**args)
                # getattr(inst, cmd)(**initialization_sequence[cmd])
            except TypeError as error:  # invalid kwargs
                print(f"\tError with initialization command\t{error}")

    return


# Testing Errors
class LowVinError(Exception):
    def __init__(self, message="vin measured below lower threshold"):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


class LowVoutError(Exception):
    def __init__(self, message="vout measured below lower threshold"):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)


if __name__ == "__main__":
    pass
