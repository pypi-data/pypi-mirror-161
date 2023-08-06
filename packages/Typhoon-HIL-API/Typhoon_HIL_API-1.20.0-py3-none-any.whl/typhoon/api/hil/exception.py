#
# HIL API exceptions module.
#
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


class HILAPIException(Exception):
    """
    Exception raised in some of HIL API functions in case some error occurs
    """
    def __init__(self, *args, **kwargs):
        super(HILAPIException, self).__init__(*args)
        self.internal_code = None

        # Read the value of internal code if provided as keywoard argument.
        if "internal_code" in kwargs:
            self.internal_code = kwargs["internal_code"]

