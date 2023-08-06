#
# SCADA API handle module.
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

ROOT_COMPONENT_INDICATOR = "root"


class WidgetHandle(object):
    """
    SCADA widget identifier.
    """

    def __init__(self, item_type, item_fqid,
                 item_name, item_fqn, item_parent_id,
                 item_parent_fqn=None, **kwargs):
        """
        Initialize handle object that carry out info about entity on the
        server side.

        Args:
            item_type (str): Widget type constant.
            item_fqid (str): Widget identifier (Widget ID)
            item_fqn (str): Widget fully qualified name (Widget FQN)
            item_name (str): Widget regular name
            item_parent_id (str): Widget parent identifier (Parent ID)
            item_parent_fqn (str): Widget parent fully qualified name
                (Parent FQN)
        """
        super().__init__()

        self.item_type = item_type
        self.item_fqid = item_fqid
        self.item_name = item_name
        self.item_fqn = item_fqn

        self.item_parent_id = item_parent_id \
            if item_parent_id != ROOT_COMPONENT_INDICATOR else None
        self.item_parent_fqn = item_parent_fqn \
            if item_parent_fqn is not None else self._get_parent_fqn()

    def __repr__(self):
        """
        Custom repr representation.
        """
        return "WidgetHandle('{}', '{}', '{}', '{}', '{}', '{}')".format(
            self.item_type, self.item_fqid, self.item_name,
            self.item_fqn, self.item_parent_id, self.item_parent_fqn)

    def __hash__(self):
        return hash((self.item_type, self.item_fqid,
                     self.item_name, self.item_fqn,
                     self.item_parent_id, self.item_parent_fqn))

    def __eq__(self, other):
        return self.item_fqid == other.item_fqid \
            and self.item_type == other.item_type \
            and self.item_fqn == other.item_fqn \
            and self.item_name == other.item_name \
            and self.item_parent_id == other.item_parent_id \
            and self.item_parent_fqn == other.item_parent_fqn

    def __str__(self):
        """
        Custom string representation.
        """
        return "WidgetHandle(\n" \
               "    item_name='{}',\n" \
               "    item_type='{}',\n" \
               "    item_fqid='{}',\n" \
               "    item_fqn='{}',\n" \
               "    item_parent_id='{}',\n" \
               "    item_parent_fqn='{}'\n" \
               ")".format(self.item_name,
                          self.item_type,
                          self.item_fqid,
                          self.item_fqn,
                          self.item_parent_id,
                          self.item_parent_fqn)

    def _get_parent_fqn(self):
        """
        Returns parent FQN from Widget FQN
        Returns:
            Parent FQN (str, None): Return parent FQN or 'None' if widget is
                located on the root canvas
        """

        # split by using FQN delimiter
        parts = self.item_fqn.split(".")

        # we have at least one parent, remove last (child widget) FQN part
        if len(parts) > 1:
            return ".".join(parts[:-1])

        # we don't have a parent
        else:
            return None
