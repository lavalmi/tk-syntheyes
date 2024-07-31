# Copyright (c) 2013 Shotgun Software Inc.
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

from SyPy3.syobj import SyObj
from engine import SynthEyesEngine

HookBaseClass = sgtk.get_hook_baseclass()


class BreakdownSceneOperations(HookBaseClass):
    """
    Breakdown operations for SynthEyes.

    This implementation handles detection of referenced files in SynthEyes.
    """

    def scan_scene(self):
        """
        The scan scene method is executed once at startup and its purpose is
        to analyze the current scene and return a list of references that are
        to be potentially operated on.

        The return data structure is a list of dictionaries. Each scene reference
        that is returned should be represented by a dictionary with three keys:

        - "node": The name of the 'node' that is to be operated on. Most DCCs have
          a concept of a node, path or some other way to address a particular
          object in the scene.
        - "type": The object type that this is. This is later passed to the
          update method so that it knows how to handle the object.
        - "path": Path on disk to the referenced object.

        Toolkit will scan the list of items, see if any of the objects matches
        any templates and try to determine if there is a more recent version
        available. Any such versions are then displayed in the UI as out of date.

        """

        items = []

        engine: SynthEyesEngine = self.parent.engine
        hlev = engine.get_syntheyes_connection()

        obj: SyObj
        for obj in hlev.Meshes():
            file = obj.Get("file")
            if not file:
                continue
            file: str = os.path.normpath(file)
            items.append({"node": str(obj.Name()), "type": str(obj.Type()), "path": str(file)})

        return items

    def update(self, items):
        """
        Perform replacements given a number of scene items passed from the app.

        Once a selection has been performed in the main UI and the user clicks
        the update button, this method is called.

        The items parameter is a list of dictionaries on the same form as was
        generated by the scan_scene hook above. The path key now holds
        the that each node should be updated *to* rather than the current path.
        """
        engine: SynthEyesEngine = self.parent.engine
        hlev = engine.get_syntheyes_connection()

        node_type_list = ["MESH"]

        for i in items:
            node_name = i["node"]
            node_type = i["type"]
            new_path = i["path"]#.replace(os.path.sep, "/")

            if node_type in node_type_list:
                engine.log_debug(
                    "Node %s: Updating to version %s" % (node_name, new_path)
                )
                if node_type == "MESH":
                    obj: SyObj = hlev.FindMeshByName(node_name)
                    if obj:
                        hlev.Begin()
                        try:
                            obj.Call("readMesh", new_path)
                        except Exception as e: raise e
                        finally: hlev.Accept("Update: {}".format(node_name))

    def find_node(self, node_name):
        engine: SynthEyesEngine = self.parent.engine
        hlev = engine.get_syntheyes_connection()
        
        obj: SyObj = hlev.FindMeshByName(node_name)
        if obj:
            hlev.Begin()
            try:
                hlev.Select1Object(obj)
            except Exception as e: raise e
            finally: hlev.Accept("Find: {}".format(node_name))