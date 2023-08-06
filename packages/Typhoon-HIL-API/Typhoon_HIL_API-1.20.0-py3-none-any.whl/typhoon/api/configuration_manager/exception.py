#
# Configuration Manager API exceptions module.
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


class ConfigurationManagerAPIException(Exception):
    """
    Base exception class for the Configuration manager API
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the object
        """
        super(ConfigurationManagerAPIException, self).__init__(*args)
        self.internal_code = None
        if "internal_code" in kwargs:
            self.internal_code = kwargs["internal_code"]


class ConfigurationManagerAPIExceptionTextX(ConfigurationManagerAPIException):
    def __init__(self, msg, *args):
        msg = "An exception has occurred while parsing/checking the " \
              "integrity of files used for generating certain objects " \
              "needed in the Configuration Manager API. It is best to " \
              "make sure all files (such as .tse, .cfg, .cmp ...) are " \
              "written correctly, and that all software used while running " \
              "the current script is up to date with the latest versions. " \
              "Inner exception: [{0}]".format(msg)
        super(ConfigurationManagerAPIExceptionTextX, self).__init__(msg, *args)


class ConfigurationManagerAPIExceptionGenerate\
            (ConfigurationManagerAPIException):
    def __init__(self, inner_exception, *args):
        msg = "Generating the output script that creates the final schematic " \
              "failed because an exception occured. This could mean that " \
              "certain files are missing, or that the input files (the " \
              "project, the projects template, the configuration or " \
              "the configuration options) may be defined incorrectly. " \
              "Concrete inner exception: [{0}]".format(inner_exception.args)
        super(ConfigurationManagerAPIExceptionGenerate, self)\
            .__init__(msg, *args)


class ConfigurationManagerAPIExceptionSchematicAPI\
            (ConfigurationManagerAPIException):
    def __init__(self, inner_exception, *args):
        msg = "An exception has occurred while trying to generate the " \
              "schematic based on the selected configuration. This could " \
              "have been caused by an error in defining, or a missing item" \
              " in the project definition, projects template definition, " \
              "or the configuration or any variants and options in the " \
              "configuration. This exception was raised by the Schematic " \
              "API, with the following message: [{0}]".format(inner_exception)
        super(ConfigurationManagerAPIExceptionSchematicAPI, self)\
            .__init__(msg, *args)


class ConfigurationManagerAPIExceptionPathNotFound\
            (ConfigurationManagerAPIException):
    def __init__(self, path, *args):
        msg = "Path not found: {0}".format(path)
        super(ConfigurationManagerAPIExceptionPathNotFound, self)\
            .__init__(msg, *args)


class ConfigurationManagerAPIExceptionItemNotFound\
            (ConfigurationManagerAPIException):
    def __init__(self, missing_item, *args):
        msg = 'Item not found: {0}'.format(missing_item)
        super(ConfigurationManagerAPIExceptionItemNotFound, self)\
            .__init__(msg, *args)


class ConfigurationManagerAPIExceptionOptionNotFound\
            (ConfigurationManagerAPIException):
    def __init__(self, pick, variant, *args):
        msg = 'Option: {0} not found for project variant: {1}'.format(
            pick, variant
        )
        super(ConfigurationManagerAPIExceptionOptionNotFound, self)\
            .__init__(msg, *args)


class ConfigurationManagerAPIExceptionVariantNotFound\
            (ConfigurationManagerAPIException):
    def __init__(self, variant, *args):
        msg = 'Variant: {0} not found for project'.format(
            variant
        )
        super(ConfigurationManagerAPIExceptionVariantNotFound, self)\
            .__init__(msg, *args)


class ConfigurationManagerAPIExceptionOutputProjectFileDoesNotExist\
            (ConfigurationManagerAPIException):
    def __init__(self, path, *args):
        msg = 'Path to output project file {0} does not exist'.format(
            path
        )
        super(ConfigurationManagerAPIExceptionOutputProjectFileDoesNotExist,
              self).__init__(msg, *args)


class ConfigurationManagerAPIExceptionOptionError\
            (ConfigurationManagerAPIException):
    def __init__(self, option_name, project_name, *args):
        msg = "Error fetching option [{0}] for project [{1}]. This could " \
              "be because the option file was not found, or the option " \
              "file/concrete option had no component defined, or there " \
              "was a general error when defining the option. Check the " \
              "project file definition, the configuration definition, " \
              "and the option definitions.".format(option_name, project_name)
        super(ConfigurationManagerAPIExceptionOptionError, self)\
            .__init__(msg, *args)
