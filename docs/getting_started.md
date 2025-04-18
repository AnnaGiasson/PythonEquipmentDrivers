# Getting Started
[Go Back](README.md)

Make sure before proceeding ensure that pythonequipmentdrivers has been successfully [installed](installation.md).

##  Connecting to a Device

To connect to a device you need to know 2 things:
- The device driver class you wish to use
- The address of the device

Aside from the Bode100 Network Analyzer, all drivers within pythonequipmentdrivers are VISA (Virtual instrument software architecture) devices. This is a common programming interface syntax common across many device manufacturers. This protocol specifies the format of the data transmitted but not the physical interfaces used.

Depending on the type of connection the device supports the address could refer to a USB address, COM port, GPIB address, or Ethernet address.

PythonEquipmentDrivers comes with a built in utility for identifing (most) connected VISA instruments if the addresses are not known.

```python
import pythonequipmentdrivers as ped
connected_devices = ped.identify_visa_resources()
```
This function will return a dictionary whose key-value pairs are the addresses and their responses to an identification (IDN) query.

Alternatively, by passing `True` to the optional `verbose`, this function will print out a more human-friendly version of the availible device connections. This includes information about any other devices connected to the computer that were queried but didn't response with an IDN response (such as a USB mouse).

```python
ped.identify_visa_resources(verbose=True)
```

To create a connection to an instrument supported by this library it's respective class needs to be instantiated with the address of the instrument you wish to control.
For example, to control a Chroma 62012P DC source on a GPIB interface at address 14:
```python
import pythonequipmentdrivers as ped
source = ped.source.Chroma_62000P('GPIB0::14::INSTR')
```
The driver instance will then manage the device connection, including closing the connection upon the deletion of the instance or termination of the program.

## Sending Commands and Querying Results
With a driver instance created, the various features of the instrument can be access through its instance methods.
```python
import pythonequipmentdrivers as ped
from time import sleep

source = ped.source.Chroma_62000P('GPIB0::14::INSTR')

# set voltage and query local measurement
source.set_voltage(48)
sleep(0.5)
print(source.measure_voltage())  # 47.98645785

# read state of output relay 
print(source.get_state())  # True

# turn off output
source.set_state(False)
print(source.get_state())  # False 
```

# Writing Test Sequences
By instantiating multiple instruments simple tests can be scripted to automatically runing the bench equipment through a sequence of test conditions and measurements.

The example below illustrates and simple test to measure the efficiency of a power converter over its input voltage range and output current range.

This test:
- Connects to multiple instruments at once
- Configures the equipment for the test
- Biases the power converter to different operating conditions
  - Measures the input/output voltage and current
  - Calculates the efficiency and prints it to the screen
- Shuts down the setup after the test completes

While the method used here to measure efficiency is not a very accurate method it serves to demonstrate a realistic use case of this module. Automating what could otherwise be a very tedious measurement.

[Link to Source Code](..\examples\super_simple_matrix_test\simple_matrix.py)
```python
import pythonequipmentdrivers as ped
from time import sleep

# conditions to test
v_in_conditions = (40, 48, 54, 60)
i_out_conditions = (0, 20, 40, 60, 80, 100, 120)
measure_delay = 0.5  # delay between setting v_in/i_out
                     # and measuring (allowing for stabilization)

# connect to equipment
source = ped.source.Chroma_62000P('GPIB0::14::INSTR')
v_in_meter = ped.multimeter.Keysight_34461A('USB0::0x2A8D::0x1301::MY59026778::INSTR')
v_out_meter = ped.multimeter.Keysight_34461A('USB0::0x2A8D::0x1301::MY59026586::INSTR')
e_load = ped.sink.Chroma_63206A('GPIB0::3::INSTR')

# initialize
source.off()
source.set_voltage(0)
source.set_current(10)

e_load.off()
e_load.set_mode('CC')
e_load.set_current(0)

v_in_meter.set_mode('VDC')
v_out_meter.set_mode('VDC')

# run test
data = [['v_in_set', 'i_out_set', 'v_in', 'i_in', 'v_out', 'i_out', 'efficiency']]
source.on()
e_load.on()

for v_in_set in v_in_conditions:
    source.set_voltage(v_in_set)
    for i_out_set in i_out_conditions:
        print(f'Testing V_in = {v_in_set} V, I_out = {i_out_set} A')

        e_load.set_current(i_out_set)
        sleep(measure_delay)
        
        v_in_measure = v_in_meter.measure_voltage()
        i_in_measure = source.measure_current()
        v_out_measure = v_out_meter.measure_voltage()
        i_out_measure = e_load.measure_current()

        # calculations
        eff = (v_out_measure*i_out_measure)/(v_in_measure*i_in_measure)

        print(f'Efficiency = {eff*100} %')

# shutdown test setup
source.set_voltage(0)
source.off()
e_load.set_current(0)
e_load.off()
print('Test complete!')
```

A script such as this is suitable for simple one-off tests. But for advice on managing data, more advanced tests, or for writing more easily reusable code see the guide on [Intermediate Test Tips](intermediate_test_tips.md).
