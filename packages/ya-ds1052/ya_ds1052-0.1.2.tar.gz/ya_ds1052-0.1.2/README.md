# Remote control of Rigol DS1000E/D series digital oscilloscopes.

## Example usage:

    >>> import matplotlib.pyplot as plt
    >>> from ds1052 import DS1052, PointsMode
    >>> with DS1052() as dso:
    ...     # Acquire the waveform of channel 1 in "normal" points mode
    ...     # which returns 600 data points.
    ...     waveform = dso.read_waveforms([1], PointsMode.normal)[0]
    ...
    >>> # Vertical scale and offset.
    >>> waveform.v_scale
    1.0
    >>> waveform.v_offset
    0.52
    >>> # Timebase scale and offset.
    >>> waveform.tb_scale
    0.0005
    >>> waveform.tb_offset
    0.0
    >>> # waveform.t is a numpy array with time axis values. 0 is the trigger
    >>> # time; waveform.v is a numpy array with the voltage values.
    >>> plt.plot(waveform.t, waveform.v)
    [<matplotlib.lines.Line2D object at 0x7f8b8e075640>]
    >>> plt.show()
    >>>

Most settings of the DS1000 oscilloscopes are available as properties:

    >>> import ds1052
    >>> dso = ds1052.DS1052()
    >>> dso.open()
    >>> dso.timebase_scale
    0.0005
    >>> dso.timebase_offset
    0.0
    >>> dso.trigger.edge.level
    1.48
    >>> dso.trigger.edge.coupling
    <TriggerCoupling.dc: 'DC'>
    >>> dso.channel[2].coupling
    <ChannelCoupling.dc: 'DC'>
    >>> dso.channel[2].scale
    1.0
    >>> dso.channel[2].offset
    -3.52
    >>> dso.channel[2].scale = 0.6
    >>> dso.channel[2].scale
    0.6

    >>> # Measurement values are returned as tuples (value, qualifier).
    >>> dso.channel[1].voltage_rms
    (2.14, <MeasurementQualifier.value: ('value',)>)
    >>> # MeasurementQualifier.less_than indicates that the DSO could make
    >>> # a measurement with sufficient precision. (Settings of this example:
    >>> # Channel 1 input is a 1kHz square wave; the sampling rate is 500k/s.
    >>> # 500 samples per period are clearly not enough to measure the rise
    >>> # time.)
    >>> dso.channel[1].rise_time
    (3e-05, <MeasurementQualifier.less_than: 'less than'>)

    >>> # Finally, DS1052.close() should be called to unlock the keyboard.
    >>> # (If DS1052 is used as a context manager, the close() call is made
    >>> # when the context is left.)
    >>> dso.close()

## Aims of ya_ds1052

1. Provide an easy to use remote control interface to DS1000E/D oscilloscopes.

2. Provide, where possible, workarounds for the many quirks of the DS1000E/D,
which have a, well, unconventional SCPI implementation.
The most glaring problem is that the DSOs do not implement the command `*OPC?`
(operation complete command). This makes it sometimes difficult, but at
least cumbersome, to figure out when the change of a setting is eventually
applied. This library tries, where possible, to implement checks if such changes
have been fully applied and when an operation can be performed without
slowing down the performance too drastically. (Rigol's own Ultrascope
software sends SCPI commands with a minimum time distance of 0.12 seconds.
This makes some operations like a read-out of all settings really slow and
does not seems to be necessary.)

## Installation:

    pip install ya_ds1052

This installs the additional libraries `numpy` and `aenum`.

One important dependency must be installed manually in many cases: An
implementation of the USBTMC layer. `ya_ds1052` works with three USBTMC
drivers:

- The `usbtmc` driver of the Linux kernel. Usage of this driver requires
  no additional Python module.

- The Python package `python-usbtmc`. This package in turn needs the `PyUSB`
  package. See http://alexforencich.com/wiki/en/python-usbtmc/start for more
  details. Note that this package has not been updated since a longer time.

- The Python package `PyVISA`, together with a suitable backend. `ya_ds1052`
  is tested with the backends `pyvisa-py` (another Python package) and with
  the National Instruments VISA library for Linux (a bit tricky to install
  for recent Linux kernel versions).

  Be aware that the USBTMC implementation of the DS1000E/D is not fully
  standard compliant. The VISA backend must provide some workarounds for
  the DS1000's quirks.

  Run `pyvisa-info` to check which backend is detected by PyVISA.

On Linux it can be necessary to add a udev rule to give users access to
the device files for the DS1000 oscilloscope. Add a file named
`45-ds1000.rules` to the directory `/etc/udev/rules.d/' with the following
content:

    SUBSYSTEMS=="usb", ACTION=="add", ATTRS{idVendor}=="1ab1", ATTRS{idProduct}=="0588", GROUP="users", MODE="0660"

(Change the group name `users` to whatever suits your needs to manage access
rights for different users.)

Then run

    udevadm control --reload-rules && udevadm trigger

to activate the new rule. Ensure that you and other users who will use the
oscilloscope are members of the user group specified in the udev rule.
If you must add yourself or other users to the user group, remember that a
new group memebership is recognized after a new login, i.e., users must
logout and login again before access to the device files is possible.
