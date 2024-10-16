import importlib.util
import os
import sys
import time

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

sys.path.append(os.path.dirname(__file__))
from ui_main_window import Ui_MainWindow
from base_panel import BasePanel
from tk_syntheyes.app_command import AppCommand
from tk_syntheyes.inbuilt_app import InbuiltApp
from engine import SynthEyesEngine

from configparser import SafeConfigParser

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, engine: SynthEyesEngine=None, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setupUi(self)

        self._engine = engine
        self.click_pos = None
        self._menu_click_time = time.time()
        
        self._auto_resize = self.actionAuto_Resize.isChecked
        self._stays_on_top = self.actionStays_On_Top.isChecked
        self._borderless = self.actionBorderless.isChecked
        self._config = SafeConfigParser()
        self._load_config()

        # Setup window hints
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, False)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
                
        self._left_panel_active = True
        self._panels = []        
        self._minimize_on_close = True
        
        # Generate panels
        self.generate_panels()

        # Initialize quick select
        self.btn_quick_select.clicked.connect(lambda: self._switch_quick_select())

        ### Setup animations ###
        self._anim_panel_transition = QPropertyAnimation(self, b"panel_split_factor", self)
        self._anim_panel_transition.finished.connect(self._switch_panel_finished)

        self._anim_panel_quick_select_transition = QPropertyAnimation(self, b"main_split_factor", self)
        self._anim_panel_quick_select_transition.setEasingCurve(QEasingCurve.OutExpo)
        self._anim_panel_quick_select_transition.finished.connect(self._switch_quick_select_finished)

        self._anim_window_geom = QPropertyAnimation(self, b"size", self)
        self._anim_window_geom.setEasingCurve(QEasingCurve.OutExpo)
        ########################

        # Setup menu actions
        self.actionExit_SynthEyes.triggered.connect(self.exit)
        self.actionOpen_Console.triggered.connect(self.open_logging_console)
        self.actionAuto_Resize.triggered.connect(self._update_auto_resize)
        self.actionStays_On_Top.triggered.connect(self._update_stays_on_top)
        self.actionBorderless.triggered.connect(self._update_borderless)
        self.actionMinimize_Window.triggered.connect(self.minimize)
        self.actionRecenter_Window.triggered.connect(self.recenter_window)
        self.actionMove_to_Cursor.triggered.connect(self.move_window_to_cursor)
        
        # Connect shortcuts to actions
        self.actionRecenter_Window.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_R))
        self.actionMove_to_Cursor.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_M))

        # Setup menu bar move on drag behaviour
        self.menubar: QMenuBar
        self.menubar.defaultMousePressEvent = self.menubar.mousePressEvent
        self.menubar.mousePressEvent = self.menu_mouse_press_event
        self.menubar.defaultMouseMoveEvent = self.menubar.mouseMoveEvent
        self.menubar.mouseMoveEvent = self.move_window
        self.menubar.defaultMouseDoubleClickEvent = self.menubar.mouseDoubleClickEvent
        self.menubar.mouseDoubleClickEvent = self.menu_double_click_event


    def move_window(self, event):
        if not (self.click_pos is None or self.isMaximized()):
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.click_pos)
                self.click_pos = event.globalPos()
                event.accept()
                return
        
        self.menubar.defaultMouseMoveEvent(event)

    def recenter_window(self):
        screen = QGuiApplication.screenAt(QCursor().pos())
        fg = self.frameGeometry()
        fg.moveCenter(screen.geometry().center())
        self.move(fg.topLeft())
    
    def move_window_to_cursor(self):
        self.move(QCursor().pos())

    def menu_mouse_press_event(self, event):
        self._menu_click_time = time.time()
        self.click_pos = event.globalPos()
        self.menubar.defaultMousePressEvent(event)
    
    def menu_double_click_event(self, event):
        if (time.time() - self._menu_click_time) * 1000 < 175: #ms
            self.minimize()
            event.accept()
        else:
            self.menubar.defaultMouseDoubleClickEvent(event)
    
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
    
    ### Properties ###
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
    ##################


    def _init_panel(self, panel_type: type, name: str, parent_panel: QWidget, visible=False, enabled=False, add_to_quick_select=True):
        """Initiate a new panel and optionally automatically link it to the quick select by inserting a corresponding button."""
        if parent_panel:
            if not hasattr(parent_panel, "sub_panels"):
                parent_panel.sub_panels = {}
            if name in parent_panel.sub_panels:
                self._engine.log_debug("%s already exists in parent panel %s", name, parent_panel.name)
                return None
        
        panel: panel_type = panel_type(self)
        panel.setVisible(visible)
        panel.setEnabled(enabled)
        panel.name = name
        panel.sub_panels = {}
        panel.panel_depth = getattr(parent_panel, "panel_depth", 0) + 1 if parent_panel else 0
        self._panels.append(panel)

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

    @property
    def inbuilt_apps(self):
        if not getattr(self, "_inbuilt_apps", None):
            self._inbuilt_apps = {}
            inbuilt_apps_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, "inbuilt_apps"))
            if os.path.isdir(inbuilt_apps_path):
                import importlib
                import inspect
                for file in os.listdir(inbuilt_apps_path):
                    file_path = os.path.join(inbuilt_apps_path, file)
                    if not os.path.isfile(file_path): continue

                    spec = importlib.util.spec_from_file_location(file.rsplit(".", 1)[0], file_path)
                    if not spec: continue

                    self._engine.log_debug("Loading inbuilt app: %s", file)
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    if not mod: continue

                    # iterate over all classes
                    for cls_name, cls in inspect.getmembers(mod, inspect.isclass):
                        if cls != InbuiltApp and issubclass(cls, InbuiltApp):
                            self._inbuilt_apps[cls_name] = cls(self._engine)
            
        return self._inbuilt_apps


    def _clear_inbuilt_apps(self):
        if hasattr(self, "_inbuilt_apps"):
            del self._inbuilt_apps


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
        
        # Add inbuilt apps
        app: InbuiltApp
        for app_name, app in self.inbuilt_apps.items():
            for cmd_name, cmd_details in app.commands.items():
                cmd = AppCommand(cmd_name, cmd_details)
                props = getattr(cmd, "properties")
                if props:
                    if "environment" in props:
                        if self._engine.environment["name"] in props["environment"]:
                            cmds.append(cmd)
                    else:
                        cmds.append(cmd)
                
        # Sort list of commands in name order
        cmds.sort(key=lambda x: x.name) #TODO incorrect sorting at times

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
                if not app_name:
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
                # more than one menu entry for this app
                # make a sub menu and put all items in the sub menu
                app_panel: BasePanel = self._init_panel(BasePanel, app_name, self._main_panel)
                self._link_panel(self._main_panel.insert_menu_button(app_panel), app_panel)

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
        """Add a button to the given panel and link its clicking action to the corresponding AppCommand retrieved from the engine."""
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
                panel = sub_panel

        # Finally create the command button
        return panel.insert_button(None, parts[-1], -1, command.callback)
    

    def _link_panel(self, button, panel_to):
        """Link the given button to a panel. Clicking the button will start the panel switching transition to display the corresponding UI elements."""
        # Connect panels via button actions
        button.clicked.connect(lambda: self._switch_panel(panel_to))


    def regenerate_panels(self):
        # Clear current UI elements based on the old context
        layout = self.sca_quick_select_contents.layout()
        while layout.count() > 1:
            item: QLayoutItem = layout.takeAt(0)
            if item: 
                widget = item.widget()
                if widget: 
                    widget.deleteLater()

        for panel in self._panels:
            panel.deleteLater()
        self._panels.clear()
                
        # Generate the UI again with the new context
        self.generate_panels()
        

    def generate_panels(self):
        ### Initialize panels ###
        self._main_panel: BasePanel = self._init_panel(BasePanel, "Main", None, True, True, True)
        # Create context menu
        context_name = "Context"
        if self._engine:
            import sgtk
            context: sgtk.Context = self._engine.context
            #context_name: str = "{}, {}".format(context.project["name"], context.step["name"])
            context_name: str = str(context)

        self._context_panel: BasePanel = self._init_panel(BasePanel, context_name, self._main_panel, False, False, True)
        self._main_panel.btn_context = self._main_panel.insert_menu_button(self._context_panel)
        self._main_panel.btn_context.setText(context_name)
        self._link_panel(self._main_panel.btn_context, self._context_panel)
                
        ######### DEBUG #########
        from helper_functions import strtobool

        if strtobool(os.environ.get("__DEV__", None)):
            self.generate_dev_panel()
        #########################

        self._main_panel.insert_line()

        self._clear_inbuilt_apps()

        # Initialize all available app commands
        self._init_commands()

        # Initialize quick select
        self.btn_quick_select.setText(self._main_panel.name)

        # Set start panel
        active_panel: QWidget = self.pnl_left if self._left_panel_active else self.pnl_right
        active_panel.layout().addWidget(self._main_panel)
        self._active_panel_depth = self._main_panel.panel_depth

        if self._auto_resize():
            # Process qt events to make sure that the preferred size of the window is updated before accessing the panels preferred size
            QApplication.processEvents()

            # Match starting panel's preferred size
            pref_size = self._get_preferred_panel_size(self._main_panel)
            if pref_size is not None:
                self.resize(pref_size)


    def generate_dev_panel(self):
        self._dev_panel: BasePanel = self._init_panel(BasePanel, "DEV", self._main_panel)
        self._link_panel(self._main_panel.insert_menu_button(self._dev_panel), self._dev_panel)
        

    def closeEvent(self, event):
        """Window behaviour on close."""
        if self._minimize_on_close:
            self.setWindowState(Qt.WindowMinimized)
            event.ignore()
        else:
            self.settings.setValue("pos", self.pos())
            event.accept()


    def minimize(self):
        self.setWindowState(Qt.WindowMinimized)

    
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
        self.sca_left.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sca_right.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)        
        
        if self._auto_resize():
            # Adjust geometry of the window to fix the new panel
            pref_size = self._get_preferred_panel_size(target_panel)
            if pref_size is not None:
                self._anim_window_geom.setDuration(duration)
                self._anim_window_geom.setEndValue(pref_size)
                self._anim_window_geom.start()

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
        self.sca_left.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.sca_right.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setEnabled(True)

   
    def _switch_quick_select(self):
        """Open the quick select panel by starting an animation."""
        self._anim_panel_quick_select_transition.stop()
        self.sca_quick_select.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sca_left.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sca_right.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

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
        self.sca_left.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.sca_right.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)


    def _get_preferred_panel_size(self, panel: QWidget):
        pref_width = getattr(panel, "preferred_width", None)
        if pref_width is not None:
            size: QSize = self.sizeHint() + panel.sizeHint()
            return QSize(size.width() + pref_width, size.height())
        return None


    def _update_auto_resize(self):
        if self._auto_resize():
            # Adjust geometry of the window to fix the new panel
            target_panel = self.pnl_left if self._left_panel_active else self.pnl_right
            if target_panel:
                item = target_panel.layout().itemAt(0)
                if item:
                    target_panel = item.widget()
                    pref_size = self._get_preferred_panel_size(target_panel)
                    if pref_size is not None:
                        self._anim_window_geom.setDuration(300)
                        self._anim_window_geom.setEndValue(pref_size)
                        self._anim_window_geom.start()


    def _update_stays_on_top(self, override = None):
        self.setWindowFlag(Qt.WindowStaysOnTopHint, self._stays_on_top() if override is None else override)
        if self._update_flags:
            self.show()


    def _update_borderless(self):
        self.setWindowFlag(Qt.FramelessWindowHint, self._borderless())
        if self._update_flags:
            self.show()

    
    def to_front(self, all_windows=True):
        if all_windows:
            for window in QApplication.allWindows():
                window.raise_()
                window.activateWindow()
        else:
            self.activateWindow()
            
  
    def open_logging_console(self):
        app = QCoreApplication.instance()
        win = app.property('tk-syntheyes.log_console')
        win.setHidden(False)
        win.activateWindow()
        win.raise_()


    def exit(self):
        """Exits the UI and engine if desired."""
        self._save_config()
        if self._engine:
            self._engine.exit()
        os._exit(0)

### Dialog #####################################################################

    def message_box(self, icon, title, text, buttons=QMessageBox.Ok, parent=None, flags=Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint | Qt.WindowStaysOnTopHint):
        
        msg_box = QMessageBox(icon, title, text, buttons, parent, flags)
        msg_box.show()
        
        screen = QGuiApplication.screenAt(QCursor().pos())
        fg = msg_box.frameGeometry()
        fg.moveCenter(screen.geometry().center())
        msg_box.move(fg.topLeft())
     
        return msg_box.exec_()

### Config #####################################################################
    
    def _user_path(self):
        user_path = {"darwin": "~/Library/Application Support/SynthEyes",
                    "win32": "%APPDATA%/SynthEyes",
                    "linux": "~/.SynthEyes"}[sys.platform]
        return os.path.expandvars(os.path.expanduser(user_path))
    

    def _config_path(self):
        return os.path.join(self._user_path(), 'sgtk_tk-syntheyes.ini')


    def _save_config(self):
        # Create directory for config file if it does not exist
        config_path = self._config_path()
        config_dir = os.path.dirname(config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        ### Save UI state to config ###
        if not self._config.has_section("UI"): 
            self._config.add_section("UI")
        self._config.set("UI", "pos", "{},{}".format(self.x(), self.y()))
        self._config.set("UI", "size", "{},{}".format(self.width(), self.height()))
        self._config.set("UI", "auto_resize", str(self._auto_resize()))
        self._config.set("UI", "stays_on_top", str(self._stays_on_top()))
        self._config.set("UI", "borderless", str(self._borderless()))
        ###############################

        # Save out the updated config
        with open(config_path, "w") as file_:
            self._config.write(file_)


    def _load_config(self):
        success = True
        try:
            self._config.read(self._config_path())
        except Exception as e:
            self._engine.log_info("Could not read tk-syntheyes config: %s", e)
            success = False
        
        ### Setup UI defaults ###
        self._update_flags = False
        # pos
        pos = self._config.get("UI", "pos", fallback=None)
        try:
            pos = pos.split(",")
            self.move(int(pos[0]), int(pos[1]))
        except:
            pass
        # size
        size = self._config.get("UI", "size", fallback=None)
        try:
            size = size.split(",")
            self.resize(int(size[0]), int(size[1]))
        except:
            pass
        # auto_resize
        self.actionAuto_Resize.setChecked(self._config.getboolean("UI", "auto_resize", fallback=self._auto_resize()))
        # stays_on_top
        self.actionStays_On_Top.setChecked(self._config.getboolean("UI", "stays_on_top", fallback=self._stays_on_top()))
        self._update_stays_on_top()
        # stays_on_top
        self.actionBorderless.setChecked(self._config.getboolean("UI", "borderless", fallback=self._borderless()))
        self._update_borderless()
        self._update_flags = True
        self.show()
        ######################
        
        return success

################################################################################

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.exec_()