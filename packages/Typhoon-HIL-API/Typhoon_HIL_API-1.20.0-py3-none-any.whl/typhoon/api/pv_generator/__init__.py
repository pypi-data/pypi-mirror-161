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

from typhoon.api.pv_generator.stub import clstub

# ----------------------------------------
# -------------- pv settings -------------
# ----------------------------------------

# pv panel model types
PV_MT_DETAILED = "Detailed"
PV_MT_EN50530 = "EN50530 Compatible"
PV_MT_NORMALIZED_IV = "Normalized IV"
PV_MODELS = [PV_MT_DETAILED, PV_MT_EN50530, PV_MT_NORMALIZED_IV]

# pv types used in EN50530 model
EN50530_PV_TYPES = ["cSi", "Thin film", "User defined"]

# pv types used in Detailed model
DETAILED_PV_TYPE = ["cSi", "Amorphous Si"]


def generate_pv_settings_file(modelType, fileName, parameters):
    """
    Generate PV panel settings (.ipvx extension) with specified parameters.

    Args:
        modelType (str): PV model type that will be used for generating settings file.
        fileName (str): file name of resulting .ipvx file.
        parameters (str): dictionary with parameters.

    Supported PV ``modelType`` are:
        * ``'Detailed'`` or ``pv.PV_MODELS[0]``
        * ``'EN50530 Compatible'`` or ``pv.PV_MODELS[1]``
        * ``'Normalized IV'`` or ``pv.PV_MODELS[2]``

    Depending on used PV model type available ``parameters`` are:

    * ``'Detailed'`` model

        +-------------------+-------------------------------------------------------+----------------------------------+
        |   Dictionary key  |                   Meaning                             |               Value              |
        +===================+=======================================================+==================================+
        |     "Voc_ref"     | Open-circuit voltage (Voc [V])                        |               float              |
        +-------------------+-------------------------------------------------------+----------------------------------+
        |     "Isc_ref"     | Short-circuit current (Isc [A])                       |               float              |
        +-------------------+-------------------------------------------------------+----------------------------------+
        |     "dIsc_dT"     | Temperature coefficient of Isc [%Isc/C]               |               float              |
        +-------------------+-------------------------------------------------------+----------------------------------+
        |       "Nc"        | Number of cells                                       |               float              |
        +-------------------+-------------------------------------------------------+----------------------------------+
        |    "dV_dI_ref"    | Curve gradient in Voc_ref point (dV/dI at Voc [V/A])  |               float              |
        +-------------------+-------------------------------------------------------+----------------------------------+
        |       "Vg"        | Band gap voltage                                      | string ("cSi" or "Amorphous Si") |
        +-------------------+-------------------------------------------------------+----------------------------------+
        |       "n"         | Curve gradient in Voc_ref point (dV/dI at Voc [V/A])  |               float              |
        +-------------------+-------------------------------------------------------+----------------------------------+
        |   "neg_current"   | Allow negative current                                |      boolean (True or False)     |
        +-------------------+-------------------------------------------------------+----------------------------------+

    * ``'EN50530 Compatible'`` model

        +----------------------+------------------------------------+------------------------------------------------------------+
        |   Dictionary key     |             Meaning                |                  Value                                     |
        +======================+====================================+============================================================+
        |     "Voc_ref"        | Open-circuit voltage (Voc [V])     | float                                                      |
        +----------------------+------------------------------------+------------------------------------------------------------+
        |     "Isc_ref"        | Short-circuit current (Isc [A])    | float                                                      |
        +----------------------+------------------------------------+------------------------------------------------------------+
        |     "pv_type"        | PV type                            | string ("cSi", "Thin film" or "User defined")              |
        +----------------------+------------------------------------+------------------------------------------------------------+
        |   "neg_current"      | Allow negative current             | boolean (True or False)                                    |
        +----------------------+------------------------------------+------------------------------------------------------------+
        |"user_defined_params" | User defined technology parameters | dictionary (can be omitted if "pv_type" != "User defined") |
        +----------------------+------------------------------------+------------------------------------------------------------+

    * ``'IV normalized'`` model

        +----------------------+------------------------------------+------------------------------------------------------------+
        |   Dictionary key     |             Meaning                |                  Value                                     |
        +======================+====================================+============================================================+
        |     "csv_path"       | path to csv file                   |   str                                                      |
        +----------------------+------------------------------------+------------------------------------------------------------+

        In case ``"User defined"`` is selected as ``pv_type`` additional sub-dictionary
        parameter (``"user_defined_params"``) should be specified.

        +----------------+-----------------------------------------------------------------------------------------+----------------------------+
        | Dictionary key |             Meaning                                                                     |           Value            |
        +================+=========================================================================================+============================+
        |     "ff_u"     | Maximal power point to open circuit voltage ratio                                       | float ( 0.0 < ff_u < 1.0)  |
        +----------------+-----------------------------------------------------------------------------------------+----------------------------+
        |     "ff_i"     | Maximal power point to short circuit voltage ratio                                      | float ( 0.0 < ff_i < 1.0)  |
        +----------------+-----------------------------------------------------------------------------------------+----------------------------+
        |     "c_g"      | Technology depending correction factor                                                  | float ( 0.0 < c_g < 1.0)   |
        +----------------+-----------------------------------------------------------------------------------------+----------------------------+
        |     "c_v"      | Technology depending correction factor                                                  | float ( 0.0 < c_v < 1.0)   |
        +----------------+-----------------------------------------------------------------------------------------+----------------------------+
        |     "c_r"      | Technology depending correction factor                                                  | float ( 0.0 < c_r < 1.0)   |
        +----------------+-----------------------------------------------------------------------------------------+----------------------------+
        |    "v_l2h"     | Voltage ratio from UMPP at irradiance of 200 W/m2 to UMPP at an irradiance of 1000 W/m2 | float ( 0.0 < v_l2h < 1.0) |
        +----------------+-----------------------------------------------------------------------------------------+----------------------------+
        |    "alpha"     | Temperature coefficient of the current                                                  | float ( 0.0 < alpha < 1.0) |
        +----------------+-----------------------------------------------------------------------------------------+----------------------------+
        |    "beta"      | Temperature coefficient of the voltage                                                  | float ( -1.0 < beta < 0.0) |
        +----------------+-----------------------------------------------------------------------------------------+----------------------------+

    Returns:
        tuple(``status``, ``message``)
            * status (bool): ``True`` if everything OK otherwise return ``False``
            * message (str): status message

    Example::

        import typhoon.api.pv_generator as pv

            params = {"Voc_ref": 45.60,
                      "Isc_ref": 5.8,
                      "dIsc_dT": 0.0004,
                      "Nc": 72,
                      "dV_dI_ref": -1.1,
                      "Vg": "cSi",
                      "n" : 1.3,
                      "neg_current": False }

            # generate settings file using Detailed type of PV Model
            (status, msg) =  pv.generate_pv_settings_file(pv.PV_MT_DETAILED,
                                                          "./setDet.ipvx",
                                                          params)


            params = {"Voc_ref": 45.60,
                      "Isc_ref": 5.8,
                      "pv_type": "Thin film",
                      "neg_current": False }

            # generate settings file using EN50530 type of PV Model
            (status, msg) =  pv.generate_pv_settings_file(pv.PV_MT_EN50530,
                                                          "./setEN.ipvx",
                                                          params)

            params = {"Voc_ref": 45.60,
                      "Isc_ref": 5.8,
                      "pv_type": "User defined",
                      "neg_current": False,
                      "user_defined_params": {
                          "ff_u": 0.72,
                          "ff_i": 0.8,
                          "c_g": 1.252e-3,
                          "c_v": 8.419e-2,
                          "c_r": 1.476e-4,
                          "v_l2h": 0.98,
                          "alpha": 0.0002,
                          "beta": -0.002 }
                      }

            # generate settings file using IV normalized type of PV Model
            (status, msg) =  pv.generate_pv_settings_file(pv.IV_Normalized,
                                                          "./setEN.ipvx",
                                                          params)

            params = {"csv_path": "csv_file.csv"}


            # generate settings file using EN50530 type of PV Model with
            # user defined parameters
            (status, msg) =  pv.generate_pv_settings_file(pv.PV_MT_EN50530,
                                                          "./setEN.ipvx",
                                                          params)

    """
    return clstub().generate_pv_settings_file(modelType=modelType,
                                              fileName=fileName,
                                              parameters=parameters)



