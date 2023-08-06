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

from textx.exceptions import TextXSyntaxError
from textx.metamodel import metamodel_from_str

from typhoon.api.modbus import util
from typhoon.api.modbus import const
from typhoon.api.modbus.exceptions import ModbusInvalidRegSpec

REGISTERS_SPEC_GRAMMAR = """
RegistersSpecification:
    registers*=RegistrySpec[',']
;

RegistrySpec:
    SingleAddress | MultiAddress
;

SingleAddress:
    address=/\d+/ reg_type=RegType
;

MultiAddress:
 '[' addresses+=INT[','] ']' reg_type=RegType
;

RegType:
    "u" | "i" | "f" | ""
;
"""


class Register(object):
    """
    Class that describe one register
    """

    def __init__(self):
        super(Register, self).__init__()

        # addresses
        self.addresses = []

        # register type
        self.register_type = const.RT_UNSIGNED_INT

        # values from addresses (unsigned int 16bit values)
        self.addresses_values = []

        # register value
        self._value = None

        # endianness
        self.endianness = const.BIG_ENDIAN


    @property
    def value(self):
        """
        Converts addresses values to register value and return it
        :return:
        """

        # number of addresses
        num_of_addr = len(self.addresses)

        # convert values to value
        # 16bit register
        if num_of_addr == 1:
            if self.register_type == const.RT_SIGNED_INT:
                self._value = util.uint16_to_int16(self.addresses_values[0])
            elif self.register_type == const.RT_UNSIGNED_INT:
                self._value = self.addresses_values[0]

        # 32bit or 64bit register
        elif num_of_addr >= 2:
            # get function to convert list of uint16 integers to registry type
            if self.register_type == const.RT_SIGNED_INT:
                list_to_value = util.uint16_list_to_int32 if num_of_addr == 2 else util.uint16_list_to_int64
            elif self.register_type == const.RT_FLOAT:
                list_to_value = util.uint16_list_to_float if num_of_addr == 2 else util.uint16_list_to_double
            elif self.register_type == const.RT_UNSIGNED_INT:
                list_to_value = util.uint16_list_to_uint32 if num_of_addr == 2 else util.uint16_list_to_uint64

            # convert list of integers to registry type
            self._value = list_to_value(self.addresses_values, big_endian=True
                                                               if self.endianness == const.BIG_ENDIAN else
                                                               False)

        return self._value

    def convert_value(self, value):
        """
        Converts given value to registry format (uint16 value or listo of uint16 values)
        :param value: value to convert
        :return: list with converted value(s)
        """

        # number of addresses
        num_of_addr = len(self.addresses)

        # convert values to value
        # 16bit register
        if num_of_addr == 1:
            if self.register_type == const.RT_SIGNED_INT:
                value = [util.int16_to_uint16(value)]
            elif self.register_type == const.RT_UNSIGNED_INT:
                if 0 <= value <= 65535:
                    value = [int(value)]
                else:
                    raise struct.error("Provided value is outside of range [0, 65535]")

        # 32bit or 64bit register
        elif num_of_addr >= 2:
            # get function to convert list of uint16 integers to registry type
            if self.register_type == const.RT_SIGNED_INT:
                value_to_list = util.int32_to_uint16_list if num_of_addr == 2 else util.int64_to_uint16_list
            elif self.register_type == const.RT_FLOAT:
                value_to_list = util.float_to_uint16_list if num_of_addr == 2 else util.double_to_uint16_list
            elif self.register_type == const.RT_UNSIGNED_INT:
                value_to_list = util.uint32_to_uint16_list if num_of_addr == 2 else util.uint64_to_uint16_list

            # convert list of integers to registry type
            value = value_to_list(value, big_endian=True
                                  if self.endianness == const.BIG_ENDIAN else
                                  False)

        return value


def parse_registers_spec(spec):
    """
    Parses Modbus registers spec string and return object representation of the specification
    :param spec: string with registers specification
    :rtype string
    :return: RegistersSpecification object
    :rtype RegistersSpecification
    :raise: ModbusInvalidRegSpec: if provided registers spec string is not in right format
    """

    if not isinstance(spec, str) or spec == "":
        raise ModbusInvalidRegSpec()

    try:
        registers_spec_obj = metamodel_from_str(REGISTERS_SPEC_GRAMMAR).model_from_str(spec)
    except TextXSyntaxError:
        raise ModbusInvalidRegSpec()

    return registers_spec_obj


def transform_registers_spec(registers_spec, big_endian = True):
    """
    Transforms given RegistersSpecification object in the list of Registry objects
    :param registers_spec:  RegistersSpecification object
    :param big_endian: endianness used for merging multiple 16bit number to one 32bit or 64bit number
    :return: list of Register objects
    """

    list_of_registers = []
    for register_spec in registers_spec.registers:

        # create register object
        reg = Register()

        # single
        if register_spec.__class__.__name__ == "SingleAddress":
            reg.addresses.append(int(register_spec.address))
        # multi
        elif register_spec.__class__.__name__ == "MultiAddress":
            reg.addresses.extend(register_spec.addresses)

        # if type is not specified default one is unsigned
        reg.register_type = register_spec.reg_type if register_spec.reg_type != "" else r"u"

        # set endianness
        reg.endianness = const.BIG_ENDIAN if big_endian else const.LITTLE_ENDIAN

        # append to the list
        list_of_registers.append(reg)

    return list_of_registers


def get_registers(spec, big_endian = True):
    """
    Returns list of registers by parsing registers specification string
    :param spec: registers specification string
    :return: lis of Register objects
    """

    if not isinstance(spec, str) or spec == "":
        raise ModbusInvalidRegSpec()

    try:
        # get registers specification obj
        registers_spec_obj = parse_registers_spec(spec)
    except ModbusInvalidRegSpec:
        raise

    # convert registers specification obj to list of registers
    return transform_registers_spec(registers_spec_obj, big_endian = big_endian)