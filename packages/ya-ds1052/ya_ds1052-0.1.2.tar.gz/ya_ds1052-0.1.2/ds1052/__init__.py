# Copyright 2022 Abel Deuring
#
# This file is part of ya_ds1052.
#
# ya_ds1052 is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# ya_ds1052 is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ya_ds1052. If not, see <https://www.gnu.org/licenses/>.

"""Remote control of Rigol DS1000E/D series oscillosopes

Usage example:

    >>>
    >>> import matplotlib.pyplot as plt
    >>> from ds1052 import DS1052, PointsMode, TriggerStatus
    >>>
    >>> with DS1052() as dso:
    >>>     # Acquire the waveform of channel 1 in "normal" points mode
    >>>     # which returns 600 data points.
    >>>     waveform = dso.read_waveforms([1], PointsMode.normal)[0]
    >>>     # waveform.t is a numpy array with time axis values. 0 is the
    >>>     # trigger time.
    >>>     # waveform.v is a numpy array with the voltage values.
    >>>     plt.plot(waveform.t, waveform.v)
    >>>     print(
    >>>         f'vertical scale: {waveform.v_scale}V/div '
    >>>         f'vertical offset: {waveform.v_offset}V')
    >>>     print(
    >>>         f'timebase scale: {waveform.tb_scale}s/div '
    >>>         f'timebase offset: {waveform.tb_offset}s')
    >>> plt.show()

Most settings of the DS1000E/D oscilloscopes are available as properties
either of `class DS1052` instances or of `DS1052.channel` and
`DS1052.trigger`.

Settings and statuses of the DS1000E/D oscilloscopes with a fixed set of
choices, like signal coupling, trigger mode, trigger status are
represented as Enum or IntEnum classes.

"On/off" settings are represnted as boolean properties.

Measurements:

Measurement properties return a tuple `(value, qualifier)`, where `value`
is the value of the measurement and `qualifier`, an instance of
`MeasurementQualifier`, indicates the "meaning" of `value`.

Background: The DS1000E/D returns either a reasonable number for a
measurement, or it adds a `<` or `>` as a prefix to the number. This
indicates that an exact measurement could not be made and that the
measurement result should be interpreted as "the measured value is
less than/greater than `value`. The DS1000E/D sometimes returns the
value 9.9e37 for a measuremnt. This indicates that the DS1000E/D could
not make the desired measurment at all.

(Note that Rigol's own documentationo does not mention anywhere the
prefixes `<`, `>` or the value 9.9e37 at all, hence the description
above is the interpretation by the author of this library.)

Limitations:

Commands related to the digital inputs of the DS1000D series and of trigger
settings related to the digital inputs are not supported.

Reading the "math" data (sum, difference, product of channel1, channel 2,
and FFT) is not supported.

Reading channel data in "long memory mode" is largely untested.

Emulating key presses via SCPI commands is not implemented.
"""

from aenum import Enum, IntEnum, extend_enum
from collections.abc import Sequence
from functools import partial
import logging
from math import inf, log
import numpy as np
import os
import sys
from time import sleep, time

from .exceptions import (
    DS1052PropertySetError, DS1052PropertyValueError, DS1052TimeoutError,
    )
from .tmc import get_tmc_device


logging.basicConfig()

ds1052_logger = logging.getLogger('DS1052')
ds1052_loglevel = os.getenv('DS1052_LOGLEVEL')
if ds1052_loglevel is not None:
    ds1052_logger.setLevel(getattr(logging, ds1052_loglevel))


class AcquisitionType(Enum):
    normal = 'NORMAL'
    average = 'AVERAGE'
    peak_detect = 'PEAK DETECT'


class AcquisitionMode(Enum):
    real_time = 'REAL_TIME'
    equal_time = 'EQUAL_TIME'


class AcquisitionMemoryDepth(Enum):
    long = 'LONG'
    normal = 'NORMAL'


class DisplayType(Enum):
    vector = 'VECTORS'
    dots = 'DOTS'


class DisplayGrid(Enum):
    full = 'FULL'
    half = 'HALF'
    # "none" is IMHO a bit too near to Python's "None"
    off = 'NONE'


class TimebaseMode(Enum):
    main = 'MAIN'
    delayed = 'DELAYED'


class TimebaseFormat(Enum):
    x_y = 'X-Y'
    y_t = 'Y-T'
    scanning = 'SCANNING'


class TriggerMode(Enum):
    edge = 'EDGE'
    pulse = 'PULSE'
    video = 'VIDEO'
    slope = 'SLOPE'
    # XXX Should be enabled for a DS1052D.
    #pattern = 'PATTERN'
    #duration = 'DURATION'
    alternation = 'ALTERNATION'


class TriggerStatus(Enum):
    run = 'RUN'
    stop = 'STOP'
    triggered = "T'D"
    wait = 'WAIT'
    auto = 'AUTO'


class ChannelNumber(IntEnum):
    """Channel numbers."""
    # XXX I don't known what is better: Start the channel numbers from 1, as
    # on the DSO's front panel, in the manual, in the "engineers thinking",
    # or start from 0, as often done in software development?
    # (Or even mis the stuff, i.e. define "ch1 = 0" - Nah, that's just crazy.)
    channel1 = 1
    channel2 = 2
    # XXX Should be enabled for a DS1052D
    # channel3 = ....


class TriggerSource(IntEnum):
    """Enum for trigger sources.

    Note that `ac_line` can only be set in `TriggerMode.edge`.
    """
    # Channels are added from class Channel below.
    external = -1
    ac_line = -2


for _ch in ChannelNumber:
    extend_enum(TriggerSource, _ch.name, _ch.value)


class Sweep(Enum):
    """Enum for the sweep mode."""
    single = 'SINGLE'
    normal = 'NORMAL'
    auto = 'AUTO'


class TriggerCoupling(Enum):
    """Enum for the trigger coupling."""
    dc = 'DC'
    ac = 'AC'
    hf = 'HF'
    lf = 'LF'


class Slope(Enum):
    """Enum for trigger slopes.

    Used in trigger mode "edge" to specify a rising (positive) or falling
    (negative) edge of the signal, or both.

    Not to be confused with the trigger mode that is also called "slope".
    """
    positive = 'POSITIVE'
    negative = 'NEGATIVE'
    both = 'ALTERNATION'


class TriggerTimeCondition(Enum):
    """Values of DS1052.trigger.pulse.time_condition
    and DS1052.trigger.slope.time_condition.
    """

    positive_pulse_width_longer_than = '+GREATER THAN'
    positive_pulse_width_shorter_than = '+LESS THAN'
    positive_pulse_width_equal = '+EQUAL'
    negative_pulse_width_longer_than = '-GREATER THAN'
    negative_pulse_width_shorter_than = '-LESS THAN'
    negative_pulse_width_equal = '-EQUAL'


class VideoTriggerSyncType(Enum):
    """Values of DS1052.trigger.video.sync"""

    odd_field = 'ODD FIELD'
    even_field = 'EVEN FIELD'
    line_number = 'LINE'
    all_lines = 'ALL LINES'


class VideoTriggerPolarity(Enum):
    """Values of DS1052.trigger.video.polarity"""

    positive = 'POSITIVE'
    negative = 'NEGATIVE'


class VideoStandard(Enum):
    """Values of DS1052.trigger.video.standard"""

    ntsc = 'NTSC'
    pal_secam = 'PAL/SECAM'


class ChannelCoupling(Enum):
    """Enum for the channel coupling."""
    dc = 'DC'
    ac = 'AC'
    gnd = 'GND'


class ChannelVernier(Enum):
    coarse = 'Coarse'
    fine = 'Fine'


class PointsMode(Enum):
    """Mode for data retrieval.

    Determines the amount of data retrieved when channel data is read in
    TriggerMode.stop.
    """

    normal = 'NORMAL'
    max = 'MAXIMUM'
    raw = 'RAW'


# 0.2s as a timeout seems to be too small, while it works in many cases.
# 0.3s works much better. But working in 5836da9 on an improved test
# setup that sets all relevant properties in
# DS1052TestsWithTestSignalBase.setUpClass() instead of betting that an
# :AUTO call will get the settings right, it turns out that one or the
# other statement in setUpClass making a property assignment still can
# time out in DS1052TestsWithTestSignal.setUpClass(). When the subsequent
# call of WaveformTest.setUpClass() is run, the call of cls.dso.open()
# fails with a "usb.core.USBError: [Errno 16] Resource busy". Occasionally
# the DS1052 must even be power-cycled. A timeout of 0.5s avoids these
# problems.
# Even 0.5s is not enough in all circumstances -- see the comment in
# DS1052TestsWithTestSignalBase.
_PROPERTY_WAIT_TIMEOUT = 1.0

def _wait_until_property_set(callable, expected):
    """The DS1052 needs some time until it return the new value when
    a parameter is changed. Wait at most for the `self.TIMEOUT` until
    the value has ben set.

    Raises a DS1052PropertySetError when a timeout occurs.
    """
    wait_until = time() + _PROPERTY_WAIT_TIMEOUT
    while time() < wait_until:
        value = callable()
        if value == expected:
            return
        sleep(0.01)
    raise DS1052PropertySetError(
        f'Timeout while waiting for a property to be set. '
        f'Expected value: {expected!r}, last seen: {value!r}')


class _DevicePropertyBase(property):
    """Base class for properties of class DS1052 that represent settings
    of the device.

    This class is mostly a convenient mechanism to avoid very repetetive
    code that implements all the different properties/device settings.
    """
    def __init__(self, command, doc, read_only=False):
        self.command = command
        if read_only:
            super().__init__(self.getter, doc=doc)
        else:
            super().__init__(self.getter, self.setter, doc=doc)
        # XXX This is strange: The doc string was passed to the
        # property constructor, but the __doc__ attribute must still be
        # explicitly set here, otherwise the property would have the
        # __doc__ string of class property itself or of one of the derived
        # classes.
        self.__doc__ = doc

    def wait_until_set(self, dso, value):
        """The DS1052 needs some time until it returns the new value when
        a parameter is changed. Wait at most `self.TIMEOUT` seconds until
        the value has ben set.

        Raises a DS1052PropertySetError when a timeout occurs.
        """
        _wait_until_property_set(partial(self.getter, dso), value)

    def as_config_value(self, dso):
        return self.getter(dso)

    def from_config_value(self, dso, new_value):
        self.setter(dso, new_value)


class _EnumDeviceProperty(_DevicePropertyBase):
    """
    Helper for class DS1052: Bind Enum classes to a getter and setter
    that access the DSO to read or change a certain parameter.
    enum: A class derived from Enum that represents the parameter values.
    command: The command string to send to the DSO in order to retrieve
        or change the parameter.
    setter_values: An optional dictionary that stores the strings needed
        to change a value. The DS1052 has an odd quirk: For example,
        ":ACQuire:TYPE" expects the parameter value "PEAKDETECT" to change
        the acquisition type but returns the value "Peak Detect" when
        queried for the acquisition type...
        When setter_values is defined, it maps certain values of the enum
        to strings to be sent to the DS1052. If no entry exists in
        setter_values, or if setter_values is None, the enum text value
        is sent to the DS1052 to set the parameter.
    """

    def __init__(
            self, enum, command, doc, setter_values=None, read_only=False):
        super().__init__(command, doc, read_only)
        self.enum = enum
        if setter_values is None:
            self.setter_values = {}
        else:
            self.setter_values = setter_values

    def getter(self, dso):
        result = dso._tmc_device.ask(f'{self.command}?')
        return self.enum._value2member_map_[result.upper()]

    def setter(self, dso, value):
        if not isinstance(value, self.enum):
            raise DS1052PropertyValueError(
                f'Expected an instance of {self.enum}, not {type(value)}')
        if value == self.getter(dso):
            return
        if value in self.setter_values:
            text_value = self.setter_values[value]
        else:
            text_value = value.value
        dso._tmc_device.write(f'{self.command} {text_value}')
        self.wait_until_set(dso, value)
        dso._update_read_source_delay()

    def as_config_value(self, dso):
        return self.getter(dso).name

    def from_config_value(self, dso, new_value):
        try:
            internal_value = getattr(self.enum, new_value)
        except (TypeError, AttributeError):
            # TypeError is raised if new_value is not a str.
            raise DS1052PropertyValueError(
                f'{new_value!r} is not a valid enum value of {self.enum}')
        self.setter(dso, internal_value)


class _BoolDeviceProperty(_DevicePropertyBase):
    def getter(self, dso):
        result = dso._tmc_device.ask(f'{self.command}?')
        if result not in {'ON', 'OFF'}:
            raise RuntimeError(
                f'Unexpected value returned for {self.command}: {result!r}')
        return result == "ON"

    def setter(self, dso, value):
        value = bool(value)
        if value == self.getter(dso):
            return
        dso._tmc_device.write(f'{self.command} {"ON" if value else "OFF"}')
        self.wait_until_set(dso, bool(value))
        dso._update_read_source_delay()


def _float_format(value, digits):
    """Problem: When for example :TIMEBASE:OFFSET is set to a value
    where abs(value) is less than 1e-4, f'{value}' evaluates to a textual
    representation in "e-notation", e.g. "1e-5".

    But the DS1052 seems to not accept this representation, i.e., the
    value must be provided in usual decimal notation, i.e. "0.00001"
    instead of "1e-5".

    This method returns always a float value in this representation,
    without adding not needed leading spaces or trailing zeros.

    When abs(value) is < 1, it is assumed that four digits for the
    "real value" are good enough, i.e., 0.123456 is evaluated to
    "0.1235".

    This formatting means that there is "precision loss": When the returned
    string representation is converted back into a float value, it is in most
    cases slightly different from the original float value.

    All property.setter() methods call _wait_until_property_set() which
    repeatedly reads the property value from the device until the expected
    value is set. This call can time out if there is "precision loss"
    and if the retrieved value is directly compared with the float argument
    of the setter() call.

    Now comes the weird detail: While the DS1052 accepts float value to be
    set only in regular simple decimal notation, it returns the value in
    scientific notation...

    Hence this function _also_ returns the float value in four-digit
    scientific notation. This allows a setter() to make a string comparison
    of the value returned by der DS1052 in wait_until_property_set() calls.
    """
    if value == 0:
        return '0.0', f'{value:.{digits-1}e}'
    lg = int(log(abs(value), 10))
    if lg < 0:
        # abs(value) < 1: Enough "space" for `lg` zeros after the decimal
        # point plus four digits for the "real value".
        m = -lg + digits
        n = m + 2
    else:
        # at most 4 digits after the decimal point.
        m = max(0, digits - lg)
        n = lg
    if value < 0:
        n += 1
    return f'{value:{n}.{m}f}', f'{value:.{digits-1}e}'


def _write_check_float_value(dso, write_message, read_message, expected):
    dso._tmc_device.write(write_message)
    wait_until = time() + _PROPERTY_WAIT_TIMEOUT
    while time() < wait_until:
        value = dso._tmc_device.ask(read_message)
        if expected == value:
            return
        sleep(0.01)
    raise DS1052PropertySetError(
        f'Timeout while waiting for a property to be set. '
        f'Expected value: {expected}, last seen: {value}')


class _FloatDeviceProperty(_DevicePropertyBase):
    greater_than_upper_limit_msg = (
        'Only values less than or equal to {} allowed.')
    less_than_lower_limit_msg = (
        'Only values greater than or equal to {} allowed.')
    def __init__(self, command, doc, min_value=None, max_value=None, digits=4):
        self.min_value = min_value
        self.max_value = max_value
        self.digits = digits
        super().__init__(command, doc)

    def getter(self, dso):
        return float(dso._tmc_device.ask(f'{self.command}?'))

    def setter(self, dso, value):
        if not isinstance(value, float):
            value = float(value)
        if self.max_value is not None and value > self.max_value:
            raise DS1052PropertyValueError(
                self.greater_than_upper_limit_msg.format(self.max_value))
        if self.min_value is not None and value < self.min_value:
            raise DS1052PropertyValueError(
                self.less_than_lower_limit_msg.format(self.min_value))
        write_value, read_value = _float_format(value, self.digits)
        if float(read_value) == self.getter(dso):
            return
        write_message = f'{self.command} {write_value}'
        read_message =f'{self.command}?'
        _write_check_float_value(dso, write_message, read_message, read_value)
        dso._update_read_source_delay()


class _PropertyWithChoicesMixin:
    def __init__(self, command, doc, choices, typecast):
        super().__init__(command, doc)
        self.choices = choices
        self.typecast = typecast

    def setter(self, dso, value):
        # Ugly trick: This property variant is used for several settings;
        # most of them have a fixed set of choices. This is not the case
        # for timebase_scale: Possible values for this property depend on the
        # DSO model that is actually controlled by an instance of
        # class DS1052: The DS1102 allows one value more than the "smaller"
        # models. Hence the choices for the property timebase_scale are in
        # turn _also_ defined as a property, which returns different values
        # for the DS1052 and the DS1102.
        #
        # This means that the choices for timebase_scale must be accessed
        # as a property of the DS1052 instance. This is implicitly indicated
        # by the type of self.choices: If this attribute is itself a
        # property, assume that it is a property of class DS1052, and retrieve
        # it value.
        if isinstance(self.choices, property):
            choices = self.choices.fget(dso)
        else:
            choices = self.choices
        value = self.typecast(value)
        if value not in choices:
            raise DS1052PropertyValueError(
                f'Invalid value: {value!r}. Allowed: {sorted(choices)}')
        super().setter(dso, value)


class _FloatChoicesDeviceProperty(
        _PropertyWithChoicesMixin, _FloatDeviceProperty):
    pass


class _IntDeviceProperty(_DevicePropertyBase):
    def __init__(self, command, doc, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value
        super().__init__(command, doc)

    def getter(self, dso):
        result = dso._tmc_device.ask(f'{self.command}?')
        return int(result)

    def setter(self, dso, value):
        if not isinstance(value, int):
            value = int(value)
        if self.max_value is not None and value > self.max_value:
            raise DS1052PropertyValueError(
                f'Only values less than or equal to {self.max_value} allowed.')
        if self.min_value is not None and value < self.min_value:
            raise DS1052PropertyValueError(
                f'Only values greater than or equal to {self.min_value} '
                f'allowed.')
        if value == self.getter(dso):
            return
        dso._tmc_device.write(f'{self.command} {value}')
        self.wait_until_set(dso, value)
        dso._update_read_source_delay()


class _IntChoicesDeviceProperty(_PropertyWithChoicesMixin, _IntDeviceProperty):
    pass


class _MappedProperty(_DevicePropertyBase):
    """A property that needs mappings to translate between strings to be sent
    to the device and the Python representation of the value.
    """
    def __init__(self, command, doc, device_to_python, python_to_device):
        self.device_to_python = device_to_python
        self.python_to_device = python_to_device
        super().__init__(command, doc)

    def getter(self, dso):
        return self.device_to_python[dso._tmc_device.ask(f'{self.command}?')]

    def setter(self, dso, value):
        if value not in self.python_to_device:
            raise DS1052PropertyValueError(
                f'Invalid value: {value!r}. Allowed: '
                f'{sorted(self.python_to_device)}')

        if value == self.getter(dso):
            return
        dso._tmc_device.write(f'{self.command} {self.python_to_device[value]}')
        self.wait_until_set(dso, value)
        dso._update_read_source_delay()


class _TriggerSourceForModeProperty(_DevicePropertyBase):
    _tr_source_set_values = {
        TriggerSource.channel1: 'CHANNEL1',
        TriggerSource.channel2: 'CHANNEL2',
        TriggerSource.external: 'EXT',
        TriggerSource.ac_line: 'ACLINE',
    }

    _device_name_2_enum = {
        'CH1': TriggerSource.channel1,
        'CH2': TriggerSource.channel2,
        'EXT': TriggerSource.external,
        'ACLINE': TriggerSource.ac_line,
        }

    _allowed_values = {
        TriggerMode.edge: TriggerSource,
        TriggerMode.pulse: (TriggerSource.channel1, TriggerSource.channel2,
                            TriggerSource.external),
        TriggerMode.video: (TriggerSource.channel1, TriggerSource.channel2,
                            TriggerSource.external),
        TriggerMode.slope: (TriggerSource.channel1, TriggerSource.channel2,
                            TriggerSource.external),
        TriggerMode.alternation: (),
        }

    _property_doc = """
    Trigger source. Possible values: {}.

    Additionally, instances of `class ChannelNumber` can be be assigned,
    or the integers (1, 2) to `source`, representing a channel number.
    """
    _property_doc_alternation = """
    Trigger source. Read-only.
    """

    def __init__(self, trigger_mode):
        self.trigger_mode = trigger_mode
        command = f':TRIG:{trigger_mode.value}:SOURCE'
        if self.trigger_mode != TriggerMode.alternation:
            doc = self._property_doc.format(
                ', '.join(
                    f'TriggerSource.{tr_source.name}'
                    for tr_source in self._allowed_values[trigger_mode]))
        else:
            doc = self._property_doc_alternation
        super().__init__(command, doc)

    def getter(self, trigger_source_attr):
        result = trigger_source_attr._dso._tmc_device.ask(f'{self.command}?')
        return self._device_name_2_enum[result]

    def setter(self, trigger_source_attr, new_source):
        if not isinstance(new_source, TriggerSource):
            # Accept channel numbers too, plain integers as well as Channel
            # instances.
            if type(new_source) == int or isinstance(new_source, ChannelNumber):
                # Assume that this is a channel number. Will raise a ValueError
                # if this is not the case.
                try:
                    new_source = ChannelNumber(new_source)
                except ValueError:
                    raise DS1052PropertyValueError(
                    'A trigger source must be an instance of TriggerSource, '
                    'or of ChannelNumber or an integer representing a channel '
                    'number')
            else:
                raise DS1052PropertyValueError(
                    'A trigger source must be an instance of TriggerSource, '
                    'or of ChannelNumber or an integer representing a channel '
                    'number')
            new_source = TriggerSource(int(new_source))

        if self.trigger_mode == TriggerMode.alternation:
            raise DS1052PropertyValueError(
                f'Cannot set a trigger source in {TriggerMode.alternation}')
        if new_source not in self._allowed_values[self.trigger_mode]:
            raise DS1052PropertyValueError(
                f'Cannot set {TriggerSource.ac_line} in {self.trigger_mode}')
        if new_source == self.getter(trigger_source_attr):
            return
        new_source_text = self._tr_source_set_values[new_source]
        trigger_source_attr._dso._tmc_device.write(
            f'{self.command} {new_source_text}')
        self.wait_until_set(trigger_source_attr, new_source)
        trigger_source_attr._dso._update_read_source_delay()


class _TriggerPropertyBase(property):
    _read_only = False

    def __init__(self, trigger_mode=None):
        if trigger_mode is not None:
            command = self._command_template.format(trigger_mode.value)
        else:
            command = self._command_template
        self._device_property = self._device_property_class(
            command, self.__doc__)
        if self._read_only:
            super().__init__(self.getter, doc=self.__doc__)
        else:
            super().__init__(self.getter, self.setter, doc=self.__doc__)

    def getter(self, trigger_mode):
        # This is a property of _TriggerSourceForModeProperty,
        # _TriggerLevelForModeProperty etc., but _DeviceProperty objects
        # need the DS1052 object itself.
        return self._device_property.getter(trigger_mode._dso)

    def setter(self, trigger_mode, new_value):
        self._device_property.setter(trigger_mode._dso, new_value)

    def as_config_value(self, trigger_mode):
        return self._device_property.as_config_value(trigger_mode._dso)

    def from_config_value(self, trigger_mode, value):
        self._device_property.from_config_value(trigger_mode._dso, value)


class _TriggerLevelForModeProperty(_TriggerPropertyBase):
    """Trigger level in V.

    Allowed values: -6 * vertical_scale - vertical_offset
    to +6 * vertical_scale - vertical_offset for the
    trigger sources channel 1, channel 2; -1.2V .. +1.2V for the external
    trigger source.

    This property can only be set when the trigger source is set to
    channel1, channel 2 or external.
    """
    _command_template = ':TRIG:{}:LEVEL'
    _device_property_class = partial(_FloatDeviceProperty, digits=3)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._device_property.greater_than_upper_limit_msg = (
            'Only values less than or equal to '
            '6 * vertical scale - vertical offset ({}) allowed.')
        self._device_property.less_than_lower_limit_msg = (
            'Only values greater than or equal to '
            '-6 * vertical scale - vertical offset ({}) allowed.')

    def setter(self, trigger_mode, new_value):
        trigger_source = trigger_mode.source
        if trigger_source in (1, 2):
            min_value, max_value = (
                trigger_mode._dso.channel[trigger_source].trigger_level_range)
            self._device_property.min_value = min_value
            self._device_property.max_value = max_value
        elif trigger_source == TriggerSource.external:
            self._device_property.max_value = 1.2
            self._device_property.min_value = -1.2
        else:
            raise DS1052PropertyValueError(
                'Trigger level can only be set when the trigger source is '
                'CH1, CH2 or external.')
        super().setter(trigger_mode, new_value)

    def adjust_source_scale_offset(self, trigger_mode, value):
        # It may be necessary to change the the trigger channel's scale and
        # offset. The values will be restored by calling set_config()
        # method.
        if trigger_mode.source not in (1, 2):
            return
        channel = trigger_mode._dso.channel[trigger_mode.source]
        level_min, level_max = channel.trigger_level_range
        if level_min <= value <= level_max:
            return
        scale_min, scale_max = channel.scale_range
        if channel.scale < scale_max:
            channel.scale = scale_max
            level_min, level_max = channel.trigger_level_range
            if level_min <= value <= level_max:
                return
        offset_min, offset_max = channel.offset_range
        if value < level_min:
            # Try to increase the offset
            new_offset = level_min - value
            if new_offset <= offset_max:
                channel.offset = new_offset
            # No real need for an "else" with a "raise SomeException":
            # setter() will do that,
            return
        # value > level_max
        new_offset = level_max - value
        if new_offset >= offset_min:
            channel.offset = new_offset
        # Again, no need for an "else".

    def from_config_value(self, trigger_mode, value):
        self.adjust_source_scale_offset(trigger_mode, value)
        self.setter(trigger_mode, value)


class _SweepForTriggerModeProperty(_TriggerPropertyBase):
    """Sweep mode.

    Allowed values: Instances of `class Sweep`.
    """
    _command_template = ':TRIG:{}:SWEEP'
    _device_property_class = partial(_EnumDeviceProperty, Sweep)


class _TriggerCouplingForTriggerModeProperty(_TriggerPropertyBase):
    """Trigger coupling.

    Allowed values: Instances of class `TriggerCoupling`.
    """
    _command_template = ':TRIG:{}:COUPLING'
    _device_property_class = partial(_EnumDeviceProperty, TriggerCoupling)


class _TriggerSlopeForTriggerModeProperty(_TriggerPropertyBase):
    """Slope setting.

    Allowed values: Instances of class `Slope`.

    It specifies when the data acquisiton is triggered in the trigger mode
    "edge": On the rising edge of the trigger signel (value Slope.positive),
    on the falling edge (Slope.negative), or both (Slope.both).

    Note: This property is different from the trigger _mode_ that is also
    called "slope". The author feels only partially responsible for this
    confusion: The DS1052 has the same mixup in the terminology used
    for the devcie's own display where a trigger _mode_ "slope" can be
    selected and for trigger mode "edge" exists the option to set
    the "slope".

    Feeling like somebody pulled your leg? Me too when I noticed this
    name clash. Suggestions for improvements are welcome.
    """
    _command_template = ':TRIG:{}:SLOPE'
    _device_property_class = partial(_EnumDeviceProperty, Slope)


class _TriggerModeProperty(_TriggerPropertyBase):
    """Trigger mode.

    Allowed values are instances of `class TriggerMode`.
    """
    _command_template = ':TRIG:MODE'
    _device_property_class = partial(_EnumDeviceProperty, TriggerMode)


class _TriggerStatusProperty(_TriggerPropertyBase):
    """Trigger status.

    Returns instances of `class TriggerStatus`.)
    """
    _command_template = ':TRIG:STAT'
    _device_property_class = partial(
        _EnumDeviceProperty, TriggerStatus, read_only=True)
    _read_only=True


class _TriggerHoldoffProperty(_TriggerPropertyBase):
    """Trigger holdoff in s. Allowed values: 500e-9 .. 1.5"""

    _command_template = ':TRIG:HOLDOFF'
    _device_property_class = partial(
        _FloatDeviceProperty, min_value=500e-9, max_value=1.5)


class _TriggerSensitivityProperty(_TriggerPropertyBase):
    """Trigger sensitivity, specified as the fraction of a display DIV.

    Allowed values: 0.1 .. 1.
    """

    _command_template = ':TRIG:{}:SENS'
    _device_property_class = partial(
        _FloatDeviceProperty, min_value=0.1, max_value=1.0, digits=3)


class _TriggerPulseSlopeConditionPropertyBase(_TriggerPropertyBase):
    """Common base class for _TriggerPulseConditionProperty and
    _TriggerSlopeTimeConditionProperty.

    Implementations can be identical but the doc should be slightly different.
    """

    _command_template = ':TRIG:{}:MODE'
    _device_property_class = partial(
        _EnumDeviceProperty, TriggerTimeCondition,
        setter_values={
            TriggerTimeCondition.positive_pulse_width_longer_than: '+GRE',
            TriggerTimeCondition.positive_pulse_width_shorter_than: '+LESS',
            TriggerTimeCondition.negative_pulse_width_longer_than: '-GRE',
            TriggerTimeCondition.negative_pulse_width_shorter_than: '-LESS',
        })


class _TriggerPulseTimeConditionProperty(
        _TriggerPulseSlopeConditionPropertyBase):
    """Condition when a pulse trigger occurs.

    This property specifies the condition for a pulse trigger event:
    If the pulse width is shorter than <time>, longer than <time>,
    or equal to <time>, and if a positive or negative pulse of the
    specified length causes a trigger event.

    <time> is specified by the property `time_condition_value`.

    Allowed values of this property: Instances of `TriggerTimeCondition`.
    """


class _TriggerSlopeTimeConditionProperty(
        _TriggerPulseSlopeConditionPropertyBase):
    """Condition when a slope trigger occurs.

    This property specifies the condition for a slope trigger event:
    If the slope width is shorter than <time>, longer than <time>,
    or equal to <time>, and if a positive or negative slope of the
    specified length causes a trigger event.

    <time> is specified by the property `time_condition_value`.

    Allowed values of this property: Instances of `TriggerTimeCondition`.
    """


class _TriggerPulseTimeConditionValueProperty(_TriggerPropertyBase):
    """Width of a pulse in s to match the trigger condition specified by the
    property `time_condition`.

    Allowed values: 20ns .. 10s.
    """

    _command_template = ':TRIG:{}:WIDTH'
    _device_property_class = partial(
        _FloatDeviceProperty, min_value=20e-9, max_value=10.0)


class _TriggerSlopeLevelBase(property):
    # The values returned by the device for :TRIGGER:SLOPE:LEVELA and
    # :TRIGGER:SLOPE:LEVELB depend on the "active edge" of the signal:
    # When a negative transition is "active" (:TRIGger:SLOPe:MODE is
    # -LESS, -GREATER, -EQUAL), level A is smaller than level B;
    # for positive transitions level A is greater than level B.
    #
    # This makes it, well, not hard but really cumbersome to figure out
    # how to set the values successfully for all conditions, like
    # old values for (lower, upper) = (1, 2), new values = (-1, 0).
    # Here, the new lower value must be set first. Attempts to set
    # a new upper value that is greater than the current lower value
    # are rejected by the DS1052. Siumilarly, when the new values are
    # (3, 4), the upper value must be set first.
    #
    # In itself, quite straightforward to implement. But when this must
    # be combined with a decision if level A or level B is actually the
    # lower level, things become messy, at least, when done in one place.
    #
    # It is also noteworthy that the DSO1052 does not seem to have
    # different settings for positive and negative slopes. When the
    # "active slope" is changed, the values returned for
    # ":TRIGGER:SLOPE:LEVELA?" and ":TRIGGER:SLOPE:LEVELB" are simply
    # swapped.
    #
    # Anyway, let's "swap" them here again to make life easier for
    # application development.

    command = ':TRIGGER:SLOPE:LEVEL'

    def __init__(self):
        super().__init__(self.getter, self.setter, doc=self.__doc__)

    def getter(self, trigger_mode):
        if trigger_mode.time_condition in (
                TriggerTimeCondition.negative_pulse_width_longer_than,
                TriggerTimeCondition.negative_pulse_width_shorter_than,
                TriggerTimeCondition.negative_pulse_width_equal):
            sel_suffix = self.negative_sel_suffix
        else:
            sel_suffix = self.positive_sel_suffix
        return float(
            trigger_mode._dso._tmc_device.ask(f'{self.command}{sel_suffix}?'))

    def setter(self, trigger_mode, new_value):
        if trigger_mode.time_condition in (
                TriggerTimeCondition.negative_pulse_width_longer_than,
                TriggerTimeCondition.negative_pulse_width_shorter_than,
                TriggerTimeCondition.negative_pulse_width_equal):
            sel_suffix = self.negative_sel_suffix
        else:
            sel_suffix = self.positive_sel_suffix
        if not isinstance(new_value, float):
            value = float(new_value)
        self.range_check(trigger_mode, new_value)

        write_value, read_value = _float_format(new_value, digits=4)
        if float(read_value) == self.getter(trigger_mode):
            return
        write_message = f'{self.command}{sel_suffix} {write_value}'
        read_message = f'{self.command}{sel_suffix}?'
        _write_check_float_value(
            trigger_mode._dso, write_message, read_message, read_value)
        trigger_mode._dso._update_read_source_delay()

    def _channel_settings_range_check(self, trigger_mode, new_value):
        source = trigger_mode.source
        if source in (TriggerSource.channel1, TriggerSource.channel2):
            min_value, max_value = (
                trigger_mode._dso.channel[source].trigger_level_range)
        else:
            min_value = -1.2
            max_value = 1.2
        if new_value > max_value:
            raise DS1052PropertyValueError(
                f'Only values less than or equal to '
                f'vertical scale - vertical offset ({max_value}) allowed.')
        if new_value < min_value:
            raise DS1052PropertyValueError(
                f'Only values greater than or equal to '
                f'vertical scale - vertical offset ({min_value}) allowed.')


class _TriggerSlopeLevelLower(_TriggerSlopeLevelBase):
    """Lower trigger voltage level.

    Allowed values:

      (-6 * vertical_scale .. +6 * vertical_scale) - vertical_offset

    but restricted to values less that the actual value of
    `voltage_level_upper`.
    """
    negative_sel_suffix = 'A'
    positive_sel_suffix = 'B'

    def range_check(self, trigger_mode, value):
        upper_value = trigger_mode.voltage_level_upper
        if upper_value < value:
            raise DS1052PropertyValueError(
                f'New value for lower level ({value}) must not be greater '
                f'than the current upper level ({upper_value})')
        self._channel_settings_range_check(trigger_mode, value)


class _TriggerSlopeLevelUpper(_TriggerSlopeLevelBase):
    """Upper trigger voltage level.

    Allowed values: -6 * vertical_scale .. +6 * vertical_scale,

      (-6 * vertical_scale .. +6 * vertical_scale) - vertical_offset

    but restricted to values greater that the actual value of
    `voltage_level_lower`.
    """
    negative_sel_suffix = 'B'
    positive_sel_suffix = 'A'

    def range_check(self, trigger_mode, value):
        lower_value = trigger_mode.voltage_level_lower
        if lower_value > value:
            raise DS1052PropertyValueError(
                f'New value for upper level ({value}) must not be smaller '
                f'than the current lower level ({lower_value})')
        self._channel_settings_range_check(trigger_mode, value)


class _TriggerVideoSyncProperty(_TriggerPropertyBase):
    """Sync type of the video trigger.

    This property specifies the condition for a video trigger event.

    Allowed values of this property: Instances of `VideoTriggerSyncType`.
    """

    _command_template = ':TRIG:{}:MODE'
    _device_property_class = partial(
        _EnumDeviceProperty, VideoTriggerSyncType,
        setter_values={
            VideoTriggerSyncType.odd_field: 'ODD',
            VideoTriggerSyncType.even_field: 'EVEN',
            VideoTriggerSyncType.all_lines: 'ALL',
        })


class _TriggerVideoPolarityProperty(_TriggerPropertyBase):
    """Polarity of the video trigger.

    Allowed values of this property: Instances of `VideoTriggerPolarity`.
    """

    _command_template = ':TRIG:{}:POL'
    _device_property_class = partial(
        _EnumDeviceProperty, VideoTriggerPolarity)


class _TriggerVideoStandardProperty(_TriggerPropertyBase):
    """Video standard.

    Allowed values of this property: Instances of `VideoStandard`.
    """

    _command_template = ':TRIG:{}:STANDARD'
    _device_property_class = partial(
        _EnumDeviceProperty, VideoStandard,
        setter_values={
            VideoStandard.pal_secam: 'PALSECAM',
        })


class _TriggerVideoLineProperty(_TriggerPropertyBase):
    """Video line number to trigger on.

    Allowed values: 1 .. 625.
    """
    # XXX The max value of line number depends on the selected video
    # standard but this property allows values up to 625 even for NTSC.
    # IOW, an example of a property whose avlue constraints depend on
    # another property's value.
    # Do not bother for now to implement such a feature: Frankly, who
    # needs a trigger mode for analog video signals in 2022?
    _command_template = ':TRIG:{}:LINE'
    _device_property_class = partial(
        _IntDeviceProperty, min_value=1, max_value=625)


class _TriggerSlopeTimeProperty(_TriggerPropertyBase):
    """Time/duration value in s of a slope trigger condition.

    Allowed values: 20e-9 .. 10.
    """
    _command_template = ':TRIG:{}:TIME'
    _device_property_class = partial(
        _FloatDeviceProperty, min_value=20e-9, max_value=10.0)


class TriggerSlopeVoltageLevelsProperty(property):
    """The trigger voltage levels as a tuple
    (voltage_level_lower, voltage_level_upper).

    Allowed values: -6 * vertical_scale .. +6 * vertical_scale.
    voltage_level_lower must be less than voltage_level_upper.

    The setter of this property ensures that the two values are
    set in the right order.
    """
    def __init__(self):
        super().__init__(self.getter, self.setter)

    def getter(self, trigger_mode):
        return (
            trigger_mode.voltage_level_lower, trigger_mode.voltage_level_upper)

    def setter(self, trigger_mode, new_value):
        lower, upper = new_value
        if lower >= upper:
            # Yeah, there is similar check in _TriggerSlopeLevelLower.setter()
            # and _TriggerSlopeLevelUpper.setter(). But with this additional
            # check here it is sure that decision which of the two values
            # to set first is alwasy correct.
            raise DS1052PropertyValueError(
                'The first value (voltage_level_lower) must be smaller '
                'than the second value (voltage_level_upper).')
        # The current value of voltage_level_upper might be smaller
        # than the new value of voltage_level_lower. In this case
        # trigger_mode.voltage_level_lower must be changed first, to prevent
        # a ValueError in _TriggerSlopeLevelUpper.setter().
        if upper < trigger_mode.voltage_level_lower:
            trigger_mode.voltage_level_lower = lower
            trigger_mode.voltage_level_upper = upper
        else:
            trigger_mode.voltage_level_upper = upper
            trigger_mode.voltage_level_lower = lower

    def as_config_value(self, trigger_mode):
        return self.getter(trigger_mode)

    def adjust_source_scale_offset(self, trigger_mode, value):
        # It may be necessary to change the the trigger channel's scale and
        # offset. The values will be restored by calling set_config()
        # method.
        if trigger_mode.source not in (1, 2):
            # External trigger source selected:Uts fixed trigger level range
            # checks are completely handled in setter()
            return
        lower, upper = value
        if upper < lower:
            # No need to try anything: (1) the setting is nonsense hence
            # setter() will anyway raise an exception, (2) Considering this
            # case in all the conditions below would make things more complex
            # that necessary.
            return
        channel = trigger_mode._dso.channel[trigger_mode.source]
        level_min, level_max = channel.trigger_level_range
        if (
                (level_min <= lower <= level_max)
                and (level_min <= upper <= level_max)):
            return
        scale_max = channel.scale_range[1]
        if channel.scale < scale_max:
            channel.scale = scale_max
            level_min, level_max = channel.trigger_level_range
            if (
                    (level_min <= lower <= level_max)
                    and (level_min <= upper <= level_max)):
                return
        # The difference of the trigger levels must not exceed the level
        # range. Otherwise, at least one of the trigger levels will be
        # outside the trigger level range for any offset.
        if upper - lower > level_max - level_min:
            raise DS1052PropertyValueError(
                f'The difference of the trigger levels ({lower}, {upper}) '
                f'must not exceed {level_max - level_min}')
        offset_min, offset_max = channel.offset_range
        if lower < level_min:
            new_offset = level_min - lower
            if new_offset > offset_max:
                # The desired trigger value is outside the possible rnage.
                # Set the "best" offset for this value anyway so that setter()
                # will show reasonable values in the exception it will raise.
                new_offset = offset_max
        else:
            new_offset = level_max - upper
            if new_offset < offset_min:
                new_offset = offset_min
        channel.offset = new_offset

    def from_config_value(self, trigger_mode, value):
        self.adjust_source_scale_offset(trigger_mode, value)
        return self.setter(trigger_mode, value)


class _ArrayDevicePropertyProxy:
    """Created by ArrayDeviceProperty when an "indexed property" is accessed.

    Provides minimal support for Python's sequence protocol.
    """
    def __init__(
            self, device, indexes, str_to_py_obj, read_command,
            write_command=None):
        self.device = device
        self.read_command = read_command
        self.write_command = write_command
        self.indexes = indexes
        self.str_to_py_obj = str_to_py_obj

    def __getitem__(self, index):
        if index not in self.indexes:
            raise IndexError(index)
        result = self.device._tmc_device.ask(
            self.read_command.format(index=index))
        return self.str_to_py_obj(result)

    def __setitem__(self, index, value):
        if self.write_command is None:
            raise TypeError('Cannot set this property')
        if index not in self.indexes:
            raise IndexError(index)
        self._tmc_device.write(
            self.write_command.format(index=index, value=value))


class _ChannelPropertyProxy(_ArrayDevicePropertyProxy):
    """Proxy for "per-channel" properties.

    Accepted key values: Channel instances, integers that are enumerated
    in Channel, and TriggerSource instances that are represent a channel.
    """
    def __init__(
            self, device, indexes, str_to_py_obj, read_command,
            write_command=None):
        super().__init__(
            device, set(ChannelNumber), str_to_py_obj, read_command,
            write_command)

    def _normalize_key(self, key):
        if isinstance(key, ChannelNumber):
            return key
        if isinstance(key, TriggerSource):
            # Allow "shortcuts" from trigger source to channel. A bit risky
            # do this since a value like TriggerSource.external will raise
            # a key error but it makes application code a bit simpler.
            #
            # Yes, this works: key is _also_ an integer.
            return ChannelNumber(key)
        if isinstance(key, IntEnum):
            # Any other enum type indicates a semantic problem.
            raise KeyError('Not a valid channel index: {key!r}')
        if isinstance(key, int):
            # Assume that a channel number is menat.
            return ChannelNumber(key)
        raise KeyError('Not a valid channel index: {key!r}')

    def __getitem__(self, key):
        key = self._normalize_key(key)
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        key = self._normalize_key(key)
        super().__setitem__(key, value)


class _ArrayDeviceProperty(_DevicePropertyBase):
    """Intended to be used for properties that represent channel data or
    similar properties where an expession like

        dso.property[index] = value

    makes sense.
    """
    def __init__(
            self, command, doc, indexes, value_type, write_command=None,
            proxy_type=_ArrayDevicePropertyProxy):
        super().__init__(command, doc, read_only=True)
        self.indexes = indexes
        self.value_type = value_type
        self.write_command = write_command
        self.proxy_type = proxy_type

    def getter(self, dso):
        return self.proxy_type(
            dso, self.indexes, self.value_type, self.command,
            self.write_command)


class _SavedChannelScaleOffset:
    """Context manager used by TriggerModeSettings classes to preserve
    channel settings.

    Restores channel scale and offset after
    _TriggerLevelForModeProperty.from_config_value() may have changed
    these parameters.

    The context manager can be entered recursively and restores the values
    only in its outmost invocation.
    """
    dso_data = {}

    def __init__(self, dso):
        self.dso = dso

    def __enter__(self):
        if self.dso in self.dso_data:
            self.dso_data[self.dso]['called'] += 1
        else:
            self.dso_data[self.dso] = {
                'called': 1,
                'settings': {
                    ch: (self.dso.channel[ch].scale,
                         self.dso.channel[ch].offset)
                    for ch in ChannelNumber
                    },
                }

    def __exit__(self, *exc_args):
        self.dso_data[self.dso]['called'] -= 1
        if not self.dso_data[self.dso]['called']:
            for ch in ChannelNumber:
                scale, offset = self.dso_data[self.dso]['settings'][ch]
                self.dso.channel[ch].scale = scale
                self.dso.channel[ch].offset = offset
            del self.dso_data[self.dso]
        return False


class TriggerModeSettings:
    """Common base class for trigger mode settings."""
    def __init__(self, dso):
        self._dso = dso

    def get_config(self):
        return {
            key: getattr(self.__class__, key).as_config_value(self)
            for key in self._config_attrs
            }

    def set_config(self, config):
        """Set the trigger mode parameters from a dictionary `config` as
        returned by get_config()`.

        See `get_config()` for recognized keys.
        """
        with _SavedChannelScaleOffset(self._dso):
            for key in self._config_attrs:
                if key in config:
                    getattr(self.__class__, key).from_config_value(
                        self, config[key])


class TriggerModeSettingsEdge(TriggerModeSettings):
    """Properties available for the trigger mode "edge".
    """
    _trigger_mode = TriggerMode.edge
    source = _TriggerSourceForModeProperty(_trigger_mode)
    level = _TriggerLevelForModeProperty(_trigger_mode)
    sweep = _SweepForTriggerModeProperty(_trigger_mode)
    coupling = _TriggerCouplingForTriggerModeProperty(_trigger_mode)

    # XXX The parameter ":TRIGger:EDGE:SLOPe".
    # So... We have on one hand a trigger _mode_ called "slope", and in the
    # trigger mode "edge" we can specify a setting named "slope". This usage
    # of one term with different meanings in closely related contexts is,
    # well, at least confusing if not insane.
    # But at least there isn't something like ":TRIGger:SLOPe:EDGE"...
    #
    # I really do not like to implement
    #
    #    dso.trigger.edge.slope
    #
    # when there is also stuff like
    #
    #    dso.trigger.slope.some_property
    #
    # What is a good synonym in this context for slope? direction? gradient?
    # Does not sound really convincing... So keeping for now the confusing
    # term "slope".
    slope = _TriggerSlopeForTriggerModeProperty(_trigger_mode)
    sensitivity = _TriggerSensitivityProperty(_trigger_mode)
    _config_attrs = (
        'source', 'coupling', 'sweep', 'level', 'slope', 'sensitivity')

    def get_config(self):
        """Return a dictionary with all settings of trigger mode `edge`.

        The keys of the dictionary are these property names:

        `source`, `coupling`, `sweep`, `level`, `slope`, `sensitivity`

        The values are of type `int`, `float` or `bool` for properties of
        the same type. For properties having an Enum type, the names of
        of the current Enum item is returned.

        The return value can be serialized as JSON, YAML etc.
        """
        return super().get_config()


class TriggerModeSettingsPulse(TriggerModeSettings):
    _trigger_mode = TriggerMode.pulse
    source = _TriggerSourceForModeProperty(_trigger_mode)
    level = _TriggerLevelForModeProperty(_trigger_mode)
    sweep = _SweepForTriggerModeProperty(_trigger_mode)
    coupling = _TriggerCouplingForTriggerModeProperty(_trigger_mode)
    time_condition = _TriggerPulseTimeConditionProperty(_trigger_mode)
    time_condition_value = _TriggerPulseTimeConditionValueProperty(
        _trigger_mode)
    sensitivity = _TriggerSensitivityProperty(_trigger_mode)
    _config_attrs = (
        'source', 'coupling', 'sweep', 'level', 'sensitivity',
        'time_condition', 'time_condition_value')

    def get_config(self):
        """Return a dictionary with all settings of trigger mode `pulse`.

        The keys of the dictionary are these property names:

        `source`, `coupling`, `sweep`, `level`, `sensitivity`,
        `time_condition`, `time_condition_value`

        The values are of type `int`, `float` or `bool` for properties of
        the same type. For properties having an Enum type, the names of
        of the current Enum item is returned.

        The return value can be serialized as JSON, YAML etc.
        """
        return super().get_config()


class TriggerModeSettingsVideo(TriggerModeSettings):
    _trigger_mode = TriggerMode.video
    source = _TriggerSourceForModeProperty(_trigger_mode)
    level = _TriggerLevelForModeProperty(_trigger_mode)
    # XXX At least for now, no "sweep" attribute for Video: Not mentioned
    # on page 35 of the Programming Guide. The sweep mode can be set though
    # via the panel... A quick test by uncommenting the line below shows
    # that the command ":TRIG:SLOPE:SWEEP?" simply times out.
    # sweep = _SweepForTriggerModeProperty(_trigger_mode)

    # Though not explicitly mentioned on page 36 of the Programming Guide,
    # the coupling mode can't be set for video trigger mode. (Makes sense
    # since the old fashioned analog video signal is quite special.)
    # coupling = _TriggerCouplingForTriggerModeProperty(_trigger_mode)
    sync = _TriggerVideoSyncProperty(_trigger_mode)
    polarity = _TriggerVideoPolarityProperty(_trigger_mode)
    standard = _TriggerVideoStandardProperty(_trigger_mode)
    line = _TriggerVideoLineProperty(_trigger_mode)
    sensitivity = _TriggerSensitivityProperty(_trigger_mode)
    _config_attrs = (
        'source', 'level', 'sensitivity', 'sync', 'polarity', 'standard',
        'line')

    def get_config(self):
        """Return a dictionary with all settings of trigger mode `video`.

        The keys of the dictionary are these property names:

        `source`, `level`, `sensitivity`, `sync`, `polarity`, `standard`,
        `line`.

        The values are of type `int`, `float` or `bool` for properties of
        the same type. For properties having an Enum type, the names of
        of the current Enum item is returned.

        The return value can be serialized as JSON, YAML etc.
        """
        return super().get_config()


class TriggerModeSettingsSlope(TriggerModeSettings):
    _trigger_mode = TriggerMode.slope
    source = _TriggerSourceForModeProperty(_trigger_mode)
    # No level property for mode pulse.
    sweep = _SweepForTriggerModeProperty(_trigger_mode)
    coupling = _TriggerCouplingForTriggerModeProperty(_trigger_mode)
    time_condition_value = _TriggerSlopeTimeProperty(_trigger_mode)
    sensitivity = _TriggerSensitivityProperty(_trigger_mode)
    time_condition = _TriggerSlopeTimeConditionProperty(_trigger_mode)
    voltage_level_lower = _TriggerSlopeLevelLower()
    voltage_level_upper = _TriggerSlopeLevelUpper()
    _config_attrs = (
        'source', 'coupling', 'sweep', 'sensitivity', 'time_condition',
        'time_condition_value', 'voltage_levels')
    voltage_levels = TriggerSlopeVoltageLevelsProperty()

    def get_config(self):
        """Return a dictionary with all settings of trigger mode `slope`.

        The keys of the dictionary are these property names:

        `source`, `coupling`, `sweep`, `sensitivity`, `time_condition`,
        `time_condition_value`, `voltage_levels`.

        The values are of type `int`, `float` or `bool` for properties of
        the same type. For properties having an Enum type, the names of
        of the current Enum item is returned.

        The return value can be serialized as JSON, YAML etc.
        """
        return super().get_config()


class TriggerModeSettingsAlternation(TriggerModeSettings):
    _trigger_mode = TriggerMode.alternation
    source = _TriggerSourceForModeProperty(_trigger_mode)

    def get_config(self):
        """Return a dictionary with all settings of trigger mode `slope`.

        Since the trigger mode `alternation` is not yet supported, an empty
        dicitonary is returned.
        """
        return {}

    def set_config(self, config):
        # Nothing to do for now.
        pass


class Trigger:
    """Container for trigger related properties and methods.

    Trigger provides the following properties which are not related
    to a certain trigger mode:

    `mode`: The currently selected trigger mode;
    `status`: The current trigger status;
    `holdoff`: The trigger holfoff time.

    "Sub-Containers" for properties related to specific trigger modes:

    `edge`, `pulse`, `video`, `slope`, `alternation`.

    This class has two methods: `force()` which forces a trigger event
    and `set_50_percent()` which sets the trigger level to the "middle"
    of the trigger signal.

    This class is used as the attribute `trigger` of class DS1052.

    Specific trigger modes can be accessed either as attributes,
    e.g. Trigger.edge or Trigger.video, or via the "dictionary protocol"
    where the keys are instances of the Enum TriggerMode.

    Usage examples:

    >>> dso = DS1052()
    >>> dso.open()
    >>> dso.trigger.edge.level
    0.46
    >>> dso.trigger[TriggerMode.edge].sweep
    Sweep.normal
    >>> dso.trigger.mode
    TriggerMode.edge
    >>> dso.trigger[dso.trigger.mode].sweep
    Sweep.single

    Each trigger mode provides different properties; for details about
    available properties see `class TriggerModeSettingsEdge',
    `class TriggerModeSettingsPulse', `class TriggerModeSettingsVideo',
    `class TriggerModeSettingsSlope', `class TriggerModeSettingsAlternation',

    Examples for dictionary-like access:

    >>> dso.trigger.keys()
    <aenum 'TriggerMode'>
    >>> dso.trigger.values()
    <generator object Trigger.values at 0x7fb710940660>
    >>> list(dso.trigger.values())
    [<ds1052.TriggerModeSettingsEdge object at 0x7fb710e4bdf0>,
    <ds1052.TriggerModeSettingsPulse object at 0x7fb710e4bee0>,
    <ds1052.TriggerModeSettingsVideo object at 0x7fb710e4bfd0>,
    <ds1052.TriggerModeSettingsSlope object at 0x7fb710e4bf40>,
    <ds1052.TriggerModeSettingsAlternation object at 0x7fb710e4bfa0>]
    >>> dso.trigger.items()
    <generator object Trigger.items at 0x7fb710940dd0>

    Other properties of this class are not available via "dictionary access".
    """
    _trigger_mode_names = [tr_mode.name for tr_mode in TriggerMode]
    _trigger_mode_classes = {
        TriggerMode.edge: TriggerModeSettingsEdge,
        TriggerMode.pulse: TriggerModeSettingsPulse,
        TriggerMode.video: TriggerModeSettingsVideo,
        TriggerMode.slope: TriggerModeSettingsSlope,
        TriggerMode.alternation: TriggerModeSettingsAlternation,
        }

    def __init__(self, dso):
        self._dso = dso
        for tr_mode in TriggerMode:
            setattr(
                self, f'_{tr_mode.name}',
                self._trigger_mode_classes[tr_mode](dso))

    def __getitem__(self, key):
        result = self.get(key)
        if result is not None:
            return result
        raise KeyError(f'Invalid trigger mode key: {key!r}')

    def __contains__(self, key):
        # The string lookup must come first - Enum.__contains__() bails out
        # when callled with a str oarameter.
        return key in self._trigger_mode_names or key in TriggerMode

    def __len__(self):
        return len(TriggerMode)

    def __iter__(self):
        return TriggerMode.__iter__()

    @property
    def edge(self):
        """Properties available for the trigger mode "edge".

        See `class TriggerModeSettingsEdge` for details.
        """
        return self._edge

    @property
    def pulse(self):
        """Properties available for the trigger mode "edge".

        See `class TriggerModeSettingsPulse` for details.
        """
        return self._pulse

    @property
    def video(self):
        """Properties available for the trigger mode "edge".

        See `class TriggerModeSettingsVideo` for details.
        """
        return self._video

    @property
    def slope(self):
        """Properties available for the trigger mode "edge".

        See `class TriggerModeSettingsSlope` for details.
        """
        return self._slope

    @property
    def alternation(self):
        """Properties available for the trigger mode "edge".

        See `class TriggerModeSettingsAlternation` for details.
        """
        return self._alternation

    def get(self, key, default=None):
        if isinstance(key, TriggerMode):
            return getattr(self, key.name)
        if key in self._trigger_mode_names:
            return getattr(self, key)
        return default

    def items(self):
        for key in TriggerMode:
            yield key, self[key]

    def keys(self):
        return TriggerMode

    def values(self):
        for key in TriggerMode:
            yield self[key]

    mode = _TriggerModeProperty()
    status = _TriggerStatusProperty()
    holdoff = _TriggerHoldoffProperty()

    def force(self):
        """Force a trigger event."""
        self._dso._tmc_device.write(':FORCETRIG')

    def set_50_percent(self):
        """Set the trigger level to the midpoint of the waveform."""
        self._dso._tmc_device.write(':TRIG%50')
        # Wait until the DSO has finally figured out the new value.
        # Sigh. Another case where "*OPC?" would be really useful.
        # Experimentation shows that a waiting time of 0.01s is not enough.
        # 0.05 seems to work, but let's stay on the safe side.
        sleep(0.1)

    config_attrs = ('mode', 'holdoff')
    def get_config(self):
        """Return a dictionary `config` with all trigger settings.

        The keys of `config` are the property names `mode`, `holdoff`

        and the trigger mode names `edge`, `pulse`, `video`, `slope`,
        `alternation`.

        The value of `mode` is one of the strings `edge`, `pulse`, `video`,
        `slope`, `alternation`, the value of `holdoff` is a float, and the
        values for the keys `edge`, `pulse`, `video`, `slope`, `alternation`
        are the results of the method `get_config()?  calls of the classes
        `TriggerModeSettingsEdge`, `TriggerModeSettingsPulse`,
        `TriggerModeSettingsVideo`, `TriggerModeSettingsSlope`,
        `TriggerModeSettingsAlternation`.
        """
        result = {
            name: getattr(Trigger, name).as_config_value(self)
            for name in self.config_attrs
            }
        for name in self._trigger_mode_names:
            result[name] = self[name].get_config()
        return result

    def set_config(self, config):
        """Set the trigger parameters from a dictionary `config` as
        returned by get_config()`.

        See `get_config()` for recognized keys.
        """
        for name in self.config_attrs:
            if name in config:
                getattr(Trigger, name).from_config_value(self, config[name])
        with _SavedChannelScaleOffset(self._dso):
            for name in self._trigger_mode_names:
                if name in config:
                    self[name].set_config(config[name])


class _PropertyConverterBase:
    def as_config_value(self, value):
        return value

    def from_config_value(self, value):
        return value


class _PropertyFloatConverter(_PropertyConverterBase):
    """Convert between a string <numstr> and a Python float.

    <numstr> is a tring representing a numerical value as needed or
    provided by the DS1052.

    `max_value` and `min_value`, if provided, give limits for conversion
    Python float -> <numstr>.
    """
    def __init__(self, min_value=None, max_value=None, digits=4):
        self.min_value = min_value
        self.max_value = max_value
        self.digits = digits

    def from_device_value(self, device_value):
        return float(device_value)

    def to_device_value(self, py_value, _):
        if not isinstance(py_value, float):
            py_value = float(py_value)
        if self.max_value is not None and py_value > self.max_value:
            raise DS1052PropertyValueError(
                f'Only values less than or equal to {self.max_value} allowed.')
        if self.min_value is not None and py_value < self.min_value:
            raise DS1052PropertyValueError(
                f'Only values greater than or equal to {self.min_value} '
                f'allowed.')
        return _float_format(py_value, self.digits)


class MeasurementQualifier(Enum):
    """Qualifier for measurement values.

    Measurement properties like signal frequency or rise time are tuples
    `(value, qualifier)`, where `value` is the numerical value returned
    by the DS1052 and `qualifier` is in instance of this enum.

    Under certain conditions the DS1052 cannot measure signal parameters
    with sufficient precision. In that case it returns a number prefixed
    by '<' or '>'. When this happens, accessing the associarted properties
    returns `(value, MeasurementQualifier.less_than)` or
    `(value, MeasurementQualifier.greater_than)`, respectively. For regular
    values (i.e., without a leading '<' or '>'),
    `(value, MeasurementQualifier.value)` is returned.

    In some situations the DS1052 returns the measurement value 9.9e37.
    This value is obviously not within the range of voltages, frequencies
    or times, specified in V or Hz or s, that can be really measured.

    This value seems to indicate that the DS1052 is (temporarily?) not able
    to perform the requested measurement. If this value is seen, it is
    converted to `math.inf`; -99e37 is converted to `-math.inf`; the
    qualifier is in both cases `MeasurementQualifier.infinite`.

    (The documentation of the DS1052 does not mention the "special"
    measurement values described here; their meaning is purely divined
    by the author of the module based on observations of the DS1052's
    behaviour.)
    """
    value = 'value',
    less_than = 'less than'
    greater_than = 'greater than'
    infinite = 'infinite'


class _MeasurementPropertyFloatConverter:
    """Convert between a string <numstr> to a tuple
    `(float_value, qualifier)`.

    Variant for measurement values received from the DS1052.

    `float_value` is a float number, `qualifier` is an instance of
    `MeasurementQualifier`.

    The data received from the DS1052 for a measurement Vpp is a string
    that represents a float value in one the formats accepted by a
    Python `float()` call.

    This "number string" may be prefixed by a '<' or '>' sign. This
    indicates that the DS1052 could not measure the given value with
    sufficient precision and the only available information is "the value
    is less/greater than...".

    Sometimes the DS1052 returns the number 9.9e37 as a measurement value
    which obviously does not make sense as a value of a voltage, time or
    frequency measurement. (Except perhaps as the "period time" of a DC
    signal. The author has not yet seen this case though.) This seems to
    be a hint from the DS1052 that the desired measurement cannot be
    reliably made at the moment.

    When the string returned by the DS1052 represents a float value,
    it is converted into the tuple (float_value, MeasurementQualifier.value);
    when the string is prefixed by a '<' or '>', it is converted into
    the tuple (float_value, MeasurementQualifier.less_than) or
    ((float_value, MeasurementQualifier.greater_than), respectively;
    "9.9e37" is converted into (math.inf, MeasurementQualifier.infinity);
    "-9.9e37" is converted into (-math.inf, MeasurementQualifier.infinity);
    """
    def from_device_value(self, device_value):
        if device_value.startswith('<'):
            qualifier = MeasurementQualifier.less_than
            device_value = device_value[1:]
        elif device_value.startswith('>'):
            qualifier = MeasurementQualifier.greater_than
            device_value = device_value[1:]
        else:
            qualifier = MeasurementQualifier.value
        py_value = float(device_value)
        if py_value == 9.9e37:
            return inf, MeasurementQualifier.infinite
        elif py_value == -9.9e37:
            return -inf, MeasurementQualifier.infinite
        return py_value, qualifier

    def to_device_value(self, py_value, _):
        # Properties using this converter are supposed to be read-only.
        raise DS1052PropertyValueError('Cannot set a measurement value')


class _ChannelScaleConverter(_PropertyFloatConverter):
    # Allowed scale values depend on the probe attenuation.
    valid_scale_values = {
        1: (0.002, 10.0),
        5: (0.01, 50.0),
        10: (0.02, 100.0),
        20: (0.04, 200.0),
        50: (0.1, 500.0),
        100: (0.2, 1000.0),
        200: (0.4, 2000.0),
        500: (1.0, 5000.0),
        1000: (2.0, 10000.0),
        }

    def to_device_value(self, py_value, channel):
        # Possible values depend on the attenuation setting.
        # Interestingly, the DS1052 allows "non-standard" settings like
        # 0.234V/div
        attenuation = channel.probe_attenuation
        min_val, max_val = self.valid_scale_values[channel.probe_attenuation]
        if not min_val <= py_value <= max_val:
            raise DS1052PropertyValueError(
                f'Invalid scale setting {py_value}. Allowed for probe '
                f'attenuation {attenuation}: {min_val} .. {max_val}')
        return super().to_device_value(py_value, channel)


class _ChannelOffsetConverter(_PropertyFloatConverter):

    def to_device_value(self, py_value, channel):
        # Possible values depend on the scale setting.
        min_value, max_value = channel.offset_range
        if min_value <= py_value <= max_value:
            return super().to_device_value(py_value, channel)
        raise DS1052PropertyValueError(
            f'Invalid offset {py_value}. Allowed for scale {channel.scale} '
            f'are values between {-max_value} and {max_value}.')


class _PropertyBoolConverter(_PropertyConverterBase):
    """Convert between the strings "ON" and "OFF" and a Python bool.
    """
    str2bool = {
        'ON': True,
        'OFF': False,
        }
    bool2str = {
        True: 'ON',
        False: 'OFF',
        }

    def __init__(self, device_read_values=None, device_write_values=None):
        if device_read_values is not None:
            self.str2bool = device_read_values
        if device_write_values is not None:
            self.bool2str = device_write_values

    def from_device_value(self, device_value):
        if device_value not in self.str2bool:
            raise RuntimeError(
                f'Unexpected device value for a bool parameter:'
                f' {device_value!r}')
        return self.str2bool[device_value]

    def to_device_value(self, py_value, _):
        py_value = bool(py_value)
        return self.bool2str[py_value]

    def as_read_value(self, value):
        return bool(value)


class _PropertyEnumConverter:
    def __init__(self, enum, setter_values={}):
        self.enum = enum
        self.setter_values = setter_values

    def from_device_value(self, device_value):
        return self.enum(device_value)

    def to_device_value(self, py_value, _):
        if not isinstance(py_value, self.enum):
            raise DS1052PropertyValueError(
                f'Expected an instance of {self.enum}, not {type(py_value)}')
        if py_value in self.setter_values:
            return self.setter_values[py_value]
        else:
            return py_value.value

    def as_read_value(self, value):
        return value

    def as_config_value(self, value):
        return value.name

    def from_config_value(self, new_value):
        try:
            return getattr(self.enum, new_value)
        except (TypeError, AttributeError):
            # TypeError is raised if new_value is not a str.
            raise DS1052PropertyValueError(
                f'{new_value!r} is not a valid enum value of {self.enum}')


class _PropertyIntChoiceConverter(_PropertyConverterBase):
    def __init__(self, choices):
        self.choices = choices

    def from_device_value(self, device_value):
        # Interesting: ":CHAN2:PROB?" returns value likes "1.000e+01"
        # and these can't be directly cast into ints.
        return int(float(device_value))

    def to_device_value(self, py_value, _):
        if py_value not in self.choices:
            raise DS1052PropertyValueError(
                f'Invalid value: {py_value!r}. Allowed: {self.choices}')
        return str(py_value)

    def as_read_value(self, value):
        return value


class _PropertyIntConverter:
    def from_device_value(self, device_value):
        return int(device_value)

    def to_device_value(self, py_value, _):
        return str(py_value)

    def as_read_value(self, value):
        return value


class _ChannelProperty(property):
    def __init__(self, command, doc, type_converter, read_only=False):
        self.command = command
        self.type_converter = type_converter
        if read_only:
            super().__init__(self.getter, doc=doc)
        else:
            super().__init__(self.getter, self.setter, doc=doc)
        # XXX the "doc=doc" parameter in the __init__() calls above should,
        # AIUI, specify a doc string for this property. But a call of
        # "help(ds1052.Channel)" does not show any details about this
        # property. But with the line below things are. What is wrong here?
        self.__doc__ = doc

    def getter(self, channel):
        return self.type_converter.from_device_value(
            channel._dso._tmc_device.ask(
                self.command.format(
                    channel=channel._channel_no, rw='?', new_value='')))

    def setter(self, channel, new_value):
        # Check if the current value is already equal to `new_value`.
        # Since _PropertyBoolConverter casts new_value into a bool value,
        # let the type converter tell which value to expect in a getter()
        # call.
        if self.type_converter.as_read_value(new_value)== self.getter(channel):
            return
        message = self.command.format(
            channel=channel._channel_no, rw='',
            new_value=self.type_converter.to_device_value(
                new_value, channel))
        channel._dso._tmc_device.write(message)
        _wait_until_property_set(partial(self.getter, channel), new_value)
        channel._dso._update_read_source_delay()

    def as_config_value(self, channel):
        return self.type_converter.as_config_value(self.getter(channel))

    def from_config_value(self, channel, new_value):
        new_value = self.type_converter.from_config_value(new_value)
        self.setter(channel, new_value)


class _ChannelFilterProperty(_ChannelProperty):
    """Do not allow changes when the DS1052 is in STOP mode.

    The property channel[...].filter_enabled seems to be the only property
    having this limitation.
    """
    def setter(self, channel, new_value):
        if (
                channel._dso.trigger.status == TriggerStatus.stop
                and new_value != self.getter(channel)):
            raise DS1052PropertySetError(
                'The channel filter cannot be enabled or disabled in stop '
                'mode.')
        super().setter(channel, new_value)


class _ChannelFloatProperty(_ChannelProperty):
    def setter(self, channel, new_value):
        write_value, read_value = self.type_converter.to_device_value(
            new_value, channel)
        if float(read_value) == self.getter(channel):
            return
        write_message = self.command.format(
            channel=channel._channel_no, rw='', new_value=write_value)
        read_message = self.command.format(
            channel=channel._channel_no, rw='?', new_value='')
        _write_check_float_value(
            channel._dso, write_message, read_message, read_value)
        channel._dso._update_read_source_delay()

class Channel:
    """Channel related settings."""
    def __init__(self, dso, channel_no):
        self._dso = dso
        self._channel_no = channel_no

    # Seems that the sampling rate shows the value for the last acquisition;
    # probably not immediately updated when the time base settings are changed.
    acquisition_sampling_rate = _ChannelProperty(
        ':ACQ:SAMP? CHAN{channel}',
        """Sampling rate of channel 1 or 2 in 1/s.

        type: float.
        """,
        _PropertyFloatConverter(), read_only=True)

    # --------------- Measurement commands ------------------
    voltage_pp = _ChannelProperty(
        ':MEAS:VPP? {channel}',
        """Peak to peak voltage of channel 1 or 2 in V.

        type: `(float, MeasurementQualifier)`.

        See also `MeasurementQualifier`.
        """,
        _MeasurementPropertyFloatConverter(), read_only=True)

    voltage_max = _ChannelProperty(
        ':MEAS:VMAX? {channel}',
        """Maximum voltage of channel 1 or 2 in V.

        type: `(float, MeasurementQualifier)`.

        See also `MeasurementQualifier`.
        """,
        _MeasurementPropertyFloatConverter(), read_only=True)

    voltage_min = _ChannelProperty(
        ':MEAS:VMIN? {channel}',
        """Minimum voltage of channel 1 or 2 in V.

        type: `(float, MeasurementQualifier)`.

        See also `MeasurementQualifier`.
        """,
        _MeasurementPropertyFloatConverter(), read_only=True)

    amplitude = _ChannelProperty(
        ':MEAS:VAMP? {channel}',
        """Amplitude of channel 1 or 2 in V.

        type: `(float, MeasurementQualifier)`.

        See also `MeasurementQualifier`.
        """,
        _MeasurementPropertyFloatConverter(), read_only=True)

    voltage_top = _ChannelProperty(
        ':MEAS:VTOP? {channel}',
        """Top voltage of channel 1 or 2 in V.

        type: `(float, MeasurementQualifier)`.

        See also `MeasurementQualifier`.
        """,
        _MeasurementPropertyFloatConverter(), read_only=True)

    voltage_base = _ChannelProperty(
        ':MEAS:VBAS? {channel}',
        """Base voltage of channel 1 or 2 in V.

        type: `(float, MeasurementQualifier)`.

        See also `MeasurementQualifier`.
        """,
        _MeasurementPropertyFloatConverter(), read_only=True)

    voltage_average = _ChannelProperty(
        ':MEAS:VAV? {channel}',
        """Average voltage of channel 1 or 2 in V.

        type: `(float, MeasurementQualifier)`.

        See also `MeasurementQualifier`.
        """,
        _MeasurementPropertyFloatConverter(), read_only=True)

    voltage_rms = _ChannelProperty(
        ':MEAS:VRMS? {channel}',
        """RMS voltage of channel 1 or 2 in V.

        type: `(float, MeasurementQualifier)`.

        See also `MeasurementQualifier`.
        """,
        _MeasurementPropertyFloatConverter(), read_only=True)

    voltage_overshoot = _ChannelProperty(
        ':MEAS:OVER? {channel}',
        """Overshoot voltage of channel 1 or 2 in V.

        type: `(float, MeasurementQualifier)`.

        See also `MeasurementQualifier`.
        """,
        _MeasurementPropertyFloatConverter(), read_only=True)

    voltage_preshoot = _ChannelProperty(
        ':MEAS:PRES? {channel}',
        """Overshoot voltage of channel 1 or 2 in V.

        type: `(float, MeasurementQualifier)`.

        See also `MeasurementQualifier`.
        """,
        _MeasurementPropertyFloatConverter(), read_only=True)

    frequency = _ChannelProperty(
        ':MEAS:FREQ? {channel}',
        """Frequency of channel 1 or 2 in Hz.

        type: `(float, MeasurementQualifier)`.

        See also `MeasurementQualifier`.
        """,
        _MeasurementPropertyFloatConverter(), read_only=True)

    rise_time = _ChannelProperty(
        ':MEAS:RIS? {channel}',
        """Rise time of channel 1 or 2 in s.

        type: `(float, MeasurementQualifier)`.

        See also `MeasurementQualifier`.
        """,
        _MeasurementPropertyFloatConverter(), read_only=True)

    fall_time = _ChannelProperty(
        ':MEAS:FALL? {channel}',
        """l time of channel 1 or 2 in s.

        type: `(float, MeasurementQualifier)`.

        See also `MeasurementQualifier`.
        """   ,
        _MeasurementPropertyFloatConverter(), read_only=True)

    period = _ChannelProperty(
        ':MEAS:PER? {channel}',
        """Period of channel 1 or 2 in s.

        type: `(float, MeasurementQualifier)`.

        See also `MeasurementQualifier`.
        """,
        _MeasurementPropertyFloatConverter(), read_only=True)

    positive_pulse_width = _ChannelProperty(
        ':MEAS:PWID? {channel}',
        """Positive pulse width of channel 1 or 2 in s.

        type: `(float, MeasurementQualifier)`.

        See also `MeasurementQualifier`.
        """,
        _MeasurementPropertyFloatConverter(), read_only=True)

    negative_pulse_width = _ChannelProperty(
        ':MEAS:NWID? {channel}',
        """Negative pulse width of channel 1 or 2 in s.

        type: `(float, MeasurementQualifier)`.

        See also `MeasurementQualifier`.
        """,
        _MeasurementPropertyFloatConverter(), read_only=True)

    positive_duty_cycle = _ChannelProperty(
        ':MEAS:PDUT? {channel}',
        """Positive duty cycle of channel 1 or 2 in s.

        type: `(float, MeasurementQualifier)`.

        See also `MeasurementQualifier`.
        """,
        _MeasurementPropertyFloatConverter(), read_only=True)

    negative_duty_cycle = _ChannelProperty(
        ':MEAS:NDUT? {channel}',
        """Negative duty cycle of channel 1 or 2 in s.

        type: `(float, MeasurementQualifier)`.

        See also `MeasurementQualifier`.
        """,
        _MeasurementPropertyFloatConverter(), read_only=True)

    # XXX Neither the user manual nor the programming manual are clear
    # what kind of delay is measured here: Delay of the edge relative to
    # the trigger time? Delay between the edges of the channels?
    # "Experiments" to figure out what is meant postponded...
    positive_edge_delay = _ChannelProperty(
        ':MEAS:PDEL? {channel}',
        '''"the delay relative to rising edge of channel1 or channel 2."
        (Quote from the "Programming Guide DS1000E, DS1000D")

        type: `(float, MeasurementQualifier)`.

        See also `MeasurementQualifier`.
        ''',
        _MeasurementPropertyFloatConverter(), read_only=True)

    negative_edge_delay = _ChannelProperty(
        ':MEAS:NDEL? {channel}',
        '''"the delay relative to rising edge of channel1 or channel 2."
        (Quote from the "Programming Guide DS1000E, DS1000D")

        type: `(float, MeasurementQualifier)`.

        See also `MeasurementQualifier`.
        ''',
        _MeasurementPropertyFloatConverter(), read_only=True)

    bandwidth_limit_enabled = _ChannelProperty(
        ':CHAN{channel}:BWLIMIT{rw} {new_value}',
        """True if the bandwidth limit of the channel is enabled else False.

        type: bool.
        """,
        _PropertyBoolConverter())

    coupling = _ChannelProperty(
        ':CHAN{channel}:COUP{rw} {new_value}',
        """The signal coupling of the channel.

        type: Enum ChannelCoupling.
        """,
        _PropertyEnumConverter(ChannelCoupling))

    enabled = _ChannelProperty(
        ':CHAN{channel}:DISP{rw} {new_value}',
        """True if the channel is enabled else False.

        type: bool.
        """,
        # Sigh... The DS1052 returns '1' or '0' for ':CHAN1:DISP? ',
        # not 'ON' or 'OFF' like for other "boolean" settings.
        _PropertyBoolConverter(device_read_values={'1': True, '0':False}))

    # XXX Not yet known: Does this setting also affect the data retrieved
    # via USB? The doc string should be accoringly changed if this is
    # the case. Also: Does this setting affect the "math" operations?
    display_inverted = _ChannelProperty(
        ':CHAN{channel}:INV{rw} {new_value}',
        """True if the channel is inverted the display else False.

        type: bool.
        """,
        _PropertyBoolConverter())

    probe_attenuation = _ChannelProperty(
        ':CHAN{channel}:PROB{rw} {new_value}',
        """Attenuation of the channel's probe.

        Allowed values: 1, 5, 10, 20, 50, 100, 200, 500, 1000

        type: int
        """,
        _PropertyIntChoiceConverter((1, 5, 10, 20, 50, 100, 200, 500, 1000)))

    offset = _ChannelFloatProperty(
        ':CHAN{channel}:OFFS{rw} {new_value}',
        """Offset of the channel in V.

        Allowed values:
        -2V .. +2V when the channel's scale is less than 250mV/div;
        -40V .. +40V when the channel's scale is greater than or equal to
        250mV/div.

        type: float.
        """,
        _ChannelOffsetConverter())

    scale = _ChannelFloatProperty(
        ':CHAN{channel}:SCAL{rw} {new_value}',
        """Scale of the channel display in V/div.

        Allowed values depend on the probe's attenuation:

        attenuation     min scale       max scale
        1               0.002 V/div     10 V/div
        5               0.01 V/div      50 V(div
        10              0.02 V/div      100 V/div
        20              0.04 V/div      200 V/div
        50              0.1 V/div       500 V(div
        100             0.2 V/div       1000 V/div
        200             0.4 V/div       2000 V/div
        500             1 V/div         5000 V(div
        1000            2 V/div         10000 V/div

        type: float.
        """,
        _ChannelScaleConverter())

    # XXX What are the commands to set the filter parameters?
    filter_enabled = _ChannelFilterProperty(
        ':CHAN{channel}:FILT{rw} {new_value}',
        """True if the digital filter of the channel is enabled else False.

        type: bool.

        This property can only be set when the DS1062 is not in STOP mode.
        Attempts to set it in STOP mode lead to a DS1052PropertySetError.
        """,
        _PropertyBoolConverter(device_write_values={True: '1', False: '0'}))

    # XXX This seems to be the memory depth of the last data acquisition.
    # Needs a bit more testing until I am sufficiently sure. Anyway,
    # the doc string should be updated if this assumption is true.
    memory_depth = _ChannelProperty(
        ':CHAN{channel}:MEMORYDEPTH{rw}',
        """Memory depth of the channel.

        This is the number of bytes of the last data acquisition.

        type: int.
        """,
        _PropertyIntConverter(),
        read_only=True)

    vernier = _ChannelProperty(
        ':CHAN{channel}:VERN{rw} {new_value}',
        """Enable/disable the fine adjustement of the channel's scale via
        the "scale" knob on the DS1052 panel.

        type: Enum ChannelVernier
        """,
        _PropertyEnumConverter(
            ChannelVernier, setter_values={
                ChannelVernier.coarse: 'OFF',
                ChannelVernier.fine: 'ON',
            }))

    @property
    def scale_range(self):
        """A tuple (min_scale, max_scale): Possible scale values for
        the actual channel's probe attenuation setting.
        """
        return _ChannelScaleConverter.valid_scale_values[self.probe_attenuation]

    @property
    def offset_range(self):
        """A tuple (min_offset, max_offset): Possible offset values for
        the actual channel's scale and probe attenuation setting.
        """
        scale = self.scale
        attenuation = self.probe_attenuation
        max_value = 40.0 if scale / attenuation >= 0.25 else 2.0
        max_value *= attenuation
        return (-max_value, max_value)

    @property
    def trigger_level_range(self):
        """A tuple (min_level, max_level): Possible tirgger level values for
        the actual channel's scale and probe attenuation setting.
        """
        scale = self.scale
        offset = self.offset
        return (-6 * scale - offset, 6 * scale - offset)

    # Configuration properties. set_config() sets the properties in the
    # order listed here. `probe_attenuation` must be set first since it
    # defines the range of possible values of `scale`. `scale` is set
    # before offset because `scale` defines the range of possible values of
    # `offset`.
    config_attrs = (
        'probe_attenuation',
        'scale',
        'offset',
        'bandwidth_limit_enabled',
        'coupling',
        'display_inverted',
        'enabled',
        'filter_enabled',
        'vernier',
        )

    def get_config(self):
        """Return a dictionary with all settings of a channel.

        The keys of the dictionary are these property names:

            `probe_attenuation`,
            `scale`,
            `offset`,
            `bandwidth_limit_enabled`,
            `coupling`,
            `display_inverted`,
            `enabled`,
            `filter_enabled`,
            `vernier`

        The values are of type `int`, `float` or `bool` for properties of
        the same type. For properties having an Enum type, the names of
        of the current Enum item is returned.

        The return value can be serialized as JSON, YAML etc.
        """
        return {
            name: getattr(self.__class__, name).as_config_value(self)
            for name in self.config_attrs
            }

    def set_config(self, config):
        """Set the channel parameters from a dictionary `config` as returned by
        `get_config()`.

        See `get_config()` for recognized keys.
        """
        for name in self.config_attrs:
            if name in config:
                # The "filter_enabled" flag can only be changed when the DSO
                # is running.
                dso_start_needed = (
                    name == 'filter_enabled'
                    and self._dso.trigger.status == TriggerStatus.stop
                    and self.filter_enabled != config[name])
                if dso_start_needed:
                    self._dso.wait_until_running()
                getattr(self.__class__, name).from_config_value(
                    self, config[name])
                if dso_start_needed:
                    self._dso.wait_until_stopped()


class _Channels:
    """Channel related settings.

    Provides access to channel related properties via key lookup:

        >>> dso = DS1052()
        >>> dso.open()
        >>> dso.channel[1].acquisition_sampling_rate

    See `class Channel` for details about available properties.
    """
    def __init__(self, dso):
        self._dso = dso
        self._channels = {key: Channel(dso, key) for key in ChannelNumber}

    def _normalize_key(self, key):
        if isinstance(key, ChannelNumber):
            return key
        if isinstance(key, TriggerSource):
            # Allow "shortcuts" from trigger source to channel. A bit risky
            # do this since a value like TriggerSource.external will raise
            # a key error but it makes application code a bit simpler.
            #
            # Yes, this works: key is _also_ an integer.
            return ChannelNumber(key)
        if isinstance(key, IntEnum):
            # Any other enum type indicates a semantic problem.
            raise KeyError('Not a valid channel index: {key!r}')
        if isinstance(key, int):
            # Assume that a channel number is menat.
            return ChannelNumber(key)
        raise KeyError('Not a valid channel index: {key!r}')

    def __getitem__(self, key):
        key = self._normalize_key(key)
        return self._channels[key]

    def get_config(self):
        return {
            int(channel): self._channels[channel].get_config()
            for channel in ChannelNumber}

    def set_config(self, config):
        for channel in ChannelNumber:
            if channel in config:
                self._channels[channel].set_config(config[channel])


class DS1052:
    """Control a DS1052 oscilloscope.

    DS1052.open() must be called before the DSO can be accessed; when the
    DSO is no longer needed, DS1052.close() should be called.

    Instances of this class can also be used as a context manager to call
    open()/close() automatically.

    Constructor parameters (all are optional):
    `serial`: The serial number of the DSO. Must be specified if more than
        one device with the USB vendor ID 0x1ab1 and the product ID 0x0588
        is connected to the host.
    `tmc_class`: The name of the TMC class (which implements communication
        with the DS1052 on the USBTMC protocol layer) to use. Available
        options:
        PyUsbTmcInstrument, LkUsbTmcInstrument, PyVisaInstrument.
        (defined in ds1052.tmc)

        PyUsbTmcInstrument requires the installation of the Python package
        `python-usbtmc`.
        LkUsbTmcInstrument uses the `usbtmc` Linux kernel driver.
        PyVisaInstrument requires the installation of the Python package
        PyVISA and of a backend for PyVISA. See
        https://pyvisa.readthedocs.io/en/latest/introduction/getting.html
        for more details.

    `resource_manager`: The pyvisa resource manager to use. Only meaningful if
        the PyVisaInstrument TMC class is passed as tmc_class.
    """
    def __init__(self, serial=None, tmc_class=None, resource_manager=None):
        self.serial = serial
        self._trigger = Trigger(self)
        self._channels = _Channels(self)
        self._tmc_class = tmc_class
        self._resource_manager = resource_manager
        self._read_wave_time = time()

    # If defined as a property, we can sneak the doc string of class Trigger
    # into the doc of class DS1052.
    @property
    def trigger(self):
        return self._trigger

    trigger.__doc__ = Trigger.__doc__

    @property
    def channel(self):
        return self._channels

    channel.__doc__ = _Channels.__doc__

    def open(self):
        """Establish the USB connection to the DS1052."""
        self._tmc_device = get_tmc_device(
            self.serial, self._tmc_class, self._resource_manager)
        self.vendor, self.model, self.serial, self.sw_version = self._get_idn()

    def close(self):
        """Close the USB connection to the DS1052."""
        # The Rigol DS1052 locks its keyboard when it is remote controlled.
        # Makes probably sense but the need to explicit unlock for direct
        # usage again is annoying. Do it here instead.
        self._tmc_device.write(':key:force')
        self._tmc_device.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *exc_args):
        self.close()
        return False

    def _get_idn(self):
        result = self._tmc_device.ask('*IDN?')
        return result.split(',')

    def reset(self):
        """Reset the device.

        (Not yet implemented.)
        """
        # xxx need some more stuff running to see what reset does exactly..
        # *RST
        raise NotImplementedError

    def run(self):
        """Start the aquisition mode."""
        self._tmc_device.write(':RUN')
        self._update_read_source_delay()

    def stop(self):
        """Stop the aquisition mode."""
        self._tmc_device.write(':STOP')

    def auto(self):
        """Let the DSO find good operating parameters for the waveforms.

        Equivalent to pressing the "Auto" button the front panel.
        Note that this operation needs several seconds; the duration
        depends on the input signals. It is unclear how or if the progress
        of the command execution can be observed by reading trigger status,
        vertical scale or timebase scale.
        """
        self._tmc_device.write(':AUTO')
        self._update_read_source_delay()

    def hard_copy(self):
        """Save a screenshot on a USB drive connected to tghe DSO."""
        self._tmc_device.write(':HARD')

    def screenshot(self):
        """Return a screenshot of the DS1052's display.

        The Linux `file` utility identifies it as "PC bitmap, Windows 3.x
        format, 320 x 234 x 8, resolution 2250 x 2250 px/m, cbSize 75958,
        bits offset 1078".

        Usage example:

            from io import BytesIO
            from PIL import Image
            from ds1052 import DS1052

            with DS1052() as dso:
                screenshot = dso.screenshot()
                # Save as a file.
                with open('screenshot.bmp', 'wb') as f:
                    f.write(screenshot)
                # Create a PIL image object and show it.
                img = Image.open(BytesIO(screenshot))
                img.show()

        """
        return self._tmc_device.ask_raw(b':DISP:DATA?', 75968)[10:]

    def clear_display(self):
        """Clears out data waveforms from the screen."""
        self._tmc_device.write(':DISP:CLEAR')

    acquisition_type = _EnumDeviceProperty(
        AcquisitionType, ':ACQ:TYPE',
        'Acquisition type. Allowed values are instances of '
        '`class AcquisitionType`.',
        {AcquisitionType.peak_detect: 'PEAKDETECT'})

    acquisition_mode = _EnumDeviceProperty(
        AcquisitionMode, ':ACQ:MODE',
        'Acquisition mode. Allowed values are instances of '
        '`class AcquisitionMode`.',
        {AcquisitionMode.real_time: 'RTIM',
         AcquisitionMode.equal_time: 'ETIM'})

    acquisition_averages = _IntChoicesDeviceProperty(
        ':ACQ:AVER',
        f'Number of samples to average. Allowed values: '
        f'{", ".join(str(2**i) for i in range(1, 9))}.',
        [2**i for i in range(1, 9)], typecast=int)

    # Sigh... The manual claims on page 2-9 that the command could
    # be given as ":ACQ:MEMD?" for reading. That yields no response.
    # Even ":ACQ:MEMDept" does not workfrom the device... Pure trial
    # and error needed to figure out what works...
    acquisition_memory_depth = _EnumDeviceProperty(
        AcquisitionMemoryDepth, ':ACQ:MEMDEPTH',
        'Acquisition memory depth. Allowed values are instances of '
        '`class AcquisitionMemoryDepth`.')

    display_type = _EnumDeviceProperty(
        DisplayType, ':DISP:TYPE',
        'Display type. Allowed values are instances of `class DisplayType`.')

    display_grid = _EnumDeviceProperty(
        DisplayGrid, ':DISP:GRID',
        'Type of the grid shown on the display. Allowed values are '
        'instances of `class DisplayGrid`.')

    display_persistence = _BoolDeviceProperty(
        ':DISP:PERSIST',
        'Display persistence: `True` -> Do not erase old waveforms from\n'
        'the display, `False` -> erase the last waveform when a new one\n'
        'is shown.')


    _display_menu_time_py_to_dev = dict((t, str(t)) for t in (1, 2, 5, 10, 20))
    # No lower case chars when setting this value.
    _display_menu_time_py_to_dev[-1] = 'INFINITE'
    _display_menu_time_dev_to_py = dict((f'{t}s', t) for t in (1, 2, 5, 10, 20))
    _display_menu_time_dev_to_py['Infinite'] = -1
    _display_menu_time_doc = """The time in seconds the display menu is shown.

        Allowed values: 1, 2, 5, 10, 20, -1, where -1 means that the menu
        is never automatically hidden.
        """

    display_menu_time = _MappedProperty(
        ':DISP:MNUD', _display_menu_time_doc, _display_menu_time_dev_to_py,
        _display_menu_time_py_to_dev)

    display_menu_status = _BoolDeviceProperty(
        ':DISP:MNUSTATUS',
        'Status of the display menu: Hidden -> `False`, shown -> `True`')

    display_brightness = _IntChoicesDeviceProperty(
        ':DISP:BRIG',
        f'Display brightness. Allowed values: 0..32', list(range(33)),
        typecast=int)

    display_intensity = _IntChoicesDeviceProperty(
        ':DISP:INT',
        f'Display intensity. Allowed values: 0..32', list(range(33)),
        typecast=int)

    timebase_mode = _EnumDeviceProperty(
        TimebaseMode, ':TIM:MODE',
        'Timebase mode. Allowed values are instances of `class TimebaseMode`.')

    # Sigh. We can't abbreviate 'TIMEBASE'.
    # XXX Figure out what the exact constraints of the offset are and
    # raise a dedicated exception.
    # The possible minimum value is quite straightforward to guess:
    # The larger the absolute value of the offset, the more data stored
    # from the time before the trigger event. And the amount of the stored
    # data obviously cannot exceed the available storage. The max positive
    # value is not yet clear to me.
    # Interestingly, the DS1052 accepts more values in STOP mode than in
    # RUN mode...
    timebase_offset = _FloatDeviceProperty(
        ':TIMEBASE:OFFSET',
        """Main time base offset in s (type float).

        The possible minimum and maximum values depend on the timebase scale
        and memory depth.
        """,
        min_value=-500., max_value=500.)

    # XXX Disabled 2022-06-15: This property is not needed for pure remote
    # control of the DS1052: It has no effect on the data gathered by the
    # oscilloscope. The delayed timebase simply offers a zoomed view into
    # the data. OTOH, it turns out that the delayed timebase offset can only
    # be changed when the delayed timebase is enabled...
    # A proper implementation would "know" about the conditions when the
    # offset can be set. But that requires a dedicated property class,
    # derived from _FloatProperty. That's currently not worth the effort.
    #delayed_timebase_offset = _FloatDeviceProperty(
    #    ':TIMEBASE:DELAYED:OFFSET',
    #    'Delayed time base offset in s (type float).',
    #    min_value=-500., max_value=500, digits=5)

    _timebase_scale_values_1052 = (
        5e-9,
        1e-8, 2e-8, 5e-8, 1e-7, 2e-7, 5e-7, 1e-6, 2e-6, 5e-6,
        1e-5, 2e-5, 5e-5, 1e-4, 2e-4, 5e-4, 1e-3, 2e-3, 5e-3,
        1e-2, 2e-2, 5e-2, 1e-1, 2e-1, 5e-1, 1e+0, 2e+0, 5e+0,
        1e+1, 2e+1, 5e+1, )

    _timebase_scale_values_1102 = (2e-9, ) + _timebase_scale_values_1052

    @property
    def _timebase_scale_values(self):
        if self.model.startswith('DS1102'):
            return self._timebase_scale_values_1102
        return _timebase_scale_values_1052

    timebase_scale = _FloatChoicesDeviceProperty(
        ':TIMEBASE:SCALE',
        f'Time base scale in s/div (type float).\n'
        f'Allowed values: '
        f'{", ".join(str(x) for x in _timebase_scale_values_1052)}\n'
        f'The DS1102 supported also the value 2e-9.',
        _timebase_scale_values, typecast=float)

    # XXX Disabled 2022-06-15. See above, delayed_timebase_offset, for the
    # reason.
    #delayed_timebase_scale = _FloatChoicesDeviceProperty(
    #    ':TIMEBASE:DELAYED:SCALE',
    #    f'Time base scale in s/div (type float).'
    #    f'Allowed values: {", ".join(str(x) for x in _timebase_scale_values)}',
    #    _timebase_scale_values)

    timebase_format = _EnumDeviceProperty(
        TimebaseFormat, ':TIM:FORM',
        'Timebase format. Allowed values are instances of '
        '`class TimebaseFormat`.',
        {TimebaseFormat.x_y: 'XY', TimebaseFormat.y_t: 'YT'})

    beep_enabled = _BoolDeviceProperty(
        ':BEEP:ENAB', 'Beep enabled. Allowed values are `False`, `True`')

    display_all_measurements = _BoolDeviceProperty(
        ':MEAS:TOT',
        'Show/hide all measuements. Allowed values are `False`, `True`')

    points_mode = _EnumDeviceProperty(
        PointsMode, ':WAV:POINTS:MODE',
        """Points mode for data acquisition.

        This property determines the number of data points returned by a
        call of `read_waveforms_raw()` for channel data when the DS1052 is in
        TriggerMode.stop.

        number of       acquisition     points          data points
        enabled         memory          mode
        channels        depth

        2               normal          max, raw        8192
        2               long            max, raw        524288
        1               normal          max, raw        16384
        1               long            max, raw        1048576
        0               normal          max, raw        8192
        0               long            max, raw        524288

        In all other cases `read_waveforms_raw()` returns 600 data points
        per channel. Other cases are one the following:

        - the DS1052 is in any trigger state other that TriggerState.stop
          The settings of points_mode and acquisition_memory_depth do not
          matter in this case.
        - points_mode is set to PointMode.normal.

        Allowed values are instances of class `PointsMode`.

        NOTE: With firmware version 00.04.04, perhaps also other
        more recent versions, read_waveforms_raw() does not work with
        acquisition memory depth "long".

        While the acquisition memory can be set to "long", the author
        is currently not able to properly test how well memory mode "long"
        works with other firmware versions. Hence "long memory" mode is
        not properly supported. Expect problems that are either caused
        by a strange behaviour of the DS1052 or by errors in this code
        that are unfortunately not reproducible by the autor of this
        module.
        """)

    # --------------- "Math" commands ------------------
    #
    # XXX Not worth an implementation right now: They just affect
    # what is shown on the display of the device.
    # (Programming guide page 79)

    def _normalize_source(self, source):
        if isinstance(source, ChannelNumber):
            return source
        if type(source) == int:
            return ChannelNumber(source)
        if isinstance(source, TriggerSource) and int(source) > 0:
            return ChannelNumber(source)
        raise ValueError(f'Not a valid data source type: {source!r}')

    # IIRC, better not use the short form "CHAN1",  "CHAN2".
    # Not recognized at least by older firmware versions.
    _source2name = {
        ChannelNumber.channel1: 'CHANNEL1',
        ChannelNumber.channel2: 'CHANNEL2',
        }

    def _read_source(self, source):
        """Read the waveform of the given source (channel 1 or 2)."""
        # `_read_wave_time` and `sleep(delta_t)`:
        #
        # Under certain conditions the ask_raw() call in this method hangs
        # waiting for the DS1052 to send the wave data, but the DS1052 doe
        # not respond: It must be power-cycled to get it working again.
        # The exact conditions under which this hanging happens are not
        # clear.
        #
        # The idea to add a sleep() call come from looking at Wireshark data
        # of the communication between Rigol's own Ultrascope software and
        # the DS1052: That program wait 0.12 seconds between each and every
        # command sent to the DS1052.
        #
        # Sigrok's module for Rigol's DS1000 DSOs uses a similar delay,
        # as can be seen here:
        # https://github.com/sigrokproject/libsigrok/blob/ffd150decfdde9c1bcfc291f633ac6aa91f140b3/src/hardware/rigol-ds/protocol.c#L329
        # (Seen while reading the sources of commit ffd150d.)
        #
        # I also emailed Rigol with questions about the necessity for this
        # kind of delays but did not get an answer that clarifies which
        # conditions require this delay. The advice was more like "well,
        # just use the delays everywhere"...
        #
        # On the other hand, the tests of this library and the library itself
        # send SCPI commands to the DS1052 without any delay or with much
        # shorter delays. And this method is the only place where the DS1052
        # tends to hang when an SCPI command is sent without delay to the
        # previously sent command.
        #
        # Moreover, some tests, like test_timebase_zero_point(), issue
        # a larger number of ":WAV:DATA?" commands, interspersed with some
        # other SCPI commands. If these tests cause the DS1052 to hang,
        # the hanging happens for the first ":WAV:DATA?" command; if
        # the first ":WAV:DATA?" succeeds, the following ":WAV:DATA?"
        # commands succeed too, even when there is no sleep() call in
        # this method.
        #
        # This suggests that this 0.1 second delay before a ":WAV:DATA?"
        # command might be necessary only when a parameter is changed.
        # Hence the setter() methods of all properties set the attribute
        # `_read_wave_time` to time() + 0.1, and this method can sleep()
        # until this point in time has passed before it sends the
        # ":WAV:DATA?" command.
        #
        # This avoids unnecessary waiting if no parameter was changed between
        # two calls of this method.
        #sleep(0.1)
        delta_t = self._read_wave_time - time()
        if delta_t > 0.0001:
            sleep(delta_t)

        # The first 10 bytes are a header "announcing" the length of the data.
        count = self.channel[source].memory_depth + 10
        result = self._tmc_device.ask_raw(
            f':WAV:DATA? {self._source2name[source]}'.encode('ascii'), count)
        # Expected header is '#nmmmmm..' where 'n' is a 1-digit int specifying
        # the number of the following digits 'm'. The digits 'm' specify
        # the length of the following data.
        if result[:1] != b'#':
            raise ValueError(f'Unexpected data header: {result[:20]!r}')
        try:
            header_len = int(result[1:2])
            data_size = int(result[2:2+header_len])
        except ValueError:
            # XXX It becomes more and more urgent to define "specialized"
            # execptions for this module.
            raise ValueError(f'Unexpected data header: {result[:20]!r}')
        expected_datasize = 2 + header_len + data_size
        if len(result) != expected_datasize:
            raise ValueError(
                f'Unexpected data size. Got {len(result)}, '
                f'expected {expected_datasize}. Header: {result[:20]!r}')
        return result[2+header_len:]

    def read_waveforms_raw(self, sources, points_mode):
        """Acquire waveforms from the given sources in the given points_mode.

        `sources` is either a single source specification or a sequence
        of source specifications.

        A source specification is an instance of class `ChannelNumber`, an
        integer representing a channel number (i.e., 1 or 2), or
        TriggerSource.channel1 or TriggerSource.channel2.

        `points_mode` is the PointsMode to use.

        The data is returned as a list
        `[(source1, data_from_source1), (source2, data_from_source2)...]`
        where `data_from_source1`, `data_from_source2` etc are `bytes`
        instances containing the raw data as returned by the DS1052 and
        `source1`, `source2` are the channel numbers provided as `sources`.

        NOTE 1: With firmware version 00.04.04, perhaps also other
        more recent versions, read_waveforms_raw() does not work with
        acquisition memory depth "long". Because this library was developed
        with a DS1052E running firmware version 00.04.04,
        read_waveforms_raw() is not tested in "long" memory depth, aside
        from a check that attempts to run it just lead to a timeout.

        NOTE 2: According to Rigol's "Programming Guide DS1000E, DS1000D
        Series Digital Oscilloscope" page 81 it should be possible
        to retrieve the data types "MATH" and "FFT" in alle three
        PointsMode variants (normal, max, raw). Working on this method,
        I only get timeout errors for attempte to retrieve "MATH" and
        "FFT" data in PointsMode.raw and PointsMode.max when the DS1052
        is in TriggerMode.stop.

        So, while "FFT" and "MATH" data are retrievable when the
        DS1052 is not stopped or when only PointsMode.normal is
        requested, it is not worth the time and effort to get all
        the conditions "when is it possible to retrieve MATH or FFT
        data?" properly implemented and tested. This should not be a
        serious usage problem, since SciPy and NumPy provide the same
        features as the DS1052's "MATH" and "FFT" functions – and much
        more.
        """
        if not isinstance(points_mode, PointsMode):
            raise ValueError(
                f'points_mode must be an instance of PointsMode, not {mode!r}')
        if not isinstance(sources, Sequence):
            sources = (sources, )
        self.points_mode = points_mode
        return [
            (ch, self._read_source(ch))
            for ch in (self._normalize_source(ch) for ch in sources)]

    def read_waveforms(self, sources, points_mode):
        """Acquire waveforms from the given sources in the given points_mode.

        `sources` is either a single source specification or a sequence
        of source specifications.

        A source specification is an instance of class `ChannelNumber`, an
        integer representing a channel number (i.e., 1 or 2), or
        TriggerSource.channel1 or TriggerSource.channel2.

        `points_mode` is the PointsMode to use.

        The data is returned as a list
        [data_from_source1, data_from_source2...]
        where the elements are instances of `class Waveform`.
        """
        if self.trigger.mode == TriggerMode.alternation:
            # Problem: The regular timebase data is not used in
            # alternating trigger mode since the timebase data is
            # set independently for the channels.
            raise NotImplementedError(
                'TriggerMode.alternation is not yet supported')
        tb_scale = self.timebase_scale
        tb_offset = self.timebase_offset
        return [
            Waveform(
                raw, ch, tb_scale, tb_offset, self.channel[ch].scale,
                self.channel[ch].offset,
                self.channel[ch].acquisition_sampling_rate)
            for ch, raw in self.read_waveforms_raw(sources, points_mode)]

    default_run_trigger_states = set(TriggerStatus) - {TriggerStatus.stop}

    def wait_until_running(self, expected_trigger_states=None, timeout=1.0):
        """Wait until the DS1052 is in one of `expected_trigger_states`.

        The method run() is called first, if the DS1052 is in
        TriggerState.stop.

        If specified, `expected_trigger_states` must be a set or sequence
        of `TriggerStatus` instances. The default value is the set of all
        TriggerStatus values except TriggerStatus.stop.

        This is a convenience method that tries to cope with the difficulties
        to track the DS1052's trigger status via SCPI commands.

        The main challenge, especially in sweep mode "single": When a ":RUN"
        command is issued while the DS1052 is in "STOP" mode, the device
        returns "STOP" for a short time when queried ":TRIG:STAT?", before
        it begins to return "RUN", again only during a short time, after
        which it returns either "WAIT" or "triggered", depending on the
        actual trigger signal and the trigger settings. After a trigger
        event the DS1052 will finally return into trigger status STOP when
        in sweep mode "single".

        So, to retrieve the waveforms recorded by a single trigger event,
        it is necessary to issue a ":RUN" command, then query the trigger
        status until "STOP" mode is reached, before finally read_waveforms()
        or read_waveforms_raw() can be called.

        All these transitions of the trigger status can occur in a few
        milliseconds. A desktop OS does not give any real time guarantees,
        so it can easily happen that the latency between issueing the
        ":RUN" command and the first ":TRIG:STAT?" query is long enough
        that the short lived "STOP" state that is returned immediately after
        the ":RUN" command is missed.

        If TriggerStatus.stop is included in `expected_trigger_states`, it
        is considered as "condition fulfilled" if it is "seen" after more
        than 0.1 seconds, or if any other status has been "seen" before.
        """
        if expected_trigger_states is None:
            expected_trigger_states = self.default_run_trigger_states
        if TriggerStatus.stop in expected_trigger_states:
            early_conditions = set(expected_trigger_states)
            early_conditions.remove(TriggerStatus.stop)
        else:
            early_conditions = None
        # No need to call run() if the DS1052 is already running.
        if self.trigger.status == TriggerStatus.stop:
            self.run()
        else:
            early_conditions = None
        started = time()
        # Shortly after a run() call, self.trigger.status may still be "STOP",
        # before it switches into "RUN". This "STOP" status is not yet the
        # status mentioned in `expected_trigger_states`. Only when some
        # other trigger status was seen, it is sure that the DS1052 indeed
        # left TriggerStatus.stop. On the other hand the while loop below
        # can miss completely the states "run" and "triggered" of the trigger
        # state sequence "stop -> run -> triggered -> stop" when running
        # on a slow machine that is under heay load. Hence the loop runs for
        # at most 0.1 seconds. After this time, the DS1052 should have
        # really left the initial "stop" state and it is safe to assume
        # that a "stop" status now indicates the end of the sequence.
        tr_stat = self.trigger.status
        if early_conditions is not None:
            while time() < started + 0.1:
                if tr_stat in early_conditions:
                    return
                if tr_stat != TriggerStatus.stop:
                    # The DS1052 left the inital "stop" state. From now on,
                    # all expected trigger states can be checked.
                    break
                sleep(0.005)
                tr_stat = self.trigger.status
        while time() < started + timeout:
            if tr_stat in expected_trigger_states:
                return
            sleep(0.005)
            tr_stat = self.trigger.status
        raise DS1052TimeoutError(
            f'Timeout while waiting for one of the trigger states '
            f'{" ,".join(str(st) for st in expected_trigger_states)}. '
            f'Last seen: {tr_stat}')

    def wait_until_stopped(self, timeout=1.0):
        """Call stop() and wait until the DS1052 is in TriggerStatus.stop
        mode.

        After a `stop()` call, the DS1052 needs a certain time until it
        enters TriggerStatus.stop mode. Until this happens, calls for
        example of `read_waveforms_raw(1, PointsMode.raw)` will return
        only 600 data points, not 8192 or more, as expected in
        TriggerStatus.stop mode.
        """
        self.stop()
        wait_until = time() + timeout
        tr_stat = self.trigger.status
        while tr_stat != TriggerStatus.stop and time() < wait_until:
            sleep(0.05)
            tr_stat = self.trigger.status
        if tr_stat != TriggerStatus.stop:
            raise DS1052TimeoutError(
                f"Timeout waiting for TriggerStatus.stop. Last seen: {tr_stat}")

    def _update_read_source_delay(self, wait=0.1):
        """An attempt to avoid this terrible sleep(0.1) call in _read_source().

        _read_source() waits, if necessary, until the "time point"
        self._read_wave_time has come before sending the ":WAV:DATA?"
        command.

        See the comment at the start of _read_source() for more details.
        """
        self._read_wave_time = max(self._read_wave_time, time() + wait)

    config_attrs = (
        'acquisition_type', 'acquisition_mode', 'acquisition_averages',
        'acquisition_memory_depth', 'display_type', 'display_grid',
        'display_persistence', 'display_menu_time', 'display_menu_status',
        'display_brightness', 'display_intensity', 'timebase_mode',
        'timebase_offset', 'timebase_scale', 'timebase_format',
        'beep_enabled', 'display_all_measurements', 'points_mode')

    def get_config(self):
        """Return a dictionary `config` with all settings of the DS1052.

        The keys of `config` are these property names:

            `acquisition_type`
            `acquisition_mode`
            `acquisition_averages`
            `acquisition_memory_depth`
            `display_type`
            `display_grid`
            `display_persistence`
            `display_menu_time`
            `display_menu_status`
            `display_brightness`
            `display_intensity`
            `timebase_mode`
            `timebase_offset`
            `timebase_scale`
            `timebase_format`
            `beep_enabled`
            `display_all_measurements`
            `points_mode`

        The values are of type `int`, `float` or `bool` for properties of
        the same type. For properties having an Enum type, the names of
        of the current Enum item is returned. (Example: The value of
        timebase_mode can be `'main'` or `'delayed'` because
        `class TimebaseMode` provides two Enum members of this name.

        The value of key `channel` of `config` is a dictionary

            {1: <channel 1 config>, 2: <channel 2 config>}

        where <channel N config> is the result of `Channel.get_config()`.

        The return value can be serialized as JSON, YAML etc.
        """
        result = {
            name: getattr(self.__class__, name).as_config_value(self)
            for name in self.config_attrs
            }
        result['channel'] = self._channels.get_config()
        result['trigger'] = self.trigger.get_config()
        return result

    def set_config(self, config):
        """Set the DS1052 parameters from a dictionary `config` as returned by
        `get_config()`.

        See `get_config()` for recognized keys.
        """
        for name in self.config_attrs:
            if name in config:
                getattr(self.__class__, name).from_config_value(
                    self, config[name])
        if 'channel' in config:
            self._channels.set_config(config['channel'])
        if 'trigger' in config:
            self.trigger.set_config(config['trigger'])


class Waveform:
    """Container for waveform related data.

    Provides the waveform and the related time data as numpy arrays as
    properties `v` and `t`, respectively.

    Relevant parameters from the data acquistion are available in these
    attributes:

    `raw_waveform`: An object of type `bytes`, containing the raw acquisition
        data as returned by the DS1052.
    `channel_no`: The channel number.
    `tb_scale`: The timebase scale in V/div.
    `tb_offset` : The timebase offset in s.
    `v_scale`: The vertical scale in V/div.
    `v_offset`: The vertical offset in V.
    `sample_rate`: The sample rate in 1/s.

    Instances of this class should not be created directly by an application.
    Instead, DS1052.read_waveforms() should be used.
    """
    # Conversion of voltage and time follows this guide:
    # https://rigol.force.com/support/s/article/DS1000E-Waveform-Data-Formatting-Guide
    # (except where that document seems to be wrong.)
    def __init__(
            self, raw_waveform, channel_no, tb_scale, tb_offset, v_scale,
            v_offset, sample_rate):
        self.raw_waveform = raw_waveform
        self.channel_no = channel_no
        self.tb_scale = tb_scale
        self.tb_offset = tb_offset
        self.v_scale = v_scale
        self.v_offset = v_offset
        self.sample_rate = sample_rate
        self._t = None
        self._v = None

    @property
    def v(self):
        """The voltage of the waveform (Unit: V) as a numpy.array.
        """
        if self._v is None:
            v = np.frombuffer(self.raw_waveform, dtype=np.uint8)
            v_scale = self.v_scale / 25
            v_offset = self.v_offset + self.v_scale * 4.6
            self._v = (240 - v) * v_scale - v_offset
        return self._v

    def _t_linspace(self, retstep):
        n_points = len(self.raw_waveform)
        if n_points == 600:
            start = - self.tb_scale * 6 + self.tb_offset
            stop = self.tb_scale * 6 + self.tb_offset
            return np.linspace(
                start, stop, n_points, endpoint=False, retstep=retstep)
        else:
            # Hrm. Copy&paste quote from Rigol's FAQ mentioned above:
            #
            # T(s) = <Time_Offset> -[ (<Points> - 10) / (1 / (2*<Samp_Rate>)]
            #
            # Aside from the fact that there should be one more ')' to the
            # left of the closing ']':
            #
            # The "double division" (<Points> - 10) / (1 / (2*<Samp_Rate>)
            # does not make sense. And the multiplication "2*<Samp_Rate>"
            # looks suspicious too. After all, the value <Samp_Rate> should
            # be in Hz (or 1/s), so a simple division 1/sample_rate
            # should give the "time step" in seconds. Or am I missing
            # something?
            # But the whole equation does not make sense, at least if my
            # assumption is right that "<Points>" means a value between
            # 0 and 8191 (for a two-channel measurement), i.e. an index,
            # increasing with time, of the data points.
            #
            # Let's take a "sanitized" version without the "double division"
            # of the sample rate:
            #
            # T(s) = time_offset - (s - 10) / sample_rate
            #
            # With the settings of the DS1052 after a press on the "AUTO"
            # when the probe adjustment signal (1 kHz square wave) is
            # connected to CH1 and CH2, we get a sample rate of 500000/s,
            # a time offset of 0 and we see a bit more than 16 cycles of
            # the signal in the data.
            # With this sample rate, (s-10) / sample_rate would range from
            # -10/500000 to 8181 / 500000; if these values are subtracted
            # from time offset (zero), most values would be for the time
            # _before_ the trigger event. But that's not the case: Half
            # of the data is before the trigger time, half is after the
            # trigger time. (OK: the number "10" in Rigols's formula may
            # be a hint that there is a constant small "horizontal shift".)
            #
            # Anyway, test_timebase_zero_point() shows that the timebase
            # calculation is straightforward, at least for lower sampling
            # rates:
            #
            # With 8192 recorded data points and a zero time offset, t=0
            # is at index 4095 (i.e, N/2-1); the step size is obviously
            # 1/sample_rate. A positive timebase offset moves t=0 to a
            # lower index. (Can't test for "long memory" due to the buggy
            # 00.04.04 firmware...)
            #
            # For higher sample rates, the index for t=0 might be slightly
            # shifted from the index 4095, due to some latency. Some sort
            # of latency is, I assume, the reason for the constant 10 in
            # Rigol's formula. OTOH I might be looking at a red herring.
            # Proper checking needs a much faster test signal. Postponed
            # for now.

            total_time = n_points / self.sample_rate
            storage_offset = (n_points / 2 - 1) / self.sample_rate
            start = self.tb_offset - storage_offset
            end = start + total_time
            return np.linspace(
                start, end, n_points, endpoint=False, retstep=retstep)

    @property
    def t(self):
        """Time data of the waveform in seconds, as a numpy.array.

        The value 0 is the time of the trigger event.
        """
        if self._t is None:
            self._t = self._t_linspace(False)
        return self._t
