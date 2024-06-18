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

import PySide2.QtConcurrent
import PySide2.QtCore
import PySide2.QtGui
import sgtk
import sys
import traceback
import re
import os
import logging
from sgtk.platform import Engine

import SyPy3
import builtins

# Although the engine has logging already, this logger is needed for callback based logging
# where an engine may not be present.
logger = sgtk.LogManager.get_logger(__name__)

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

        sys.path.insert(0, os.path.join(self.disk_location, "python"))

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
        
        self.hlev: SyPy3.sylevel.SyLevel = SyPy3.SyLevel()
        if not builtins.DEBUG:
            if not self.hlev.OpenExisting(self._port, self._pin):
                raise sgtk.TankError("Could not open existing instance of SynthEyes with port:%s and pin:%s.", self._port, self._pin)

            syntheyes_ver = self.hlev.Version()
            if syntheyes_ver in {
                "2023.10.1057",
            }:
                self.logger.debug("Running SynthEyes version %s", syntheyes_ver)
            else:
                msg = (
                    "The Flow Production Tracking has not yet been fully tested with SynthEyes %s.  "
                    "You can continue to use Toolkit but you may experience bugs or instability."
                )
                # always log the warning to the script editor:
                self.logger.warning(msg)

        # Set the SynthEyes project based on config
        #self._set_project()

        # add qt paths and dlls
        self._init_pyside() # TODO Not sure if this is needed for SynthEyes

        # Initialize a dictionary of SynthEyes panels that have been created by the engine.
        # Each panel entry has a SynthEyes panel name key and an app widget instance value.
        self._syntheyes_panel_dict = {}

    def pre_app_init(self):
        """
        Runs after the engine is set up but before any apps have been initialized.
        """
        # unicode characters returned by the shotgun api need to be converted
        # to display correctly in all of the app windows
        from sgtk.platform.qt import QtCore, QtGui

        from tk_syntheyes import logging_console

        # tell QT to interpret C strings as utf-8
        utf8 = QtCore.QTextCodec.codecForName("utf-8")
        QtCore.QTextCodec.setCodecForCStrings(utf8)
        self.logger.debug("set utf-8 codec for widget text")

        # Initialize heartbeat
        #try:
        #    from syntheyes.heartbeat import Heartbeat
        #    self.heartbeat = Heartbeat(self.logger)
        #except Exception as e:
        #    msg = ("Shotgun Pipeline Toolkit failed to initialize SynthEyes heartbeat: %s" % e)
        #    self.logger.exception(msg)
        #    raise sgtk.TankError(msg)

        # Create QApplication
        try:
            sys.argv[0] = 'Shotgun SynthEyes'
            self.qt_app = QtGui.QApplication(sys.argv)
            self.qt_app.setQuitOnLastWindowClosed(True)
            res_dir = os.path.join(self.disk_location, "resources")
            self.qt_app.setWindowIcon(QtGui.QIcon(os.path.join(res_dir, "process_icon_256.png")))
            self.qt_app.setApplicationName(sys.argv[0])
        except Exception as e:
            msg = "Could not create PySide app"
            self.logger.exception(msg)
            raise sgtk.TankError(msg)

        # Create SynthEyes logging console
        try:
            self.qt_log = logging_console.LogConsole()
            self.qt_app.setProperty("tk-syntheyes.log_console", self.qt_log)
            qt_handler = logging_console.QtLogHandler(self.qt_log.logs)
            self.logger.addHandler(qt_handler)
            self.qt_log.setHidden(True)
        except Exception as e:
            msg = "Could not create logging console"
            self.logger.exception(msg)
            raise sgtk.TankError(msg)

        # Create UI panel for toolkit
        from tk_syntheyes.ui.sgtk_panel import Ui_SgtkPanel
        self.ui = Ui_SgtkPanel(self._get_dialog_parent())

    def post_app_init(self):
        """
        Called when all apps have initialized
        """
        import tk_syntheyes
        self._initialize_dark_look_and_feel()
        self._panel_generator = tk_syntheyes.PanelGenerator(self)
        self._panel_generator.populate_panel()
        self.ui.show()

    def destroy_engine(self):
        """
        Stops watching scene events and tears down menu.
        """
        self.logger.debug("%s: Destroying...", self)

        self._panel_generator.destroy_panel()

        self.hlev.Close()
        
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
        if sys.platform.is_windows():
            env_var_sep = ";"
        else:
            env_var_sep = ":"
        pythonpath = os.environ.get("PYTHONPATH", "").split(env_var_sep)
        if pythonpath:
            for path in pythonpath:
                if "SynthEyes" in path:
                    pythonpath.remove(path)
                    return
            # Write the result back to the environment
            os.environ["PYTHONPATH"] = env_var_sep.join(pythonpath)

        # Clear the dictionary of SynthEyes panels to keep the garbage collector happy.
        self._syntheyes_panel_dict = {}

    def show_dialog(self, title, *args, **kwargs):
        """
        If on Windows or Linux, this method will call through to the base implementation of
        this method without alteration. On OSX, we'll do some additional work to ensure that
        window parenting works properly, which requires some extra logic on that operating
        system beyond setting the dialog's parent.

        :param str title: The title of the dialog.

        :returns: the created widget_class instance
        """
        if not sgtk.util.is_macos():
            return super(SynthEyesEngine, self).show_dialog(title, *args, **kwargs)
        else:
            from sgtk.platform.qt import QtCore, QtGui

            # create the dialog:
            dialog, widget = self._create_dialog_with_widget(title, *args, **kwargs)

            # When using the recipe here to get Z-depth ordering correct we also
            # inherit another feature that results in window size and position being
            # remembered. This size/pos retention happens across app boundaries, so
            # we would end up with one app inheriting the size from a previously
            # launched app, which was weird. To counteract that, we keep track of
            # the dialog's size before SynthEyes gets ahold of it, and then resize it
            # right after it's shown. We'll also move the dialog to the center of
            # the desktop.
            center_screen = (
                QtGui.QApplication.desktop().availableGeometry(dialog).center()
            )
            self.__DIALOG_SIZE_CACHE[title] = dialog.size()

            # TODO: Get an explanation and document why we're having to do this. It appears to be
            # a SynthEyes-only solution, because similar problems in other integrations, namely Nuke,
            # are not resolved in the same way. This fix comes to us from the SynthEyes dev team, but
            # we've not yet spoken with someone that can explain why it fixes the problem.
            dialog.setWindowFlags(QtCore.Qt.Window)
            dialog.setProperty("saveWindowPref", True)
            dialog.show()

            # The resize has to happen after the dialog is shown, and we need
            # to move the dialog after the resize, since center of screen will be
            # relative to the final size of the dialog.
            dialog.resize(self.__DIALOG_SIZE_CACHE[title])
            dialog.move(center_screen - dialog.rect().center())

            # lastly, return the instantiated widget
            return widget

    def _init_pyside(self):
        """
        Handles the pyside init
        """

        # First see if pyside6 is present
        try:
            from PySide6 import QtGui
        except:
            # fine, we don't expect PySide2 to be present just yet
            self.logger.debug("PySide6 not detected - trying for PySide2 now...")
        else:
            # looks like pyside2 is already working! No need to do anything
            self.logger.debug("PySide6 detected - the existing version will be used.")
            return

        # Next, check if PySide2 is present
        try:
            from PySide2 import QtGui
        except:
            # fine, we don't expect PySide2 to be present just yet
            self.logger.debug("PySide2 not detected - trying for PySide now...")
        else:
            # looks like pyside2 is already working! No need to do anything
            self.logger.debug("PySide2 detected - the existing version will be used.")
            return

        # Then see if pyside is present
        try:
            from PySide import QtGui
        except:
            # must be a very old version of SynthEyes.
            self.logger.debug(
                "PySide not detected - it will be added to the setup now..."
            )
        else:
            # looks like pyside is already working! No need to do anything
            self.logger.debug("PySide detected - the existing version will be used.")
            return

        if sgtk.util.is_macos():
            pyside_path = os.path.join(
                self.disk_location, "resources", "pyside112_py26_qt471_mac", "python"
            )
            self.logger.debug("Adding pyside to sys.path: %s", pyside_path)
            sys.path.append(pyside_path)

        elif sgtk.util.is_windows():
            # default windows version of pyside for 2011 and 2012
            pyside_path = os.path.join(
                self.disk_location, "resources", "pyside111_py26_qt471_win64", "python"
            )
            self.logger.debug("Adding pyside to sys.path: %s", pyside_path)
            sys.path.append(pyside_path)
            dll_path = os.path.join(
                self.disk_location, "resources", "pyside111_py26_qt471_win64", "lib"
            )
            path = os.environ.get("PATH", "")
            path += ";%s" % dll_path
            os.environ["PATH"] = path

        elif sgtk.util.is_linux():
            pyside_path = os.path.join(
                self.disk_location, "resources", "pyside112_py26_qt471_linux", "python"
            )
            self.logger.debug("Adding pyside to sys.path: %s", pyside_path)
            sys.path.append(pyside_path)

        else:
            self.logger.error("Unknown platform - cannot initialize PySide!")

        # now try to import it
        try:
            from PySide import QtGui
        except Exception as e:
            self.logger.error(
                "PySide could not be imported! Apps using pyside will not "
                "operate correctly! Error reported: %s",
                e,
            )

    def _get_dialog_parent(self):
        """
        Get the QWidget parent for all dialogs created through
        show_dialog & show_modal.
        """
        # determine the parent widget to use:
        if sys.platform == "win32":
            # for windows, we create a proxy window parented to the
            # main application window that we can then set as the owner
            # for all Toolkit dialogs.
            # FIXME: Doesn't work. Crashes the workfiles app when opening a file
            # There seems to be an issue with SynthEyes having another
            # child window. The parenting itself works. Checked with
            # "Window Detective". The proxy QWidget is parented correctly.
            # Even the show_modal stuff seems to enable and disable the window
            # correctly.
            # But opening a file from the workfiles app will crash SynthEyes.
            # Either it's a problem in SynthEyes or there still is something
            # wrong in the hack parenting in _win32_get_proxy_window().
            #parent_widget = self._win32_get_proxy_window()
            from sgtk.platform.qt import QtGui
            parent_widget = QtGui.QApplication.activeWindow()
        else:
            from sgtk.platform.qt import QtGui
            parent_widget = QtGui.QApplication.activeWindow()

        return parent_widget

    def _win32_get_syntheyes_process_id(self):
        """
        Windows specific method to find the process id of SynthEyes.  This
        assumes that it is the parent process of this python process
        """
        if hasattr(self, "_win32_syntheyes_process_id"):
            return self._win32_syntheyes_process_id
        self._win32_syntheyes_process_id = None

        this_pid = os.getpid()

        from tk_syntheyes import win_32_api
        self._win32_syntheyes_process_id = win_32_api.find_parent_process_id(
            this_pid)

        return self._win32_syntheyes_process_id

    def _win32_get_syntheyes_main_hwnd(self):
        """
        Windows specific method to find the main SynthEyes window
        handle (HWND)
        """
        if hasattr(self, "_win32_syntheyes_main_hwnd"):
            return self._win32_syntheyes_main_hwnd
        self._win32_syntheyes_main_hwnd = None

        # find SynthEyes process id:
        se_process_id = self._win32_get_syntheyes_process_id()

        if se_process_id != None:
            # get main application window for SynthEyes process:
            from tk_syntheyes import win_32_api
            found_hwnds = win_32_api.find_windows(process_id=se_process_id,
                                                  class_name='SynthEyes',
                                                  stop_if_found=False)
            if len(found_hwnds) == 1:
                self._win32_syntheyes_main_hwnd = found_hwnds[0]

        return self._win32_syntheyes_main_hwnd

    def _win32_get_proxy_window(self):
        """
        Windows specific method to get the proxy window that will 'own' all
        Toolkit dialogs. This will be parented to the main syntheyes
        application. Creates the proxy window if it doesn't already exist.
        """
        if hasattr(self, "_win32_proxy_win"):
            return self._win32_proxy_win
        self._win32_proxy_win = None

        # get the main syntheyes window:
        se_hwnd = self._win32_get_syntheyes_main_hwnd()

        if se_hwnd != None:

            from sgtk.platform.qt import QtGui
            from tk_syntheyes import win_32_api

            # create the proxy QWidget:
            self._win32_proxy_win = QtGui.QWidget()
            self._win32_proxy_win.setWindowTitle('SGTK Dialog Owner Proxy')

            proxy_win_hwnd = win_32_api.qwidget_winid_to_hwnd(
                self._win32_proxy_win.winId())

            # set no parent notify:
            try:
                win_ex_style = win_32_api.GetWindowLong(proxy_win_hwnd,
                                                        win_32_api.GWL_EXSTYLE)
                win_32_api.SetWindowLong(proxy_win_hwnd, win_32_api.GWL_EXSTYLE,
                                         win_ex_style
                                         | win_32_api.WS_EX_NOPARENTNOTIFY)

                # parent to syntheyes application window:
                win_32_api.SetParent(proxy_win_hwnd, se_hwnd)
            except Exception as e:
                self.log_debug(e)

        return self._win32_proxy_win

    @property
    def has_ui(self):
        """
        Detect and return if syntheyes is running in batch mode
        """
        return False