.. image:: https://github.com/maritime-labs/kahn/workflows/Tests/badge.svg
    :target: https://github.com/maritime-labs/kahn/actions?workflow=Tests

.. image:: https://codecov.io/gh/maritime-labs/kahn/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/maritime-labs/kahn

.. image:: https://pepy.tech/badge/kahn/month
    :target: https://pypi.org/project/kahn/

.. image:: https://img.shields.io/pypi/v/kahn.svg
    :target: https://pypi.org/project/kahn/

.. image:: https://img.shields.io/pypi/status/kahn.svg
    :target: https://pypi.org/project/kahn/

.. image:: https://img.shields.io/pypi/pyversions/kahn.svg
    :target: https://pypi.org/project/kahn/

.. image:: https://img.shields.io/pypi/l/kahn.svg
    :target: https://github.com/maritime-labs/kahn/blob/main/LICENSE

|

##################
Maritime Labs Kahn
##################


*****
About
*****

A light-weight and energy-efficient NMEA message broker.


.. note::

    Please note this is PRE-ALPHA quality software.


Features
========

- Read NMEA sentences from serial devices
- Submit NMEA sentences via UDP broadcast


*****
Setup
*****
::

    pip install --upgrade kahn

To install the latest development version from the repository, invoke::

    pip install --upgrade git+https://github.com/maritime-labs/kahn#egg=kahn


*****
Usage
*****

::

    # Read data from serial device and display on the terminal.
    kahn forward --source=serial:///dev/ttyUSB0 --target=file:///dev/stdout

    # Read data from serial device and forward to UDP broadcast.
    kahn forward --source=serial:///dev/ttyUSB0 --target=udp+broadcast+nmea0183://255.255.255.255:10110


**************
Other projects
**************

- ROS NMEA NavSat driver:
  https://github.com/ros-drivers/nmea_navsat_driver (`nmea_serial_driver`_, `nmea_socket_driver`_)


- Waterlinked ``nmeaoutput.py``
  `waterlinked-nmeaoutput.py`_


*******************
Project information
*******************

Contributions
=============

Any kind of contribution, feedback or patches are very much welcome! Just `create
an issue`_ or submit a patch if you think we should include a new feature, or to
report or fix a bug.

Development
===========

In order to setup a development environment on your workstation, please head over
to the `development sandbox`_ documentation. When you see the software tests succeed,
you should be ready to start hacking.

Resources
=========

- `Source code repository <https://github.com/maritime-labs/kahn>`_
- `Documentation <https://github.com/maritime-labs/kahn/blob/main/README.rst>`_
- `Python Package Index (PyPI) <https://pypi.org/project/kahn/>`_

License
=======

The project is licensed under the terms of the GNU AGPL license.



.. _create an issue: https://github.com/maritime-labs/kahn/issues
.. _development sandbox: https://github.com/maritime-labs/kahn/blob/main/doc/sandbox.rst
.. _nmea_serial_driver: https://github.com/ros-drivers/nmea_navsat_driver/blob/master/src/libnmea_navsat_driver/nodes/nmea_serial_driver.py
.. _nmea_socket_driver: https://github.com/ros-drivers/nmea_navsat_driver/blob/master/src/libnmea_navsat_driver/nodes/nmea_serial_driver.py
.. _waterlinked-nmeaoutput.py: https://github.com/waterlinked/examples/blob/master/nmeaoutput.py
