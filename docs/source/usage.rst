
phyphox-py
=================

Use phyphox-py package  to get experimental data from your phyphox mobile app. 

This library allows you to access sensor data from the Phyphox app (see www.phyphox.org) directly in Python.


What is Phyphox?
-----------------
Phyphox is an open-source mobile application developed by RWTH Aachen University. Available on both Android and iOS, it provides access to the phone’s internal sensors for use in physics experiments.


Install 
-----------------
    .. _installation: 


To install phyphox-py, run the following command in your terminal:

``python3 -m pip install phyphox-py``

or in Windows

``python -m pip install phyphox-py``


Usage
-----------------


Basic Example
^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import phyphox
    import time

    my_phone = phyphox.Logger("192.168.0.12", 8080)
    my_phone.get_meta()
    print(my_phone)


Sample output (truncated):

.. code-block:: 

    accelerometer    
    Name : ICM20602 Accelerometer
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



Getting Experiment Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    my_phone.get_config()
    print(my_phone)

Sample output (truncated):

.. code-block::

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


Selecting Buffers for an Experiment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Buffer order is based on the export key.
To select gyr_time, gyrZ, and gyrX:

.. code-block::
    
    my_phone.buffer_needed([(0, (0, 3, 1))])

To check buffer selection:

.. code-block::
    
    my_phone.print_select_buffer()

Expected output:

.. code-block::
    
    Buffer  gyr_time
    Buffer  gyrZ
    Buffer  gyrX


Reading mobile sensor Data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Clear all buffer data, start data acquisition, wait for 2 seconds, then retrieve any data in a list:

.. code-block::

    my_phone.clear_data()
    my_phone.start()
    time.sleep(2)
    my_phone.read_buffers(mode_data=phyphox.BufferMode.FULL)
    last_tab = my_phone.get_last_buffer_read()
    te=(-last_tab1[0][0][0]+ last_tab1[0][0][-1])/(len(last_tab1[0][1])-1)
    print("data length {0} from Time {1} to {2}".format(len(last_tab1[0][1]), last_tab1[0][0][0], last_tab1[0][0][-1]))
    print("Hope next time {0}.".format(last_tab1[0][0][-1]+te))

Now wait 0.5 seconds and retrieve any new data:

.. code-block::

    time.sleep(0.5)
    my_phone.read_buffers()
    last_tab1 = my_phone.get_last_buffer_read()
    print("data length {0} from Time {1} to {2}".format(len(last_tab1[0][1]), last_tab1[0][0][0], last_tab1[0][0][-1]))
    print("Hope next time {0}.".format(last_tab1[0][0][-1]+te))

Stop sampling
^^^^^^^^^^^^^^^^^^

.. code-block::

    my_phone.stop()


Sample output

.. code-block::

    data length 380 from Time 0.095016596 to 1.9895734
    Hope next time 1.9945722306174143.
    data length 127 from Time 1.9945783 to 2.6244306
    Hope next time 2.6294294306174146.



Credits
-----------------

This library was developed by Laurent Berger with the help from phyphox forum and github issues.


Licence
-----------------

This library is released under the GNU Lesser General Public Licence v3.0.


Contact
-----------------

If you have questions or issues, feel free to open an issue on the GitHub repository.

