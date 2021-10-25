import pythonequipmentdrivers as ped
from time import sleep


# addresses of the equipment to connect, yours may vary
address = {'v_in_meter': 'USB0::0x2A8D::0x1301::MY59026778::INSTR',
           'v_out_meter': 'USB0::0x2A8D::0x1301::MY59026586::INSTR',
           'source': 'GPIB0::14::INSTR',
           'sink': 'GPIB0::3::INSTR',
           }


# connect to equipment
source = ped.source.Chroma_62012P(address['source'])
v_in_meter = ped.multimeter.Keysight_34461A(address['v_in_meter'])
v_out_meter = ped.multimeter.Keysight_34461A(address['v_out_meter'])
sink = ped.sink.Chroma_63206A(address['sink'])

# initialize equipment
source.set_voltage(0)
source.off()
source.set_current(10)

sink.off()
sink.set_mode('CC')
sink.set_current(0)

v_in_meter.set_mode('VDC')
v_out_meter.set_mode('VDC')

# conditions to test, test parameters, location to store data
v_in_conditions = [40, 48, 54, 60]
i_out_conditions = range(0, 120+1, 10)

measure_delay = 0.5
cooldown_delay = 5

data_path = 'C:\\top_sneaky\\'
data_file_name = 'test_data.csv'

# create file to store data using the utility function
ped.utility.log_data(data_path + data_file_name,
                     'v_in_set', 'i_out_set', 'v_in',         # columns names
                     'i_in', 'v_out', 'i_out', 'efficiency',  # of the data csv
                     init=True)

# run test
source.on()
sink.on()
for v_in_set in v_in_conditions:
    source.set_voltage(v_in_set)

    for i_out_set in i_out_conditions:
        print(f'Testing V_in = {v_in_set} V, I_out = {i_out_set} A')
        sink.set_current(i_out_set)

        sleep(measure_delay)
        measurement = [v_in_set, i_out_set,
                       v_in_meter.measure_voltage(),
                       source.measure_current(),
                       v_out_meter.measure_voltage(),
                       sink.measure_current()]

        sink.set_current(0)

        # calculations
        v_in, i_in, v_out, i_out = measurement[2:5+1]
        eff = (v_out*i_out)/(v_in*i_in)

        # add to data
        measurement.append(eff)

        # log measurements
        ped.utility.log_data(data_path + data_file_name, *measurement)

        sleep(cooldown_delay)  # cool down unit

# shutdown test setup
print('Test complete!')
source.set_voltage(0)
source.off()
sink.set_current(0)
sink.off()
