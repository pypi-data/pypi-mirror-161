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

import sys
import threading
from typhoon.api.common import thread_safe, LoggingMixin, ConnectionMixin, \
    ClientStub
from warnings import warn

from typhoon.api.constants import SCADA_API_NAME
from typhoon.api.scada.exception import ScadaAPIException
from typhoon.api.scada.handle import WidgetHandle
from typhoon.api.scada.const import WIDGET_HANDLE
from typhoon.api.utils import check_environ_vars, init_stub, lru_cache

lock = threading.RLock()


class ClientAPIStub(LoggingMixin, ClientStub, ConnectionMixin):

    def __init__(self, server_params, log_file="client.log"):
        super(ClientAPIStub, self).__init__(log_file=log_file)
        self.server_ip, self.server_port = server_params

        # Switch for raising exceptions and warnings instead of just printing
        self.raise_exceptions = False

    @property
    def server_addr(self):
        return "tcp://{}:{}".format(self.server_ip, self.server_port)

    def _ping_resp_handler(self, response):
        if self.server_port is None:
            # If server_port is None, it means following:
            #   1. server_port is not defined in settings.conf
            #   2. server_port is not provided as env variable
            #
            # In that case, we use port number provided by server through
            # announcement.
            port_data = response.get("result")[2]
            ports = port_data["scada_api"]
            self.server_port = ports["server_rep_port"]

    def connect(self):
        self._ping()

    def __getattr__(self, name):
        try:
            attr = self.__getattribute__(name)
            return attr
        except:

            @thread_safe(lock)
            def wrapper(*args, **kwargs):
                #
                # Build request to call function on server side
                #
                msg = self.build_req_msg(name, **kwargs)

                self.log("{} message: {}".format(name, msg))

                self._req_socket.send_json(msg)

                #
                # Get response
                #
                response = self._req_socket.recv_json()

                result = response.get("result")
                error = response.get("error")
                warnings = response.get("warnings", [])

                self.log("{} status: {}".format(name, result))

                #
                # Warnings
                #
                for warning in warnings:
                    if self.raise_exceptions:
                        f_warning = warn
                    else:
                        f_warning = print

                    if sys.version_info[0] < 3:
                        f_warning(warning.encode("utf-8"))
                    else:
                        f_warning(warning)

                #
                # Errors
                #
                if error:
                    err_msg = error["message"]
                    err_msg = err_msg.encode("utf-8") \
                        if sys.version_info[0] < 3 else err_msg

                    raise ScadaAPIException(err_msg)

                #
                # Return value
                #

                # some function return None (by default)
                if result is None and error is None:
                    result = None

                # function returns single WidgetHandle object
                elif isinstance(result, dict) and WIDGET_HANDLE in result:
                    # If a function returns WidgetHandle object, server will
                    # serialize into a dictionary. So, now we need to create an
                    # WidgetHandle instance from that dictionary and return it to
                    # the client.
                    result = WidgetHandle(**result)

                # function returns multiple WidgetHandle objects
                elif isinstance(result, list):
                    result = [WidgetHandle(**res)
                              if (isinstance(res, dict) and WIDGET_HANDLE in res)
                              else res for res in result]

                # function returns something else
                return result

            return wrapper


@lru_cache(maxsize=None)
@check_environ_vars(server_type=SCADA_API_NAME)
def clstub(server_params):
    return init_stub(ClientAPIStub, server_params)
