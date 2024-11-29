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
        # disable export for all meshes and trackers
        for list in (hlev.Meshes(), hlev.Lights(), hlev.Trackers()):
            obj: SyObj
            for obj in list:
                obj.isExported = False

        # disable export for all objects except the one corresponding to this item 
        item_unique_id = item.get_property("unique_id")
        
        # Even though an object is not to be exported, usda still generates a root node for said object.
        # Therefore, delete it instead. Take note that deleting any object does not correct the active object, which is stored as an index.
        # Thus, deleting objects may cause SynthEyes to crash due an index-out-of-bounds error. While there are still objects to be deleted,
        # keep the first object in the list active and only once object deletion is completed set the correct active object.
        hlev.SetActive(hlev.Objects()[0])
        obj: SyObj
        for obj in hlev.Objects():
            if obj.uniqueID != item_unique_id:
                hlev.Delete(obj)
        
        # make the camera corresponding to this item the active object
        for cam in hlev.Cameras():
            if cam.uniqueID == item_unique_id:
                hlev.SetActive(cam)
                break

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