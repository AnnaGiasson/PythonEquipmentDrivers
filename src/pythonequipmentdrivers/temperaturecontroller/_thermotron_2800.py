
"""
Created on Wed Feb 10 11:53:18 2021

@author: DS_TestStation
"""

from ..core import VisaResource


class Thermotron2800(VisaResource):
    def __init__(self, address: str, **kwargs):
        super().__init__(address, **kwargs)
        self.write_resource("LKS 1") # lock keyboard - should happen automatically, but we'll assert anyway... =)

    def RunChamber(self) -> None:
        self.write_resource("RM")     # Enter "Run Manual" state to follow single set point
    
    def StopChamber(self) -> None:
        self.write_resource("S")      # Stop chamber output
    
    def SetTemp(self, temp:float) -> None:
        self.write_resource("LTS " + f'{temp:.1f}')
    
    def GetTempSetpoint(self) -> float:
        return self._resource.query_ascii_values("DTS")[-1]
    
    def GetTempMeasurement(self) -> float:
        return self._resource.query_ascii_values("DTV")[-1]
        
    def Close(self) -> None:
        self.write_resource("LKS 0")  # unlock keyboard before closing session
        self.close_resource()
        