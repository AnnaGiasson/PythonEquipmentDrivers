from typing import Protocol

from .agilent_6030a import Agilent_6030A
from .bkprecision_9132b import BKPrecision_9132B
from .californiainstruments_csw5550 import CaliforniaInstruments_CSW5550
from .chroma_62000p import Chroma_62000P
from .elgar_1750a import Elgar_1750A
from .elgar_5250a import Elgar_5250A
from .hp_6632a import HP_6632A
from .intepro_psi9000 import Intepro_PSI9000
from .keithley_2231a import Keithley_2231A
from .ppsc_3150afx import PPSC_3150AFX
from .sorensen_sga import Sorensen_SGA


class VoltageSource(Protocol):
    """
    A protocol defining the minimum functionallity of a voltage source. Can be
    used for type-hinting, intellisense, or other code-completion tools in more
    complicated automation applications.
    """

    def set_voltage(self, voltage: float) -> None:
        """sets output level of the voltage source"""

    def get_voltage(self) -> float:
        """returns the output level of the voltage source"""

    def set_state(self, state: bool) -> None:
        """sets the state of the source's output"""

    def get_state(self) -> bool:
        """returns the state of the source's output"""

    def on(self) -> None:
        """sets the state of the source's output to active"""

    def off(self) -> None:
        """sets the state of the source's output to inactive"""

    def toggle(self) -> None:
        """reverses the state of the source's output"""


__all__ = (
    "BKPrecision_9132B",
    "CaliforniaInstruments_CSW5550",
    "Chroma_62000P",
    "Keithley_2231A",
    "Elgar_1750A",
    "Elgar_5250A",
    "Intepro_PSI9000",
    "PPSC_3150AFX",
    "HP_6632A",
    "Agilent_6030A",
    "Sorensen_SGA",
    "VoltageSource",
)