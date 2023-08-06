#
# This file is a part of Typhoon HIL API library.
#
# Typhoon HIL API is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

#
# Modbus API
#
class ModbusError(Exception):
    """
    Modbus general base error
    """
    def __init__(self, *args):
        super(ModbusError, self).__init__(*args)

class ModbusNotConnected(ModbusError):
    """
    Modbus connection is not opened
    """
    def __init__(self, *args):
        super(ModbusError, self).__init__(*args)

        self.message = "Connection is not opened!"

class ModbusInvalidRegSpec(ModbusError):
    """
    Modbus registers spec string is invalid
    """
    def __init__(self, *args):
        super(ModbusError, self).__init__(*args)

        self.message = "Registers specification string is invalid!"

class ModbusInvalidData(ModbusError):
    """
    Modbus values that need to be writen is invalid
    """
    def __init__(self, *args):
        super(ModbusError, self).__init__(*args)