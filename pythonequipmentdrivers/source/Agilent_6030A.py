from .HP_6632A import HP_6632A


class Agilent_6030A(HP_6632A):
    """
    Agilent_6030A(address)

    address : str, address of the connected power supply

    object for accessing basic functionallity of the Agilent 6030A DC supply
    """

    def __init__(self, address, **kwargs):
        super().__init__(address, **kwargs)
        return None


if __name__ == '__main__':
    pass
