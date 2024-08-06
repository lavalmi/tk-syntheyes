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
import SyPy3
from SyPy3.syobj import SyObj

from engine import SynthEyesEngine


HookBaseClass = sgtk.get_hook_baseclass()


class SyntheyesSessionCollector(HookBaseClass):
    """
    Collector that operates on the current SynthEyes session. Should inherit from
    the basic collector hook.
    """

    @property
    def settings(self):
        """
        Dictionary defining the settings that this collector expects to receive
        through the settings parameter in the process_current_session and
        process_file methods.

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

        # grab any base class settings
        collector_settings = super(SyntheyesSessionCollector, self).settings or {}

        # settings specific to this collector
        syntheyes_session_settings = {
            "Work Template": {
                "type": "template",
                "default": None,
                "description": "Template path for artist work files. Should "
                "correspond to a template defined in "
                "templates.yml. If configured, is made available"
                "to publish plugins via the collected item's "
                "properties. ",
            },
        }

        # update the base settings with these settings
        collector_settings.update(syntheyes_session_settings)

        return collector_settings

    def process_current_session(self, settings, parent_item):
        """
        Analyzes the current Syntheyes session and parents a subtree of items
        under the parent_item passed in.

        :param dict settings: Configured settings for this collector
        :param parent_item: Root item instance
        """
        # create an item representing the current syntheyes session
        session_item = self.collect_current_syntheyes_session(settings, parent_item)

        self.collect_cameras(settings, session_item)
        self.collect_camera_tracks(settings, session_item)
        self.collect_object_tracks(settings, session_item)
        self.collect_geometry(settings, session_item)
    
    def collect_current_syntheyes_session(self, settings, parent_item):
        """
        Creates an item that represents the current SynthEyes session.

        :param dict settings: Configured settings for this collector
        :param parent_item: Parent Item instance

        :returns: Item of type syntheyes.session
        """

        publisher = self.parent

        # retrieve connection to SynthEyes from the engine
        engine: SynthEyesEngine = publisher.engine
        hlev = engine.get_syntheyes_connection()
        
        # get the path to the current file
        path = hlev.SNIFileName()

        # determine the display name for the item
        if path:
            file_info = publisher.util.get_file_path_components(path)
            display_name = file_info["filename"]
        else:
            display_name = "Current SynthEyes Session"

        # create the session item for the publish hierarchy
        session_item = parent_item.create_item(
            "syntheyes.session", "SynthEyes File", display_name
        )
        session_item.properties["publish_type"] = "SynthEyes Scene"

        # get the icon path to display for this item
        icon_path = os.path.join(self.disk_location, os.pardir, "icons", "syntheyes.png")
        session_item.set_icon_from_path(icon_path)

        # if a work template is defined, add it to the item properties so that
        # it can be used by attached publish plugins
        work_template_setting = settings.get("Work Template")
        if work_template_setting:
            work_template = publisher.engine.get_template_by_name(
                work_template_setting.value
            )

            # store the template on the item for use by publish plugins. we
            # can't evaluate the fields here because there's no guarantee the
            # current session path won't change once the item has been created.
            # the attached publish plugins will need to resolve the fields at
            # execution time.
            session_item.properties["work_template"] = work_template
            self.logger.debug("Work template defined for SynthEyes collection.")

        self.logger.info("Collected current SynthEyes session")
        return session_item

    def collect_cameras(self, settings, parent_item):
        publisher = self.parent

        # retrieve connection to SynthEyes from the engine
        engine: SynthEyesEngine = publisher.engine
        hlev = engine.get_syntheyes_connection()

        # get the icon path to display for this item
        icon_path = os.path.join(self.disk_location, os.pardir, "icons", "camera.png")

        # iterate over all cameras
        cam: SyObj
        for cam in hlev.Cameras():
            cam_item = parent_item.create_item("syntheyes.camera", "Camera", cam.Name())
            cam_item.set_icon_from_path(icon_path)
            cam_item.properties["unique_id"] = cam.uniqueID

    def collect_object_tracks(self, settings, parent_item):
        """
        Creates and adds items to the parent_item, each of which represents an object track in the current SynthEyes session.

        :param dict settings: Configured settings for this collector
        :param parent_item: Parent Item instance
        """
        # retrieve connection to SynthEyes from the engine
        publisher = self.parent
        engine: SynthEyesEngine = publisher.engine
        hlev = engine.get_syntheyes_connection()

        icon_path = os.path.join(self.disk_location, os.pardir, "icons", "object_track.png")

        cams = hlev.Cameras()       
        obj: SyObj
        for obj in hlev.Objects():
            if obj in cams: continue
            
            # get the icon path to display for this item
            item = parent_item.create_item("syntheyes.object_track", "Object Track", obj.Name())
            item.set_icon_from_path(icon_path)
            item.properties["unique_id"] = obj.uniqueID

    def collect_camera_tracks(self, settings, parent_item):
        """
        Creates and adds items to the parent_item, each of which represents a camera track in the current SynthEyes session.

        :param dict settings: Configured settings for this collector
        :param parent_item: Parent Item instance
        """
        # retrieve connection to SynthEyes from the engine
        publisher = self.parent
        engine: SynthEyesEngine = publisher.engine
        hlev = engine.get_syntheyes_connection()

        # get the icon path to display for this item
        icon_path = os.path.join(self.disk_location, os.pardir, "icons", "camera_track.png")

        # iterate over all cameras
        cam: SyObj
        for cam in hlev.Cameras():
            if not cam.Trackers(): continue
            cam_item = parent_item.create_item("syntheyes.camera_track", "Camera Track", cam.Name())
            cam_item.set_icon_from_path(icon_path)
            cam_item.properties["unique_id"] = cam.uniqueID

    def collect_geometry(self, settings, parent_item):
        """
        Creates and adds an item to the parent_item that represents all static geometries in the current SynthEyes session.

        :param dict settings: Configured settings for this collector
        :param parent_item: Parent Item instance
        """
        # retrieve connection to SynthEyes from the engine
        publisher = self.parent
        engine: SynthEyesEngine = publisher.engine
        hlev = engine.get_syntheyes_connection()

        # if one static mesh is present, attach the scene geometry item and return
        mesh: SyObj
        for mesh in hlev.Meshes():
            if not mesh.Get("obj") and mesh.Get("isExported"):
                file = mesh.Get("file")
                if not file or len(file) < 4 or file[-4:].lower() != ".xyz":
                    # get the icon path to display for this item
                    icon_path = os.path.join(self.disk_location, os.pardir, "icons", "geometry.png")
                    geometry_item = parent_item.create_item("syntheyes.geometry", "Geometry", "Scene Geometry")
                    geometry_item.set_icon_from_path(icon_path)
                    break

    def collect_distortion_maps(self, settings, parent_item):
        pass