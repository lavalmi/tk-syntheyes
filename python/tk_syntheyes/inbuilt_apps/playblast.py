import os
import glob
import time
from threading import Thread

import sgtk
import SyPy3

from engine import SynthEyesEngine
from tk_syntheyes.inbuilt_app import InbuiltApp

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class PlayblastInbuiltApp(InbuiltApp):

    @property
    def display_name(self):
        return "Playblast"
    
    @property
    def description(self):
        return ""
        
    @property
    def commands(self):
        return {
            "Playblast (Fl. Persp.)":
            {
                "callback": self.playblast,
                "properties": {
                    "app": self,
                    "description": "Render a playblast via the 'Render Preview'-function"
                                   "in the SynthEyes' view 'Floating Perspective'.",
                    "environment": ["asset_step", "element_step", "shot_step"]
                }
            },
        }

    def __init__(self, engine: SynthEyesEngine):
        super().__init__(engine)

    def playblast(self):
        hlev = self.engine.get_syntheyes_connection()
        ui = self.engine.ui

        if "tk-multi-publish2" not in self.engine.apps:
            ui.message_box(
                QMessageBox.Critical,
                "Missing App",
                "The tk-multi-publish2 app is required to resolve the path for the playblast, "
                "yet it is currently unavailable.",
                QMessageBox.Abort,
                ui
            )
            return

        if hlev.Popup().IsValid():
            ui.message_box(
                QMessageBox.Critical,
                "Open Popup",
                "A popup is currently open. Close it first, before starting the playblast.",
                QMessageBox.Abort,
                ui
            )
            return

        if hlev.HasChanged():
            save = ui.message_box(
                QMessageBox.Warning,
                "Unsaved Changes",
                "The current scene has unsaved changes. Do you want to save the scene before continueing?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                ui
            )
            if save == QMessageBox.Yes:
                self.engine.save_session()
            elif save == QMessageBox.Cancel:
                return

        timer = Timer(0.033, 5)
        first_undo_block = "Prepare SGTK Playblast"
        reached_first_undo = False
        try:
            active_cam = hlev.Active().cam
            shot = active_cam.shot
            live = shot.live
            
            # get the file path to export to and clear the directory or cancel
            work_path = self._get_playblast_work_path(active_cam.Name())[0]
            path = work_path % (shot.start + shot.frameMatchOffset)
            dir = os.path.dirname(path)
            if os.path.exists(dir):
                files = os.listdir(dir)
                if len(files):
                    result = ui.message_box(
                        QMessageBox.Warning,
                        "Not an empty directory",
                        "The Playblast directory is not empty. Do you want to clean all files in the directory?\n{}".format(dir),
                        QMessageBox.Yes | QMessageBox.Cancel,
                        self.engine.ui
                    )
                    if result == QMessageBox.Yes:
                        for file in files:
                            os.remove(os.path.join(dir, file))
                    else:
                        raise Exception("Error: Playblast directory is not empty.")
            else:
                os.makedirs(dir)

            prepset_name = "sgtk_render_playblast"
            prepset_path = os.path.abspath(os.path.join(self.engine.disk_location, "prepsets", prepset_name + ".prp"))
            hlev.BeginShotChanges(shot)
            try:
                # 1. disable resampling in preprocessor
                live.stabilizeMode = float(int(live.stabilizeMode) & ~128)
                live.Call("MakeStabilizeReference")
                        
                # 2. load custom prepset
                shot.Call("LoadPrepSetsFromFile", 1, prepset_path)
            except Exception as e: raise e
            finally: 
                hlev.AcceptShotChanges(shot, first_undo_block)
                reached_first_undo = True

            # 3. open preprocessor to set the active prepset; 
            # This is a workaround due to the bad type error when directly accessing prepsets from code.
            # If this issue can be resolved, the code here can be improved, but for now this works fine.
            hlev.PerformActionByIDAndContinue(40147) # Shot > Image Preprocessor

            # wait for preprocessor to open
            timer.reset()
            while hlev.Popup().Name() != "Image Preprocessor": # Image Preprocessor
                timer.sleep("Error: Timeout while waiting for Image Preprocessor to open.")

            img_proc = hlev.Popup()
            img_proc.ByID(1400).SetOption(prepset_name) # prepset dropdown; will be reverted via the undo later

            img_proc.ByID(1).ClickAndWait() # OK

            # 4. hide all other cameras and clear the selection to prevent them from showing up in the playblast
            hlev.Begin()
            try:
                for cam in hlev.Cameras():
                    if cam != active_cam:
                        cam.show = False
                hlev.ClearSelection()
            except Exception as e: raise e
            finally: hlev.Accept("Hide other Cameras")

            # 5. open floating perspective if not already present            
            window_title = "Perspective Window"
            persp_already_open = hlev.Floating(window_title).IsValid()
            # ensure perspective window is open
            if not persp_already_open:
                persp_already_open = False
                hlev.PerformActionByIDAndWait(40376) # Window > Floating Perspective
            persp = hlev.Floating(window_title)

            # Locking to the host twice ensures that the perspective is locked to the current camera, regardless of its initial state.
            # It's not the most elegant solution, but at least it works. If there is a way to access the toggle states of all the 
            # perspective window's view settings in the future, this code can be improved.
            persp.PerformActionByIDAndWait(40603) # Persp/Stay Locked to Host
            persp.PerformActionByIDAndWait(40603) # Persp/Stay Locked to Host
            persp.PerformActionByIDAndWait(40366) # Persp/Reset 2D zoom

            # Reset mode to navigation to avoid any handles being rendered, just in case.
            persp.PerformActionByIDAndWait(40090) # Persp/Navigate
            
            # 6. Open the preview movie dialog
            persp.PerformActionByIDAndContinue(40131) # Persp/Preview Movie

            timer.reset()
            while not hlev.Popup().IsValid():
                timer.sleep("Error: Timeout while waiting for Preview Movie window to open.")

            # set prview movie file and compression
            popup = hlev.Popup()
            popup.ByID(1333).SetName(path) # File

            if path.rsplit(".", 1)[1].lower() == "jpg":
                popup.ByID(1340).ClickAndContinue() # Compression Settings
                timer.reset()
                while hlev.Popup().hwnd == popup.hwnd:
                    timer.sleep("Error: Timeout while waiting for compression settings window to open.")
                # Compression settings popup
                comp = hlev.Popup()
                comp.ByID(1573).SetSpnValue(90) # Quality
                comp.ByID(1).ClickAndWait() # OK

            # set preview movie settings
            popup.ByID(1335).SetChecked(True) # Show All Viewport Items
            popup.ByID(1336).SetChecked(False) # Show Grid
            popup.ByID(1337).SetChecked(True) # Square-Pixel Output
            popup.ByID(1346).SetChecked(True) # RGB Included
            popup.ByID(1570).SetChecked(False) # Alpha Included
            popup.ByID(1347).SetChecked(False) # Depth Included
            popup.ByID(2352).SetChecked(True) # Frame#/Time Burn-in
            
            popup.ByID(1339).SetOptionNo(0) # Anti-aliasing and motion blur
            
            popup.ByID(2353).SetSpnValue(180) # Shutter Angle
            popup.ByID(2354).SetSpnValue(-90) # Phase

            popup.ByID(1).ClickAndWait() # Start
            hlev.Unlock()
            
            while popup.IsValid():
                time.sleep(0.25)

            if not persp_already_open:
                persp.CloseAndWait()

            # check if the correct number of frames was written to the file system
            shot_len = shot.stop - shot.start + 1
            seq = glob.glob(work_path.replace("%04d", "[0-9]" * 4))
            if len(seq) != shot_len:
                raise Exception("Error: The number of rendered frames ({:g}) does not match the current shot settings in SynthEyes ({:g}).".format(len(seq), shot_len))

        except Exception as e:
            err_msg = "Error during Playblast: {}".format(e)
            self.engine.log_error(err_msg)
            ui.message_box(
                QMessageBox.Critical,
                "Failure",
                err_msg,
                QMessageBox.Abort,
                self.engine.ui
            )
            return
        finally: 
            if reached_first_undo:
                self._undo_playblast_changes(first_undo_block)

        ui.message_box(
            QMessageBox.Information,
            "Success",
            "The Playblast was successfully rendered and is now available for publishing.",
            QMessageBox.Ok,
            self.engine.ui
        )

    
    def _undo_playblast_changes(self, first_undo):
        hlev = self.engine.get_syntheyes_connection()
        while hlev.UndoCount() and hlev.TopUndoName() != first_undo:
            hlev.Undo()
        hlev.Undo() # Undo once more to undo the first undo block

    def _get_playblast_work_path(self, name):
        for app_name, publish_app in self.engine.apps.items():
            if publish_app.name == "tk-multi-publish2":
                break

        if not publish_app: return
        hlev = self.engine.get_syntheyes_connection()

        template_name = publish_app.settings["collector_settings"]["Playblast Template"]
        template = self.engine.get_template_by_name(template_name)
        
        work_template_name = publish_app.settings["collector_settings"]["Work Template"]
        work_template = self.engine.get_template_by_name(work_template_name)
        
        path = sgtk.util.ShotgunPath.normalize(hlev.SNIFileName())
        work_fields = work_template.get_fields(path)
        work_fields["syntheyes.export_name"] = name.replace(" ", "_")
        work_fields["playblast_extension"] = "jpg"
        work_fields["SEQ"] = 9999

        path = template.apply_fields(work_fields)
        path = path.replace("9999", "%04d")
        return path, template, work_fields
        
class Timer(): #TODO maybe move this somewhere else
    def __init__(self, sleep, timeout):
        self._time = 0
        self._timeout = timeout
        self._sleep = sleep

    def sleep(self, err_msg=""):
        time.sleep(self._sleep)
        self._time += self._sleep
        if self._time > self._timeout:
            raise Exception(err_msg)
        
    def reset(self):
        self._time = 0