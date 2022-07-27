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
        open_timeout (float, optional): The time to wait (in milliseconds) when
            trying to connect to a resource before this operation returns an
            error. Defaults to 1.
        timeout (float, optional): Timeout (in seconds) for I/O operations
            with the connected resource. Defaults to 1.

    Returns:
        List[Tuple[str, str]]: list of resource (address, response) tuples is
            returned for those resources that respond to the query
    """

    # resources to query
    resource_addrs = find_visa_resources() if resources is None else resources

    # timeout config
    resource_config = {'open_timeout': 1, 'timeout': 1}  # defaults
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
        clear (bool): whether or not to clear the VISA resource's input/output
            buffers after instantiating the connection at class creation (see
            self.clear() for more details). Defaults to False.

    Kwargs:
        open_timeout (float, optional): The time to wait (in seconds) when
            trying to connect to a resource before this operation returns an
            error; resolves to the nearest millisecond. Defaults to 1.0.
        timeout (float, optional): Timeout (in seconds) for I/O operations
            with the connected resource; resolves to the nearest millisecond.
            Defaults to 1.0.
    """

    idn: str  # str: Description which uniquely identifies the instrument

    def __init__(self, address: str, clear: bool = False, **kwargs) -> None:
        self.address = address

        default_settings = {
            'open_timeout': int(1000*kwargs.get("open_timeout", 1.0)),  # ms
            'timeout': int(1000*kwargs.get("timeout", 1.0)),  # ms
        }

        try:
            self._resource = rm.open_resource(self.address, **default_settings)

            self.idn = self.query_resource("*IDN?")
        except (pyvisa.Error) as error:
            raise ResourceConnectionError(
                f"Could not connect to resource at: {address}", error
            )

        if clear:
            self.clear()

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

        self.write_resource("*CLS", **kwargs)

    def clear(self) -> None:
        """
        clear()

        The clear() operation clears the device input and output buffers. The
        bus-specific details are:

        Clear for 488.2 Instruments (GPIB, VXI, TCPIP, and USB)

        For a GPIB device, VISA sends the Selected Device Clear command.
        For a VXI device, VISA sends the Word Serial Clear command.
        For a USB device, VISA sends the INITIATE_CLEAR and CHECK_CLEAR_STATUS
        commands on the control pipe.
        Clear for Non-488.2 Instruments (Serial INSTR, TCPIP SOCKET, and USB
        RAW)

        For Serial INSTR sessions, VISA flushes (discards) the I/O output
        buffer, sends a break, and then flushes (discards) the I/O input
        buffer.
        For TCPIP SOCKET sessions, VISA flushes (discards) the I/O buffers.
        For USB RAW sessions, VISA resets the endpoints referred to by the
        attributes VI_ATTR_USB_BULK_IN_PIPE and VI_ATTR_USB_BULK_OUT_PIPE.
        Invoking viClear() also discards the read and write buffers used by the
        formatted I/O services for that session.
        """
        try:
            self._resource.clear()
        except pyvisa.VisaIOError as error:
            raise IOError("Error communicating with the resource\n", error)

    def reset(self, **kwargs) -> None:
        """
        reset()

        Reset Command

        Executes a device reset and cancels any pending *OPC command or query.
        The RST command sent to the instrument is one of the IEEE 488.2 Common
        Commands and should be supported by all SCPI compatible instruments.
        """

        self.write_resource("*RST", **kwargs)

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
        return f"Resource ID: {self.idn}\nAddress: {self.address}"

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
            raise IOError("Error communicating with the resource\n", error)

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
            raise IOError("Error communicating with the resource\n", error)

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
            raise IOError("Error communicating with the resource\n", error)

    def read_resource_raw(self, **kwargs) -> bytes:
        """
        read_resource_raw(**kwargs)

        Reads data back from the connected resource and returns it in its
        recieved raw byte format with no decoding. This can be useful for
        responses which do not use a simple ASCII or UTF-8 encoding.

        Returns:
            bytes: data recieved from a connected resource
        """

        try:
            response = self._resource.read_raw(**kwargs)
            return response

        except pyvisa.VisaIOError as error:
            raise IOError("Error communicating with the resource\n", error)


class GpibInterface(VisaResource):
    """
    Class for instantiation of the GPIB interface device (typically plugs into
    the computer's USB port). Since GPIB is a bus based interface layer,
    all instruments that utilize the bus can be accessed with group commands,
    if supported, to perform syncronized tasks.
    """

    def group_execute_trigger(self, *trigger_devices):
        """
        Sends the group execture trigger (GET) command to the devices specified

        *trigger_devices: Device instances to trigger
        """
        visa_resources = [n._resource for n in trigger_devices]
        self.instrument.group_execute_trigger(*visa_resources)
