# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainrOKrvr.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(227, 417)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QSize(0, 90))
        MainWindow.setWindowTitle(u"SynthEyes ShotGrid")
        MainWindow.setLocale(QLocale(QLocale.English, QLocale.Germany))
        self.actionExit_SynthEyes = QAction(MainWindow)
        self.actionExit_SynthEyes.setObjectName(u"actionExit_SynthEyes")
        self.actionAlways_On_Top = QAction(MainWindow)
        self.actionAlways_On_Top.setObjectName(u"actionAlways_On_Top")
        self.actionAlways_On_Top.setCheckable(True)
        self.actionAlways_On_Top.setChecked(True)
        self.actionOpen_Console = QAction(MainWindow)
        self.actionOpen_Console.setObjectName(u"actionOpen_Console")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.vertical_layout = QVBoxLayout(self.centralwidget)
        self.vertical_layout.setSpacing(0)
        self.vertical_layout.setObjectName(u"vertical_layout")
        self.vertical_layout.setContentsMargins(0, 0, 0, 0)
        self.btn_quick_select = QPushButton(self.centralwidget)
        self.btn_quick_select.setObjectName(u"btn_quick_select")
        sizePolicy1 = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.btn_quick_select.sizePolicy().hasHeightForWidth())
        self.btn_quick_select.setSizePolicy(sizePolicy1)
        self.btn_quick_select.setCheckable(True)

        self.vertical_layout.addWidget(self.btn_quick_select)

        self.panel_split_layout = QVSplitLayout()
        self.panel_split_layout.setSpacing(0)
        self.panel_split_layout.setObjectName(u"panel_split_layout")
        self.sca_quick_select = QScrollArea(self.centralwidget)
        self.sca_quick_select.setObjectName(u"sca_quick_select")
        sizePolicy2 = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.sca_quick_select.sizePolicy().hasHeightForWidth())
        self.sca_quick_select.setSizePolicy(sizePolicy2)
        self.sca_quick_select.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.sca_quick_select.setWidgetResizable(True)
        self.sca_quick_select_contents = QWidget()
        self.sca_quick_select_contents.setObjectName(u"sca_quick_select_contents")
        self.sca_quick_select_contents.setGeometry(QRect(0, 0, 206, 16))
        sizePolicy.setHeightForWidth(self.sca_quick_select_contents.sizePolicy().hasHeightForWidth())
        self.sca_quick_select_contents.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(self.sca_quick_select_contents)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.verticalSpacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.sca_quick_select.setWidget(self.sca_quick_select_contents)

        self.panel_split_layout.addWidget(self.sca_quick_select)

        self.split_layout = QHSplitLayout()
        self.split_layout.setSpacing(0)
        self.split_layout.setObjectName(u"split_layout")
        self.split_layout.setContentsMargins(9, 9, 9, 0)
        self.sca_left = QScrollArea(self.centralwidget)
        self.sca_left.setObjectName(u"sca_left")
        sizePolicy2.setHeightForWidth(self.sca_left.sizePolicy().hasHeightForWidth())
        self.sca_left.setSizePolicy(sizePolicy2)
        self.sca_left.setFrameShape(QFrame.NoFrame)
        self.sca_left.setWidgetResizable(True)
        self.pnl_left = QWidget()
        self.pnl_left.setObjectName(u"pnl_left")
        self.layout_left = QVBoxLayout(self.pnl_left)
        self.layout_left.setSpacing(0)
        self.layout_left.setObjectName(u"layout_left")
        self.layout_left.setContentsMargins(0, 0, 0, 0)
        self.sca_left.setWidget(self.pnl_left)

        self.split_layout.addWidget(self.sca_left)

        self.sca_right = QScrollArea(self.centralwidget)
        self.sca_right.setObjectName(u"sca_right")
        sizePolicy2.setHeightForWidth(self.sca_right.sizePolicy().hasHeightForWidth())
        self.sca_right.setSizePolicy(sizePolicy2)
        self.sca_right.setFrameShape(QFrame.NoFrame)
        self.sca_right.setWidgetResizable(True)
        self.pnl_right = QWidget()
        self.pnl_right.setObjectName(u"pnl_right")
        self.layout_right = QVBoxLayout(self.pnl_right)
        self.layout_right.setSpacing(0)
        self.layout_right.setObjectName(u"layout_right")
        self.layout_right.setContentsMargins(0, 0, 0, 0)
        self.sca_right.setWidget(self.pnl_right)

        self.split_layout.addWidget(self.sca_right)

        self.split_layout.setStretch(0, 1000)

        self.panel_split_layout.addLayout(self.split_layout)

        self.panel_split_layout.setStretch(1, 1000)

        self.vertical_layout.addLayout(self.panel_split_layout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 227, 21))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        self.statusBar.setSizeGripEnabled(False)
        MainWindow.setStatusBar(self.statusBar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menuFile.addAction(self.actionOpen_Console)
        self.menuFile.addAction(self.actionExit_SynthEyes)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        self.actionExit_SynthEyes.setText(QCoreApplication.translate("MainWindow", u"Exit SynthEyes", None))
        self.actionAlways_On_Top.setText(QCoreApplication.translate("MainWindow", u"Always On Top", None))
        self.actionOpen_Console.setText(QCoreApplication.translate("MainWindow", u"Open Console", None))
        self.btn_quick_select.setText("")
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        pass
    # retranslateUi

################################################################################

class SplitProperty(object):
    @property
    def stretch_steps(self):
        return self.stretch(0) + self.stretch(1)

    def get_split_factor(self):
        stretch_steps = self.stretch_steps
        if stretch_steps:
            return self.stretch(0) / stretch_steps
        return 0.5

    def set_split_factor(self, factor: float):
        """Set the stretch factors to resemble the given factor in range [0,1]"""
        stretch_steps = self.stretch_steps
        self.setStretch(0, round(factor * stretch_steps))
        self.setStretch(1, round((1 - factor) * stretch_steps))
    
    split_factor = Property(float, get_split_factor, set_split_factor)

class QHSplitLayout(QHBoxLayout, SplitProperty):
    def __init__(self, parent=None):
        super(QHSplitLayout, self).__init__(parent)    

class QVSplitLayout(QVBoxLayout, SplitProperty):
    def __init__(self, parent=None):
        super(QVSplitLayout, self).__init__(parent)

################################################################################
import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

sys.path.append(os.path.join(os.path.dirname(__file__)))
from app_command import AppCommand
from base_panel import BasePanel, SynthEyesPanel
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

        # Setup animations
        self._anim_panel_transition = QPropertyAnimation(self.split_layout, b"split_factor", self)
        self._anim_panel_transition.finished.connect(self._switch_panel_finished)
        self._anim_panel_quick_select_transition = QPropertyAnimation(self.panel_split_layout, b"split_factor", self)
        self._anim_panel_quick_select_transition.setEasingCurve(QEasingCurve.OutExpo)
        self._anim_panel_quick_select_transition.finished.connect(self._switch_quick_select_finished)

        # Setup menu actions
        self.actionExit_SynthEyes.triggered.connect(self.exit)
        self.actionOpen_Console.triggered.connect(self.open_logging_console)

    
    def _init_panel(self, panel_type: type, name: str, parent_panel: QWidget, visible=False, enabled=False, add_to_quick_select=True):
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
            if panel_type is SynthEyesPanel or issubclass(panel_type, SynthEyesPanel):
                self._link_panel(panel.make_sub_panel(parent_panel), parent_panel)

        return panel


    def _init_commands(self):
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
        # Connect panels via button actions
        button.clicked.connect(lambda: self._switch_panel(panel_to))

    
    def closeEvent(self, event):
        if self._minimize_on_close:
            self.setWindowState(Qt.WindowMinimized)
            event.ignore()
        else:
            self.settings.setValue("pos", self.pos())
            event.accept()

    
    def _switch_panel(self, target_panel: QWidget, easing_curve_type:QEasingCurve.Type=QEasingCurve.OutBounce, amplitude:float=0.25):
        self._anim_panel_transition.stop()
        
        # Disable panel during animation
        self.setEnabled(False)

        if self.btn_quick_select.isChecked():
            self.btn_quick_select.setChecked(False)
            self._switch_quick_select()

        # Identify direction of the animation based on current and targeted panel depth
        left_to_right = getattr(target_panel, "panel_depth", 0) >= self._active_panel_depth

        # Change panel name 
        self.btn_quick_select.setText(target_panel.name)

        self._active_panel_depth += 1 if left_to_right else -1
        if self._left_panel_active and not left_to_right:
            self.pnl_right.layout().addWidget(self.pnl_left.takeAt(0).widget())
            self.split_layout.split_factor = 0
        elif not self._left_panel_active and left_to_right:
            self.pnl_left.layout().addWidget(self.pnl_right.takeAt(0).widget())
            self.split_layout.split_factor = 1

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
        
        split: QHSplitLayout = self.split_layout
        split_factor = split.split_factor
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
        self._anim_panel_quick_select_transition.stop()
        self.sca_quick_select.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        quick_select = self.btn_quick_select.isChecked()

        # If panel is not fully opened/closed shrink duration respectively
        split_factor = self.panel_split_layout.split_factor
        duration = 300 * (1 - split_factor if split_factor < quick_select else split_factor)

        self._anim_panel_quick_select_transition.setEndValue(quick_select)
        self._anim_panel_quick_select_transition.setDuration(duration)
        self._anim_panel_quick_select_transition.start()

  
    def _switch_quick_select_finished(self):
        self.sca_quick_select.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

  
    def open_logging_console(self):
        app = QCoreApplication.instance()
        win = app.property('tk-syntheyes.log_console')
        win.setHidden(False)
        win.activateWindow()
        win.raise_()


    def exit(self):
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