from .HP_6632A import HP_6632A as _HP_6632A


class Agilent_6030A(_HP_6632A):
    """
    Agilent_6030A(address)

    address : str, address of the connected power supply

    object for accessing basic functionallity of the Agilent 6030A DC supply
    """

    def __init__(self, address):
        super().__init__(address)
        return


if __name__ == '__main__':
    pass
