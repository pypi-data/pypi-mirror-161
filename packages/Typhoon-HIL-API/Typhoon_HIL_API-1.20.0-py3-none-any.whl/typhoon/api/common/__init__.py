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

from __future__ import unicode_literals

from typhoon.api.constants import SCHEMATIC_API_NAME, HIL_API_NAME, \
    FIRMWARE_API_NAME, PV_GENERATOR_API_NAME, SCADA_API_NAME, \
    SERVICE_REGISTRY_HEADER, CONFIGURATION_MANAGER_API_NAME, ENV_API_NAME, \
    DEVICE_MANAGER_API_NAME
from typhoon.api.version import get_version
from typhoon.api.utils import get_user_folder_path, get_or_create_config

import configparser as ConfigParser
import json
import logging
import os
import subprocess
import sys

import zmq

__version__ = get_version()

def get_installation_dir_from_env():
    """
    Returns path to the Typhoon software installation directory
    (by reading specific environment variable).

    Returns:
        Path to the installation directory, empty string when
        installation can't be found.
    """
    #
    # Read value of TYPHOONPATH variable, normally contains one or more
    # paths (separated by ;) where various Typhoon SW installation is located.
    #
    typhoon_path = os.environ.get("TYPHOONPATH", "")
    if not typhoon_path:
        return ""

    parts = [part.strip() for part in typhoon_path.split(";")]
    if parts:
        # Return path to the last installed Typhoon SW location.
        return parts[0]
    else:
        return ""


def get_installation_dir_from_cfg():
    """
    Return installation dir as specified in configuration file.

    Returns:
        Path to software as specified in configuration, empty string
        if src_path configuration entry was not present.
    """
    try:
        sw_path = os.path.normpath(get_conf_value("path", "src_path"))
        return sw_path
    except ConfigParser.NoOptionError:
        return ""


def get_server_location():
    """
    Returns path to software, configuration is consulted first,
    then environment.

    Returns:
        ...
    """
    from_cfg = get_installation_dir_from_cfg()
    if from_cfg:
        return from_cfg

    from_env = get_installation_dir_from_env()
    if from_env:
        return from_env

    return ""


__author__ = 'Alen Suljkanovic'
JSON_RPC_VER = "2.0"
API_VER = "1.0"
DEFAULT_PING_TIMEOUT = 1000
DEFAULT_PING_RETRIES = 30
DEBUG = "DEBUG"
INFO = "INFO"
ERROR = "ERROR"
BAT_TEMPLATE = """
@echo off
start {cmd}
""".strip()


def _handle_to_dict(handle):
    from typhoon.api.schematic_editor.const import ITEM_HANDLE
    from typhoon.api.scada.const import WIDGET_HANDLE
    from typhoon.api.schematic_editor.handle import ItemHandle
    from typhoon.api.scada.handle import WidgetHandle

    d = handle.__dict__
    if isinstance(handle, ItemHandle):
        d[ITEM_HANDLE] = True
    elif isinstance(handle, WidgetHandle):
        d[WIDGET_HANDLE] = True

    return d


def serialize_obj(obj):
    from typhoon.api.schematic_editor import ItemHandle
    from typhoon.api.scada.handle import WidgetHandle
    from pathlib import Path

    if isinstance(obj, (ItemHandle, WidgetHandle)):
        return _handle_to_dict(obj)

    elif isinstance(obj, list):
        return [serialize_obj(o) for o in obj]

    elif isinstance(obj, Path):
        return str(obj)

    return obj


def thread_safe(lock):
    """Decorator that makes given function thread safe using RLock mutex

    Args:
        lock - RLock instance that will be used for locking decorated function.
    """

    # when decorator have arguments inner decorator is needed
    def inner_decorator(func):

        def func_wrapper(*args, **kwargs):
            # lock function call
            with lock:
                return func(*args, **kwargs)

        return func_wrapper

    return inner_decorator


def build_rep_msg(msg_id, method_name, result=None, error=None, warnings=None):
    """

    Args:
        msg_id:
        method_name:
        result:
        error:
        warnings:

    Returns:
         JSON
    """
    message = {
        "jsonrpc": JSON_RPC_VER,
        "method": method_name,
        "id": msg_id
    }

    if result and error:
        raise Exception("Invalid response message! Response message cannot"
                        "contain both 'result' and 'error' objects.")

    if error:
        message["error"] = error
    else:
        message["result"] = result

    if warnings:
        message["warnings"] = warnings

    return json.dumps(message, default=serialize_obj)


@get_or_create_config
def get_settings_conf_path():
    return os.path.join(get_user_folder_path(),
                        "typhoon-api",
                        get_version(), "settings.conf")


def get_server_configuration(server_type):
    """
    Reads the settings.conf file and
    depending on the server type argument
    returns the API server's IP address and port.


    Args:
        server_type (str): string value which is used to find the server's
                           section when parsing the settings file.

    Returns:
        server_ip (str), port (int)
    """
    supported_server_types = (SCHEMATIC_API_NAME, HIL_API_NAME,
                              FIRMWARE_API_NAME, PV_GENERATOR_API_NAME,
                              SCADA_API_NAME, CONFIGURATION_MANAGER_API_NAME,
                              ENV_API_NAME, DEVICE_MANAGER_API_NAME,)

    if server_type not in supported_server_types:
        raise AttributeError("The provided server type '{}' "
                             "is not a valid value."
                             "Currently supported server types: {}".
                             format(server_type, supported_server_types))
    #
    # Returns the path to the settings.conf file
    #
    server_ip = "localhost"

    try:
        server_ip = get_conf_value("server_settings", "server_ip").strip("\"'")
        port = get_conf_value(server_type, "server_port")
    except Exception:

        # # If the port section was not found
        # if port is None:
        #     if server_type == "sch_api":
        #         port = DEFAULT_SCH_SERVER_PORT
        #     elif server_type == "hil_api":
        #         port = DEFAULT_HIL_SERVER_PORT
        #     elif server_type == "fw_api":
        #         port = DEFAULT_FW_MANAGER_SERVER_PORT
        #     elif server_type == "pv_gen_api":
        #         port = DEFAULT_PV_GENERATOR_SERVER_PORT
        #     print("Client API - settings.conf file is corrupted. "
        #           "Attempting to connect to {}:{}".format(server_ip, port))
        port = None

    return server_ip, port


def get_conf_value(section, key):
    """Get value from settings.conf

    Args:
        section: section name
        key: value identifier
    """

    settings_path = get_settings_conf_path()

    if sys.version_info[0] < 3:
        config_parser = ConfigParser.SafeConfigParser()
    else:
        config_parser = ConfigParser.ConfigParser()

    config_parser.read(settings_path)

    return config_parser.get(section, key)


_loggers = {}


def get_logger(logger_name, file_name):
    """Return logger with given name and file handler name."""
    if file_name in _loggers:
        return _loggers[file_name]

    from logging import handlers

    # create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    # create file handler which logs even debug messages
    fh = handlers.RotatingFileHandler(file_name, encoding="utf-8",
                                      backupCount=3, maxBytes=5*1024*1024)
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    _loggers[file_name] = logger

    return logger


def start_server():
    """
    Starts a server.
    """
    server_path = get_server_location()

    err_msg = "Can't start Typhoon software because path to it is not valid" \
              " or installation is corrupted.\n Please check if Typhoon " \
              "software is installed, TYPHOONPATH environment variable is " \
              "present and points to installation \n and/or if settings.conf" \
              " src_path entry is present and its value is valid."

    if not server_path or not os.path.exists(server_path):
        raise Exception(err_msg)

    source_file = os.path.join(server_path, "typhoon_hil.py")
    exe_file = os.path.join(server_path, "typhoon_hil.exe")

    if os.path.exists(source_file):
        # Handle server from source.
        args = "-hapi"
        #
        # When running with server from source, get python for running of
        # server from settings.conf.
        #
        try:
            python_path = get_conf_value("path", "python_path")
        except ConfigParser.NoOptionError:
            raise Exception("Can't start Typhoon server, python_path must be"
                            " defined in settings.conf under 'path' section")
        python_exe = os.path.join(python_path)
    elif os.path.exists(exe_file):
        args = "-hapi"
    else:
        # No sw was found to run (both in source form and in installed form).
        print(err_msg)
        return

    # Important note: All logger calls above were removed due to trac #2345
    # typhoon_hil.exe would somehow open any client "RotatingFileHandler" file
    # and prevent it from being rotated (windows access denied)
    if os.path.exists(exe_file):
        print("Starting from installation...")
        subprocess.Popen([exe_file, args])
    else:
        subprocess.Popen([python_exe, source_file, args])


class LoggingMixin(object):
    """Mixin class for all stubs that need logging."""
    def __init__(self, log_file):
        super(LoggingMixin, self).__init__()
        try:
            self._logging_on = get_conf_value("debug", "logging_on") == "True"
        except ConfigParser.NoSectionError:
            self._logging_on = False

        if self._logging_on:
            self.logger = get_logger(__name__+".debuglogs", log_file)

    def log(self, msg, severity=DEBUG, level=0):
        """Logs message info a file, if the debug mode is activated."""
        if self._logging_on:

            callables = {
                INFO: lambda m: self.logger.log(level, m),
                DEBUG: self.logger.debug,
                ERROR: self.logger.error
            }

            fnc = callables[severity]
            fnc(msg)


class ConnectionMixin(object):
    """
    Class used by API clients for remote server configuration
    """
    def __init__(self):
        super(ConnectionMixin, self).__init__()
        self.server_ip = "localhost"
        self.server_port = None
        self.connected = False
        self.config_set_by_api = False

    def set_server_config(self, ip=None, port=None):
        """
        Sets the remote server IP address and port.
        Args:
            ip: (str) API server IP address
            port: (int) API server port

        Returns:
            bool - un/successful operation
        """
        if ip is not None:
            self.server_ip = ip
        if port is not None:
            self.server_port = port
        if ip is None and port is None:
            return False
        self.config_set_by_api = True
        return True


class ClientStub(object):
    """Client stub class."""

    # message ID
    ID = 0

    def __init__(self):
        super(ClientStub, self).__init__()
        # ZMQ context
        self._context = zmq.Context()

        # Request socket (sends requests to server)
        self._req_socket = self._context.socket(zmq.REQ)
        # Subscribe socket (used for server auto-discovery)
        self._sub_ann_socket = self._context.socket(zmq.SUB)

        # Ping request timeout
        try:
            self._ping_timeout = int(get_conf_value("server_settings",
                                                    "ping_timeout"))
        except Exception:
            self._ping_timeout = DEFAULT_PING_TIMEOUT

        # How many times should client try to ping server
        try:
            self._ping_retries = int(get_conf_value("server_settings",
                                                    "ping_retries"))
        except Exception:
            self._ping_retries = DEFAULT_PING_RETRIES

    @property
    def _id(self):
        ClientStub.ID += 1
        return ClientStub.ID

    def build_req_msg(self, method_name, **params):
        """Builds a JSON-RCP request message that is being sent to the server

        Args:
            method_name (str): name of the method on the server that will be
                called
            params (dict): method arguments
        Returns:
            dict: JSON-like dict object
        """

        message = {
            "api": API_VER,
            "jsonrpc": JSON_RPC_VER,
            "method": method_name,
            "params": {k: serialize_obj(v) for k, v in params.items()},
            "id": self._id
        }

        return message

    def connect_to_api_server(self):
        """Connects to servers response port."""
        self._req_socket.connect(self.server_addr)
        self.connected = True

    def _ping_resp_handler(self, response):
        """Handles the response from the server if the ping is successful"""
        pass

    def _wait_for_server(self, request_retries, timeout):
        """Waits for server to start and publish message that it's ready
        to receive messages.

        Client is attempting to reach server `request_retries` times, with a
        given `timeout` between attempts.
        """
        socket = self._sub_ann_socket

        start_port, end_port = get_announcement_range()
        offset = end_port - start_port + 1

        for i in range(offset):
            port = start_port + i
            socket.connect("tcp://{}:{}".format(self.server_ip, port))

        socket.setsockopt_string(zmq.SUBSCRIBE, "")
        socket.setsockopt(zmq.LINGER, 0)

        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)

        connected = False

        while request_retries != 0:

            socks = dict(poller.poll(timeout))
            if socks.get(socket) == zmq.POLLIN:
                response = socket.recv_json()

                if not response:
                    break

                header, _, _ = response.get("result")

                # Continue discovery if a received message is not from Typhoon
                # HIL Control Center.
                if header != SERVICE_REGISTRY_HEADER:
                    continue

                connected = True
                self._ping_resp_handler(response)
                break
            else:
                request_retries -= 1
                if request_retries == 0:
                    break

        # If discovery is successful then disconnect and close socket
        if connected:
            poller.unregister(socket)
            socket.unsubscribe("")
            for i in range(offset):
                port = start_port + i
                socket.disconnect("tcp://{}:{}".format(self.server_ip, port))
            socket.close()

        return connected

    def _ping(self, start=True, request_retries=None, request_timeout=None):
        """Pings server to check if it's running

        If server is not responding, and the number of retries is reached,
        client will try to start the server is option is enabled.
        """
        if not request_retries:
            request_retries = self._ping_retries

        if not request_timeout:
            request_timeout = self._ping_timeout

        connected = self._wait_for_server(request_retries, request_timeout)

        #
        # If server does not respond, then start it if `start` is set to True.
        #
        if not connected and start:
            if self.server_ip in {"localhost", "127.0.0.1"}:
                # Start a server thread in HEADLESS_MODE...
                start_server()

                # Wait for server to start, and then connect.
                # self._reset_ann_socket()
                connected = self._wait_for_server(request_retries,
                                                  request_timeout)

            if not connected:
                self.connected = False
                raise Exception("No response from the remote "
                                "server at {}. Please check "
                                "your settings.conf file."
                                .format(self.server_ip))

        return connected

    def reconnect(self):
        """Reconnects sockets with THCC."""
        print("Reconnecting...")
        self._req_socket.setsockopt(zmq.LINGER, 0)
        self._req_socket.close()

        self.server_ip = "localhost"
        self.server_port = None

        # Reinstantiate sockets
        self._req_socket = self._context.socket(zmq.REQ)
        self._sub_ann_socket = self._context.socket(zmq.SUB)

        # By calling _ping, we ensure that servers heartbeat is caught and
        # sockets are bind to proper server ports.
        self._ping()
        self.connect_to_api_server()


def get_announcement_range():
    in_str = get_conf_value("server_settings",
                            "announcement_port_pub_range")
    start, end = in_str.split("-")
    return int(start), int(end)