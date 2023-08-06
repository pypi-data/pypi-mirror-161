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
"""
This module defines the interface with HIL API.
"""
# Constants
from __future__ import print_function, unicode_literals

import os
from typhoon.api.hil.stub import clstub

# MAX_NO_SAMPLES = model_constants.MAX
MAX_NO_SAMPLES = "max"

RUN_MODES = ['EMBEDDED', 'SYSTEM']

RM_EMBEDDED = RUN_MODES[0]
RM_SYSTEM = RUN_MODES[1]

FL_ARITHMETIC_OVERFLOW = "flg_arithmetic_overflow"
FL_DEAD_TIME = "flg_dead_time"
FL_SERIAL_LINK = "flg_serial_link"
FL_COMP_INT_OVERRUN = "flg_computing_interval_overrun"
FL_SP_CPU_STALLED = "flg_signal_processing_cpu_stalled"
FL_SP_EXC_OCCURRED = "flg_signal_processing_exception_occurred"
FL_PSU_STATUS = "power_supply_unit_status"


def raise_exceptions(value):
    clstub().raise_exceptions = value


def _reconnect():
    """Reconnects client to Typhoon HIL Control Center.

    This is used in cases where Typhoon HIL Control Center needs to be
    restarted, to reestablish the connection between the client and THCC.
    """
    clstub().reconnect()


def _check_requirements(requirements, device=None, conf_id=None):
    """
    Checks the list of feature/s against the specified HIL device.

    Args:
        requirements (list): list of requirement name(s).

        hil (str): the name of the HIL device (in the following format: 'HIL602', 'HIL402'...).

        conf_id (int): HIL configuration id.

     .. note::
        In case either the parameter `hil` or `conf_id` is not specified, the unspecified parameter(s) will be auto-detected from the connected HIL device.

    Returns:
        ``True`` if the specified feature or features are supported for the specified (or detected) HIL device, ``False`` otherwise.
        In case an error occurs ``None`` will be returned.

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions
    """

    return clstub().check_requirements(requirements=requirements,
                                       device=device,
                                       conf_id=conf_id)


def load_model(file="", offlineMode=False, vhil_device=False):
    """
    Uploads a compiled model to a HIL device.

    Args:
        file (str): absolute or relative path to the compiled model file (.cpd extension).

        offlineMode (bool): ``True`` for activating the offline mode or  ``False`` to deactivate it.

        vhil_device (bool): If set to ``True`` Virtual HIL Device will be used in case a hardware HIL device is not detected.

    .. note::
         In the offline mode data will not be sent to the HIL device and some of API functions cannot be used.

    Returns:
        ``True`` if uploading a compiled model succeeded, otherwise returns ``False``.

    Availability:
        * standalone scripts

    Example::

        # loading model
        status =  load_model(file = r"./examples/models/3phaseRectifier Target files/3phaseRectifier.cpd")

        if status:
            # if loading went successfully we can continue
            ...

    """
    return clstub().load_model(file=os.path.abspath(file),
                               offlineMode=offlineMode,
                               vhil_device=vhil_device)


def load_settings_file(file=""):
    """
    Loads a HIL Control Panel settings file and configures the model accordingly.

    Args:
        file (str): absolute or relative path to .run/.runx simulation settings file.

    Returns:
        ``True`` if the settings file loaded successfully, otherwise returns ``False``.

    Availability:
        * standalone scripts

    Example::

        # load HIL Control Panel settings file
        hil.load_settings_file(file = r"./examples/models/3phaseRectifier Target files/init.runx")
    """
    return clstub().load_settings_file(file=os.path.abspath(file))


def save_settings_file(filePath):
    """
    Saves the settings file to a location provided in the argument.

    Args:
        filePath (str): the file path where the settings file will be saved.

    Returns:
        ``True`` if the settings file is saved successfully, otherwise returns ``False``.

    Availability:
        * standalone scripts

    Example::

        # save HIL Control Panel settings file
        hil.save_settings_file(r"./examples/models/3phaseRectifier Target files/init.runx")
    """
    return clstub().save_settings_file(filePath=os.path.abspath(filePath))


def save_model_state(save_to):
    """
    Saves the current model state to the file, from which the model state can be restored any time.

    This function can be used in case the test scenario needs to be divided in multiple
    Python test scripts, when reloading and reconfiguring the model is not an option.

    At the end of the first test script, the model state can be saved and at the beginning of another test script,
    the model state can be loaded again without stopping the simulation.

    Args:
        save_to (str): the path to a file where the current model state will be saved.

    Returns:
        ``True`` if the model state was successfully saved, otherwise returns ``False``

    Availability:
        * standalone scripts

    An example that uses three scripts.

    Initialization script::

        # load the model by using load_model() function
        # ...
        # initialize model parameters
        # ...
        # start the simulation
        # ...
        # at the end of the script save the model state (the name of file is arbitrary)
        hil.save_model_state("./model_state.ms")

    Configuration script::

        # at the beginning load the model state saved at the end of previous script
        hil.load_model_state("./model_state.ms")
        # ...
        # change model parameters by the following test scenario
        # ...
        # at the end of the script save the model state (the name of file is arbitrary)
        hil.save_model_state("./model_state.ms")

    Data analysis script::

        # at the beginning load model state saved at the end of the previous script
        hil.load_model_state("./model_state.ms")
        # ...
        # capture data
        # ...
        # analyze data
        # ...
        # stop the simulation

    """

    return clstub().save_model_state(save_to=os.path.abspath(save_to))


def load_model_state(load_from):
    """
    Loads the HIL model state from a file and connects to the HIL device.

    This function can be used in case the test scenario needs to be divided in multiple
    Python test scripts when reloading and reconfiguring of the model is not an option.

    At the end of the first test script, the model state can be saved and at the beginning of another test script,
    the model state can be loaded again without stopping the simulation.

    .. note::
        Model state is not going to be synchronized with the connected HIL device.

    Args:
        load_from (str): the path to a file with the saved HIL model state.

    Returns:
        ``True`` if the model state was successfully restored, otherwise returns ``False``

    An example that uses three scripts.

    Initialization script::

        # load the model by using load_model() function
        # ...
        # initialize model parameters
        # ...
        # start the simulation
        # ...
        # at the end of script save model state (the name of file is arbitrary)
        hil.save_model_state("./model_state.ms")

    Configuration script::

        # at the beginning load the model state saved at the end of the previous script
        hil.load_model_state("./model_state.ms")
        # ...
        # change model parameters by the following test scenario
        # ...
        # at the end of the script save the model state (the name of file is arbitrary)
        hil.save_model_state("./model_state.ms")

    Data analysis script::

        # at the beginning load the model state saved at the end of the previous script
        hil.load_model_state("./model_state.ms")
        # ...
        # capture data
        # ...
        # analyze data
        # ...
        # stop the simulation
    """

    return clstub().load_model_state(load_from=os.path.abspath(load_from))


def upload_standalone_model(model_location):
    """
    Upload already loaded Model as standalone model to the HIL device
    on specified model location.

    .. note::
        Standalone configuration can be uploaded only after Model is loaded with
        ``load_model()`` function and simulation is not running.

    Args:
        model_location (int): upload model to selected model location slot.
            There are 8 available slots for standalone models.
    Returns:
        status (bool): ``True`` if everything ok, otherwise returns ``False``.

    Availability:
        * standalone scripts
    """

    return clstub().upload_standalone_model(model_location=model_location)


def model_write(model_variable, new_value):
    """
    Sets new value of Model variable with name `model_variable`.

    Args:
        model_variable (str): the name of Model variable that need to be
            changed. The Model variable name's components can be divided with
            different separators.
            Currently supported separators are: ".", "/"

            Example of different separators::

                # name of a Model variable with default '.' separator
                model_write("Vgrid.rms" , 25)

                # name of a Model variable with '/' separator
                model_write("Vgrid/rms" , 25)

            .. note::
                The list of all available Model variables and theirs attributes
                can be acquired by calling ``get_model_variables()`` function.
        new_value (int, float, list): new Model variable value

    Returns:
        None

    Raises:
        HILAPIException: in case Model variable with `model_variable`
            cannot be found
        HILAPIException: in case Model variable with `model_variable` is read
            only variable and cannot be changed.
        HILAPIException: in case `new_value` argument is invalid
        HILAPIException: in case Model variable value cannot be changed
            for any other reasons.
    """

    return clstub().model_write(model_variable=model_variable,
                                new_value=new_value)


def model_read(model_variable):
    """
    Reads value of Model variable with name `model_variable`.

    Args:
        model_variable (str): the name of Model variable that we want to read.
            The Model variable name's components can be divided with different
            separators.
            Currently supported separators are: ".", "/"

            Example of different separators::

                # name of a Model variable with default '.' separator
                model_read("Vgrid.rms")

                # name of a Model variable with '/' separator
                model_read("Vgrid/rms")

            .. note::
                The list of all available Model variables and theirs attributes
                can be acquired by calling ``get_model_variables()`` function.

    Returns:
        variable value (int, float): Model variable value

    Raises:
        HILAPIException: in case Model variable with `model_variable` name
            cannot be found
        HILAPIException: in case Model variable with `model_variable` name is
            write only variable and cannot be read.
        HILAPIException: in case Model variable value cannot be acquired
            for any reason.
    """

    return clstub().model_read(model_variable=model_variable)


def add_data_logger(name, signals, data_file, use_suffix=True):
    """
    Adds one logger to the model that will collect ``signals`` data and store
    them to the specified ``data`` file.

    .. note::
        Only streaming analog and digital signals can be continuously logged
        to the data file.

    .. note::
        Data logger will start to collect data only after simulation and data
        logger are started.

    .. note::
        Each time data logger is started it will overwrite old data file in
        case ``use_suffix=False`` otherwise it will create new file with
        the current data and time suffix.

    Args:
        name (str): the name of the data logger

        signals (list): list of streaming analog or digital signals' names

            .. note::
                Only streaming signals that works on the same execution rates
                are supported to be logged in one data logger.

        data_file (string): file path to the data file where collected data
            are going to be saved.

            .. note::
                Comma Separated Values (.csv), and HDF5 (.h5), and MDF (.mf4)
                data files formats are supported.

            .. note::
                It is not recommended to use .csv data format for high data
                transfer rates.

        use_suffix (bool): suffix with date and time will be added to the end
        of given data file name

    Returns:
        status (bool): ``True`` if data logger is successfully added,
        otherwise returns ``False``

    Availability:
        * standalone scripts

    Example::

        # add data logger
        status = hil.add_data_logger(
            name='data_logger_1',
            signals=["Probe1[0]", "Probe1[1]",
                     "Digital Probe1[0]", "Digital Probe1[1]"],
            data_file="./data_data_logger_1.csv",
            use_suffix=False)

        # start data logger
        # (it won't start to collect data because simulation is not started)
        status = hil.start_data_logger(name='data_logger_1')

        # start simulation
        # (data logger will immediately start to collect data because
        # is already started)
        hil.start_simulation()

        # ... do something

        # stop data logger
        status = hil.stop_data_logger(name='data_logger_1')

    Example::

        # to open and parse saved data files you can use excellent
        # Python Pandas library
        import pandas as pd

        # read *.csv file (you will get pandas DataFrame object)
        pandas_data_frame = pd.read_csv("./data_data_logger_1.csv")

        # read *.h5 file (you will get pandas DataFrame object)
        pandas_data_frame = pd.read_hdf("./data_data_logger_1.h5")

    """

    if isinstance(data_file, str):
        data_file = os.path.abspath(data_file)

    return clstub().add_data_logger(name=name,
                                    signals=signals,
                                    data_file=data_file,
                                    use_suffix=use_suffix)

def remove_data_logger(name):
    """
    Removes data logger with the given ``name`` from the model.
    In case the ``name`` is given as a list of loggers names, all loggers from the list will be removed at the same time.

    Args:
        name (str or list): the name of one data logger or list of data loggers names that need to be removed.

    Returns:
        status (bool): ``True`` if data logger is successfully removed, otherwise returns ``False``

    Example::

        # add data loggers
        status = hil.add_data_logger(name='data_logger_1',
                                     signals=["Probe1[0]", "Probe1[1]",
                                              "Digital Probe1[0]", "Digital Probe1[1]"],
                                     data_file="./data_data_logger_1.csv")

        status = hil.add_data_logger(name='data_logger_2',
                                     signals=["Probe1[0]", "Probe1[1]",
                                              "Digital Probe1[0]", "Digital Probe1[1]"],
                                     data_file="./data_data_logger_2.csv")

        # ... do something

        # remove data loggers one by one from the model
        status = hil.remove_data_logger(name='data_logger_1')
        status = hil.remove_data_logger(name='data_logger_2')

        # ...or
        status = hil.remove_data_logger(name=['data_logger_1', 'data_logger_2'])
    """

    return clstub().remove_data_logger(name=name)


def start_data_logger(name):
    """
    Starts data logger with the given ``name`` from the model.
    In case the ``name`` is given as a list of loggers names, all loggers from the list will be started at the same time.

    Args:
        name (str or list): the name of one data logger or list of data loggers names that need to be started.

    Returns:
        status (bool): ``True`` if data logger is successfully started, otherwise returns ``False``

    Example::

        # add data loggers
        status = hil.add_data_logger(name='data_logger_1',
                                     signals=["Probe1[0]", "Probe1[1]",
                                              "Digital Probe1[0]", "Digital Probe1[1]"],
                                     data_file="./data_data_logger_1.csv")

        status = hil.add_data_logger(name='data_logger_2',
                                     signals=["Probe1[0]", "Probe1[1]",
                                              "Digital Probe1[0]", "Digital Probe1[1]"],
                                     data_file="./data_data_logger_2.csv")

        # ... do something

        # start data loggers one by one
        status = hil.start_data_logger(name='data_logger_1')
        status = hil.start_data_logger(name='data_logger_2')

        # ...or
        status = hil.start_data_logger(name=['data_logger_1', 'data_logger_2'])
    """

    return clstub().start_data_logger(name=name)


def stop_data_logger(name):
    """
    Stops data logger with the given ``name`` from the model.
    In case the ``name`` is given as a list of loggers names, all loggers from the list will be stopped at the same time.

    Args:
        name (str or list): the name of one data logger or list of data loggers names that need to be stopped.

    Returns:
        status (bool): ``True`` if data logger is successfully stopped, otherwise returns ``False``

    Example::

        # add data loggers
        status = hil.add_data_logger(name='data_logger_1',
                                     signals=["Probe1[0]", "Probe1[1]",
                                              "Digital Probe1[0]", "Digital Probe1[1]"],
                                     data_file="./data_data_logger_1.csv")

        status = hil.add_data_logger(name='data_logger_2',
                                     signals=["Probe1[0]", "Probe1[1]",
                                              "Digital Probe1[0]", "Digital Probe1[1]"],
                                     data_file="./data_data_logger_2.csv")

        # ... do something

        # stop data loggers one by one
        status = hil.stop_data_logger(name='data_logger_1')
        status = hil.stop_data_logger(name='data_logger_2')

        # ...or
        status = hil.stop_data_logger(name=['data_logger_1', 'data_logger_2'])
    """

    return clstub().stop_data_logger(name=name)


def update_sources(sources, executeAt=None):
    """
    Updates (activates) previously prepared source waveforms.

    Args:
        sources (list): a list that contains sources' names.

        executeAt (int, float): executes this command at a specified simulation time.
                                If ``executeAt`` is not specified (or ``executeAt`` == None)
                                the command will be executed immediately.

    Returns:
        ``True`` if waveforms are updated/activated, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        # get the simulation step
        simulationStep = hil.get_sim_step()

        # calculate the update (execution) times
        executeAt1 = simulationStep * 100000 # execute after 100000 simulation cycles
        executeAt2 = simulationStep * 200000

        # prepare arbitrary waveforms for three sources
        hil.prepare_source_arbitrary_waveform("Va", file = r"./examples/inputs/sources/230V_50Hz_phase_a.isg")
        hil.prepare_source_arbitrary_waveform("Vb", file = r"./examples/inputs/sources/230V_50Hz_phase_b.isg")
        hil.prepare_source_arbitrary_waveform("Vc", file = r"./examples/inputs/sources/230V_50Hz_phase_c.isg")

        # update 'Va' and 'Vb' source at the same time
        hil.update_sources(["Va","Vb"],executeAt=executeAt1)

        # update 'Vc' source at a different time
        hil.update_sources(["Vc"],executeAt=executeAt2)

    """
    return clstub().update_sources(sources=sources, executeAt=executeAt)


def prepare_source_arbitrary_waveform(name, file=""):
    """
    Assigns an arbitrary waveform file (isg) to a given independent voltage/current
    source(s).
    Arbitrary waveform data will be sent to a HIL device, but will not be activated.

    To activate the uploaded waveform use the ``update_sources()`` function.

    .. note::
        Only one waveform can be queued for update. Further calls to this function will
        overwrite the previously prepared waveform.

    Args:
        name (str, list): source name or a list of source names that need to be prepared.

        file (str, list): absolute or relative path to the waveform file (isg extension)
            or list of paths to waveform files.

    Returns:
        ``True`` if waveform assignment succeeded, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        # prepare one by one
        hil.prepare_source_arbitrary_waveform("Va", file=r"./examples/inputs/sources/230V_50Hz_phase_a.isg")
        hil.prepare_source_arbitrary_waveform("Vb", file=r"./examples/inputs/sources/230V_50Hz_phase_b.isg")
        hil.prepare_source_arbitrary_waveform("Vc", file=r"./examples/inputs/sources/230V_50Hz_phase_c.isg")

        # or prepare all of them
        hil.prepare_source_arbitrary_waveform(name=["Va", "Vb", "Vc"],
                                              file=[r"./examples/inputs/sources/230V_50Hz_phase_a.isg",
                                                    r"./examples/inputs/sources/230V_50Hz_phase_b.isg",
                                                    r"./examples/inputs/sources/230V_50Hz_phase_c.isg"])
    """
    return clstub().prepare_source_arbitrary_waveform(name=name,
                                                      file=os.path.abspath(file))


def prepare_source_constant_value(name, value=0):
    """
    Sets a constant value to a given independent voltage/current source(s).
    The new value will be sent to a HIL device, but it will not be activated.

    To activate the prepared value use the ``update_sources()`` function.

    .. note::
        Only one value change can be queued for update. Further calls to this function
        will overwrite the previously prepared value.

    Args:
        name (str, list): source name or a list of source names.

        value (float, list): the constant value or list of constant values that need to
            be prepared.

    Returns:
        ``True`` if setting the constant value succeeded, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        # prepare one source
        hil.prepare_source_constant_value("Vdc", value=200)

        # or prepare multiple sources
        hil.prepare_source_constant_value(["Vdc", "Vab"], value=[200, 100])
    """
    return clstub().prepare_source_constant_value(name=name, value=value)


def prepare_source_sine_waveform(name, rms=None, frequency=None, phase=None,
                                 harmonics=None, harmonics_pu=None):
    """
    Assigns a sinusoidal signal to a given independent voltage/current source(s).
    The sinusoidal signal will be sent to a HIL device, but it will not be activated.

    To activate the uploaded waveform data use the ``update_sources()`` function.

    .. note::
        Only one signal change can be queued for update. Further calls to this function
        will overwrite the previously prepared signal change.

    Args:
        name (str, list): source name or a list of source names.

        rms (float, list): rms value or list of rms values.

        frequency (float, list): frequency (default 50Hz) or list of frequency values.

        phase (float, list): phase (in degrees) or list of phase values.

        harmonics (list): list of harmonics, which should be specified as follows:

            list[(harmonic_number_1,rms_1,phase_1),...(harmonic_number_n,rms_n,phase_n)].

        harmonics_pu (list): list of per-unit harmonics, which should be specified
            as follows:

            list[(harmonic_number_1,rms_p_u_1,phase_1),...(harmonic_number_n,rms_p_u_n,phase_n)]

            where:

                 ``rms_p_u_n`` value is harmonic rms given in a relative unit between 0 and 1.

    .. note::
        ``harmonics`` argument was left for the compatibility purposes.
        Old type of harmonics will be automatically converted to the new per-unit
        harmonics.

    Returns:
        ``True`` if the sinusoidal signal is assigned successfully, otherwise returns ``False``

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        # list of harmonics
        harmonics = []

        # tuples that contains harmonic settings
        # (harmonic_number,rms,phase)
        harmonic1 = (2,23,2)
        harmonic2 = (2,2,0)
        harmonic3 = (20,5,5)

        # store harmonics
        harmonics.append(harmonic1)
        harmonics.append(harmonic2)
        harmonics.append(harmonic3)

        # prepare one
        hil.prepare_source_sine_waveform("Vb", rms=220, frequency=50,
                                         phas= 120, harmonics=harmonics)

        # or prepare multiple sources
        hil.prepare_source_sine_waveform(["Va", "Vb"],
                                         rms=[220, 230],
                                         frequency=[50, 60],
                                         phase=[120, 100],
                                         harmonics=harmonics)
    """
    return clstub().prepare_source_sine_waveform(name=name, rms=rms,
                                                 frequency=frequency,
                                                 phase=phase,
                                                 harmonics=harmonics,
                                                 harmonics_pu=harmonics_pu)


def enable_ao_limiting(channel, lower_limit, upper_limit, device=0):
    """
    Enables Analog output current/voltage limiting features and sets new
    lower and upper limits, which is necessary to activate the protection for a model
    created with +/-5.0 AO range on devices with +/-10.0 AO range.

    Args
        channel (int): analog output channel number.

        lower_limit (float): lover limiting value.

        upper_limit (float): upper limiting value

        device (int): on which device you want to set analog output.

    Returns:
        * ``True`` if everything ok, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        hil.enable_ao_limiting(1, lower_limit = -1.0, upper_limit = 1.0, device=0)
    """

    return clstub().enable_ao_limiting(channel=channel,
                                       lower_limit=lower_limit,
                                       upper_limit=upper_limit,
                                       device=device)


def disable_ao_limiting(channel, device=0):
    """
    Disables Analog output current/voltage limiting features and set
    lover and upper limits to the default value.

    Args
        channel (int): analog output channel number.

        device (int): on which device you want to set analog output.

    Returns:
        * ``True`` if everything ok, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        hil.disable_ao_limiting(1, device=1)
    """

    return clstub().disable_ao_limiting(channel=channel,
                                        device=device)


def set_boot_configuration(boot_opt, model_location=None, digital_settings=None):
    """
    Sets standalone configuration boot options.

    Args:
        boot_opt (int): there is three supported boot options listed bellow
        model_location (int): in case boot option ``Boot using selected model`` is used,
            this argument specify which uploaded model slot is used.

            .. note:
                It should be int value in range [1, 8].

        digital_settings (list): in case ``Boot using model selected by digital inputs``
            is used, this argument specify digital signal settings used for selecting
            uploaded model location slot.

            ..note:
                ``digital_settings`` argument should be list of three elements, where each
                element is int number of digital signal used for configuration
                in range [1, number of digital outputs].

    +---------------+---------------------------------------------+
    |  BOOT OPTIONS |                    MEANING                  |
    +===============+=============================================+
    |       1       | Disable standalone boot                     |
    +---------------+---------------------------------------------+
    |       2       | Boot using selected model                   |
    +---------------+---------------------------------------------+
    |       3       | Boot using model selected by digital inputs |
    +---------------+---------------------------------------------+

    Returns:
        status (bool): ``True`` if everything ok, otherwise returns ``False``.

    Availability:
        * standalone scripts
    """

    return clstub().set_boot_configuration(boot_opt=boot_opt,
                                           model_location=model_location,
                                           digital_settings=digital_settings)


def set_source_arbitrary_waveform(name, file):
    """
    Assigns an arbitrary waveform file (isg) to a given independent voltage/current
    source(s).

    Args:
        name (str, list): source name or a list of source names that need to be set.

        file (str, list): absolute or relative path to the waveform file (isg extension)
            or list of paths to waveform files.

    Returns:
        ``True`` if an arbitrary waveform file is successfully assigned,
        otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        # prepare one by one
        hil.set_source_arbitrary_waveform("Va", file=r"./examples/inputs/sources/230V_50Hz_phase_a.isg")
        hil.set_source_arbitrary_waveform("Vb", file=r"./examples/inputs/sources/230V_50Hz_phase_b.isg")
        hil.set_source_arbitrary_waveform("Vc", file=r"./examples/inputs/sources/230V_50Hz_phase_c.isg")

        # or set all of them
        hil.set_source_arbitrary_waveform(name=["Va", "Vb", "Vc"],
                                          file=[r"./examples/inputs/sources/230V_50Hz_phase_a.isg",
                                                r"./examples/inputs/sources/230V_50Hz_phase_b.isg",
                                                r"./examples/inputs/sources/230V_50Hz_phase_c.isg"])

    """

    # in case name is given as list of file paths
    if isinstance(file, (list, tuple)):
        converted_file_name = [os.path.abspath(f) for f in file]

    # it is given as str
    else:
        converted_file_name = os.path.abspath(file)

    return clstub().set_source_arbitrary_waveform(name=name, file=converted_file_name)


def set_source_constant_value(name, value=0, executeAt=None, ramp_time=0, ramp_type='lin'):
    """
    Sets a constant value to a given independent voltage/current source(s).

    Args:
        name (str, list): source name or a list of source names.

        value (float, list): the constant value or list of constant values that need to
            be set.

        executeAt (int, float): executes this command at a specified simulation time.
            If ``executeAt`` is not specified (or ``executeAt`` == None) the command
            will be executed immediately.

        ramp_time (int): defines the period over which the transition is applied

        ramp_type (str): defines the transition shape.
            Supported values are 'lin' (linear interpolation) and 'exp'
            (first order system response - ramp time equals to 7 tau)

    Returns:
        ``True`` if a constant value is set successfully, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        # set one source
        hil.set_source_constant_value("Vdc", value = 200)

        # or set multiple sources
        hil.prepare_source_constant_value(["Vdc", "Vab], value=[200, 100])
    """
    return clstub().set_source_constant_value(name=name, value=value,
                                              executeAt=executeAt,
                                              ramp_time=ramp_time,
                                              ramp_type=ramp_type)


def set_source_sine_waveform(name, rms=None, frequency=None,
                             phase=None, harmonics=None,
                             harmonics_pu=None, executeAt=None,
                             ramp_time=0, ramp_type='lin'):
    """
    Assigns a sinusoidal signal to a given independent voltage/current source(s).

    Args:
        name (str, list): source name or a list of source names.

        rms (float, list): rms value or list of rms values.

        frequency (float, list): frequency (default 50Hz) or list of frequency values.

        phase (float, list): phase (in degrees) or list of phase values.

        harmonics (list): list of harmonics defined in absolute units, specified
            as follows:

            list[(harmonic_number_1,rms_1,phase_1),...(harmonic_number_n,rms_n,phase_n)].

        harmonics_pu (list): list of harmonics defined in relative units, specified
            as follows:

            list[(harmonic_number_1,rms_pu_1,phase_1),...(harmonic_number_n,rms_pu_n,phase_n)]

            where

            ``rms_pu_n`` value is harmonic rms given in relative units between 0 and 1.

        executeAt (int, float): executes this command at a specified simulation time.
            If ``executeAt`` is not specified (or ``executeAt`` == None) the command will
            be executed immediately.

        ramp_time(int): defines the period over which the transition is applied

        ramp_type(str): defines the transition shape. Supported values are 'lin'
            (linear interpolation) and 'exp' (first order system response - ramp time
            equals to 7 tau)

    .. note::
        ``harmonics`` argument is left for compatibility purposes. For all new development
        purposes, it is strongly recommended to use the ``harmonics_pu`` attribute instead.

    .. note::
        It is strongly recommended to use the ``harmonics_pu`` argument for specifying
        higher harmonic content.

    .. note::
        ``executeAt`` option is not available if the ``harmonics`` or ``harmonics_pu``
        arguments are used.


    Returns:
        ``True`` if a sinusoidal signal is successfully assigned, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        # list of harmonics
        harmonics_pu = []

        # tuples that contains harmonic settings
        # (harmonic_number,rms,phase)
        harmonic1 = (3, 0.1, 0)
        harmonic2 = (5, 0.05, 90)
        harmonic3 = (7, 0.03, 270)

        # store harmonics
        harmonics_pu.append(harmonic1)
        harmonics_pu.append(harmonic2)
        harmonics_pu.append(harmonic3)

        # set one source
        hil.set_source_sine_waveform("Vb", rms=220, frequency=50,
                                     phase= 120, harmonics_pu=harmonics_pu)

        # or set multiple sources
        hil.set_source_sine_waveform(["Va", "Vb"],
                                     rms=[220, 230],
                                     frequency=[50, 60],
                                     phase=[120, 100],
                                     harmonics_pu=harmonics_pu)
    """
    return clstub().set_source_sine_waveform(name=name, rms=rms,
                                             frequency=frequency,
                                             phase=phase,
                                             harmonics=harmonics,
                                             harmonics_pu=harmonics_pu,
                                             executeAt=executeAt,
                                             ramp_time=ramp_time,
                                             ramp_type=ramp_type)


def set_source_scaling(name, scaling, executeAt=None, ramp_time=0, ramp_type='lin'):
    """
    Set the source scaling factor.

    .. note::
        In case any source parameter is changed, the scaling value will be reset to 1.0.

    Args:
        name (str): source name or a list of source names.

        scale (float, list): new scaling factor (float value or a list of float values)

        executeAt (int, float): executes this command at specified simulation time.
            If ``executeAt`` is not specified (or ``executeAt`` == None) the command
            will be executed immediately.

        ramp_time(int): defines the period over which the transition is applied

        ramp_type(str): defines the transition shape.
            Supported values are 'lin' (linear interpolation) and 'exp' (
            first order system response - ramp time equals to 7 tau)

    Returns:
        ``True`` if the source scaling factor was set successfully, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        # get simulation step
        simulationStep = hil.get_sim_step()

        # calculate update (execution) times
        executeAt1 = simulationStep * 100000 # execute after 100000 simulation cycles

        # set one source
        hil.set_source_scaling("Vb", 5.0, executeAt=executeAt1)

        # or set multiple sources
        hil.set_source_scaling(["Vb", "Vb"], [5.0, 6], executeAt=executeAt1)
    """
    return clstub().set_source_scaling(name=name,
                                       scaling=scaling,
                                       executeAt=executeAt,
                                       ramp_time=ramp_time,
                                       ramp_type=ramp_type)


def set_pv_input_file(name,
                      file,
                      illumination=0.0,
                      temperature=0.0,
                      isc=10.0,
                      voc=100.0):
    """
    Assigns an IV curve to a given photovoltaic panel.

    Args:
        name (str): name of the photovoltaic

        file (str): absolute or relative path to the PV file (.ipv or .ipvx extension).

        illumination (float): illumination value of the PV panel (float value).

        temperature (float): temperature value of the PV panel  (float value).

        isc (float): current scaling factor value of PV panel (float value).

        voc (float): voltage scaling factor value of PV panel  (float value).

    .. note::
        If you load a PV file with .ipv extension you will not be able to change ``illumination`` and ``temperature`` parameters.
        Changing these parameters is only available by loading a new version of the PV file with .ipvx extension.

    Returns:
        ``True`` if an IV curve was successfully assigned, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        # setting PV using an .ipv PV file (in this case changing 'illumination' and 'temperature' values will have no effect)
        hil.set_pv_input_file("PV_panel",file = r"./examples/inputs/photovoltaics/PVFN_pv_200_wpms_20c.ipv")

        # setting PV using an .ipvx PV file (in this case you can change 'illumination' and 'temperature' values)
        hil.set_pv_input_file("PV_panel",file = r"./examples/inputs/photovoltaics/Jinko_JKM200M-72.ipvx",
                              illumination = 1000.0, temperature = 25.0)

        # setting PV using an .ipvx PV file (in this case you can change 'isc' and 'voc' values)
        hil.set_pv_input_file("PV_panel",file = r"./examples/inputs/photovoltaics/IV_Normalized.ipvx",
                              isc = 10.0, voc = 25.0)
    """
    return clstub().set_pv_input_file(name=name,
                                      file=os.path.abspath(file),
                                      illumination=illumination,
                                      temperature=temperature,
                                      isc=isc,
                                      voc=voc)


def set_pv_amb_params(name,
                      illumination=None,
                      temperature=None,
                      isc=None,
                      voc=None,
                      executeAt=None,
                      ramp_time=0,
                      ramp_type='lin'):
    """
    Change ambiental parameters of the PV panel with a given name.

    .. note::
        Before changing a PV panel's ambiental settings you need to initialize the PV panel with an .ipvx PV settings file.
        To initialize a PV panel, call the ``set_pv_input_file()`` function.

    .. note::
        You can change both ``illumination`` and ``temperature`` at the same time, or only one of them.
        If you change only one parameter, the last set value will be used for the second parameter.

    .. note::
        In case you are using the timed command (``executeAt`` != None), you need to wait
        for the first command to execute before setting the next timed command.
        Successive use of a timed command in this function will overwrite illumination and
        temperature values scheduled in the previously set timed command.

    Args:
        name (str): name of the photovoltaic.

        illumination (float): illumination value of a PV panel (float value).

        temperature (float): temperature value of a PV panel  (float value).

        isc (float): current scaling factor value of PV panel (float value).

        voc (float): voltage scaling factor value of PV panel  (float value).

        executeAt (int, float): executes this command at specified simulation time.
                                If ``executeAt`` is not specified (or ``executeAt`` == None)
                                the command will be executed immediately.

        ramp_time (float): defines the period over which the transition is applied
        
        ramp_type (str): defines the transition shape.
                         Supported values are 'lin' (linear interpolation) and 'exp' (first order
                         system response - ramp time equals to 7 tau).


    Returns:
        tuple(status, tuple(Imp,Vmp))
            * status: ``True`` if everything ok, otherwise returns ``False``.
            * Imp: maximal power current.
            * Vmp: maximal power voltage.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        # initialize PV using an .ipvx PV file and set the initial illumination and temperature values
        status = hil.set_pv_input_file("PV_panel",
                                       file = r"./examples/inputs/photovoltaics/Jinko_JKM200M-72.ipvx",
                                       illumination = 1000.0,
                                       temperature = 25.0)

        # change both illumination and temperature parameters
        (status,(Imp,Vmp)) = hil.set_pv_amb_params("PV_panel", illumination = 1500.0, temperature = 30.0)

        # change only illumination (last set temperature value will be used -> 30.0)
        (status,(Imp,Vmp)) = hil.set_pv_amb_params("PV_panel", illumination = 1800.0)

        # change only the temperature parameter (last set illumination value will be used -> 1800.0)
        (status,(Imp,Vmp)) = hil.set_pv_amb_params("PV_panel", temperature = 35.0)

        # change both isc and voc parameters
        (status,(Imp,Vmp)) = hil.set_pv_amb_params("PV_panel", isc = 1500.0, voc = 30.0)

        # change only isc (last set voc value will be used -> 30.0)
        (status,(Imp,Vmp)) = hil.set_pv_amb_params("PV_panel", isc = 1800.0)

        # change only the voc parameter (last set isc value will be used -> 1800.0)
        (status,(Imp,Vmp)) = hil.set_pv_amb_params("PV_panel", voc = 35.0)

        # change both isc and voc parameters gradually
        (status,(Imp,Vmp)) = hil.set_pv_amb_params("PV_panel", isc = 1500.0,voc = 30.0, ramp_time = 1)

        # get the simulation step
        simulationStep = hil.get_sim_step()

        # calculate the execution time
        executeAt1 = simulationStep * 100000 # execute after 100000 simulation cycles

        # change illumination at a specified simulation time
        (status,(Imp,Vmp)) = hil.set_pv_amb_params("PV_panel", illumination = 2000.0, executeAt = executeAt1)


    """
    return clstub().set_pv_amb_params(name=name,
                                      illumination=illumination,
                                      temperature=temperature,
                                      isc=isc,
                                      voc=voc,
                                      executeAt=executeAt,
                                      ramp_time=ramp_time,
                                      ramp_type=ramp_type)



def set_analog_output(channel, name=None, scaling=None, offset=None, device=0):
    """
    Defines signal assignment, scaling and offset for a given analog output.

    Args:
        channel (int): analog output channel number.

        name (str): name of the analog signal.

        scaling (float): scaling value.

        offset (float): offset value.

        device (int): specifies on which device you want to set the analog output.

    Returns:
        ``True`` if the assignment was successful, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        hil.set_analog_output(1, "V( V0 )", scaling = 100, offset = 0)
    """
    return clstub().set_analog_output(channel=channel, name=name,
                                      scaling=scaling, offset=offset,
                                      device=device)


def set_analog_output_signal(channel, name, device=0):
    """
    Defines signal assignment for a given analog output.

    Args:
        channel (int): analog output channel number.

        name (str): name of the analog signal.

        device (int): specifies on which device you want to set the analog output signal.

    Returns:
        ``True`` if the assignment was successful, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        hil.set_analog_output_signal(1,"V( V0 )")
    """
    return clstub().set_analog_output_signal(channel=channel, name=name,
                                             device=device)


def set_analog_output_scaling(channel, scaling=0.0, device=0):
    """
    Defines signal scaling for a given analog output.

    Args:
        channel (int): analog output channel number.

        scaling (float): scaling value.

        device (int): specifies on which device you want to set the analog output scaling.

    Returns:
        ``True`` if scaling was successfully defined, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        hil.set_analog_output_scaling(1, scaling = 100)
    """
    return clstub().set_analog_output_scaling(channel=channel, scaling=scaling,
                                              device=device)


def set_analog_output_offset(channel, offset=0.0, device=0):
    """
    Defines offset value for a given analog output.

    Args:
        channel (int): analog output channel number.

        offset (float): offset value.

        device (int): specifies on which device you want to set the analog output offset.

    Returns:
        ``True`` if offset value was defined successfully, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        hil.set_analog_output_offset(1, offset = 0)
    """
    return clstub().set_analog_output_offset(channel=channel,
                                             offset=offset,
                                             device=device)


def set_digital_output(channel, name=None, invert=None, swControl=None,
                       value=None, device=0):
    """
    Defines all properties of a given digital output.

    Args:
        channel (int): digital output channel number.

        name (str): name of assigned digital signal.

        invert (bool): if ``True`` digital output is inverted.

        swControl (bool): Defines the control mode. If ``True`` (software mode) the digital output
                          value is defined by a value argument, otherwise the value is defined by
                          the assigned signal (hardware mode).

        value (int): software defined value 0/1.

        device (int): specifies on which device you want to set the digital output.

    .. note::
        Invert logic will have no effect instantly if the software control mode is selected for a given digital output.
        Once software control is disabled, invert logic will be applied on the assigned digital signal.

    .. note::
        Changing software value will have no effect instantly if the hardware control mode is selected for a given digital output.
        Once hardware control is disabled, the software value will be set on the given digital output.

    Returns:
        ``True`` if all properties have been successfully defined, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        hil.set_digital_output(1, name = 'machine encoder A', invert = False, swControl = False, value = 0)
    """
    return clstub().set_digital_output(channel=channel, name=name,
                                       invert=invert, swControl=swControl,
                                       value=value, device=device)


def set_digital_output_signal(channel, name,device = 0):
    """
    Defines signal assignment for a given digital output.

    Args:
        channel (int): digital output channel number.

        name (str): name of the assigned digital signal.

        device (int): specifies on which device you want to set the digital output signal.

    .. note::
        This function will have no effect instantly if the software control mode is selected for a given digital output.
        Once software control is disabled, the assigned digital signal will be activated.

    Returns:
        ``True`` if signal assignment was performed successfully, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        hil.set_digital_output_signal(1, name = 'machine encoder A')
    """
    return clstub().set_digital_output_signal(channel=channel,
                                              name=name,
                                              device=device)


def set_digital_output_inverting(channel, invert=False, device=0):
    """
    Defines signal inverting for a given digital output.

    Args:
        channel (int): digital output channel number.

        invert (bool): if ``True`` the digital output is inverted.

        device (int): specifies on which device you want to set the analog output inverting state.

    .. note::
        This function will have no effect instantly if the software control mode is selected for a given digital output.
        Once software control is disabled, invert logic will be applied on the assigned digital signal.

    Returns:
        ``True`` if signal inverting process was successful, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        hil.set_digital_output_inverting(1, invert = False)
    """
    return clstub().set_digital_output_inverting(channel=channel,
                                                 invert=invert,
                                                 device=device)


def set_digital_output_sw_control(channel, swControl=False, device=0):
    """
    Defines the control mode for a given digital output.

    Args:
        channel (int): digital output channel number.

        swControl (bool): Defines the control mode. If ``True`` (software mode) the digital output
                          value is defined by the value argument, otherwise the value is defined by
                          the assigned signal (hardware mode).

        device (int): specifies on which device you want to set the analog output software control state.

    Returns:
        ``True`` if the control mode was set successfully, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        hil.set_digital_output_sw_control(1, swControl = False)
    """
    return clstub().set_digital_output_sw_control(channel=channel,
                                                  swControl=swControl,
                                                  device=device)


def set_digital_output_software_value(channel, value=0, device=0):
    """
    Specifies the value on a given digital output.

    Args:
        channel (int): digital output channel number (from 1 to 32).

        value (int): software defined value 0/1.

        device (int): specifies on which device you want to set the analog output software value.

    .. note::
        This function will have no effect instantly if the hardware control mode is selected for a given digital output.
        Once hardware control is disabled, the software value will be set on the given digital output.

    Returns:
        ``True`` if the value was specified successfully, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        hil.set_digital_output_software_value(1, value = 0)
    """
    return clstub().set_digital_output_software_value(channel=channel,
                                                      value=value,
                                                      device=device)


def set_contactor(name, swControl=None, swState=None, executeAt=None):
    """
    Selects the control mode and defines the SW state for a given contactor.

    Args:
        name (str): contactor name.

        swControl (bool): Defines the control mode. If ``True`` (software mode) the contactor state
                          is defined by the swState argument. Otherwise, the contactor is controlled
                          from the assigned digital input (hardware mode).

        swState (bool): Defines the contactor state in the SW control mode. ``True`` closed, ``False`` open.

        executeAt (int, float): executes this command at a specified simulation time.
                                If ``executeAt`` is not specified (or ``executeAt`` == None) the command will
                                be executed immediately.

    Returns:
        ``True`` if the control mode and state were successfully set, ``False`` if an error occurred.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        # get the simulation step
        simulationStep = hil.get_sim_step()

        # calculate the execution time
        executeAt1 = simulationStep * 100000 # execute after 100000 simulation cycles

        # execute the command immediately
        hil.set_contactor('contactor_disch', swControl = True, swState = True)

        # execute the command at a specified time
        hil.set_contactor('contactor_disch', swControl = True, swState = True, executeAt = executeAt1)
    """
    return clstub().set_contactor(name=name, swControl=swControl,
                                  swState=swState, executeAt=executeAt)


def set_contactor_control_mode(name, swControl=False, executeAt=None):
    """
    Selects the control mode for a given contactor.

    Args:
        name (str): contactor name.

        swControl (bool): Defines the control mode. If ``True`` (software mode) the contactor state
                          is defined by the software value (see the set_contactor_state() function).
                          Otherwise, the contactor is controlled from the assigned digital input (hardware mode).

        executeAt (int, float): executes this command at a specified simulation time.
                                If ``executeAt`` is not specified (or ``executeAt`` == None)
                                the command will be executed immediately.

    Returns:
        ``True`` if the control mode was selected successfully, ``False`` if an error occurred.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        # get the simulation step
        simulationStep = hil.get_sim_step()

        # calculate the execution time
        executeAt1 = simulationStep * 100000 # execute after 100000 simulation cycles

        # execute the command immediately
        hil.set_contactor_control_mode('contactor_disch', swControl = True)

        # execute the command at a specified time
        hil.set_contactor_control_mode('contactor_disch', swControl = True, executeAt = executeAt1)
    """
    return clstub().set_contactor_control_mode(name=name,
                                               swControl=swControl,
                                               executeAt=executeAt)


def set_contactor_state(name, swState=False, executeAt=None):
    """
    Defines the SW state for a given contactor.

    Args:
        name (str): contactor name.

        swState   (bool): Defines the contactor state in the SW control mode. ``True`` closed, ``False`` - open.

        executeAt (int, float): executes this command at a specified simulation time.
                                If ``executeAt`` is not specified (or ``executeAt`` == None)
                                the command will be executed immediately.

    .. note::
        Changing the contactor SW state will only have effect if the contactor control mode was set to
        ``software mode`` (see the ``set_contactor_control_mode()`` function).

    Returns:
        ``True`` if the SW state was selected successfully, ``False`` if an error occurred.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        # get the simulation step
        simulationStep = hil.get_sim_step()

        # calculate the execution time
        executeAt1 = simulationStep * 100000 # execute after 100000 simulation cycles

        # execute the command immediately
        hil.set_contactor_state('contactor_disch', swState = True)

        # execute the command at a specified time
        hil.set_contactor_state('contactor_disch', swState = True, executeAt = executeAt1)
    """
    return clstub().set_contactor_state(name=name,
                                        swState=swState,
                                        executeAt=executeAt)


def set_machine_constant_torque(name="", value=0.0, executeAt=None):
    """
    Sets the constant load torque for the machine in the model

    Args:
        name (str): machine name in the model.

        value (float): constant load torque value - value unit is [Nm].

        executeAt (int, float): executes this command at a specified simulation time.
                                If ``executeAt`` is not specified (or ``executeAt`` == None) the command will be executed immediately.

    Returns:
        ``True`` if the load torque was set successfully, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        # get the simulation step
        simulationStep = hil.get_sim_step()

        # calculate the execution time
        executeAt1 = simulationStep * 100000 # execute after 100000 simulation cycles

        # execute the command immediately
        hil.set_machine_constant_torque(name = "Induction_machine1", value = 5.0)

        # execute the command at a specified time
        hil.set_machine_constant_torque(name = "Induction_machine1", value = 5.0, executeAt = executeAt1)
    """
    return clstub().set_machine_constant_torque(name=name, value=value,
                                                executeAt=executeAt)


def set_machine_linear_torque(name="", value=0.0, executeAt=None):
    """
    Sets linear load torque coefficient for the machine in the model.

    Args:
        name (str): machine name in the model.

        value (float): linear load torque coefficient value - value unit is [Nm*s].

        executeAt (int, float): executes this command at a specified simulation time.
                                If ``executeAt`` is not specified (or ``executeAt`` == None)
                                the command will be executed immediately.

    Returns:
        ``True`` if linear load torque coefficient was set successfully, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        # get the simulation step
        simulationStep = hil.get_sim_step()

        # calculate the execution time
        executeAt1 = simulationStep * 100000 # execute after 100000 simulation cycles

        # execute the command immediately
        hil.set_machine_linear_torque(name = "Induction_machine1", value = 0.1)

        # execute the command at a specified time
        hil.set_machine_linear_torque(name = "Induction_machine1", value = 0.1, executeAt = executeAt1)
    """
    return clstub().set_machine_linear_torque(name=name,
                                              value=value,
                                              executeAt=executeAt)


def set_machine_square_torque(name="", value=0.0, executeAt=None):
    """
    Sets square load torque coefficient for the machine in the model.

    Args:
        name (str): machine name in the model.

        value (float): square load torque coefficient value - value unit is [Nm*s^2].

        executeAt (int, float): executes this command at a specified simulation time.
                                If ``executeAt`` is not specified (or ``executeAt`` == None)
                                the command will be executed immediately.

    Returns:
        ``True`` if square load torque coefficient was set successfully, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        # get the simulation step
        simulationStep = hil.get_sim_step()

        # calculate the execution time
        executeAt1 = simulationStep * 100000 # execute after 100000 simulation cycles

        # execute the command immediately
        hil.set_machine_square_torque(name = "Induction_machine1", value = 0.01)

        # execute the command at a specified time
        hil.set_machine_square_torque(name = "Induction_machine1", value = 0.01, executeAt = executeAt1)
    """
    return clstub().set_machine_square_torque(name=name,
                                              value=value,
                                              executeAt=executeAt)


def set_machine_load_source(name="", software=True):
    """
    Sets load torque source for the machine in the model (software or external).

    Args:
        name (str): machine name in the model.

        software (bool): ``True`` if you want to use software control of the machine load torque,
                         otherwise ``False`` for external load torque control.

    Returns:
        ``True`` if load torque source was set successfully, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        hil.set_machine_load_source(name = "Induction_machine1", software = True)
    """
    return clstub().set_machine_load_source(name=name, software=software)


def set_machine_external_torque_type(name="", frictional=True):
    """
    Sets the type of the external torque load for a machine in the model (frictional or potential).

    .. note::
        Changing external torque type is only available when the load torque source is set to 'External'.

    Args:
        name (str): machine name in the model.

        frictional (bool): ``True`` if you want to use the frictional type, otherwise ``False`` for the potential type.

    Returns:
        ``True`` if the type of the external torque load is set successfully, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        hil.set_machine_external_torque_type(name = "Induction_machine1", frictional = True)
    """
    return clstub().set_machine_external_torque_type(name=name,
                                                     frictional=frictional)


def set_machine_constant_torque_type(name="", frictional=True):
    """
    Sets the type of the constant load for a machine in the model (frictional or potential).

    Args:
        name (str): machine name in the model.

        frictional (bool): ``True`` if you want to use the frictional type, otherwise 'False' for the potential type.
                           The direction of frictional load is always opposite in regard to machine
                           rotation (direction), and the direction of potential load is always
                           the same regardless of machine rotation.

    Returns:
        ``True`` if the  type of the constant load is set successfully, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        hil.set_machine_constant_torque_type(name = "Induction_machine1", frictional = True)
    """
    return clstub().set_machine_constant_torque_type(name=name,
                                                     frictional=frictional)


def set_machine_load_type(name="", torque=True):
    """
    Sets the load type for a machine in the model (torque or speed).

    Args:
        name (str): machine name in the model.

        torque (float): ``True`` if you want to use the 'torque' load type, otherwise ``False`` for the 'speed' load type.

    .. note::
        Setting the ``speed`` load type will reset all ``torque`` load types values to their initial state.

    Returns:
        ``True`` if the load type was set successfully, otherwise returns ``False``

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        # set 'speed' load type
        hil.set_machine_load_type(name = "Induction_machine1", torque = False)
    """
    return clstub().set_machine_load_type(name=name, torque=torque)


def set_machine_speed(name="", speed=0.0, executeAt=None):
    """
    Sets the machine speed. The speed is given in rad/s.

    Args:
        name (str): machine name in the model.

        speed (float): machine speed value given as a float value.

        executeAt (int, float): executes this command at a specified simulation time.
                                If ``executeAt`` is not specified (or ``executeAt`` == None)
                                the command will be executed immediately.

    .. note::
        Setting the machine speed value is only possible if the machine load type is set to ``Speed``
        and the machine load source is set to ``Software``.

    Returns:
        ``True`` if the machine speed was set successfully, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        # get the simulation step
        simulationStep = hil.get_sim_step()

        # calculate the execution time
        executeAt1 = simulationStep * 100000 # execute after 100000 simulation cycles

        # execute the command immediately
        hil.set_machine_speed(name = "Induction_machine1", speed = 314)

        # execute the command at a specified time
        hil.set_machine_speed(name = "Induction_machine1", speed = 314, executeAt = executeAt1)

    """
    return clstub().set_machine_speed(name=name,
                                      speed=speed,
                                      executeAt=executeAt)


def set_machine_initial_angle(name="", angle=0.0):
    """
    Sets the machine initial angle.

    Args:
        name (str): machine name in the model.

        angle (float): machine angle initial value - value unit is [rad].

    Returns:
        ``True`` if the machine initial angle was set successfully, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        import math
        hil.set_machine_constant_torque_type(name = "Induction_machine1", angle = math.pi)
    """
    return clstub().set_machine_initial_angle(name=name, angle=angle)


def set_machine_initial_speed(name="", speed=0.0):
    """
    Sets the machine initial speed.

    Args:
        name (str): machine name in the model.

        speed (float): machine speed initial value -  value unit is [rad/s].

    Returns:
        ``True`` if the machine initial speed was set successfully, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        import math
        speed_rpm = 1000
        speed_init = (2*math.pi/60)*speed_rpm
        hil.set_machine_initial_speed(name = "Induction_machine1", speed = speed_init)
    """
    return clstub().set_machine_initial_speed(name=name, speed=speed)


def set_machine_inc_encoder_offset(name="", offset=0.0):
    """
    Sets the incremental encoder offset in the machine model.

    .. Note::

        This function now calls the ``set_machine_encoder_offset()`` function and will be
        deprecated soon.
        Please use ``set_machine_encoder_offset()`` instead.

    Args:
        name (str): machine name in the model.

        offset (float): incremental encoder offset value.

    Returns:
        ``True`` if the incremental encoder offset is set successfully, otherwise
        returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        hil.set_machine_inc_encoder_offset(name = "Induction_machine1", offset = 0.0)
    """
    return clstub().set_machine_encoder_offset(name=name, offset=offset)


def set_machine_sin_encoder_offset(name="", offset=0.0):
    """
    Sets the machine's sinusoidal encoder and the resolver offset.

    .. note::

        This function now calls the ``set_machine_resolver_offset()`` function and will
        be deprecated soon.
        Please use ``set_machine_encoder_offset()`` or ``set_machine_resolver_offset()``
        instead.

    Args:
        name (str): machine name in the model.

        offset (float): machine's sinusoidal encoder and the resolver offset value.

    Returns:
        ``True`` if the machine's sinusoidal encoder and the resolver offset are set
        successfully, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        hil.set_machine_sin_encoder_offset(name = "Induction_machine1", offset = 0.0)
    """
    return clstub().set_machine_resolver_offset(name=name, offset=offset)


def set_machine_encoder_offset(name="", offset=0.0):
    """
    Sets both incremental and sinusoidal encoder offset relative to the machine's
    zero angle.

    Args:
        name (str): machine name in the model.

        offset (float): encoder offset value in radians.

    Returns:
        ``True`` if everything ok, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        hil.set_machine_encoder_offset(name = "Induction_machine1", offset = 0.0)
    """
    return clstub().set_machine_encoder_offset(name=name, offset=offset)


def set_machine_resolver_offset(name="", offset=0.0):
    """
    Sets resolver offset relative to the machine's zero angle.

    Args:
        name (str): machine name in the model.

        offset (float): machine's resolver offset value in radians.

    Returns:
        * ``True`` if everything ok, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        hil.set_machine_resolver_offset(name = "Induction_machine1", offset = 0.0)
    """

    return clstub().set_machine_resolver_offset(name=name, offset=offset)


def set_pe_switching_block_control_mode(blockName="", switchName="",
                                        swControl=True, executeAt=None):
    """
    Defines the control mode for a single switch in a given power electronics switching block.

    Args:
        blockName (str): name of the power electronics switching block.

        switchName (str): switch name.

        swControl (bool): Defines the control mode. If ``True`` (software mode) the switch is controlled
                          from software (see ``set_pe_switching_block_software_value()`` function),
                          otherwise the value is defined by the assigned digital input (hardware mode).

        executeAt (int, float): executes this command at a specified simulation time.
                                If ``executeAt`` is not specified (or ``executeAt`` == None)
                                the command will be executed immediately.

    Returns:
        ``True`` if everything ok, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        # get the simulation step
        simulationStep = hil.get_sim_step()

        # calculate the execution time
        executeAt1 = simulationStep * 100000 # execute after 100000 simulation cycles

        # execute the command immediately
        hil.set_pe_switching_block_control_mode(blockName = "3ph_inverter 1", switchName = "Sa_top", swControl = True)

        # execute the command at a specified time
        hil.set_pe_switching_block_control_mode(blockName = "3ph_inverter 1", switchName = "Sa_top", swControl = True, executeAt = executeAt1)
    """
    return clstub().set_pe_switching_block_control_mode(blockName=blockName,
                                                        switchName=switchName,
                                                        swControl=swControl,
                                                        executeAt=executeAt)


def set_pe_switching_block_software_value(blockName="", switchName="", value=0, executeAt=None):
    """
    Sets the state of a single switch in a given power electronics switching block.

    Args:
        blockName (str): name of the power electronics switching block.

        switchName (str): switch name.

        value (float): software defined value (0 - switch open, 1 - switch closed).

        executeAt (int, float): executes this command at a specified simulation time.
                                If ``executeAt`` is not specified (or ``executeAt`` == None)
                                the command will be executed immediately.

    .. note::
        This function will have no effect if the hardware control mode is selected for a given switch.

    Returns:
        ``True`` if the state of a single switch is set successfully, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        # get the simulation step
        simulationStep = hil.get_sim_step()

        # calculate the execution time
        executeAt1 = simulationStep * 100000 # execute after 100000 simulation cycles

        # execute the command immediately
        hil.set_pe_switching_block_software_value(blockName = "3ph_inverter 1", switchName = "Sa_top", value = 1)

        # execute the command at a specified time
        hil.set_pe_switching_block_software_value(blockName = "3ph_inverter 1", switchName = "Sa_top", value = 1, executeAt = executeAt1)
    """
    return clstub().set_pe_switching_block_software_value(blockName=blockName,
                                                          switchName=switchName,
                                                          value=value,
                                                          executeAt=executeAt)


def set_initial_battery_soc(batteryName, initialValue):
    """
    Sets the initial value for the battery state of charge.

    .. note::
        The initial state of charge will be set on each simulation start.
        Changing state of charge during the simulation will have no effect.

    Args:
        batteryName (str): battery name

        initialValue (float): state of charge initial value.

    Returns:
        ``True`` if the initial value for the battery state of chargeything is set successfully, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        # first set the initial state of charge...
        hil.set_initial_battery_soc("Ebatt",90.0)

        # ... then start the simulation (on simulation start, the initial state of charge will be applied)
        hil.start_simulation()
    """
    return clstub().set_initial_battery_soc(batteryName=batteryName,
                                            initialValue=initialValue)


def set_scada_input_value(scadaInputName, value):
    """
    Sets the SCADA Input value.

    Args:
        scadaInputName (str): SCADA Input name whose value you want to change

        value (int, float): the value to be set.

    Returns:
        ``True`` if the SCADA Input value was set successfully, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        hil.set_scada_input_value("Sconst1.Pref", 32.00)
    """
    return clstub().set_scada_input_value(scadaInputName=scadaInputName,
                                          value=value)


def set_cp_input_value(cpCategory, cpGroup, cpInputName, value):
    """
    Sets the CP Input value.

    .. note::
        This function will be soon deprecated. Please use the ``set_scada_input_value()``
        function instead.

    Args:
        cpCategory (str): CP Input category name

        cpGroup (str): CP Input group name

        cpInputName (str): CP Input name whose value we want to change

        value (int, float): the value to be set.

    Returns:
        ``True`` if the CP Input value was set successfully, otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        hil.set_cp_input_value('Power load/source',"Sconst1",'Pref',32.00)
    """
    return clstub().set_cp_input_value(cpCategory=cpCategory,
                                       cpGroup=cpGroup,
                                       cpInputName=cpInputName,
                                       value=value)


def set_text_mode(mode):
    """
    Sets the mode of text messages which come from the API library (warnings,errors...).

    .. note::
        These modes do not affect messages from user scripts.

    Args:
        mode (str): the text mode to be used.

    Available modes:
        * RM_EMBEDDED - all text from API will be HTML text.
        * RM_SYSTEM   - all text from API will be plain text.

    The default mode is RM_EMBEDDED.

    Availability:
        * standalone scripts

    Example::

        hil.set_text_mode(hil.RM_EMBEDDED)
    """
    return clstub().set_text_mode(mode=mode)


def set_debug_level(level=0):
    """
    Sets the level of console printing.

    Args:
        level (str): indicates the debug level

            1 - only print messages from user scripts

            2 - level 1 + print API messages

            3 - level 1 + level 2 + print communication messages

    Availability:
        * standalone scripts
    """
    return clstub().set_debug_level(level=level)


def start_capture(cpSettings, trSettings, chSettings,
                  dataBuffer=[], fileName="",
                  executeAt=None, timeout=None):
    """
        Starts the capture process that will in the background collect data, return them and, if
        ``fileName`` is specified, the data will be stored in the specified file with the appropriate extension
        (.mat , .h5 , .tdms, .csv...)

        .. note::
            You cannot start another capture process if the previous one has not finished.

            To check if the previously started capture process has finished, use the ``capture_in_progress()`` function.

        Args:
            cpSettings (list): list[``decimation``, ``numberOfChannels``, ``numberOfSamples``, ``enableDigitalCapture``]

                * decimation (int): capture downsampling value.
                * numberOfChannels (int): the number of captured analog channels \
                    ( ``number_of_used_hil_devices`` * ``max_number_of_analog_channels_per_hil`` >= ``numberOfChannels`` >= 1, int value).

                    .. note::
                        ``max_number_of_analog_channels_per_hil`` depends on the connected HIL device and can be 16, 32 or 64 channels.

                        The maximum number of channels that can be captured on one HIL device must be <= ``max_number_of_analog_channels_per_hil``.

                * numberOfSamples (int): the number of captured points per one channel or ``hil.MAX_NO_SAMPLES``.

                    .. note::
                        ``numberOfSamples`` per one channel depends on ``numberOfChannels`` and must be divisible by 2.

                        The minimum number for samples per channel is 256 and the maximum number is ``max_number_of_samples_per_hil`` / ``numberOfChannels``.

                    .. note::
                        The ``max_number_of_samples_per_hil`` depends on the connected HIL device and can be 32e6 or 64e6 samples.

                    .. note::
                        In case ``numberOfSamples == hil.MAX_NO_SAMPLES``, maximal the number of samples will be used.

                * enableDigitalCapture (bool): Enable digital signal capturing.

                    .. note::
                        In case digital capture is enabled, the ``max_number_of_analog_channels_per_hil`` is reduced
                        by one, so that ``max_number_of_analog_channels`` = ``max_number_of_analog_channels_per_hil`` - 1.

                        See the ``numberOfChannels`` for more info.

            trSettings (list): list[``triggerType``, ``triggerSource``, ``threshold``, ``edge``, ``triggerOffset``, ``useFirstTriggerOccurrence``]

                * triggerType (str): type of trigger ("Analog" , "Digital" or "Forced")

                    .. note::
                        If you use the "Forced" triggerType you do not need to pass other triggerType's parameters, for example::

                            # if we use regular "triggerType"
                            # triggerType = "Analog"...
                            triggerSettings = ["Analog",1,80.0,"Rising edge",0.0]

                            #...or
                            triggerSettings = ["Analog","V( Va )",80.0,"Rising edge",50.0]

                            # triggerType = "Digital"...
                            triggerSettings = ["Digital",1,0,"Rising edge"]

                            #...or
                            # The unit will trigger to the digital input 1 of the first HIL device.
                            triggerSettings = ["Digital","HIL0 digital input 1",0,"Rising edge",0]

                            #...or
                            # The unit will trigger to the digital input 1 of the first HIL device.
                            triggerSettings = ["Digital","HIL0 digital input 1",0,"Rising edge",0]


                            #..or
                            # The unit will trigger to the digital input 1 of the second HIL device.
                            triggerSettings = ["Digital","HIL1 digital input 1",0,"Rising edge",0]


                            # ... and if we use 'Forced'
                            triggerSettings = ["Forced"]

                * triggerSource (int, str): the channel or the name of a signal that will be used for triggering (int value or string value)

                    .. note::
                        In case ``triggerType`` == 'Analog':

                            * triggerSource (int):  the value can be > 0 and <= ``numberOfChannels`` if we enter the channel number.
                            * triggerSource (string): the value is the Analog signal name that we want to use for the trigger source. \
                                Analog Signal name must be one of the signal names from the list of \
                                signals that we want to capture (``chSettings`` list, see below).

                        In case ``triggerType`` == 'Digital':

                            * triggerSource (int): the value must be > 0
                            * triggerSource (string): the value is a Digital signal name that we want to use for the trigger source.

                        In both cases:

                            The selected trigger source must be a signal that is in the list of signals for capturing!


                * threshold (float): trigger threshold.

                    .. note::
                        ``threshold`` is only used for the "Analog" type of trigger. If you use
                        the "Digital" type of trigger, you still need to provided this parameter  (for example 0.0 )

                * edge (str): trigger on "Rising edge" or "Falling edge"
                * triggerOffset (str): Defines the number of samples in percentage to capture before the trigger event \
                                       (for example 20, if the numberOfSamples is 100k, 20k samples before and 80k \
                                       samples after the trigger event will be captured)
                * useFirstTriggerOccurrence (bool) - Defines a trigger behaviour when an offset is set. \
                                        (False - any trigger occurrence will be ignored until the offset is satisfied \
                                        True - the first trigger occurrence will be used despite the desired offset) \

            chSettings (list): list[[``analog signals names``],[``digital signals names``]],
                list that contains the string name of Analog and Digital signals that we want to capture

                .. note::
                    The number of Analog signals that we capture (and specify in ``[analog signals names]`` list) must be equal to ``numberOfChannels``.

                    The number of Digital signals that we capture (and specify in ``[digital signals names]`` list) must be <= 32.

            dataBuffer (list, Queue.Queue): the buffer that will hold names of signals that were captured and the captured data

                .. note::
                    The default type of 'dataBuffer' is the Python Queue.Queue() type of buffer (more details on http://docs.python.org/2/library/queue.html?highlight=queue#Queue.Queue)

                    The second supported type is the regular Python list. For info how you need to use this type of buffer, please see the examples below.

            fileName (str): the desired name of file. If you do not specify this parameter, the captured data will not be written at all

                .. note::
                    For now the following file formats are supported: csv, mat, h5 (HDF5 - table format), tdms,
                    mf4 (ASAMMDF) and cff (COMTRADE).

            executeAt (int, float): executes this command at a specified simulation time.
                If ``executeAt`` is not specified (or ``executeAt`` == None) the command will be executed immediately.
            timeout (int): Starts a counter to abort the capture process after n seconds. When not defined, the timeout will be inf.

        Returns:
            * in the background collected data will be saved in the file (only if ``fileName`` is specified)
            * put tuple in the ``dataBuffer`` in the form: tuple(``captured_signal_names``, ``captured_data``, ``timeData``) where arguments are:
                * captured_signal_names  - a regular Python list with string names
                * captured_data - ``numpy.ndarray`` \
                    (more details on http://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.html) \
                    the data matrix where the first row contains captured data for the first signal \
                    in the 'captured_signal_names' list, and so on.
                * timeData - ``numpy.array`` that holds time data for x-axis
            * return ``True`` if everything ws OK and the capture process started successfully, \
                otherwise return ``False`` is an error occurred.

        Availability:
            * standalone scripts


        Example (using regular python list for data buffer)::

            import typhoon.api.hil as hil

            # before starting the capture process, load the model and do necessary configurations

            # decimation,numberOfChannels,numberOfSamples
            captureSettings = [1,3,1e5]
            # triggerType,triggerSource,threshold,edge,triggerOffset
            triggerSettings = ["Analog",1,0.0,"Rising edge",50.0]
            # signals for capturing
            channelSettings = ["V( Va )","V( Vb )","V( Vc )"]

            # regular Python list is used for data buffer
            capturedDataBuffer = []

            # start capture process and if everything is ok continue...
            if hil.start_capture(captureSettings,
                                 triggerSettings,
                                 channelSettings,
                                 dataBuffer = capturedDataBuffer,
                                 fileName = r'C:\captured_signals\capture_test.mat'):

                # when capturing is finished...
                while hil.capture_in_progress():
                    pass

                # unpack data from the data buffer
                # (signalsNames - list with names,
                #  yDataMatrix  - 'numpy.ndarray' matrix with data values,
                #  xData        - 'numpy.array' with time data)
                (signalsNames,yDataMatrix,xData) = capturedDataBuffer[0]

                # unpack data for the appropriate captured signals
                Va_data = yDataMatrix[0] # first row for first signal and so on
                Vb_data = yDataMatrix[1]
                Vc_data = yDataMatrix[2]


        Example (using the regular Python list for data buffer with the FirstTriggerOccurrence parameter set)::

            import typhoon.api.hil as hil

            # before starting the capture process, load the model and do necessary configurations

            # decimation,numberOfChannels,numberOfSamples
            captureSettings = [1,3,1e5]
            # triggerType,triggerSource,threshold,edge,triggerOffset,useFirstTriggerOccurrence
            # useFirstTriggerOccurrence parameter is optional, and the default value is False
            triggerSettings = ["Analog",1,0.0,"Rising edge",50.0, True]
            # signals for capturing
            channelSettings = ["V( Va )","V( Vb )","V( Vc )"]

            # regular Python list is used for data buffer
            capturedDataBuffer = []

            # start the capture process and if everything is OK continue...
            if hil.start_capture(captureSettings,
                                 triggerSettings,
                                 channelSettings,
                                 dataBuffer = capturedDataBuffer,
                                 fileName = r'C:\captured_signals\capture_test.mat'):

                # when capturing is finished...
                while hil.capture_in_progress():
                    pass

                # unpack data from the data buffer
                # (signalsNames - list with names,
                #  yDataMatrix  - 'numpy.ndarray' matrix with data values,
                #  xData        - 'numpy.array' with time data)
                (signalsNames,yDataMatrix,xData) = capturedDataBuffer[0]

                # unpack data for the appropriate captured signals
                Va_data = yDataMatrix[0] # first row for first signal and so on
                Vb_data = yDataMatrix[1]
                Vc_data = yDataMatrix[2]


        Example (using regular Python list for the data buffer with stop_capture() executed)::

            import typhoon.api.hil as hil

            # before starting the capture process, load the model and do necessary configurations

            # decimation,numberOfChannels,numberOfSamples
            captureSettings = [1,3,1e5]
            # triggerType,triggerSource,threshold,edge,triggerOffset
            triggerSettings = ["Analog",1,0.0,"Rising edge",50.0]
            # signals for capturing
            channelSettings = ["V( Va )","V( Vb )","V( Vc )"]

            # the regular Python list is used for the data buffer
            capturedDataBuffer = []

            # start the capture process and if everything is OK continue...
            if hil.start_capture(captureSettings,
                                 triggerSettings,
                                 channelSettings,
                                 dataBuffer = capturedDataBuffer,
                                 fileName = r'C:\captured_signals\capture_test.mat'):

                # some other proccessing
                sleep(Time)
                # force the capture to stop
                hil.stop_capture()

                # unpack data from the data buffer
                # (signalsNames - list with names,
                #  yDataMatrix  - 'numpy.ndarray' matrix with data values,
                #  xData        - 'numpy.array' with time data)
                (signalsNames,yDataMatrix,xData) = capturedDataBuffer[0]

                # unpack data for the appropriate captured signals
                Va_data = yDataMatrix[0] # first row for first signal and so on
                Vb_data = yDataMatrix[1]
                Vc_data = yDataMatrix[2]


        Example with digital signals (using regular Python list for the data buffer)::

            import typhoon.api.hil as hil

            #  before starting the capture process, load the model and do necessary configurations

            # decimation, numberOfChannels, numberOfSamples, enableDigitalCapture
            captureSettings = [1,3,1e5,True]
            # triggerType,triggerSource,threshold,edge,triggerOffset
            triggerSettings = ["Digital",1,0.0,"Rising edge",50.0]
            # signals for capturing
            channelSettings = [["V( Va )","V( Vb )","V( Vc )"],["HIL0 digital input 1","HIL0 digital input 2","HIL0 digital input 3"]]

            # the regular Python list is used for the data buffer
            capturedDataBuffer = []

            # start the capture process and if everything is OK continue...
            if hil.start_capture(captureSettings,
                                 triggerSettings,
                                 channelSettings,
                                 dataBuffer = capturedDataBuffer,
                                 fileName = r'C:\captured_signals\capture_test.mat'):

                # when capturing is finished...
                while hil.capture_in_progress():
                    pass

                # unpack data from the data buffer
                # (signalsNames - list with names,
                #  yDataMatrix  - 'numpy.ndarray' matrix with data values,
                #  xData        - 'numpy.array' with time data)
                (signalsNames,yDataMatrix,xData) = capturedDataBuffer[0]

                # unpack data for the appropriate captured signals
                Va_data = yDataMatrix[0] # first row for first signal and so on
                Vb_data = yDataMatrix[1]
                Vc_data = yDataMatrix[2]
                Digital1_data = yDataMatrix[3]
                Digital2_data = yDataMatrix[4]
                Digital3_data = yDataMatrix[5]


        Example when capturing only digital signals (using regular Python list for the data buffer)::

            import typhoon.api.hil as hil

            #  before starting the capture process, load the model and do necessary configurations

            # decimation, numberOfChannels, numberOfSamples, enableDigitalCapture
            captureSettings = [1,1,1e5,True]
            # triggerType,triggerSource,threshold,edge,triggerOffset
            triggerSettings = ["Digital",1,0.0,"Rising edge",50.0]
            # signals for capturing
            channelSettings = [["V( Va )"],["HIL0 digital input 1","HIL0 digital input 2","HIL0 digital input 3"]]

            # the regular Python list is used for the data buffer
            capturedDataBuffer = []

            # start the capture process and if everything is OK continue...
            if hil.start_capture(captureSettings,
                                 triggerSettings,
                                 channelSettings,
                                 dataBuffer = capturedDataBuffer,
                                 fileName = r'C:\captured_signals\capture_test.mat'):

                # when capturing is finished...
                while hil.capture_in_progress():
                    pass

                # unpack data from the data buffer
                # (signalsNames - list with names,
                #  yDataMatrix  - 'numpy.ndarray' matrix with data values,
                #  xData        - 'numpy.array' with time data)
                (signalsNames,yDataMatrix,xData) = capturedDataBuffer[0]

                # unpack data for the appropriate captured signals
                Va_data = yDataMatrix[0] # first row for first signal and so on
                Digital1_data = yDataMatrix[1]
                Digital2_data = yDataMatrix[2]
                Digital3_data = yDataMatrix[3]

        .. note::

            When using paralleled HILs (multi-HIL model), the digital signals can be defined as::

                # in this case, the digital input 1 and digital input 2 will be captured from the first HIL and the digital input 3
                # will be captured from the second HIL
                # HIL numeration : 1st HIL (HIL 0), 2nd HIL (HIL 1) etc.
                channelSettings = [["V( Va )","V( Vb )","V( Vc )"],["HIL0 digital input 1","HIL1 digital input 2","HIL1 digital input 3"]]


                # in this case, the digital input 1 will be captured from the first HIL while the digital input 2 and digital input 3
                # will be captured from the second HIL
                # HIL numeration : 1st HIL (HIL 0), 2nd HIL (HIL 1) etc.
                channelSettings = [["V( Va )","V( Vb )","V( Vc )"],["HIL0 digital input 1","HIL1 digital input 2","HIL1 digital input 3"]]


        Example (using Queue.Queue() for data buffer)::

            import typhoon.api.hil as hil
            from Queue import Queue

            #  before starting the capture process, load the model and do necessary configurations

            # decimation,numberOfChannels,numberOfSamples
            captureSettings = [1,3,1e5]
            # triggerType,triggerSource,threshold,edge,triggerOffset
            triggerSettings = ["Analog",1,0.0,"Rising edge",50.0]
            # signals for capturing
            channelSettings = ["V( Va )","V( Vb )","V( Vc )"]

            # Queue.Queue() is used for data buffer
            capturedDataBuffer = Queue()

            # start the capture process and if everything is OK continue...
            if hil.start_capture(captureSettings,
                                 triggerSettings,
                                 channelSettings,
                                 dataBuffer = capturedDataBuffer,
                                 fileName = r'C:\captured_signals\capture_test.mat'):

                # when capturing is finished...
                while hil.capture_in_progress():
                    pass

                # unpack data from the data buffer
                # (signalsNames - list with names,
                #  yDataMatrix  - 'numpy.ndarray' matrix with data values,
                #  xData        - 'numpy.array' with time data)
                (signalsNames,yDataMatrix,xData) = capturedDataBuffer.get_nowait()

                # unpack data for the appropriate captured signals
                Va_data = yDataMatrix[0] # first row for first signal and so on
                Vb_data = yDataMatrix[1]
                Vc_data = yDataMatrix[2]


        Example (using executeAt)::

            # calculate the execution time
            # execute after 100000 simulation cycles
            executeAt1 = simulationStep * 100000

            # execute the start capture command at a specified time
            if hil.start_capture(captureSettings,
                                 triggerSettings,
                                 channelSettings,
                                 dataBuffer = capturedDataBuffer,
                                 fileName = r'C:\captured_signals\capture_test.mat',
                                 executeAt = executeAt1):

                # when capturing is finished...
                while hil.capture_in_progress():
                    pass


        Example (using timeout)::

            # the capture process will be aborted after 5 seconds.
            if hil.start_capture(captureSettings,
                                 triggerSettings,
                                 channelSettings,
                                 dataBuffer = capturedDataBuffer,
                                 fileName = r'C:\captured_signals\capture_test.mat',
                                 timeout = 5):

                # when capturing is finished...
                while hil.capture_in_progress():
                    pass

        .. note::

            If the trigger is set to "Forced", the timeout value will be ignored even if it is entered.

        """
    return clstub().start_capture(cpSettings=cpSettings,
                                  trSettings=trSettings,
                                  chSettings=chSettings,
                                  dataBuffer=dataBuffer,
                                  fileName=fileName,
                                  executeAt=executeAt,
                                  timeout=timeout)


def stop_capture():
    """
    Stops the capture process.

    .. note::
        All data that was captured by a HIL device prior capture process is stopped and are going to be downloaded.

    Returns:
        ``True`` if capture stopped successfully, otherwise if an error occurred returns ``False``.

    Availability:
        * standalone scripts

    Example::

        # start capture...

        # ...do some configuration after the capture process is started...

        # ...stop the capture process
        hil.stop_capture()
    """
    return clstub().stop_capture()


def start_simulation():
    """
    Starts the simulation process.

    Returns:
        ``True`` if the simulation started successfully, otherwise if an error occurred returns ``False``.

    Availability:
        * standalone scripts

    Example::

        # load model...

        # ...do some configuration before we start the simulation...

        # ...start the simulation...
        hil.start_simulation()

        # ...do some configuration after the simulation process is started...
    """
    return clstub().start_simulation()


def stop_simulation():
    """
    Stops the simulation.

    Returns:
        ``True`` if the simulation stopped successfully, otherwise if an error occurred returns ``False``.

    Availability:
        * standalone scripts

    Example::

        # start simulation...

        # ...do some configuration after simulation process is started...

        # ...stop the simulation
        hil.stop_simulation()
    """
    return clstub().stop_simulation()


def is_simulation_running():
    """
    Returns:
        * ``True`` if simulation is running otherwise return ``False``.
            In case model is not loaded ``None`` will be returned.

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    """

    return clstub().is_simulation_running()


def check_hil_hwid():
    """
    Check hardware IDs of all connected HIL devices.

    Returns:
        status (bool): ``True`` if all HWIDs of all connected HILs are correct
            otherwise ``False`` will be returned.

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions
    """
    return clstub().check_hil_hwid()


def capture_in_progress():
    """
    Returns:
        ``True`` if the capture process is still in progress.

    Availability:
        * standalone scripts
    """
    return clstub().capture_in_progress()


def timeout_occurred():
    """
    Returns:
        ``True`` if the capture is timed out, otherwise returns False.

    Availability:
        * standalone scripts
    """
    return clstub().timeout_occurred()


def read_pv_iv_curve(name, voltage):
    """
    Gets the current and power value from the PV panel I-V curve that corresponds to a given voltage value.

    .. note::
        Current and power values are only available after the PV panel is initialized.
        Therefore, before using this function, you need to initialize the PV panel with an .ipvx or .ipv PV settings file.
        To initialize the PV panel, call the ``set_pv_input_file()`` function.

    Args:
        name (str): name of the photovoltaic.

    Returns:
        tuple(``status``, ``tuple(I,P)``).
            * status - ``True`` if everything ok, otherwise returns ``False``.
            * I - I-V current.
            * P - I-V power voltage.

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        # initialize a PV using an .ipvx PV file and set the initial illumination and temperature values
        status = hil.set_pv_input_file("PV_panel",
                                       file = r"./examples/inputs/photovoltaics/Jinko_JKM200M-72.ipvx",
                                       illumination = 1000.0,
                                       temperature = 25.0)

        # get the current and power when voltage = 30
        (status,(I,P)) = hil.read_pv_iv_curve("PV_panel",30)


    """
    return clstub().read_pv_iv_curve(name=name, voltage=voltage)


def read_analog_signal(name=""):
    """
    Reads the selected analog signal value from HIL.

    Args:
        name (str): name of the analog signal.

    Returns:
        Signal value (floating point), in case of a read error returns ``None``.

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        sigVal = hil.read_analog_signal(name = "V( Vab )")
    """
    return clstub().read_analog_signal(name=name)


def read_analog_signals(signals=()):
    """
    Reads the selected analog signals values from HIL.

    Args:
        signals (list): list of the analog signals names.

    Returns:
        list with signal values (floating point), in case of a read error returns ``None``.

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        # return a list with requested signal values
        # [V( Vab ) value, V (Vbc) value, I (Ib) value]
        signalValues = hil.read_analog_signals(signals = ["V( Vab )","V (Vbc)","I (Ib)"])
    """
    return clstub().read_analog_signals(signals=signals)


def read_digital_signal(name="", device=None):
    """
    Reads the selected digital signal value from HIL.

    Args:
        name (str): name of the digital signal.

        device (int): specifies from which device you want to read digital signal. By default, the signal will be searched on all devices.

    Returns:
        Signal value (int type), in case of a read error returns ``None``.

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        # read 'HIL0 digital input 1' digital signal (it will be searched on all devices)
        sigVal = hil.read_digital_signal(name = "HIL0 digital input 1")

        # now read the machine encoder A from the device with "device id" == 1
        sigVal = hil.read_digital_signal(name = "machine encoder A", device = 1)


    """
    return clstub().read_digital_signal(name=name, device=device)


def read_digital_signals(signals=()):
    """
    Reads the selected digital signals values from the HIL device.

    Args:
        signals (list): list of digital signal names.

    Returns:
        A list with signal values (int type), in case of a read error returns ``None``.

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        # return a list with the requested signal values
        signalValues = hil.read_digital_signals(signals = ["HIL0 digital input 1", "machine encoder A", " HIL1 digital input 13"])


    """
    return clstub().read_digital_signals(signals=signals)


def read_digital_input(pinNum=1, device=0):
    """
    Reads the selected digital input value from the HIL device.

    Args:
        pinNum (int): pin number (the channel number from 1 to 32).

        device (int): specifies from which device you want to read the digital input.

    Returns:
        The digital input value (int value), in case of a read error returns ``None``.

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        digVal = hil.read_digital_input(pinNum = 23)
    """
    return clstub().read_digital_input(pinNum=pinNum, device=device)


def read_streaming_signals(signals, from_last_index=0):
    """
    Reads data from last selected index
    of selected streaming signals values from HIL.

    Args:
        signals (list): of streaming signals names.

        from_last_index (int): from which index reading should start

            .. note::
                ``from_last_index`` arg in some case can be overwritten.

            .. note::
                All signals specified must have the same execution rate.

    Returns:
         Pandas (DataFrame) with signal names as keys and
         signal values(floating point) and time column with simulation time,
         and index of last read data. In case of read error returns ``None``.

    Example::

        # read
        data, last_index = hil.read_streaming_signals(['streaming_signal_name',
        'streaming signal_name2'])
        # get values from pandas DataFrame
        streaming_signal_name_value = data['streaming_signal_name']
        streaming_signal_name_2_value = data['streaming_signal_name2']

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions
    """
    return clstub().read_streaming_signals(signals=signals,
                                           from_last_index=from_last_index)


def load_signal_gen_data(filename: str) -> dict:
    """
    Loads data from a file and prepares it for a signal generator.
    Args:
        filename: file path.

    Returns: Dictionary with a data loaded from a file.

    """

    return clstub().load_signal_gen_data(filename=filename)


def create_signal_stimulus(signal_data):
    """
    Create signal generator object.
    Args:
        signal_data (Dictionary): data used for a signal reproduction.
        Signal names are represented as dictionary keys and signal values are represented as list of numbers.
        Time axis is defined with dictionary key 'Time' and time values are represented as list of ascending numbers.
        All signals values need to have the same size.

    Returns: ObjectHandle for created signal generator.

    """
    return clstub().create_signal_stimulus(signal_data=signal_data)


def prepare_signal_stimulus(signal_stimulus):
    """
    Prepare initial data for signal stimulus.
    It is necessary to call this function before starting signal stimulation.
    For creating signal_stimulus data, create_signal_stimulus() can be used.

    Args:
        signal_stimulus (Dictionary): stimulus to prepare.

    Returns:
        status (bool): ``True`` if everything ok, otherwise returns ``False``.
    """
    return clstub().prepare_signal_stimulus(signal_stimulus=signal_stimulus)


def start_signal_stimulus(signal_stimulus):
    """
    Start desired signal stimulus.
    Args:
        signal_stimulus (ItemHandle): signal stimulus object.

    Returns:
        status (bool): ``True`` if everything ok, otherwise returns ``False``.

    Example::

    # read
    stimulus_example = hil.create_signal_stimulus(
    {
    'Time' : [data_array],
    'signal_name1':[data_array],
    'signal_name2':[data_array]})

    hil.prepare_signal_stimulus(stimulus_example)
    hil.start_simulation()
    hil.start_signal_stimulus(stimulus_example)
    """
    return clstub().start_signal_stimulus(signal_stimulus=signal_stimulus
                                          )


def stop_signal_stimulus(signal_stimulus):
    """
    Stop desired signal stimulus.
    Args:
        signal_stimulus (ItemHandle): signal stimulus object.

    Returns:
        status (bool): ``True`` if everything ok, otherwise returns ``False``.

    Example::

    # previous created stimulus 'stimulus_example'
    hil.stop_signal_stimulus(stimulus_example)
    hil.stop_simulation()

    """

    return clstub().stop_signal_stimulus(signal_stimulus=signal_stimulus,
                                         )


def pause_signal_stimulus(signal_stimulus):
    """
    Pause desired signal stimulus.
    Args:
        signal_stimulus (ItemHandle): signal stimulus object.

    Returns:
        status (bool): ``True`` if everything ok, otherwise returns ``False``.

    Example:

    # previous created stimulus 'stimulus_example'
    hil.pause_signal_stimulus(stimulus_example)
    hil.stop_simulation()

    """
    return clstub().pause_signal_stimulus(signal_stimulus=signal_stimulus)


def reboot_hil():
    """
    Reboots all connected HIL devices.

    .. note::
        After rebooting a HIL, model (.cpd file) should be loaded again.

    Returns:
        status (bool): ``True`` if everything ok, otherwise returns ``False``.

    Availability:
        * standalone scripts

    """
    return clstub().reboot_hil()


def wait_sec(sec):
    """
    Waits for a specified time in seconds.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        # ...some code

        # pause execution for 3 seconds
        hil.wait_sec(3)

        # ...code after wait_sec() command will be executed after 'waiting' period is expired
    """
    return clstub().wait_sec(sec=sec)


def wait_msec(msec):
    """
    Waits for a specified time in milliseconds.

    Availability:
        * standalone scripts
        * macro scripts

    Example::

        # ...some code

        # pause execution for 500 milliseconds
        hil.wait_msec(500)

        # ...code after wait_msec() command will be executed after 'waiting' period is expired
    """
    clstub().wait_msec(msec=msec)


def wait_on_user():
    """
    Waits on a user action - 'ENTER' needs to be pressed to continue with the script execution.

    Availability:
        * standalone scripts

    Example::

        # ...some code

        # pause execution until the user presses 'ENTER'
        hil.wait_on_user()

        # ...code after wait_on_user() command will be executed immediately after user presses 'ENTER'
    """
    clstub().wait_on_user()


def end_script_by_user():

    """
    Terminates the script execution by pressing 'ENTER'.

    Availability:
        * standalone scripts

    Example::

        # ...some code

        # ends the execution of the current script by pressing 'ENTER'
        hil.end_script_by_user()

        # after the user presses 'ENTER', the script execution will be terminated...
        # ...and any commands after end_script_by_user() command will not be executed


    """
    clstub().end_script_by_user()


def reset_flag_status(flag, device=0):
    """
    Resets the status of a given flag.

    Args:
        flag (str): name of the flag whose status you want to reset.

        device (int): specifies on which device you want to reset the flag status.

    Supported flags (which can be used in the ``flaq`` parameter) and their description is listed below.

    +--------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------+
    |       Flag constant      |   Description                                                                                                                                        |
    +==========================+======================================================================================================================================================+
    |  FL_ARITHMETIC_OVERFLOW  | Indicates that some values from the model being simulated were out of the HIL device's numerical range. It may be followed by erratic model behavior.|
    +--------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------+
    |       FL_DEAD_TIME       | Indicates a shoot-through condition on a phase lag caused by gate drive digital inputs.                                                              |
    +--------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------+
    |    FL_SP_EXC_OCCURRED    | Indicates that an exception is thrown by the generated code running on either System or User CPU.                                                    |
    +--------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------+
    |    FL_COMP_INT_OVERRUN   | Indicates that SP computation time exceeded the reserved time slot.                                                                                  |
    +--------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------+

    Returns:
        ``True`` if the flag is reset successfully , otherwise returns ``False``.

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        import typhoon.api.hil as hil

        # reset Dead Time flag status
        status = hil.reset_flag_status(hil.FL_DEAD_TIME)
    """
    return clstub().reset_flag_status(flag=flag, device=device)


def get_model_variables(name_separator="."):
    """
    Returns all Model variables and theirs Attributes values from loaded Model.

    Args:
        name_separator (str): separator used to divide Model variable name's
            components. All Model variables' names will use this separator.
            Currently supported separators are: ".", "/"

            Example::

                # name of a Model variable with default '.' separator
                {"PV_panel.illumination": {
                    "att_value_type": "float",
                    "att_access_rights": "write_only",
                    "att_hil_device": 0},
                "Vgrid.rms": {
                    "att_value_type": "float",
                    "att_access_rights": "write_only",
                    "att_hil_device": 0},
                ...
                }

                # name of a Model variable with '/' separator
                {"PV_panel/illumination": {
                    "att_value_type": "float",
                    "att_access_rights": "write_only",
                    "att_hil_device": 0},
                "Vgrid/rms": {
                    "att_value_type": "float",
                    "att_access_rights": "write_only",
                    "att_hil_device": 0},
                ...
                }

    Returns:
        variable dictionary (dict): dictionary in format::

            {"variable_name_1": {
                "attribute_name_1": attribute_value_1,
                "attribute_name_2": attribute_value_2, ...}
            }
            "variable_name_2": {
                "attribute_name_1": attribute_value_1,
                "attribute_name_2": attribute_value_2, ...}
            }, ...}

    Raises:
        HILAPIException: in case information about available Model
            variables cannot be acquired.
        HILAPIException: in case unsupported separator was given.
    """

    return clstub().get_model_variables(name_separator=name_separator)


def get_cp_output_value(cpCategory, cpGroup, cpOutputName):
    """
    Gets, i.e. reads, the CP Output value.

    .. note::
        This function will be soon deprecated. Please use the ``get_scada_output_value()``
        instead.

    Args:
        cpCategory (str): CP Output category name

        cpGroup (str): CP Output group name

        cpOutputName (str): CP Output name whose value you want to read

    Returns:
        The value read from the CP Output if everything is OK, otherwise returns ``None``.

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        hil.get_cp_output_value('Power load/source','Sconst1",'Active power')
    """
    return clstub().get_cp_output_value(cpCategory=cpCategory,
                                        cpGroup=cpGroup,
                                        cpOutputName=cpOutputName)


def get_scada_output_value(scadaOutputName):
    """
    Gets the SCADA Output value.

    Args:
        scadaOutputName (str): SCADA Output name whose value you want to read

    Returns:
        The value read from the SCADA Output if everything is OK, otherwise returns ``None``.

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        value = hil.get_scada_output_value('Sconst1.Active power')
    """
    return clstub().get_scada_output_value(scadaOutputName=scadaOutputName)


def get_battery_soc(batteryName):
    """
    Gets, i.e. reads, the battery's state of charge.

    .. note::
        The state-of-charge value will be returned in a range between 0.0 and 1.0.

    Args:
        batteryName (str): battery name

    Returns:
        The state-of-charge value if everything is OK, otherwise returns ``None``.

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expression

    Example::

        # get the battery's state of charge
        hil.get_battery_soc("Ebatt")


    """
    return clstub().get_battery_soc(batteryName=batteryName)


def get_pv_mpp(name):
    """
    Gets, i.e. reads, the maximal power current and voltage for the given photovoltaic panel.

    .. note::
        The maximal power and current are only available after the PV panel is initialized.
        Therefore, before using this function you need to initialize the PV panel with an .ipvx or .ipv PV settings file.
        To initialize the PV panel, call the ``set_pv_input_file()`` function.

    Args:
        name (str): name of the photovoltaic.

    Returns:
        tuple(``status``, ``tuple(Imp,Vmp)``).
            * status - ``True`` if everything is OK, otherwise returns ``False``.
            * Imp - maximal power current.
            * Vmp - maximal power voltage.

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        # initializes the PV using an .ipvx PV file and sets the initial illumination and temperature values
        status = hil.set_pv_input_file("PV_panel",
                                       file = r"./examples/inputs/photovoltaics/Jinko_JKM200M-72.ipvx",
                                       illumination = 1000.0,
                                       temperature = 25.0)

        # changes both the illumination and temperature parameters
        (status,(Imp,Vmp)) = hil.get_pv_mpp("PV_panel")


    """
    return clstub().get_pv_mpp(name=name)


def get_num_of_connected_hils():
    """
    Returns the number of currently connected HIL devices.

    Returns:
        int
    """
    return clstub().get_num_of_connected_hils()


def get_sim_step(device=0):
    """
    Gets the simulation time step of the active model.

    Args:
        device (int): specifies for which device you want to get the simulation time step

    Returns:
        The simulation time step in seconds (floating value). If an error occurred ``None`` will be returned instead.

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        simulationStep = get_sim_step()
    """
    return clstub().get_sim_step(device=device)


def get_sim_time(device=0):
    """
    Gets the simulation time. The simulation time is read as a number of elapsed simulation steps (cycles) multiplied with the model simulation step.

    Args:
        device (int): specifies for which device you want to get the simulation time

    Returns:
        The simulation time value (float value), in case of an error returns ``None``.

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        simulationTime = get_sim_time()
    """
    return clstub().get_sim_time(device=device)


def _server_running():
    """
    Checks if server with Typhoon HIL software is up and running.

    Returns:
        True if it is running, False otherwise.
    """
    return clstub(connect=False).server_running()


def get_device_cfg_list():
    """
    Returns the list of available devices and their FW configurations.

    Returns:
        Dictionary of available devices (keys) with a list of their FW configurations (values).

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions
    """

    return clstub().get_device_cfg_list()


def get_sw_version():
    """
    Returns a string which contains the Typhoon software version.

    Returns:
        A string that contains the current software version

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions
    """

    return clstub().get_sw_version()


def get_hil_calibration_date(device_id=0):
    """
    Returns the calibration date of the connected HIL device.

    Args:
        device_id (int): specifies for which device you want to get the calibration date.
            By default, the calibration date is returned for the device with device_id == 0.

    Returns:
        A string that contains the HIL device calibration date or ''None'' if the device does not exist.

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions
    """

    return clstub().get_hil_calibration_date(device_id=device_id)


def get_device_features(device=None, conf_id=None, feature=None):
    """
    Provides information about the features of the selected HIL device.

    Args:
        device (str): HIL device name (in format 'HIL604', 'HIL402'...)

        conf_id (int): HIL configuration id

        feature (str): feature name whose value will be returned. If ``feature`` is not provided,
            information about all features will be returned.

    .. note::
        In case either the parameter `device` or `conf_id` is not specified, unspecified parameter(s) will be auto-detected from the connected HIL device.

    Returns:
        If ``feature`` is not defined, returns a dictionary with all available features (keys) and their values.
        However, if ``feature`` is defined, it returns the value of the specific feature.

        In case an error occurred, ``None`` will be returned.

    The format of the returned dictionary is displayed below.

    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | Dictionary key                                 | Meaning                                                                  | Value  |
    +================================================+==========================================================================+========+
    | "Number of SPCs"                               | Number of SPC                                                            | int    |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "Machine solvers"                              | Number of machine solvers                                                | int    |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "Signal generators"                            | Number of signal generators                                              | int    |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "Look Up Tables"                               | Number of LUTs                                                           | int    |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "PWM modulators"                               | Number of PWM modulators                                                 | int    |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "PWM analyzers"                                | Number of PWM analyzers                                                  | int    |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "SPC peak processing power [GMACS]"            | SPC peak processing power                                                | float  |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "SPC matrix memory [Kwords]"                   | SPC matrix memory                                                        | float  |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "SPC output memory size [variables]"           | SPC output memory size                                                   | int    |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "Max converter weight (ideal switches) / SPC"  | Max converter weight                                                     | int    |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "Contactors (ideal switches) / SPC"            | Number of contactors                                                     | int    |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "Non-ideal switches / SPC"                     | Number of non-ideal switches                                             | int    |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "Time varying elements / SPC"                  | Number of time varying elements                                          | int    |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "Comparators / SPC"                            | Number of comparators per SPC                                            | int    |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "Switching delay"                              | Switching delay support                                                  | bool   |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "Converter power loss calculation"             | Power loss calculation support                                           | bool   |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "Time commands support"                        | Time commands support                                                    | bool   |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "Digital inputs"                               | Number of HIL digital inputs                                             | int    |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "Digital outputs"                              | Number of HIL digital outputs                                            | int    |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "Analog inputs"                                | Number of HIL analog inputs                                              | int    |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "Analog outputs"                               | Number of HIL analog outputs                                             | int    |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "Analog inputs voltage range"                  | HIL analog inputs voltage range (ex. [-10, 10])                          | list   |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "Analog outputs voltage range"                 | HIL analog outputs voltage range (ex. [-10, 10])                         | list   |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "Multi HIL devices"                            | Max number of devices which can be connected in multi HIL configuration  | int    |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "Can bus ports"                                | Number of CAN bus ports                                                  | int    |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "Scope digital signals"                        | Number of available scope digital channels                               | int    |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "Scope analog signals"                         | Number of available scope analog channels                                | int    |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "Scope buffer size"                            | Maximum supported capture number of samples                              | int    |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "Max number of digital probes"                 | Maximum number of digital probes in the model                            | int    |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+
    | "Max number of analog probes"                  | Maximum number of analog probes in the model                             | int    |
    +------------------------------------------------+--------------------------------------------------------------------------+--------+


    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    """

    return clstub().get_device_features(device=device,
                                        conf_id=conf_id,
                                        feature=feature)


def get_hw_info():
    """
    Gets hardware information of the connected HIL unit.

    .. note::
        This function will return information about connected HIL device only if it is called after model is loaded.

    Returns:
        tuple(``product ID``, ``device ID``, ``configuration ID``, ``Firmware release date``).

        If an error occurred ``None`` will be returned instead.
            * product ID (str): product ID in the format "HIL402, HIL604...".
            * device ID (int): HIL device ID.
            * configuration ID (int): HIL configuration ID.
            * Firmware release date (str): Firmware release date in the "year-month-day" format .

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        (productID,deviceID,configurationID,fwReleaseDate) = hil.get_hw_info()

    """
    return clstub().get_hw_info()


def get_flag_status(flag, device=0):
    """
    Reads and returns the status of the given flag from the HIL device.

    Args:
        flag (str): name of the flag whose status you want to read.

        device (int): specifies from which device you will read the flag.

    Supported flags and their descriptions are listed below.

    +--------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
    |       Flag constant      |   Description                                                                                                                                      |
    +==========================+====================================================================================================================================================+
    |  FL_ARITHMETIC_OVERFLOW  | Indicates that some values from the model being simulated were out of HIL device numerical range. It may be followed by erratic model behavior.    |
    +--------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
    |       FL_DEAD_TIME       | Indicates shoot through condition on a phase lag caused by gate drive digital inputs.                                                              |
    +--------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
    |      FL_SERIAL_LINK      | Indicates that serials link between HIL devices is down.                                                                                           |
    +--------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
    |    FL_COMP_INT_OVERRUN   | Indicates that SP computation time exceeded the reserved time slot.                                                                                |
    +--------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
    |     FL_SP_CPU_STALLED    | Indicates that SP CPU is stalled during execution.                                                                                                 |
    +--------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
    |    FL_SP_EXC_OCCURRED    | Indicates that an exception is thrown by the generated code running on either System or User CPU.                                                  |
    +--------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+
    |    FL_PSU_STATUS         | Indicates status of the externally available power supply outputs.                                                                                 |
    +--------------------------+----------------------------------------------------------------------------------------------------------------------------------------------------+


    Returns:
        ``True`` if a flag is raised, otherwise returns ``False``. In case an error occurred, an appropriate message will be displayed and ``None`` will be returned.

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        import typhoon.api.hil as hil

        # get the dead time violation flag status
        dtv_flag = hil.get_flag_status(hil.FL_DEAD_TIME)
    """
    return clstub().get_flag_status(flag=flag, device=device)


def get_sources():
    """
    Returns the list of all independent voltage/current sources in the model.

    Returns:
        List of source names grouped by HIL device if everything is OK, otherwise returns an empty list.

    .. note::
        The returned list will be in the following format:
        [[device 0 sources], [device 1 sources], ...[device N sources]] where [device N sources] is [source_1_name, source_2_name, ... source_n_name]

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        import typhoon.api.hil as hil

        # get the list of all source names in the loaded model
        sources = hil.get_sources()
    """
    return clstub().get_sources()


def get_pvs():
    """
    Returns the list of all photovoltaic panels in the model.

    Returns:
        List of pvs names grouped by HIL device if everything is OS, otherwise returns an empty list.

    .. note::
        The returned list will be in the following format:
        [[device 0 pvs], [device 1 pvs], ...[device N pvs]] where [device N pvs] is [pvs_1_name, pvs_2_name, ... pvs_n_name]

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        import typhoon.api.hil as hil

        # get the list of all pvs names in the loaded model
        pvs = hil.get_pvs()
    """
    return clstub().get_pvs()


def get_analog_signals():
    """
    Returns the list of all analog signals in the model.

    Returns:
        List of analog signal names grouped by HIL device if everything is OK, otherwise returns an empty list.

    .. note::
        The returned list will be in the following format:
        [[device 0 analog signals], [device 1 analog signals], ...[device N analog signals]] where [device N analog signals] is [a_sig_1_name, a_sig_2_name, ... a_sig_n_name]

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        import typhoon.api.hil as hil

        # get the list of all analog signal names in the loaded model
        analogSignals = hil.get_analog_signals()
    """
    return clstub().get_analog_signals()


def get_digital_signals():
    """
    Returns the list of all digital signals in the model.

    Returns:
        List of digital signal names grouped by HIL device if everything is OK, otherwise returns an empty list.

    .. note::
        The returned list will be in the following format:
        [[device 0 digital signals], [device 1 digital signals], ...[device N digital signals]] where [device N digital signals] is [d_sig_1_name, d_sig_2_name, ... d_sig_n_name]

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        import typhoon.api.hil as hil

        # get the list of all digital signal names in the loaded model
        digitalSignals = hil.get_digital_signals()
    """
    return clstub().get_digital_signals()


def get_streaming_analog_signals():
    """
    Returns the list of all streaming analog signals in the model.

    Returns:
        signals (list): of streaming analog signals names grouped by HIL device if everything ok, otherwise returns empty list.

    .. note::
        Returned list will be in the format:

        [[device 0 streaming analog signals], [device 1 streaming analog signals], ...[device N streaming analog signals]]

        where [device N streaming analog signals] is [a_sig_1_name, a_sig_2_name, ... a_sig_n_name]

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        import typhoon.api.hil as hil

        # get list of all streaming analog signals names in the loaded model
        streaming_analog_signals = hil.get_streaming_analog_signals()
    """

    return clstub().get_streaming_analog_signals()


def get_streaming_digital_signals():
    """
    Returns the list of all streaming digital signals in the model.

    Returns:
        signals (list): of streaming digital signals names grouped by HIL device if everything ok, otherwise returns empty list.

    .. note::
        Returned list will be in the format:

        [[device 0 streaming digital signals], [device 1 streaming digital signals], ...[device N streaming digital signals]]

        where [device N streaming digital signals] is [d_sig_1_name, d_sig_2_name, ... d_sig_n_name]

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        import typhoon.api.hil as hil

        # get list of all streaming digital signals names in the loaded model
        streaming_digital_signals = hil.get_streaming_digital_signals()
    """

    return clstub().get_streaming_digital_signals()


def get_contactors():
    """
    Returns the list of all contactors in the model.

    Returns:
        List of contactor names grouped by HIL device if everything is OK, otherwise returns an empty list.

    .. note::
        The returned list will be in the following format:
        [[device 0 contactors], [device 1 contactors], ...[device N contactors]] where [device N contactors] is [cont_1_name, cont_2_name, ... cont_n_name]

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        import typhoon.api.hil as hil

        # get the list of all contactor names in the loaded model
        contactors = hil.get_contactors()
    """
    return clstub().get_contactors()


def get_machines():
    """
    Returns the list of all machines in the model.

    Returns:
        List of machine names grouped by HIL device if everything is OK, otherwise returns an empty list.

    .. note::
        The returned list will be in the following format:
        [[device 0 machines], [device 1 machines], ...[device N machines]] where [device N machines] is [mch_1_name, mch_2_name, ... mch_n_name]

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        import typhoon.api.hil as hil

        # get the list of all machine names in the loaded model
        machines = hil.get_machines()
    """
    return clstub().get_machines()


def get_pe_switching_blocks():
    """
    Returns the list of all software controllable power electronics switching blocks in the model.

    Returns:
        List of software controllable power electronics switching block names grouped by HIL device if everything is OK, otherwise returns an empty list.

    .. note::
        The returned list will be in the following format:
        [[device 0 sw_blocks], [device 1 sw_blocks], ...[device N sw_blocks]] where [device N sw_blocks] is [swch_1_name, swch_2_name, ... swch_n_name]

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        import typhoon.api.hil as hil

        # get the list of all switching block names in the loaded model
        switchingBlocks = hil.get_pe_switching_blocks()
    """
    return clstub().get_pe_switching_blocks()


def get_scada_inputs():
    """
    Returns the list of all SCADA inputs in the model.

    Returns:
        List of SCADA input names grouped by HIL device if everything is OK, otherwise returns an empty list.

    .. note::
        The returned list will be in the following format:
        [[device 0 scada_inputs], [device 1 scada_inputs], ...[device N scada_inputs]] where [device N scada_inputs] is
        [scada_input_1_name, scada_input_2_name, ... scada_input_n_name]

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        import typhoon.api.hil as hil

        # get the list of all SCADA input names in the loaded model
        scada_inputs = hil.get_scada_inputs()
    """
    return clstub().get_scada_inputs()


def get_scada_outputs():
    """
    Returns the list of all SCADA outputs in the model.

    Returns:
        List of SCADA output names grouped by HIL device if everything is OK, otherwise returns an empty list.

    .. note::
        The returned list will be in the following format:
        [[device 0 scada_outputs], [device 1 scada_outputs], ...[device N scada_outputs]] where [device N scada_outputs] is
        [scada_output_1_name, scada_output_2_name, ... scada_output_n_name]

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        import typhoon.api.hil as hil

        # get the list of all SCADA output names in the loaded model
        scada_outputs = hil.get_scada_outputs()
    """
    return clstub().get_scada_outputs()


def get_source_settings(name):
    """
    Returns the settings parameters of the source with the given name.

    Args:
        name (str): Name of a source
    Returns:
        Dictionary with the source settings or ``None`` if the source with the given name cannot be found.

    +-----------------+-----------------------------+-------------------------------------------------------------------------+
    |  Dictionary key | Meaning                     | Value                                                                   |
    +=================+=============================+=========================================================================+
    | "source_type"   | Type of Source              | string ("One Phase Source", "Two Phase Source" or "Three Phase Source") |
    +-----------------+-----------------------------+-------------------------------------------------------------------------+
    | "input_type"    | Type of Source input        | string ("Arbitrary", "Constant" or "Sine")                              |
    +-----------------+-----------------------------+-------------------------------------------------------------------------+
    | "scaling_value" | Source scaling value        | float                                                                   |
    +-----------------+-----------------------------+-------------------------------------------------------------------------+

    Depending on the ``source_type`` and ``input_type``, additional settings parameters are:

    * ``One Phase Source`` source

        * ``Arbitrary`` input type

            +-----------------+-------------------------------+-------------+
            | Dictionary key  | Meaning                       | Value       |
            +=================+===============================+=============+
            | "file"          | Full path to a waveform file  | string      |
            +-----------------+-------------------------------+-------------+


        * ``Constant`` input type

            +-----------------+-----------------+---------+
            | Dictionary key  | Meaning         | Value   |
            +=================+=================+=========+
            | "value"         | Constant value  | float   |
            +-----------------+-----------------+---------+


        * ``Sine`` input type

            +---------------------+---------------------------------------------+---------------------------------------------------------------------------------------+
            | Dictionary key      | Meaning                                     | Value                                                                                 |
            +=====================+=============================================+=======================================================================================+
            | "rms"               | Signal RMS value                            | float                                                                                 |
            +---------------------+---------------------------------------------+---------------------------------------------------------------------------------------+
            | "frequency"         | Signal frequency                            | float                                                                                 |
            +---------------------+---------------------------------------------+---------------------------------------------------------------------------------------+
            | "phase"             | Signal phase                                | float                                                                                 |
            +---------------------+---------------------------------------------+---------------------------------------------------------------------------------------+
            | "harmonics_active"  | Are harmonics active?                       | bool                                                                                  |
            +---------------------+---------------------------------------------+---------------------------------------------------------------------------------------+
            | "harmonics"         | List of harmonics defined in absolute units | list [(harmonic_number_1,rms_1,phase_1),...(harmonic_number_n,rms_n,phase_n)].        |
            +---------------------+---------------------------------------------+---------------------------------------------------------------------------------------+
            | "harmonics_pu"      | List of harmonics defined in relative units | list [(harmonic_number_1,rms_pu_1,phase_1),...(harmonic_number_n,rms_pu_n,phase_n)]   |
            +---------------------+---------------------------------------------+---------------------------------------------------------------------------------------+

    * ``Two Phase Source`` and ``Three Phase Source`` source type have the same settings parameters as when the ``One Phase Source`` with ``Sine`` input type is used


    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        # list of harmonics
        harmonics_pu = []

        # tuples that contains harmonic settings
        # (harmonic_number,rms,phase)
        harmonic1 = (3, 0.1, 0)
        harmonic2 = (5, 0.05, 90)
        harmonic3 = (7, 0.03, 270)

        # store harmonics
        harmonics_pu.append(harmonic1)
        harmonics_pu.append(harmonic2)
        harmonics_pu.append(harmonic3)

        # set a three-phase source
        hil.set_source_sine_waveform("Vb", rms = 250, frequency = 50, phase = 120, harmonics_pu = harmonics_pu)

        # get source settings parameters
        source_settings = hil.get_source_settings("Vb")

        # unpack parameters from dictionary
        source_type      = source_settings["source_type"]
        input_type       = source_settings["input_type"]
        rms              = source_settings["rms"]
        frequency        = source_settings["frequency"]
        phase            = source_settings["phase"]
        harmonics_active = source_settings["harmonics_active"]
        harmonics        = source_settings["harmonics"]
        harmonics_pu     = source_settings["harmonics_pu"]

    """
    return clstub().get_source_settings(name=name)


def get_pv_panel_settings(name):
    """
    Returns the settings parameters of the PV panel with the given name.

    Args:
        name (str): Name of a PV panel

    Returns:
        Dictionary with the PV panel settings, or ``None`` if the PV panel with
            the given name cannot be found.

    +-----------------+-----------------------------------------------------------------------+--------+
    | Dictionary key  | Meaning                                                               | Value  |
    +=================+=======================================================================+========+
    | "file"          | Full path to the PV panel initialization file (old .ipv or new .ipvx) | string |
    +-----------------+-----------------------------------------------------------------------+--------+
    | "illumination"  | Illumination value of the PV panel                                    | float  |
    +-----------------+-----------------------------------------------------------------------+--------+
    | "temperature"   | Temperature value of the PV panel                                     | float  |
    +-----------------+-----------------------------------------------------------------------+--------+
    | "isc"           | current scaling factor value of PV panel                              | float  |
    +-----------------+------------------------------------------------------------------------+-------+
    | "voc"           | voltage scaling factor value of PV pane                               | float  |
    +-----------------+-----------------------------------------------------------------------+--------+

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        # initialize the PV using an .ipvx PV file and set the initial illumination and temperature values
        status = hil.set_pv_input_file("PV_panel",
                                       file = r"./examples/inputs/photovoltaics/Jinko_JKM200M-72.ipvx",
                                       illumination = 1000.0,
                                       temperature = 25.0)

        # or use this for IV normalized generator
         status = hil.set_pv_input_file("PV_panel",
                                file = r"./examples/inputs/photovoltaics/IV_Normalized.ipvx",
                                isc = 10.0,
                                voc = 25.0)

        # get the PV panel settings parameters
        pv_settings = hil.get_pv_panel_settings("PV_panel")

        # unpack the parameters from the dictionary
        pv_file      = pv_settings["file"]
        illumination = pv_settings["illumination"]
        temperature  = pv_settings["temperature"]
        voc          = pv_settings["voc"]
        isc          = pv_settings["isc"]

    """
    return clstub().get_pv_panel_settings(name=name)


def get_machine_settings(name):
    """
    Returns settings parameters of a machine with the given name.

    Args:
        name (str): Name of a machine

    Returns:
        Dictionary with the machine settings or ``None`` if the machine with the given name cannot be found.

    +--------------------------+------------------------------------------------+---------------------------------------+
    | Dictionary key           | Meaning                                        | Value                                 |
    +==========================+================================================+=======================================+
    | "load_source"            | Machine torque load source                     | String ("Software" or "External")     |
    +--------------------------+------------------------------------------------+---------------------------------------+
    | "load_type"              | Machine load type                              | String ("Torque" or "Speed")          |
    +--------------------------+------------------------------------------------+---------------------------------------+
    | "external_torque_type"   | Machine external torque load type              | String ( "Frictional" or "Potential") |
    +--------------------------+------------------------------------------------+---------------------------------------+
    | "speed"                  | Machine speed                                  | float                                 |
    +--------------------------+------------------------------------------------+---------------------------------------+
    | "constant_torque"        | Machine constant load torque                   | float                                 |
    +--------------------------+------------------------------------------------+---------------------------------------+
    | "constant_torque_type"   | Machine constant load torque type              | String ( "Frictional" or "Potential") |
    +--------------------------+------------------------------------------------+---------------------------------------+
    | "linear_torque"          | Machine linear load torque coefficient         | float                                 |
    +--------------------------+------------------------------------------------+---------------------------------------+
    | "square_torque"          | Machine square load torque coefficient         | float                                 |
    +--------------------------+------------------------------------------------+---------------------------------------+
    | "initial_angle"          | Machine initial angle                          | float                                 |
    +--------------------------+------------------------------------------------+---------------------------------------+
    | "initial_speed"          | Machine initial speed                          | float                                 |
    +--------------------------+------------------------------------------------+---------------------------------------+
    | "inc_encoder_offset"     | Machine incremental encoder offset             | float                                 |
    +--------------------------+------------------------------------------------+---------------------------------------+
    | "sin_encoder_offset"     | Machine sinusoidal encoder and resolver offset | flaot                                 |
    +--------------------------+------------------------------------------------+---------------------------------------+

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        # initialize the machine
        hil.set_machine_load_source(name="machine 1", software = True)
        hil.set_machine_load_type(name="machine 1", torque = True)
        hil.set_machine_constant_torque(name="machine 1",value=2.5)
        hil.set_machine_constant_torque_type(name="machine 1",frictional=True)
        hil.set_machine_linear_torque(name="machine 1",value=5.0)
        hil.set_machine_square_torque(name="machine 1",value=6.0)
        hil.set_machine_initial_angle(name="machine 1",angle=3.14)
        hil.set_machine_initial_speed(name="machine 1",speed=100.0)
        hil.set_machine_encoder_offset(name="machine 1",offset=3.14)
        hil.set_machine_sin_encoder_offset(name="machine 1",offset=1.57)

        # get the machine settings parameters
        machine_settings = hil.get_machine_settings("machine 1")

        # unpack the parameters from the dictionary
        load_source             = machine_settings["load_source"]
        load_type               = machine_settings["load_type"]
        external_torque_type    = machine_settings["external_torque_type"]
        speed                   = machine_settings["speed"]
        constant_torque         = machine_settings["constant_torque"]
        constant_torque_type    = machine_settings["constant_torque_type"]
        linear_torque           = machine_settings["linear_torque"]
        square_torque           = machine_settings["square_torque"]
        initial_angle           = machine_settings["initial_angle"]
        initial_speed           = machine_settings["initial_speed"]
        inc_encoder_offset      = machine_settings["inc_encoder_offset"]
        sin_encoder_offset      = machine_settings["sin_encoder_offset"]


    """
    return clstub().get_machine_settings(name=name)


def get_pe_switching_block_settings(blockName="", switchName=""):
    """
    Returns settings parameters of a single switch in a given power electronics switching block.

    Args:
        blockName (str): name of the power electronics switching block.

        switchName (str): the name of the switch .

    Returns:
        Dictionary with the switch settings, or ``None`` if the switch with the given name cannot be found.

    +-----------------------------+-------------------------------------------------------------------------------------+---------+
    | Dictionary key              | Meaning                                                                             | Value   |
    +=============================+=====================================================================================+=========+
    | "software_control_enabled"  | Is software mode for a single switch in a power electronics switching block active? | boolean |
    +-----------------------------+-------------------------------------------------------------------------------------+---------+
    | "software_value"            | State of a single switch in a power electronics switching block                     | int     |
    +-----------------------------+-------------------------------------------------------------------------------------+---------+

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        # initialize switching blocks
        hil.set_pe_switching_block_control_mode(blockName = "3ph_inverter 1", switchName = "Sa_top", swControl = True)
        hil.set_pe_switching_block_software_value(blockName = "3ph_inverter 1", switchName = "Sa_top", value = 1)

        # get the switch settings parameters
        switch_settings = hil.get_pe_switching_block_settings(blockName = "3ph_inverter 1", switchName = "Sa_top")

        # unpack the parameters from the dictionary
        software_control_enabled  = switch_settings["software_control_enabled"]
        software_value            = switch_settings["software_value"]

    """
    return clstub().get_pe_switching_block_settings(blockName=blockName,
                                                    switchName=switchName)


def get_contactor_settings(name):
    """
    Returns settings parameters of a contactor with the given name.

    Args:
        name (str): Name of a contactor

    Returns:
        Dictionary with the contactor settings, or ``None`` if the contactor with given name cannot be found.

    +-----------------------------+--------------------------------------------+-------------------------------+
    | Dictionary key              | Meaning                                    | Value                         |
    +=============================+============================================+===============================+
    | "software_control_enabled"  | Is contactor software control mode active? | boolean                       |
    +-----------------------------+--------------------------------------------+-------------------------------+
    | "software_value"            | Contactor software state                   | string ("Opened" or "Closed") |
    +-----------------------------+--------------------------------------------+-------------------------------+

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        # initialize the contactor
        hil.set_contactor_control_mode('contactor_disch', swControl = True, swState = True)

        # get contactor settings parameters
        contactor_settings = hil.get_contactor_settings('contactor_disch')

        # unpack the parameters from the dictionary
        software_control_enabled  = contactor_settings["software_control_enabled"]
        software_value            = contactor_settings["software_value"]

    """
    return clstub().get_contactor_settings(name=name)


def get_analog_output_settings(channel, device=0):
    """
    Returns settings parameters of an analog output channel.

    Args:
        channel (int): Analog output channel number

        device (int): HIL device ID to which the desired analog output channel belongs

    Returns:
        Dictionary with the analog output channel settings, or ``None`` if the analog output channel cannot be found.

    +----------------+-----------------------------+------------------------------------------+
    | Dictionary key | Meaning                     | Value                                    |
    +================+=============================+==========================================+
    | "signal_name"  | Assigned analog signal name | string or None if signal is not assigned |
    +----------------+-----------------------------+------------------------------------------+
    | "scaling"      | Scaling value               | float                                    |
    +----------------+-----------------------------+------------------------------------------+
    | "offset"       | Offset value                | float                                    |
    +----------------+-----------------------------+------------------------------------------+

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        # initialize the analog output channel
        hil.set_analog_output(1, "V( V0 )", scaling = 100, offset = 0, device = 0)

        # get the analog output settings parameters
        channel_settings = hil.get_analog_output_settings(channel = 1, device = 0)

        # unpack the parameters from the dictionary
        signal_name  = channel_settings["signal_name"]
        scaling      = channel_settings["scaling"]
        offset       = channel_settings["offset"]

    """
    return clstub().get_analog_output_settings(channel=channel, device=device)


def get_digital_output_settings(channel, device=0):
    """
    Returns settings parameters of a digital output channel.

    Args:
        channel (int): Digital output channel number

        device (int): HIL device ID to which the desired digital output channel belongs

    Returns:
        Dictionary with the digital output channel settings, or ``None`` if the digital output channel cannot be found.

    +----------------------------+---------------------------------------+---------+
    | Dictionary key             | Meaning                               | Value   |
    +============================+=======================================+=========+
    | "signal_name"              | Assigned digital signal name          | string  |
    +----------------------------+---------------------------------------+---------+
    | "inverted"                 | Is digital output inverted?           | boolean |
    +----------------------------+---------------------------------------+---------+
    | "software_control_enabled" | Is software control mode active?      | boolean |
    +----------------------------+---------------------------------------+---------+
    | "software_value"           | Digital output software defined value | int     |
    +----------------------------+---------------------------------------+---------+

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        # initialize the digital output channel
        hil.set_digital_output(1, name = 'machine encoder A', invert = False, swControl = False, value = 0)

        # get the digital output settings parameters
        channel_settings = hil.get_digital_output_settings(channel = 1, device = 0)

        # unpack the parameters from the dictionary
        signal_name              = channel_settings["signal_name"]
        inverted                 = channel_settings["inverted"]
        software_control_enabled = channel_settings["software_control_enabled"]
        software_value           = channel_settings["software_value"]

    """
    return clstub().get_digital_output_settings(channel=channel, device=device)


def get_cp_input_settings(cpCategory, cpGroup, cpInputName):
    """
    Returns the settings parameters of a Control Panel Input (CP Input).

    .. note::

        This function will soon be deprecated.
        Please use the ``get_scada_input_settings()`` instead.

    Args:
        cpCategory (str): CP Input category name

        cpGroup (str): CP Input group name

        cpInputName (str): CP Input name

    Returns:
        Dictionary with the CP input settings, or ``None`` if the CP input cannot be found.

    +---------------------+----------------------------------+---------------+
    | Dictionary key      | Meaning                          | Value         |
    +=====================+==================================+===============+
    | "input_value"       | Control Panel input value        | int or float  |
    +---------------------+----------------------------------+---------------+

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        # initialize the CP Input
        hil.set_cp_input_value('Power load/source', "Sconst1", 'Pref', 32.00)

        # get the CP Input settings parameters
        cp_input_settings = hil.get_cp_input_settings('Power load/source', "Sconst1", 'Pref',)

        # unpack the parameters from the dictionary
        input_value      = cp_input_settings["input_value"]
    """
    return clstub().get_cp_input_settings(cpCategory=cpCategory,
                                          cpGroup=cpGroup,
                                          cpInputName=cpInputName)


def get_scada_input_settings(scadaInputName):
    """
    Returns the settings parameters of a SCADA Input.

    Args:
        scadaInputName (str): SCADA Input name

    Returns:
        * Dictionary with the SCADA Input settings, or ``None`` if the SCADA Input cannot be found.

    +---------------------+-----------------------+---------------+
    | Dictionary key      | Meaning               | Value         |
    +=====================+=======================+===============+
    | "input_value"       | SCADA input value     | int or float  |
    +---------------------+-----------------------+---------------+

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        # initialize the SCADA Input
        hil.set_scada_input_value("Sconst1.Pref", 32.00)

        # get the SCADA Input settings parameters
        scada_input_settings = hil.get_scada_input_settings("Sconst1.Pref")

        # unpack the parameters from the dictionary
        input_value = scada_input_settings["input_value"]
    """
    return clstub().get_scada_input_settings(scadaInputName=scadaInputName)


def get_hil_serial_number():
    """
    Returns the serial numbers of all connected HIL devices.

    .. note::
        Serial numbers will be returned as a list sorted by HIL device ID:
        [device_with_id_0_serial, device_with_id_1_serial, ... device_with_id_N_serial]

    .. note::
        In case multiple HIL devices with the same device ID are connected, the returned list will be unsorted

    Returns:
        * list of serial numbers sorted by the HIL device ID. In case an error occurs, an empty list will be returned or an appropriate exception will be raised

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions

    Example::

        import typhoon.api.hil as hil

        # get the list of serial numbers of all connected HIL
        serialNumbers = hil.get_hil_serial_number()
    """
    return clstub().get_hil_serial_number()


def get_ns_var(var_name):
    """
    Returns the value of the Schematic Editor namespace variable named ``var_name``.

    Args:
        var_name (str): Namespace variable name.
    Returns:
         Data stored in the variable ``var_name`` or ``None`` if the variable with the name ``var_name`` cannot be found or if an error occurred.

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions
    """
    return clstub().get_ns_var(var_name=var_name)


def get_ns_vars():
    """
    Gets names of all variables in the Schematic Editor namespace.

    Returns:
         List with all variable names in the namespace, or ``None`` if an error occurred.

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions
    """
    return clstub().get_ns_vars()


def get_data_logger_status(name):
    """
    Returns a status of the data logger with given ``name``.

    Args:
        name (str): The name of data logger whose status we want to obtain.

    Returns:
        status (tuple): (status, status_message) where ``status`` can be ``True`` or ``False``
            depending if everything is ok or some error occurs.
    """

    return clstub().get_data_logger_status(name)


def get_model_file_path():
    """
    Returns loaded HIL Model file path.

    Returns:
        path (str or None): Full path to loaded .cpd file.
            In case model is not loaded ``None`` will be returned.

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions
    """

    return clstub().get_model_file_path()


def get_sp_monitors_values():
    """
    Returns values and other information (current value, maximum achieved
    value, CPU stalled flag status...) of all SP Monitors in loaded model.

    Returns:
        sp monitors' data (list): None if error occurs or sp monitors' data
        organized like:

            ::

                [
                    {
                        # ("System CPU", "User 'Nth' CPU", "Communication CPU")
                        "SP Monitor type": "System CPU",

                        # [0 , (number_of_device-1)]
                        "HIL Device": 0,

                        # (True, False)
                        "CPU Stalled": False,

                        "Execution rates": [
                            {
                                # execution rate value
                                "Execution rate": 1e-5,

                                # [0%, 100%]
                                "Current value": 56.8,

                                # [0%, 100%]
                                "Maximum achieved": 80
                            },
                            {
                                # another execution rate data
                            }
                        ]
                    },

                    {
                        # another SP Monitor data
                    }
                ]

    Availability:
        * standalone scripts
        * macro scripts
        * signal monitoring expressions
    """

    return clstub().get_sp_monitors_values()


def available_sources():
    """
    Displays the list of all independent voltage/current sources in the model.

    Returns:
        ``True`` if everything is OK, otherwise returns ``False``.

    Availability:
        * standalone scripts
    """
    return clstub().available_sources()


def available_pvs():
    """
    Displays the list of all photovoltaic panels in the model.

    .. note::

        This function is deprecated and it will be removed from the HIL API.

    Returns:
        ``True`` if everything is OK, otherwise returns ``False``.

    Availability:
        * standalone scripts
    """
    return clstub().available_pvs()


def available_analog_signals():
    """
    Displays the list of all analog signals in the model.

    .. note::

        This function is deprecated and it will be removed from the HIL API.

    Returns:
        ``True`` if everything is OK, otherwise returns ``False``.

    Availability:
        * standalone scripts
    """
    return clstub().available_analog_signals()


def available_digital_signals():
    """
    Displays the list of all digital signals that can be assigned to digital outputs.

    .. note::

        This function is deprecated and it will be removed from the HIL API.

    Returns:
        ``True`` if everything is OK, otherwise returns ``False``.

    Availability:
        * standalone scripts
    """
    return clstub().available_digital_signals()


def available_contactors():
    """
    Displays the list of all contactors in the model.

    .. note::

        This function is deprecated and it will be removed from the HIL API.

    Returns:
        ``True`` if everything is OK, otherwise returns ``False``.

    Availability:
        * standalone scripts
    """
    return clstub().available_contactors()


def available_machines():
    """
    Displays the list of all machines in the model.

    .. note::

        This function is deprecated and it will be removed from the HIL API.

    Returns:
        ``True`` if everything is OK, otherwise returns ``False``.

    Availability:
        * standalone scripts
    """
    return clstub().available_machines()


def available_pe_switching_blocks():
    """
    Displays the list of all software-controllable power electronics switching blocks in the model.

    .. note::

        This function is deprecated and it will be removed from the HIL API.

    Returns:
        ``True`` if everything is OK, otherwise returns ``False``.

    Availability:
        * standalone scripts
    """
    return clstub().available_pe_switching_blocks()
