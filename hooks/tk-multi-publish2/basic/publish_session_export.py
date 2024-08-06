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
import sgtk
import shutil

from engine import SynthEyesEngine

HookBaseClass = sgtk.get_hook_baseclass()


class SyntheyesExportPublishPlugin(HookBaseClass):
    """
    Plugin for publishing a SynthEyes camera.

    This hook relies on functionality found in the base file publisher hook in
    the publish2 app and should inherit from it in the configuration. The hook
    setting for this plugin should look something like this::

        hook: "{self}/publish_file.py:{engine}/tk-multi-publish2/basic/publish_session.py"

    """

    # NOTE: The plugin icon and name are defined by the base file plugin.

    @property
    def description(self):
        """
        Verbose, multi-line description of what the plugin does. This can
        contain simple html for formatting.
        """

        return """
        <p>This plugin publishes session geometry for the current session. Any
        session geometry will be exported to the path defined by this plugin's
        configured "publish_template" setting. The plugin will fail to validate
        if the "AbcExport" plugin is not enabled or cannot be found.</p>
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
        base_settings = super(SyntheyesExportPublishPlugin, self).settings or {}

        # settings specific to this class
        syntheyes_publish_settings = {
            "publish_template": {
                "type": "template",
                "default": None,
                "description": "Template path for published work files. Should"
                               "correspond to a template defined in "
                               "templates.yml.",
            },
            "publish_type": {
                "type": "str",
                "default": None,
                "description": "",
            },
            "checked": {
                "type": "bool",
                "default": True,
                "description": "Is the task checked",
            },
            "enabled": {
                "type": "bool",
                "default": True,
                "description": "Is the task editable",
            },
            "type_spec": {
                "type": "str",
                "default": None,
                "description": "Item class",
            },
            "exporter": {
                "type": "str",
                "default": None,
                "description": "Folder in which to search for the sticky file and export hook",
            },
            "export_hook": {
                "type": "str",
                "default": "export_hook.py",
                "description": "Path to the export hook",
            },
            "export_type": {
                "type": "str",
                "default": None,
                "description": "SynthEyes export type",
            },
            "export_sticky": {
                "type": "str",
                "default": None,
                "description": "SynthEyes sticky file name for export settings",
            },
            "extension": {
                "type": "str",
                "default": None,
                "description": "Extension of exported file",
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
        return ["syntheyes.*"]

    @property
    def item_property_cache(self):
        """
        Backup of each valid item's properties. Since, in this case, mutliple
        plugins may work on the same item with varying publish paths, it cannot 
        be guaranteed that the properties of the article will remain the same as 
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
        template_name = settings["publish_template"].value

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
            if item.type_spec != type_spec(settings):
                accepted = False
                self.logger.debug("The item's type spec %s does not match the plugin's type spec %s. Not accepting the item.", item.type_spec, type_spec)
            else:
                # we've validated the publish template. add it to the item properties
                # for use in subsequent methods
                #item.properties["publish_template"] = publish_template

                # because a publish template is configured, disable context change. This
                # is a temporary measure until the publisher handles context switching
                # natively.
                item.context_change_allowed = False

        return {
            "accepted": accepted,
            "checked": accepted and settings["checked"].value,
            "enabled": settings["enabled"].value
        }

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

        # ---- check if the session contains unsaved changes
        #if hlev.HasChanged():
        #    error_msg = "The SynthEyes session has unsaved changes. Make sure to save your file first."
        #    self.logger.error(
        #        error_msg,
        #        extra=_get_save_action(),
        #    )
        #    raise Exception(error_msg)

        item.properties["publish_type"] = settings["publish_type"].value
        template_name = settings["publish_template"].value
        publish_template = publisher.get_template_by_name(template_name)
        item.properties["publish_template"] = publish_template

        # get the configured work file template
        work_template = item.parent.properties.get("work_template")

        # get the current scene path and extract fields from it using the work template:
        work_fields = work_template.get_fields(path)
        # set the export_name and export_extension for syntheyes required to resolve the publish path
        work_fields["syntheyes.export_name"] = item.name.replace(" ", "_")
        work_fields["syntheyes.export_extension"] = settings["extension"].value

        # ensure the fields work for the publish template
        missing_keys = publish_template.missing_keys(work_fields)
        if missing_keys:
            error_msg = (
                "Work file '%s' missing keys required for the "
                "publish template: %s" % (path, missing_keys)
            )
            raise Exception(error_msg)

        # create the publish path by applying the fields. store it in the item's
        # properties. This is the path we'll create and then publish in the base
        # publish plugin. Also set the publish_path to be explicit.
        item.properties["path"] = publish_template.apply_fields(work_fields)
        item.properties["publish_path"] = item.properties["path"]

        # use the work file's version number when publishing
        if "version" in work_fields:
            item.properties["publish_version"] = work_fields["version"]

        # run the base class validation
        if super(SyntheyesExportPublishPlugin, self).validate(settings, item):
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
        engine = publisher.engine

        # get the path to create and publish
        publish_path = item.properties["path"]

        # ensure the publish folder exists:
        publish_folder = os.path.dirname(publish_path)
        self.parent.ensure_folder_exists(publish_folder)

        # invokes the respective syntheyes exporter
        try:
            self._export(settings, item)
        except Exception as e:
            self.logger.error("Failed to export {} {}: {}".format(item.type_spec, item.name, e))
            return

        #raise Exception("DEBUG do not publish")

        # Now that the path has been generated, hand it off to the
        super(SyntheyesExportPublishPlugin, self).publish(settings, item)

    def _export(self, settings, item):
        publisher = self.parent
        engine: SynthEyesEngine = publisher.engine        
        hlev = engine.get_syntheyes_connection()
        hlev.FlushUndo()

        exporter = sgtk.util.ShotgunPath.normalize(settings["exporter"].value)
        export_hook = sgtk.util.ShotgunPath.normalize(settings["export_hook"].value)
        export_type = settings["export_type"].value
        export_sticky = settings["export_sticky"].value

        sticky_path = os.path.join(os.getenv("APPDATA"), "SynthEyes", "sticky") #TODO Check AppData equivalents on linux and mac and implement os-specific logic if necessary

        ### 1. Construct path if exporter was not specified as an absolute path
        if not os.path.isabs(exporter):
            exporter = os.path.abspath(os.path.join(self.disk_location, os.pardir, "exports", exporter))

        self.logger.info("Loading exporter: %s", exporter)

        if not os.path.exists(exporter):
            error_msg = "The defined exporter directory does not exist: {}".format(exporter)
            self.logger.error(error_msg)
            raise Exception(error_msg)
        
        ### 2. backup user's export config file
        sticky = os.path.join(sticky_path, export_sticky + ".txt")
        sticky_backup = sticky + ".user"
        if os.path.isfile(sticky_backup):
            os.remove(sticky_backup)
        os.rename(sticky, sticky_backup)
        
        ### 3. move publish export file to the sticky config location
        export_sticky_abs = os.path.join(exporter, export_sticky + ".txt")
        if not os.path.exists(export_sticky_abs):
            error_msg = "The defined export sticky file does not exist: {}".format(sticky)
            self.logger.error(error_msg)
            raise Exception(error_msg)
        shutil.copy(export_sticky_abs, sticky)

        ### 4. find and execute export_hook.py
        hook_path = os.path.abspath(os.path.join(exporter, export_hook))
        hook = None
        if os.path.isfile(hook_path):
            import importlib
            from pathlib import Path
            hook_spec = importlib.util.spec_from_file_location(Path(export_hook).stem, hook_path)

            if hook_spec:
                self.logger.info("Loading export hook: %s", hook_path)
                hook = importlib.util.module_from_spec(hook_spec)
                hook_spec.loader.exec_module(hook)
                if hook and hasattr(hook, "prepare"):
                    hook.prepare(engine, settings, item)

        ### 5. actual export
        if hook and hasattr(hook, "export"):
            hook.export(engine, settings, item)
        else:
            hlev.Export(export_type, item.properties["path"])

        ### 6. restore user's export config file
        os.remove(sticky)
        os.rename(sticky_backup, sticky)

        ### 7. undo any changes made during the export
        while hlev.UndoCount():
            hlev.Undo()

        ### 8. execute hook's cleanup function
        if hook and hasattr(hook, "cleanup"):
            hook.cleanup(engine, settings, item)

        hlev.FlushUndo()
        hlev.ClearChanged()

def type_spec(settings):
    return "syntheyes." + settings["type_spec"].value

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

def _get_save_action():
    """
    Simple helper for returning a log action dict for saving unsaved changes in the current session
    """

    engine: SynthEyesEngine = sgtk.platform.current_engine()
    callback = engine.save_session

    return {
        "action_button": {
            "label": "Save",
            "tooltip": "Save unsaved changes",
            "callback": callback
        }
    }