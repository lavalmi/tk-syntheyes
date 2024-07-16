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

### DEBUG ###
import builtins
builtins.DEBUG = os.environ.get("__DEBUG__")
sys.path.append(os.path.dirname(__file__))
from helper_functions import strtobool    
#############

class SynthEyesLauncher(SoftwareLauncher):
    """
    Handles launching SynthEyes executables. Automatically starts up
    a tk-syntheyes engine with the current context in the new session
    of SynthEyes.
    """

    # Named regex strings to insert into the executable template paths when
    # matching against supplied versions and products. Similar to the glob
    # strings, these allow us to alter the regex matching for any of the
    # variable components of the path in one place
    COMPONENT_REGEX_LOOKUP = {"version": r"[\d.]+", "match": r"x\d+"}

    # This dictionary defines a list of executable template strings for each
    # of the supported operating systems. The templates are used for both
    # globbing and regex matches by replacing the named format placeholders
    # with an appropriate glob or regex string. As Side FX adds modifies the
    # install path on a given OS for a new release, a new template will need
    # to be added here.
    EXECUTABLE_TEMPLATES = {
        "darwin": [
            #"/Applications/Autodesk/Maya{version}/Maya.app", #TODO Check path on mac
        ],
        "win32": [
            "C:/Program Files/BorisFX/SynthEyes 2024/SynthEyes64.exe"
            #"C:/Program Files/Autodesk/Maya{version}/bin/Maya.exe",
        ],
        "linux": [
            #"/usr/autodesk/Maya{version}/bin/Maya", #TODO Check path on linux
        ],
    }

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
        sypy_path = "C:\\Program Files\\BorisFX\\SynthEyes 2024" #TODO implement a better alternative than hardcoding the path for windows only and potentially add older SyPy as well to allow backwards compatibility?
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

        if not strtobool(getattr(builtins, "DEBUG", None)):
            args = " ".join([args, '-port', str(port), '-pin', pin])

        # Run the engine's bootstrap.py file when SynthEyes starts up
        # by appending it to the start arguments
        startup_path = os.path.join(self.disk_location, "startup", "bootstrap.py")
        if startup_path:
            if strtobool(getattr(builtins, "DEBUG", None)):
                args = " ".join([args, startup_path])
            else:
                args = " ".join([args, "-start", startup_path])

        # Set the syntheyes python path to point to the shotgun python executable to ensure package compatibility. Ignore this If the path is already present to allow overwriting the default path if necessary.
        if not os.environ.get("SYNTHEYES_PYTHON_PATH"):
            os.environ["SYNTHEYES_PYTHON_PATH"] = "C:\\Program Files\\Shotgun\\Python3\\pythonw.exe"

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

        if not strtobool(getattr(builtins, "DEBUG", None)) and file_to_open:
            # Add the file name to open to the launch arguments
            args = " ".join(file_to_open)

        required_env["PYTHONPATH"] = os.environ["PYTHONPATH"]

        return LaunchInformation(exec_path, args, required_env)

    ##########################################################################################
    # private methods

    def _icon_from_executable(self, exec_path):
        """
        Find the application icon based on the executable path and
        current platform.

        :param exec_path: Full path to the executable.

        :returns: Full path to application icon as a string or None.
        """

        # the engine icon in case we need to use it as a fallback
        engine_icon = os.path.join(self.disk_location, "icon_256.png")

        #TODO Fix icon search pattern
        self.logger.debug(
            "Looking for Application icon for executable '%s' ..." % exec_path
        )
        icon_base_path = ""
        if sgtk.util.is_macos() and "SynthEyes.app" in exec_path:
            # e.g. /Applications/Autodesk/Maya2016.5/Maya.app/Contents
            icon_base_path = os.path.join(
                "".join(exec_path.partition("SynthEyes.app")[0:2]), "Contents"
            )

        elif (sgtk.util.is_windows() or sgtk.util.is_linux()) and "bin" in exec_path:
            # e.g. C:\Program Files\Autodesk\Maya2017\  or
            #      /usr/autodesk/Maya2017/
            icon_base_path = "".join(exec_path.partition("bin")[0:1])

        if not icon_base_path:
            # use the bundled engine icon
            self.logger.debug("Couldn't find bundled icon. Using engine icon.")
            return engine_icon

        # Append the standard icon to the base path and
        # return that path if it exists, else None.
        icon_path = os.path.join(icon_base_path, "icons", "SynthEyesico.png")
        if not os.path.exists(icon_path):
            self.logger.debug(
                "Icon path '%s' resolved from executable '%s' does not exist!"
                "Falling back on engine icon." % (icon_path, exec_path)
            )
            return engine_icon

        # Record what the resolved icon path was.
        self.logger.debug(
            "Resolved icon path '%s' from input executable '%s'."
            % (icon_path, exec_path)
        )
        return icon_path

    def scan_software(self):
        """
        Scan the filesystem for SynthEyes executables.

        :return: A list of :class:`SoftwareVersion` objects.
        """

        self.logger.debug("Scanning for SynthEyes executables...")

        supported_sw_versions = []
        for sw_version in self._find_software():
            (supported, reason) = self._is_supported(sw_version)
            if supported:
                supported_sw_versions.append(sw_version)
            else:
                self.logger.debug(
                    "SoftwareVersion %s is not supported: %s" % (sw_version, reason)
                )

        return supported_sw_versions

    def _find_software(self):
        """
        Find executables in the default install locations.
        """

        # all the executable templates for the current OS
        executable_templates = self.EXECUTABLE_TEMPLATES.get(
            "darwin"
            if sgtk.util.is_macos()
            else "win32"
            if sgtk.util.is_windows()
            else "linux"
            if sgtk.util.is_linux()
            else []
        )

        # all the discovered executables
        sw_versions = []

        for executable_template in executable_templates:

            self.logger.debug("Processing template %s.", executable_template)

            executable_matches = self._glob_and_match(
                executable_template, self.COMPONENT_REGEX_LOOKUP
            )

            # Extract all products from that executable.
            for (executable_path, key_dict) in executable_matches:

                # extract the matched keys form the key_dict (default to None if
                # not included)
                executable_version = key_dict.get("version")

                sw_versions.append(
                    SoftwareVersion(
                        executable_version,
                        "SynthEyes",
                        executable_path,
                        self._icon_from_executable(executable_path),
                    )
                )

        return sw_versions
