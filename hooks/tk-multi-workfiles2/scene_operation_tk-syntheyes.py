# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from sgtk.platform.qt import QtGui

from engine import SynthEyesEngine
import SyPy3
import SyPy3.sywin
from SyPy3.sywin import SyWin
import SyPy3.symenu
from SyPy3.symenu import SyMenu

import os

HookClass = sgtk.get_hook_baseclass()

class SceneOperation(HookClass):
    """
    Hook called to perform an operation with the
    current file
    """

    def execute(
        self,
        operation,
        file_path,
        context=None,
        parent_action=None,
        file_version=None,
        read_only=None,
        **kwargs
    ):
        """
        Main hook entry point

        :param operation:       String
                                Scene operation to perform

        :param file_path:       String
                                File path to use if the operation
                                requires it (e.g. open)

        :param context:         Context
                                The context the file operation is being
                                performed in.

        :param parent_action:   This is the action that this scene operation is
                                being executed for.  This can be one of:
                                - open_file
                                - new_file
                                - save_file_as
                                - version_up

        :param file_version:    The version/revision of the file to be opened.  If this is 'None'
                                then the latest version should be opened.

        :param read_only:       Specifies if the file should be opened read-only or not

        :returns:               Depends on operation:
                                'current_path' - Return the current scene
                                                 file path as a String
                                'open'         - True if file was opened, otherwise False
                                'reset'        - True if scene was reset to an empty
                                                 state, otherwise False
                                all others     - None
        """

        engine: SynthEyesEngine = sgtk.platform.current_engine()
        hlev = engine.get_syntheyes_connection()

        if operation == "current_path":
            return hlev.SNIFileName()

        elif operation == "open":
            return bool(hlev.OpenSNI(file_path))

        elif operation == "save":
            scene = hlev.Scene()
            scene.Call("Save", file_path)
            hlev.ClearChanged()

        elif operation == "save_as":
            scene = hlev.Scene()
            scene.Call("Save", file_path)
            hlev.SetSNIFileName(file_path)
            hlev.ClearChanged()

        elif operation == "reset":
            hlev.ClearChanged()
            hlev.ClickTopMenuAndWait("File", "Close")
            return True
        
        elif operation == "prepare_new":
            #hlev.ClickTopMenuAndContinue("File", "New")
            try:
                from PySide2.QtWidgets import QFileDialog

                if hasattr(context, "entity_locations") and len(context.entity_locations):
                    start_path = context.entity_locations[0]
                    footage_path = os.path.join(start_path, "Footage")
                    if os.path.exists(footage_path):
                        start_path = footage_path
                else:
                    start_path = context.sgtk.project_path

                new_file = QFileDialog.getOpenFileName(engine.ui, "Select Image File", start_path)
                
                if new_file[0]:
                    hlev.NewSceneAndShot(new_file[0])
                    hlev.ClickTopMenuAndContinue("Shot", "Edit Shot")
            except Exception as e:
                self.logger.error("Could not open the selected image file.\n%s", e)
