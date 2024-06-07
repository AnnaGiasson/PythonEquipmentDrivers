from .keithley_2231a import Keithley_2231A


# acts as an alias of Keithley_2231A
class BKPrecision_9132B(Keithley_2231A):
    """
    BKPrecision_9132B(address)

    address : str, address of the connected power supply

    object for accessing basic functionallity of the B&K Precision DC supply
    """

    pass


if __name__ == "__main__":
    pass
