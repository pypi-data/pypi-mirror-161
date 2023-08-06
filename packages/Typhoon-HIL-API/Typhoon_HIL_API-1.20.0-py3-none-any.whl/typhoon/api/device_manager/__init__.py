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
from typhoon.api.device_manager.stub import clstub


class DeviceManagerAPI(object):
    def __init__(self):
        super(DeviceManagerAPI, self).__init__()

    def load_setup(self, file=""):
        """
        Loads HIL setup from file to Control Center.

        Args:
            file (str): Setup description.

        Returns:
            status (bool): ``True`` if everything ok, otherwise returns ``False``.
        """
        return clstub().load_setup(file=file)

    def get_setup_devices(self):
        """
        Get all devices from current HIL setup.

        Returns:
             devices (list): dicts with information for each devices
              {"serial_number": "some_serial", "device_name": "some_device_name",
               "status": "device_stauts"}.

        """
        return clstub().get_setup_devices()

    def get_setup_devices_serials(self):
        """
        Get all devices from current HIL setup.

        Returns:
             devices (list): serial number of each device from setup.

        """
        return clstub().get_setup_devices_serials()

    def get_available_devices(self):
        """
        Get all discovered available devices.

        Returns:
            devices (list): available devices in JSON representation.

        """
        return clstub().get_available_devices()

    def get_detected_devices(self):
        """
        Get all discovered devices.

        Returns:
            devices (list): discovered devices in JSON representation.

        """
        return clstub().get_detected_devices()

    def add_devices_to_setup(self, devices=[]):
        """
        Add devices to active setup.

        Args:
            devices (list): devices to add.

        Returns:
            status (bool): ``True`` if everything ok, otherwise returns ``False``.
        """
        return clstub().add_devices_to_setup(devices=devices)

    def remove_devices_from_setup(self, devices=[]):
        """
        Remove devices from active setup.

        Args:
            devices (list): devices to remove.

        Returns:
            status (bool): ``True`` if everything ok, otherwise returns ``False``.
        """
        return clstub().remove_devices_from_setup(devices=devices)

    def connect_setup(self):
        """
        Activate current selected HIL setup.
        Make all devices in the selected setup inaccessible to others.

        Returns:
            status (bool): ``True`` if everything ok, otherwise returns ``False``.
        """
        return clstub().connect_setup()

    def disconnect_setup(self):
        """
        Deactivate current selected HIL setup.
        Make all devices in the selected setup accessible to others.

        Returns:
            status (bool): ``True`` if everything ok, otherwise returns ``False``.
        """
        return clstub().disconnect_setup()

    def is_setup_connected(self):
        """
        Returns current status of active HIL setup.

        Returns:
            status (bool): ``True`` if everything ok, otherwise returns ``False``.

        """
        return clstub().is_setup_connected()

    def add_discovery_ip_addresses(self, addresses=[]):
        """
        Specify addresses where HIL devices are located if auto discovery
        fails for some reason.

        Args:
            addresses (list): IP addresses where HIL devices are located.

        Returns:
            status (bool): ``True`` if everything ok, otherwise returns ``False``.

        """
        return clstub().add_discovery_ip_addresses(addresses=addresses)

    def remove_discovery_ip_addresses(self, addresses=[]):
        """
        Remove previously added addresses where HIL devices are located
        if auto discovery fails for some reason.
        
        Args:
            addresses (list): IP addresses which you want to remove.

        Returns:
            status (bool): ``True`` if everything ok, otherwise returns ``False``.

        """
        return clstub().remove_discovery_ip_addresses(addresses=addresses)


device_manager = DeviceManagerAPI()
