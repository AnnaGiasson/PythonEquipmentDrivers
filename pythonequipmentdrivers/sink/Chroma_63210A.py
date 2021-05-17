from .Chroma_63206A import Chroma_63206A


class Chroma_63210A(Chroma_63206A):  # 10 kW
    """
    Chroma_63210A(address)

    address : str, address of the connected electronic load

    object for accessing basic functionallity of the Chroma_63210A DC load
    """

    def __init__(self, address, **kwargs):
        super().__init__(address, **kwargs)
        return None
