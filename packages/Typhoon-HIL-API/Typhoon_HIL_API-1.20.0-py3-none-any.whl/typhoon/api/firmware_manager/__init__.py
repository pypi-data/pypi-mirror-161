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
from __future__ import print_function, unicode_literals

from typhoon.api.firmware_manager.stub import clstub


def update_firmware(device_id=0, configuration_id=None, force=False):
    """
    Uploads firmware with given configuration id to HIL device with chosen id.
    If HIL device already have the same configuration, only upload if force
    parameter is set.

    Args:
        device_id (int): id of HIL device whose firmware is to be updated
        configuration_id (int): Update to a firmware with given
            configuration id
        force (boolean): Force upload even if desired firmware is the same as
            the one already in HIL device

    .. note::
        There should be only one device with a given device id, otherwise
        exception will be raised.

        If `configuration_id` is not provided, it is considered as the current
        firmware id in the device.

    Returns:
        None
    """
    return clstub().update_firmware(device_id=device_id,
                                    configuration_id=configuration_id,
                                    force=force)


def get_hil_info():
    """
    Returns information about all connected HIL devices.

    Returns:
        list: list that contains dictionaries where each dictionary holds
        information about one connected HIL device.

        In case there is no connected HIL devices ``None`` will be returned.

    .. list-table::  Format of one dictionary that holds HIL information.
       :widths: auto
       :header-rows: 1
       :align: left

       * - Dictionary key
         - Meaning
         - Value Type

       * - "device_id"
         - HIL Device ID (0, 1, 2...)
         - int value

       * - "serial_number"
         - HIL Serial number (00404-00-0001, 00402-00-0001...)
         - string value

       * - "configuration_id"
         - HIL Configuration ID (1, 2, 3...)
         - int value

       * - "product_name"
         - HIL Product Name (HIL402, HIL602...)
         - string value

       * - "firmware_release_date"
         - HIL Firmware Release date (in format Y-M-D)
         - string value

       * - "calibration_date"
         - HIL Calibration date (in format Y-M-D). ``None`` will be
           returned if HIL is not calibrated, calibration data is
           wrong or calibration is not supported on connected HIL)
         - string value
    """

    return clstub().get_hil_info()
