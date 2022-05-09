from typing import Iterable, List, Optional, Tuple

import pyvisa

from pythonequipmentdrivers.errors import ResourceConnectionError

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
    identify_connections(resources=None, verbose=False)

    Attempts to connect to and query the specified Visa resource connections
    with an IDN query, which is a str identifing the resouce. If no resources
    are specified the function will attempt to find connected Visa resources to
    query. A list of resource (address, response) tuples is returned for those
    resources that respond to the query. The IDN query is a IEEE 488.2 Common
    Command and should be supported by all SCPI compatible instruments.

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

        except ResourceConnectionError:
            resource_id = "Failed to connect"
        except IOError:
            resource_id = "No response"
        except Exception:
            resource_id = f"Failed to instantiate resouce at: {addr}"
        else:
            visa_resources.append((addr, resource_id))
            del resource

        if verbose:
            print(f"\taddress: {addr}\n\tresponse: {resource_id}\n")

    return visa_resources


class VisaResource:
    """
    VisaResource

    Base class used to institate a Visa resource connection. The connection
    can be used to read/write data to the resource, including sending
    commands and querying information from the resource.

    Arg:
        address (str): Visa resource address to connect to

    Kwargs:
        open_timeout (float, optional): The time to wait (in seconds) when
            trying to connect to a resource before this operation returns an
            error; resolves to the nearest millisecond. Defaults to 1.0.
        timeout (float, optional): Timeout (in seconds) for I/O operations
            with the connected resource; resolves to the nearest millisecond.
            Defaults to 1.0.
        query_delay (float, optional): the time to wait after each write
            operation when performing a query in seconds. Defaults to 0.1
    """

    idn: str  # str: Description which uniquely identifies the instrument

    def __init__(self, address: str, **kwargs) -> None:
        self.address = address

        default_settings = {
            'open_timeout': int(1000*kwargs.get("open_timeout", 1.0)),  # ms
            'timeout': int(1000*kwargs.get("timeout", 1.0)),  # ms
            'delay': kwargs.get('query_delay', 0.1),  # s
        }

        try:
            self._resource = rm.open_resource(self.address, **default_settings)

            self.idn = self._resource.query("*IDN?").strip()
        except pyvisa.VisaIOError as error:
            raise IOError(
                f"Error communicating with resource at: {address}", error
                )
        except (pyvisa.Error) as error:
            raise ResourceConnectionError(
                f"Could not connect to resource at: {address}", error
                )

        self.timeout = int(kwargs.get("timeout", 1000))  # ms

    def clear_status(self, **kwargs) -> None:
        """
        clear_status(**kwargs)

        Clear Status Command

        Clears the instrument status byte by emptying the error queue and
        clearing all event registers. Also cancels any preceding *OPC command
        or query. The CLS command sent to the instrument is one of the
        IEEE 488.2 Common Commands and should be supported by all SCPI
        compatible instruments.
        """

        self._resource.write("*CLS", **kwargs)

    def reset(self, **kwargs) -> None:
        """
        reset()

        Reset Command

        Executes a device reset and cancels any pending *OPC command or query.
        The RST command sent to the instrument is one of the IEEE 488.2 Common
        Commands and should be supported by all SCPI compatible instruments.
        """

        self._resource.write("*RST", **kwargs)

    @property
    def timeout(self) -> int:
        """
        timeout

        Returns:
            int: Timeout (in milliseconds) for I/O operations with the
                connected resource.
        """

        return self._resource.timeout

    @timeout.setter
    def timeout(self, timeout: int) -> None:
        """
        timeout

        Args:
            timeout (int): timeout (in milliseconds) for I/O operations with
                the connected resource.
        """
        self._resource.timeout = int(timeout)  # ms

    def __del__(self) -> None:
        if hasattr(self, '_resource'):
            self._resource.close()

    def __repr__(self) -> str:

        def_str = f"{self.__class__.__name__}"
        def_str += f"({self.address}, timeout={self.timeout})"

        return def_str

    def __str__(self) -> str:
        return f"Rource ID: {self.idn}\nAddress: {self.address}"

    def write_resource(self, message: str, **kwargs) -> None:
        """
        write_resource(message, **kwargs)

        Writes data to the connected resource.

        Args:
            message (str): data to write to the connected resource, string of
                ascii characters
        """

        try:
            self._resource.write(message, **kwargs)
        except pyvisa.VisaIOError as error:
            raise IOError("Error communicating with resource\n", error)

    def query_resource(self, message: str, **kwargs) -> str:
        """
        query_raw_scpi(query, **kwargs)

        Writes data to the connected resource before reading data back from the
        resource. The duration of the delay between the write and read
        operations can be adjusted by the "query_delay" kwarg passed when
        instantiating a resource connection.

        Args:
            message (str): data to write to the connected resource before
                issueing a read, string of ascii characters
        Returns:
            str: data recieved from a connected resource, as string of
                ascii characters
        """

        try:
            response: str = self._resource.query(message, **kwargs)
            return response.strip()

        except pyvisa.VisaIOError as error:
            raise IOError("Error communicating with resource\n", error)

    def read_resource(self, **kwargs) -> str:
        """
        read_resource(**kwargs)

        Reads data back from the connected resource.

        Returns:
            str: data recieved from a connected resource, as string of
                ascii characters
        """

        try:
            response: str = self._resource.read(**kwargs)
            return response.strip()

        except pyvisa.VisaIOError as error:
            raise IOError("Error communicating with resource\n", error)
