# PythonEquipmentDrivers
The purpose of this module is to provide a collection of classes for controlling various electronics laboratory instruments.
The library of supported devices is categorized into 8 sub-categories that are accessed as sub-modules:
* Voltage Sources (`pythonequipmentdrivers.source`)
* Electronic Loads (`pythonequipmentdrivers.sink`)
* Multimeters (`pythonequipmentdrivers.multimeter`)
* Oscilloscopes (`pythonequipmentdrivers.oscilloscope`)
* Function Generators (`pythonequipmentdrivers.functiongenerator`)
* Power Meters/Analyzers (`pythonequipmentdrivers.powermeter`)
* Network Analyzers (`pythonequipmentdrivers.networkanalyzer`)
* Temperature Controllers (`pythonequipmentdrivers.temperaturecontroller`)

### Installation
This library utilizes the NI-VISA (or compatible) hardware drivers, this should be installed prior to using this libray.
To install this module download or clone this repository and install using pip with 
`pip install .` or
`C:\\{path_to_python}\python.exe -m pip install .` if multiple Python installations exist.

Additionally the package can be installed in development mode with the `-e/--editable` flag e.g `pip install -e .` More details on development mode can be found at https://setuptools.pypa.io/en/latest/userguide/development_mode.html 

For additional help with installation help you can contact the module author Anna Giasson (AnnaGraceGiasson@GMail.com)

### Examples
To create a connection to an instrument supported by this library it's respective class needs to be instantiated with the address of the instrument you wish to control.
For example, to control a Chroma 62012P voltage source on a GPIB interface at address 14:
```python
import pythonequipmentdrivers as ped
source = ped.source.Chroma_62000P('GPIB0::14::INSTR')
```
With this instance, various features of the instrument can be access through its methods.
```python
source.set_voltage(48)
print(source.measure_voltage())
# 47.98645785
```
PythonEquipmentDrivers comes with a built in utility for identifing (most) connected instruments if the addresses are not known.
```python
import pythonequipmentdrivers as ped
ped.identify_visa_resources()
```
By instantiating multiple instruments simple tests can be scripted to automatically log data for a "device under test" (DUT)
Here is an example test which measures the efficiency of a power converter over multiple operating points and logs the resulting data to file:
```python
import pythonequipmentdrivers as ped
from time import sleep

# connect to equipment
source = ped.source.Chroma_62000P('GPIB0::14::INSTR')
v_in_meter = ped.multimeter.Keysight_34461A('USB0::0x2A8D::0x1301::MY59026778::INSTR')
v_out_meter = ped.multimeter.Keysight_34461A('USB0::0x2A8D::0x1301::MY59026586::INSTR')
sink = ped.sink.Chroma_63206A('GPIB0::3::INSTR')

# initialize
source.set_voltage(0)
source.off()
source.set_current(10)

sink.off()
sink.set_mode('CC')
sink.set_current(0)

v_in_meter.set_mode('VDC')
v_out_meter.set_mode('VDC')

# conditions to test
v_in_conditions = (40, 48, 54, 60)
i_out_conditions = range(0, 120+1, 10)
measure_delay = 0.5
cooldown_delay = 5
data_file_name = 'C:\\top_sneaky\\my_first_test.csv'

# run test
data = [['v_in_set', 'i_out_set', 'v_in', 'i_in', 'v_out', 'i_out', 'efficiency']]
source.on()
sink.on()
for v_in_set in v_in_conditions:
    source.set_voltage(v_in_set)
    for i_out_set in i_out_conditions:
        print(f'Testing V_in = {v_in_set} V, I_out = {i_out_set} A')
        sink.set_current(i_out_set)
        sleep(measure_delay)
        datum = [v_in_set,
                 i_out_set,
                 v_in_meter.measure_voltage(),
                 source.measure_current(),
                 v_out_meter.measure_voltage(),
                 sink.measure_current()]

        sink.set_current(0)

        # calculations
        eff = (datum[4]*datum[5])/(datum[2]*datum[3])
        # add to data
        datum.append(eff)
        data.append(datum)

        sleep(cooldown_delay) # cool down unit

# shutdown test setup
print('Test complete!')
source.set_voltage(0)
source.off()
sink.set_current(0)
sink.off()

# log data
with open(data_file_name, "w") as file:
    for row in data:
        print(*row, sep=',', end='\n')
print(f'data saved to: {data_file_name}')
```

See the examples folder within this repository for additional examples.