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
import sys
import threading
from functools import lru_cache
from warnings import warn

from typhoon.api.configuration_manager.conf_objects import GeneratedResult
from typhoon.api.configuration_manager.constants import ITEM_HANDLE, UNIQUE_OBJECT_IDENTIFIER, \
    CONF_OBJECT_TYPE_GENERATED_RESULT
from typhoon.api.configuration_manager.exception import \
    ConfigurationManagerAPIException
from typhoon.api.configuration_manager.handle import ItemHandle
from typhoon.api.constants import CONFIGURATION_MANAGER_API_NAME
from typhoon.api.utils import check_environ_vars, init_stub

from typhoon.api.common import thread_safe, LoggingMixin, ClientStub

lock = threading.RLock()


class ClientAPIStub(LoggingMixin, ClientStub):

    def __init__(self, server_params, log_file="client.log"):
        super(ClientAPIStub, self).__init__(log_file)
        self.server_ip, self.server_port = server_params

    def __getattr__(self, name):
        try:
            attr = self.__getattribute__(name)
            return attr
        except Exception as ex:
            @thread_safe(lock)
            def wrapper(*args, **kwargs):
                msg = self.build_req_msg(name, **kwargs)
                self.log("{} message: {}".format(name, msg))
                self._req_socket.send_json(msg)
                response = self._req_socket.recv_json()

                result = response.get("result")
                error = response.get("error")
                warnings = response.get("warnings", [])

                self.log("{} status: {}".format(name, result))

                for warning in warnings:
                    if sys.version_info[0] < 3:
                        warn(warning.encode("utf-8"))
                    else:
                        warn(warning)

                if error:
                    err_msg = error["message"]
                    err_msg = err_msg.encode("utf-8") \
                        if sys.version_info[0] < 3 else err_msg

                    data = error.get("data", {})
                    internal_code = data.get("internal_error_code", None)
                    raise ConfigurationManagerAPIException(
                        err_msg, internal_code=internal_code)

                if isinstance(result, dict):
                    if ITEM_HANDLE in result:
                        # Configuration manager returned an object handle
                        # This object handle needs to be serialized
                        result = ItemHandle(**result)
                    elif UNIQUE_OBJECT_IDENTIFIER in result:
                        object_type = result[UNIQUE_OBJECT_IDENTIFIER]
                        if object_type == CONF_OBJECT_TYPE_GENERATED_RESULT:
                            result = GeneratedResult(**result)
                return result
            return wrapper

    def _ping_resp_handler(self, response):
        if self.server_port is None:
            # If server_port is None, it means following:
            #   1. server_port is not defined in settings.conf
            #   2. server_port is not provided as env variable
            #
            # In that case, we use port number provided by server through
            # announcement.
            port_data = response.get("result")[2]
            self.server_port = port_data[CONFIGURATION_MANAGER_API_NAME]\
                ["server_rep_port"]

    def connect(self):
        self._ping()

    @property
    def server_addr(self):
        return "tcp://{}:{}".format(self.server_ip, self.server_port)


@lru_cache(maxsize=None)
@check_environ_vars(server_type=CONFIGURATION_MANAGER_API_NAME)
def clstub(server_params):
    return init_stub(ClientAPIStub, server_params)
