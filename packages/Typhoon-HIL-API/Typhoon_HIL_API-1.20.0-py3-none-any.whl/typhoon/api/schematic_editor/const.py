#
# Schematic API constants.
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

# Icon rotate behavior constants.
ICON_ROTATE = "rotate"
ICON_NO_ROTATE = "no_rotate"
ICON_TEXT_LIKE = "text_like"

# Fully qualified name separator
FQN_SEP = "."

# Signal types
SIG_TYPE_ANALOG = "analog"
SIG_TYPE_DIGITAL = "digital"

# Signal processing type constants.
SP_TYPE_INHERIT = "inherit"
SP_TYPE_INT = "int"
SP_TYPE_UINT = "uint"
SP_TYPE_REAL = "real"

# Kind constants.
KIND_SP = "sp"
KIND_PE = "pe"

# Direction constants.
DIRECTION_IN = "in"
DIRECTION_OUT = "out"

# Constants for specifying rotation.
ROTATION_DOWN = "down"
ROTATION_UP = "up"
ROTATION_LEFT = "left"
ROTATION_RIGHT = "right"

# Constants for specifying tag scopes.
TAG_SCOPE_LOCAL = "local"
TAG_SCOPE_GLOBAL = "global"
TAG_SCOPE_MASKED_SUBSYSTEM = "masked_subsystem"

# Constant for ItemHandle type
ITEM_HANDLE = "item_handle"

# Flip constants.
FLIP_NONE = "flip_none"
FLIP_HORIZONTAL = "flip_horizontal"
FLIP_VERTICAL = "flip_vertical"
FLIP_BOTH = "flip_both"

# Constants used for specifying item types.
ITEM_ANY = "unknown"
ITEM_COMPONENT = "component"
ITEM_MASKED_COMPONENT = "masked_component"
ITEM_MASK = "mask"
ITEM_CONNECTION = "connection"
ITEM_TAG = "tag"
ITEM_PORT = "port"
ITEM_COMMENT = "comment"
ITEM_JUNCTION = "junction"
ITEM_TERMINAL = "terminal"
ITEM_PROPERTY = "property"
ITEM_SIGNAL = "signal"
ITEM_SIGNAL_REF = "signal_ref"

# Constants used for specifying kind of error and/or warning.
ERROR_GENERAL = "General error"
ERROR_PROPERTY_VALUE_INVALID = "Invalid property value"

WARNING_GENERAL = "General warning"

# Constants used for specifying simulation method.
SIM_METHOD_EXACT = "exact"
SIM_METHOD_EULER = "euler"
SIM_METHOD_TRAPEZOIDAL = "trapezoidal"

GRID_RESOLUTION = 8

# Constants for handler names.
HANDLER_MODEL_INIT = "model_init"
HANDLER_MODEL_LOADED = "model_loaded"
HANDLER_OPEN = "open"
HANDLER_INIT = "init"
HANDLER_MASK_INIT = "mask_init"
HANDLER_CONFIGURATION_CHANGED = "configuration_changed"
HANDLER_PRE_COMPILE = "pre_compile"
HANDLER_BEFORE_CHANGE = "before_change"
HANDLER_PRE_VALIDATE = "pre_validate"
HANDLER_ON_DIALOG_OPEN = "on_dialog_open"
HANDLER_ON_DIALOG_CLOSE = "on_dialog_close"
HANDLER_CALC_TYPE = "calc_type"
HANDLER_CALC_DIMENSION = "calc_dimension"
HANDLER_BUTTON_CLICKED = "button_clicked"
HANDLER_DEFINE_ICON = "define_icon"
HANDLER_POST_RESOLVE = "post_resolve"
HANDLER_PRE_COPY = "pre_copy"
HANDLER_POST_COPY = "post_copy"
HANDLER_PRE_DELETE = "pre_delete"
HANDLER_POST_DELETE = "post_delete"
HANDLER_NAME_CHANGED = "name_changed"
HANDLER_POST_C_CODE_EXPORT = "post_c_code_export"
HANDLER_MASK_PRE_COMPILE = "mask_pre_cmpl"
HANDLER_PROPERTY_VALUE_CHANGED = "property_value_changed"
HANDLER_PROPERTY_VALUE_EDITED = "property_value_edited"

#
# Utility constants which are used with handlers.
#

#
# These REASON_CLOSE_* further explains how dialog is closing in context
# of ON_DIALOG_CLOSE handler.
#
REASON_CLOSE_OK = "reason_close_ok"
REASON_CLOSE_CANCEL = "reason_close_cancel"

# Constants for specifying widget types.
# One exception is file chooser widget which must be
# specified by string value "file_chooser *.ext", where *.ext
# specifies desired file extension.
#
WIDGET_COMBO = "combo"
WIDGET_EDIT = "edit"
WIDGET_CHECKBOX = "checkbox"
WIDGET_BUTTON = "button"
WIDGET_TOGGLE_BUTTON = "togglebutton"
WIDGET_SIGNAL_CHOOSER = "signal_chooser"

#
# For file chooser widget, there is no constant but direct string is used
# as this widget type is parametrized with extension, so for example to specify
# file chooser for extension *.dll and *.so, string will be:
# file_chooser '*.dll *.so'
#

WIDGET_EDIT_MAX_LENGTH = 2 ** 31 - 1

#
# Constants used to determine how hierarchy traversal is performed in context
# of various functions which traverse model.
#
RECURSE_INTO_LINKED_COMPS = "recurse_linked_components"
