import os

import SyPy3
from SyPy3.sylevel import SyLevel
from SyPy3.syobj import SyObj

def prepare(engine, settings, item):
    """
    Prepares SynthEyes for the imminent export. 
    This is highly dependant on the specific purpose of each hook and the implementation and settings of the associated exporter. 
    Drastically altering the scene file should be avoided. All changes to the SynthEyes scene should be done in Begin-Accept-blocks.
    This is necessary to automatically revert any changes after the export.
    Depending on whether the associated exporter supports it, the best way to exclude objects from the export process is to set their 
    'isExported'-attribute to false prior to the export.
    """
    hlev: SyLevel = engine.get_syntheyes_connection()
        
    hlev.Begin()
    try:
        for list in (hlev.Cameras(), hlev.Lights()):
            for obj in list:
                obj.isExported = False

        item_unique_id = item.get_property("unique_id")

        # make the camera corresponding to this item the active object
        for obj in hlev.Objects():
            if obj.uniqueID == item_unique_id:
                hlev.SetActive(obj.cam)
                break

        for mesh in hlev.Meshes():
            if not mesh.obj or mesh.obj.uniqueID != item_unique_id:
                mesh.isExported = False

        for tracker in hlev.Trackers():
            if tracker.obj.uniqueID != item_unique_id:
                tracker.isExported = False

    except Exception as e: raise e
    finally: hlev.Accept("Prepare Export")
        
#def export(engine, settings, item):
    #"""
    #Executes specific export logic. If this function is implemented, the default export behaviour is not called.
    #Therefore, the actual export functionality has to be specified here.
    #It should be preferred to use __init__() and the default export behaviour in most cases.
    #"""
    #pass

#def cleanup(engine, settings, item):
    #"""
    #Executes after the export has finished and all changes in SynthEyes are already undone.
    #That should usually be sufficient. However, in case there is anything that has to be done afterwards, this can be implemented here.
    #"""
    #pass