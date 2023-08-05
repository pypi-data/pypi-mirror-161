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

# Alternatve TMC layer classes used by DS1052.

from contextlib import contextmanager
import logging
import os
from pathlib import Path
import sys
from time import time

try:
    import pyvisa
except ModuleNotFoundError:
    pyvisa = None

try:
    import usbtmc
except ModuleNotFoundError:
    usbtmc = None

from .exceptions import DS1052InitError, DS1052TimeoutError

DS1000_VENDOR_ID = 0x1ab1
DS1000_PRODUCT_ID = 0x0588


logging.basicConfig()
tmc_logger = logging.getLogger('tmc')
tmc_loglevel = os.getenv('TMC_LOGLEVEL')
if tmc_loglevel is not None:
    tmc_logger.setLevel(getattr(logging, tmc_loglevel))

instrument_classes = {}


class InstrumentBase:
    """Blackbox-like recording of TMC traffic:
    There are still enough obscure spurious errors, probably related to the
    DS1052 sometimes not liking to receive commands too quickly, that it
    makes sense to record the last commands and responses.
    """
    BUFFLEN = 50

    def __init__(self, *args, **kwargs):
        self.cmd_buff = []
        super().__init__(*args, **kwargs)

    def show_log_buff(self):
        now = time()
        for entry in self.cmd_buff:
            if len(entry) == 3:
                t, cmd, resp = entry
            else:
                t, cmd = entry
                resp = None
            tmc_logger.error(f'cmdlog: {now - t} {cmd!r} {resp!r}')

    def log_write(self, cmd):
        tmc_logger.debug(f'>>> {cmd!r}')
        if len(self.cmd_buff) >= self.BUFFLEN:
            self.cmd_buff.pop(0)
        self.cmd_buff.append([time(), cmd])

    def log_ask(self, response):
        tmc_logger.debug(f'<<< {response[:50]!r}')
        self.cmd_buff[-1].append(response[:30])


if usbtmc is not None:
    from usb.core import USBTimeoutError


    class PyUsbTmcInstrument(InstrumentBase, usbtmc.Instrument):
        """Instrument class based on the Instrment class from the
        python-usbtmc package.

        Minor addition to usbtmc.Instrument: Methods ask() and write()
        with logging.
        """
        def __init__(self, serial=None, **kwargs):
            if serial is not None:
                # An odd quirk in usbtmc: It seems to use internally a
                # representation of the serial number where the terminating
                # null byte is included...
                if not serial.endswith('\x00'):
                    serial = serial + '\x00'
            try:
                super().__init__(
                    idVendor=DS1000_VENDOR_ID, idProduct=DS1000_PRODUCT_ID,
                    iSerial=serial)
            except usbtmc.usbtmc.UsbtmcException as exc:
                if str(exc) == 'Device not found [init]':
                    raise DS1052InitError('Device not found.', exc)
                else:
                    raise

        def write_raw(self, message, encoding='utf-8'):
            """Write bytes to instrument."""
            super().write_raw(message)
            self.log_write(message)

        def ask(self, message):
            """Write the string `message` to the device and return the
            response as a string.
            """
            try:
                result = super().ask(message)
            except USBTimeoutError as exc:
                self.show_log_buff()
                raise DS1052TimeoutError(
                    f'Timeout waiting for a response to {message!r}.', exc)
            except:
                self.show_log_buff()
                raise
            self.log_ask(result)
            return result

        def ask_raw(self, message, size):
            """Write the bytes `message` to the device and return the
            response as bytes.
            """
            # XXX This is crazy: If a "num=..." is specified below, at least
            # 7 must be added to size, otherwise
            # test_read_waveforms_raw_in_stop_mode
            # crashes with "usb.core.USBError: [Errno 75] Overflow".
            # Interestingly, this does not happen in the first call of
            # ask_raw() in that test... Anyway, the size parameter is not
            # really needed by the parent classes method ask_raw() -
            # it is able to properly figure out the size of the response
            # by itself.
            try:
                result = super().ask_raw(message)
            except USBTimeoutError as exc:
                self.show_log_buff()
                raise DS1052TimeoutError(
                    f'Timeout waiting for a response to {message!r}.', exc)
            except:
                self.show_log_buff()
                raise
            self.log_ask(result)
            return result


    instrument_classes[PyUsbTmcInstrument.__name__] = PyUsbTmcInstrument

if sys.platform == 'linux':
    class LkUsbTmcInstrument(InstrumentBase):
        """Instrument class that uses device files provided by the Linux
        kernel usbtmc module.
        """
        def __init__(self, serial=None, **kwargs):
            super().__init__()
            candidates = self.list_devices(serial)
            if not candidates:
                raise DS1052InitError('Device not found.')
            if len(candidates) > 1:
                raise DS1052InitError(
                    f'More than one matching device found: {candidates}\n'
                    f'Specify a serial number.')
            self.file = os.open(
                f'/dev/{candidates[0][0]}', os.O_RDWR | os.O_EXCL)

        @classmethod
        def list_devices(cls, serial=None):
            result = []
            if serial is not None and serial[-1] == '\x00':
                serial = serial[:-1]
            for path in Path('/sys/class/usbmisc').iterdir():
                if not path.name.startswith('usbtmc'):
                    continue
                # This is a symlink that points to a directory like
                #
                # /sys/devices/pci0000:00/0000:00:1c.2/0000:02:00.0/
                # usb5/5-3/5-3:1.0/usbmisc/usbtmc1
                #
                # "5-3" contains the more generic stuff like the product and
                # vendor IDs we want.
                device_path = path.resolve().parent.parent.parent
                with (device_path / 'idVendor').open() as f:
                    vendor_id = int(f.read().strip(), 16)
                if vendor_id != DS1000_VENDOR_ID:
                    continue
                with (device_path / 'idProduct').open() as f:
                    product_id = int(f.read().strip(), 16)
                if product_id != DS1000_PRODUCT_ID:
                    continue
                serial_path = device_path / 'serial'
                if not serial_path.exists():
                    found_serial = None
                else:
                    with serial_path.open() as f:
                        found_serial = f.read().strip()
                if serial is not None and found_serial != serial:
                    continue
                result.append((path.name, found_serial))
            return result

        def close(self):
            if self.file is not None:
                os.close(self.file)
                self.file = None

        def write(self, message):
            self.write_raw(message.encode('utf-8'))

        def write_raw(self, message):
            """Write string to instrument."""
            # Parameter encoding dropped: It's quite unlikely that any string
            # sent by this module will contain a symbol outside the ASCII set.
            os.write(self.file, message)
            self.log_write(message)

        def ask(self, message):
            # ask() is only called to get relatiely short response string.
            # A size of 256 is sufficient. The exact value does not matter,
            # as long as _some_ number is given: The os.read() call in
            # ask_raw() needs a value.
            return self.ask_raw(message.encode('utf-8'), 256).decode('utf-8')

        def ask_raw(self, message, size):
            self.write_raw(message)
            try:
                result = os.read(self.file, size)
            except TimeoutError as exc:
                self.show_log_buff()
                raise DS1052TimeoutError(
                    f'Timeout waiting for a response to {message!r}.', exc)
            except:
                self.show_log_buff()
                raise
            self.log_ask(result)
            return result


    instrument_classes[LkUsbTmcInstrument.__name__] = LkUsbTmcInstrument

if pyvisa is not None:
    _visa_rm = None


    class PyVisaInstrument(InstrumentBase):
        def __init__(self, serial=None, resource_manager=None):
            super().__init__()
            if resource_manager is None:
                resource_manager = self._get_resource_manager()
            resource_ids = self._find_resource_ids(serial, resource_manager)
            if not resource_ids:
                raise DS1052InitError('Device not found.')
            if len(resource_ids) > 1:
                raise DS1052InitError(
                    f'More than one matching device found: {resource_ids}\n'
                    f'Specify a serial number.')
            self.visa_device = resource_manager.open_resource(
                resource_ids[0], chunk_size=1024*1024)

        def _get_resource_manager(self):
            global _visa_rm
            if _visa_rm is None:
                _visa_rm = pyvisa.ResourceManager('@py')
            return _visa_rm

        def _find_resource_ids(self, wanted_serial, resource_manager):
            result = []
            # The pyvisa-py backend returns a serial number with a trailing
            # null value; ni-visa does not do that... Users may give
            # either variant - just remove possibly exiting trailing nulls
            # fromo the "wanted" value and from the serial numbers found
            # in strings returned by list_resources().
            if wanted_serial is not None and wanted_serial.endswith('\x00'):
                wanted_serial = wanted_serial[:-1]
            for item in resource_manager.list_resources():
                parts = item.split('::')
                if len(parts) <= 4:
                    # e.g.: 'ASRL2::INSTR'
                    continue
                bus, vendor_id, product_id, serial = parts[:4]
                if not bus.startswith('USB'):
                    continue
                if self._id_from_str(vendor_id) != DS1000_VENDOR_ID:
                    continue
                if self._id_from_str(product_id) != DS1000_PRODUCT_ID:
                    continue
                if wanted_serial is not None:
                    if serial.endswith('\x00'):
                        serial = serial[:-1]
                    if wanted_serial != serial:
                        continue
                result.append(item)
            return result

        def _id_from_str(self, s):
            # pyvisa-py provides USB vendor/product IDs in decimal
            # representation; NI-Visa as hex numbers with a leading '0x'...
            if s.startswith('0x'):
                return int(s[2:], 16)
            return int(s)

        def close(self):
            self.visa_device.close()


        @contextmanager
        def _visa_exceptions_mapper(self, message, writing):
            try:
                yield
            except pyvisa.VisaIOError as exc:
                self.show_log_buff()
                if 'Timeout expired before operation completed.' in str(exc):
                    if writing:
                        raise DS1052TimeoutError(
                            f'Timeout writing {message!r}.', exc)
                    else:
                        raise DS1052TimeoutError(
                            f'Timeout waiting for a response to {message!r}.',
                            exc)
                raise
            except ValueError as exc:
                # A ValueError can occur with pyvisa_py in
                # pyvisa_py.protocols.usbtmc.USBTMC.read() when the TMC
                # message DEV_DEP_MSG_IN is written.
                # XXX not the best idea to rely on the fixed errno value...
                # In a sense, this is a problem of pyvisa_py: The original
                # exception is a usb.core.USBTimeoutError but that is
                # replace with a generic ValueError in
                # pyvisa_py.protocols.usbtmc.write()...
                self.show_log_buff()
                if str(exc) == '[Errno 110] Operation timed out':
                    if writing:
                        raise DS1052TimeoutError(
                            f'Timeout writing {message!r}.', exc)
                    else:
                        raise DS1052TimeoutError(
                            f'Timeout waiting for a response to {message!r}.',
                            exc)
                raise
            except:
                self.show_log_buff()
                raise

        def write(self, message):
            with self._visa_exceptions_mapper(message, True):
                self.visa_device.write(message)
            self.log_write(message)

        def write_raw(self, message):
            with self._visa_exceptions_mapper(message, True):
                self.visa_device.write_raw(message)
            self.log_write(message)

        def ask_raw(self, message, size):
            self.write_raw(message)
            with self._visa_exceptions_mapper(message, False):
                result = self.visa_device.read_raw(size)
            self.log_ask(result)
            return result

        def ask(self, message):
            self.write(message)
            with self._visa_exceptions_mapper(message, False):
                result = self.visa_device.read()
            self.log_ask(result)
            return result

    instrument_classes[PyVisaInstrument.__name__] = PyVisaInstrument

_all_instrument_class_names = [
    'PyVisaInstrument', 'PyUsbTmcInstrument', 'LkUsbTmcInstrument']


def get_tmc_device(serial=None, tmc_class=None, resource_manager=None):
    if len(instrument_classes) == 0:
        raise DS1052InitError(
            'No TMC instrument class found. At least one of the following\n'
            'modules is required:\n'
            '- the Python package PyVISA, together with a suitable backend,\n'
            '- the Python package python-tmcusb together with PyUSB \n'
            '  (questionable choice as python-tmcusb seems to be \n'
            '  unmaintained since a few years)')
    if tmc_class is None:
        for name in _all_instrument_class_names:
            if name in instrument_classes:
                tmc_class = instrument_classes[name]
                break
    else:
        if tmc_class not in instrument_classes:
            raise DS1052InitError(
                f'class {tmc_class!r} not found. Available classes:'
                f'{sorted(instrument_classes)}')
        tmc_class = instrument_classes[tmc_class]
    return tmc_class(serial, resource_manager=resource_manager)
