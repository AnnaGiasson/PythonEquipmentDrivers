from typing import Iterable, List, Optional, Tuple

import pyvisa
from pyvisa import VisaIOError

# Globals
rm = pyvisa.ResourceManager()


# Utility Functions
def find_visa_resources(query: str = "?*::INSTR") -> Tuple[str]:
    """
    find_visa_resources()

    Returns connected Visa resources addresses.

    Returns:
        Tuple[str]: Address strings for the connected Visa resources
    """
    return rm.list_resources(query=query)


def identify_visa_resources(resources: Optional[Iterable[str]] = None,
                            verbose: bool = False,
                            **kwargs) -> List[Tuple[str, str]]:
    """
    identify_connections(verbose=False)

    Queries the specified Visa resource connections with an IDN query, which is
    a str identifing the resouce. If no resources are specified the function
    will attempt to find connected Visa resources to query. A list of resource
    (address, response) tuples is returned for those resources that respond to
    the query. The IDN query is a IEEE 488.2 Common Command and should be
    supported by all SCPI compatible instruments.

    Args:
        resources (Iterable[str], optional): a list of Visa resource addresses
            (str) to identify, if None the find_visa_resources function will be
            internally called to get a list of Visa resources. Defaults to None
        verbose (bool, optional): if True resource addresses and idn strings
            are printed to screen as their query responses are recieved and an
            error message is printed for resources which could not be reached
            or didn't return a response. Defaults to False.
    Kwargs:
        open_timeout (int, optional): The time to wait (in milliseconds) when
            trying to connect to a resource before this operation returns an
            error. Defaults to 1000.
        timeout (int, optional): Timeout (in milliseconds) for I/O operations
            with the connected resource. Defaults to 1000.

    Returns:
        List[Tuple[str, str]]: list of resource (address, response) tuples is
            returned for those resources that respond to the query
    """

    # resources to query
    resource_addrs = find_visa_resources() if resources is None else resources

    # timeout config
    resource_config = {'open_timeout': 1000, 'timeout': 1000}  # defaults
    resource_config.update(kwargs)  # update based on any user input

    if verbose and (len(resource_addrs) > 0):
        print("Querying resource id's, may take a few seconds...")

    visa_resources: List[Tuple[str, str]] = []
    for addr in resource_addrs:
        try:
            resource = VisaResource(addr, **resource_config)
            resource_id = resource.idn

        except (pyvisa.Error, pyvisa.VisaIOError):
            resource_id = "No response/Failed to connect"
        else:
            visa_resources.append((addr, resource_id))
            del resource

        if verbose:
            print(f"\taddress: {addr}\n\tresponse: {resource_id}\n")

    return visa_resources


class VisaResource:
    def __init__(self, address: str, **kwargs) -> None:
        self.address = address
        open_timeout = int(kwargs.get("open_timeout", 1000))

        self.instrument = rm.open_resource(
            self.address, open_timeout=open_timeout
        )
        self.timeout = int(kwargs.get("timeout", 1000))  # ms

    @property
    def idn(self) -> str:
        """
        idn

        Identify Query

        Returns a string that uniquely identifies the instrument. The IDN query
        sent to the instrument is one of the IEEE 488.2 Common Commands and
        should be supported by all SCPI compatible instruments.

        Returns:
            str: uniquely identifies the instrument
        """

        return self.instrument.query("*IDN?").strip()

    def cls(self, **kwargs) -> None:
        """
        cls(**kwargs)

        Clear Status Command

        Clears the instrument status byte by emptying the error queue and
        clearing all event registers. Also cancels any preceding *OPC command
        or query. The CLS command sent to the instrument is one of the
        IEEE 488.2 Common Commands and should be supported by all SCPI
        compatible instruments.

        Returns:
            None
        """

        self.instrument.write("*CLS", **kwargs)

    def rst(self, **kwargs) -> None:
        """
        rst()

        Reset Command

        Executes a device reset and cancels any pending *OPC command or query.
        The RST command sent to the instrument is one of the IEEE 488.2 Common
        Commands and should be supported by all SCPI compatible instruments.
        """

        self.instrument.write("*RST", **kwargs)

    @property
    def timeout(self) -> int:
        return self.instrument.timeout

    @timeout.setter
    def timeout(self, timeout: int) -> None:
        self.instrument.timeout = int(timeout)  # ms

    def __del__(self) -> None:
        try:
            # if connection has been estabilished terminate it
            if hasattr(self, "instrument"):
                self.instrument.close()
        except VisaIOError:
            # if connection not connection has been estabilished (such as if an
            # error is throw in __init__) do nothing
            pass

    def __repr__(self) -> str:

        def_str = f"{self.__class__.__name__}"
        def_str += f"({self.address}, timeout={self.timeout})"

        return def_str

    def __str__(self) -> str:
        return f"Instrument ID: {self.idn}\nAddress: {self.address}"

    def __eq__(self, obj) -> bool:

        """
        __eq__(obj)

        Args:
            obj (object): object to compare

        Returns:
            bool: True if the objects are both instances of VisaResource
                (or any class that inherits from VisaResource) and have the
                same address and class name. Otherwise False.
        """

        if not isinstance(obj, VisaResource):
            return False

        if not (self.__class__.__name__ == obj.__class__.__name__):
            return False

        if not (self.address == obj.address):
            return False
        return True

    def __ne__(self, obj) -> bool:
        """
        __ne__(obj)

        Args:
            obj (object): object to compare

        Returns:
            bool: whether or not to object are not equal. Defined as the
                inverse of the result from __eq__
        """

        return not self.__eq__(obj)

    def send_raw_scpi(self, command_str: str, **kwargs) -> None:
        """
        send_raw_scpi(command_str, **kwargs)

        Pass-through function which forwards the contents of 'command_str' to
        the device. This function is intended to be used for API calls for
        functionally that is not currently supported. Can only be used for
        commands, will not return queries.

        Args:
            command_str: string, scpi command to be passed through to the
                device.
        """

        self.instrument.write(str(command_str), **kwargs)

    def query_raw_scpi(self, query_str: str, **kwargs) -> str:
        """
        query_raw_scpi(query, **kwargs)

        Pass-through function which forwards the contents of 'query_str' to
        the device, returning the response without any processing. This
        function is intended to be used for API calls for functionally that is
        not currently supported. Only to be used for queries.

        Args:
            query_str: string, scpi query to be passed through to the device.

        """

        return self.instrument.query(str(query_str), **kwargs)

    def read_raw_scpi(self, **kwargs) -> str:
        """
        read_raw_scpi(**kwargs)

        Pass-through function which reads the device, returning the response
        without any processing. This function is intended to be used for API
        calls for functionally that is not currently supported.
        Only to be used for read.
        """

        return self.instrument.read(**kwargs)
