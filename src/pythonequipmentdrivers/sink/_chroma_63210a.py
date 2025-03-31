from ._chroma_63206a import Chroma_63206A


# Acts as an alias for the 10kW Version of the Chroma_63206A
class Chroma_63210A(Chroma_63206A):  # 10 kW
    """
    Chroma_63210A(address)

    address : str, address of the connected electronic load

    object for accessing basic functionallity of the Chroma_63210A DC load
    """

    def __init__(self, address: str, **kwargs) -> None:
        super().__init__(address, **kwargs)
