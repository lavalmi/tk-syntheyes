# Copyright (c) 2015 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
A SynthEyes engine for Shotgun Toolkit.

"""

import logging
import os
import sys

import sgtk
from sgtk.platform import Engine

import SyPy3
import SyPy3.sytalker

parent_dir = os.path.dirname(__file__)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

python_dir = os.path.join(parent_dir, "python")
if python_dir not in sys.path:
    sys.path.insert(0, python_dir)

###############################################################################################
# The Tank SynthEyes engine


class SynthEyesEngine(Engine):
    """
    Toolkit engine for SynthEyes.
    """

    __DIALOG_SIZE_CACHE = dict()

    @property
    def context_change_allowed(self):
        """
        Whether the engine allows a context change without the need for a restart.
        """
        return True

    @property
    def host_info(self):
        """
        :returns: A dictionary with information about the application hosting this engine.

        The returned dictionary is of the following form on success:

            {
                "name": "SynthEyes",
                "version": "2017 Update 4",
            }

        The returned dictionary is of following form on an error preventing
        the version identification.

            {
                "name": "SynthEyes",
                "version: "unknown"
            }
        """

        host_info = {"name": "SynthEyes", "version": "unknown"}
        '''
        try:
            # The 'about -installedVersion' SynthEyes MEL command returns:
            # - the app name (SynthEyes, SynthEyes LT, SynthEyes IO)
            # - the major version (2017, 2018)
            # - the update version when applicable (update 4)
            syntheyes_installed_version_string = "0"

            # group(0) entire match
            # group(1) 'SynthEyes' match (name)
            # group(2) LT, IO, etc ... match (flavor)
            # group(3) 2017 ... match (version)
            
            matches = re.search(
                r"(syntheyes)\s+([a-zA-Z]+)?\s*(.*)",
                syntheyes_installed_version_string,
                re.IGNORECASE,
            )
            host_info["name"] = matches.group(1).capitalize().rstrip().lstrip()
            host_info["version"] = matches.group(3)
            if matches.group(2):
                host_info["name"] = host_info["name"] + " " + matches.group(2)
        except:
            # Fallback to 'SynthEyes' initialized above
            pass
        '''

        return host_info

    ##########################################################################################
    # init and destroy

    def init_engine(self):
        """
        Initializes the SynthEyes engine.
        """
        self.logger.debug("%s: Initializing...", self)

        # check that we are running an ok version of syntheyes
        current_os = sys.platform
        if current_os not in ["win32", "linux", "macOS"]:
            raise sgtk.TankError(
                "The current platform is not supported! Supported platforms "
                "are MacOS, Linux and Windows."
            )

        # Get high level handle to SynthEyes' python API
        self._port: int = int(os.environ["SGTK_SYNTHEYES_PORT"])
        self._pin: str = os.environ["SGTK_SYNTHEYES_PIN"]
        if not (self._port and self._pin):
            raise sgtk.TankError("SynthEyes port:%d and pin:%s are not valid.", self._port, self._pin)
        
        self._hlev: SyPy3.sylevel.SyLevel = SyPy3.SyLevel()
        if not self._hlev.OpenExisting(self._port, self._pin):
            raise sgtk.TankError("Could not open existing instance of SynthEyes with port:%s and pin:%s.", self._port, self._pin)

        syntheyes_ver = self._hlev.Version()
        if syntheyes_ver in {
            "2023.10.1057",
        }:
            self.logger.debug("Running SynthEyes version %s", syntheyes_ver)
        else:
            msg = (
                "The Flow Production Tracking has not yet been fully tested with SynthEyes %s. "
                "You can continue to use Toolkit but you may experience bugs or instability."
            )
            # always log the warning to the script editor:
            self.logger.warning(msg)

    def pre_app_init(self):
        """
        Runs after the engine is set up but before any apps have been initialized.
        """
        # unicode characters returned by the shotgun api need to be converted
        # to display correctly in all of the app windows

        # tell QT to interpret C strings as utf-8
        # these imports won't work on top of the file as these aren't available at that time
        # and regular PySide2 does not know the function setCodecForCStrings
        from sgtk.platform.qt import QtCore, QtGui
        utf8 = QtCore.QTextCodec.codecForName("utf-8")
        QtCore.QTextCodec.setCodecForCStrings(utf8)
        self.logger.debug("set utf-8 codec for widget text")

        # Create QApplication
        creating_qt_app = False
        try:
            sys.argv[0] = 'Shotgun SynthEyes'
            res_dir = os.path.join(self.disk_location, "resources")

            self.qt_app = QtGui.QApplication.instance()
            if self.qt_app is None:
                creating_qt_app = True
                self.qt_app = QtGui.QApplication(sys.argv)
                self.qt_app.setQuitOnLastWindowClosed(True)            
                self.qt_app.setWindowIcon(QtGui.QIcon(os.path.join(res_dir, "process_icon_256.png")))
                self.qt_app.setApplicationName(sys.argv[0])
        except Exception as e:
            msg = "Could not create PySide app" if creating_qt_app else "Could not access PySide app"
            self.logger.exception(msg)
            raise sgtk.TankError(msg)
        
    def post_app_init(self):
        """
        Called when all apps have been initialized
        """
        # Create UI panel for toolkit
        from tk_syntheyes.ui.main_window import MainWindow

        self.ui = getattr(self.qt_app, "main_window", None)
        if self.ui is None:
            self.ui = MainWindow(self, None)
            self.qt_app.main_window = self.ui
            self._initialize_dark_look_and_feel()
            self.ui.show()
        else:
            self.ui: MainWindow
            self.ui._engine = self
            self.ui.console.connect_to_engine(self.ui._engine)
            self.ui.regenerate_panels()
        self.init_heartbeat()

    def init_heartbeat(self):
        """
        Initialize heartbeat to check if the engine is still connected to SynthEyes.
        """
        try:
            from tk_syntheyes.util.heartbeat import Heartbeat
            if hasattr(self, "_heartbeat"):
                self._heartbeat.join(True)
            self._heartbeat = Heartbeat(self, self.logger)
        except Exception as e:
            msg = ("Shotgun Pipeline Toolkit failed to initialize SynthEyes heartbeat: %s" % e)
            self.logger.exception(msg)
            raise sgtk.TankError(msg)

    def destroy_engine(self):
        """
        Stops watching scene events and tears down menu.
        """
        self.logger.debug("%s: Destroying...", self)
        if hasattr(self, "_heartbeat"):
            self._heartbeat.join(True)
        hlev = self.get_syntheyes_connection()
        hlev.Close()

    def change_context(self, new_context):
        context = self.context
        super().change_context(new_context)
        if context == new_context:
            return
        
        # Call update function to reflect the context change in the UI
        self.ui.regenerate_panels()
    
    def _get_dialog_parent(self):
        """
        Get the QWidget parent for all dialogs created through
        show_dialog & show_modal.
        """
        return getattr(self, "ui", None)

    def check_connection(self):
        """Check the connection status of SynthEyes."""
        hlev = SyPy3.SyLevel()
        if hlev.OpenExisting(self._port, self._pin):
            return hlev.core.OK()
        return False

    @property
    def has_ui(self):
        """Return if SynthEyes' UI currently exists."""
        return True
    
    ############################################################################    
    ### Logging ###

    def _init_logging(self):
        if self.get_setting("debug_logging", False):
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

    def log_debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def log_info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def log_warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def log_error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def log_exception(self, msg, *args, **kwargs):
        self.logger.exception(msg, *args, **kwargs)

    ############################################################################
    ### Functions ###

    def _cleanup_env(self):
        self.logger.debug("Cleaning up environment.")

        # Clean up SynthEyes env variables.
        del_vars = [
            "SGTK_ENGINE",
            "SGTK_CONTEXT",
            "SGTK_FILE_TO_OPEN",
            "SGTK_LOAD_SYNTHEYES_PLUGINS",
            "SGTK_SYNTHEYES_PORT",
            "SGTK_SYNTHEYES_PIN",
        ]
        for var in del_vars:
            if var in os.environ:
                del os.environ[var]

        # Remove SynthEyes' directory from PYTHONPATH
        env_var_sep = ";" if sys.platform.startswith("win32") else ":"
        pythonpath = os.environ.get("PYTHONPATH", "").split(env_var_sep)
        if pythonpath:
            for path in pythonpath:
                if "SynthEyes" in path:
                    pythonpath.remove(path)
                    break
            # Write the result back to the environment
            os.environ["PYTHONPATH"] = env_var_sep.join(pythonpath)

    def exit(self):
        self._heartbeat.join(True, True)
        try:
            hlev = self.get_syntheyes_connection()
            hlev.ClearChanged()
            hlev.CloseSynthEyes()
        except Exception as e:
            self.log_error(e)
        self._cleanup_env()

    def save_session(self):
        try:
            self._hlev.Scene().Call("Save", self._hlev.SNIFileName())
            self._hlev.ClearChanged()
        except Exception as e:
            self.log_error("Could not save current SynthEyes session file.\n%s", e)

    def save_session_as(self, path: str):
        try:
            self._hlev.SetSNIFileName(path)
            self._hlev.Scene().Call("Save", path)
            self._hlev.ClearChanged()
        except Exception as e:
            self.log_error("Error during saving to %s\n%s", path, e)

    def get_session_path(self):
        try:
            return self._hlev.SNIFileName()
        except Exception as e:
            self.log_error("Error accessing the file path\n%s", e)
        return None
    
    def get_syntheyes_connection(self) -> SyPy3.sylevel.SyLevel:
        if self._hlev is None or not self._hlev.core.OK():
            self._hlev = SyPy3.SyLevel()
            if not self._hlev.OpenExisting(self._port, self._pin):
                raise Exception("Connection to SynthEyes can not be established. Make sure there is a running SynthEyes instance that was launched via ShotGrid.")
            
        return self._hlev
    
    def get_syntheyes_hwnd(self):
        return int(self._hlev.Main().HWND(), 16)
    
    def prompt_to_close_popup(self):
        from sgtk.platform.qt import QtCore, QtGui
        
        # check if a popup that might interfere with the reset is still open and ask the user to close it first
        hlev = self.get_syntheyes_connection()
        self.ui.suppress()

        while True:
            popup = hlev.Popup()
            if not popup.IsValid():
                break
            try:
                QtGui.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)
                self.ui.message_box(
                    QtGui.QMessageBox.Critical,
                    "Popup detected",
                    "A popup \"{}\" is currently open in SynthEyes, which might interfere with the current action. Close the popup first and then hit OK to proceed.".format(
                        popup.Name()),
                    QtGui.QMessageBox.Ok
                )
            finally:
                QtGui.QApplication.restoreOverrideCursor()
        self.ui.free()

    def check_for_popups(self):
        """
        Checks and returns if there are any open popups in SynthEyes. If True, a message box will be displayed.
        """
        from sgtk.platform.qt import QtCore, QtGui

        hlev = self.get_syntheyes_connection()
        popup = hlev.Popup()
        if popup.IsValid():
            message = "A popup \"{}\" is still open in SynthEyes. This may cause unexpected behaviour. Please close the popup first and repeat the previous action.".format(popup.Name())
            self.log_info(message)
            try:
                QtGui.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)
                self.ui.message_box(
                    QtGui.QMessageBox.Critical,
                    "Popup detected - Action canceled",
                    message,
                    QtGui.QMessageBox.Abort
                )
            finally:
                QtGui.QApplication.restoreOverrideCursor()
                return True
        
        return False