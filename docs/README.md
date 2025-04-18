# PythonEquipmentDrivers

## Overview

This module provide a straightforward interface to communicate with various electronics laboratory instruments. Instrument drivers are written to allow an engineer or technician to easily interface with their equipment without having to worry about constructing or parsing the command syntax for their particular instrument.

The driver classes included within are writen to handle the lower-level commands and queries used by the equipment and provide a simple interface in which specified command voltages/currents can be set using floating point numbers, modifying on/off state can be set/queried with boolean values, and parsing through string responses is not needed to interpret measurement results.

See the [Installation Guide](installation.md) for guidance on installing this module.

Afterward check out the [getting started page](getting_started.md) for code examples to help construct your first tests or the [guide for intermediate](intermediate_test_tips.md) programmers on how to improve your tests

## Module Structure

Often, model numbers for differnt types of equipment made by the same manufacturer can have very similar names.

For example:
 
> [!NOTE] 
> - Chroma 66204: 3-phase Powermeter
> - Chroma 63206A: DC Electronic Load
> - Chroma 62000P: DC Source

To help users navigate the collection of supported devices to find their instrument the module is constructed as a collection of sub-modules which contain different categories of equipment.

With this in place the various sub-modules, and their containing driver classes, can be accessed via the `.` operator.

For example, to accesss the driver class for the Chroma DC source referenced above
```python
import pythonequipmentdrivers as ped
source = ped.source.Chroma_62000P("USB0::0x1698::0x0837::002000000655::INSTR")
```

Currently the module has **8 such categories**:

> [!NOTE]
> * Voltage Sources: `pythonequipmentdrivers.source`
> * Electronic Loads: `pythonequipmentdrivers.sink`
> * Multimeters: `pythonequipmentdrivers.multimeter`
> * Oscilloscopes: `pythonequipmentdrivers.oscilloscope`
> * Function Generators: `pythonequipmentdrivers.functiongenerator`
> * Power Meters/Analyzers: `pythonequipmentdrivers.powermeter`
> * Network Analyzers: `pythonequipmentdrivers.networkanalyzer`
> * Temperature Controllers: `pythonequipmentdrivers.temperaturecontroller`

The submodules for each of the equipment categories and their contained drivers form a tree structure.
Most modern IDE possess some level of Intellisense providing some level of auto-complete, with such tools navigating the module tree structure to find the needed driver classes can be very easy.

```mermaid
flowchart TD;
    %%{init:{'flowchart':{'nodeSpacing': 20, 'rankSpacing': 100}}}%%
    classDef blue color:#4ab9b8,fill:#2a3939;
    classDef purple color:#9f7cf1,fill:#332f3c;
    classDef grey color:#262626,fill:#2a3939;

    pythonequipmentdrivers:::purple@{ shape: procs }-->source:::blue@{ shape: procs };
    source-->Chroma_62000P;
    source-->id1[...]@{ shape: procs };
    pythonequipmentdrivers--->sink:::blue@{ shape: procs };
    sink-->Kikusui_PLZ1004WH;
    sink-->id2[...]@{ shape: procs };
    pythonequipmentdrivers-->multimeter:::blue@{ shape: procs };
    multimeter-->id3[...]@{ shape: procs };
    pythonequipmentdrivers--->oscilloscope:::blue@{ shape: procs };
    oscilloscope-->Tektronix_DPO4xxx;
    oscilloscope-->Lecroy_WR8xxx;
    oscilloscope-->id4[...]@{ shape: procs };
    pythonequipmentdrivers-->functiongenerator:::blue@{ shape: procs };
    functiongenerator-->id5[...]@{ shape: procs };
    pythonequipmentdrivers--->powermeter:::blue@{ shape: procs };
    powermeter-->id6[...]@{ shape: procs };
    pythonequipmentdrivers-->networkanalyzer:::blue@{ shape: procs };
    networkanalyzer--->Bode100;
    pythonequipmentdrivers--->temperaturecontroller:::blue@{ shape: procs };
    temperaturecontroller-->Koolance_EXC900;
```


## Contributing
Would you like to contribue to the module? Whether its adding support for more instruments, creating utilities for testing, fixing bugs, or adding to the documentation your contributions are welcome.

Please visit the [how to contribute](.\how_to_contribute.md) doc to learn more.

