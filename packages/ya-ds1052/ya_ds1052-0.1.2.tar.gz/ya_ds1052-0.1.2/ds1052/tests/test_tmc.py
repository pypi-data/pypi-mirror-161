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

from functools import partial
import logging
from logging.handlers import BufferingHandler
import os
import re
import sys
from time import sleep
from unittest import skipIf, SkipTest, skipUnless, TestCase
from unittest.mock import patch

from .. import tmc


class InstrumentTestBase:
    def setUp(self):
        self.log_handler = BufferingHandler(100)
        self.log_handler.setLevel(logging.DEBUG)
        tmc.tmc_logger.addHandler(self.log_handler)
        tmc.tmc_logger.setLevel(logging.DEBUG)
        self.tmc_logger_propagate = tmc.tmc_logger.propagate
        tmc.tmc_logger.propagate = False
        self.instr = self.class_tested()

    def tearDown(self):
        self.instr.close()
        tmc.tmc_logger.removeHandler(self.log_handler)
        tmc.tmc_logger.propagate = self.tmc_logger_propagate

    def test_init(self):
        # No parameter is required.
        ident = self.instr.ask('*IDN?')
        _, _, serial, _ = ident.split(',')
        self.instr.close()

        # The serial number can be specified.
        self.instr = self.class_tested(serial=serial)
        self.instr.close()

        # The serial number can be specified with and without a trailing null.
        # Sounds perhaps silly but python-usbtmc expects a trailing null, as
        # it uses the device's serial number as returned by a plain
        # usb.core.Device instance for comparisions, and that value ends with
        # a null byte... Similiarly, pyvisa-py returns the serial number with
        # a trailing null.
        # Hence user applications could have reasons to specify the
        # serial number with and without a trailing null...)
        self.instr = self.class_tested(serial=serial + '\x00')
        self.instr.close()

        # If the specified serial nuber does not match that of any
        # connected device, an exception is returned.
        with self.assertRaises(tmc.DS1052InitError) as ctx:
            self.class_tested(serial='nonsense')
        self.assertEqual('Device not found.', str(ctx.exception))

    def test_close(self):
        # Record in the mock that the base class's close() method was called
        # and let the mock call that method as a "side effect".
        with self.close_patch as mock:
            self.instr.close()
        mock.assert_called()
        # close() can be called more than once.
        self.instr.close()

    def test_write_raw_logging(self):
        self.instr.write_raw(b':key:force')
        self.assertEqual(1, len(self.log_handler.buffer))
        self.assertEqual(">>> b':key:force'", self.log_handler.buffer[0].msg)

    def test_write_logging(self):
        self.instr.write(':key:force')
        self.assertEqual(1, len(self.log_handler.buffer))
        self.assertIn(
            self.log_handler.buffer[0].msg,
            (">>> ':key:force'", ">>> b':key:force'", ))

    def test_ask_raw_logging(self):
        self.instr.ask_raw(b'*idn?', 256)
        self.assertEqual(2, len(self.log_handler.buffer))
        self.assertEqual(">>> b'*idn?'", self.log_handler.buffer[0].msg)
        self.assertTrue(
            self.log_handler.buffer[1].msg.startswith(
                "<<< b'Rigol Technologies"))

    def test_ask_logging(self):
        self.instr.ask('*idn?')
        self.assertEqual(2, len(self.log_handler.buffer))
        self.assertIn(
            self.log_handler.buffer[0].msg, (">>> '*idn?'", ">>> b'*idn?'", ))
        self.assertTrue(
            self.log_handler.buffer[1].msg.startswith(
                "<<< 'Rigol Technologies")
            or self.log_handler.buffer[1].msg.startswith(
                "<<< b'Rigol Technologies")
,
            f'Unexpected log entry: {self.log_handler.buffer[1].msg}')

    def test_timeout_error(self):
        with self.assertRaises(tmc.DS1052TimeoutError) as ctx:
            # "*OPC?" is unfortuantely not implemented by the DS1052, so
            # it can be used to force a time out error while waiting for
            # a response. A failure of this test because some future
            # firmware version will indeed implement "*OPC?" would be a good
            # reason to open a bottle of champagne...

            # Make the test a bit faster.
            self.instr.timeout = 0.5
            self.instr.ask('*OPC?')
        self.assertIn(
            str(ctx.exception),
            ("Timeout waiting for a response to '*OPC?'.",
             "Timeout waiting for a response to b'*OPC?'."))
        self.assertEqual(
            self.timeout_implementation_error,
            ctx.exception.original_exc.__class__.__name__)
        # There are two log entries
        self.assertEqual(2, len(self.log_handler.buffer))
        # The first entry is from the debug logging
        self.assertIn(
            self.log_handler.buffer[0].msg, (">>> '*OPC?'", ">>> b'*OPC?'", ))
        # The second entry is from the "black box log" that is shown when
        # an exception is raised.
        self.assertIsNot(
            None,
            re.search(
                r"^cmdlog: \d\.\d+ b?'\*OPC\?' None",
                self.log_handler.buffer[1].msg))


@skipIf(tmc.usbtmc is None, 'python-usbtmc is not installed.')
class TestPyUsbTmcInstrument(InstrumentTestBase, TestCase):
    class_tested = tmc.PyUsbTmcInstrument
    timeout_implementation_error = 'USBTimeoutError'

    def setUp(self):
        super().setUp()
        self.close_patch = patch.object(
            tmc.usbtmc.Instrument, 'close',
            side_effect=partial(tmc.usbtmc.Instrument.close, self.instr))


if sys.platform == 'linux':
    # Check if the usbtmc kernel module is loaded: Only if this is the case
    # it makes sense to try to run TestLkUsbTmcInstrument.
    import subprocess

    lkusbtmc_skip_msg = 'Test requires that the kernel module usbtmc is loaded.'
    lkusbtmc_testable = False
    for line in subprocess.run(
            'lsmod', capture_output=True).stdout.split(b'\n'):
        if line.startswith(b'usbtmc'):
            lkusbtmc_testable = True
            break
else:
    lkusbtmc_skip_msg = 'Test can only be run under Linux.'
    lkusbtmc_testable = False


@skipUnless(lkusbtmc_testable, lkusbtmc_skip_msg)
class TestLkUsbTmcInstrument(InstrumentTestBase, TestCase):
    class_tested = tmc.LkUsbTmcInstrument
    timeout_implementation_error = 'TimeoutError'
    close_patch = patch.object(os, 'close', side_effect=os.close)

    @classmethod
    def setUpClass(cls):
        # Tests in this file run after tests in test_ds1052.py; tests in the
        # latter file open an Instrument class. This can lead to a problem:
        # If test_ds1052.py uses PyUsbTmcInstrument, opening the
        # "/dev/usbtmcN" file raises a PermissionError for a short time.
        # No clue why - perhaps the "core USB" device file used by
        # PyUsbTmcInstrument is not yet completely closed (or some kernel
        # resources are not yet released. Anyway, it helps in this case to
        # wait a short time.
        for count in range(10):
            try:
                device = cls.class_tested()
                device.close()
                return
            except PermissionError as exc:
                sleep(0.1)
            except tmc.DS1052InitError as exc:
                raise SkipTest(
                    'TestLkUsbTmcInstrument cannit be run:\n'
                    'No appropriate /dev/usbtmc* device files found.\n'
                    'Possible reason: A VISA library disabled the kernel\n'
                    'device files. Disconnect/reconnect the DS1052 to run\n'
                    'this test.\n')
        raise exc


@skipIf(tmc.pyvisa is None, 'pyvisa is not installed.')
class TestPyVisaInstrument1PyVisaPy(InstrumentTestBase, TestCase):
    resource_manager = tmc.pyvisa.ResourceManager('@py')
    class_tested = partial(
        tmc.PyVisaInstrument, resource_manager=resource_manager)
    timeout_implementation_error = 'VisaIOError'

    def setUp(self):
        super().setUp()
        self.close_patch = patch.object(
            self.instr.visa_device, 'close',
            side_effect=self.instr.visa_device.close)


@skipIf(tmc.pyvisa is None, 'pyvisa is not installed.')
class TestPyVisaInstrument2Ivi(InstrumentTestBase, TestCase):
    resource_manager = tmc.pyvisa.ResourceManager('@ivi')
    class_tested = partial(
        tmc.PyVisaInstrument, resource_manager=resource_manager)
    timeout_implementation_error = 'VisaIOError'

    def setUp(self):
        super().setUp()
        self.close_patch = patch.object(
            self.instr.visa_device, 'close',
            side_effect=self.instr.visa_device.close)
