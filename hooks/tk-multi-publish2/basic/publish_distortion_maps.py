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
from pathlib import Path

from engine import SynthEyesEngine

HookBaseClass = sgtk.get_hook_baseclass()


class SyntheyesDistortionMapsPublishPlugin(HookBaseClass):
    """
    Plugin for publishing a pair of distortion maps for a SynthEyes camera.

    This hook relies on functionality found in the base file publisher hook in
    the publish2 app and should inherit from it in the configuration. The hook
    setting for this plugin should look something like this::

        hook: "{self}/publish_file.py:{engine}/tk-multi-publish2/basic/publish_distortion_maps.py"

    """

    @property
    def description(self):
        """
        Verbose, multi-line description of what the plugin does. This can
        contain simple html for formatting.
        """

        return """
        <p>This plugin publishes distortion maps of a shot within the current session.
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
        base_settings = super(SyntheyesDistortionMapsPublishPlugin, self).settings or {}

        # settings specific to this class
        syntheyes_publish_settings = {
            "Publish Template": {
                "type": "template",
                "default": None,
                "description": "Template path for published work files. Should"
                               "correspond to a template defined in "
                               "templates.yml.",
            },
            "Undistort Template": {
                "type": "template",
                "default": None,
                "description": "String template for publishing undistort images. Should"
                               "correspond to a string template defined in templates.yml.",
            },
            "Redistort Template": {
                "type": "template",
                "default": None,
                "description": "String template for publishing redistort images. Should"
                               "correspond to a string template defined in templates.yml.",
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
        return ["syntheyes.distortion_maps"]

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

        item.properties["publish_type"] = "SynthEyes Distortion Maps"
        template_id = settings["Publish Template"].value
        publish_template = publisher.get_template_by_name(template_id)
        item.properties["publish_template"] = publish_template
        
        # get the configured work file template
        work_template = item.parent.properties.get("work_template")

        # get the current scene path and extract fields from it using the work template:
        work_fields = work_template.get_fields(path)
        # set the export_name for syntheyes required to resolve the publish path
        item_name = item.name.replace(" ", "_")
        item_name = re.sub("[.,-,_]*v\d*", "", item_name)
        work_fields["syntheyes.export_name"] = item_name

        # ensure the fields work for the publish template
        missing_keys = publish_template.missing_keys(work_fields)
        if missing_keys:
            error_msg = (
                "Work file '%s' missing keys required for the "
                "publish template: %s" % (path, missing_keys)
            )
            raise Exception(error_msg)

        # resolve undistort and redistort template strings
        for template_id, prop_name in {"Undistort Template" : "undistort_name", "Redistort Template": "redistort_name"}.items():
            distort_template = publisher.get_template_by_name(settings[template_id].value)
            missing_keys = distort_template.missing_keys(work_fields)
            if missing_keys:
                error_msg = (
                    "%s is missing required keys: %s" % (template_id, missing_keys)
                )
                raise Exception(error_msg)
            item.properties[prop_name] = distort_template.apply_fields(work_fields)            

        # create the publish path by applying the fields. store it in the item's
        # properties. This is the path we'll create and then publish in the base
        # publish plugin. Also set the publish_path to be explicit.
        item.properties["path"] = sgtk.util.ShotgunPath.normalize(publish_template.apply_fields(work_fields))
        item.properties["publish_path"] = item.properties["path"]

        #item.properties["publish_name"] = item_name + "_distortion_maps"

        # use the work file's version number when publishing
        if "version" in work_fields:
            item.properties["publish_version"] = work_fields["version"]

        # run the base class validation
        if super(SyntheyesDistortionMapsPublishPlugin, self).validate(settings, item):
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

        # export distortion maps
        hlev = engine.get_syntheyes_connection()
        for shot in hlev.Shots():
            if shot.uniqueID == item.properties["unique_id"]:
                # define the export-relevant preferences and values 
                export_prefs = {
                    "exrUVMcmp" : "exr: <ZIP-scanline>,45",
                    "exrUVmap" : 4
                }
                # cache a few preferences to allow altering and restoring them before and after the export
                prefs = hlev.Prefs()
                pref_cache = {pref: prefs.Get(pref) for pref in export_prefs}

                # adjust the preferences
                hlev.BeginPref()
                try:
                    for pref, value in export_prefs.items(): prefs.Set(pref, value)
                except Exception as e: raise e
                finally: hlev.AcceptPref()

                # export maps on first frame of the shot
                frame = hlev.Frame()
                hlev.SetFrame(shot.start)
                shot.Call("WriteUndistortImage", os.path.join(publish_path, item.properties["undistort_name"]), 0)
                shot.Call("WriteRedistortImage", os.path.join(publish_path, item.properties["redistort_name"]), 0)

                hlev.SetFrame(frame)

                # restore the user's preferences
                hlev.BeginPref()
                try:
                    for pref, value in pref_cache.items(): prefs.Set(pref, value)
                except Exception as e: raise e
                finally: hlev.AcceptPref()

                break

        # Now that the path has been generated, hand it off to the
        super(SyntheyesDistortionMapsPublishPlugin, self).publish(settings, item)

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