#
# Configuration Manager API
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

from typhoon.api.configuration_manager.constants \
    import UNIQUE_OBJECT_IDENTIFIER


class ConfObject(object):
    def generate_message_dict(self):
        raise NotImplementedError()


class GeneratedResult(ConfObject):
    def __init__(self, *args, **kwargs):
        super(GeneratedResult, self).__init__()
        self.generated_schematic_path = kwargs["generated_schematic_path"]

    def __str__(self):
        return "GeneratedResult('{0}')".format(self.generated_schematic_path)

    def __repr__(self):
        return "GeneratedResult('{0}')".format(self.generated_schematic_path)

    def __hash__(self):
        return hash(self.generated_schematic_path)

    def __eq__(self, other):
        return self.generated_schematic_path == other.generated_schematic_path

    def generate_message_dict(self):
        d = self.__dict__
        d[UNIQUE_OBJECT_IDENTIFIER] = "GeneratedResult"
        return d
