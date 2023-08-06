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

import os
import platform

from typhoon.api.version import get_version
from typhoon.api.constants import DEFAULT_SETTINGS_CONF_STR

try:
    from functools import lru_cache
except ImportError:
    # for py2
    from backports.functools_lru_cache import lru_cache


def os_compat_guard(func):
    """
    Decorator function used to check for OS compatibility
    Args:
        func: function which is being decorated

    Returns:
        guard function
    """
    os_name = platform.system()
    if os_name not in ("Windows", "Linux"):
        raise OSError("{} is currently unsupported.".format(os_name))

    def guard(*args, **kwargs):
        return func(*args, **kwargs)

    return guard


@os_compat_guard
def get_user_folder_path():
    """
    Depending on the OS, returns the path to the user.
    Returns:
    """
    os_name = platform.system()
    if os_name == "Windows":
        program_data = os.path.expandvars("%APPDATA%")
        # APPDATA system variable has not been defined
        if program_data == "%APPDATA%":
            return os.path.join(os.path.expanduser("~"),
                                "AppData","Roaming")
        else:
            # Returning APPDATA variable value as-is
            # Note: the user can still mess this up on his/her machine
            return program_data
    elif os_name == "Linux":
        config_home = os.path.expandvars("$XDG_CONFIG_HOME")
        # XDG_CONFIG_HOME system variable has not been defined
        if config_home == "$XDG_CONFIG_HOME":
            return os.path.join(os.path.expandvars("$HOME"),".config")
        else:
            # Returning XDG_CONFIG_HOME variable value as-is
            # Note: the user can still mess this up on his/her machine
            return config_home


def get_or_create_config(func):
    def inner(*args, **kwargs):
        config_path = func(*args, **kwargs)
        if not os.path.exists(config_path):
            try:
                os.makedirs(os.path.join(get_user_folder_path(),
                                         "typhoon-api", get_version()))
            except FileExistsError:
                pass
            # Creates the settings.conf file (if old
            with open(config_path, "w") as cfg_file:
                cfg_file.write(DEFAULT_SETTINGS_CONF_STR)
        return config_path

    return inner


def check_environ_vars(server_type):
    """
    Decorator which checks environment vars
    for the TYPHOON-API entry, and uses those
    settings if they are found - otherwise,
    the default settings are used (settings.conf values).

    Args:
        server_type (str): server type string which will be used
                            to search for host IP and port

    Returns:
        decorated function
    """
    from typhoon.api.common import get_server_configuration

    server_params = get_server_configuration(server_type)
    variable_entry = os.environ.get("TYPHOON-API", None)
    if variable_entry is not None:
        entry_dict = {}
        for entry in variable_entry.split(";"):
            if entry == "":
                continue
            key, val = entry.split("=")
            entry_dict[key.lower().strip("\"'")] = val.strip("\"'")
        #
        # An exception will be raised if
        # the system variable entry does not contain these keys
        #
        try:
            server_params = (entry_dict["host"], entry_dict[server_type+"_port"])
        except KeyError:
            # !! Using the file-specified host and port !!
            pass

    def to_decorate(stubfunc):
        def inner():
            return stubfunc(server_params)
        return inner

    return to_decorate


def init_stub(cls, server_params):
    stub = cls(server_params)
    server_ip, _ = server_params
    stub.connect()
    stub.connect_to_api_server()

    return stub


def determine_path(path):
    """
    Map relative filesystem path into absolute, if path is given in absolute
    path return it unchanged

    Arguments:
        * path - filesystem path

    Returns:
        absolute filesystem path
    """
    if os.path.isabs(path):
        return path
    else:
        (directory, filename) = os.path.split(
            os.path.abspath(os.path.realpath(path)))
        return os.path.join(directory, filename)
