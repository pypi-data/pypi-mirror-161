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
class SignalStimulusHandle(object):
    """
    Represents HIL API item in the context of HIL MODEL.
    """
    def __init__(self, item_id, **kwargs):
        """
        Initialize signal stimulus item object.

        Args:
            item_id (str): Item id.
        """
        super(SignalStimulusHandle, self).__init__()

        self.id = str(item_id)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


SIGNAL_STIMULUS_HANDLE = "SIGNAL_STIMULUS_HANDLE"