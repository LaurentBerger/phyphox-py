# phyphox-py
Use phyphox-py package  to get experimental data from your phyphox phone app. 

The purpose of this library is to get sensor data  from the phyphox app (see www.phyphox.org) in python.

## Concept of phyphox

Phyphox is an open source app that has been developed at the RWTH Aachen University. It is available on Android and iOS and primarily aims at making the phone's sensors available for physics experiments. 

## Installation

To install phyphox-py run this command in your terminal :

```python3 -m pip install phyphox-py```

or in Windows

```python -m pip install phyphox-py```

## Usage

To use phyphox-py from command line:
```
import phyphox
import time

my_phone = phyphox.PhyphoxLogger("192.168.0.12", 8080)
my_phone = phyphox.PhyphoxLogger("192.168.0.12", 8080)
my_phone.get_meta()
print(my_phone)
accelerometer    Name : ICM20602 Accelerometer
Vendor : InvenSense
Range : 78.45346
Resolution : 0.0011901855
MinDelay : 5000
MaxDelay : 1000000
Power : 0.325
Version : 20170509
...

version : 1.2.0
build : 1020009
fileFormat : 1.19
...
camera2api : [{"id":"0","facing":"LENS_FACING_BACK","hardwareLevel":"HARDWARE_LEVEL_3","capabilities":["CAPABILIT ...
camera2apiFull : [{"id":"0","facing":"LENS_FACING_BACK","hardwareLevel":"HARDWARE_LEVEL_3","capabilities":["CAPABILIT ...

```
We can get experiment configuration too:
```
my_phone.get_config()
print(my_phone)
crc32 : 44c5dc97
title : Gyroscope (rotation rate)
localTitle : Gyroscope (vitesse angulaire)
category : Raw Sensors
localCategory : Capteurs
buffers : [{'name': 'gyrX', 'size': 0}, {'name': 'gyrY', 'size': 0}, {'name': 'gyrZ', 'size': 0}, {'name': 'gyr', 'size': 0}, {'name': 'gyr_time', 'size': 0}]
inputs : [{'source': 'gyroscope', 'outputs': [{'x': 'gyrX'}, {'y': 'gyrY'}, {'z': 'gyrZ'}, {'abs': 'gyr'}, {'t': 'gyr_time'}]}]
export : [{'set': 'Raw Data', 'sources': [{'label': 'Time (s)', 'buffer': 'gyr_time'}, {'label': 'Gyroscope x (rad/s)', 'buffer': 'gyrX'}, {'label': 'Gyroscope y (rad/s)', 'buffer': 'gyrY'}, {'label': 'Gyroscope z (rad/s)', 'buffer': 'gyrZ'}, {'label': 'Absolute (rad/s)', 'buffer': 'gyr'}]}]

accelerometer    Name : ICM20602 Accelerometer
...
camera2api : [{"id":"0","facing":"LENS_FACING_BACK","hardwareLevel":"HARDWARE_LEVEL_3","capabilities":["CAPABILIT ...
camera2apiFull : [{"id":"0","facing":"LENS_FACING_BACK","hardwareLevel":"HARDWARE_LEVEL_3","capabilities":["CAPABILIT ...
```
Now we can select buffers in each experiment. Buffer order is in export key. To select gyr_time, gyrZ and gyrX :
```
my_phone.buffer_needed([(0, (0, 3, 1))])
True
```
We can check if everything is fine :
```
my_phone.print_select_buffer()
Buffer  gyr_time
Buffer  gyrZ
Buffer  gyrX
```
Now we clear all buffers data, start sampling, wait 2 seconds and read all data available since experiment started, retreive all last buffers read in a list:
```
my_phone.clear_data()
my_phone.start()
time.sleep(2)
my_phone.read_buffers(mode_data=phyphox.BufferMode.FULL)
last_tab = my_phone.get_last_buffer_read()
te=(-last_tab1[0][0][0]+ last_tab1[0][0][-1])/(len(last_tab1[0][1])-1)
print("data length {0} from Time {1} to {2}".format(len(last_tab1[0][1]), last_tab1[0][0][0], last_tab1[0][0][-1]))
print("Hope next time {0}.".format(last_tab1[0][0][-1]+te))

```
Now we can wait 1 seconds and retrieve all new data:
```
time.sleep(0.5)
my_phone.read_buffers()
last_tab1 = my_phone.get_last_buffer_read()
print("data length {0} from Time {1} to {2}".format(len(last_tab1[0][1]), last_tab1[0][0][0], last_tab1[0][0][-1]))
print("Hope next time {0}.".format(last_tab1[0][0][-1]+te))
```
To stop sampling:
my_phone.stop()

Results are 
data length 380 from Time 0.095016596 to 1.9895734
Hope next time 1.9945722306174143.
data length 127 from Time 1.9945783 to 2.6244306
Hope next time 2.6294294306174146.
## Credits

This library has been developed by Laurent Berger with the help of phyphox forum and github issue.

## Licence

This library is released under the GNU Lesser General Public Licence v3.0.

## Contact

Contact me any time create an issue.

