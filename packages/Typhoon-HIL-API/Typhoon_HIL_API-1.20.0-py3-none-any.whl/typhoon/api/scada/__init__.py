#
# SCADA API
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

import os

from typhoon.api.scada.stub import clstub

__all__ = ["panel"]


class ScadaAPI(object):
    """
    SCADA API (Application Programming Interface) allows interfacing to the
    underlying HIL SCADA model.
    """

    def __init__(self):
        super(ScadaAPI, self).__init__()

    def add_library_path(self, library_path, add_subdirs=False, persist=False):
        """
        Add path to library search path. Added path will be treated as
        temporarily path (``persist=False``). In case you want to save it,
        set ``persist=True``.

        Args:
            library_path(str): Directory path where library files are located.
            add_subdirs(bool): Search in subdirectories for library files.
            persist(bool): Make library path change permanent.

        Returns:
            None

        Availability:
            * standalone scripts

        **Example:**

        .. literalinclude:: scada_api_examples/add_library_path.example
           :language: python
           :lines: 2-
        """

        return clstub().add_library_path(library_path=library_path,
                                         add_subdirs=add_subdirs,
                                         persist=persist)

    def create_widget(self, widget_type, parent=None,
                      name=None, position=None, link_to_model_comp=None):
        """
        Creates new widget using provided widget type inside the group like
        widget specified by ``parent``. If ``parent`` is not
        specified main Panel's canvas will be used as a parent.

        Args:
            widget_type (str): type of widget that need to be created.
                The list of all widget type names can be found in the
                ``typhoon.api.scada.const`` module or listed in the section
                `SCADA API constants`_
            parent (WidgetHandle): parent group like widget where this widget
                need to be  created and added.
            name (str): name of the widget.
            position (list or tuple): list[x, y] coordinates where new widget
                need to be positioned after it is created.
            link_to_model_comp (str): Fully qualified name (FQN) of Schematic
                Model component that we want to connect to created
                Library Widget.

                .. note::
                    Specifying this argument only has effect if a Library
                    widget is created and that Library widget is configured to
                    be connected to Model component.

        Returns:
            Widget handle (WidgetHandle): handle to the created widget.

        Raises:
            ScadaAPIException: in case any of arguments is invalid.
            ScadaAPIException: in case Panel is not specified.
            ScadaAPIException: in case parent widget with given id cannot be
                found in loaded Panel.
            ScadaAPIException: in case widget cannot be created for
                some reason

        Availability:
            * standalone scripts

        **Example:**

        .. literalinclude:: scada_api_examples/create_widget.example
           :language: python
           :lines: 2-
        """

        return clstub().create_widget(widget_type=widget_type,
                                      parent=parent,
                                      name=name,
                                      position=position,
                                      link_to_model_comp=link_to_model_comp)

    def create_new_panel(self):
        """
        Creates new empty Panel in memory.

        .. note::
            In case Panel is created and not loaded with ``load_panel()``, for
            first time it can be only saved by calling ``save_panel_as()``
            function. After Panel is saved with ``save_panel_as()`` it can be
            saved later by using regular ``save_panel()`` function.

        Returns:
            None

        Availability:
            * standalone scripts

        **Example:**

        .. literalinclude:: scada_api_examples/create_panel.example
           :language: python
           :lines: 2-
        """

        return clstub().create_new_panel()

    def create_new_library_panel(self, library_name, library_description=""):
        """
        Creates new empty Library Panel in memory.

        Args:
            library_name (str): name of the Widget Library
            library_description (str): short description

        .. note::
            In case Library Panel is created and not loaded with
            ``load_library_panel()`` for first time it can be only saved by
            calling ``save_panel_as()`` function.
            After Panel is saved with ``save_panel_as()`` it can be saved later
            with regular ``save_panel()`` function.

        Returns:
            None

        Raises:
            ScadaAPIException: in case any of arguments are invalid

        Availability:
            * standalone scripts

        **Example:**

        .. literalinclude:: scada_api_examples/create_library_panel.example
           :language: python
           :lines: 2-
        """

        return clstub().create_new_library_panel(
            library_name=library_name,
            library_description=library_description)

    def copy(self, src_handle, dst_handle=None, name=None, position=None):
        """
        Copies widget identified  by ``src_handle`` to Group like widget
            identified by ``dst_handle``.

        .. note::
            Source widget and all its child widgets (in case source widget is
            Group like widget) will be copied to destination widget.

        Args:
            src_handle (WidgetHandle): Handle of widget that need to be copied.
            dst_handle (WidgetHandle): Handle to Group like widget where source
                widget need to be copied.

                .. note::
                    In case ``dst_handle`` is None, source widget will be
                    copied to main (root) Panel's canvas.

            name (str): new name of copied widget.
            position (list or tuple): list[x, y] coordinates where new copied
                widget need to be positioned.

        Returns:
            List of copied widgets (List[WidgetHandle]): flatten list that
                contains handles of all copied widgets.

        Raises:
            ScadaAPIException: in case any of arguments is invalid.
            ScadaAPIException: in case destination widget is not Group like
                widget.
            ScadaAPIException: in case Panel is not specified.
            ScadaAPIException: in case source or destination widget with
                given id cannot be found in loaded Panel.

        Availability:
            * standalone scripts

        **Example:**

        .. literalinclude:: scada_api_examples/copy.example
           :language: python
           :lines: 2-
        """

        return clstub().copy(src_handle=src_handle,
                             dst_handle=dst_handle,
                             name=name,
                             position=position)

    def delete_widget(self, widget_handle):
        """
        Deletes widget from the loaded or created Panel.

        Args:
            widget_handle (WidgetHandle): Handle of the widget that need to
                be deleted.

        Returns:
            None

        Raises:
            ScadaAPIException: in case ``widget_handle`` argument is invalid.
            ScadaAPIException: in case Panel is not specified.
            ScadaAPIException: in case widget with given id cannot be found in
                loaded Panel.

        Availability:
            * standalone scripts

        **Example:**

        .. literalinclude:: scada_api_examples/delete.example
           :language: python
           :lines: 2-
        """

        return clstub().delete_widget(widget_handle=widget_handle)

    def execute_action(self, widget_handle, action_name, **params):
        """
        Executes an action of a widget, if the widget is found
        by widget handle on the panel.

        .. note::
            This function can only be used in HIL SCADA.
            For a detailed list of executable actions for each widget,
            please consult the :doc:`Available Widget Actions </widget_actions>`
            documentation.

        Args:
            widget_handle (WidgetHandle): widget handle object
            action_name (str): name of the action which needs to be executed
                               (all action_name constants are listed in the
                               ``typhoon.api.scada.const`` module or listed in
                               the section `SCADA API constants`_)

            params (dict): optional parameters of the action

        Returns:
            None

        Raises:
            ScadaAPIException: in case `widget_handle` or `action_name`
                arguments are invalid
            ScadaAPIException: in case the widget doesn't have the passed
                `action_name` action
            ScadaAPIException: in case Panel is not specified
            ScadaAPIException: in case widget with given id cannot be found
                in loaded Panel

        Availability:
            * macro scripts
            * signal monitoring expressions

        **Example:**

        .. literalinclude:: scada_api_examples/execute_action.example
           :language: python
        """

        return clstub().execute_action(widget_handle=widget_handle,
                                       action_name=action_name, **params)

    def reload_libraries(self):
        """
        Reload all libraries which are found in library search path.

        .. note::
            After libraries are reloaded and there is the opened Panel that has
            a Library widgets, it is recommended to reopen Panel again
            in order to load up to date Library widgets.

        Returns:
            None

        Raises:
            ScadaAPIException: when there is error during library reloading.

        Availability:
            * standalone scripts

        **Example:**

        .. literalinclude:: scada_api_examples/add_library_path.example
           :language: python
           :lines: 2-
        """

        return clstub().reload_libraries()

    def remove_library_path(self, library_path, persist=False):
        """
        Remove path from library search path.

        Args:
            library_path(str): Library path to remove.
            persist(bool): Make library path change permanent after library
                path is removed.

        Returns:
            None

        Availability:
            * standalone scripts

        Raises:
            ScadaAPIException: when given path cannot be found in
                library registry search path.

        **Example:**

        .. literalinclude:: scada_api_examples/remove_library_path.example
           :language: python
           :lines: 2-
        """

        return clstub().remove_library_path(library_path=library_path,
                                            persist=persist)

    def load_panel(self, panel_file):
        """
        Load the provided HIL SCADA Panel (.cus) file.

        Args:
            panel_file (str): full path to the HIL SCADA Panel (.cus) file.

        Returns:
            None

        Raises:
            ScadaAPIException: In case `panel_file` argument is invalid.
            ScadaAPIException: In case provided Panel file cannot be opened.

        Availability:
            * standalone scripts

        **Example:**

        .. literalinclude:: scada_api_examples/load.example
           :language: python
           :lines: 2-
        """

        return clstub().load_panel(panel_file=os.path.abspath(panel_file))

    def load_library_panel(self, library_panel_file):
        """
        Load provided HIL SCADA Widget Library (.wlib) file.

        Args:
            library_panel_file (str): full path to the HIL SCADA
                Widget Library (.wlib) file.

        Returns:
            None

        Raises:
            ScadaAPIException: In case `library_panel_file` argument is
                invalid.
            ScadaAPIException: in case provided Library Panel file cannot
                be opened.

        Availability:
            * standalone scripts

        **Example:**

        .. literalinclude:: scada_api_examples/load_lib.example
           :language: python
           :lines: 2-
        """

        return clstub().load_library_panel(
            library_panel_file=os.path.abspath(library_panel_file))

    def save_panel(self):
        """
        Save currently opened Panel to the same Panel file.

        Returns:
            None

        Raises:
            ScadaAPIException: In case the Panel file is not opened.
            ScadaAPIException: In case the opened Panel cannot be saved.

        Availability:
            * standalone scripts

        **Example:**

        .. literalinclude:: scada_api_examples/save.example
           :language: python
           :lines: 2-
        """
        return clstub().save_panel()

    def save_panel_as(self, save_to):
        """
        Save the currently opened Panel to a new Panel file.

        Args:
            save_to (str): full path where opened Panel need to be saved.

        Returns:
            None

        Raises:
            ScadaAPIException: In case the Panel file is not opened.
            ScadaAPIException: In case `save_to` argument is invalid.
            ScadaAPIException: In case the opened Panel cannot be saved.

        Availability:
            * standalone scripts

        **Example:**

        .. literalinclude:: scada_api_examples/save_as.example
           :language: python
           :lines: 2-
        """
        return clstub().save_panel_as(save_to=os.path.abspath(save_to))

    def set_property_value(self, widget_handle, prop_name, prop_value):
        """
        Set a new value for the widget property.

        Args:
            widget_handle (WidgetHandle): The widget handle used as a widget
                identifier.
            prop_name (str): The name of property that you want to change.
                The list of all property names can be found in the
                ``typhoon.api.scada.const`` module or listed in the section
                `SCADA API constants`_


                .. note::
                    Not all widget properties can be changed by SCADA API.
                    For detailed information which properties can be changed
                    for a specific widget, please consult
                    :doc:`Available Widget Properties </widget_prop>` section.

            prop_value (object): A new property value that need to be set.

                .. note::
                    Type of value that need to be set depends of which property
                    is being changed. More details can be found in the
                    :doc:`Available Widget Properties </widget_prop>` section.

        Returns:
            None

        Raises:
            ScadaAPIException: In case the Panel file is not opened.
            ScadaAPIException: In case any of arguments is invalid.
            ScadaAPIException: In case the widget identified by
                ``widget_handle`` cannot be found in opened Panel.
            ScadaAPIException: In case widget doesn't have property with
                given ``prop_name``.
            ScadaAPIException: In case property is read only and cannot
                be changed.

        Availability:
            * standalone scripts
            * macro scripts
            * signal monitoring expressions

        **Example:**

        .. literalinclude:: scada_api_examples/change_prop.example
           :language: python
           :lines: 2-
        """
        return clstub().set_property_value(widget_handle=widget_handle,
                                           prop_name=prop_name,
                                           prop_value=prop_value)

    def get_property_value(self, widget_handle, prop_name):
        """
        Returns the value of a given property for the given widget handle.

        Args:
            widget_handle (WidgetHandle): The widget handle used as a widget
                identifier.
            prop_name (str): The name of a property.
                The list of all property names can be found in
                ``typhoon.api.scada.const`` module or listed in the section
                `SCADA API constants`_

                .. note::
                    Not all widget properties can be changed by SCADA API.
                    For detailed information which properties can be changed
                    for a specific widget, please consult
                    :doc:`Available Widget Properties </widget_prop>` section.

        Returns:
            property value (object): value can be arbitrary type
                depending of the type of widget and property. More details can
                be found in the
                :doc:`Available Widget Properties </widget_prop>` section.
        Raises:
            ScadaAPIException: In case any of arguments is invalid.
            ScadaAPIException: In case the widget does not have the property
                with given the ``prop_name``.
            ScadaAPIException: In case property is write only and cannot
                be read.
            ScadaAPIException: In case the Panel is not specified.
            ScadaAPIException: In case the widget identified by the
                ``widget_handle`` cannot be found in the opened Panel.

        Availability:
            * standalone scripts
            * macro scripts
            * signal monitoring expressions

        **Example:**

        .. literalinclude:: scada_api_examples/get_prop.example
           :language: python
           :lines: 2-
        """

        return clstub().get_property_value(widget_handle=widget_handle,
                                           prop_name=prop_name)

    def get_widget_by_id(self, widget_id):
        """
        Returns the widget handle for the widget with a given widget ID.

        Args:
            widget_id (str): Widget ID. Widget ID can be acquired from
                WidgetHandle ``item_fqid`` attribute
                (widget_handle_object.item_fqid).

        Returns:
            handle to widget (WidgetHandle): A handle to the widget with the
                given ``widget_id`` that can be used as a widget identifier.

        Raises:
            ScadaAPIException: In case the Panel file is not opened.
            ScadaAPIException: In case the ``widget_id`` argument is invalid.
            ScadaAPIException: In case the widget with the given id cannot be
                found in the loaded Panel.

        Availability:
            * standalone scripts
            * macro scripts
            * signal monitoring expressions

        **Example:**

        .. literalinclude:: scada_api_examples/get_widget.example
           :language: python
           :lines: 2-
        """

        return clstub().get_widget_by_id(widget_id=widget_id)

    def get_widget_by_fqn(self, widget_fqn, parent=None):
        """
        Returns widget handle for widget with given widget fully qualified
        name (FQN).

        Args:
            widget_fqn (str): Widget fully qualified name
            parent (WidgetHandle): parent group like widget where widget with
                given `widget_fqn` will be searched. In case `parent` is
                specified, given `widget_fqn` will be used as relative fully
                qualified name (relative from given parent).

        Returns:
            WidgetHandle: handle to widget with given widget FQN

        Raises:
            ScadaAPIException: In case any argument is invalid
            ScadaAPIException: in case widget with given
                fully qualified name cannot be found in loaded Panel
            ScadaAPIException: in case parent widget with given
                `WidgetHandle` cannot be found in loaded Panel
            ScadaAPIException: in case Panel is not specified

        Availability:
            * standalone scripts
            * macro scripts
            * signal monitoring expressions

        **Example:**

        .. literalinclude:: scada_api_examples/get_widget_by_fqn.example
           :language: python
           :lines: 2-
        """

        return clstub().get_widget_by_fqn(widget_fqn=widget_fqn, parent=parent)

    def get_library_paths(self):
        """
        Get a list of the library search paths.

        Returns:
            library paths (list): list with user library paths

        Availability:
            * standalone scripts
        """

        return clstub().get_library_paths()


panel = ScadaAPI()
