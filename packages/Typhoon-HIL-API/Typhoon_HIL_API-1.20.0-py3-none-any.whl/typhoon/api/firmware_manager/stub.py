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
from __future__ import unicode_literals, print_function
from typhoon.api.common import thread_safe, LoggingMixin, ClientStub
import threading
import sys
from warnings import warn

from typhoon.api.constants import FIRMWARE_API_NAME
from typhoon.api.utils import check_environ_vars, init_stub, lru_cache

lock = threading.RLock()


class ClientAPIStub(LoggingMixin, ClientStub):

    def __init__(self, server_params, log_file="client.log"):
        super(ClientAPIStub, self).__init__(log_file=log_file)
        self.server_ip, self.server_port = server_params

    def connect(self):
        self._ping()

    def _ping_resp_handler(self, response):
        if self.server_port is None:
            # If server_port is None, it means following:
            #   1. server_port is not defined in settings.conf
            #   2. server_port is not provided as env variable
            #
            # In that case, we use port number provided by server through
            # announcement.
            port_data = response.get("result")[2]
            ports = port_data[FIRMWARE_API_NAME]
            self.server_port = ports["server_rep_port"]

    @property
    def server_addr(self):
        return "tcp://{}:{}".format(self.server_ip, self.server_port)

    def __getattr__(self, name):
        # This method will return the method with a given name if it exists.
        # If the method with a given name doesn't exist, a "wrapper" method
        # will be returned. The main job if the "wrapper" function is to make
        # a remote call to the server, and to return the response.
        try:
            attr = self.__getattribute__(name)
            return attr
        except:
            # Dynamically create a function, and make a remote call.
            @thread_safe(lock)
            def wrapper(*args, **kwargs):

                msg = self.build_req_msg(name, **kwargs)

                self.log("{} message: {}".format(name, msg))

                # Send request to the server
                self._req_socket.send_json(msg)

                # Wait and process the response
                response = self._req_socket.recv_json()

                result = response.get("result", None)
                warnings = response.get("warnings", [])
                error = response.get("error", None)

                self.log("{} result: {}".format(name, result))

                # Print warnings...
                for warning in warnings:
                    if self.raise_exceptions:
                        f_warning = warn
                    else:
                        f_warning = print

                    if sys.version_info[0] < 3:
                        f_warning(warning.encode("utf-8"))
                    else:
                        f_warning(warning)

                if error:
                    err_msg = error["message"]
                    err_msg = err_msg.encode("utf-8") \
                        if sys.version_info[0] < 3 else err_msg

                    if self.raise_exceptions is False:
                        print(err_msg)
                        # Set result to False to ensure backward compatibility
                        result = False
                    else:
                        raise Exception(err_msg)

                return result

            return wrapper


_CL_STUB = None


@lru_cache(maxsize=None)
@check_environ_vars(server_type=FIRMWARE_API_NAME)
def clstub(server_params):
    return init_stub(ClientAPIStub, server_params)
