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
from typhoon.api.configuration_manager.base import ConfigurationManagerAPIBase
from typhoon.api.configuration_manager.stub import clstub
from typhoon.api.utils import determine_path


# noinspection PyMethodMayBeStatic
class ConfigurationManagerAPI(ConfigurationManagerAPIBase):

    def save_config(self, config_handle, save_path):
        return clstub().save_config(config_handle=config_handle,
                                    save_path=determine_path(save_path))

    def create_config(self, config_name):
        return clstub().create_config(config_name=config_name)

    def generate(self, project_handle, config_handle, out_dir="",
                 file_name="", standalone_model=True):
        # -- Only the output directory needs to be determined
        # -- The file name should only be a file name, and not contain any
        # folder parts
        out_dir_intermediate = determine_path(out_dir)
        return clstub().generate(project_handle=project_handle,
                                 config_handle=config_handle,
                                 out_dir=out_dir_intermediate,
                                 file_name=file_name,
                                 standalone_model=standalone_model)

    def load_config(self, config_path):
        return clstub().load_config(config_path=determine_path(config_path))

    def load_project(self, project_path):
        return clstub().load_project(project_path=determine_path(project_path))

    def make_pick(self, variant_name, option_name,
                  option_configuration=None):
        return clstub().make_pick(variant_name=variant_name,
                                  option_name=option_name,
                                  option_configuration=option_configuration)

    def picks(self, config_handle, pick_handles):
        if not (isinstance(pick_handles, (list, tuple)) and \
                all(isinstance(i, dict) for i in pick_handles)):
            raise TypeError(
                "Function picks() expects ``pick_handles`` argument"
                " to be a list (or tuple) of Pick objects."
            )
        clstub().picks(config_handle=config_handle, pick_handles=pick_handles)

    def get_name(self, item_handle):
        return clstub().get_name(item_handle=item_handle)

    def get_project_variants(self, project_handle):
        return clstub().get_project_variants(project_handle=project_handle)

    def get_options(self, project_handle, variant_handle):
        return clstub().get_name(project_handle=project_handle,
                                 variant_handle=variant_handle)
