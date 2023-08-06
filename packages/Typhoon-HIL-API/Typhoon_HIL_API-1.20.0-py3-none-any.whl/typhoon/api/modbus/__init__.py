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
import struct
from itertools import groupby
from operator import itemgetter

from pyModbusTCP.client import ModbusClient
from scipy._lib.decorator import decorator

from typhoon.api.modbus.exceptions import ModbusError, ModbusNotConnected, ModbusInvalidRegSpec, ModbusInvalidData
from typhoon.api.modbus import lang as lang_util
from typhoon.api.modbus import util
from typhoon.api.modbus import const

# monkey patch socket module
import win_inet_pton

# special decorator that is friendly with the Sphinx autodoc feature and propagate
# not only __name__, __doc__ but also signature of the wrapped function
@decorator
def _check_connection(func ,*args, **kwargs):
    """
    Decorator functions that checks if connection to modbus server is opened
    :return:
    """
    # get self
    self = args[0]

    # only check if connection auto open features is not enabled
    if not self.auto_open():
        # check if connection is opened
        if not self._modbus.is_open():
            raise ModbusNotConnected()

    return func(*args, **kwargs)


class TCPModbusClient(object):
    """
    Class that implements functionalities of the TCP based Modbus client.

    The class itself is the proxy to ModbusClent() class of the PyModbusTCP library (http://pythonhosted.org/pyModbusTCP/package/class_ModbusClient.html)
    with a additional functionalities.
    """

    LITTLE_ENDIAN = const.LITTLE_ENDIAN
    BIG_ENDIAN    = const.BIG_ENDIAN

    def __init__(self, host=None, port=None, unit_id=None,
                 timeout=None, debug=None, auto_open=None, auto_close=None):
        """
        Creates a instance of the TCPModbusClient.
        Client parameters can be set here or later by using appropriate functions (``set_host()``, ``set_port()`` etc)

        :param host: hostname or IPv4/IPv6 address server address (optional)
        :type host: str
        :param port: TCP port number (optional)
        :type port: int
        :param unit_id: unit ID (optional)
        :type unit_id: int
        :param timeout: socket timeout in seconds (optional)
        :type timeout: float
        :param debug: debug state (optional)
        :type debug: bool
        :param auto_open: auto TCP connect on first request (optional)
        :type auto_open: bool
        :param auto_close: auto TCP close after each request (optional)
        :type auto_close: bool
        :return: TCPModbusClient object
        :rtype: TCPModbusClient
        :raise ValueError: if input parameters' values are incorrect
        """
        super(TCPModbusClient, self).__init__()

        # create a instance of the modbus client
        self._modbus = ModbusClient(host=host, port=port, unit_id=unit_id,timeout=timeout,
                                    debug=debug, auto_open=auto_open, auto_close=auto_close)

        # endianness
        self.endianness = TCPModbusClient.BIG_ENDIAN


    def _validate_registers(self, registers):
        """
        Validates given registers.
        :param registers: list of registers that need to be validated
        :raise: ModbusInvalidRegSpec: if register validation is not passed
        """

        # validate registers (correct length of addresses)
        for reg in registers:
            # supported 16bit, 32bit and 64bit registers only
            if len(reg.addresses) > 4 or len(reg.addresses) == 3:
                raise ModbusInvalidRegSpec("Input register not specified correctly! "
                                           "Only 16 bit, 32 bit and 64 bit registers are supported.")

            # if register is float type only 32bit and 64bit registers are supported
            if reg.register_type == const.RT_FLOAT and len(reg.addresses) == 1:
                raise ModbusInvalidRegSpec("Input register not specified correctly! "
                                           "Only 32 bit and 64 bit float registers are supported.")

    def _read_registers(self, registers, read_func):
        """
        Reads values from the addresses of given ``registers`` by using provided ``read_func`` function.
        :param registers: list of ``Register`` objects
        :param read_func: function used for reading values from registers' addresses
        :return: list of data read from given registers
        """
        # reg_addr = [1,2,3, 3, 7,8,9 ,5]
        #               to
        # reg_addr = [1,2,3,7,8,9,5]
        # collect registers addresses (the same addresses will be excluded)
        reg_addr = set()
        for reg in registers:
            for adr in reg.addresses:
                reg_addr.add(adr)

        # sort addresses
        # sorted_list = [1,2,3,5,7,8,9]
        reg_addr = sorted(reg_addr)

        # group successive addresses
        # grouped_list = [[1,2,3],[5],[7,8,9]]
        grouped_list = []
        for k, g in groupby(enumerate(reg_addr), lambda i_x: i_x[0] - i_x[1]):
            grouped_list.append(list(map(itemgetter(1), g)))

        # read all data
        # sorted_list = [1,2,3,5,7,8,9]
        #           to
        # grouped_list = [[1,2,3],[5],[7,8,9]]
        #           to
        # data = [d1,d2,d3,d5,d7,d8,d9]
        read_data = []
        for gr in grouped_list:
            # read data by using address from each group
            read_data.extend(read_func(reg_addr=gr[0], reg_nb=len(gr)))

        # collect data for each register
        for reg in registers:
            # find indexes in sorted addresses list
            indexes = list(map(reg_addr.index, reg.addresses))

            # use indexes to get data and fill register
            reg.addresses_values = [read_data[i] for i in indexes]

        return [reg.value for reg in registers]


    def _write_registers(self, registers, values):
        """
        Writes ``values` to the addresses of given ``registers``.
        :param registers: list of ``Register`` objects
        :param values: list of uint16 values that need to be writen on given registers addresses
        """

        # reg_addr = [1,2,3, 7,8,9 ,5]
        # collect registers addresses
        reg_addr = []
        for reg in registers:
            reg_addr.extend(reg.addresses)

        # convert given values
        # reg_addr = [1,2,3, 7,8,9 ,5] -> three registers
        # values = [rd1, rd2, rd3]
        #        to
        # converted_values = [d1,d2,d3,d7,d8,d9,d5]
        converted_values = []
        for reg, val in zip(registers, values):
            # convert value to list of uint16 values
            c_v = reg.convert_value(val)

            # add to list of converted values
            converted_values.extend(c_v)

        # sort addresses
        # sorted_list = [1,2,3,5,7,8,9]
        sorted_reg_addr = sorted(reg_addr)

        # group successive addresses
        # grouped_list = [[1,2,3],[5],[7,8,9]]
        grouped_list = []
        for k, g in groupby(enumerate(sorted_reg_addr), lambda i_x1: i_x1[0] - i_x1[1]):
            grouped_list.append(list(map(itemgetter(1), g)))

        # write all data
        # converted_values = [d1,d2,d3,d7,d8,d9,d5]
        #           write to
        # grouped_list = [[1,2,3],[5],[7,8,9]]
        #
        # find indexes of grouped addresses in unsorted registers addresses list
        # in order to collect correct data
        #
        # grouped_list = [[1,2,3],[5],[7,8,9]]
        #           index from
        # reg_addr = [1,2,3, 7,8,9 ,5]
        #           to index data
        # converted_values = [d1,d2,d3,d7,d8,d9,d5]
        #
        for gr in grouped_list:
            # find indexes in unsorted addresses list
            indexes = list(map(reg_addr.index, gr))

            # collect data
            data = [converted_values[i] for i in indexes]

            # write collected data on the group of addresses
            self.write_multiple_registers(gr[0], data)


    def modbus(self):
        """
        Return wrapped ModbusClent object.

        :returns: ModbusClent object
        :rtype: ModbusClent
        """

        return self._modbus


    def endianness(self):
        """
        Returns currently set endianness
        :return:
        """

        return self.endianness

    def set_endianness(self, endian_type):
        """
        Sets endianness that will be used for merging multiple 16 bit registers' values in one 32 bit or 64 bit number

        :param endian_type: ``little_endian`` or ``big_endian`` or appropriate constants can be used:

        * TCPModbusClient.BIG_ENDIAN
        * TCPModbusClient.LITTLE_ENDIAN

        :raises ModbusError: in case endianness type is not supported
        """

        if endian_type not in (TCPModbusClient.BIG_ENDIAN, TCPModbusClient.LITTLE_ENDIAN):
            raise ModbusError("Unsupported endianness type!")

        self.endianness = endian_type


    def auto_close(self):
        """
        Returns status of auto TCP close mode.
        :returns: auto close mode status (``True`` activated or ``False`` deactivated)
        :rtype: bool
        """

        return self._modbus.auto_close()

    def set_auto_close(self, state):
        """
        Set auto TCP close mode. If this mode is active, connection will be closed after each request.

        :param state: Activate/deactivate auto close mode
        :type state: bool
        """

        self._modbus.auto_close(state=state)

    def auto_open(self):
        """
        Returns status of auto TCP connect mode.
        :returns: auto open mode status (``True`` activated or ``False`` deactivated)
        :rtype: bool
        """

        return self._modbus.auto_open()

    def set_auto_open(self, state):
        """
        Set auto TCP connect mode. If this mode is active, connection will be opened on the first request.

        :param state: Activate/deactivate auto open mode
        :type state: bool
        """

        self._modbus.auto_open(state=state)

    def close(self):
        """
        Closes TCP connection.

        :returns: close status (``True`` if connection successfully closed or ``None`` if connection already closed)
        :rtype: bool or None
        """
        return self._modbus.close()

    def open(self):
        """
        Connect to modbus server (open TCP connection)

        :returns: connect status (``True`` if connection successfully opened otherwise return ``False``)
        :rtype: bool
        """

        return self._modbus.open()

    def debug(self):
        """
        Returns status of debug mode.

        :returns: debug mode status (``True`` activated or ``False`` deactivated)
        :rtype: bool
        """
        return self._modbus.debug()

    def set_debug(self, state):
        """
        Set debug mode.

        .. note::

            While debug mode is active, debug information will be writen to the console.

        :param state: Activate/deactivate debug mode
        :type state: bool
        """
        self._modbus.debug(state=state)

    def host(self):
        """
        Returns current host.

        :returns: hostname
        :rtype: str
        """

        return self._modbus.host()

    def set_host(self, hostname):
        """
        Set host (IPv4/IPv6 address or hostname like 'plc.domain.net')

        :param hostname: hostname or IPv4/IPv6 address
        :type hostname: str
        :raise ModbusError: if hostname is invalid or cannot be set
        """

        status =  self._modbus.host(hostname=hostname)
        if status is None:
            raise ModbusError("Host name '{0}' cannot be set! Please check host name.".format(hostname))

    def port(self):
        """
        Returns current TCP port.

        :returns: TCP port value
        :rtype: int
        """
        return self._modbus.port()

    def set_port(self, port):
        """
        Set TCP port.

        :param port: TCP port number
        :type port: int
        :raise ModbusError: if port is invalid or cannot be set
        """
        status =  self._modbus.port(port=port)
        if status is None:
            raise ModbusError("Port '{0}' cannot be set! Please, check input parameter.".format(port))


    def timeout(self):
        """
        Returns current timeout.

        :returns: socket timeout value
        :rtype: float
        """

        return self._modbus.timeout()

    def set_timeout(self, timeout=None):
        """
        Set socket timeout.

        :param timeout: socket timeout in seconds (0 to 3600)
        :type timeout: float
        :raise ModbusError: if timeout is invalid or cannot be set
        """

        status = self._modbus.timeout(timeout=timeout)
        if status is None:
            raise ModbusError("Timeout '{0}' cannot be set! Please, check input parameter.".format(timeout))


    def unit_id(self):
        """
        Returns current unit ID.

        :returns: unit ID value
        :rtype: int
        """

        return self._modbus.unit_id()


    def set_unit_id(self, unit_id=None):
        """
        Sets unit ID field.

        :param unit_id: unit ID (0 to 255)
        :type unit_id: int
        :raise ModbusError: if unit ID is invalid or cannot be set
        """

        status = self._modbus.unit_id(unit_id=unit_id)
        if status is None:
            raise ModbusError("Unit ID '{0}' cannot be set! Please, check input parameter.".format(unit_id))


    def is_open(self):
        """
        Get status of TCP connection.

        :returns: status (``True`` if connection is opened otherwise return ``False``)
        :rtype: bool
        """

        return self._modbus.is_open()

    @_check_connection
    def read_coils(self, bit_addr, bit_nb=1, to_int = False):
        """
        Implementation of Modbus function READ_COILS (0x01).

        Reads ``bit_nb`` number of successive addresses starting from ``bit_addr`` address.

        :param bit_addr: bit address (0 to 65535)
        :type bit_addr: int
        :param bit_nb: number of bits to read (1 to 2000)
        :type bit_nb: int
        :param to_int: convert coils values to integer number

        .. note::

            Value read from ``bit_addr`` address is treated as MSB

        :type to_int: bool
        :returns: list of booleans (``True`` or ``False``) or integer number if ``to_int==True``
        :rtype: list of bool
        :raises ModbusError (base exception): if error occurs during read of coils
        :raises ModbusNotConnected: if connection is not opened before this function is called
        """

        bool_values = self._modbus.read_coils(bit_addr, bit_nb=bit_nb)

        # if error occurs
        if bool_values is None:
            raise ModbusError("Coils cannot be read! Please, check input parameters and timeout value.")

        # if we don't need to convert to integer number
        if not to_int:
            return bool_values

        # convert value to integer number
        else:
            return util.bool_list_to_int(bool_values)

    @_check_connection
    def read_discrete_inputs(self, bit_addr, bit_nb=1, to_int = False):
        """
        Implementation of Modbus function READ_DISCRETE_INPUTS (0x02)

        Reads ``bit_nb`` number of successive addresses starting from ``bit_addr`` address.

        :param bit_addr: bit address (0 to 65535)
        :type bit_addr: int
        :param bit_nb: number of bits to read (1 to 2000)
        :type bit_nb: int
        :param to_int: convert coils values to integer number

        .. note::

            Value read from ``bit_addr`` address is treated as MSB

        :type to_int: bool
        :returns: list of integers (``1`` or ``0``) or integer number if ``to_int==True``
        :rtype: list of bool
        :raises ModbusError (base exception): if error occurs during read of discrete inputs
        :raises ModbusNotConnected: if connection is not opened before this function is called
        """

        bool_values = self._modbus.read_discrete_inputs(bit_addr, bit_nb=bit_nb)

        # if error occurs
        if bool_values is None:
            raise ModbusError("Discrete inputs cannot be read! Please, check input parameters and timeout value.")

        # if we don't need to convert to integer number
        if not to_int:
            return bool_values

        # convert value to integer number
        else:
            return util.bool_list_to_int(bool_values)

    @_check_connection
    def read_input_registers(self, reg_addr, reg_nb=1):
        """
        Implementation of Modbus function READ_INPUT_REGISTERS (0x04)

        :param reg_addr: register address (0 to 65535)
        :type reg_addr: int
        :param reg_nb: number of registers to read (1 to 125)
        :type reg_nb: int
        :returns: registers list
        :rtype: list of int
        :raises ModbusError (base exception): if error occurs during read of input registers
        :raises ModbusNotConnected: if connection is not opened before this function is called
        """

        register_values = self._modbus.read_input_registers(reg_addr, reg_nb=reg_nb)

        # if error occurs
        if register_values is None:
            raise ModbusError("Input registers cannot be read! Please, check input parameters and timeout value.")

        return register_values

    @_check_connection
    def read_holding_registers(self, reg_addr, reg_nb=1):
        """
        Implementation of Modbus function READ_HOLDING_REGISTERS (0x03)

        :param reg_addr: register address (0 to 65535)
        :type reg_addr: int
        :param reg_nb: number of registers to read (1 to 125)
        :type reg_nb: int
        :returns: registers list
        :rtype: list of int
        :raises ModbusError (base exception): if error occurs during read of holding registers
        :raises ModbusNotConnected: if connection is not opened before this function is called
        """

        register_values = self._modbus.read_holding_registers(reg_addr, reg_nb=reg_nb)

        # if error occurs
        if register_values is None:
            raise ModbusError("Holding registers cannot be read! Please, check input parameters and timeout value.")

        return register_values

    @_check_connection
    def read_input_registers_adv(self, read_spec):
        """
        Advance function for reading input registers.

        :param read_spec: string with registers specification

        .. note::

            To specify registers specification special simple language is used.
            More about ``Registers Specification Language`` you can read :doc:`here </modbus_reg_spec>`.

        :type read_spec: string
        :returns: data list with values converted to specified registers types
        :rtype: list of unsigned/signed int or float numbers depending read specification
        :raises ModbusError (base exception): if error occurs during read of input registers
        :raises ModbusNotConnected: if connection is not opened before this function is called
        :raises ModbusInvalidRegSpec: if registers specification (``read_spec``) is not correct
        """

        # validate and parse
        registers = lang_util.get_registers(read_spec)

        # validate registers
        self._validate_registers(registers)

        # read registers' addresses
        return self._read_registers(registers, self.read_input_registers)

    @_check_connection
    def read_holding_registers_adv(self, read_spec):
        """
        Advance function for reading holding registers.

        :param read_spec: string with registers specification

        .. note::

            To specify registers specification special simple language is used.
            More about ``Registers Specification Language`` you can read :doc:`here </modbus_reg_spec>`.

        :type read_spec: string
        :returns: data list with values converted to specified registers types
        :rtype: list of unsigned/signed int or float numbers depending read specification
        :raises ModbusError (base exception): if error occurs during read of input registers
        :raises ModbusNotConnected: if connection is not opened before this function is called
        :raises ModbusInvalidRegSpec: if registers specification (``read_spec``) is not correct
        """

        # validate and parse
        registers = lang_util.get_registers(read_spec)

        # validate registers
        self._validate_registers(registers)

        # read registers' addresses
        return self._read_registers(registers, self.read_holding_registers)


    @_check_connection
    def write_single_coil(self, bit_addr, bit_value):
        """
        Implementation of Modbus function WRITE_SINGLE_COIL (0x05)

        Write ``bit_value`` value on ``bit_addr`` address.

        :param bit_addr: bit address (0 to 65535)
        :type bit_addr: int
        :param bit_value: bit value to write
        :type bit_value: bool
        :raises ModbusError (base exception): if error occurs during write of single coil
        :raises ModbusNotConnected: if connection is not opened before this function is called
        """

        status = self._modbus.write_single_coil(bit_addr, bit_value)
        if status is None:
            raise ModbusError("Single coil cannot be written! Please, check input parameters and timeout value.")


    @_check_connection
    def write_single_register(self, reg_addr, reg_value):
        """
        Implementation of Modbus function WRITE_SINGLE_REGISTER (0x06)

        Write ``reg_value`` value on ``reg_addr`` address.

        :param reg_addr: register address (0 to 65535)
        :type reg_addr: int
        :param reg_value: register value to write
        :type reg_value: int
        :raises ModbusError (base exception): if error occurs during write of single register
        :raises ModbusNotConnected: if connection is not opened before this function is called
        """

        status = self._modbus.write_single_register(reg_addr, reg_value)
        if status is None:
            raise ModbusError("Single register cannot be written! Please, check input parameters and timeout value.")


    @_check_connection
    def write_multiple_coils(self, bits_addr, bits_value):
        """
        Implementation of Modbus function WRITE_MULTIPLE_COILS (0x0F)

        Write ``bits_value`` values starting from ``bits_addr`` address.

        :param bits_addr: bits address (0 to 65535)
        :type bits_addr: int
        :param bits_value: bits values to write
        :type bits_value: list
        :raises ModbusError (base exception): if error occurs during write of multiple coils
        :raises ModbusNotConnected: if connection is not opened before this function is called
        """

        status = self._modbus.write_multiple_coils(bits_addr, bits_value)
        if status is None:
            raise ModbusError("Multiple coils cannot be written! Please, check input parameters and timeout value.")

    @_check_connection
    def write_multiple_registers(self, regs_addr, regs_value):
        """
        Implementation of Modbus function WRITE_MULTIPLE_REGISTERS (0x10)

        Write ``regs_value`` values starting from ``regs_addr`` address.

        :param regs_addr: registers address (0 to 65535)
        :type regs_addr: int
        :param regs_value: registers values to write
        :type regs_value: list
        :raises ModbusError (base exception): if error occurs during write of multiple registers
        :raises ModbusNotConnected: if connection is not opened before this function is called
        """

        status = self._modbus.write_multiple_registers(regs_addr, regs_value)
        if status is None:
            raise ModbusError("Multiple registers cannot be written! Please, check input parameters and timeout value.")

    @_check_connection
    def write_registers_adv(self, write_spec, regs_values):
        """
        Advance function for writing multiple registers.

        :param write_spec: string with registers specification

        .. note::

            To specify registers specification special simple language is used.
            More about ``Registers Specification Language`` you can read :doc:`here </modbus_reg_spec>`.

        :param regs_values: registers values to write.
        :type regs_values: list of unsigned/signed int or float numbers depending write specification
        :raises ModbusError (base exception): if error occurs during write of multiple registers
        :raises ModbusNotConnected: if connection is not opened before this function is called
        :raises ModbusInvalidRegSpec: if registers specification (``write_spec``) is not correct
        :raises ModbusInvalidData: if provided registers values are not compatible with registers types
        """

        # validate and parse
        registers = lang_util.get_registers(write_spec)

        # validate registers
        self._validate_registers(registers)

        # check length of data and registers
        if len(registers) != len(regs_values):
            raise ModbusInvalidRegSpec("Number of registers need to be the same as registers values that need to be writen!")

        # write data to registers
        try:
            self._write_registers(registers, regs_values)
        except struct.error:
            raise ModbusInvalidData("Some of provided registers values are not compatible with the registers types "
                                    "specified in registers specification!")
