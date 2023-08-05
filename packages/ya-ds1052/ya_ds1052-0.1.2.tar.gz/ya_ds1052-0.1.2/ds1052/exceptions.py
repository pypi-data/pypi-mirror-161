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

class DS1052Error(Exception):
    def __init__(self, msg, original_exc=None):
        super().__init__(msg)
        self.original_exc = original_exc


class DS1052InitError(DS1052Error):
    pass


class DS1052TimeoutError(DS1052Error):
    pass


class DS1052PropertySetError(DS1052Error):
    """Raised when a property could not be successfully set because the
    read check after setting the property failed."""
    pass


class DS1052PropertyValueError(DS1052Error):
    """Raised when a property could not be set because an invalid value 
    was provided."""
    pass
