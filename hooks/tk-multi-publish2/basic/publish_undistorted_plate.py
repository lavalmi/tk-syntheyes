# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import re
import sgtk
import shutil
import time
from pathlib import Path

from engine import SynthEyesEngine

HookBaseClass = sgtk.get_hook_baseclass()


class SyntheyesUndistortedPlatePublishPlugin(HookBaseClass):
    """
    Plugin for publishing an undistorted version of a camera's plate.

    This hook relies on functionality found in the base file publisher hook in
    the publish2 app and should inherit from it in the configuration. The hook
    setting for this plugin should look something like this::

        hook: "{self}/publish_file.py:{engine}/tk-multi-publish2/basic/publish_undistorted_plate.py"

    """

    @property
    def description(self):
        """
        Verbose, multi-line description of what the plugin does. This can
        contain simple html for formatting.
        """

        return """
        <p>This plugin publishes an undistorted version of a shot's plate.
        The respective data will be exported to the path defined by this plugin's configured 
        "publish_template" setting.</p>
        """

    @property
    def settings(self):
        """
        Dictionary defining the settings that this plugin expects to receive
        through the settings parameter in the accept, validate, publish and
        finalize methods.

        A dictionary on the following form::

            {
                "Settings Name": {
                    "type": "settings_type",
                    "default": "default_value",
                    "description": "One line description of the setting"
            }

        The type string should be one of the data types that toolkit accepts as
        part of its environment configuration.
        """
        # inherit the settings from the base publish plugin
        base_settings = super(SyntheyesUndistortedPlatePublishPlugin, self).settings or {}

        # settings specific to this class
        syntheyes_publish_settings = {
            "Publish Template": {
                "type": "template",
                "default": None,
                "description": "Template path for published work files. Should"
                               "correspond to a template defined in templates.yml.",
            },
            "Frame Name Template": {
                "type": "template",
                "default": None,
                "description": "Template name for the frames saved in the published"
                               "undistorted plate folder. Should correspond to a template"
                               "defined in templates.yml.",
            },
        }

        # update the base settings
        base_settings.update(syntheyes_publish_settings)

        return base_settings

    @property
    def item_filters(self):
        """
        List of item types that this plugin is interested in.

        Only items matching entries in this list will be presented to the
        accept() method. Strings can contain glob patters such as *, for example
        ["maya.*", "file.maya"]
        """
        return ["syntheyes.undistort_plate"]

    @property
    def item_property_cache(self):
        """
        Backup of each valid item's properties. Since, in this case, mutliple
        plugins may work on the same item with varying publish paths, it cannot 
        be guaranteed that the properties of the item will remain the same as 
        they were at the time of validation.
        Therefore, the state of the item's properties is cached here and re-set
        before publishing.
        """
        if not hasattr(self, "_item_property_cache"):
            self._item_property_cache = {}
        return self._item_property_cache

    def accept(self, settings, item):
        """
        Method called by the publisher to determine if an item is of any
        interest to this plugin. Only items matching the filters defined via the
        item_filters property will be presented to this method.

        A publish task will be generated for each item accepted here. Returns a
        dictionary with the following booleans:

            - accepted: Indicates if the plugin is interested in this value at
                all. Required.
            - enabled: If True, the plugin will be enabled in the UI, otherwise
                it will be disabled. Optional, True by default.
            - visible: If True, the plugin will be visible in the UI, otherwise
                it will be hidden. Optional, True by default.
            - checked: If True, the plugin will be checked in the UI, otherwise
                it will be unchecked. Optional, True by default.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process

        :returns: dictionary with boolean keys accepted, required and enabled
        """
        accepted = True
        publisher = self.parent
        engine = publisher.engine
        template_name = settings["Publish Template"].value

        # ensure a work file template is available on the parent item
        work_template = item.parent.properties.get("work_template")
        if not work_template:
            self.logger.debug(
                "A work template is required for the session item in order to "
                "publish session. Not accepting the item."
            )
            accepted = False

        # ensure the publish template is defined and valid and that we also have
        publish_template = publisher.get_template_by_name(template_name)
        if not publish_template:
            self.logger.debug(
                "The valid publish template could not be determined for the "
                "session item. Not accepting the item."
            )
            accepted = False

        if accepted:
            # because a publish template is configured, disable context change. This
            # is a temporary measure until the publisher handles context switching
            # natively.
            item.context_change_allowed = False

        return { "accepted": accepted, "checked": accepted }

    def validate(self, settings, item):
        """
        Validates the given item to check that it is ok to publish. Returns a
        boolean to indicate validity.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process
        :returns: True if item is valid, False otherwise.
        """
        publisher = self.parent
        engine: SynthEyesEngine = publisher.engine
        hlev = engine.get_syntheyes_connection()
               
        # ---- ensure the session has been saved
        
        # get the normalized path
        path = sgtk.util.ShotgunPath.normalize(hlev.SNIFileName())
        if not path or hlev.HasChanged():
            # the session still requires saving. provide a save button.
            # validation fails.
            error_msg = "The SynthEyes session has not been saved."
            self.logger.error(error_msg, extra=_get_save_as_action())
            raise Exception(error_msg)

        item.properties["publish_type"] = "SynthEyes Undistorted Plate"
        template_id = settings["Publish Template"].value
        publish_template = publisher.get_template_by_name(template_id)
        item.properties["publish_template"] = publish_template
        
        # get the configured work file template
        work_template = item.parent.properties.get("work_template")

        # get the current scene path and extract fields from it using the work template:
        work_fields = work_template.get_fields(path)
        # set the export_name for syntheyes required to resolve the publish path
        item_name = item.name.replace(" ", "_")
        work_fields["syntheyes.export_name"] = item_name
        work_fields["syntheyes.frame"] = "1001"

        # create the publish path by applying the fields. store it in the item's
        # properties. This is the path we'll create and then publish in the base
        # publish plugin. Also set the publish_path to be explicit.
        item.properties["path"] = sgtk.util.ShotgunPath.normalize(publish_template.apply_fields(work_fields))
        item.properties["publish_path"] = item.properties["path"]
        
        # get frame name template and apply the work fields to it as well
        template_id = settings["Frame Name Template"].value
        frame_name_template = publisher.get_template_by_name(template_id)
        item.properties["frame_name_template"] = frame_name_template
        item.properties["frame_name"] = frame_name_template.apply_fields(work_fields)

        # use the work file's version number when publishing
        if "version" in work_fields:
            item.properties["publish_version"] = work_fields["version"]

        # run the base class validation
        if super(SyntheyesUndistortedPlatePublishPlugin, self).validate(settings, item):
            self.item_property_cache[id(item)] = dict(item.properties)
            return True
        return False

    def publish(self, settings, item):
        """
        Executes the publish logic for the given item and settings.

        :param settings: Dictionary of Settings. The keys are strings, matching
            the keys returned in the settings property. The values are `Setting`
            instances.
        :param item: Item to process
        """

        item.properties.clear()
        item.properties.update(self.item_property_cache[id(item)])

        publisher = self.parent
        engine: SynthEyesEngine = publisher.engine

        # get the path to create and publish
        publish_path = item.properties["path"]

        # ensure the publish folder exists:
        self.parent.ensure_folder_exists(publish_path)

        # undistort and export plate
        hlev = engine.get_syntheyes_connection()
        for shot in hlev.Shots():
            if shot.uniqueID == item.properties["unique_id"]:
                self._render_undistorted_plate(settings, item, shot)
                break

        # Now that the path has been generated, hand it off to the
        super(SyntheyesUndistortedPlatePublishPlugin, self).publish(settings, item)

    def _render_undistorted_plate(self, settings, item, shot):
        publisher = self.parent
        engine: SynthEyesEngine = publisher.engine
        hlev = engine.get_syntheyes_connection()
        live = shot.live

        first_undo_block = "Prepare undistorted export"
        prepset_name = "sgtk_undistort_plate"
        prepset_path = os.path.abspath(os.path.join(self.disk_location, os.pardir, "prepsets", prepset_name + ".prp"))
        hlev.BeginShotChanges(shot)
        try:
            # 1. disable resampling in preprocessor
            live.stabilizeMode = float(int(live.stabilizeMode) & ~128)
            live.Call("MakeStabilizeReference")
        
            # 2. setup render settings
            shot.renderFile = os.path.join(item.properties["path"], item.properties["frame_name"])
            shot.renderCompression = "exr: <DWAA32 Lossy>,100"
            
            # 3. load custom prepset
            shot.Call("LoadPrepSetsFromFile", 1, prepset_path)
        except Exception as e: raise e
        finally: hlev.AcceptShotChanges(shot, first_undo_block)

        # 4. Open 'Save Sequence' via the main menu and configure the export
        # Due to "Bad Tpye"-Errors when accessing most prepset-related variables, there 
        # seems to be no way to activate an imported prepset without said errors 
        # nor does it seem possible to access any kurve properties for the same reason.
        # Interacting directly with the popup, however, allows to set the prepset and
        # use it that way.
        hlev.PerformActionByIDAndContinue(40602) # Shot > Save Sequence
        timeout, timer = 5, 0 # Seconds
        # make sure the popup is open before proceeding
        while hlev.Popup().Name() != "Save Processed Image Sequence": #TODO Find better method to identify the popup other than using its name
            timer += 0.1
            if timer >= timeout:
                raise Exception("Timeout: Popup with title 'Save processed Image Sequence' not found after %ds", timer)

        popup = hlev.Popup()
        popup.ByID(1346).SetChecked(True) # RGB Included
        popup.ByID(1570).SetChecked(False) # Alpha Included
        popup.ByID(2250).SetChecked(False) # Meshes Included
        popup.ByID(2352).SetChecked(False) # Frame#/Time Burn-in
        popup.ByID(1400).SetOption(prepset_name) # prepset

        # 5. start save sequence
        popup.ByID(1).ClickAndContinue() # Start
        while popup.IsValid():
            if popup.hwnd != hlev.Popup().hwnd:
                # close error dialog
                error_dialog = hlev.Popup()
                error_msg = error_dialog.ByID(65535).Name() # text message
                error_dialog.ByID(2).ClickAndWait() # OK
                # close sequence popup
                popup.ByID(2).ClickAndWait() # close
                raise Exception(error_msg)
            time.sleep(0.033)

        # 6. revert all changes
        while hlev.UndoCount() and hlev.TopUndoName() != first_undo_block:
            hlev.Undo()
        hlev.Undo() # Undo once more to revert the first undo block

def _get_save_as_action():
    """
    Simple helper for returning a log action dict for saving the session
    """

    engine = sgtk.platform.current_engine()

    # default save callback
    callback = engine.save_session_as

    # if workfiles2 is configured, use that for file save
    if "tk-multi-workfiles2" in engine.apps:
        app = engine.apps["tk-multi-workfiles2"]
        if hasattr(app, "show_file_save_dlg"):
            callback = app.show_file_save_dlg

    return {
        "action_button": {
            "label": "Save As...",
            "tooltip": "Save the current session",
            "callback": callback,
        }
    }