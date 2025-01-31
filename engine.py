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

import importlib
import importlib.util
import inspect
import os
from queue import Queue
import re
import sys

import sgtk
import SyPy3
import SyPy3.sytalker
from sgtk.platform import Engine

parent_dir = os.path.dirname(__file__)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

python_dir = os.path.join(parent_dir, "python")
if python_dir not in sys.path:
    sys.path.insert(0, python_dir)

from tk_syntheyes.inbuilt_app import InbuiltApp
from helper_functions import load_module, rreload


class InbuiltAppPackageFinder:
    """
    Custom finder for assisting the reloading process of active packages of inbuilt and user apps.
    The finder will attempt to find the specs for modules that have been previously loaded.
    The search is, however, limited to the modules in the set provided by the __init__ function.
    """
    def __init__(self, modules: set[str] = None):
        self._modules = set()
        if modules:
            self._modules.update(modules)

    def find_spec(self, fullname, path, target = None):
        if fullname not in self._modules or not target or fullname not in sys.modules:
            return None
        spec = getattr(target, "__spec__", None)
        return importlib.util.spec_from_file_location(fullname, target.__file__, submodule_search_locations=[] if not spec else getattr(spec, "submodule_search_locations", []))        
    
    @property
    def modules(self):
        return self._modules
    
###############################################################################################
# The Tank SynthEyes engine


class SynthEyesEngine(Engine):
    """
    Toolkit engine for SynthEyes.
    """

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
                "version": "2023.10.1057",
            }

        The returned dictionary is of following form on an error preventing
        the version identification.

            {
                "name": "SynthEyes",
                "version: "unknown"
            }
        """
        host_info = {
            "name": "SynthEyes",
            "version": "unknown"
        }
        try:
            hlev = self.get_syntheyes_connection()
            host_info["version"] = hlev.Version()
        except:
            pass

        return host_info

    @property
    def inbuilt_apps(self):
        if getattr(self, "_inbuilt_apps", None):
            return self._inbuilt_apps
        
        # Setup all paths where the engine will look for apps
        # List[path, is_user_app, is_user_specific]
        inbuilt_apps_paths = [
            (os.path.abspath(os.path.join(os.path.dirname(__file__), "python", "tk_syntheyes", "inbuilt_apps")), False, False)
        ]

        user = getattr(self.context, "user", None)
        user_name = "" if user is None else user.get("name", None)
        
        # Group all valid user module paths
        module_paths = os.environ.get("SYNTHEYES_MODULE_PATH", "")
        if module_paths:
            module_path_list = module_paths.split(";")
            for module_path in module_path_list:                
                if not self._is_valid_user_path(module_path):
                    continue
                inbuilt_apps_paths.append((module_path, True, False))
                
                # Add dedicated user folder that is only loaded for this user
                if not user_name:
                    continue
                module_path = os.path.join(module_path, user_name)
                if self._is_valid_user_path(module_path):
                    inbuilt_apps_paths.append((module_path, True, True))


        valid_chars = re.compile('[\W]+') # Regex pattern to filter undesired characters -> only A-Z, a-z, 0-9, _
        loaded_pckgs = set()
        self._inbuilt_apps = {}
        for inbuilt_apps_path, is_user_path, is_user_specific in inbuilt_apps_paths:
            if not os.path.isdir(inbuilt_apps_path) or (is_user_path and not self._check_init_file(inbuilt_apps_path)):
                continue
            
            # Load the current user path as a package for all the corresponding apps to reside in.
            # That way, potential namespace collisions should be avoidable and this simultaneously allows the use of relative imports in the imported modules.
            pckg_pre = "user" if is_user_path else "inbuilt"
            
            if is_user_specific:
                pckg_name = f"{pckg_pre}_{os.path.basename(os.path.dirname(inbuilt_apps_path))}_{os.path.basename(inbuilt_apps_path)}"
            else:
                pckg_name = f"{pckg_pre}_{os.path.basename(inbuilt_apps_path)}"
            pckg_name = valid_chars.sub('', pckg_name)

            # Load package module
            package_mod = load_module(pckg_name, os.path.join(inbuilt_apps_path, "__init__.py"), True, False, submodule_search_locations = [], logger = self.logger)
            if not package_mod:
                continue
            
            loaded_pckgs.add(pckg_name)
            module_prefix = pckg_name + "."

            # Load all python modules aka files that contain an InbuiltApp subclass and import them into the new package
            for file in os.listdir(inbuilt_apps_path):
                if file == "__init__.py" or not file.endswith(".py"):
                    continue

                file_path = os.path.join(inbuilt_apps_path, file)
                if not os.path.isfile(file_path):
                    continue

                mod = load_module(module_prefix + file.rsplit('.', 1)[0], file_path, True, True, logger = self.logger)
                if not mod:
                    continue

                # iterate over all classes
                for cls_name, cls in inspect.getmembers(mod, inspect.isclass):
                    if cls != InbuiltApp and issubclass(cls, InbuiltApp):
                        ins = cls(self)
                        ins._is_user_app = is_user_path
                        self._inbuilt_apps[cls_name] = ins

        self._update_inbuilt_app_finder(loaded_pckgs)
        return self._inbuilt_apps

    def _clear_inbuilt_apps(self):
        if hasattr(self, "_inbuilt_apps"):
            del self._inbuilt_apps
        self._update_inbuilt_app_finder(None)

    def _update_inbuilt_app_finder(self, modules: set[str]) -> InbuiltAppPackageFinder:
        finder: InbuiltAppPackageFinder = getattr(self, "_inbuilt_app_finder", None)
        empty = not modules or len(modules)
        if finder:
            if empty:
                finder.modules.clear()
                finder.modules.update(modules)
                return finder
            else:
                if finder in sys.meta_path:
                    sys.meta_path.remove(finder)
                del self._inbuit_app_finder
                return None
        elif empty:
            finder = self._inbuit_app_finder = InbuiltAppPackageFinder(modules)
            sys.meta_path.append(finder)
            return finder
        
        return None

    @staticmethod
    def _is_valid_user_path(path):
        if not os.path.isdir(path):
            return False

        # Check that no invalid __init__.py file is present
        init = os.path.join(path, "__init__.py")
        if os.path.exists(init) and not os.path.isfile(init):
            return False
        
        return True
    
    @staticmethod
    def _check_init_file(path):
        """Check if an __init__.py file exists in the target directory :path:.
        returns: True if an __init__.py file exists, False otherwise
        """
        if not os.path.isdir(path):
            return False
        init_path = os.path.join(path, "__init__.py")
        if os.path.exists(init_path) and os.path.isfile(init_path):
            return True
        return False

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
        
        # Will initialize the connection if not present already
        self.get_syntheyes_connection()

        host_info = self.host_info
        syntheyes_ver = host_info["version"]
        if syntheyes_ver in {
            "2023.10.1057",
        }:
            self.logger.debug("Running SynthEyes version %s", syntheyes_ver)
        else:
            msg = (
                "The Flow Production Tracking has not yet been fully tested with SynthEyes %s. "
                "You can continue to use Toolkit but you may experience bugs or instability."
            )
            self.logger.warning(msg, syntheyes_ver)        

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
        except:
            msg = "Could not create PySide app" if creating_qt_app else "Could not access PySide app"
            self.logger.exception(msg)
            raise sgtk.TankError(msg)
        
    def post_app_init(self):
        """
        Called when all apps have been initialized
        """
        # Store the "Open Log Folder" command as it may be lost after the first context switch for some reason.
        # The same issue seems to be present in tk-substancepainter
        cmds = self.commands
        if "Open Log Folder" in cmds:
            self._open_log_folder = [("Open Log Folder", cmds["Open Log Folder"])]
        elif hasattr(self, "_open_log_folder"):
            self.commands.update(self._open_log_folder)

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
            self.ui.regenerate_panels()
        self.init_heartbeat()
        
        # Write any pending logs to the log console if any
        self.log_to_console()

    def post_context_change(self, old_context, new_context):
        """
        Runs after a context change. The Substance Painter event watching will 
        be stopped and new callbacks registered containing the new context 
        information.

        :param old_context: The context being changed away from.
        :param new_context: The new context being changed to.
        """
        # Re-add the "Open Log Folder" command since it may have been lost after the first context switch for some reason.
        # The same issue seems to be present in tk-substancepainter
        if hasattr(self, "_open_log_folder"):
            self.commands.update(self._open_log_folder)
        self.ui.regenerate_panels()

    def init_heartbeat(self):
        """
        Initialize heartbeat to check if the engine is still connected to SynthEyes.
        """
        try:
            from tk_syntheyes.util.heartbeat import Heartbeat
            if hasattr(self, "_heartbeat"):
                self._heartbeat.join(True)
            self._heartbeat = Heartbeat(self)
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
        del hlev

    def change_context(self, new_context):
        context = self.context
        super().change_context(new_context)
    
    def _get_dialog_parent(self):
        """
        Get the QWidget parent for all dialogs created through
        show_dialog & show_modal.
        """
        return getattr(self, "ui", None)

    def check_connection(self):
        """Check the connection status of SynthEyes."""
        # NOTE: Important to open a new connection here as the hlev does not update the OK status after connecting
        hlev = SyPy3.SyLevel()
        if hlev.OpenExisting(self._port, self._pin):
            ok = hlev.core.OK()
            hlev.Close()
            return ok
        return False

    @classmethod
    def check_connection(self, hlev: SyPy3.sylevel.SyLevel):
        if not hlev or not hlev.core or not hlev.core.OK():
            return False
        try:
            return hlev.core.Send("sgtk::connection")
        except:
            return False

    @property
    def has_ui(self):
        """Return if SynthEyes' UI currently exists."""
        return True
    
    ############################################################################    
    ### Logging ###

    def _emit_log_message(self, handler, record):
        """
        Called by the engine to log messages in Maya script editor.
        All log messages from the toolkit logging namespace will be passed to this method.

        :param handler: Log handler that this message was dispatched from.
                        Its default format is "[levelname basename] message".
        :type handler: :class:`~python.logging.LogHandler`
        :param record: Standard python logging record.
        :type record: :class:`~python.logging.LogRecord`
        """
        # Use default formatting
        msg = f"{record.asctime} {handler.format(record)}"
        
        COLOR_MAP = {
            'CRITICAL': 'indianred',
            'ERROR': 'indianred',
            'WARNING': 'khaki',
            'INFO': 'lightgray',
            'DEBUG': 'lightblue',
        }

        for lvl, col in COLOR_MAP.items():
            if f"[{lvl}" in msg:
                msg = f"<font color={col}>{msg}</font>"
                break
        msg = f"<pre>{msg}</pre>"

        # Try to display the message in the logging console in a thread safe manner.
        self.async_execute_in_main_thread(self.log_to_console, msg)

    @property
    def pending_logs(self) -> Queue:
        logs = getattr(self, "_pending_logs", None)
        if logs is None:
            self._pending_logs = Queue()
        return self._pending_logs

    def log_to_console(self, msg = None):
        """Log all pending log messages to the engine's UI log console if present.
        Otherwise, temporarily store :msg: in a queue.
        When called without any arguments, no new log message will be added to the queue.
        However, writing all pending messages to the console will still be attempted.
        :returns: False if console is not present and the pending items could not be written. True, otherwise.
        """
        pending = self.pending_logs
        
        if msg is not None:
            pending.put(msg)

        # Get ui logging console
        ui = getattr(self, "ui", None)
        if not ui:
            return False
        console = getattr(ui, "console", None)
        if not console:
            return False

        while not pending.empty():
            log = pending.get()
            if not log:
                continue
            self.ui.console.append_to_log(log)

        return True

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
            self.logger.error(e)
        self._cleanup_env()

    def save_session(self):
        try:
            hlev = self.get_syntheyes_connection()
            hlev.Scene().Call("Save", hlev.SNIFileName())
            hlev.ClearChanged()
        except Exception as e:
            self.logger.error("Could not save current SynthEyes session file.\n%s", e)

    def save_session_as(self, path: str):
        try:
            hlev = self.get_syntheyes_connection()
            hlev.SetSNIFileName(path)
            hlev.Scene().Call("Save", path)
            hlev.ClearChanged()
        except Exception as e:
            self.logger.error("Error during saving to %s\n%s", path, e)

    def get_session_path(self):
        try:
            hlev = self.get_syntheyes_connection()
            return hlev.SNIFileName()
        except Exception as e:
            self.logger.error("Error accessing the file path\n%s", e)
        return None
    
    def get_syntheyes_connection(self) -> SyPy3.sylevel.SyLevel:
        hlev: SyPy3.sylevel.SyLevel = getattr(self, "_hlev", None)
        
        # Close established connection if invalid
        if hlev and hlev.core and not hlev.core.OK():
            hlev.Close()
        
        # Open new connection if current handle is faulty or non-existent
        if hlev is None or hlev.core is None:
            self._hlev = self.get_new_syntheyes_connection()
            
        return self._hlev
    
    def get_new_syntheyes_connection(self) -> SyPy3.sylevel.SyLevel:
        hlev = SyPy3.SyLevel()
        if not hlev.OpenExisting(self._port, self._pin):
            raise Exception("Connection to SynthEyes can not be established. Make sure there is a running SynthEyes instance that was launched via ShotGrid.")
        return hlev

    def get_syntheyes_hwnd(self):
        hlev = self.get_syntheyes_connection()
        return int(hlev.Main().HWND(), 16)
    
    def prompt_to_close_popup(self):
        from sgtk.platform.qt import QtCore, QtGui
        
        # check if a popup that might interfere with the reset is still open and ask the user to close it first
        hlev = self.get_syntheyes_connection()
        
        while True:
            popup = hlev.Popup()
            name = popup.Name()
            
            if not popup.IsValid():
                break
            self.ui.suppress()
            try:
                QtGui.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)
                self.ui.message_box(
                    QtGui.QMessageBox.Critical,
                    "Popup detected",
                    "A popup \"{}\" is currently open in SynthEyes, which might interfere with the current action. Close the popup first and then hit OK to proceed.".format(name),
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
            self.logger.info(message)
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

    def prompt_to_save_changes(self):
        """
        Opens a Qt dialog to allow the user to save unsaved changes if present.

        :returns: False if the action was Canceled, True otherwise
        """
        from sgtk.platform.qt import QtCore, QtGui

        hlev = self.get_syntheyes_connection()
        
        if hlev.HasChanged():
            yes = QtGui.QMessageBox.Yes
            no = QtGui.QMessageBox.No
            cancel = QtGui.QMessageBox.Cancel
            try:
                QtGui.QApplication.setOverrideCursor(QtCore.Qt.ArrowCursor)
                res = self.ui.message_box(
                    QtGui.QMessageBox.Information,
                    "Unsaved Changes",
                    "The current scene has unsaved changes. Do you want to save before closing?",
                    yes | no | cancel
                )
            except:
                raise
            finally:
                QtGui.QApplication.restoreOverrideCursor()
            
            if res == yes:
                self.save_session()
            elif res == no:
                pass
            else:
                return False
        
        return True