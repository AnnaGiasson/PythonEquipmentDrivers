from typing import Protocol
from .Agilent_6030A import Agilent_6030A
from .BKPrecision_9132B import BKPrecision_9132B
from .CaliforniaInstruments_CSW5550 import CaliforniaInstruments_CSW5550
from .Chroma_62000P import Chroma_62000P
from .Elgar_1750A import Elgar_1750A
from .Elgar_5250A import Elgar_5250A
from .HP_6632A import HP_6632A
from .Intepro_PSI9000 import Intepro_PSI9000
from .Keithley_2231A import Keithley_2231A
from .PPSC_3150AFX import PPSC_3150AFX
from .Sorensen_SGA import Sorensen_SGA


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


__all__ = ('BKPrecision_9132B',
           'CaliforniaInstruments_CSW5550',
           'Chroma_62000P',
           'Keithley_2231A',
           'Elgar_1750A',
           'Elgar_5250A',
           'Intepro_PSI9000',
           'PPSC_3150AFX',
           'HP_6632A',
           'Agilent_6030A',
           'Sorensen_SGA',
           'VoltageSource',
           )
