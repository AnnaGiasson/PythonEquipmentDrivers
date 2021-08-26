import pyvisa
from pyvisa import VisaIOError
from typing import List, Tuple


# Globals
rm = pyvisa.ResourceManager()


# Utility Functions
def get_devices_addresses() -> Tuple[str]:
    """
    returns a list of the addresses of peripherals connected to the computer
    """
    return rm.list_resources()


def identify_devices(verbose: bool = False) -> List[Tuple[str]]:
    """
    identify_connections(verbose=False)

    Queries devices connected to the machine for with and IDN query, return
    those with a valid response response. The IDN query is a IEEE 488.2 Common
    Command and should be supported by all SCPI compatible instruments.

    Args:
        verbose (bool, optional): if True device addresses and responses, or,
            lack thereof are printed to stdout as they are queried. Defaults to
            False.

    Returns:
        List[Tuple[str]]: A list of tuples containing address, IDN response
            pairs for each detected device that responded to the query with a
            valid response.
    """

    scpi_devices = []
    for address in rm.list_resources():
        try:
            device = Scpi_Instrument(address, open_timeout=100,
                                     timeout=500)
            scpi_devices.append((address, device.idn))
            if verbose:
                print("address: {}\nresponse: {}\n".format(*scpi_devices[-1]))

        except pyvisa.Error:
            if verbose:
                print(f"Invalid IDN query reponse from address {address}\n")
        finally:
            del(device)

    return scpi_devices


class Scpi_Instrument():

    def __init__(self, address: str, **kwargs) -> None:
        self.address = address
        open_timeout = int(kwargs.get('open_timeout', 1000))

        self.instrument = rm.open_resource(self.address,
                                           open_timeout=open_timeout)
        self.timeout = int(kwargs.get('timeout', 1000))  # ms

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

        return self.instrument.query('*IDN?')

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

        self.instrument.write('*CLS', **kwargs)

    def rst(self, **kwargs) -> None:
        """
        rst()

        Reset Command

        Executes a device reset and cancels any pending *OPC command or query.
        The RST command sent to the instrument is one of the IEEE 488.2 Common
        Commands and should be supported by all SCPI compatible instruments.
        """

        self.instrument.write('*RST', **kwargs)

    @property
    def timeout(self) -> int:
        return self.instrument.timeout

    @timeout.setter
    def timeout(self, timeout: int) -> None:
        self.instrument.timeout = int(timeout)  # ms

    def __del__(self) -> None:
        try:
            # if connection has been estabilished terminate it
            if hasattr(self, 'instrument'):
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
        return f'Instrument ID: {self.idn}\nAddress: {self.address}'

    def __eq__(self, obj) -> bool:

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


if __name__ == "__main__":
    pass
