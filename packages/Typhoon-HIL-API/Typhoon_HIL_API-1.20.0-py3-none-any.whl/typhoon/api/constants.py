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

SERVICE_REGISTRY_HEADER = "typhoon-service-registry"

SCHEMATIC_API_NAME = "sch_api"
HIL_API_NAME = "hil_api"
FIRMWARE_API_NAME = "fw_api"
PV_GENERATOR_API_NAME = "pv_gen_api"
SCADA_API_NAME = "scada_api"
CONFIGURATION_MANAGER_API_NAME = "configuration_manager_api"
DEVICE_MANAGER_API_NAME = "device_manager_api"

ENV_API_NAME = "env_api"

DEFAULT_SETTINGS_CONF_STR = """
[server_settings]
server_ip = "localhost"
announcement_port_req_range = 30000-30100
announcement_port_pub_range = 50000-50100

[path]
;python_path = c:\\Python37
;src_path = c:\\path\\to\\source
""".strip()