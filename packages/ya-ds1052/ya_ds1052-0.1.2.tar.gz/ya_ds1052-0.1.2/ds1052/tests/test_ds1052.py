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

from collections import namedtuple
from contextlib import contextmanager, ExitStack
from io import BytesIO
from math import inf, sqrt
import numpy as np
import os
from PIL import Image
from time import sleep, time
from unittest import skip, SkipTest, TestCase
from unittest.mock import patch
import usb
import sys

from ds1052 import (
    _float_format,
    AcquisitionMemoryDepth, AcquisitionMode, AcquisitionType,
    ChannelCoupling, ChannelNumber, ChannelVernier, DisplayGrid,
    DisplayType,
    DS1052, IntEnum, MeasurementQualifier,
    PointsMode, Slope, Sweep,
    TimebaseFormat, TimebaseMode,
    TriggerCoupling, TriggerMode, TriggerModeSettings,
    TriggerSource, TriggerStatus, TriggerTimeCondition,
    VideoStandard,
    VideoTriggerPolarity,
    VideoTriggerSyncType,
    Waveform,
    )
from ds1052.exceptions import (
    DS1052InitError, DS1052PropertySetError, DS1052PropertyValueError,
    DS1052TimeoutError,
    )
# Access needed at least to _FloatDeviceProperty.
import ds1052


TMC_CLASS = os.getenv('TMC_CLASS', None)
if TMC_CLASS is None:
    TMC_CLASS = 'PyUsbTmcInstrument'
    print('TMC_CLASS not set: using PyUsbTmcInstrument')
if ds1052.tmc.pyvisa is not None:
    # VSIA_RM should be either 'py' or 'ivi'.
    VISA_RM = os.getenv('VISA_RM', 'py')
    visa_rm = ds1052.tmc.pyvisa.ResourceManager('@' + VISA_RM)
else:
    visa_rm = None


class HelpersTest(TestCase):
    """test of miscellaneous helper functions.
    """
    def test_float_format(self):
        self.assertEqual(('0.0', '0.000e+00'), _float_format(0.0, 4))
        self.assertEqual(('0.1234', '1.234e-01'), _float_format(0.12341, 4))
        self.assertEqual(('-0.1234', '-1.234e-01'), _float_format(-0.12341, 4))
        self.assertEqual(('0.01234', '1.234e-02'), _float_format(1.234e-2, 4))
        self.assertEqual(
            ('-0.01234', '-1.234e-02'), _float_format(-1.234e-2, 4))
        self.assertEqual(('0.001234', '1.234e-03'), _float_format(1.234e-3, 4))
        self.assertEqual(
            ('-0.001234', '-1.234e-03'), _float_format(-1.234e-3, 4))
        self.assertEqual(
            ('0.0001234', '1.234e-04'), _float_format(1.234e-4, 4))
        self.assertEqual(
            ('-0.0001234', '-1.234e-04'), _float_format(-1.234e-4, 4))
        self.assertEqual(
            ('0.00001234', '1.234e-05'), _float_format(1.234e-5, 4))
        self.assertEqual(
            ('-0.00001234', '-1.234e-05'), _float_format(-1.234e-5, 4))
        self.assertEqual(
            ('0.000001234', '1.234e-06'), _float_format(1.234e-6, 4))
        self.assertEqual(
            ('-0.000001234', '-1.234e-06'), _float_format(-1.234e-6, 4))
        self.assertEqual(
            ('0.0000001234', '1.234e-07'), _float_format(1.234e-7, 4))
        self.assertEqual(
            ('-0.0000001234', '-1.234e-07'), _float_format(-1.234e-7, 4))
        self.assertEqual(
            ('0.00000001234', '1.234e-08'), _float_format(1.234e-8, 4))
        self.assertEqual(
            ('-0.00000001234', '-1.234e-08'), _float_format(-1.234e-8, 4))
        self.assertEqual(
            ('0.000000001234', '1.234e-09'), _float_format(1.234e-9, 4))
        self.assertEqual(
            ('-0.000000001234', '-1.234e-09'), _float_format(-1.234e-9, 4))
        self.assertEqual(
            ('0.0000000001234', '1.234e-10'), _float_format(1.234e-10, 4))
        self.assertEqual(
            ('-0.0000000001234', '-1.234e-10'), _float_format(-1.234e-10, 4))

        self.assertEqual(('1.2340', '1.234e+00'), _float_format(1.234e0, 4))
        self.assertEqual(('-1.2340', '-1.234e+00'), _float_format(-1.234e0, 4))
        self.assertEqual(('12.340', '1.234e+01'), _float_format(1.234e1, 4))
        self.assertEqual(('-12.340', '-1.234e+01'), _float_format(-1.234e1, 4))
        self.assertEqual(('123.40', '1.234e+02'), _float_format(1.234e2, 4))
        self.assertEqual(('-123.40', '-1.234e+02'), _float_format(-1.234e2, 4))
        self.assertEqual(('1234.0', '1.234e+03'), _float_format(1.234e3, 4))
        self.assertEqual(('-1234.0', '-1.234e+03'), _float_format(-1.234e3, 4))
        self.assertEqual(('12340', '1.234e+04'), _float_format(1.234e4, 4))
        self.assertEqual(('-12340', '-1.234e+04'), _float_format(-1.234e4, 4))
        self.assertEqual(('123400', '1.234e+05'), _float_format(1.234e5, 4))
        self.assertEqual(('-123400', '-1.234e+05'), _float_format(-1.234e5, 4))
        self.assertEqual(('1234000', '1.234e+06'), _float_format(1.234e6, 4))
        self.assertEqual(('-1234000', '-1.234e+06'), _float_format(-1.234e6, 4))

        self.assertEqual(('1.346', '1.35e+00'), _float_format(1.3456, 3))

    def test_MeasurementPropertyFloatConverter_from_device_value(self):
        conv = ds1052._MeasurementPropertyFloatConverter()
        # Texts representing float numbers are converted into
        # (float_value, MeasurementQualifier.value)
        value, qualifier = conv.from_device_value('1.234')
        self.assertEqual(1.234, value)
        self.assertEqual(MeasurementQualifier.value, qualifier)
        value, qualifier = conv.from_device_value('-3.45e-4')
        self.assertEqual(-0.000345, value)
        self.assertEqual(MeasurementQualifier.value, qualifier)
        # Strings starting with "<", followed by a number are converted
        # into (float_value, MeasurementQualifier.less_than)
        value, qualifier = conv.from_device_value('<7.45')
        self.assertEqual(7.45, value)
        self.assertEqual(MeasurementQualifier.less_than, qualifier)
        value, qualifier = conv.from_device_value('<-42.')
        self.assertEqual(-42, value)
        self.assertEqual(MeasurementQualifier.less_than, qualifier)
        # Strings starting with ">", followed by a number are converted
        # into (float_value, MeasurementQualifier.greater_than)
        value, qualifier = conv.from_device_value('>5.467e+05')
        self.assertEqual(546700, value)
        self.assertEqual(MeasurementQualifier.greater_than, qualifier)
        # Strings starting with ">", followed by a number are converted
        # into (float_value, MeasurementQualifier.greater_than)
        value, qualifier = conv.from_device_value('>-0.876')
        self.assertEqual(-0.876, value)
        self.assertEqual(MeasurementQualifier.greater_than, qualifier)
        # The "magic values" 9.9e38 is converted into
        # (math.inf, MeasurementQualifier.greater_than)
        value, qualifier = conv.from_device_value('9.9e37')
        self.assertEqual(inf, value)
        self.assertEqual(MeasurementQualifier.infinite, qualifier)
        value, qualifier = conv.from_device_value('-99e36')
        self.assertEqual(-inf, value)
        self.assertEqual(MeasurementQualifier.infinite, qualifier)

        # Other strings raise a ValueError.
        with self.assertRaises(ValueError):
            conv.from_device_value('#678')
        with self.assertRaises(ValueError):
            conv.from_device_value('nonsense')

    def test_MeasurementPropertyFloatConverter_to_device_value(self):
        # The "pro forma" implementation of
        # _MeasurementPropertyFloatConverter.to_device_value() raises
        # a RuntimeError: Measurement properities should be read-only.
        # If to_device_value() is called, this indicates a bad proerpty
        # configuration.
        conv = ds1052._MeasurementPropertyFloatConverter()
        with self.assertRaises(DS1052PropertyValueError):
            conv.to_device_value(3.21, None)


class BasicDS1052Test(TestCase):
    # Most basic tests.
    def test_open(self):
        # A connection to the DSO must explicitly be opened and it should
        # finally be closed.
        dso = DS1052(tmc_class=TMC_CLASS, resource_manager=visa_rm)
        dso.open()
        try:
            self.assertEqual('Rigol Technologies', dso.vendor)
            self.assertIn(dso.model, ('DS1052E', 'DS1102E'))
            self.assertTrue(isinstance(dso.serial, str))
            existing_serial = dso.serial
            self.assertTrue(isinstance(dso.sw_version, str))
        finally:
            dso.close()

        # The serial number of the device can be specified.
        dso = DS1052(
            tmc_class=TMC_CLASS, resource_manager=visa_rm,
            serial=existing_serial)
        dso.open()
        try:
            self.assertEqual('Rigol Technologies', dso.vendor)
            self.assertIn(dso.model, ('DS1052E', 'DS1102E'))
            self.assertEqual(existing_serial, dso.serial)
            self.assertTrue(isinstance(dso.sw_version, str))
        finally:
            dso.close()

        dso = DS1052(
            tmc_class=TMC_CLASS, resource_manager=visa_rm, serial='nonsense')
        with self.assertRaises(DS1052InitError) as ctx:
            dso.open()
        self.assertEqual('Device not found.', str(ctx.exception))


class DS1052Test(TestCase):
    def setUp(self):
        self.dso = DS1052(tmc_class=TMC_CLASS, resource_manager=visa_rm)
        self.dso.open()
        # Ensure that the DSO does not beep for every test...
        # Nah. I won't restore a "beep on". These devices should be silent.
        self.dso.beep_enabled = False
        super().setUp()

    def tearDown(self):
        self.dso.close()
        super().tearDown()

    def _callTestMethod(self, method):
        try:
            method()
        except:
            self.dso._tmc_device.show_log_buff()
            raise

    def delayed_property_check(self, object, prop_name, value_wanted):
        wait_until = time() + 0.4
        while time() < wait_until:
            try:
                value_seen = getattr(object, prop_name)
            # This is crazy: With PyVisaInstrument and at least pyvisa_py,
            # we get a timeout in test_run_stop() after the stop() call,
            # when DEV_DEP_MSG_IN is sent to the DS1052. Just trying again
            # works though....
            # Increasing the sleep time up to 0.01s below does not prevent
            # the exception.
            except DS1052TimeoutError:
                value_seen = getattr(object, prop_name)
            if value_seen != value_wanted:
                sleep(0.001)
            else:
                break
        else:
            self.fail(
                f'Timeout while waiting for property {prop_name} to change '
                f'to value {value_wanted!r}. Last value seen: {value_seen!r}')

    def test_run_stop(self):
        self.dso.run()
        self.delayed_property_check(
            self.dso.trigger, 'status', TriggerStatus.run)
        self.dso.stop()
        self.delayed_property_check(
            self.dso.trigger, 'status', TriggerStatus.stop)
        # XXX This is weird: If we do not wait here for some time,
        # test_timebase_offset(), which runs shortly after, will "hang up"
        # the DSO so that it must be power-cycled...
        # Seems to be no longer needed. The exact reason is unclear. So
        # keep the commented-out call for now as a reminder...
        #sleep(0.5)

    def enum_property_check(self, property_name, enum_type):
        # Try to set each enum value for the given property.
        original_value = getattr(self.dso, property_name)
        try:
            all_values = list(enum_type)
            # Append the first value to the end of the list: When this test
            # starts, the property may already be set to the first value, so
            # the first setattr() call might not change anything.
            all_values.append(all_values[0])
            for new_value in all_values:
                setattr(self.dso, property_name, new_value)
                self.assertEqual(new_value, getattr(self.dso, property_name))
            with self.assertRaises(DS1052PropertyValueError) as ctx:
                bad_value = f'Not a {enum_type} instance'
                setattr(self.dso, property_name, bad_value)
            self.assertEqual(
                f"Expected an instance of {enum_type}, not <class 'str'>",
                str(ctx.exception))
            setattr(self.dso, property_name, original_value)
        finally:
            setattr(self.dso, property_name, original_value)

    def bool_property_check(self, property_name):
        original_value = getattr(self.dso, property_name)
        # Bool properties accept anything that evaluates to True or False.
        for new_value, device_value in (
                (False, False), (True, True), (0, False), (1, True),
                ('', False), ('x', True)):
            setattr(self.dso, property_name, new_value)
            self.assertIs(bool(new_value), getattr(self.dso, property_name))
        setattr(self.dso, property_name, original_value)

    def choices_property_check(
            self, property_name, choices, invalid_choice):
        choices = list(choices)
        original_value = getattr(self.dso, property_name)
        try:
            for value in choices:
                setattr(self.dso, property_name, value)
                self.assertEqual(value, getattr(self.dso, property_name))

            with self.assertRaises(DS1052PropertyValueError) as ctx:
                setattr(self.dso, property_name, invalid_choice)
            self.assertEqual(
                f'Invalid value: {invalid_choice!r}. Allowed: '
                f'{sorted(choices)}',
                str(ctx.exception))
        finally:
            setattr(self.dso, property_name, original_value)

    def test_acquisition_type(self):
        self.enum_property_check('acquisition_type', AcquisitionType)

    def test_acquisition_mode(self):
        self.enum_property_check('acquisition_mode', AcquisitionMode)

    def test_acquisition_averages(self):
        self.choices_property_check(
            'acquisition_averages', (2**i for i in range(1, 9)), -17)

    def test_acquisition_sampling_rate(self):
        # XXX better test needed: How and when is this value is changed?
        for channel in (1, 2):
            result = self.dso.channel[channel].acquisition_sampling_rate
            self.assertTrue(isinstance(result, float))

    def test_acquisition_memory_depth(self):
        self.enum_property_check(
            'acquisition_memory_depth', AcquisitionMemoryDepth)

    def test_display_type(self):
        self.enum_property_check(
            'display_type', DisplayType)

    def test_display_grid(self):
        self.enum_property_check(
            'display_grid', DisplayGrid)

    def test_display_persistence(self):
        self.bool_property_check('display_persistence')

    def test_display_menu_time(self):
        self.choices_property_check(
            'display_menu_time', (-1, 1, 2, 5, 10, 20,), 42)

    def test_display_menu_status(self):
        self.bool_property_check('display_menu_status')

    def test_clear_display(self):
        # XXX This is hard to test: We would need to check the pixels of a
        # screenshot...
        with patch.object(self.dso._tmc_device, 'write') as mocked_write:
            self.dso.clear_display()
        mocked_write.assert_called_once_with(':DISP:CLEAR')

    def test_display_brightness(self):
        self.choices_property_check(
            'display_brightness', range(33), -17)

    def test_display_intensity(self):
        self.choices_property_check(
            'display_intensity', range(33), -17)

    def test_timebase_mode(self):
        self.enum_property_check('timebase_mode', TimebaseMode)

    def test_timebase_offset(self):
        original_value = self.dso.timebase_offset
        for value in (
                0, 4.3e-1, 4.3e-2, 4.3e-3, 4.3e-4, 4.3e-5,
                4.3e-6, 5.4e-1, -6.3e-5, -5.e-4):
            self.dso.timebase_offset = value
            self.assertEqual(value, self.dso.timebase_offset)
        # Rounded value.
        self.dso.timebase_offset = -3.34567e-5
        self.assertEqual(-3.346e-5, self.dso.timebase_offset)
        with self.assertRaises(DS1052PropertyValueError) as ctx:
            self.dso.timebase_offset = 500.01
        self.assertEqual(
            'Only values less than or equal to 500.0 allowed.',
            str(ctx.exception))
        with self.assertRaises(DS1052PropertyValueError) as ctx:
            self.dso.timebase_offset = -500.01
        self.assertEqual(
            'Only values greater than or equal to -500.0 allowed.',
            str(ctx.exception))
        self.dso.timebase_offset = original_value

    # XXX Disabled 2022-06-15. For the reason, see the comment in ds1052.py
    # before the definition of the property delayed_timebase_offset.
    # def test_delayed_timebase_offset(self):
    #     original_value = self.dso.delayed_timebase_offset
    #     for value in (
    #             0, 4.3e-1, -4.3e-2, -4.3e-3, -4.3e-4, 4.3e-5,
    #             -4.3e-6, 5.4e0, -6.3e1, 5.e2):
    #         self.dso.delayed_timebase_offset = value
    #         self.delayed_property_check(
    #             self.dso, 'delayed_timebase_offset', value)
    #     with self.assertRaises(ValueError) as ctx:
    #         self.dso.delayed_timebase_offset = 500.01
    #     self.assertEqual(
    #         'Only values between -500 and 500 are allowed.',
    #         str(ctx.exception))
    #     with self.assertRaises(ValueError) as ctx:
    #         self.dso.delayed_timebase_offset = -500.01
    #     self.assertEqual(
    #         'Only values between -500 and 500 are allowed.',
    #         str(ctx.exception))
    #     self.dso.delayed_timebase_offset = original_value

    def test_timebase_scale(self):
        if self.dso.model.startswith('DS1102'):
            allowed = [
                2e-9, 5e-09,
                1e-08, 2e-08, 5e-08, 1e-07, 2e-07, 5e-07, 1e-06, 2e-06, 5e-06,
                1e-05, 2e-05, 5e-05, 0.0001, 0.0002, 0.0005,
                0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5,
                1.0, 2.0, 5.0, 10.0, 20.0, 50.0]
        else:
            allowed = [
                5e-09,
                1e-08, 2e-08, 5e-08, 1e-07, 2e-07, 5e-07, 1e-06, 2e-06, 5e-06,
                1e-05, 2e-05, 5e-05, 0.0001, 0.0002, 0.0005,
                0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5,
                1.0, 2.0, 5.0, 10.0, 20.0, 50.0]
        self.choices_property_check('timebase_scale', allowed, 2.1)

    #def test_delayed_timebase_scale(self):
    #    self.choices_property_check(
    #        'delayed_timebase_scale',
    #        [5e-09,
    #         1e-08, 2e-08, 5e-08, 1e-07, 2e-07, 5e-07, 1e-06, 2e-06, 5e-06,
    #         1e-05, 2e-05, 5e-05, 0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005,
    #         0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0],
    #        2.1)

    def test_timebase_format(self):
        self.enum_property_check('timebase_format', TimebaseFormat)

    def test_trigger_mode(self):
        original_trigger_mode = self.dso.trigger.mode
        try:
            for mode in TriggerMode:
                self.dso.trigger.mode = mode
                self.assertEqual(mode, self.dso.trigger.mode)
        finally:
            self.dso.trigger.mode = original_trigger_mode

    tr_sources_for_tr_mode = {
        TriggerMode.edge: {
            'working': tuple(TriggerSource),
            'not_working': (),
        },
        TriggerMode.pulse: {
            'working': (TriggerSource.channel1, TriggerSource.channel2,
                        TriggerSource.external),
            'not_working': (TriggerSource.ac_line, ),
        },
        TriggerMode.video: {
            'working': (TriggerSource.channel1, TriggerSource.channel2,
                        TriggerSource.external),
            'not_working': (TriggerSource.ac_line, ),
        },
        TriggerMode.slope: {
            'working': (TriggerSource.channel1, TriggerSource.channel2,
                        TriggerSource.external),
            'not_working': (TriggerSource.ac_line, ),
        },
        TriggerMode.alternation: {
            'working': (),
            'not_working': tuple(TriggerSource),
        },
        }

    def test_trigger_source(self):
        # The trigger source is specified separately for each trigger mode.
        original_tr_sources = {
            tr_mode: self.dso.trigger[tr_mode].source
            for tr_mode in TriggerMode
            if tr_mode != TriggerMode.alternation}
        for tr_mode in TriggerMode:
            # Option 1: Use "dictionary access"
            for tr_source in self.tr_sources_for_tr_mode[tr_mode]['working']:
                self.dso.trigger[tr_mode].source = tr_source
                self.assertEqual(tr_source, self.dso.trigger[tr_mode].source)

            no_sources = self.tr_sources_for_tr_mode[tr_mode]['not_working']
            for tr_source in no_sources:
                with self.assertRaises(DS1052PropertyValueError) as ctx:
                    self.dso.trigger[tr_mode].source = tr_source
                if tr_mode == TriggerMode.alternation:
                    error_text = f'Cannot set a trigger source in {tr_mode}'
                else:
                    error_text = f'Cannot set {tr_source} in {tr_mode}'
                self.assertEqual(error_text, str(ctx.exception))

        for tr_mode, tr_source in original_tr_sources.items():
            self.dso.trigger[tr_mode].source = tr_source

    def test_trigger_source_typecheck(self):
        # When the trigger source is set, it can be specified as a
        # TriggerSource instance, as a ChannelNumber instance, or as an integer,
        # where the integer must be equal to a ChannelNumber number.
        tr_mode = self.dso.trigger.mode
        original_trigger_source = self.dso.trigger[tr_mode].source
        for channel in ChannelNumber:
            expected = TriggerSource(int(channel))
            self.dso.trigger[tr_mode].source = channel
            self.assertEqual(expected, self.dso.trigger[tr_mode].source)
            self.dso.trigger[tr_mode].source = int(channel)
            self.assertEqual(expected, self.dso.trigger[tr_mode].source)
        # Other IntEnums cannot be used.
        class UnusableEnum(IntEnum):
            one = 1

        with self.assertRaises(DS1052PropertyValueError) as ctx:
            self.dso.trigger.edge.source = UnusableEnum.one
        self.assertEqual(
            'A trigger source must be an instance of TriggerSource, or of '
            'ChannelNumber or an integer representing a channel number',
            str(ctx.exception))

    def test_trigger_level(self):
        supported_tr_modes = (
            TriggerMode.edge, TriggerMode.pulse, TriggerMode.video)
        original_levels = {
            tr_mode: self.dso.trigger[tr_mode].level
            for tr_mode in supported_tr_modes}
        original_sources = {
            tr_mode: self.dso.trigger[tr_mode].source
            for tr_mode in supported_tr_modes}
        original_v_scales = {ch: self.dso.channel[ch].scale for ch in (1, 2)}
        original_v_offsets = {ch: self.dso.channel[ch].offset for ch in (1, 2)}
        # Double-check that a precondition for the following tests is
        # satisfied.
        self.assertEqual(1, self.dso.channel[1].scale)
        self.assertEqual(1, self.dso.channel[2].scale)
        try:
            trigger_levels_tested_mode = (-0.2, 1.1, -0.65, 0.54)
            for tr_mode in supported_tr_modes:
                for source in (
                        TriggerSource.channel1, TriggerSource.channel2):
                    self.dso.trigger[tr_mode].source = source
                    self.dso.channel[source].scale = 1
                    self.dso.channel[source].offset = 0
                    for level in (1.22, -0.2, 1.1, -0.65, 0.54):
                        self.dso.trigger[tr_mode].level = level
                        self.assertEqual(level, self.dso.trigger[tr_mode].level)
                    # Rounded value.
                    self.dso.trigger[tr_mode].level = -1.9876
                    self.assertEqual(-1.99, self.dso.trigger[tr_mode].level)

                    # Range checks.
                    with self.assertRaises(DS1052PropertyValueError) as ctx:
                        self.dso.trigger[tr_mode].level = 6.01
                    self.assertEqual(
                        'Only values less than or equal to '
                        '6 * vertical scale - vertical offset (6.0) allowed.',
                        str(ctx.exception))
                    with self.assertRaises(DS1052PropertyValueError) as ctx:
                        self.dso.trigger[tr_mode].level = -6.01
                    self.assertEqual(
                        'Only values greater than or equal to '
                        '-6 * vertical scale - vertical offset (-6.0) allowed.',
                        str(ctx.exception))

                    # The allowed range depends of the vertical offset.
                    self.dso.channel[source].offset = 1.5
                    with self.assertRaises(DS1052PropertyValueError) as ctx:
                        self.dso.trigger[tr_mode].level = 4.51
                    self.assertEqual(
                        'Only values less than or equal to '
                        '6 * vertical scale - vertical offset (4.5) allowed.',
                        str(ctx.exception))
                    self.dso.channel[source].offset = 4.5
                    self.assertEqual(4.5, self.dso.channel[source].offset)
                    self.dso.channel[source].offset = -7.5
                    self.assertEqual(-7.5, self.dso.channel[source].offset)
                self.dso.trigger[tr_mode].source = TriggerSource.external
                for level in (1.2, -0.2, 1.1, -0.65, 0.54):
                    self.dso.trigger[tr_mode].level = level
                    self.assertEqual(level, self.dso.trigger[tr_mode].level)
                # Rounded value.
                self.dso.trigger[tr_mode].level = -0.9764
                self.assertEqual(-0.976, self.dso.trigger[tr_mode].level)
                with self.assertRaises(DS1052PropertyValueError) as ctx:
                    self.dso.trigger[tr_mode].level = 1.21
                self.assertEqual(
                    'Only values less than or equal to '
                    '6 * vertical scale - vertical offset (1.2) allowed.',
                    str(ctx.exception))
                with self.assertRaises(DS1052PropertyValueError) as ctx:
                    self.dso.trigger[tr_mode].level = -1.21
                self.assertEqual(
                    'Only values greater than or equal to '
                    '-6 * vertical scale - vertical offset (-1.2) allowed.',
                    str(ctx.exception))
                if tr_mode == TriggerMode.edge:
                    self.dso.trigger[tr_mode].source = TriggerSource.ac_line
                    with self.assertRaises(DS1052PropertyValueError) as ctx:
                        self.dso.trigger[tr_mode].level = 0
                    self.assertEqual(
                        'Trigger level can only be set when the trigger '
                        'source is CH1, CH2 or external.',
                        str(ctx.exception))

            unsupported_tr_modes = [
                tr_mode for tr_mode in TriggerMode
                if tr_mode not in supported_tr_modes]
            for tr_mode in unsupported_tr_modes:
                with self.assertRaises(AttributeError):
                    self.dso.trigger[tr_mode].level
        finally:
            for ch in (1, 2):
                self.dso.channel[ch].scale = original_v_scales[ch]
                self.dso.channel[ch].offset = original_v_offsets[ch]
            for tr_mode in supported_tr_modes:
                self.dso.trigger[tr_mode].source = original_sources[tr_mode]
                self.dso.trigger[tr_mode].level = original_levels[tr_mode]

    def test_sweep(self):
        # Yes, TriggerMode.video is not supported. See the comment in
        # class TriggerModeSettingsVideo.
        supported_tr_modes = (
            TriggerMode.edge, TriggerMode.pulse, TriggerMode.slope)
        original_sweep_modes = {
            tr_mode: self.dso.trigger[tr_mode].sweep
            for tr_mode in supported_tr_modes}

        for tr_mode in supported_tr_modes:
            for sweep in Sweep:
                self.dso.trigger[tr_mode].sweep = sweep
                self.assertEqual(sweep, self.dso.trigger[tr_mode].sweep)

        for tr_mode, sweep in original_sweep_modes.items():
            self.dso.trigger[tr_mode].swwp = sweep

        unsupported_tr_modes = [
            tr_mode for tr_mode in TriggerMode
            if tr_mode not in supported_tr_modes]
        for tr_mode in unsupported_tr_modes:
            with self.assertRaises(AttributeError):
                self.dso.trigger[tr_mode].sweep

    def test_trigger_coupling(self):
        supported_tr_modes = (
            TriggerMode.edge, TriggerMode.pulse, TriggerMode.slope)
        original_couplings = {
            tr_mode: self.dso.trigger[tr_mode].coupling
            for tr_mode in supported_tr_modes}

        for tr_mode in supported_tr_modes:
            for coupling in TriggerCoupling:
                self.dso.trigger[tr_mode].coupling = coupling
                self.assertEqual(coupling, self.dso.trigger[tr_mode].coupling)

        for tr_mode, coupling in original_couplings.items():
            self.dso.trigger[tr_mode].coupling = coupling

    def test_trigger_holdoff(self):
        current_value = self.dso.trigger.holdoff
        for value in (5e-7, 1.1e-5, 0.34, 1.5):
            self.dso.trigger.holdoff = value
            self.assertEqual(value, self.dso.trigger.holdoff)
        # Rounded value.
        self.dso.trigger.holdoff = 4.5678e-3
        self.assertEqual(4.568e-3, self.dso.trigger.holdoff)
        for value in (4.999e-7, 1.501):
            with self.assertRaises(DS1052PropertyValueError) as ctx:
                self.dso.trigger.holdoff = value
        self.dso.trigger.holdoff = current_value

    def test_trigger_attribute(self):
        # DS1052.trigger is a "container" for settings of specific trigger
        # modes.
        # Specific trigger modes can be accessed as attributes or via
        # "dictionary lookup".
        for tr_mode in TriggerMode:
            tr_mode_settings = getattr(self.dso.trigger, tr_mode.name)
            self.assertIsInstance(tr_mode_settings, TriggerModeSettings)
            self.assertEqual(tr_mode_settings, self.dso.trigger[tr_mode])
            # The trigger mode name can also be used as a key.
            self.assertEqual(tr_mode_settings, self.dso.trigger[tr_mode.name])

        # Attempts to acces an invalid trigger mode raises a KeyError
        with self.assertRaises(KeyError) as ctx:
            self.dso.trigger['nonsense']
        self.assertEqual(
            '"Invalid trigger mode key: \'nonsense\'"', str(ctx.exception))
        # The "read-only part" of the dictionary protocol is provided.
        # __iter__()
        collected_keys = list(self.dso.trigger)
        self.assertEqual(len(collected_keys), len(TriggerMode))
        self.assertEqual(set(collected_keys), set(TriggerMode))
        # __contains__()
        for k in TriggerMode:
            self.assertTrue(k in self.dso.trigger)
            self.assertTrue(k.name in self.dso.trigger)
        # __len__()
        self.assertEqual(len(self.dso.trigger), len(TriggerMode))

        for k in TriggerMode:
            self.assertEqual(
                self.dso.trigger[k], self.dso.trigger.get(k, 'foo'))
            self.assertEqual(
                self.dso.trigger[k], self.dso.trigger.get(k))

        self.assertEqual('foo', self.dso.trigger.get('nonsense', 'foo'))
        self.assertIs(None, self.dso.trigger.get('nonsense'))

        items = list(self.dso.trigger.items())
        self.assertEqual(len(items), len(TriggerMode))
        keys_from_items = set(item[0] for item in items)
        tr_mode_settings_from_items = set(item[1] for item in items)
        self.assertEqual(set(TriggerMode), keys_from_items)
        for k, tr_mode_settings in items:
            self.assertEqual(self.dso.trigger[k], tr_mode_settings)

        # Very naive implementation of keys():
        self.assertEqual(TriggerMode, self.dso.trigger.keys())

        self.assertEqual(
            tr_mode_settings_from_items, set(self.dso.trigger.values()))

    def test_trigger_slope_edge(self):
        # Aaarrgh. Again this mad combination of "edge" and "slope". (See
        # the source code of class TriggerModeSettingsEdge...)
        # This test is about the setting DS1052.trigger.edge.slope
        original_trigger_edge = self.dso.trigger.edge.slope
        for slope in Slope:
            self.dso.trigger.edge.slope = slope
            self.assertEqual(slope, self.dso.trigger.edge.slope)
        # The attribute exists only for the trigger mode "edge"-
        try:
            for mode in TriggerMode:
                if mode == TriggerMode.edge:
                    continue
                with self.assertRaises(AttributeError) as ctx:
                    self.dso.trigger[mode].slope
                self.assertEqual(
                    f"'{self.dso.trigger[mode].__class__.__name__}' object "
                    f"has no attribute 'slope'",
                    str(ctx.exception))
        finally:
            self.dso.trigger.edge.slope = original_trigger_edge

    def test_trigger_sensitivity(self):
        supported_tr_modes = (
            TriggerMode.edge, TriggerMode.pulse, TriggerMode.video,
            TriggerMode.slope, )
        for tr_mode in supported_tr_modes:
            current_sesitivity = self.dso.trigger[tr_mode].sensitivity
            try:
                for value in (0.1, 1, 0.43, 0.76):
                    self.dso.trigger[tr_mode].sensitivity = value
                    self.assertEqual(
                        value, self.dso.trigger[tr_mode].sensitivity)
                # Rounded value.
                self.dso.trigger[tr_mode].sensitivity = 0.2345
                self.assertEqual(0.234, self.dso.trigger[tr_mode].sensitivity)

                with self.assertRaises(DS1052PropertyValueError) as ctx:
                    self.dso.trigger[tr_mode].sensitivity = 0.09
                self.assertEqual(
                    'Only values greater than or equal to 0.1 allowed.',
                    str(ctx.exception))

                with self.assertRaises(DS1052PropertyValueError) as ctx:
                    self.dso.trigger[tr_mode].sensitivity = 1.01
                self.assertEqual(
                    'Only values less than or equal to 1.0 allowed.',
                    str(ctx.exception))
            finally:
                current_sesitivity = self.dso.trigger[tr_mode].sensitivity
        for tr_mode in TriggerMode:
            if tr_mode in supported_tr_modes:
                continue
            with self.assertRaises(AttributeError) as ctx:
                self.dso.trigger[tr_mode].sensitivity
            self.assertEqual(
                f"'{self.dso.trigger[tr_mode].__class__.__name__}' object "
                "has no attribute 'sensitivity'",
                str(ctx.exception))

    def test_pulse_or_slope_trigger_time_condition(self):
        supported_trigger_modes = (TriggerMode.pulse, TriggerMode.slope)
        current_tr_mode = self.dso.trigger.mode
        try:
            for tr_mode in supported_trigger_modes:
                current_condition = self.dso.trigger[tr_mode].time_condition
                for value in TriggerTimeCondition:
                    try:
                        self.dso.trigger[tr_mode].time_condition = value
                        self.delayed_property_check(
                            self.dso.trigger[tr_mode], 'time_condition', value)
                    finally:
                        self.dso.trigger[tr_mode].time_condition = (
                            current_condition)
            for tr_mode in TriggerMode:
                if tr_mode in supported_trigger_modes:
                    continue
                with self.assertRaises(AttributeError) as ctx:
                    self.dso.trigger[tr_mode].time_condition
                self.assertEqual(
                    f"'{self.dso.trigger[tr_mode].__class__.__name__}' object "
                    "has no attribute 'time_condition'",
                    str(ctx.exception))
        finally:
            self.dso.trigger.mode = current_tr_mode

    def test_pulse_slope_trigger_time_condition_value(self):
        supported_tr_modes = (TriggerMode.pulse, TriggerMode.slope)
        for tr_mode in supported_tr_modes:
            for value in (20e-9, 512e-6, 438e-3, 4.2, 10):
                self.dso.trigger[tr_mode].time_condition_value = value
                self.delayed_property_check(
                    self.dso.trigger[tr_mode], 'time_condition_value', value)
            # Rounded value.
            self.dso.trigger[tr_mode].time_condition_value = 1.23456e-3
            self.assertEqual(
                1.235e-3, self.dso.trigger[tr_mode].time_condition_value)
            with self.assertRaises(DS1052PropertyValueError) as ctx:
                self.dso.trigger[tr_mode].time_condition_value = 19.99e-9
            self.assertEqual(
                'Only values greater than or equal to 2e-08 allowed.',
                str(ctx.exception))
            with self.assertRaises(DS1052PropertyValueError) as ctx:
                self.dso.trigger[tr_mode].time_condition_value = 10.01
            self.assertEqual(
                'Only values less than or equal to 10.0 allowed.',
                str(ctx.exception))
        for tr_mode in TriggerMode:
            if tr_mode in supported_tr_modes:
                continue
            with self.assertRaises(AttributeError) as ctx:
                self.dso.trigger[tr_mode].time_condition_value
            self.assertEqual(
                f"'{self.dso.trigger[tr_mode].__class__.__name__}' object "
                "has no attribute 'time_condition_value'",
                str(ctx.exception))

    def test_video_trigger_sync_type(self):
        for value in VideoTriggerSyncType:
            self.dso.trigger.video.sync = value
            self.delayed_property_check(
                self.dso.trigger.video, 'sync', value)
        with self.assertRaises(DS1052PropertyValueError) as ctx:
            self.dso.trigger.video.sync = 'not the right enum'
        self.assertEqual(
            "Expected an instance of <aenum 'VideoTriggerSyncType'>, "
            "not <class 'str'>",
            str(ctx.exception))
        for tr_mode in TriggerMode:
            if tr_mode == TriggerMode.video:
                continue
            with self.assertRaises(AttributeError) as ctx:
                self.dso.trigger[tr_mode].sync
            self.assertEqual(
                f"'{self.dso.trigger[tr_mode].__class__.__name__}' object "
                "has no attribute 'sync'",
                str(ctx.exception))

    def test_video_trigger_polarity(self):
        for value in VideoTriggerPolarity:
            self.dso.trigger.video.polarity = value
            self.delayed_property_check(
                self.dso.trigger.video, 'polarity', value)
        with self.assertRaises(DS1052PropertyValueError) as ctx:
            self.dso.trigger.video.polarity = 'not the right enum'
        self.assertEqual(
            "Expected an instance of <aenum 'VideoTriggerPolarity'>, "
            "not <class 'str'>",
            str(ctx.exception))
        for tr_mode in TriggerMode:
            if tr_mode == TriggerMode.video:
                continue
            with self.assertRaises(AttributeError) as ctx:
                self.dso.trigger[tr_mode].polarity
            self.assertEqual(
                f"'{self.dso.trigger[tr_mode].__class__.__name__}' object "
                "has no attribute 'polarity'",
                str(ctx.exception))

    def test_video_trigger_standard(self):
        for value in VideoStandard:
            self.dso.trigger.video.standard = value
            self.delayed_property_check(
                self.dso.trigger.video, 'standard', value)
        with self.assertRaises(DS1052PropertyValueError) as ctx:
            self.dso.trigger.video.standard = 'not the right enum'
        self.assertEqual(
            "Expected an instance of <aenum 'VideoStandard'>, "
            "not <class 'str'>",
            str(ctx.exception))
        for tr_mode in TriggerMode:
            if tr_mode == TriggerMode.video:
                continue
            with self.assertRaises(AttributeError) as ctx:
                self.dso.trigger[tr_mode].standard
            self.assertEqual(
                f"'{self.dso.trigger[tr_mode].__class__.__name__}' object "
                "has no attribute 'standard'",
                str(ctx.exception))

    def test_video_trigger_line(self):
        current_video_standard = self.dso.trigger.video.standard
        current_video_sync = self.dso.trigger.video.sync
        try:
            # Only PAL and SECAM have 625 lines.
            self.dso.trigger.video.standard = VideoStandard.pal_secam
            self.dso.trigger.video.sync = VideoTriggerSyncType.line_number
            for value in (1, 343, 404, 42, 625):
                self.dso.trigger.video.line = value
                self.delayed_property_check(
                    self.dso.trigger.video, 'line', value)
            with self.assertRaises(DS1052PropertyValueError) as ctx:
                self.dso.trigger.video.line = 0
            self.assertEqual(
                "Only values greater than or equal to 1 allowed.",
                str(ctx.exception))
            with self.assertRaises(DS1052PropertyValueError) as ctx:
                self.dso.trigger.video.line = 626
            # XXX The range restriction for NTSC is NOT very well checked:
            # We still have the value 625.
            self.assertEqual(625, self.dso.trigger.video.line)
            self.dso.trigger.video.standard = VideoStandard.ntsc
            self.delayed_property_check(
                self.dso.trigger.video, 'standard', VideoStandard.ntsc)
            # The DSO silently changed the value to 525. That's good
            # and, BTW, a nice example why caching device property
            # values would be error prone.
            self.assertEqual(525, self.dso.trigger.video.line)
            # XXX An attempt to set the line number to a value that is invalid
            # for NTSC but valid for PAL/SECAM yields a quite unspecific
            # error. That's bad: There is enough information to produce
            # a dedicated exception. OTOH: Who uses or needs the video trigger
            # mode in 2022?
            with self.assertRaises(DS1052PropertySetError) as ctx:
                self.dso.trigger.video.line = 550
            self.assertEqual(
                'Timeout while waiting for a property to be set. '
                'Expected value: 550, last seen: 525',
                str(ctx.exception))

            with self.assertRaises(ValueError) as ctx:
                self.dso.trigger.video.line = 'not an int'
            self.assertEqual(
                "invalid literal for int() with base 10: 'not an int'",
                str(ctx.exception))
            for tr_mode in TriggerMode:
                if tr_mode == TriggerMode.video:
                    continue
                with self.assertRaises(AttributeError) as ctx:
                    self.dso.trigger[tr_mode].line
                self.assertEqual(
                    f"'{self.dso.trigger[tr_mode].__class__.__name__}' object "
                    "has no attribute 'line'",
                    str(ctx.exception))
        finally:
            self.dso.trigger.video.standard = current_video_standard
            self.dso.trigger.video.sync = current_video_sync

    negative_slope_conditions = (
        TriggerTimeCondition.negative_pulse_width_longer_than,
        TriggerTimeCondition.negative_pulse_width_shorter_than,
        TriggerTimeCondition.negative_pulse_width_equal)

    def test_slope_trigger_level_lower_upper(self):
        current_levels = self.dso.trigger.slope.voltage_levels
        current_time_condition = self.dso.trigger.slope.time_condition
        current_trigger_source = self.dso.trigger.slope.source
        current_v_scale = self.dso.channel[1].scale
        current_v_offset = self.dso.channel[1].offset
        try:
            for time_condition in TriggerTimeCondition:
                self.dso.trigger.slope.source = TriggerSource.channel1
                self.dso.channel[1].scale = 1
                self.dso.channel[1].offset = 0
                self.dso.trigger.slope.time_condition = time_condition
                for lower, upper in (
                        (-0.33, -0.15), (-0.2, 0.3), (0.1, 1.5)):
                    self.dso.trigger.slope.voltage_level_lower = lower
                    self.dso.trigger.slope.voltage_level_upper = upper
                    self.assertEqual(
                        lower, self.dso.trigger.slope.voltage_level_lower)
                    self.assertEqual(
                        upper, self.dso.trigger.slope.voltage_level_upper)
                # Rounded values.
                self.dso.trigger.slope.voltage_level_lower = 0.98765
                self.assertEqual(
                    0.9877, self.dso.trigger.slope.voltage_level_lower)
                self.dso.trigger.slope.voltage_level_upper = 1.56789
                self.assertEqual(
                    1.568, self.dso.trigger.slope.voltage_level_upper)
                with self.assertRaises(DS1052PropertyValueError) as ctx:
                    self.dso.trigger.slope.voltage_level_lower = 3
                self.assertEqual(
                    f'New value for lower level (3) must not be greater than '
                    f'the current upper level '
                    f'({self.dso.trigger.slope.voltage_level_upper})',
                    str(ctx.exception))
                with self.assertRaises(DS1052PropertyValueError) as ctx:
                    self.dso.trigger.slope.voltage_level_upper = -1
                self.assertEqual(
                    f'New value for upper level (-1) must not be smaller '
                    f'than the current lower level '
                    f'({self.dso.trigger.slope.voltage_level_lower})',
                    str(ctx.exception))
                # Min/max possible values.
                self.dso.trigger.slope.voltage_level_upper = 6.0
                with self.assertRaises(DS1052PropertyValueError) as ctx:
                    self.dso.trigger.slope.voltage_level_upper = 6.1
                self.assertEqual(
                    'Only values less than or equal to '
                    'vertical scale - vertical offset (6.0) allowed.',
                    str(ctx.exception))
                self.dso.trigger.slope.voltage_level_lower = -6.0
                with self.assertRaises(DS1052PropertyValueError) as ctx:
                    self.dso.trigger.slope.voltage_level_lower = -6.1
                self.assertEqual(
                    'Only values greater than or equal to '
                    'vertical scale - vertical offset (-6.0) allowed.',
                    str(ctx.exception))

                self.dso.channel[1].offset = 1
                with self.assertRaises(DS1052PropertyValueError) as ctx:
                    self.dso.trigger.slope.voltage_level_upper = 5.1
                self.assertEqual(
                    'Only values less than or equal to '
                    'vertical scale - vertical offset (5.0) allowed.',
                    str(ctx.exception))
                with self.assertRaises(DS1052PropertyValueError) as ctx:
                    self.dso.trigger.slope.voltage_level_lower = -7.1
                self.assertEqual(
                    'Only values greater than or equal to '
                    'vertical scale - vertical offset (-7.0) allowed.',
                    str(ctx.exception))
        finally:
            self.dso.channel[1].scale = current_v_scale
            self.dso.channel[1].offset = current_v_offset
            self.dso.trigger.slope.source = current_trigger_source
            self.dso.trigger.slope.time_condition = current_time_condition
            self.dso.trigger.slope.voltage_levels = current_levels

    def test_slope_trigger_levels_tuple(self):
        current_levels = self.dso.trigger.slope.voltage_levels
        current_time_condition = self.dso.trigger.slope.time_condition
        try:
            for time_condition in TriggerTimeCondition:
                self.dso.trigger.slope.time_condition = time_condition
                for lower, upper in (
                        (-0.33, -0.15), (-0.2, 0.3), (0.1, 1.5)):
                    self.dso.trigger.slope.voltage_levels = (lower, upper)
                    self.assertEqual(
                        lower, self.dso.trigger.slope.voltage_level_lower)
                    self.assertEqual(
                        upper, self.dso.trigger.slope.voltage_level_upper)
                    self.assertEqual(
                        (lower, upper), self.dso.trigger.slope.voltage_levels)
                with self.assertRaises(DS1052PropertyValueError) as ctx:
                    self.dso.trigger.slope.voltage_levels = (2, 2)
                self.assertEqual(
                    'The first value (voltage_level_lower) must be smaller '
                    'than the second value (voltage_level_upper).',
                    str(ctx.exception))
                with self.assertRaises(DS1052PropertyValueError) as ctx:
                    self.dso.trigger.slope.voltage_levels = (4, 2)
                self.assertEqual(
                    'The first value (voltage_level_lower) must be smaller '
                    'than the second value (voltage_level_upper).',
                    str(ctx.exception))
        finally:
            self.dso.trigger.slope.time_condition = current_time_condition
            self.dso.trigger.slope.voltage_levels = current_levels

    @contextmanager
    def save_restore_channel_properties(
            self, ch, *property_names, reverse_for_restore=True):
        saved_values = {}
        for property_name in property_names:
            saved_values[property_name] = getattr(
                self.dso.channel[ch], property_name)
        try:
            yield
        finally:
            if reverse_for_restore:
                restore_seq = reversed(property_names)
            else:
                restore_seq = property_names
            for property_name in restore_seq:
                setattr(
                    self.dso.channel[ch], property_name,
                    saved_values[property_name])

    def check_bool_channel_property(self, property_name):
        for ch in 1, 2:
            with self.save_restore_channel_properties(ch, property_name):
                for new_value in (False, True, False):
                    setattr(self.dso.channel[ch], property_name, new_value)
                    self.assertEqual(
                        new_value, getattr(self.dso.channel[ch], property_name))

    def check_enum_channel_property(self, property_name, enum):
        for ch in 1, 2:
            with self.save_restore_channel_properties(ch, property_name):
                # We don't know what the current value of the property is.
                # It can very well be test_values[0]. In this case the
                # _wait_until_property_set() call in _ChannelProperty.setter()
                # succeeds even if the command sent to the device is broken.
                # Appending the first value to the end of the list ensures
                # that a real change will occur for every item of the enum.
                test_values = list(enum)
                test_values.append(test_values[0])
                for new_value in test_values:
                    setattr(self.dso.channel[ch], property_name, new_value)
                    self.assertEqual(
                        new_value, getattr(self.dso.channel[ch], property_name))

    def check_int_choices_channel_property(
            self, property_name, choices, invalid_values):
        for ch in 1, 2:
            with self.save_restore_channel_properties(ch, property_name):
                test_values = list(choices)
                test_values.append(test_values[0])
                for new_value in test_values:
                    setattr(self.dso.channel[ch], property_name, new_value)
                    self.assertEqual(
                        new_value, getattr(self.dso.channel[ch], property_name))
                for new_value, expected_msg in invalid_values:
                    with self.assertRaises(DS1052PropertyValueError) as ctx:
                        setattr(self.dso.channel[ch], property_name, new_value)
                    self.assertEqual(expected_msg, str(ctx.exception))

    def test_channel_bandwidth_limit_enabled(self):
        self.check_bool_channel_property('bandwidth_limit_enabled')

    def test_channel_coupling(self):
        self.check_enum_channel_property('coupling', ChannelCoupling)

    def test_channel_enabled(self):
        self.check_bool_channel_property('enabled')

    def test_channel_display_inverted(self):
        self.check_bool_channel_property('display_inverted')

    def test_channel_probe_attenuation(self):
        self.check_int_choices_channel_property(
            'probe_attenuation', (1, 5, 10, 20, 50, 100, 200, 500, 1000),
            ((-1,
              'Invalid value: -1. Allowed: (1, 5, 10, 20, 50, 100, 200, '
              '500, 1000)'),
             (15,
              'Invalid value: 15. Allowed: (1, 5, 10, 20, 50, 100, 200, '
              '500, 1000)'),
             ('nonsense',
              "Invalid value: 'nonsense'. Allowed: (1, 5, 10, 20, 50, 100, "
              "200, 500, 1000)")))

    def test_channel_offset(self):
        for ch in 1, 2:
            with self.save_restore_channel_properties(
                    ch, 'scale', 'offset', reverse_for_restore=False):
                for scale in (2e-3, 0.249, 0.25, 10):
                    attenuation = self.dso.channel[ch].probe_attenuation
                    self.dso.channel[ch].scale = scale * attenuation
                    for new_value in (-2.0, -1.68, 0.865, -0.478, 2.0):
                        # Allowed range for scales < 0.25V: -2 .. +2;
                        # for larger scale -40 .. +40
                        if scale >= 0.25:
                            new_value *= 20
                        new_value *= attenuation
                        self.dso.channel[ch].offset = new_value
                        # The multiplications of new_value above can
                        # introduce "rounding effects". For example,
                        # -0.478 * 10 -> -4.799999999
                        self.assertAlmostEqual(
                            new_value, self.dso.channel[ch].offset)
                    for sign in (-1, 1):
                        within_limits = 2.0 * sign
                        outside_limits = 2.001 * sign
                        if scale >= 0.25:
                            within_limits *= 20
                            outside_limits *= 20
                        within_limits *= attenuation
                        outside_limits *= attenuation
                        self.dso.channel[ch].offset = within_limits
                        with self.assertRaises(DS1052PropertyValueError) as ctx:
                            self.dso.channel[ch].offset = outside_limits
                    # Rounded value.
                    self.dso.channel[ch].offset = 0.234567
                    self.assertEqual(0.2346, self.dso.channel[ch].offset)

    def test_channel_scale(self):
        # Test values for probe attenuation 1:
        valid_scale_values = (0.002, 1, 7.5, 0.465, 10.0)
        invalid_scale_values = (0.00199, 10.01)
        for ch in 1, 2:
            with self.save_restore_channel_properties(
                    ch, 'probe_attenuation', 'scale',
                    reverse_for_restore=False):
                for attenuation in (1, 5, 10, 20, 50, 100, 200, 500, 1000):
                    self.dso.channel[ch].probe_attenuation = attenuation
                    for scale in valid_scale_values:
                        scale = scale * attenuation
                        self.dso.channel[ch].scale = scale
                        self.assertEqual(scale, self.dso.channel[ch].scale)
                    for scale in invalid_scale_values:
                        scale = scale * attenuation
                        with self.assertRaises(DS1052PropertyValueError) as ctx:
                            self.dso.channel[ch].scale = scale
                        min_value = 0.002 * attenuation
                        max_value = 10.0 * attenuation
                        self.assertEqual(
                            f'Invalid scale setting {scale}. Allowed for probe '
                            f'attenuation {attenuation}: {min_value} .. '
                            f'{max_value}',
                            str(ctx.exception))
                    # A rounded value.
                    self.dso.channel[ch].scale = 3.45678
                    self.assertEqual(3.457, self.dso.channel[ch].scale)

    def test_channel_filter_enabled(self):
        # filter_enabled cannot be changed when the DS1052 is in stop mode.
        original_filter_enabled = self.dso.channel[1].filter_enabled
        try:
            # defined start value.
            self.dso.channel[1].filter_enabled = False
            self.dso.wait_until_stopped()
            with self.assertRaises(DS1052PropertySetError) as ctx:
                self.dso.channel[1].filter_enabled = True
            self.assertEqual(
                'The channel filter cannot be enabled or disabled in '
                'stop mode.',
                str(ctx.exception))
            # The exception is _not_ raised when the value does not change.
            self.dso.channel[1].filter_enabled = False
            self.dso.wait_until_running()
            self.check_bool_channel_property('filter_enabled')
        finally:
            self.dso.wait_until_running()
            self.dso.channel[1].filter_enabled = original_filter_enabled

    def test_channel_memory_depth(self):
        # XXX This test is a bit too simple: It would make sense to
        # document how the setting of
        # DS1052.acquisition_memory_depth and the number of enabled
        # channels impact the value of DS1052.channel[ch].memory_depth.
        # Summary of playing a bit with the DS1052:
        # - channel[ch].memory_depth shows the mem depth of the _last data acquistion_.
        #   IOW: if the DS1052 is in "stop" mode when  DS1052.acquisition_memory_depth
        #   is changed, channel[ch].memory_depth will change only after a DS10652.run()
        #   and the subsequent trigger event.
        # - Even when the DS1052 in "run" mode, when a "reliable" signal is connected
        #   to the CH1 and CH2 inputs and when trigger system is properly configured,
        #   there can be a suprisingly long delay until the value of
        #   DS1052.channel[ch].memory_depth changes. Haven't yet figured output
        #   what is going on there...
        #
        # For now, a too simple test...
        for ch in 1, 2:
            value = self.dso.channel[ch].memory_depth
            self.assertIn(value, (8192, 16384, 524288, 1048576))

    def test_vernier(self):
        self.check_enum_channel_property('vernier', ChannelVernier)

    def test_channel_scale_range(self):
        # A simple way to acccess _ChannelScaleConverter.valid_scale_values.
        channel = self.dso.channel[1]
        current_probe_attenuation = channel.probe_attenuation
        try:
            scale_map = ds1052._ChannelScaleConverter.valid_scale_values
            for probe_attenuation, scale in scale_map.items():
                channel.probe_attenuation = probe_attenuation
                self.assertEqual(scale, channel.scale_range)
        finally:
            channel.probe_attenuation = current_probe_attenuation

    def test_channel_offset_range(self):
        current_offset = self.dso.channel[1].offset
        current_scale = self.dso.channel[1].scale
        current_probe_attenuation = self.dso.channel[1].probe_attenuation
        try:
            for probe_attenuation in (
                    1, 5, 10, 20, 50, 100, 200, 500, 1000):
                for scale in (0.002, 0.249):
                    scale = scale * probe_attenuation
                    self.dso.channel[1].probe_attenuation = probe_attenuation
                    self.dso.channel[1].scale = scale
                    offset_range = self.dso.channel[1].offset_range
                    self.assertEqual(
                        (-2 * probe_attenuation, 2 * probe_attenuation),
                        offset_range)
                    self.dso.channel[1].offset = offset_range[0]
                    self.dso.channel[1].offset = offset_range[1]
                    with self.assertRaises(DS1052PropertyValueError):
                        self.dso.channel[1].offset = offset_range[0] * 1.01
                    with self.assertRaises(DS1052PropertyValueError):
                        self.dso.channel[1].offset = offset_range[1] * 1.01
            for probe_attenuation in (
                    1, 5, 10, 20, 50, 100, 200, 500, 1000):
                for scale in (0.25, 10.0):
                    scale = scale * probe_attenuation
                    self.dso.channel[1].probe_attenuation = probe_attenuation
                    self.dso.channel[1].scale = scale
                    offset_range = self.dso.channel[1].offset_range
                    self.assertEqual(
                        (-40 * probe_attenuation, 40 * probe_attenuation),
                        offset_range)
                    self.dso.channel[1].offset = offset_range[0]
                    self.dso.channel[1].offset = offset_range[1]
                    with self.assertRaises(DS1052PropertyValueError):
                        self.dso.channel[1].offset = offset_range[0] * 1.01
                    with self.assertRaises(DS1052PropertyValueError):
                        self.dso.channel[1].offset = offset_range[1] * 1.01
        finally:
            self.dso.channel[1].probe_attenuation = current_probe_attenuation
            self.dso.channel[1].scale = current_scale
            self.dso.channel[1].offset = current_offset

    def test_trigger_level_range(self):
        current_scale = self.dso.channel[1].scale
        current_offset = self.dso.channel[1].offset
        try:
            self.dso.channel[1].scale = 0.1
            self.dso.channel[1].offset = 0
            min_level, max_level = self.dso.channel[1].trigger_level_range
            self.assertAlmostEqual(-0.6, min_level)
            self.assertAlmostEqual(0.6, max_level)

            self.dso.channel[1].offset = -2
            min_level, max_level = self.dso.channel[1].trigger_level_range
            self.assertAlmostEqual(1.4, min_level)
            self.assertAlmostEqual(2.6, max_level)

            self.dso.channel[1].offset = +2
            min_level, max_level = self.dso.channel[1].trigger_level_range
            self.assertAlmostEqual(-2.6, min_level)
            self.assertAlmostEqual(-1.4, max_level)

            self.dso.channel[1].scale = 5
            self.dso.channel[1].offset = 0
            min_level, max_level = self.dso.channel[1].trigger_level_range
            self.assertAlmostEqual(-30.0, min_level)
            self.assertAlmostEqual(30.0, max_level)

            self.dso.channel[1].offset = -40
            min_level, max_level = self.dso.channel[1].trigger_level_range
            self.assertAlmostEqual(10.0, min_level)
            self.assertAlmostEqual(70.0, max_level)

            self.dso.channel[1].offset = +40
            min_level, max_level = self.dso.channel[1].trigger_level_range
            self.assertAlmostEqual(-70.0, min_level)
            self.assertAlmostEqual(-10.0, max_level)
        finally:
            self.dso.channel[1].scale = current_scale
            self.dso.channel[1].offset = current_offset

    def test_points_mode(self):
        self.enum_property_check(
            'points_mode', PointsMode)

    def test_screenshot(self):
        data = self.dso.screenshot()
        # The data can be loaded as a PIL image.
        pil_image = Image.open(BytesIO(data))
        self.assertEqual((320, 234), pil_image.size)
        self.assertEqual('BMP', pil_image.format)
        # It is palette image. (See
        # https://pillow.readthedocs.io/en/stable/handbook/concepts.html )
        self.assertEqual('P', pil_image.mode)

        # Possible conflicts with a subsequent :WAV:DATA?
        for _ in range(10):
            self.dso.screenshot()
            self.dso.read_waveforms((1, 2), PointsMode.normal)

    def test_as_config_value_from_config_value__EnumDeviceProperty(self):
        # _EnumDeviceProperty.as_confgi_value() returns the name of the
        # currently selected Enum member.
        aq_type = self.dso.acquisition_type
        try:
            for new_aq_type in AcquisitionType:
                DS1052.acquisition_type.from_config_value(
                    self.dso, new_aq_type.name)
                self.assertEqual(
                    new_aq_type.name,
                    DS1052.acquisition_type.as_config_value(self.dso))
                self.assertEqual(new_aq_type, self.dso.acquisition_type)
                with self.assertRaises(DS1052PropertyValueError) as ctx:
                    DS1052.acquisition_type.from_config_value(
                        self.dso, 'nonsense')
                self.assertEqual(
                    "'nonsense' is not a valid enum value of "
                    "<aenum 'AcquisitionType'>",
                    str(ctx.exception))
        finally:
            self.dso.acquisition_type = aq_type

    def test_as_config_value_from_config_value__BoolDeviceProperty(self):
        disp_menu_status = self.dso.display_menu_status
        try:
            # Bool properties accept any value that can be cast into a bool.
            for new_menu_status in (False, True, 0, 1, '', 'x', None):
                DS1052.display_menu_status.from_config_value(
                    self.dso, new_menu_status)
                self.assertIs(
                    bool(new_menu_status),
                    DS1052.display_menu_status.as_config_value(self.dso))
                self.assertIs(
                    bool(new_menu_status), self.dso.display_menu_status)
        finally:
            self.dso.display_menu_status = disp_menu_status

    def test_as_config_value_from_config_value__FloatDeviceProperty(self):
        timebase_offset = self.dso.timebase_offset
        try:
            for new_timebase_offset in (1e-3, -2e-4, 1e-6, '-2e-6'):
                DS1052.timebase_offset.from_config_value(
                    self.dso, new_timebase_offset)
                self.assertEqual(
                    float(new_timebase_offset),
                    DS1052.timebase_offset.as_config_value(self.dso))
                self.assertEqual(
                    float(new_timebase_offset), self.dso.timebase_offset)
            with self.assertRaises(ValueError) as ctx:
                DS1052.timebase_offset.from_config_value(
                    self.dso, 'nonsense')
            self.assertEqual(
                "could not convert string to float: 'nonsense'",
                str(ctx.exception))
        finally:
            self.dso.timebase_offset = timebase_offset

    def test_as_config_value_from_config_value__FloatChoicesDeviceProperty(
            self):
        timebase_scale = self.dso.timebase_scale
        try:
            for new_timebase_scale in (5e-8, 2e-4, 1e0, 2e-6, '2e-6'):
                DS1052.timebase_scale.from_config_value(
                    self.dso, new_timebase_scale)
                self.assertEqual(
                    float(new_timebase_scale),
                    DS1052.timebase_scale.as_config_value(self.dso))
                self.assertEqual(
                    float(new_timebase_scale), self.dso.timebase_scale)
            with self.assertRaises(DS1052PropertyValueError) as ctx:
                DS1052.timebase_scale.from_config_value(
                    self.dso, 1.25)
            self.assertTrue(
                str(ctx.exception).startswith(
                    "Invalid value: 1.25. Allowed: [",))
            with self.assertRaises(ValueError) as ctx:
                DS1052.timebase_scale.from_config_value(
                    self.dso, 'nonsense')
            self.assertEqual(
                "could not convert string to float: 'nonsense'",
                str(ctx.exception))
        finally:
            self.dso.timebase_scale = timebase_scale

    @skip('Unused property type.')
    def test_as_config_value_from_config_value__IntDeviceProperty(self):
        # There ATM (commit 78d156d) no "simple" _IntDeviceProperty.
        raise NotImplementedError

    def test_as_config_value_from_config_value__IntChoicesDeviceProperty(self):
        acquisition_averages = self.dso.acquisition_averages
        try:
            for new_acquisition_averages in (2, 256, 32):
                DS1052.acquisition_averages.from_config_value(
                    self.dso, new_acquisition_averages)
                self.assertEqual(
                    new_acquisition_averages,
                    DS1052.acquisition_averages.as_config_value(self.dso))
                self.assertEqual(
                    new_acquisition_averages, self.dso.acquisition_averages)
            with self.assertRaises(DS1052PropertyValueError) as ctx:
                DS1052.acquisition_averages.from_config_value(
                    self.dso, 42)
            self.assertEqual(
                "Invalid value: 42. Allowed: [2, 4, 8, 16, 32, 64, 128, 256]",
                str(ctx.exception))

            with self.assertRaises(ValueError) as ctx:
                DS1052.acquisition_averages.from_config_value(
                    self.dso, 'nonsense')
            self.assertEqual(
                "invalid literal for int() with base 10: 'nonsense'",
                str(ctx.exception))
        finally:
            self.dso.acquisition_averages = acquisition_averages

    def test_as_config_value_from_config_value__MappedProperty(self):
        display_menu_time = self.dso.display_menu_time
        try:
            for new_value in (1, 2, 5, 10, 20, -1):
                DS1052.display_menu_time.from_config_value(self.dso, new_value)
                self.assertEqual(
                    new_value,
                    DS1052.display_menu_time.as_config_value(self.dso))
                self.assertEqual(new_value, self.dso.display_menu_time)
                with self.assertRaises(DS1052PropertyValueError) as ctx:
                    self.dso.display_menu_time = 42
                self.assertEqual(
                    'Invalid value: 42. Allowed: [-1, 1, 2, 5, 10, 20]',
                    str(ctx.exception))
        finally:
            self.dso.display_menu_time = display_menu_time

    channel_config_properties = (
        'probe_attenuation', 'scale', 'offset', 'bandwidth_limit_enabled',
        'coupling', 'display_inverted', 'enabled', 'filter_enabled','vernier')

    def test_get_set_config(self):
        ds1052_config_properties = (
            'acquisition_averages', 'acquisition_memory_depth',
            'acquisition_mode', 'acquisition_type', 'beep_enabled',
            'display_all_measurements', 'display_brightness',
            'display_grid', 'display_intensity', 'display_menu_status',
            'display_menu_time', 'display_persistence', 'display_type',
            'points_mode', 'timebase_format', 'timebase_mode',
            'timebase_offset', 'timebase_scale')
        with ExitStack() as stack:
            mocks = {}
            for prop_name in ds1052_config_properties:
                prop = getattr(DS1052, prop_name)
                mocks[prop_name] = stack.enter_context(
                    patch.object(
                        prop, 'as_config_value',
                        wraps=prop.as_config_value))
            channels_get_config_mock = stack.enter_context(
                patch.object(
                    self.dso._channels, 'get_config',
                    wraps=self.dso._channels.get_config))
            trigger_get_config_mock = stack.enter_context(
                patch.object(
                    self.dso.trigger, 'get_config',
                    wraps=self.dso.trigger.get_config))
            config = self.dso.get_config()
        self.assertEqual(
            {'acquisition_averages', 'acquisition_memory_depth',
             'acquisition_mode', 'acquisition_type', 'beep_enabled',
             'display_all_measurements', 'display_brightness',
             'display_grid', 'display_intensity', 'display_menu_status',
             'display_menu_time', 'display_persistence', 'display_type',
             'points_mode', 'timebase_format', 'timebase_mode',
             'timebase_offset', 'timebase_scale', 'channel', 'trigger'},
            set(config))
        for prop_name in ds1052_config_properties:
            # MagicMock.assertCalledOnce() does not allow to pass a message
            # like assertEqual() and friends...
            if len(mocks[prop_name].mock_calls) != 1:
                self.fail(
                    f'Expected one access of property {prop_name}. but '
                    f'got {len(mocks[prop_name].mock_calls)} accesses.')
        channels_get_config_mock.assert_called_once()
        trigger_get_config_mock.assert_called_once()
        self.assertEqual({1, 2}, set(config['channel']))
        for channel in (1, 2):
            self.assertEqual(
                set(self.channel_config_properties),
            set(config['channel'][channel]))

        with ExitStack() as stack:
            mocks = {}
            for prop_name in ds1052_config_properties:
                prop = getattr(DS1052, prop_name)
                mocks[prop_name] = stack.enter_context(
                    patch.object(
                        prop, 'from_config_value',
                        wraps=prop.from_config_value))
            channels_set_config_mock = stack.enter_context(
                patch.object(
                    self.dso._channels, 'set_config',
                    wraps=self.dso._channels.set_config))
            trigger_set_config_mock = stack.enter_context(
                patch.object(
                    self.dso.trigger, 'set_config',
                    wraps=self.dso.trigger.set_config))
            self.dso.set_config(config)
        for prop_name in ds1052_config_properties:
            mocks[prop_name].assert_called_once()
        channels_set_config_mock.assert_called_once()
        trigger_set_config_mock.assert_called_once()
        for prop_name in ds1052_config_properties:
            # MagicMock.assertCalledOnce() does not allow to pass a message
            # like assertEqual() and friends...
            if len(mocks[prop_name].mock_calls) != 1:
                self.fail(
                    f'Expected one access of property {prop_name}. but '
                    f'got {len(mocks[prop_name].mock_calls)} accesses.')

    def test_channels_get_set_config(self):
        with ExitStack() as stack:
            mocks = [
                stack.enter_context(
                    patch.object(
                        self.dso._channels._channels[ch], 'get_config',
                        wraps=self.dso._channels._channels[ch].get_config
                    ))
                for ch in (1, 2)]
            config = self.dso._channels.get_config()
        [mock.assert_called_once() for mock in mocks]
        self.assertEqual({1, 2}, set(config))
        for channel in (1, 2):
            self.assertEqual(
                set(self.channel_config_properties),
            set(config[channel]))

        with ExitStack() as stack:
            mocks = {
                ch: stack.enter_context(
                    patch.object(
                        self.dso._channels._channels[ch], 'set_config',
                        wraps=self.dso._channels._channels[ch].set_config
                    ))
                for ch in (1, 2)}
            self.dso._channels.set_config(config)
        for ch, mock in mocks.items():
            mock.assert_called_once_with(config[ch])

    def check_property_container_get_set_config(
            self, container, property_names):
        with ExitStack() as stack:
            mocks = {
                prop_name: stack.enter_context(
                    patch.object(
                        getattr(container.__class__, prop_name),
                        'as_config_value',
                        wraps=getattr(
                            container.__class__, prop_name).as_config_value))
                for prop_name in property_names}
            config = container.get_config()
        for prop_name in property_names:
            mocks[prop_name].assert_called_once()
        self.assertEqual(
            set(property_names), set(config))

        with ExitStack() as stack:
            mocks = {
                prop_name: stack.enter_context(
                    patch.object(
                        getattr(container.__class__, prop_name),
                        'from_config_value',
                        wraps=getattr(
                            container.__class__, prop_name).from_config_value))
                for prop_name in property_names}
            config = container.set_config(config)
        for prop_name in property_names:
            mocks[prop_name].assert_called_once()

    def test_channel_get_set_config(self):
        self.check_property_container_get_set_config(
            self.dso.channel[1], self.channel_config_properties)

    def test_float_channel_property_as_from_config(self):
        channel = self.dso.channel[1]
        offset = channel.offset
        try:
            self.assertEqual(
                offset, ds1052.Channel.offset.as_config_value(channel))
            ds1052.Channel.offset.from_config_value(channel, -offset)
            self.assertEqual(-offset, channel.offset)
        finally:
            channel.offset = offset

    def test_int_choice_channel_property_as_from_config(self):
        channel = self.dso.channel[1]
        probe_attenuation = channel.probe_attenuation
        try:
            self.assertEqual(
                probe_attenuation,
                ds1052.Channel.probe_attenuation.as_config_value(channel))
            ds1052.Channel.probe_attenuation.from_config_value(channel, 1000)
            self.assertEqual(1000, channel.probe_attenuation)
            ds1052.Channel.probe_attenuation.from_config_value(channel, 100)
            self.assertEqual(100, channel.probe_attenuation)
        finally:
            channel.probe_attenuation = probe_attenuation

    def test_bool_channel_property_as_from_config(self):
        channel = self.dso.channel[1]
        bandwidth_limit_enabled = channel.bandwidth_limit_enabled
        try:
            for value in (False, True, False):
                ds1052.Channel.bandwidth_limit_enabled.from_config_value(
                    channel, value)
                self.assertEqual(value, channel.bandwidth_limit_enabled)
                self.assertEqual(
                    value,
                    ds1052.Channel.bandwidth_limit_enabled.as_config_value(
                        channel))
        finally:
            channel.bandwidth_limit_enabled = bandwidth_limit_enabled

    def test_enum_channel_property_as_from_config(self):
        channel = self.dso.channel[1]
        coupling = channel.coupling
        try:
            for value in ChannelCoupling:
                ds1052.Channel.coupling.from_config_value(channel, value.name)
                self.assertEqual(value, channel.coupling)
                self.assertEqual(
                    value.name,
                    ds1052.Channel.coupling.as_config_value(channel))
            with self.assertRaises(DS1052PropertyValueError) as ctx:
                ds1052.Channel.coupling.from_config_value(channel, 'nonsense')
            self.assertEqual(
                "'nonsense' is not a valid enum value of "
                "<aenum 'ChannelCoupling'>",
                str(ctx.exception))
        finally:
            channel.coupling = coupling

    def test_trigger_sweep_property_as_from_config_value(self):
        # Properties derived from _TriggerPropertyBase call the
        # as_config() and from_config() of their _device_property.
        sweep_prop = ds1052.TriggerModeSettingsEdge.sweep
        with patch.object(
                sweep_prop._device_property, 'as_config_value',
                wraps=sweep_prop._device_property.as_config_value
                ) as mock:
            value = sweep_prop.as_config_value(self.dso.trigger.edge)
        mock.assert_called_once()
        with patch.object(
                sweep_prop._device_property, 'from_config_value',
                wraps=sweep_prop._device_property.from_config_value
                ) as mock:
            sweep_prop.from_config_value(self.dso.trigger.edge, value)
        mock.assert_called_once()

    def test_TriggerSlopeVoltageLevelsProperty_as_from_config(self):
        # TriggerSlopeVoltageLevelsProperty.as_config_value() calls
        # getter(); TriggerSlopeVoltageLevelsProperty.from_config_value()
        # calls setter().
        voltage_levels_prop = ds1052.TriggerModeSettingsSlope.voltage_levels
        with patch.object(
                voltage_levels_prop, 'getter',
                wraps=voltage_levels_prop.getter) as mock:
            value = voltage_levels_prop.as_config_value(self.dso.trigger.slope)
        mock.assert_called_once()
        with patch.object(
                voltage_levels_prop, 'setter',
                wraps=voltage_levels_prop.setter) as mock:
            voltage_levels_prop.from_config_value(
                self.dso.trigger.slope, value)
        mock.assert_called_once()

    def test_TriggerModeSettingsEdge_get_set_config(self):
        edge_trigger_config_properties = (
            'source', 'coupling', 'sweep', 'level', 'slope', 'sensitivity')
        self.check_property_container_get_set_config(
            self.dso.trigger.edge, edge_trigger_config_properties)

    def test_TriggerModeSettingsPulse_get_set_config(self):
        pulse_trigger_config_properties = (
            'source', 'coupling', 'sweep', 'level', 'sensitivity',
            'time_condition', 'time_condition_value')
        self.check_property_container_get_set_config(
            self.dso.trigger.pulse, pulse_trigger_config_properties)

    def test_TriggerModeSettingsVideo_get_set_config(self):
        pulse_trigger_config_properties = (
            'source', 'level', 'sensitivity', 'sync', 'polarity', 'standard',
            'line')
        self.check_property_container_get_set_config(
            self.dso.trigger.video, pulse_trigger_config_properties)

    def test_TriggerModeSettingsSlope_get_set_config(self):
        pulse_trigger_config_properties = (
            'source', 'coupling', 'sweep', 'sensitivity', 'time_condition',
            'time_condition_value', 'voltage_levels')
        self.check_property_container_get_set_config(
            self.dso.trigger.slope, pulse_trigger_config_properties)

    def test_TriggerModeSettingsAlternation_get_set_config(self):
        # For now, a pretty dumb implementation...
        self.assertEqual({}, self.dso.trigger.alternation.get_config())

    def test_Trigger_get_set_config(self):
        with ExitStack() as stack:
            trigger_mode_mocks = [
                stack.enter_context(
                    patch.object(self.dso.trigger[tr_mode], 'get_config',
                    wraps=self.dso.trigger[tr_mode].get_config))
                for tr_mode in TriggerMode]
            current_mode_prop_mock = stack.enter_context(
                patch.object(
                    ds1052.Trigger.mode, 'as_config_value',
                    wraps=ds1052.Trigger.mode.as_config_value))
            holdoff_mock = stack.enter_context(
                patch.object(ds1052.Trigger.holdoff, 'as_config_value',
                             wraps=ds1052.Trigger.holdoff.as_config_value))
            config = self.dso.trigger.get_config()
        self.assertEqual(
            {mode.name for mode in TriggerMode}.union({'mode', 'holdoff'}),
            set(config))
        for mock in trigger_mode_mocks:
            mock.assert_called_once()
        current_mode_prop_mock.assert_called_once()
        holdoff_mock.assert_called_once()

        with ExitStack() as stack:
            trigger_mode_mocks = [
                stack.enter_context(
                    patch.object(
                        self.dso.trigger[tr_mode], 'set_config',
                        wraps=self.dso.trigger[tr_mode].set_config))
                for tr_mode in TriggerMode]
            current_mode_prop_mock = stack.enter_context(
                patch.object(
                    ds1052.Trigger.mode, 'from_config_value',
                    wraps=ds1052.Trigger.mode.from_config_value))
            holdoff_mock = stack.enter_context(
                patch.object(
                    ds1052.Trigger.holdoff, 'from_config_value',
                    wtapr=ds1052.Trigger.holdoff.from_config_value))
            self.dso.trigger.set_config(config)
        self.assertEqual(
            {mode.name for mode in TriggerMode}.union({'mode', 'holdoff'}),
            set(config))
        for mock in trigger_mode_mocks:
            mock.assert_called_once()
        current_mode_prop_mock.assert_called_once()
        holdoff_mock.assert_called_once()

    def test_trigger_level_setting_changing_channel_scale_offset(self):
        # Trigger levels and channel scale/offset.
        #
        # Set a "large" triggger channel scale/offset and the max trigger
        # level for this channel/offset.
        current_scale = self.dso.channel[1].scale
        current_offset = self.dso.channel[1].offset
        current_tr_mode = self.dso.trigger.mode
        current_tr_source = self.dso.trigger.edge.source
        current_tr_level = self.dso.trigger.edge.level
        try:
            self.dso.channel[1].scale = 1
            self.dso.channel[1].offset = 0
            self.dso.trigger.mode = TriggerMode.edge
            self.dso.trigger.edge.source = ChannelNumber.channel1
            self.dso.trigger.edge.level = 6

            # When the channel scale is decreased, the trigger level
            # decreases too.
            self.dso.channel[1].scale = 0.1
            self.assertEqual(0.6, self.dso.trigger.edge.level)

            # When the scale is increased again, the trigger level is back
            # at the larger value.
            self.dso.channel[1].scale = 1
            self.assertEqual(6, self.dso.trigger.edge.level)
        finally:
            self.dso.channel[1].scale = current_scale
            self.dso.channel[1].offset = current_offset
            self.dso.trigger.mode = current_tr_mode
            self.dso.trigger.edge.source = current_tr_source
            self.dso.trigger.edge.level = current_tr_level

    def trigger_levels_config(self, level):
       return {
           'channel': {
               1: {
                   'scale': 2,
                   'offset': 0,
                   },
               },
           'trigger': {
               'mode': 'pulse',
               'edge': {
                   'source': 1,
                   'level': level,
                   },
               },
           }

    def test_set_config_trigger_levels(self):
        # Setting a trigger level that is outside of the
        # current trigger channel's scale/offset is possblie.
        current_scale_ch1 = self.dso.channel[1].scale
        current_offset_ch1 = self.dso.channel[1].offset
        current_probe_attenuation_ch1 = self.dso.channel[1].probe_attenuation
        current_trigger_mode = self.dso.trigger.mode
        current_trigger_level = self.dso.trigger[current_trigger_mode].level
        current__edge_trigger_level = self.dso.trigger[
            TriggerMode.edge].level
        try:
            self.dso.channel[1].scale = 1
            self.dso.channel[1].offset = 0
            # 30V is outside the actually possible range of
            # channel 1 and 2 as well as the external source.
            # But with an offset change the value will "fit".
            config = {
                'channel': {
                    1: {
                        'scale': 2,
                        'offset': 0,
                        },
                    },
                'trigger': {
                    'mode': 'pulse',
                    'edge': {
                        # 30V is outside the actually possible range of
                        # channel 1 and 2 as well as the external source.
                        # But with an offset change the value will "fit".
                        'source': 1,
                        'level': 30,
                        },
                    },
                }
            # _TriggerLevelForModeProperty.adjust_source_scale_offset()
            # has several return statement. Try each of them with
            # the min and max values.
            # 1. Trigger level is within the range for the trigger channel's
            # scale and offset.
            self.dso.set_config(self.trigger_levels_config(12))
            self.assertEqual(12, self.dso.trigger.edge.level)
            self.dso.set_config(self.trigger_levels_config(-12))
            self.assertEqual(-12, self.dso.trigger.edge.level)

            # 2. Trigger level is within the trigger level range for max
            # voltage scale (100) and current offset.
            self.dso.set_config(self.trigger_levels_config(600))
            self.assertEqual(600, self.dso.trigger.edge.level)
            self.dso.set_config(self.trigger_levels_config(-600))
            self.assertEqual(-600, self.dso.trigger.edge.level)

            # 3. Trigger level is within the trigger level range for max
            # voltage scale (100) and min/max offset.
            self.dso.set_config(self.trigger_levels_config(1000))
            self.assertEqual(1000, self.dso.trigger.edge.level)
            self.dso.set_config(self.trigger_levels_config(-1000))
            self.assertEqual(-1000, self.dso.trigger.edge.level)

            with self.assertRaises(DS1052PropertyValueError):
                self.dso.set_config(self.trigger_levels_config(1001))
            with self.assertRaises(DS1052PropertyValueError):
                self.dso.set_config(self.trigger_levels_config(-1001))
        finally:
            self.dso.channel[1].probe_attenuation = (
                current_probe_attenuation_ch1)
            self.dso.channel[1].scale = current_scale_ch1
            self.dso.channel[1].offset = current_offset_ch1
            self.dso.trigger.mode = current_trigger_mode
            self.dso.trigger[current_trigger_mode].level = current_trigger_level
            self.dso.trigger[
                TriggerMode.edge].level = current__edge_trigger_level

    def slope_trigger_levels_config(self, levels):
       return {
           'channel': {
               1: {
                   'scale': 2,
                   'offset': 0,
                   },
               },
           'trigger': {
               'mode': 'pulse',
               'slope': {
                   'source': 1,
                   'voltage_levels': levels,
                   },
               },
           }

    def test_set_config_slope_trigger(self):
        current_scale_ch1 = self.dso.channel[1].scale
        current_offset_ch1 = self.dso.channel[1].offset
        current_probe_attenuation_ch1 = self.dso.channel[1].probe_attenuation
        current_trigger_mode = self.dso.trigger.mode
        current_slope_trigger_levels = self.dso.trigger[
            TriggerMode.slope].voltage_levels
        try:
            # Trigger levels within the range for the current channel's
            # scale/offset.
            self.dso.channel[1].scale = 2
            self.dso.set_config(
                self.slope_trigger_levels_config((-5, -3)))
            self.assertEqual((-5, -3), self.dso.trigger.slope.voltage_levels)
            self.dso.set_config(
                self.slope_trigger_levels_config((-5, 5)))
            self.assertEqual((-5, 5), self.dso.trigger.slope.voltage_levels)
            self.dso.set_config(
                self.slope_trigger_levels_config((2, 12)))
            self.assertEqual((2, 12), self.dso.trigger.slope.voltage_levels)

            # Wrong "order".
            with self.assertRaises(DS1052PropertyValueError) as ctx:
                self.dso.set_config(
                    self.slope_trigger_levels_config((1, -1)))
            self.assertEqual(
                'The first value (voltage_level_lower) must be smaller than '
                'the second value (voltage_level_upper).',
                str(ctx.exception))

            # Levels outside the range for the current trigger channels's
            # scale/offset.
            self.dso.set_config(
                self.slope_trigger_levels_config((-40, 30)))
            self.assertEqual((-40, 30), self.dso.trigger.slope.voltage_levels)

            # Max difference (1200V) for the max channel scale (100V).
            self.dso.set_config(
                self.slope_trigger_levels_config((-800, 400)))
            self.assertEqual((-800, 400), self.dso.trigger.slope.voltage_levels)

            # Max difference exceeded.
            with self.assertRaises(DS1052PropertyValueError) as ctx:
                self.dso.set_config(
                    self.slope_trigger_levels_config((-800.1, 400)))
            self.assertEqual(
                'The difference of the trigger levels (-800.1, 400) must '
                'not exceed 1200.0',
                str(ctx.exception))

            # Mix/max values are determined by the possible offset range
            # (-400V .. +400V for the selected probe attenuation) and the
            # max scale (100V).
            self.dso.set_config(
                self.slope_trigger_levels_config((-1000, -400)))
            self.assertEqual(
                (-1000, -400), self.dso.trigger.slope.voltage_levels)
            with self.assertRaises(DS1052PropertyValueError) as ctx:
                self.dso.set_config(
                    self.slope_trigger_levels_config((-1001, -401)))
            self.assertEqual(
                'Only values greater than or equal to vertical scale - '
                'vertical offset (-1000.0) allowed.',
                str(ctx.exception))

            self.dso.set_config(
                self.slope_trigger_levels_config((400, 1000)))
            self.assertEqual(
                (400, 1000), self.dso.trigger.slope.voltage_levels)
            with self.assertRaises(DS1052PropertyValueError) as ctx:
                self.dso.set_config(
                    self.slope_trigger_levels_config((401, 1001)))
            self.assertEqual(
                'Only values less than or equal to vertical scale - '
                'vertical offset (1000.0) allowed.',
                str(ctx.exception))
        finally:
            self.dso.channel[1].scale = current_scale_ch1
            self.dso.channel[1].offset = current_offset_ch1
            self.dso.channel[1].probe_attenuation = (
                current_probe_attenuation_ch1)
            self.dso.trigger.mode = current_trigger_mode
            self.dso.trigger[TriggerMode.slope].voltage_levels = (
                current_slope_trigger_levels)

    def test_set_config_filter_property_in_stop_mode(self):
        config_filter_off = {'filter_enabled': False}
        config_filter_on = {'filter_enabled': True}

        # The DS1052 must not be in trigger mode "stop" when the
        # "digital filter" is enabled or disabled. Channel.set_config()
        # sets the DS1052 shortly into RUN mode if necessary to change
        # the value.
        dso_stopped = self.dso.trigger.status == TriggerStatus.stop
        if not dso_stopped:
            self.dso.wait_until_stopped()
        try:
            self.dso.channel[1].set_config(config_filter_on)
            self.dso.channel[1].set_config(config_filter_off)
        finally:
            if not dso_stopped:
                self.dso.wait_until_running()


class DS1052TestsWithTestSignalBase:
    """ Tests that require a test signal.
    The "probe comp" signal of the device, a 1kHz square wave that
    "switches" betwwen 0V and 3V, must be connected to CH1 and CH2;
    the compensation capacitors of the probes should be properly adjusted
    and the attenuation settings of both channels must match the position
    the probe attenuation switches.

    Uses the same instance of DS1052 for all tests. In many cases not the
    best idea – but the required setup of the device takes too long to
    be done for each test...

    Remember that the dso.auto() call does NOT change the coupling of
    the channels, so we will see voltages between 0V and 3V for DC
    coupling or between -1.5V and +1.5V for AC coupling.
    """

    # XXX This is annoying: If a measurement property is accessed too early
    # after a call of DS1052.auto(), the result tends to be 9.9e-37.
    # Seen for example in tests of DS1052.frequency and DS1052.amplitude.
    # Might make sense to add a sleep() call to DS1053.auto() itself.
    # Anyway, the root cause is probably that the DS1052 does not support
    # the command "*OPC?". The "Programmer Manual" mentions it only on page
    # 120 in an examplehow to use VISA in Windows with the device.
    # The command not described anywhere; grepping through the output of
    # "strings <firmware-file>" shows many commands described in the
    # manual (I did not check all though) – but "OPC" does not appear.
    # XXX Would it make sense to add a sleep() call to DS1052.auto()?
    WAIT_TIME_AFTER_AUTO_CALL = 0.5

    def _callTestMethod(self, method):
        try:
            method()
        except:
            self.dso._tmc_device.show_log_buff()
            raise

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if os.getenv('DS1052_TEST_SIGNAL_CONNECTED') is None:
            raise SkipTest(
                'Set the env var DS1052_TEST_SIGNAL_CONNECTED to run these '
                'tests')

        cls.dso = DS1052(tmc_class=TMC_CLASS, resource_manager=visa_rm)
        cls.dso.open()
        cls.dso.beep_enabled = False

        cls.set_default_params()

    @classmethod
    def set_default_params(cls):
        # Reasonable settings for a 1kHz signal switching between 0V and 3V.
        for ch in 1, 2:
            cls.dso.channel[ch].bandwidth_limit_enabled = False
            cls.dso.channel[ch].coupling = ChannelCoupling.dc
            cls.dso.channel[ch].enabled = True
            cls.dso.channel[ch].display_inverted = False
            # This line is obviously nonsensical for the main purpose,
            # was added out of some, erm, sloppiness -- and revealed
            # a strange issue, see the comment a few lines below.
            cls.dso.channel[ch].offset = 0.52
            cls.dso.channel[ch].scale = 1.0
            cls.dso.channel[ch].filter_enabled = False
        cls.dso.channel[1].offset = 0.52
        # XXX When the DS1052 is set to the timebase scale 100ms/div, the next
        # statement times out when ds1052._PROPERTY_WAIT_TIMEOUT is 0.5.
        # Quite interesting that the TB scale setting has an impact on
        # a parameter that does not seem to be that closely related.
        # OTOH, the conversion rules of the raw waveform data let me suspect
        # this: The vertical offset might be implemented hardware-wise as
        # an offset that is added to the input signal before it is fed into
        # the ADC. When an acquisition is running, the offset should
        # not change immediately to ensure consistency of the acquired data.
        # At 100ms/div, the sample rate is 6.827kSamples/s, so filling
        # an 8k buffer needs more than one second.
        # But this obviously does not explain everything: (1) Why does the
        # first change of the offset in the for loop above _not_ time out?
        # (2) "Slower" timebase scale settings than 100ms/div should require
        # an even longer timeout if the guessing above is right –– but I do
        # not see such an increase in the required timeout.
        cls.dso.channel[2].offset = -3.52
        cls.dso.timebase_mode = TimebaseMode.main
        cls.dso.timebbase_offset = 0
        cls.dso.timebase_scale = 0.5e-3
        cls.dso.timebase_format = TimebaseFormat.y_t
        cls.dso.acquisition_type = AcquisitionType.normal
        cls.dso.acquisition_mode = AcquisitionMode.real_time
        cls.dso.acquisition_averages = 4
        cls.dso.acquisition_memory_depth = AcquisitionMemoryDepth.normal
        cls.dso.points_mode = PointsMode.normal
        cls.dso.trigger.mode = TriggerMode.edge
        cls.dso.trigger.holdoff = 500e-9
        cls.dso.trigger.edge.source = 1
        cls.dso.trigger.edge.level = 1.52
        cls.dso.trigger.edge.sweep = Sweep.auto
        cls.dso.trigger.edge.coupling = TriggerCoupling.dc
        cls.dso.trigger.edge.slope = Slope.positive
        cls.dso.trigger.edge.sensitivity = 0.5

        cls.dso.wait_until_running()

    @classmethod
    def tearDownClass(cls):
        cls.dso.close()
        super().tearDownClass()

    @classmethod
    def wait_for_trigger_status(cls, status, timeout=1.0):
        wait_until = time() + timeout
        while time() < wait_until:
            if cls.dso.trigger.status == status:
                return
        raise RuntimeError(f'Timeout waiting for trigger status {status}')

    def setUp(self):
        # Check that the device is in the status that it should be in
        # after the auto() call in setUpClass(): Some tests may have changed
        # the status without cleaning up...
        try:
            self.assertEqual(
                TriggerMode.edge, self.dso.trigger.mode,
                f'Unexpected trigger mode: {self.dso.trigger.mode}')
            sweep_mode = self.dso.trigger[self.dso.trigger.mode].sweep
            self.assertEqual(
                Sweep.auto, sweep_mode, f'Unexpected sweep mode: {sweep_mode}')
            trigger_status = self.dso.trigger.status
            self.assertIn(
                trigger_status,
                (TriggerStatus.auto, TriggerStatus.run,
                 TriggerStatus.triggered),
                f'Unexpected trigger status: {trigger_status}')
            trigger_source = self.dso.trigger[self.dso.trigger.mode].source
            self.assertIn(
                trigger_source,
                (TriggerSource.channel1, TriggerSource.channel2),
                f'Unexpected trigger source {trigger_source}')
            trigger_level = self.dso.trigger[self.dso.trigger.mode].level
            # The trigger level should be "half way" between min and max voltage
            # of the trigger source.
            # XXX In the first call of this method after setUpClass()
            # voltage_top and voltage_base show often the value 9.9e+37.
            # This lets the assertTrue() below fail.
            # Could this mean something like "measurement not yet available"?
            # Is anywhere documented what this obviously impossible (but
            # probably intended?) value is supposed to mean?
            # We may see "inf"/9.9e37 for more than 0.5s.
            wait_until = time() + 2
            while time() < wait_until:
                v_top, q_top = self.dso.channel[trigger_source].voltage_top
                v_base, q_base = self.dso.channel[trigger_source].voltage_base
                if (q_top == MeasurementQualifier.value
                    and q_base == MeasurementQualifier.value):
                    break
                # Hrm. It happens occasionally that the DS1052 returns "99e36"
                # for two seconds without the "sleep(0.01)" below. The
                # "native" delay (i.e., without sleep() between two SCPI
                # commands) is ca 1.2ms. Let's see if this helps.
                #
                # I've meanwhile asked the Rigol support for recommendations
                # about delays between two SCPI commands but got only a quite
                # vague answer that 0.1s, or even 0.12s would be good.
                # Rigol's Ultrascope program works that way but these delays
                # make it ridiculously slow... So let's see if a shorter
                # pause helps here.
                sleep(0.01)
            v_trigger = (v_top + v_base) / 2
            self.assertTrue(
                v_trigger - 0.1 <= trigger_level <= v_trigger  + 0.1,
                f'Unexpected trigger level in setUp(): {trigger_level} for '
                f'Vtop {v_top} and Vbase {v_base}')
        except:
            self.dso._tmc_device.show_log_buff()
            raise

class DS1052TestsWithTestSignal(DS1052TestsWithTestSignalBase, TestCase):
    def check_channel_measurement(
            self, attribute_name, value_min, value_max, retry_on_inaccurate=0):
        channel_specs = tuple(ChannelNumber) + (
            TriggerSource.channel1, TriggerSource.channel2, 1, 2)
        for channel in channel_specs:
            value, qualifier = (
                getattr(self.dso.channel[channel], attribute_name))
            while (
                    qualifier != MeasurementQualifier.value
                    and retry_on_inaccurate):
                retry_on_inaccurate -= 1
                sleep(0.01)
                value, qualifier = (
                    getattr(self.dso.channel[channel], attribute_name))
            self.assertEqual(
                qualifier, MeasurementQualifier.value,
                f'Measurement value: {value}')
            self.assertTrue(
                value_min <= value <= value_max,
                f'expected a value between {value_min} and {value_max} for '
                f'{attribute_name}[{channel}] but got {value} '
                f'(channel: {channel})')

    def test_voltage_pp(self):
        self.check_channel_measurement('voltage_pp', 2.8, 3.2)

    def test_voltage_max(self):
        # XXX 1. This is a bit risky: The probe calibration signal switches
        # between 0V and 3V, the auto() has hopefully set the coupling of
        # CH1 and CH2 to DC. If this assumption is wrong, the test will fail.
        # XXX 2. Better explicitly set the coupling for CH1, CH2 to AC
        # _and_ DC and check the values in both settings.
        # Problem: The required properties are not yet implemented.
        # A range of (2.9, 3.1) can lead to failures...
        self.check_channel_measurement('voltage_max', 2.8, 3.2)

    def test_voltage_min(self):
        # XXX Same problem as with voltage_max
        self.check_channel_measurement('voltage_min', -0.1, 0.1)

    def test_amplitude(self):
        self.check_channel_measurement('amplitude', 2.9, 3.1)

    def test_voltage_top(self):
        # XXX Same problem as with voltage_max
        self.check_channel_measurement('voltage_top', 2.9, 3.1)

    def test_voltage_base(self):
        # XXX Same problem as with voltage_max
        self.check_channel_measurement('voltage_base', -0.1, 0.1)

    def test_voltage_average(self):
        # XXX Same problem as with voltage_max
        self.check_channel_measurement('voltage_average', 1.5, 1.6)

    def test_voltage_rms(self):
        # One half period has the value 3V, the other half has the value 0V,
        # RMS is the integral of the square of the voltage over one period,
        # so the expected value is:
        expected = sqrt(3 * 3 / 2.0)
        self.check_channel_measurement(
            'voltage_rms', expected - 0.1, expected + 0.1)

    def test_voltage_overshoot(self):
        self.check_channel_measurement('voltage_overshoot', -0.1, 0.1)

    def test_voltage_preshoot(self):
        # XXX Same problem as with voltage_max
        self.check_channel_measurement('voltage_preshoot', -0.1, 0.1)

    def test_frequency(self):
        # We can get math.inf for the signal frequency for a short time.
        # so try again when that happens.
        # Seems to mean "not yet ready for a measurement"?
        # One would assume that the frequency of a 1kHz 3Vpp square wave
        # signal can be reliably measured with an accuracy of 0.1%. But
        # the DS1052E returns remarkably often the value 990. So let's
        # relax the test somewhat: This test suite is after all not about
        # the functions of the DS1062 but about controlling it more or
        # less reliably.
        self.check_channel_measurement(
            #'frequency', 999, 1001, retry_on_inaccurate=3)
            'frequency', 980, 1020, retry_on_inaccurate=3)
        original_tb_scale = self.dso.timebase_scale
        try:
            # The DS1052 sometimes returns the value math.inf. This looks
            # really odd, so: For which conditions is this value is returned?
            # Guess: a somewhat too "long" timebase scale/too low sampling
            # rate. 5ms/div and 50kSamples/s leave some room for a frequency
            # measurement of a 1kHz signal but not too much.
            #
            # XXX This is crazy: The following tests succeed...
            # Multiply the timebase scale by 10 leads to a division by
            # 10 of the reported frequency.
            self.dso.timebase_scale = 5e-3
            self.check_channel_measurement('frequency', 99, 101)
            # But only for a short time, then things are sane again.
            sleep(0.1)
            self.check_channel_measurement('frequency', 999, 1001)

            # Multiplying the timebase again by 4, the same happens.
            self.dso.timebase_scale = 20e-3
            self.check_channel_measurement('frequency', 24, 26)
            sleep(0.1)
            result = self.dso._tmc_device.ask(':MEAS:FREQ? 1')
            # ... but the DS1052 now says that it cannot properly measure
            # a frequency. A value "more than 250Hz" makes sense: With
            # 10kSamples/s a measurement with only 40 samples per cycle
            # might not very reliable.
            self.assertEqual('>2.50e+02', result)
            # Just to be sure: This s a permanent value.
            sleep(1)
            result = self.dso._tmc_device.ask(':MEAS:FREQ? 1')
            self.assertEqual('>2.50e+02', result)

            # When the timebase scale is reduced to values too small for a
            # 1 kHz signal...
            self.dso.timebase_scale = 5e-9
            # ...the short-lived wrong value is, well, suprising...
            result = self.dso._tmc_device.ask(':MEAS:FREQ? 1')
            self.assertEqual('>1.00e+09', result)
            sleep(0.1)
            # ...and the final value 99e36 is also odd: Sure, with 5e-9s/div,
            # or 500MSamples/s and 8k memory, a complete cycle of the 1kHz
            # input signal does not fit into the memory. But the lower limit
            # of a frequency measurement is easy to estimate: The inverse
            # of the time duration of the data acquisition. The duration
            # of the data acquisition is 8192/500e9, so the mininum frequency
            # to stire a full cycle is 8192/500e9 -> ca 61MHz.
            #
            # So the DS1052 could return a value like "<6.1e7", as is does
            # for some other measurements.
            result = self.dso._tmc_device.ask(':MEAS:FREQ? 1')
            self.assertEqual('99e36', result)
        finally:
            self.dso.timebase_scale = original_tb_scale
            # XXX The TB scale change affects the next test,
            # test_negative_duty_cycle(): Without the sleep(), the value
            # 0.33 may be seen there. Would it make sense to add some sort
            # of attribute to DS1052, like "wait for timing measurements until
            # N acquisitions with the newly selected TB scale are finished"?
            sleep(0.2)

    def test_rise_time(self):
        current_timebase_scale = self.dso.timebase_scale
        current_trigger_mode = self.dso.trigger.mode
        current_trigger_slope = self.dso.trigger.edge.slope
        self.dso.trigger.mode = TriggerMode.edge
        # In the "auto settings", the DS1052 tells that the rise time
        # cannot be measured accurately. Makes sense with a timebase
        # scale of 0.5ms/div and a sample rate of 500kSamples/s: When there
        # are only 500 samples for one cycle, a reliable measurement
        # of the edges of a square wave are not possible.
        try:
            for ch in 1, 2:
                value, qualifier = self.dso.channel[ch].rise_time
                # We get occcasionally `inf`. In that case wait a bit and try
                # again.
                retries = 5
                while retries > 0:
                    retries -= 1
                    if value == inf:
                        sleep(0.01)
                        value, qualifier = self.dso.channel[ch].rise_time
                self.assertEqual(qualifier, MeasurementQualifier.less_than)
                self.assertEqual(value, 3e-5)
            # Now use a better time resolution.
            self.dso.timebase_scale = 2e-6
            # XXX I really hate the need to wait for a somewhat larger time.
            # Is there any way to query the device for something like
            # "Did you already measure X after the last parameter change?"
            sleep(0.5)
            # The range of allowed values looks quite large...
            # Observed values: 2.92e-6, 3.16e-6, 3.28e-6, 3.32e-6, 3.44e-6,
            # 3.08e-6, 3.52e-6, 3.64e-5
            # The relatively wide range could be caused by a problem with
            # one of my probes.
            self.check_channel_measurement('rise_time', 2.8e-6, 3.7e-6)
        finally:
            self.dso.trigger.mode = current_trigger_mode
            self.dso.trigger.edge.slope = current_trigger_slope
            self.dso.timebase_scale = current_timebase_scale
            sleep(0.5)

    def test_fall_time(self):
        current_timebase_scale = self.dso.timebase_scale
        current_trigger_mode = self.dso.trigger.mode
        current_trigger_slope = self.dso.trigger.edge.slope
        self.dso.trigger.mode = TriggerMode.edge
        # For some reason, this test tends to fail with Slope.positive...
        self.dso.trigger.edge.slope = Slope.negative
        try:
            for ch in 1, 2:
                value, qualifier = self.dso.channel[ch].fall_time
                retries = 5
                while retries > 0:
                    retries -= 1
                    if value == inf:
                        sleep(0.01)
                        value, qualifier = self.dso.channel[ch].rise_time
                self.assertEqual(qualifier, MeasurementQualifier.less_than)
                self.assertEqual(value, 3e-5)
            # Now use a better time resolution.
            self.dso.timebase_scale = 2e-6
            sleep(0.5)
            self.check_channel_measurement('fall_time', 2.8e-6, 3.7e-6)
        finally:
            self.dso.trigger.mode = current_trigger_mode
            self.dso.trigger.edge.slope = current_trigger_slope
            self.dso.timebase_scale = current_timebase_scale
            sleep(0.5)

    def test_period(self):
        # 1 ms with a bit measurement error.
        self.check_channel_measurement('period', 0.99e-3, 1.01e-3)

    def test_positive_pulse_width(self):
        # 0.5 ms with a bit measurement error.
        self.check_channel_measurement('positive_pulse_width', 0.49e-3, 0.51e-3)

    def test_negative_pulse_width(self):
        # 0.5 ms with a bit measurement error.
        #self.check_channel_measurement('negative_pulse_width', 0.49e-3, 0.51e-3)
        # More "tolerance" needed, similar to positive/negatvie duty cycle...
        # Seen for example 0.4e-3
        self.check_channel_measurement('negative_pulse_width', 0.35e-3, 0.51e-3)

    def test_positive_duty_cycle(self):
        # 50% with a bit measurement error.
        # Well. Occasionally we get the value 0.333… For other measurement
        # values, the DS1052 returns 9.9e37 ("inf") when the device is not
        # yet ready to provide reliable values. Why not for duty cycle?
        # Once again, just "allow" the bogus value and carry on.
        #self.check_channel_measurement('positive_duty_cycle', 0.49, 0.51)
        self.check_channel_measurement('positive_duty_cycle', 0.3, 0.51)

    def test_negative_duty_cycle(self):
        # 50% with a bit measurement error.
        # See test_positive_duty_cycle(): The funny detail is that _both_
        # values can be too small, but I haven't yet seen either of them
        # being too large... Is this behavious perhaps what Rigol meant
        # with the slogan "beyond measure"?
        #self.check_channel_measurement('negative_duty_cycle', 0.49, 0.51)
        self.check_channel_measurement('negative_duty_cycle', 0.3, 0.51)

    def test_positive_edge_delay(self):
        # XXX I don't really get what this is supposed to be. With the 1kHz
        # probe test signal, the measured value is quite small.
        #
        # First attempts to read the property tend to return the qualifier
        # "less than".
        #
        # Giving up: It can also happem that the value is always `inf`
        # Waiting does not change anything. So only check that we get data
        # expected for measurement properties.
        #self.check_channel_measurement(
        #    'positive_edge_delay', -670e-6, -650e-6, retry_on_inaccurate=10)
        value, qualifier = self.dso.channel[2].positive_edge_delay
        self.assertEqual(float, type(value))
        self.assertEqual(MeasurementQualifier, type(qualifier))

    def test_negative_edge_delay(self):
        # XXX See the comment at the definition of DS1052.positive_edge_delay:
        #self.check_channel_measurement(
        #    'negative_edge_delay', -670e-6, -650e-6, retry_on_inaccurate=10)
        value, qualifier = self.dso.channel[1].negative_edge_delay
        self.assertEqual(float, type(value))
        self.assertEqual(MeasurementQualifier, type(qualifier))

    def test_display_all_measurements(self):
        self.dso.display_all_measurements = True
        self.assertTrue(self.dso.display_all_measurements)
        self.dso.display_all_measurements = False
        self.assertFalse(self.dso.display_all_measurements)

    # Tests of TriggerStatus and related things. To some extent written
    # just to observe under which conditions the DS1052 is in a certain
    # TriggerStatus.

    TriggerInfo = namedtuple(
        'TriggerInfo', ('status', 'started', 'duration', 'count'))

    def record_trigger_statuses(self, final_status, timeout, skip_first):
        # skip_first: If the final status is present _at the start_, wait
        # until the device witches into another status.
        statuses = []
        started = time()
        run_until = started + timeout
        now = time()
        if skip_first:
            while now < run_until:
                status = self.dso.trigger.status
                statuses.append((status, now))
                if status != final_status:
                    break
                sleep(0.005)
                now = time()
        while now < run_until:
            status = self.dso.trigger.status
            statuses.append((status, now))
            if status == final_status:
                return statuses, True
            # The DS1052 is "slow enough" in many (all?) circumstances
            # that a short sleep() does not lead to misses in trigger states.
            sleep(0.005)
            now = time()
        return statuses, False if final_status is not None else True

    def trigger_status_durations(
            self, final_status=None, timeout=3, show=False, skip_first=False,
            fail_on_timeout=True):
        statuses, success = self.record_trigger_statuses(
            final_status, timeout, skip_first)
        result = []
        if not statuses:
            # Should not happen: The DS1052 should _always_ report a status...
            raise RuntimeError('No statuses recorded at all')
        last_status = None
        t0 = statuses[0][1]
        for status, recorded in statuses:
            if last_status != status:
                if last_status is not None:
                    result.append(
                        self.TriggerInfo(
                            status=last_status, started=start_recorded,
                         duration=end_recorded - start_recorded, count=count))
                last_status = status
                start_recorded = end_recorded = recorded - t0
                count = 1
            else:
                end_recorded = recorded - t0
                count += 1
        result.append(
            self.TriggerInfo(
                status=last_status, started=start_recorded,
                duration=end_recorded - start_recorded, count=count))
        if show or not success:
            print()
            for item in result:
                print(item)
        if not success and fail_on_timeout:
            self.fail(f'Final status {final_status} not reached')
        return result

    def test_auto(self):
        # What happens when ":AUTO" is issued?
        # Get a defined start status.
        try:
            self.dso.stop()
            # The timing etc is not that intersting here, just ensure that
            # TriggerStatus.stop is reached.
            self.trigger_status_durations(TriggerStatus.stop)
            self.dso.auto()
            status_info = self.trigger_status_durations(TriggerStatus.triggered)
            # Sometimes three statuses are recorded, sometime four...
            # TriggerStatus.run exists for ca 1.5s.
            expected_3 = [
                TriggerStatus.stop, TriggerStatus.run, TriggerStatus.triggered]
            expected_4 = [
                TriggerStatus.stop, TriggerStatus.auto, TriggerStatus.run,
                TriggerStatus.triggered]
            if len(status_info) == 3:
                self.assertEqual(
                    expected_3, [item.status for item in status_info])
            else:
                self.assertEqual(
                    expected_4, [item.status for item in status_info])
        finally:
            # Waiting for WAIT_TIME_AFTER_AUTO_CALL is probably no longer
            # needed due to the set_defaults() below. Let's see...
            # Prevent failures in subsequent tests...
            #sleep(self.WAIT_TIME_AFTER_AUTO_CALL)
            self.set_default_params()

    def test_stop_run__sweep_mode_auto_useful_trigger_setting(self):
        # setUp() ensures that the device is in sweep mode auto.
        self.dso.stop()
        self.trigger_status_durations(TriggerStatus.stop)
        # The status "triggered" should be reached quickly after a run() call.
        self.dso.run()
        status_info = self.trigger_status_durations(TriggerStatus.triggered)
        self.assertEqual(
            [TriggerStatus.stop, TriggerStatus.run, TriggerStatus.triggered],
            [item.status for item in status_info])
        self.assertTrue(status_info[0].duration < 0.1)
        self.assertTrue(
            status_info[1].duration < 0.1,
            'Is the probe adjustment signal properly connected?')

    def test_stop_run__sweep_mode_auto_useless_trigger_setting(self):
        # setUp() ensures that the device is in sweep mode auto.
        self.dso.stop()
        self.trigger_status_durations(TriggerStatus.stop)
        # The call of self.dso.auto() in setUpClass() should have set
        # a trigger level near 0V (assuming that CH1 and CH2 are AC coupled).
        # When the trigger level is set to a value greater than the
        # amplitude of the signal, we should not see TriggerStatus.triggered.
        # The test signal switches between 0V and 3V; to prevent test failures
        # just because auto() might decide to set DC coupling of the channels
        # and the trigger source, set a trigger voltage of 4V.
        current_trigger_level = self.dso.trigger[self.dso.trigger.mode].level
        self.dso.trigger[self.dso.trigger.mode].level = 4
        try:
            self.dso.run()
            status_info = self.trigger_status_durations(
                TriggerStatus.auto, timeout=2, show=True)
            self.assertEqual(
                [TriggerStatus.stop, TriggerStatus.run, TriggerStatus.auto],
                [item.status for item in status_info])
            self.assertTrue(status_info[0].duration < 0.1)
            self.assertTrue(0.9 < status_info[1].duration < 1.1)
        finally:
            self.dso.trigger[self.dso.trigger.mode].level = (
                current_trigger_level)

    def test_stop_run__sweep_mode_normal_useful_trigger_setting(self):
        self.dso.stop()
        self.trigger_status_durations(TriggerStatus.stop)
        tr_mode = self.dso.trigger.mode
        self.dso.trigger[tr_mode].sweep = Sweep.normal
        try:
            # The status "triggered" should be reached quickly after a run()
            # call.
            self.dso.run()
            status_info = self.trigger_status_durations(
                TriggerStatus.triggered, show=True)
            self.assertEqual(
                [TriggerStatus.stop, TriggerStatus.run,
                 TriggerStatus.triggered],
                [item.status for item in status_info])
            self.assertTrue(status_info[0].duration < 0.1)
            self.assertTrue(
                status_info[1].duration < 0.1,
                'Is the probe adjustment signal properly connected?')
        finally:
            self.dso.trigger[tr_mode].sweep = Sweep.auto
        # XXX This is weird: The next test, test_voltage_average(), fails
        # in setUp() without this sleep() call because the device returns
        # the value 9.9e-37 for self.dso.voltage_top[trigger_channel]
        # and self.dso.voltage_base[trigger_channel].
        # What would the real conclusion be? Add a sleep() call to the
        # setter of DS1052.trigger.mode.sweep? Is this another case where
        # the "*OPC?" command would be really handy? Should the value
        # 9.9e+37 be treated as an indicator for "try again later"?
        sleep(self.WAIT_TIME_AFTER_AUTO_CALL)

    def test_stop_run__sweep_mode_normal_useless_trigger_setting(self):
        self.dso.stop()
        self.trigger_status_durations(TriggerStatus.stop)
        tr_mode = self.dso.trigger.mode
        self.dso.trigger[tr_mode].sweep = Sweep.normal
        current_trigger_level = self.dso.trigger[tr_mode].level
        # 4V as the trigger level is too large for a 3V signal.
        self.dso.trigger[tr_mode].level = 4
        try:
            # The status "triggered" should be reached quickly after a run()
            # call.
            self.dso.run()
            status_info = self.trigger_status_durations(
                TriggerStatus.wait, show=True)
            self.assertEqual(
                [TriggerStatus.stop, TriggerStatus.run, TriggerStatus.wait],
                [item.status for item in status_info])
            # The DSO is in the mode "RUN" for ca 1s, the goes into "WAIT".
            self.assertTrue(status_info[0].duration < 0.1)
            self.assertTrue(0.9 <= status_info[1].duration < 1.1)
        finally:
            self.dso.trigger[tr_mode].sweep = Sweep.auto
            self.dso.trigger[tr_mode].level = current_trigger_level
        # XXX This is weird: The next test, test_voltage_average(), fails
        # in setUp() without this sleep() call because the device returns
        # the value 9.9e-37 for self.dso.voltage_top[trigger_channel]
        # and self.dso.voltage_base[trigger_channel].
        # What would the real conclusion be? Add a sleep() call to the
        # setter of DS1052.sweep? Is this another case where the "*OPC?"
        # command would be really handy? Should the value 9.9e+37 be treated
        # as an indicator for "try again later"?
        sleep(self.WAIT_TIME_AFTER_AUTO_CALL)

    def test_stop_run__sweep_mode_single_useful_trigger_setting(self):
        self.dso.stop()
        self.trigger_status_durations(TriggerStatus.stop)
        tr_mode = self.dso.trigger.mode
        self.dso.trigger[tr_mode].sweep = Sweep.single
        try:
            # The status "triggered" should be reached quickly after a run()
            # call.
            self.dso.run()
            status_info = self.trigger_status_durations(
                TriggerStatus.stop, show=True, skip_first=True)
            self.assertEqual(
                [TriggerStatus.stop, TriggerStatus.run,
                 TriggerStatus.wait, TriggerStatus.stop],
                [item.status for item in status_info])
            self.assertTrue(status_info[0].duration < 0.1)
            self.assertTrue(
                status_info[1].duration < 0.1,
                'Is the probe adjustment signal properly connected?')
            self.assertTrue(
                status_info[2].duration < 0.1,
                'Is the probe adjustment signal properly connected?')
        finally:
            self.dso.trigger[tr_mode].sweep = Sweep.auto
        # XXX This is weird: The next test, test_voltage_average(), fails
        # in setUp() without this sleep() call because the device returns
        # the value 9.9e-37 for self.dso.voltage_top[trigger_channel]
        # and self.dso.voltage_base[trigger_channel].
        # What would the real conclusion be? Add a sleep() call to the
        # setter of DS1052.sweep? Is this another case where the "*OPC?"
        # command would be really handy? Should the value 9.9e+37 be treated
        # as an indicator for "try again later"?
        sleep(self.WAIT_TIME_AFTER_AUTO_CALL)

    def test_stop_run__sweep_mode_single_useless_trigger_setting(self):
        self.dso.stop()
        self.trigger_status_durations(TriggerStatus.stop)
        tr_mode = self.dso.trigger.mode
        self.dso.trigger[tr_mode].sweep = Sweep.single
        current_trigger_level = self.dso.trigger[tr_mode].level
        # 4V as the trigger level is too large for a 3V signal.
        self.dso.trigger[tr_mode].level = 4
        try:
            # The status "triggered" should be reached quickly after a run()
            # call.
            self.dso.run()
            # The final status specified here is _not_ expected to be reached...
            status_info = self.trigger_status_durations(
                TriggerStatus.stop, show=True, skip_first=True,
                fail_on_timeout=False)
            self.assertEqual(
                [TriggerStatus.stop, TriggerStatus.run,
                 TriggerStatus.wait],
                [item.status for item in status_info])
            self.assertTrue(status_info[0].duration < 0.1)
            self.assertTrue(status_info[1].duration < 0.1)
            # The DSO waited all the time for a trigger.
            self.assertTrue(status_info[2].duration > 2.8)
        finally:
            self.dso.trigger[tr_mode].sweep = Sweep.auto
            self.dso.trigger[tr_mode].level = current_trigger_level
        # XXX This is weird: In the next test, test_voltage_average(), fails
        # in setUp() without this sleep() call because the device returns
        # the value 9.9e-37 for self.dso.voltage_top[trigger_channel]
        # and self.dso.voltage_base[trigger_channel].
        # What would the real conclusion be? Add a sleep() call to the
        # setter of DS1052.sweep? Is this another case where the "*OPC?"
        # command would be really handy? Should the value 9.9e+37 be treated
        # as an indicator for "try again later"?
        sleep(self.WAIT_TIME_AFTER_AUTO_CALL)

    def test_set_trigger_50percent(self):
        tr_mode = self.dso.trigger.mode
        current_trigger_level = self.dso.trigger[tr_mode].level
        # A trigger voltage that is definitely useless for a 3V signal.
        self.dso.trigger[tr_mode].level = 4
        try:
            self.dso.trigger.set_50_percent()
            trigger_source = self.dso.trigger[self.dso.trigger.mode].source
            trigger_level =self.dso.trigger[self.dso.trigger.mode].level
            v_top, _ = self.dso.channel[trigger_source].voltage_top
            v_base, _ = self.dso.channel[trigger_source].voltage_base
            expected = (v_top + v_base) / 2
            self.assertTrue(
                expected - 0.1 <= trigger_level <= expected  + 0.1,
                f'Unexpected trigger level: {trigger_level} for Vtop {v_top} '
                f'and Vbase {v_base}')
        finally:
            self.dso.trigger[tr_mode].level = current_trigger_level

    def test_force_trigger(self):
        tr_mode = self.dso.trigger.mode
        current_trigger_level = self.dso.trigger[tr_mode].level
        try:
            self.dso.trigger[tr_mode].sweep = Sweep.single
            # The DS1052 sees a trigger signal and since the sweep mode is
            # "single", it goes into trigger mode "stop".
            self.trigger_status_durations(TriggerStatus.stop)
            # Prevent a "regular" trigger event by setting a useless trigger
            # level.
            self.dso.trigger[tr_mode].level = 4
            status_info = self.trigger_status_durations(
                TriggerStatus.triggered, timeout=0.5, fail_on_timeout=False)
            # Nothing happened so far.
            self.assertEqual(
                [TriggerStatus.stop], [item.status for item in status_info])
            # Try a force_trigger() call in stop mode.
            self.dso.trigger.force()
            status_info = self.trigger_status_durations(
                TriggerStatus.triggered, timeout=0.5, fail_on_timeout=False)
            # Nothing happened.
            self.assertEqual(
                [TriggerStatus.stop], [item.status for item in status_info])
            self.dso.run()
            # Still nothing happened.
            status_info = self.trigger_status_durations(
                TriggerStatus.triggered, timeout=0.5, fail_on_timeout=False)
            self.assertEqual(
                [TriggerStatus.stop, TriggerStatus.run, TriggerStatus.wait],
                [item.status for item in status_info])
            # Now we'll see a trigger evebt.
            self.dso.trigger.force()
            status_info = self.trigger_status_durations(
                TriggerStatus.stop, timeout=0.5, fail_on_timeout=True)
            # Note that we did _not_ see TriggerStatus.triggered.
            # Not sure why: Could be an oddity of the DS1052, or
            # record_trigger_statuses() missed that status due to its sleep()
            # call.
            self.assertEqual(
                [TriggerStatus.wait, TriggerStatus.stop],
                [item.status for item in status_info])
        finally:
            self.dso.trigger[tr_mode].sweep = Sweep.auto
            self.dso.trigger[tr_mode].level = current_trigger_level

    def test_wait_until_running__wait_until_stopped__sweep_mode_auto(self):
        self.dso.stop()
        wait_until = time() + 1
        while (
                self.dso.trigger.status != TriggerStatus.stop
                and time() < wait_until):
            sleep(0.1)
        self.assertEqual(TriggerStatus.stop, self.dso.trigger.status)

        current_sweep_mode = self.dso.trigger[self.dso.trigger.mode].sweep
        current_trigger_source = self.dso.trigger[self.dso.trigger.mode].source
        try:
            self.dso.trigger[self.dso.trigger.mode].sweep = Sweep.auto
            self.dso.wait_until_running()
            # It is risky to test for any specific trigger status:
            # TriggerStatus.run or TriggerStatus.auto is only visible for
            # a quite short time after a run() call; after that the status
            # tends to be TriggerStatus.wait or TriggerStatus.triggered.
            self.assertTrue(self.dso.trigger.status != TriggerStatus.stop)

            self.dso.wait_until_stopped()
            self.assertTrue(self.dso.trigger.status == TriggerStatus.stop)

        finally:
            self.dso.run()
            self.dso.trigger[self.dso.trigger.mode].source = (
                current_trigger_source)
            self.dso.trigger[self.dso.trigger.mode].sweep = current_sweep_mode
            # The next setUp() call checks the trigger status: Give the
            # DS1052 some time to finish the things to do after a :RUN
            # command. (Yeah, wait_until_running() does exactly what is
            # needed but I am not sure if it is a good idea to use the very
            # method tested here to ensure "recovery" from setup changes...)
            sleep(0.1)

    def test_wait_until_running__wait_until_stopped__sweep_mode_normal(self):
        self.dso.stop()
        wait_until = time() + 1
        while (
                self.dso.trigger.status != TriggerStatus.stop
                and time() < wait_until):
            sleep(0.1)
        self.assertEqual(TriggerStatus.stop, self.dso.trigger.status)

        current_sweep_mode = self.dso.trigger[self.dso.trigger.mode].sweep
        current_trigger_source = self.dso.trigger[self.dso.trigger.mode].source
        current_trigger_level = self.dso.trigger[self.dso.trigger.mode].level
        try:
            self.dso.trigger[self.dso.trigger.mode].sweep = Sweep.normal
            self.dso.wait_until_running()
            # It is risky to test for any specific trigger status:
            # TriggerStatus.run or TriggerStatus.auto is only visible for
            # a quite short time after a run() call; after that the status
            # tends to be TriggerStatus.wait or TriggerStatus.triggered.
            self.assertTrue(self.dso.trigger.status != TriggerStatus.stop)

            self.dso.wait_until_stopped()
            self.assertTrue(self.dso.trigger.status == TriggerStatus.stop)

            # Timeouts can occur: Set the trigger voltage to a value that is
            # too large for the probe adjustment signal.
            self.dso.trigger[self.dso.trigger.mode].level = 4
            # Waiting for TriggerStatus.triggered can't succeed.
            with self.assertRaises(DS1052TimeoutError) as ctx:
                self.dso.wait_until_running({TriggerStatus.triggered})
            self.assertEqual(
                'Timeout while waiting for one of the trigger states '
                'TriggerStatus.triggered. Last seen: TriggerStatus.run',
                str(ctx.exception))

            self.dso.wait_until_stopped()
            self.assertTrue(self.dso.trigger.status == TriggerStatus.stop)

        finally:
            self.dso.run()
            self.dso.trigger[self.dso.trigger.mode].level = (
                current_trigger_level)
            self.dso.trigger[self.dso.trigger.mode].source = (
                current_trigger_source)
            self.dso.trigger[self.dso.trigger.mode].sweep = current_sweep_mode
            sleep(0.1)


    def test_wait_until_running__wait_until_stopped__sweep_mode_single(self):
        self.dso.stop()
        wait_until = time() + 1
        while (
                self.dso.trigger.status != TriggerStatus.stop
                and time() < wait_until):
            sleep(0.1)
        self.assertEqual(TriggerStatus.stop, self.dso.trigger.status)

        current_sweep_mode = self.dso.trigger[self.dso.trigger.mode].sweep
        current_trigger_source = self.dso.trigger[self.dso.trigger.mode].source
        current_trigger_level = self.dso.trigger[self.dso.trigger.mode].level
        try:
            self.dso.trigger[self.dso.trigger.mode].sweep = Sweep.single
            # In Sweep.single it makes usually sense to wait until the
            # DS1052 is again in STOP mode.
            self.dso.wait_until_running({TriggerStatus.stop})
            # Yeah, a trivial "no-op" would have the same result...
            # But the call of wait_until_running() below, with a "bad"
            # trigger voltage, shows that at least something is happening.
            # A better check that the intended things happened would still
            # be nice. A monkey patch of DS1052.run() that calls the "real"
            # method while counting the calls would be an option.
            self.assertTrue(self.dso.trigger.status == TriggerStatus.stop)

            # Timeouts can occur: Set the trigger voltage to a value that is
            # too large for the probe adjustment signal.
            self.dso.trigger[self.dso.trigger.mode].level = 4
            with self.assertRaises(DS1052TimeoutError) as ctx:
                self.dso.wait_until_running({TriggerStatus.stop})
            self.assertEqual(
                'Timeout while waiting for one of the trigger states '
                'TriggerStatus.stop. Last seen: TriggerStatus.wait',
                str(ctx.exception))

            self.dso.wait_until_stopped()
            self.assertTrue(self.dso.trigger.status == TriggerStatus.stop)

        finally:
            self.dso.run()
            self.dso.trigger[self.dso.trigger.mode].level = (
                current_trigger_level)
            self.dso.trigger[self.dso.trigger.mode].source = (
                current_trigger_source)
            self.dso.trigger[self.dso.trigger.mode].sweep = current_sweep_mode
            sleep(0.1)

    def test_read_waveforms_raw_in_run_mode(self):
        # When the DS1052 is not in "stop" mode, the DS1052 returns
        # 600 data points. (OK, 512 data points for FFT data - but FFT is
        # deliberately not supported; See the doc string of
        # DS1052.read_waveforms_raw() for the reason.) The setting of
        # DS1052.memory_depth also does not matter.
        current_sweep_mode = self.dso.trigger[self.dso.trigger.mode].sweep
        current_memory_depth = self.dso.acquisition_memory_depth
        current_channels_enabled = [
            self.dso.channel[ch].enabled for ch in range(1, 3)]

        self.dso.trigger[self.dso.trigger.mode].sweep = Sweep.auto
        self.dso.wait_until_running()

        sources = (ChannelNumber.channel1, ChannelNumber.channel2)
        try:
            for mem_depth in AcquisitionMemoryDepth:
                self.dso.acquisition_memory_depth = mem_depth
                # Seems that a longer wait time is necessary between
                # setting the memory depth and a :WAV:DATA? query.
                # Otherwise the :WAV:DATA? times out...
                # Sigh...
                sleep(0.1)
                for points_mode in PointsMode:
                    for ch1_en, ch2_en in (
                            (True, True), (True, False), (False, True),
                            # Testing this (admittedly somewhat insane)
                            # condition needs a sleep() time of 1 second
                            # a few lines below...
                            # (False, False),
                            ):
                        self.dso.channel[1].enabled = ch1_en
                        self.dso.channel[2].enabled = ch2_en
                        # Enabling/disabling a channel needs more than 0.2s and
                        # at most 0.3s.
                        sleep(0.3)
                        (ch1, result1), (ch2, result2) = (
                            self.dso.read_waveforms_raw(sources, points_mode))
                        self.assertEqual(ch1, ChannelNumber.channel1)
                        self.assertEqual(ch2, ChannelNumber.channel2)
                        self.assertEqual(
                            600, len(result1),
                            f'Unexpected data len for CH1: {len(result1)}. '
                            f'mem_depth: {mem_depth} '
                            f'points_mode: {points_mode} ch1_en: {ch1_en} '
                            f'ch2_en: {ch2_en}')
                        self.assertEqual(
                            600, len(result2),
                            f'Unexpected data len for CH2: {len(result2)}. '
                            f'mem_depth: {mem_depth} '
                            f'points_mode: {points_mode} ch1_en: {ch1_en} '
                            f'ch2_en: {ch2_en}')
                        # It is very unlikely that identical data is acquired
                        # for both channels, so this should be a reliable check
                        # that the parameter "channel number" properly used.
                        self.assertNotEqual(
                            result1, result2,
                            f'Unexpected equality of CH1 and CH2 data. '
                            f'mem_depth: {mem_depth} '
                            f'points_mode: {points_mode} ch1_en: {ch1_en} '
                            f'ch2_en: {ch2_en}')
                        if not ch1_en:
                            self.assertEqual(
                                b'\x00' * 600, result1,
                                f'Unexpected non-zero data of CH1. '
                                f'mem_depth: {mem_depth} '
                                f'points_mode: {points_mode} ch1_en: {ch1_en} '
                                f'ch2_en: {ch2_en}')
                        if not ch2_en:
                            self.assertEqual(
                                b'\x00' * 600, result2,
                                f'Unexpected non-zero data of CH2. '
                                f'mem_depth: {mem_depth} '
                                f'points_mode: {points_mode} ch1_en: {ch1_en} '
                                f'ch2_en: {ch2_en}')
                        # XXX add a check if the values "look plausible" for
                        # a square wave signal. numpy.histogram() could perhaps
                        # be used.
        finally:
            self.dso.acquisition_memory_depth = current_memory_depth
            self.dso.trigger[self.dso.trigger.mode].sweep = current_sweep_mode
            self.dso.channel[1].enabled = current_channels_enabled[0]
            self.dso.channel[2].enabled = current_channels_enabled[1]


    def test_read_waveforms_raw_in_stop_mode(self):
        # When the DS1052 is in "stop" mode, the number of data points depends
        # on the settings of DS1052.acquisition_memory_depth and
        # DS1052. and DS1052.points_mode.
        sources = (ChannelNumber.channel1, ChannelNumber.channel2)

        current_sweep_mode = self.dso.trigger[self.dso.trigger.mode].sweep
        current_memory_depth = self.dso.acquisition_memory_depth
        current_channels_enabled = [
            self.dso.channel[ch].enabled for ch in range(1, 3)]

        self.dso.trigger[self.dso.trigger.mode].sweep = Sweep.single
        self.dso.wait_until_stopped()
        try:
            for mem_depth in (AcquisitionMemoryDepth.normal,
                              AcquisitionMemoryDepth.long):
                self.dso.acquisition_memory_depth = mem_depth
                for points_mode in PointsMode:
                    if (
                            mem_depth == AcquisitionMemoryDepth.long
                            and self.dso.sw_version == '00.04.04.00.00'
                            and points_mode != PointsMode.normal):
                        # The timeout of the assertRaises below takes
                        # 5 seconds and it occurs in points mode MAX
                        # as well as in RAW. It's enough to show that
                        # for one of the modes.
                        if points_mode != PointsMode.raw:
                            continue
                        # I hate this: Sometimes we get a timeout in
                        # wait_until_running(), sometimes we get the timeout
                        # in read_waveforms_raw(). The DS1052 can be extremely
                        # unpredictable.
                        with self.assertRaises(DS1052TimeoutError) as ctx:
                            self.dso.wait_until_running({TriggerStatus.stop})
                            self.dso.read_waveforms_raw(
                                ChannelNumber.channel1, points_mode)
                        self.assertEqual(
                            "Timeout waiting for a response to "
                            "b':WAV:DATA? CHANNEL1'.",
                            str(ctx.exception))
                        continue

                    for ch1_en, ch2_en in (
                            (True, True), (True, False), (False, True)):
                        self.dso.channel[1].enabled = ch1_en
                        self.dso.channel[2].enabled = ch2_en
                        self.dso.wait_until_running(
                            {TriggerStatus.stop}, timeout=5)
                        result1, result2 = self.dso.read_waveforms_raw(
                            sources, points_mode)
                        if points_mode == PointsMode.normal:
                            expected_data_len = 600
                        else:
                            if mem_depth == AcquisitionMemoryDepth.normal:
                                expected_data_len = 8192
                            else:
                                expected_data_len = 512 * 1024
                            if not ch1_en or not ch2_en:
                                expected_data_len *= 2
                        (ch1, result1), (ch2, result2) = (
                            self.dso.read_waveforms_raw(sources, points_mode))
                        self.assertEqual(ChannelNumber.channel1, ch1)
                        self.assertEqual(ChannelNumber.channel2, ch2)
                        self.assertEqual(
                            expected_data_len, len(result1),
                            f'Unexpected data len for CH1: {len(result1)}. '
                            f'mem_depth: {mem_depth} '
                            f'points_mode: {points_mode} ch1_en: {ch1_en} '
                            f'ch2_en: {ch2_en}')
                        self.assertEqual(expected_data_len, len(result2),
                            f'Unexpected data len for CH2: {len(result2)}. '
                            f'mem_depth: {mem_depth} '
                            f'points_mode: {points_mode} ch1_en: {ch1_en} '
                            f'ch2_en: {ch2_en}')
                        # It is very unlikely that identical data is acquired
                        # for both channels, so this should be a reliable check
                        # that the parameter "channel number" properly used.
                        if ch1_en or ch2_en:
                            self.assertNotEqual(result1, result2,
                            f'Unexpected equality of CH1 and CH2 data. '
                            f'mem_depth: {mem_depth} '
                            f'points_mode: {points_mode} ch1_en: {ch1_en} '
                            f'ch2_en: {ch2_en}')
                        # In "STOP" mode, some junk data is returned for a
                        # disabled channel.
                        #if not ch1_en:
                        #    self.assertEqual(
                        #        b'\x00' * expected_data_len, result1,
                        #        f'Unexpected non-zero data of CH1. '
                        #        f'mem_depth: {mem_depth} '
                        #        f'points_mode: {points_mode} ch1_en: {ch1_en} '
                        #        f'ch2_en: {ch2_en}')
                        #if not ch2_en:
                        #    self.assertEqual(
                        #        b'\x00' * expected_data_len, result2,
                        #        f'Unexpected non-zero data of CH2. '
                        #        f'mem_depth: {mem_depth} '
                        #        f'points_mode: {points_mode} ch1_en: {ch1_en} '
                        #        f'ch2_en: {ch2_en}')

                        # XXX add a check if the values "look plausible" for
                        # a square wave signal. numpy.histogram() could perhaps
                        # be used.
        finally:
            self.dso.acquisition_memory_depth = current_memory_depth
            self.dso.trigger[self.dso.trigger.mode].sweep = current_sweep_mode
            self.dso.channel[1].enabled = current_channels_enabled[0]
            self.dso.channel[2].enabled = current_channels_enabled[1]

    def test_read_waveforms(self):
        # A short test should suffice here as DS1052.read_waveforms()
        # mostly collects raw waveforms and timebase related data and
        # builds Waveform instances from this data.
        result = self.dso.read_waveforms((1, 2), PointsMode.normal)
        for ch, waveform in zip(
                (ChannelNumber.channel1, ChannelNumber.channel2), result):
            self.assertEqual(self.dso.timebase_scale, waveform.tb_scale)
            self.assertEqual(self.dso.timebase_offset, waveform.tb_offset)
            self.assertEqual(self.dso.channel[ch].scale, waveform.v_scale)
            self.assertEqual(self.dso.channel[ch].offset, waveform.v_offset)
            self.assertEqual(
                self.dso.channel[ch].acquisition_sampling_rate,
                waveform.sample_rate)
            self.assertEqual(ch, waveform.channel_no)


class WaveformTest(DS1052TestsWithTestSignalBase, TestCase):
    def get_waveform(self, ch, points_mode):
        ch, raw_data = self.dso.read_waveforms_raw(ch, points_mode)[0]
        return Waveform(
            raw_waveform=raw_data,
            channel_no=ch,
            tb_scale=self.dso.timebase_scale,
            tb_offset=self.dso.timebase_offset,
            v_scale=self.dso.channel[ch].scale,
            v_offset=self.dso.channel[ch].offset,
            sample_rate=self.dso.channel[ch].acquisition_sampling_rate)

    def test_waveform_voltage__points_mode_normal(self):
        waveform = self.get_waveform(1, PointsMode.normal)
        values = waveform.v
        self.assertEqual((600, ), values.shape)

        # As usual, we expect data for the probe adjustment signal, a 1 kHz
        # square wave with level 0V and 3V. A histogram of the data should
        # thus show most data points "around" 0 and 3. A histogram with
        # 11 bins, for values ranging from -0.15 to 3.15, allows for enough
        # tolerance that even a badly calibrated device should pass the
        # assertions below.
        bins = np.linspace(-0.15, 3.15, 12, endpoint=True)
        hist, _ = np.histogram(values, bins)
        # Nearly half of the data points values should be in the first and
        # last bin, respectively. Allow for some values in between
        # since the DS1052 is well able to capture the voltage when the
        # signal is rising or falling.
        self.assertTrue(270 <= hist[0] <= 300)
        self.assertTrue(270 <= hist[10] <= 300)

    def test_waveform_voltage__points_mode_raw(self):
        current_sweep_mode = self.dso.trigger[self.dso.trigger.mode].sweep
        current_memory_depth = self.dso.acquisition_memory_depth

        try:
            self.dso.trigger[self.dso.trigger.mode].sweep = Sweep.single
            self.dso.wait_until_stopped()
            self.dso.acquisition_memory_depth = AcquisitionMemoryDepth.normal
            self.dso.wait_until_running({TriggerStatus.stop})

            waveform = self.get_waveform(1, PointsMode.raw)
            values = waveform.v
            self.assertEqual((8192, ), values.shape)
            bins = np.linspace(-0.15, 3.15, 12, endpoint=True)
            hist, _ = np.histogram(values, bins)
            # The typical sum of counts in the histogram in bins 1..9 is
            # around 70, hence the "assertion threshold" could be more narrow.
            # But again: Allow for some oddities in the setup.
            # A more thorough test should anyway check that data "matches"
            # a square wave signal and not some random distribution of the
            # values along the time axis.
            self.assertTrue(3600 <= hist[0] <= 4096)
            self.assertTrue(3600 <= hist[10] <= 4096)
        finally:
            self.dso.trigger[self.dso.trigger.mode].sweep = current_sweep_mode
            self.dso.acquisition_memory_depth = current_memory_depth
            self.dso.run()
            sleep(0.1)

    def test_waveform_time__points_mode_normal(self):
        waveform = self.get_waveform(1, PointsMode.normal)
        values = waveform.t
        self.assertEqual((600, ), values.shape)

        # The auto() call in setUpClass() has set the timebase parameters
        self.assertEqual(500e-6, self.dso.timebase_scale)
        self.assertEqual(0, self.dso.timebase_offset)
        # The data returned by the DS1052 for Points.noraml are the values
        # that are also shown on the internal display, which has 12
        #"divisions" on the time axis. With a timebase scale of
        # 500 microseconds/dev and a time offset 0 (i.e., the "trigger
        # time" is in the center), the first value of the time points
        # is -500µs * 6 -> -3 ms; the last value is
        # +500µs * 6 - time_step_size, where time_step_size is
        # the full "duration" of the data (6ms) divided by the number of
        # data points (600), or 10µs.
        self.assertEqual(-3e-3, values[0])
        # There may be a small rounding error or whatever: I assume that
        # np.linspace() (used to generate the time values) simply adds the
        # step size 599 times, which is of course less accurate than
        # taking the upper limit and subtracting one setp size.
        self.assertAlmostEqual(3e-3 - 10e-6, values[-1])
        # Similar rounding error even here:
        # -3e-3 + 10e-6 + 3e-3 -> 1.0000000000000026e-05
        self.assertAlmostEqual(10e-6, values[1] - values[0])

    def test_waveform_time__points_mode_raw(self):
        current_sweep_mode = self.dso.trigger[self.dso.trigger.mode].sweep
        current_memory_depth = self.dso.acquisition_memory_depth

        try:
            self.dso.trigger[self.dso.trigger.mode].sweep = Sweep.single
            self.dso.wait_until_stopped()
            self.dso.acquisition_memory_depth = AcquisitionMemoryDepth.normal
            self.dso.wait_until_running({TriggerStatus.stop})

            waveform = self.get_waveform(1, PointsMode.raw)
            values = waveform.t
            self.assertEqual((8192, ), values.shape)
            # t=0 is at index 4095 if the timebase offset is zero.
            # See test_timebase_zero_point() for details.
            self.assertEqual(0, self.dso.timebase_offset)
            self.assertAlmostEqual(0, values[4095])
            # The "time step" is the inverse of the sampling rate.
            self.assertAlmostEqual(
                1/self.dso.channel[1].acquisition_sampling_rate,
                values[1] - values[0])
            start_value = (
                -4095/self.dso.channel[1].acquisition_sampling_rate)
            self.assertEqual(start_value, values[0])
            last_value = (
                start_value
                + 8191 / self.dso.channel[1].acquisition_sampling_rate)
            self.assertAlmostEqual(last_value, values[-1])
        finally:
            self.dso.trigger[self.dso.trigger.mode].sweep = current_sweep_mode
            self.dso.acquisition_memory_depth = current_memory_depth
            self.dso.run()
            sleep(0.1)

    def find_positive_trigger_point_transitions(self, waveform, trigger_level):
        # Find the index in the numpy array v where the value "crosses"
        # from a value <= trigger_level to a value > trigger_level.

        # "Binarize" the data: We don't need the exact waveform; all we
        # want to know is where positive transitions occur.
        bin = np.where(waveform.v > trigger_level, 1, 0)
        # The discrete difference should be 1 at exactly one index,
        # the trigger time. Of course this assumes that the signal
        # not too noisy.
        diff = np.diff(bin)
        return np.where(diff > 0)[0], bin, diff

    def find_timebase_trigger_points(
            self, timebase_scale, timebase_offset, trigger_level,
            expected_trigger_indexes, expected_index_error, ch1_enabled,
            ch2_enabled):
        current_sweep_mode = self.dso.trigger[self.dso.trigger.mode].sweep
        current_memory_depth = self.dso.acquisition_memory_depth
        current_tb_scale = self.dso.timebase_scale
        current_tb_offset = self.dso.timebase_offset
        current_trigger_level = self.dso.trigger[self.dso.trigger.mode].level
        current_ch1_enabled = self.dso.channel[1].enabled
        current_ch2_enabled = self.dso.channel[2].enabled

        try:
            self.dso.channel[1].enabled = ch1_enabled
            self.dso.channel[2].enabled = ch2_enabled
            self.dso.trigger[self.dso.trigger.mode].sweep = Sweep.single
            self.dso.acquisition_memory_depth = AcquisitionMemoryDepth.normal
            self.dso.timebase_scale = timebase_scale
            self.dso.timebase_offset = timebase_offset
            self.dso.trigger[self.dso.trigger.mode].level = trigger_level

            transition_indexes = set()
            self.dso.wait_until_stopped()
            for count in range(10):
                self.dso.wait_until_running({TriggerStatus.stop})
                waveform = self.get_waveform(1, PointsMode.raw)

                transitions, bin, diff = (
                    self.find_positive_trigger_point_transitions(
                        waveform,
                        self.dso.trigger[self.dso.trigger.mode].level))
                print(transitions)
                # check if the signal level changes are at the expected
                # positions.
                for index in transitions:
                    for expected in expected_trigger_indexes:
                        if (
                                expected - expected_index_error
                                <= index
                                <= expected + expected_index_error):
                            break
                    else:
                        #import matplotlib.pyplot as plt
                        #plt.plot(bin)
                        #plt.plot(waveform.v)
                        #plt.plot(diff)
                        #plt.show()
                        self.fail(
                            f'Positive edge index {index} seen but is not '
                            f'near the expected indexes '
                            f'{expected_trigger_indexes}\n'
                            f'(time base: {timebase_scale}, offset: '
                            f'{timebase_offset})')
        finally:
            self.dso.channel[1].enabled = current_ch1_enabled
            self.dso.channel[2].enabled = current_ch2_enabled
            self.dso.trigger[self.dso.trigger.mode].level = (
                current_trigger_level)
            self.dso.timebase_scale = current_tb_scale
            self.dso.timebase_offset = current_tb_offset
            self.dso.trigger[self.dso.trigger.mode].sweep = current_sweep_mode
            self.dso.acquisition_memory_depth = current_memory_depth
            self.dso.run()
            sleep(0.1)

    def test_timebase_zero_point(self):
        # This test is a bit tricky to get right, at least with the 1 kHz
        # probe adjustment signal... The trigger time is usually defined
        # (for the "edge" mode) as the time at which the signal crosses
        # the trigger level. This means for the display of a DSO:
        # When the time offset is zero, the waveform of the trigger channel
        # should cross the horizontal center of the screen at the trigger
        # voltage level.
        #
        # The DS1052 seems to have some additional "lag" that depends on the
        # gradient of the signal. This is easy to see for the 1 kHz "square
        # wave" signal that, when displayed at timebase scales like 1µs/div
        # or 5µs/div, does not look "square like" at all: A "positive edge"
        # starts with a gradient of 1.6V/µs but in the voltage range
        # between 1V and 2V the gradient is already down to around 1V/µs.
        #
        # When the trigger level is changed, the DS1052 shows an orange
        # horizontal line for its current setting, and it could be
        # expected that this trigger level line, the curve of the trigger
        # signal and the vertical grid line in the center of the display
        # all cross at the same point on the screen. Unfortunately this is
        # not the case: With increasing trigger voltage, the point in time
        # where the signal crosses the trigger voltage moves to the left
        # on the display.
        #
        # Even worse: This time offset depends also on the vertical scale
        # of the trigger channel...
        #
        # The goal of this test is to ensure that the assumptions made
        # in Waveform._t_linspace() to calculate the timebase values for
        # PointsMode.raw/PointsMode.max are at least half way correct.
        # Where "correct" means that the calculation in
        # Waveform._t_linspace() matches what is seen on the display.
        #
        # The first idea to acquire the rising edge of the 1kHz signal
        # with a sampling rate of 50M/s (5e-6s/div), 25M/s (10e-6s/div)
        # perhaps even 100M/s, and to check at which index in waveform.v
        # the signal rises to levels above the trigger level does not
        # work out well since the gradient of the signal, measured as
        # "change between samples", is relatively low at these sampling
        # rates and the weird behaviour described above kicks in.
        #
        # Alternative approach: Acquire data with these timebase setting:
        #
        # time base     sampling        Number of positive/negative
        # (s/div)       rate            edges in 8k data
        # 20e-6         10M/s           1 pos
        # 50e-6         5M/s            1 pos, 2 neg
        # 100e-6        2.5M/s          4 pos, 4 neg
        # 200e-6        1M/s            9 pos, 8 neg
        #
        # So we will get more than one positive crossing of the trigger
        # level in two of these cases. But it is sure that one of these
        # crossing is visible near index 4096; the most interesting question
        # is if there is some small constant offset from the expected value
        # 4095 or 4096 that could for example explain the constant 10 in the
        # last formula in this recommendation from Rigol how to calculate the
        # timebase data:
        # https://rigol.force.com/support/s/article/DS1000E-Waveform-Data-Formatting-Guide

        # Conclusion from this test:
        # 1. With the relatively slow signal (1kHz is not much for a DSO
        #    that can acquire up to 500MSamples per second) there is no
        #    visible offset of the "trigger index" in the waveform data:
        #    It is 4095, except for the strange shift to the left described
        #    above. But that shift does not change what the DS1052 tells
        #    on its own display about the trigger time.
        # 2. A possible constant offset of the "trigger index" from 4095
        #    that might exist for higher sample rates (cf. the constant
        #    value 10 in Rigol's recommendation how to calculate time values)
        #    cannot be seen with this used test setup: It requires a test
        #    signal with much shorter rise/fall times than the probe
        #    adjustment signal. Postponed for now.
        # 3. A positive time base offset moves the "trigger index" to lower
        #    values; a negative TB offset moves the "tirgger index" to higher
        #    values.

        # 5 MSamples/s: 1.6384ms recording time. Enough for one positive edge
        # and two negative edges. (The latter are not checked.)
        self.find_timebase_trigger_points(
            timebase_scale=50e-6, timebase_offset=0, trigger_level=0.24,
            expected_trigger_indexes=[4094], expected_index_error=2,
            ch1_enabled=True, ch2_enabled=True)

        # 2.5 MSamples/s: 3.2768ms recording time. Enough for three positive
        # edges; expected distance is 1ms or 1e3*2.5e6 -> 2500 "indexes"
        self.find_timebase_trigger_points(
            timebase_scale=100e-6, timebase_offset=0, trigger_level=0.24,
            expected_trigger_indexes=[4095-2500, 4095, 4095+2500],
            expected_index_error=2, ch1_enabled=True, ch2_enabled=True)
        # 1 MSamples/s: 8.192ms recording time -> 9 positive edge.
        # Distance: 1000 "indexes".
        self.find_timebase_trigger_points(
            timebase_scale=200e-6, timebase_offset=0, trigger_level=0.24,
            expected_trigger_indexes=[
                95, 1095, 2095, 3095, 4095, 5095, 6095, 7095, 8095],
            expected_index_error=2, ch1_enabled=True, ch2_enabled=True)

        # With a higher trigger level, the signal is shifted to the left
        # at higher sampling rates.
        self.find_timebase_trigger_points(
            timebase_scale=20e-6, timebase_offset=0, trigger_level=2.5,
            expected_trigger_indexes=[4080], expected_index_error=5,
            ch1_enabled=True, ch2_enabled=True)

        # 5 MSamples/s: 1.6384ms recording time. Enough for one positive edge
        # and two negative edges. (The latter are not checked.)
        self.find_timebase_trigger_points(
            timebase_scale=50e-6, timebase_offset=0, trigger_level=2.5,
            expected_trigger_indexes=[4088], expected_index_error=3,
            ch1_enabled=True, ch2_enabled=True)

        # Non-zero timebase offsets.
        # 5 Msamples/s -> recording time 1.6384ms.
        # TB offset 0.2ms means an "index shift" of 1000.
        # Due to the offset, we have antoher positive slope on the right end.
        # Distance from the first is 1ms -> 5000 samples.
        self.find_timebase_trigger_points(
            timebase_scale=50e-6, timebase_offset=0.2e-3, trigger_level=0.24,
            expected_trigger_indexes=[4093-1000, 4093+4000],
            expected_index_error=2, ch1_enabled=True, ch2_enabled=True)
        # With the sign of the TB offset flipped, the "trigger index" moves
        # to the right. (Use a smaller avsolute value here to prevent another
        # another positive edge right at the start.)
        self.find_timebase_trigger_points(
            timebase_scale=50e-6, timebase_offset=-0.1e-3, trigger_level=0.24,
            expected_trigger_indexes=[4093+500],
            expected_index_error=2, ch1_enabled=True, ch2_enabled=True)

        # And final tests with only one channel enabled. Now we have 16384
        # data points.
        # 5 MSamples/s: 3.2678ms recording time. Enough for three positive
        # edges.
        self.find_timebase_trigger_points(
            timebase_scale=50e-6, timebase_offset=0, trigger_level=0.24,
            expected_trigger_indexes=[3190, 8190, 13190],
            expected_index_error=2, ch1_enabled=True, ch2_enabled=False)
        # 2.5 MSamples/s: 6.6636ms recording time. Enough for six positive
        # edges.
        self.find_timebase_trigger_points(
            timebase_scale=100e-6, timebase_offset=0, trigger_level=0.24,
            expected_trigger_indexes=[
                8191-7500, 8191-5000, 8191-2500, 8191, 8191+2500, 8191+5000,
                8191+7500],
            expected_index_error=2, ch1_enabled=True, ch2_enabled=False)

    t_linspace_test_data_600_datapoints = (
        dict(
            tb_scale=2e-9,
            tb_offset=0,
            expected_t0_index=300,
            expected_t_min=-12e-9,
            expected_t_max=12e-9 - 2e-9/50,
            expected_step_size=2e-9/50,
            # Adjustment of the accuracy of the assertAlmostEqual() calls:
            # Default is 7 decimal places, subtract from that values the
            # exponent of the time base scale: That's the order of the
            # values to be dealt with.
            places=16),
        dict(
            tb_scale=2e-9,
            tb_offset=2e-9,
            expected_t0_index=250,
            expected_t_min=-10e-9,
            expected_t_max=14e-9 - 2e-9/50,
            expected_step_size=2e-9/50,
            places=16),
        dict(
            tb_scale=2e-9,
            tb_offset=-4e-9,
            expected_t0_index=400,
            expected_t_min=-16e-9,
            expected_t_max=8e-9 - 2e-9/50,
            expected_step_size=2e-9/50,
            places=16),
        dict(
            tb_scale=5e-9,
            tb_offset=0,
            expected_t0_index=300,
            expected_t_min=-30e-9,
            expected_t_max=30e-9 - 5e-9/50,
            expected_step_size=5e-9/50,
            places=16),
        dict(
            tb_scale=5e-9,
            tb_offset=10e-9,
            expected_t0_index=200,
            expected_t_min=-20e-9,
            expected_t_max=40e-9 - 5e-9/50,
            expected_step_size=5e-9/50,
            places=16),
        dict(
            tb_scale=5e-9,
            tb_offset=-20e-9,
            expected_t0_index=500,
            expected_t_min=-50e-9,
            expected_t_max=10e-9 - 5e-9/50,
            expected_step_size=5e-9/50,
            places=16),
        dict(
            tb_scale=200e-6,
            tb_offset=0,
            expected_t0_index=300,
            expected_t_min=-1200e-6,
            expected_t_max=1200e-6 - 200e-6/50,
            expected_step_size=200e-6/50,
            places=13),
        dict(
            tb_scale=200e-6,
            tb_offset=100e-6,
            expected_t0_index=275,
            expected_t_min=-1100e-6,
            expected_t_max=1300e-6 - 200e-6/50,
            expected_step_size=200e-6/50,
            places=13),
        dict(
            tb_scale=200e-6,
            tb_offset=-300e-6,
            expected_t0_index=375,
            expected_t_min=-1500e-6,
            expected_t_max=900e-6 - 200e-6/50,
            expected_step_size=200e-6/50,
            places=13),
        dict(
            tb_scale=50e-3,
            tb_offset=0,
            expected_t0_index=300,
            expected_t_min=-300e-3,
            expected_t_max=300e-3 - 50e-3/50,
            expected_step_size=50e-3/50,
            places=10),
        )
    def test_t_linspace_600_datapoints(self):
        for test_params in self.t_linspace_test_data_600_datapoints:
            test_params = test_params.copy()
            expected_t0_index = test_params.pop('expected_t0_index')
            expected_t_min = test_params.pop('expected_t_min')
            expected_t_max = test_params.pop('expected_t_max')
            expected_step_size = test_params.pop('expected_step_size')
            places = test_params.pop('places')
            raw_waveform = np.empty((600, ))

            waveform = Waveform(
                raw_waveform, channel_no=None, v_scale=None, v_offset=None,
                sample_rate=None, **test_params)
            tb_data, step_size = waveform._t_linspace(retstep=True)
            self.assertAlmostEqual(
                expected_step_size, step_size, places=places,
                msg=f'tb_scale: {test_params["tb_scale"]} '
                    f'tb_offset: {test_params["tb_offset"]}')
            self.assertAlmostEqual(expected_t_min, tb_data[0], places=places,
                msg=f'tb_scale: {test_params["tb_scale"]} '
                    f'tb_offset: {test_params["tb_offset"]}')
            # Position of t=0
            self.assertAlmostEqual(0, tb_data[expected_t0_index], places=places,
                msg=f'tb_scale: {test_params["tb_scale"]} '
                    f'tb_offset: {test_params["tb_offset"]}')
            self.assertAlmostEqual(expected_t_max, tb_data[-1], places=places,
                msg=f'tb_scale: {test_params["tb_scale"]} '
                    f'tb_offset: {test_params["tb_offset"]}')

    t_linspace_test_data_8192_16384_datapoints = (
        # 1 GSample/s is used when only one channel is enabled for time base
        # scales <= 50ns/div.
        dict(
            sample_rate=1e9,
            tb_offset=0,
            expected_t0_index=8191,
            expected_t_min=-8191e-9,
            expected_t_max=8192e-9,
            expected_step_size=1e-9,
            n_points=16384,
            places=16),
        dict(
            sample_rate=1e9,
            tb_offset=20e-9,
            expected_t0_index=4075,
            expected_t_min=-4075e-9,
            expected_t_max=4116e-9,
            expected_step_size=1e-9,
            n_points=8192,
            places=16),
        dict(
            sample_rate=1e9,
            tb_offset=-50e-9,
            expected_t0_index=4145,
            expected_t_min=-4145e-9,
            expected_t_max=4046e-9,
            expected_step_size=1e-9,
            n_points=8192,
            places=16),
        # 500MSamples/s is used with two channels enabled for timebase
        # scales <= 100ns/div.
        dict(
            sample_rate=500e6,
            tb_offset=0,
            expected_t0_index=4095,
            expected_t_min=-4095 * 2e-9,
            expected_t_max=4096 * 2e-9,
            expected_step_size=2e-9,
            n_points=8192,
            places=16),
        dict(
            sample_rate=500e6,
            tb_offset=10e-9,
            expected_t0_index=4090,
            expected_t_min=-4095 * 2e-9 + 10e-9,
            expected_t_max=4096 * 2e-9 + 10e-9,
            expected_step_size=2e-9,
            n_points=8192,
            places=16),
        dict(
            sample_rate=500e6,
            tb_offset=-20e-9,
            expected_t0_index=4105,
            expected_t_min=-4095 * 2e-9 - 20e-9,
            expected_t_max=4096 * 2e-9 - 20e-9,
            expected_step_size=2e-9,
            n_points=8192,
            places=16),
        dict(
            sample_rate=10e3,
            tb_offset=0,
            expected_t0_index=4095,
            expected_t_min=-4095 * 0.1e-3,
            expected_t_max=4096 * 0.1e-3,
            expected_step_size=0.1e-3,
            n_points=8192,
            places=10),
        )

    def test_t_linspace_8192_16384_datapoints(self):
        for test_params in self.t_linspace_test_data_8192_16384_datapoints:
            test_params = test_params.copy()
            expected_t0_index = test_params.pop('expected_t0_index')
            expected_t_min = test_params.pop('expected_t_min')
            expected_t_max = test_params.pop('expected_t_max')
            expected_step_size = test_params.pop('expected_step_size')
            places = test_params.pop('places')
            n_points = test_params.pop('n_points')
            raw_waveform = np.empty((n_points, ))

            # For 8192, 16384, 512*1024 and 1024*1024 datapoints, the
            # timebase data depends only the sample rate and the timebase
            # offset but not directly on the timebase scale. (The timebase
            # scale determines the sample rate though.)
            waveform = Waveform(
                raw_waveform, channel_no=None, tb_scale=None, v_scale=None,
                v_offset=None, **test_params)
            tb_data, step_size = waveform._t_linspace(retstep=True)
            self.assertAlmostEqual(
                expected_step_size, step_size, places=places,
                msg=f'sample_rate: {test_params["sample_rate"]} '
                    f'tb_offset: {test_params["tb_offset"]}')
            self.assertAlmostEqual(expected_t_min, tb_data[0], places=places,
                msg=f'sample_rate: {test_params["sample_rate"]} '
                    f'tb_offset: {test_params["tb_offset"]}')
            # Position of t=0
            self.assertAlmostEqual(0, tb_data[expected_t0_index], places=places,
                msg=f'sample_rate: {test_params["sample_rate"]} '
                    f'tb_offset: {test_params["tb_offset"]}')
            self.assertAlmostEqual(expected_t_max, tb_data[-1], places=places,
                msg=f'sample_rate: {test_params["sample_rate"]} '
                    f'tb_offset: {test_params["tb_offset"]}')
