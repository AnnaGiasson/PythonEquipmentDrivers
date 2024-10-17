import json
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, Iterator, Tuple, Union
from enum import Enum

from pyvisa import VisaIOError

from .errors import ResourceConnectionError, UnsupportedResourceError

__all__ = ["ResourceCollection", "connect_resources", "initiaize_device"]


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
        raise ValueError(
            'Unsupported type for arguement "config_info"'
            " should a str/Path object to a JSON file or a"
            " dictionary"
        )

    if isinstance(config_info, dict):
        return config_info

    # read equipment info from file
    with open(config_info, "rb") as file:
        configuration = json.load(file)
    return configuration


class ResourceCollection(SimpleNamespace):
    """
    ResourceCollection

    Object containing a multiple resources as properties of the instance,
    returned by connect_resources. The specific names and values of the
    properties of a ResourceCollection instance depend on the configuration
    passed into the connect_resources function.
    """

    dmms: "DmmCollection"

    def __repr__(self) -> str:
        return super().__repr__().replace("namespace", self.__class__.__name__)

    def __iter__(self) -> Iterator:
        # allows intuitive iteration over the collection objects
        return iter(self.__dict__.values())

    def reset(self) -> None:
        """
        reset()

        Attempt to reset each resource in the collection.
        """
        for resource in self:
            try:
                resource.reset()
            except (VisaIOError, AttributeError):
                pass

    def set_local(self) -> None:
        """
        set_local()

        Attempt to reset each resource in the collection.
        """
        for resource in self:
            try:
                resource.set_local()
            except (VisaIOError, AttributeError):
                pass


class DmmCollection(ResourceCollection):
    """
    A slightly modified subclass of ResourceCollection to act as a container
    for multimeters and support some common methods.
    """

    def fetch_data(
        self, mapper: Dict[str, str] = None, only_mapped: bool = False
    ) -> Dict[str, float]:
        """
        fetch_data([mapper])

        Fetch measurements from all DMMs and pack them into a dict. The keys
        will be the DMM name by default. Optionally, a mapper can be specified
        to rename the dictonary keys.
        Args:
            mapper (dict, optional): rename keys of the collected data. Key
                should be the DMM name and the value should be the desired new
                name.
            only_mapped (bool, optional): If true only measurments of DMMs
                found in mapper will be returned.

        Returns:
            dict: dict of the fetched measurements
        """

        mapper = {} if mapper is None else mapper
        measurements = {}
        for name, resource in self.__dict__.items():

            if (name not in mapper) and only_mapped:
                continue

            new_name = mapper.get(name, name)

            try:
                measurements[new_name] = resource.fetch_data()
            except AttributeError as exc:
                raise AttributeError(
                    "All multimeter instances must have a " '"fetch_data" method'
                ) from exc

        return measurements

    def init(self) -> None:
        """
        init()

        Initialize (arm) the trigger of dmms where applicable.
        """
        for resource in self:
            try:
                resource.init()
            except (VisaIOError, AttributeError):
                pass

    def trigger(self) -> None:
        """
        trigger()

        Perform a basic sequential triggering of all devices.
        """
        for resource in self:
            try:
                resource.trigger()
            except (VisaIOError, AttributeError):
                pass


# Update expected/assumed format of json file


def connect_resources(config: Union[str, Path, dict], **kwargs) -> ResourceCollection:
    """
    connect_resources(config, **kwargs)

    Returns in instance of an ResourceCollection object; an object containing
    multiple equipment instances as instance attributes. This simplifies the
    overhead needed to instantiate connections to an entire set of devices.

    This can be useful when repeatedly connecting to the same set of devices,
    or for ensuring different sets of equipment are instantiated as
    ResourceCollection objects with the same attributes; allowing for easy
    reuse of the same test scripts using differents setups.

    The information required to configure the returned ResourceCollection
    object is provided using the 'config' arguement which is either a
    path to a file or a dictionary containing the required information.

    Args:
        config (Union[str, Path, dict]): [description]

    Kwargs:
        object_mask (set, optional): A set of attribute names specified in the
            config information to connect. If any of the specified
            devices fail to connect an exception will be raised. Defaults
            behavior is to connect everything present.
        verbose (bool, optional): If True, instantiation, status, and error
            information will be printed to the console. Defaults to True.
        init (bool, optional): Whether or not to run any initialization
            sequences (if present) after connecting to a device. Defaults to
            False.

    Returns:
        ResourceCollection: An object containing the device instances
            specified in 'config' as attributes.

    Examples:

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
                    "object": "Chroma_62000P",
                    "definition": "pythonequipmentdrivers.source",
                    "address": "USB0::0x1698::0x0837::002000000655::INSTR",
                    "kwargs": {}
                    },

    If this device is connected and availible this will create an instance of
    the Chroma_62000P at the provided address. The source is defined in the
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
                    "object": "Chroma_62000P",
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
    collection_config = read_configuration(config)

    object_mask = set(kwargs.get("object_mask", {}))
    if object_mask:

        # remove resources that are not needed
        for resource in set(collection_config).difference(object_mask):
            collection_config.pop(resource)

        # check if something is missing
        if collection_config.keys() != object_mask:
            missing = object_mask.difference(collection_config.keys())
            raise ResourceConnectionError("Required resource missing", missing)

    # build ResourceCollection instance
    resources = ResourceCollection()
    dmms = {}
    for name, meta_info in collection_config.items():

        try:
            # get object to instantate from it's source module
            module_name = meta_info.pop("definition")
            Module = import_module(module_name)
            Resource = getattr(Module, meta_info.pop("object"))

            # special keyword for resource initialization, not passed as kwarg
            init_sequence = meta_info.pop("init", [])

            # create instance of Resource called 'name', any remaining items in
            # meta_info will be passed as kwargs
            resource = Resource(**meta_info)
            setattr(resources, name, resource)

            if "multimeter" in module_name:
                dmms[name.replace("DMM", "")] = resource

            if kwargs.get("verbose", True):
                print(f"[CONNECTED] {name}")

            if kwargs.get("init", False) and (init_sequence):
                # get the instance in question
                resource_instance = getattr(resources, name)

                initiaize_device(resource_instance, init_sequence)
                if kwargs.get("verbose", True):
                    print("\tInitialzed")

        except (VisaIOError, ConnectionError) as error:

            if kwargs.get("verbose", True):
                print(f"[FAILED CONNECTION] {name}")

            if object_mask:  # failed resource connection is required
                raise ResourceConnectionError(error)

        except (ModuleNotFoundError, AttributeError) as error:

            if kwargs.get("verbose", True):
                print(f"[UNSUPPORTED DEVICE] {name}\t{error}")

            if object_mask:  # unknown resource is required equipment
                raise UnsupportedResourceError(error)

    if dmms:
        resources.dmms = DmmCollection(**dmms)

    return resources


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
    cmds = filter(lambda method: (callable(getattr(instance, method))), methods)

    # filter out ignore dunders
    cmds = filter(lambda func_name: ("__" not in func_name), cmds)
    return tuple(cmds)


def convert_to_enum(instance, value):
    """
    Attempt to convert a string value to an Enum value if a matching Enum exists in the instance.
    """
    for attr_name in dir(instance):
        attr = getattr(instance, attr_name)
        if isinstance(attr, type) and issubclass(attr, Enum):
            try:
                return attr[value.upper()]
            except KeyError:
                pass
    return value


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
    error_msg_template = "\tError with initialization command {}:\t{}"

    for method_name, method_kwargs in sequence:
        if method_name in valid_cmds:
            try:
                func = getattr(instance, method_name)
                # Convert string values to Enum values where possible
                converted_kwargs = {
                    key: convert_to_enum(instance, value) if isinstance(value, str) else value
                    for key, value in method_kwargs.items()
                }
                func(**converted_kwargs)

            except TypeError as error:  # invalid kwargs
                print(error_msg_template.format(method_name, error))
            except ValueError as error:  # invalid Enum value
                print(error_msg_template.format(method_name, error))
        else:
            print(error_msg_template.format(method_name, '"unknown method"'))
