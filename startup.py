# Copyright (c) 2016 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import sys

import sgtk
from sgtk.platform import SoftwareLauncher, SoftwareVersion, LaunchInformation


class SynthEyesLauncher(SoftwareLauncher):
    """
    Handles launching SynthEyes executables. Automatically starts up
    a tk-syntheyes engine with the current context in the new session
    of SynthEyes.
    """

    @property
    def minimum_supported_version(self):
        """
        The minimum software version that is supported by the launcher.
        """
        return "0"

    def prepare_launch(self, exec_path, args, file_to_open=None):
        """
        Prepares an environment to launch SynthEyes in that will automatically
        load Toolkit and the tk-syntheyes engine when SynthEyes starts.

        :param str exec_path: Path to SynthEyes executable to launch.
        :param str args: Command line arguments as strings.
        :param str file_to_open: (optional) Full path name of a file to open on launch.
        :returns: :class:`LaunchInformation` instance
        """
        required_env = {}

        # Add SynthEyes' SyPy to PYTHONPATH
        sypy_path = os.path.dirname(exec_path)
        sys.path.insert(0, sypy_path)
        sgtk.util.append_path_to_env_var("PYTHONPATH", sypy_path)

        # Generate a random port and pin to establish a connection to this instance of 
        # SynthEyes when launching the engine
        from SyPy3 import syconfig
        port = syconfig.RandomPort(59200, 59300)
        pin = syconfig.RandomPin()
        os.environ["SGTK_SYNTHEYES_PORT"] = str(port)
        os.environ["SGTK_SYNTHEYES_PIN"] = str(pin)
        self.logger.debug("SynthEyes will be started using port:%d and pin:%s.", port, pin)

        args = " ".join([args, '-port', str(port), '-pin', pin])

        # Run the engine's bootstrap.py file when SynthEyes starts up
        # by appending it to the start arguments
        startup_path = os.path.join(self.disk_location, "startup", "bootstrap.py")
        if startup_path:
            args = " ".join([args, "-start", startup_path])

        # Set the syntheyes python path to point to the shotgun python executable to ensure package compatibility. Ignore this If the path is already present to allow overwriting the default path if necessary.
        if not os.environ.get("SYNTHEYES_PYTHON_PATH"):
            python = os.path.splitext(sys.executable)
            os.environ["SYNTHEYES_PYTHON_PATH"] = "w".join(python)

        # Check the engine settings to see whether any plugins have been
        # specified to load.
        
        find_plugins = self.get_setting("launch_builtin_plugins")
        if find_plugins:
            # Parse the specified comma-separated list of plugins
            self.logger.debug(
                "Plugins found from 'launch_builtin_plugins': %s" % find_plugins
            )

            # Keep track of the specific list of Toolkit plugins to load when
            # launching SynthEyes. This list is passed through the environment and
            # used by the startup/bootstrap.py file.
            load_SynthEyes_plugins = []

            # Add Toolkit plugins to load to the SynthEyes_MODULE_PATH environment
            # variable so the SynthEyes loadPlugin command can find them.
            SynthEyes_module_paths = os.environ.get("SynthEyes_MODULE_PATH") or []
            if SynthEyes_module_paths:
                SynthEyes_module_paths = SynthEyes_module_paths.split(os.pathsep)

            for find_plugin in find_plugins:
                load_plugin = os.path.join(self.disk_location, "plugins", find_plugin)
                if os.path.exists(load_plugin):
                    # If the plugin path exists, add it to the list of SynthEyes_MODULE_PATHS
                    # so SynthEyes can find it and to the list of SGTK_LOAD_SynthEyes_PLUGINS so
                    # the startup's bootstrap.py file knows what plugins to load.
                    self.logger.debug(
                        "Preparing to launch builtin plugin '%s'" % load_plugin
                    )
                    load_SynthEyes_plugins.append(load_plugin)
                    if load_plugin not in SynthEyes_module_paths:
                        # Insert at beginning of list to give priority to toolkit plugins
                        # launched from the desktop app over standalone ones whose
                        # path is already part of the SynthEyes_MODULE_PATH env var
                        SynthEyes_module_paths.insert(0, load_plugin)
                else:
                    # Report the missing plugin directory
                    self.logger.warning(
                        "Resolved plugin path '%s' does not exist!" % load_plugin
                    )

            # Add SynthEyes_MODULE_PATH and SGTK_LOAD_SynthEyes_PLUGINS to the launch
            # environment.
            required_env["SynthEyes_MODULE_PATH"] = os.pathsep.join(SynthEyes_module_paths)
            required_env["SGTK_LOAD_SynthEyes_PLUGINS"] = os.pathsep.join(load_SynthEyes_plugins)

            # Add context and site info
            std_env = self.get_standard_plugin_environment()
            required_env.update(std_env)

        else:
            # Prepare the launch environment with variables required by the
            # classic bootstrap approach.
            self.logger.debug(
                "Preparing SynthEyes Launch via Toolkit Classic methodology ..."
            )
            required_env["SGTK_ENGINE"] = self.engine_name
            required_env["SGTK_CONTEXT"] = sgtk.context.serialize(self.context)

        if file_to_open:
            # Add the file name to open to the launch arguments
            args = " ".join(file_to_open)

        required_env["PYTHONPATH"] = os.environ["PYTHONPATH"]

        return LaunchInformation(exec_path, args, required_env)