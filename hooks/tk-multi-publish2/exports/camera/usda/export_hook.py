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
                obj.Set("isExported", False)

        # disable export for all objects except the one corresponding to this item 
        item_unique_id = item.get_property("unique_id")
        
        # Even though an object is not to be exported, usda still generates a root node for said object.
        # Therefore, use delete here as well. Take note that the active object must not be deleted. Thus, the current item's camera 
        # has to be made the active object before deleting the current one.
        active_obj = hlev.Active()
        cam = None
        obj: SyObj
        for obj in hlev.Objects():
            if obj.uniqueID == item_unique_id:
                cam = obj
                hlev.SetActive(cam)
                active_obj = cam
            elif obj is not active_obj:
                hlev.Delete(obj)

        if cam is not active_obj:
            hlev.Delete(active_obj)
        
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