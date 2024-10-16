# Copyright (c) 2017 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import glob
import os
import re
import sgtk
import SyPy3
from SyPy3.syobj import SyObj
from pathlib import Path

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
            "Playblast Template": {
                "type": "template",
                "default": None,
                "description": "Template path for playblast work files. Should "
                "correspond to a template defined in templates.yml. If configured,"
                "is made available to publish plugins via the collected item's "
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
        self.collect_distortion_maps(settings, session_item)
        self.collect_camera_plates(settings, session_item)
        self.collect_camera_tracks(settings, session_item)
        self.collect_object_tracks(settings, session_item)
        self.collect_geometry(settings, session_item)
        self.collect_playblasts(settings, session_item)
    
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
            scene_item = self.get_or_create_item_parent(cam.Name(), icon_path, parent_item)
            cam_item = scene_item.create_item("syntheyes.camera", "Camera", cam.Name())
            cam_item.set_icon_from_path(icon_path)
            cam_item.properties["unique_id"] = cam.uniqueID
            cam_item.expanded = False

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

        # get the icon path to display for this item
        icon_path = os.path.join(self.disk_location, os.pardir, "icons", "object_track.png")
        parent_icon_path = os.path.join(self.disk_location, os.pardir, "icons", "object.png")

        cams = hlev.Cameras()       
        obj: SyObj
        for obj in hlev.Objects():
            if obj in cams: continue
            
            scene_item = self.get_or_create_item_parent(obj.Name(), parent_icon_path, parent_item)
            item = scene_item.create_item("syntheyes.object_track", "Object Track", obj.Name())
            item.set_icon_from_path(icon_path)
            item.properties["unique_id"] = obj.uniqueID
            item.expanded = False

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
            scene_item = self.get_or_create_item_parent(cam.Name(), icon_path, parent_item)
            cam_item = scene_item.create_item("syntheyes.camera_track", "Camera Track", cam.Name())
            cam_item.set_icon_from_path(icon_path)
            cam_item.properties["unique_id"] = cam.uniqueID
            cam_item.expanded = False

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
                if not file or os.path.splitext(file)[1].lower() != ".xyz":
                    # get the icon path to display for this item
                    icon_path = os.path.join(self.disk_location, os.pardir, "icons", "geometry.png")
                    geometry_item = parent_item.create_item("syntheyes.geometry", "Geometry", "Scene Geometry")
                    geometry_item.set_icon_from_path(icon_path)
                    geometry_item.expanded = False
                    break

    def collect_distortion_maps(self, settings, parent_item):
        """
        Creates and adds an item to the parent_item to export distortion maps for the corresponding shot in the current SynthEyes session.

        :param dict settings: Configured settings for this collector
        :param parent_item: Parent Item instance
        """
        # retrieve connection to SynthEyes from the engine
        publisher = self.parent
        engine: SynthEyesEngine = publisher.engine
        hlev = engine.get_syntheyes_connection()

        # get the icon path to display for this item
        icon_path = os.path.join(self.disk_location, os.pardir, "icons", "distortion_maps.png")
        parent_icon_path = os.path.join(self.disk_location, os.pardir, "icons", "camera.png")

        for shot in hlev.Shots():          
            # alternatively use: shot.live.lensHasDistortion -> always outputs True for fisheye lenses
            # lensAtDefaults reflects whether changes were made to the default values of all lenses.
            if not shot.live.lensAtDefaults and not shot.live.isImageMap:
                scene_item = self.get_or_create_item_parent(shot.cam.Name(), parent_icon_path, parent_item)
                dist_item = scene_item.create_item("syntheyes.distortion_maps", "Distortion Maps", shot.cam.Name())
                dist_item.set_icon_from_path(icon_path)
                dist_item.properties["unique_id"] = shot.uniqueID
                dist_item.properties["shot_path"] = shot.Name()
                dist_item.expanded = False

    def collect_camera_plates(self, settings, parent_item):
        """
        Creates and adds an item to the parent_item that represents a plate that can be undistorted.

        :param dict settings: Configured settings for this collector
        :param parent_item: Parent Item instance
        """
        # retrieve connection to SynthEyes from the engine
        publisher = self.parent
        engine: SynthEyesEngine = publisher.engine
        hlev = engine.get_syntheyes_connection()

        # get the icon path to display for this item
        icon_path = os.path.join(self.disk_location, os.pardir, "icons", "undistorted_plate.png")
        parent_icon_path = os.path.join(self.disk_location, os.pardir, "icons", "camera.png")

        for cam in hlev.Cameras():
            # alternatively use: shot.live.lensHasDistortion -> always outputs True for fisheye lenses
            # lensAtDefaults reflects whether changes were made to the default values of all lenses.
            shot = cam.shot
            if not shot.live.lensAtDefaults or shot.live.isImageMap:
                scene_item = self.get_or_create_item_parent(cam.Name(), parent_icon_path, parent_item)
                plate_item = scene_item.create_item("syntheyes.undistorted_plate", "Undistorted Plate", cam.Name())
                plate_item.set_icon_from_path(icon_path)
                plate_item.properties["unique_id"] = cam.uniqueID
                plate_item.expanded = False

    def collect_playblasts(self, settings, parent_item):
        """
        Creates and adds an item to the parent_item to publish a rendered playblast from the work files for each camera.

        :param dict settings: Configured settings for this collector
        :param parent_item: Parent Item instance
        """
        # retrieve connection to SynthEyes from the engine
        publisher = self.parent
        engine: SynthEyesEngine = publisher.engine
        hlev = engine.get_syntheyes_connection()     
            
        playblast_template_name = settings.get("Playblast Template").value
        if not playblast_template_name:
            raise Exception("Can't collect playblasts: Playblast Template is not available in the collector settings.")
        
        playblast_template = engine.get_template_by_name(playblast_template_name)

        path = sgtk.util.ShotgunPath.normalize(hlev.SNIFileName())
        work_template = parent_item.properties.get("work_template")
        work_fields = work_template.get_fields(path)
        work_fields["playblast_extension"] = "jpg" #TODO add an option to select png or jpg
        work_fields["SEQ"] = 9999

        icon_path = os.path.join(self.disk_location, os.pardir, "icons", "playblast.png")
        parent_icon_path = os.path.join(self.disk_location, os.pardir, "icons", "camera.png")

        for cam in hlev.Cameras():
            work_fields["syntheyes.export_name"] = cam.Name().replace(" ", "_")
            playblast_path = playblast_template.apply_fields(work_fields)
            if not os.path.exists(os.path.dirname(playblast_path)): continue

            playblast_path = playblast_path.replace("9999", "*")
            self.logger.debug("Searching in: %s" % (playblast_path,))
            playblast_files = sorted(glob.glob(playblast_path))
            if not len(playblast_files): continue

            # get first and last frame and see if they match the camera's shot
            first_frame = playblast_template.get_fields(playblast_files[0])["SEQ"]
            last_frame = playblast_template.get_fields(playblast_files[-1])["SEQ"]

            shot = cam.shot            
            if (shot.stop - shot.start + 1 != len(playblast_files) 
                or first_frame != shot.start + shot.frameMatchOffset 
                or last_frame != shot.stop + shot.frameMatchOffset):
                continue

            # create and add the item
            scene_item = self.get_or_create_item_parent(cam.Name(), parent_icon_path, parent_item)
            item = scene_item.create_item("file.image.sequence", "Playblast", cam.Name())

            item.properties["sequence_paths"] = playblast_files
            item.properties["first_frame"] = first_frame
            item.properties["last_frame"] = last_frame
            item.properties["path"] = playblast_path.replace("*", "%04d")

            # get the icon path to display for this item
            item.set_icon_from_path(icon_path)

            item.properties["unique_id"] = cam.uniqueID
            item.expanded = False


    @property
    def item_parents(self):
        if not hasattr(self, "_item_parents"):
            self._item_parents = {}
        return self._item_parents
    
    def get_or_create_item_parent(self, name, icon, parent_item):
        parent = self.item_parents.get(name)
        if not parent:
            parent = parent_item.create_item("syntheyes.scene_item", "Scene Item", name)
            parent.properties["work_template"] = parent_item.properties.get("work_template")
            parent.set_icon_from_path(icon)
            self.item_parents[name] = parent
        return parent