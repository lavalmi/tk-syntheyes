import os
import sys

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

sys.path.append(os.path.dirname(__file__))
from ui_main_window import Ui_MainWindow
from base_panel import BasePanel
from tk_syntheyes.app_command import AppCommand
from engine import SynthEyesEngine


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, engine: SynthEyesEngine=None, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self._engine = engine

        # Setup button hints
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, False)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
                
        self._minimize_on_close = True
        self._left_panel_active = True
        self._active_panel_depth = 0

        ### Initialize panels ###
        #from main_panel import MainPanel
        #self._main_panel: BasePanel = self._init_panel(BasePanel, "Main", None, True, True, True)
        self._main_panel: BasePanel = self._init_panel(BasePanel, "Main", None, True, True, True)
        # Create context menu button
        self._context_panel: BasePanel = self._init_panel(BasePanel, "Context", self._main_panel, False, False, True)
        self._main_panel.btn_context = self._main_panel.insert_menu_button(self._context_panel)
        self._link_panel(self._main_panel.btn_context, self._context_panel)
        self._main_panel.insert_line()
        
        if self._engine:
            import sgtk
            context: sgtk.Context = self._engine.context
            self._main_panel.btn_context.setText("{}, {}".format(context.project["name"], context.step))
        #########################

        # Initialize all available app commands
        self._init_commands()

        # Initialize quick select
        self.btn_quick_select.clicked.connect(lambda: self._switch_quick_select())
        self.btn_quick_select.setText(self._main_panel.name)

        # Set start panel
        self.pnl_left.layout().addWidget(self._main_panel)        
        
        # Disable standby panels just in case
        self.pnl_right.setEnabled = False

        ### Setup animations ###
        self._anim_panel_transition = QPropertyAnimation(self, b"panel_split_factor", self)
        self._anim_panel_transition.finished.connect(self._switch_panel_finished)

        self._anim_panel_quick_select_transition = QPropertyAnimation(self, b"main_split_factor", self)
        self._anim_panel_quick_select_transition.setEasingCurve(QEasingCurve.OutExpo)
        self._anim_panel_quick_select_transition.finished.connect(self._switch_quick_select_finished)
        ########################

        # Setup menu actions
        self.actionExit_SynthEyes.triggered.connect(self.exit)
        self.actionOpen_Console.triggered.connect(self.open_logging_console)

    
    def get_layout_stretch_steps(self, layout: QBoxLayout):
        """Return the total amount of stretch of the given layout."""
        return layout.stretch(0) + layout.stretch(1)

    def get_split_factor(self, layout: QBoxLayout):
        """Get the stretch ratio of the layout stretch values as a factor in range [0,1]"""
        stretch_steps = self.get_layout_stretch_steps(layout)
        if stretch_steps:
            return layout.stretch(0) / stretch_steps
        return 0.5

    def set_split_factor(self, layout: QBoxLayout, factor: float):
        """Set the stretch values of the layout to resemble the given factor in range [0,1]"""
        stretch_steps = self.get_layout_stretch_steps(layout)
        layout.setStretch(0, round(factor * stretch_steps))
        layout.setStretch(1, round((1 - factor) * stretch_steps))
    
    def set_main_panel_split_factor(self, factor: float):
        self.set_split_factor(self.main_split_layout, factor)

    def get_main_panel_split_factor(self):
        return self.get_split_factor(self.main_split_layout)
    
    def set_split_panel_split_factor(self, factor: float):
        self.set_split_factor(self.panel_split_layout, factor)

    def get_split_panel_split_factor(self):
        return self.get_split_factor(self.panel_split_layout)

    main_split_factor = Property(float, get_main_panel_split_factor, set_main_panel_split_factor)
    panel_split_factor = Property(float, get_split_panel_split_factor, set_split_panel_split_factor)


    def _init_panel(self, panel_type: type, name: str, parent_panel: QWidget, visible=False, enabled=False, add_to_quick_select=True):
        """Initiate a new panel and optionally automatically link it to the quick select by inserting a corresponding button."""
        if parent_panel:
            if not hasattr(parent_panel, "sub_panels"):
                parent_panel.sub_panels = {}
            if name in parent_panel.sub_panels:
                self._engine.log_debug("%s already exists in parent panel %s", name, parent_panel.name)
                return None
        
        panel: QWidget = panel_type(self)
        panel.setVisible(visible)
        panel.setEnabled(enabled)
        panel.name = name
        panel.sub_panels = {}
        panel.panel_depth = getattr(parent_panel, "panel_depth", 0) + 1 if parent_panel else 0

        # Add quick select button
        if add_to_quick_select:
            quick_select: QVBoxLayout = self.sca_quick_select_contents.layout()
            btn = QPushButton(text=name, parent=self.centralwidget)
            btn.clicked.connect(lambda: self._switch_panel(panel))
            quick_select.insertWidget(quick_select.count() - 1, btn)

        if parent_panel:
            parent_panel.sub_panels[name] = panel
            if panel_type is BasePanel or issubclass(panel_type, BasePanel):
                self._link_panel(panel.make_sub_panel(parent_panel), parent_panel)

        return panel


    def _init_commands(self):
        """Iterate over all commands retrieved from the engine and generate menu panels to reflect their respective hierarchy. Buttons are automatically created and linked to either the command or a subpanel."""
        # Enumerate all items and create menu objects for them
        favs = self._engine.get_setting("menu_favourites") if self._engine else {}
        engine_cmds = self._engine.commands.items() if self._engine else {}
        cmds: list[AppCommand] = []
        for (cmd_name, cmd_details) in engine_cmds:
            cmd = AppCommand(cmd_name, cmd_details)

            # Check if command is a favourite
            for fav in favs:
                app_instance_name = fav["app_instance"]
                menu_name = fav["name"]
                if cmd.get_app_instance_name() == app_instance_name and cmd.name == menu_name:
                    cmd.favourite = True

            cmds.append(cmd)
        
        # Sort list of commands in name order
        cmds.sort(key=lambda x: x.name)

        # now go through all of the menu items.
        # separate them out into various sections
        cmds_by_app = {}
        fav_pos = 2

        for cmd in cmds:
            if cmd.get_type() == "context_menu":
                # context menu
                self._add_command_button(cmd, self._context_panel)
            elif cmd.favourite:
                # favourites
                self._add_command_button(cmd, self._main_panel, fav_pos)
                fav_pos += 1
            else:
                # normal menu
                app_name = cmd.get_app_name()
                if app_name is None:
                    # un-parented app
                    app_name = "Other Items"
                if not app_name in cmds_by_app:
                    cmds_by_app[app_name] = []
                cmds_by_app[app_name].append(cmd)

        # Add line after favourites
        if fav_pos > 2:
            self._main_panel.insert_line()

        # Now add all apps to main menu
        for app_name in sorted(cmds_by_app.keys()):
            if len(cmds_by_app[app_name]) > 1:
                # more than one menu entry fort his app
                # make a sub menu and put all items in the sub menu
                app_panel = self._init_panel(BasePanel, app_name, self._main_panel)

                # get the list of menu commands for this app
                cmds = cmds_by_app[app_name]
                # make sure it is in alphabetical order
                cmds.sort(key=lambda x: x.name)

                for cmd in cmds:
                    if not cmd.favourite:
                        # skip favourites since they are already on the menu
                        self._add_command_button(cmd, app_panel)
            else:
                # this app only has a single entry.
                # display that on the menu
                cmd = cmds_by_app[app_name][0]
                if not cmd.favourite:
                    # skip favourites since they are already on the menu
                    self._add_command_button(cmd, self._main_panel)


    def _add_command_button(self, command: AppCommand, panel: BasePanel, row=-1):
        """Add a button to the given panel and linking its clicking action to the corresponding AppCommand retrieved from the engine."""
        # create menu sub-tree if need to:
        # Support menu items separated by '/'
        parts = command.name.split("/")
        for item_label in parts[:-1]:
            # see if there is already a sub-menu item
            sub_panel = panel.sub_panel[item_label]
            if sub_panel:
                # already have sub menu
                panel = sub_panel
            else:
                # create new sub menu
                sub_panel: BasePanel = self._init_panel(BasePanel, item_label, panel, False, False, False) #TODO Consider whether the sub panels should be added to the quick select or not
                self._link_panel(panel.insert_menu_button(sub_panel), sub_panel)
                self._link_panel(sub_panel.make_sub_panel(panel), panel)
                panel = sub_panel

        # Finally create the command button
        return panel.insert_button(None, parts[-1], -1, command.callback)
    

    def _link_panel(self, button, panel_to):
        """Link the given button to a panel. Clicking the button will start the panel switching transition to display the corresponding UI elements."""
        # Connect panels via button actions
        button.clicked.connect(lambda: self._switch_panel(panel_to))

    
    def closeEvent(self, event):
        """Window behaviour on close."""
        if self._minimize_on_close:
            self.setWindowState(Qt.WindowMinimized)
            event.ignore()
        else:
            self.settings.setValue("pos", self.pos())
            event.accept()

    
    def _switch_panel(self, target_panel: QWidget, easing_curve_type:QEasingCurve.Type=QEasingCurve.OutBounce, amplitude:float=0.25):
        """Initiate switching the currently displayed panel to another by starting an animation."""
        if self.btn_quick_select.isChecked():
            self.btn_quick_select.setChecked(False)
            self._switch_quick_select()
        
        # Check if the target panel is already active anyways
        active_layout: QLayout = self.pnl_left.layout() if self._left_panel_active else self.pnl_right.layout()
        active_panel = active_layout.itemAt(0).widget()
        if target_panel == active_panel:
            return
        
        # Disable panel during animation
        self.setEnabled(False)
        self._anim_panel_transition.stop()

        # Identify direction of the animation based on current and targeted panel depth
        left_to_right = getattr(target_panel, "panel_depth", 0) >= self._active_panel_depth

        # Change panel name 
        self.btn_quick_select.setText(target_panel.name)

        self._active_panel_depth += 1 if left_to_right else -1
        if self._left_panel_active and not left_to_right:
            self.pnl_right.layout().addWidget(self.pnl_left.layout().takeAt(0).widget())
            self.set_split_panel_split_factor(0)
        elif not self._left_panel_active and left_to_right:
            self.pnl_left.layout().addWidget(self.pnl_right.layout().takeAt(0).widget())
            self.set_split_panel_split_factor(1)

        # Switch panels if direction is reversed
        if left_to_right:
            panel_to = self.pnl_right
            end_value = 0
        else:
            panel_to = self.pnl_left
            end_value = 1

        # Add target panel and make it visible
        target_panel.setVisible(True)
        target_panel.setEnabled(True)
        panel_to.layout().addWidget(target_panel)
        
        split_factor = self.get_split_panel_split_factor()
        duration = 200 * (1 - split_factor if split_factor < end_value else split_factor)

        self._left_panel_active = not left_to_right

        self._anim_panel_transition.setDuration(duration)
        self._anim_panel_transition.setEndValue(end_value)
    
        easing_curve = QEasingCurve(easing_curve_type)
        easing_curve.setAmplitude(amplitude)
        self._anim_panel_transition.setEasingCurve(easing_curve)

        self.sca_left.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sca_right.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._anim_panel_transition.start()

   
    def _switch_panel_finished(self):
        """Wrap up the panel transition to ensure the UI can be properly used. This is automatically triggered once the respective animation has finished."""
        panel = self.pnl_right if self._left_panel_active else self.pnl_left
        item = panel.layout().takeAt(0)
        if item:
            widget = item.widget()
            if widget:
                widget.setParent(self.centralWidget())
                widget.setVisible(False)
                widget.setEnabled(False)
        self.sca_left.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.sca_right.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setEnabled(True)

   
    def _switch_quick_select(self):
        """Open the quick select panel by starting an animation."""
        self._anim_panel_quick_select_transition.stop()
        self.sca_quick_select.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        quick_select = self.btn_quick_select.isChecked()

        # If panel is not fully opened/closed shrink duration respectively
        split_factor = self.get_main_panel_split_factor()
        duration = 300 * (1 - split_factor if split_factor < quick_select else split_factor)

        self._anim_panel_quick_select_transition.setEndValue(quick_select)
        self._anim_panel_quick_select_transition.setDuration(duration)
        self._anim_panel_quick_select_transition.start()

  
    def _switch_quick_select_finished(self):
        """Wrap up the quick select panel transition to ensure the UI can be properly used. This is automatically triggered once the respective animation has finished."""
        self.sca_quick_select.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

  
    def open_logging_console(self):
        app = QCoreApplication.instance()
        win = app.property('tk-syntheyes.log_console')
        win.setHidden(False)
        win.activateWindow()
        win.raise_()


    def exit(self):
        """Exits the UI and engine if desired."""
        if self._engine:
            self._engine.exit()
        os._exit(0)

################################################################################

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.exec_()