#
# SCADA API constants.
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

# Constant for WidgetHandle type
WIDGET_HANDLE = "widget_handle"

#
# Property names
#

PROP_NAME = "name"
PROP_HTML_NAME = "html_name"
PROP_NAME_POSITION = "name_position"
PROP_LABEL = "label"
PROP_USE_LABEL = "use_label"
PROP_FQN = "fully_qualified_name"
PROP_DESCRIPTION = "description"
PROP_PANEL_INIT = "panel_init_code"
PROP_PANEL_LOCK = "panel_locked"
PROP_POSITION = "position"
PROP_SIZE = "size"
PROP_APPEARANCE = "appearance"
PROP_SIGNALS = "signals"
PROP_STREAMING_SIGNALS = "streaming_signals"
PROP_DATA_TYPE = "data_type"
PROP_EXPRESSION = "expression_code"
PROP_UPDATE_RATE = "update_rate"
PROP_TIME_WINDOW = "time_window"
PROP_UNIT = "unit"
PROP_AUTO_UNIT = "auto_unit_assign"
PROP_BG_COLOR = "bg_color"
PROP_PANEL_BG_COLOR = "panel_bg_color"
PROP_BG_TYPE = "bg_type"
PROP_USE_AS_BG = "use_as_bg"
PROP_RANGE = "range"
PROP_USE_COLOR_RANGE = "use_color_range"
PROP_WARNING_RANGE = "warning_range"
PROP_CRITICAL_RANGE = "critical_range"
PROP_GREEN_RANGE = "green_range"
PROP_ORANGE_RANGE = "orange_range"
PROP_DECIMALS = "decimals"
PROP_RED_RANGE = "red_range"
PROP_LED_COLOR = "led_color"
PROP_X_TITLE = "x_title"
PROP_Y_TITLE = "y_title"
PROP_Y_RANGE = "y_range"
PROP_X_RANGE = "x_range"
PROP_X_TITLE_ENABLED = "x_title_enabled"
PROP_Y_TITLE_ENABLED = "y_title_enabled"
PROP_AUTO_SCALE_ENABLED = "autoscale_enabled"
PROP_X_AUTO_SCALE_ENABLED = "x_axis_autoscale_enabled"
PROP_Y_AUTO_SCALE_ENABLED = "Y_axis_autoscale_enabled"
PROP_LEGEND_ENABLED = "legend_enabled"
PROP_REF_CURVE_ENABLED = "ref_curves_enabled"
PROP_REF_CURVE = "ref_curves_code"
PROP_PV_PANEL = "pv_panel"
PROP_LINE_STYLE = "line_style"
PROP_PLOT_RANGE = "plot_range"
PROP_PHASORS_SETTINGS = "phasors_settings"
PROP_BARS_SETTINGS = "bars_settings"
PROP_ON_USE_ENABLED = "on_use_enabled"
PROP_ON_USE = "on_use_code"
PROP_ON_START_ENABLED = "on_start_enabled"
PROP_ON_START = "on_start_code"
PROP_ON_START_SOURCE = "on_start_code_source"
PROP_ON_TIMER_ENABLED = "on_timer_enabled"
PROP_ON_TIMER = "on_timer_code"
PROP_ON_TIMER_RATE = "on_timer_rate"
PROP_ON_STOP_ENABLED = "on_stop_enabled"
PROP_ON_STOP = "on_stop_code"
PROP_COMBO_VALUES = "values"
PROP_VALUE_TYPE = "value_type"
PROP_INPUT_WIDTH = "input_width"
PROP_STEP = "step"
PROP_USE_PANEL_DIR = "use_panel_dir"
PROP_LOG_FILE_DIR = "log_file_dir"
PROP_LOG_FILE = "log_file"
PROP_LOG_FILE_FORMAT = "log_file_format"
PROP_USE_SUFFIX = "use_suffix"
PROP_LOGGING_ON_START = "start_logging_on_start"
PROP_USE_SLOWER_UPDATE_RATE = "use_slower_update_rate"
PROP_SLOWER_UPDATE_RATE = "slower_update_rate"
PROP_CONNECTION_IDENTIFIER = "connection_identifier"
PROP_SERIAL_PORT_SETTINGS = "serial_port_settings"
PROP_SERIAL_PORT_NAME = "serial_port_name"
PROP_GROUP_NAMESPACE = "group_namespace"
PROP_COLLAPSED = "collapsed"
PROP_USE_IMAGE = "use_image"
PROP_IMAGE = "image"
PROP_IMAGE_SCALING = "image_scaling"
PROP_TEXT = "text"
PROP_SUB_PANEL_MODE = "sub_panel_mode"
PROP_MODEL_COMP_TYPES = "model_components_types"
PROP_MODEL_COMP = "model_component"
PROP_WIDGET_VALUE = "widget_value"
PROP_CS_STATE = "state"
PROP_CS_CAPTURE_TIME_INTERVAL = "time_interval"
PROP_CS_CAPTURE_SAMPLE_RATE = "sample_rate"
PROP_CS_SCOPE_TIME_BASE = "time_base"
PROP_CS_CAPTURE_BG = "capture_background"
PROP_CS_SCOPE_BG = "scope_background"
PROP_CS_CAPTURE_LEGEND = "capture_legend"
PROP_CS_SCOPE_LEGEND = "scope_legend"
PROP_CS_CAPTURE_LAYOUT = "capture_layout"
PROP_CS_SCOPE_LAYOUT = "scope_layout"
PROP_CS_SCOPE_ANALOG_SIGNALS = "scope_analog_signals"
PROP_CS_SCOPE_DIGITAL_SIGNALS = "scope_digital_signals"
PROP_CS_CAPTURE_ANALOG_SIGNALS = "capture_analog_signals"
PROP_CS_CAPTURE_DIGITAL_SIGNALS = "capture_digital_signals"
PROP_CS_SCOPE_TRIGGER = "scope_trigger"
PROP_CS_CAPTURE_TRIGGER = "capture_trigger"
PROP_CS_ACTIVE_CAPTURE_PRESET = "active_capture_preset"
PROP_CS_ACTIVE_SCOPE_PRESET = "active_scope_preset"

#
# Widget actions
#

ACT_CS_FORCE_TRIGGER = "force_trigger"
ACT_CS_ENABLE_TRIGGER = "enable_trigger"
ACT_CS_STOP_CAPTURE = "stop_capture"
ACT_CS_EXPORT_DATA = "export_data"

#
# Widget types
#

WT_MACRO = "Macro"
WT_BUTTON_MACRO = "MacroButton"
WT_TEXT_MACRO = "TextBoxMacro"
WT_COMBO_MACRO = "ComboBoxMacro"
WT_CHECKBOX_MACRO = "CheckBoxMacro"
WT_SLIDER_MACRO = "SliderMacro"
WT_KNOB_MACRO = "KnobMacro"

WT_GAUGE = "Gauge"
WT_DIGITAL = "DigitalDisplay"
WT_TEXT = "TextDisplay"
WT_LED = "LedDisplay"
WT_TRACE = "TraceDisplay"
WT_PV = "PVDisplay"
WT_XY_GRAPH = "XYGraphDisplay"
WT_PHASOR_GRAPH = "PhasorGraphDisplay"
WT_BAR_GRAPH = "BarGraphDisplay"

WT_GROUP = "Group"
WT_SUB_PANEL = "SubPanel"
WT_LIBRARY_CATEGORY = "LibraryCategory"
WT_TEXT_NOTE = "TextNote"
WT_IMAGE = "Image"
WT_SERIAL_COMM = "SerialComm"
WT_CAPTURE_SCOPE = "Capture/Scope"

WT_SIGNAL_DATA_LOGGER = "SignalDataLogger"
WT_STREAMING_DATA_LOGGER = "StreamingSignalDataLogger"

WT_FREQUENCY_RESPONSE = "FrequencyResponse"
