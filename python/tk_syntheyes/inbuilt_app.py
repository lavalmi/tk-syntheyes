from PySide2.QtWidgets import QMessageBox
from PySide2.QtCore import Qt

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
    def author(self):
        """Name of the app author."""
        return ""

    @property
    def commands(self):
        """
        Contains a dictionary of dictionries, which defines all commands of this app.
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

    @property
    def full_name(self):
        return f"{self.__module__}.{type(self).__name__}"

    @property
    def is_user_app(self):
        is_user_app = getattr(self, "_is_user_app", None)
        if is_user_app is None:
            self._is_user_app = True
        return self._is_user_app

    def __init__(self, engine):
        self.engine = engine

    def get_syntheyes_connection(self):
        return self.engine.get_syntheyes_connection()
    
    def message_box(self, icon, title, text, buttons=QMessageBox.Ok, parent=None, flags=Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint | Qt.WindowStaysOnTopHint):
        return self.engine.ui.message_box(icon, title, text, buttons, parent, flags)

    def status_message(self, text, timeout=4000):
        self.engine.ui.status_message(text, timeout)