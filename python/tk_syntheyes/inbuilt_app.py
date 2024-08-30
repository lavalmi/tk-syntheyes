from engine import SynthEyesEngine

class InbuiltApp(object):
    @property
    def display_name(self):
        return ""
    
    @property
    def description(self):
        return ""
        
    @property
    def commands(self):
        return {
            # "app_name":
            # {
            #     "callback": self.some_function,
            #     "properties": {
            #         "app": self,
            #         "description": "some function description",
            #         "context": ["asset_step", "element_step", "shot_step"]
            #     }
            # }
        }

    def __init__(self, engine: SynthEyesEngine):
        self.engine = engine