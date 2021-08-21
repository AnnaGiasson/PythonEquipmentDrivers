from pathlib import Path
import json
from pyvisa import VisaIOError
from . import errors
from importlib import import_module
from typing import Union, Tuple


def read_configuration(config_info: Union[str, Path, dict]) -> dict:
    """
    read_configuration(config_info)

    Reads configuration information and stores it as the instance variable
    "configuration".

    Args:
        config_info (str, Path, dict): Configuration information for the
            devices to connect to. Information can either be passed directly
            (dict) or can read from a file (str or Path-like).
    """

    if not isinstance(config_info, (str, Path, dict)):
        raise ValueError('Unsupported type for arguement "config_info"'
                         ' should a str/Path object to a JSON file or a'
                         ' dictionary')

    if isinstance(config_info, dict):
        return config_info

    # read equipment info from file
    with open(config_info, 'rb') as file:
        configuration = json.load(file)
    return configuration


def mask_resources(configuration: dict, resource_mask: set) -> dict:
    """
    mask_resources(configuration, resource_mask)

    Removes resources from 'configuration' that are not present in
    'resource_mask'.

    Args:
        configuration (dict): resource configuration information for the
            build_environment function.
        resource_mask (set): a set of resources that are to be kept in the
            configuration information.

    Returns:
        dict: configuration information with the items not present in
            resource_mask removed.
    """

    for resource in set(configuration).difference(resource_mask):
        configuration.pop(resource)

    return configuration


class Environment:
    """
    Environment

    Test environment Base-Class returned by build_environment

    Attributes of the Environment instance depend on the configuration passed
    into the build_environment
    """

    pass


# Update expected/assumed format of json file
def build_environment(configuration, **kwargs) -> Environment:
    """
    Class for handling the instantiation of generic sets of test equipment
    based on addressing data from file. Can blindly connect to all equipment in
    the provided file or dictionary (configuration) and can optionally verify
    that a specific set of equipment is in file (based on object_mask)

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

    If init_ is True than this object will search the JSON file for an
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

    In this example, If init is True and the device was successfully
    connected, this object will successively iterate through the array of
    command, arguement pairs; calling the commands listed using arguements (if
    any) provided. The commands listed must be valid methods of the device
    object, all arguements used will be passed as keyword arguements and
    therefore need to be named.
    """

    # read/process configuration information
    env_config = read_configuration(configuration)

    object_mask = set(kwargs.get('object_mask', {}))
    if object_mask:
        env_config = mask_resources(env_config, object_mask)

        if env_config.keys() != object_mask:
            missing = object_mask.difference(env_config.keys())
            raise errors.EnvironmentSetupError("Required Equipment Missing",
                                               missing)

    # build Environment instance
    env = Environment()
    for name, meta_info in env_config.items():

        try:
            # get object to instantate from it's source module
            Module = import_module(meta_info.pop('definition'))
            Resource = getattr(Module, meta_info.pop('object'))

            # special keyword for resource initialization, not passed as kwarg
            init_sequence = meta_info.pop('init', [])

            # create instance of Resource called 'name', any remaining items in
            # meta_info will be passed as kwargs
            setattr(env, name, Resource(**meta_info))

            if kwargs.get('verbose', True):
                print(f'[CONNECTED] {name}')

            if kwargs.get('init', False) and (init_sequence):
                # get the instance in question
                resource_instance = getattr(env, name)

                initiaize_device(resource_instance, init_sequence)
                if kwargs.get('verbose', True):
                    print('\tInitialzed')

        except (VisaIOError, ConnectionError) as error:

            if kwargs.get('verbose', True):
                print(f'[FAILED CONNECTION] {name}')

            if object_mask:  # failed resource connection is required
                raise errors.ResourceConnectionError(error)

        except (ModuleNotFoundError, AttributeError) as error:

            if kwargs.get('verbose', True):
                print(f'[UNSUPPORTED DEVICE] {name}\t{error}')

            if object_mask:  # unknown resource is required equipment
                raise errors.UnsupportedResourceError(error)

    return env


def get_callable_methods(instance) -> Tuple:
    """
    get_callable_methods(instance)

    Returns a tuple of all callable methods of an object or instance that
    are not "dunder"/"magic"/"private" methods

    Args:
        instance (object): object or instance of an object to get the
            callable methods of.

    Returns:
        tuple: collection of callable methods.
    """

    # get methods that are callable (will not include sub-classes)
    methods = instance.__dir__()
    cmds = filter(lambda method: (callable(getattr(instance, method))),
                  methods)

    # filter out ignore dunders
    cmds = filter(lambda func_name: ('__' not in func_name), cmds)
    return tuple(cmds)


def initiaize_device(instance, sequence) -> None:
    """
    initiaize_device(instance, sequence)

    Here "instance" has the two methods "set_voltage", and "off". The first of
    which requires the arguement voltage and the second of which has no args.

    Args:
        instance (object): object instance to initialize

        sequence (list): list of lists containing valid
            methods of "instance" with a dict of arguements to pass as kwargs.
            Will run in the order given.

    ex: sequence = [
                    ["set_voltage", {"voltage": 0}],
                    ["off", {}],
                ]
    """

    valid_cmds = get_callable_methods(instance)
    error_msg_template = '\tError with initialization command {}:\t{}'

    for method_name, method_kwargs in sequence:
        if method_name in valid_cmds:
            try:
                func = getattr(instance, method_name)
                func(**method_kwargs)

            except TypeError as error:  # invalid kwargs
                print(error_msg_template.format(method_name, error))
        else:
            print(error_msg_template.format(method_name, '"unknown method"'))
