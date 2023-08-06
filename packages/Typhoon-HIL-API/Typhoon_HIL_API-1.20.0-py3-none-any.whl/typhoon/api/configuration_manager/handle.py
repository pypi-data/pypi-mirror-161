#
# Configuration Manager API handle module.
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


class ItemHandle(object):
    """
    Represents an object handle that the configuration manager API
    may return.
    """
    def __init__(self, item_type, item_fqid):
        """
        Initialize an object that the configuration manager API may return

        Args:
            item_type(str): Describes the type of the item - constant
            item_fqid(str): Item id.
        """
        super(ItemHandle, self).__init__()
        self.item_type = item_type
        self.item_fqid = item_fqid

    def __str__(self):
        return "{0} - ID: {1}".format(self.item_type, self.item_fqid)

    def __repr__(self):
        return "Item handle('{0}', '{1}')".format(self.item_type, self.item_fqid)

    def __hash__(self):
        return hash((self.item_type, self.item_fqid))

    def __eq__(self, other):
        return (self.item_type == other.item_type and
                self.item_fqid == other.item_fqid)
