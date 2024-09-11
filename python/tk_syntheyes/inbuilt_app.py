from engine import SynthEyesEngine

class InbuiltApp(object):
    @property
    def display_name(self):
        """The name this app should be displayed as in the menu."""
        return ""
    
    @property
    def description(self):
        """Brief description of the app."""
        return ""
        
    @property
    def commands(self):
        """
        Contains a dictrionary of dictionries, which defines all commands of this app.
        Each command is made up of a name as the key and a dictionary containing its callback
        and some additional properties such as a reference to the app itself, a description and
        a list in which contexts the command should be displayed. 
        
        A dictionary on the following form:
        {
            "command_name":
            {
                "callback": self.some_function,
                "properties": {
                    "app": self,
                    "description": "some function description",
                    "context": ["asset_step", "element_step", "shot_step"]
                }
            }
        }
        """
        return {}

    def __init__(self, engine: SynthEyesEngine):
        self.engine = engine