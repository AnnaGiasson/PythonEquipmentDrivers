from typing import Protocol

from ._chroma_6310 import Chroma_6310
from ._chroma_63206a import Chroma_63206A
from ._chroma_63210a import Chroma_63210A
from ._chroma_63600 import Chroma_63600
from ._kikusui_plz1004wh import Kikusui_PLZ1004WH


class ElectronicLoad(Protocol):
    """
    A protocol defining the minimum functionallity of an electronic load. Can be
    used for type-hinting, intellisense, or other code-completion tools in more
    complicated automation applications.
    """

    def set_current(self, current: float) -> None:
        """sets output level of the electronic load"""

    def get_current(self) -> float:
        """returns the output level of the electronic load"""

    def set_state(self, state: bool) -> None:
        """sets the state of the electronic load's output"""

    def get_state(self) -> bool:
        """returns the state of the electronic load's output"""

    def on(self) -> None:
        """sets the state of the electronic load's output to active"""

    def off(self) -> None:
        """sets the state of the electronic load's output to inactive"""

    def toggle(self) -> None:
        """reverses the state of the electronic load's output"""


__all__ = [
    "Chroma_6310",
    "Chroma_63206A",
    "Chroma_63210A",
    "Chroma_63600",
    "Kikusui_PLZ1004WH",
]
