# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'shot_widgetsmRBuB.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_ShotPanel(object):
    def setupUi(self, ShotPanel):
        if not ShotPanel.objectName():
            ShotPanel.setObjectName(u"ShotPanel")
        ShotPanel.resize(187, 270)
        sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ShotPanel.sizePolicy().hasHeightForWidth())
        ShotPanel.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(ShotPanel)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setVerticalSpacing(6)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.btn_work_area_info = QPushButton(ShotPanel)
        self.btn_work_area_info.setObjectName(u"btn_work_area_info")
        sizePolicy1 = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.btn_work_area_info.sizePolicy().hasHeightForWidth())
        self.btn_work_area_info.setSizePolicy(sizePolicy1)
        self.btn_work_area_info.setFlat(False)

        self.gridLayout.addWidget(self.btn_work_area_info, 9, 1, 1, 1)

        self.btn_back = QPushButton(ShotPanel)
        self.btn_back.setObjectName(u"btn_back")
        self.btn_back.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.btn_back.sizePolicy().hasHeightForWidth())
        self.btn_back.setSizePolicy(sizePolicy1)
        self.btn_back.setAutoFillBackground(False)
        self.btn_back.setStyleSheet(u"")
        self.btn_back.setCheckable(False)
        self.btn_back.setFlat(False)

        self.gridLayout.addWidget(self.btn_back, 0, 1, 1, 1)

        self.spc_center = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

        self.gridLayout.addItem(self.spc_center, 10, 1, 1, 1)

        self.btn_jump_to_shotgrid = QPushButton(ShotPanel)
        self.btn_jump_to_shotgrid.setObjectName(u"btn_jump_to_shotgrid")
        sizePolicy1.setHeightForWidth(self.btn_jump_to_shotgrid.sizePolicy().hasHeightForWidth())
        self.btn_jump_to_shotgrid.setSizePolicy(sizePolicy1)
        self.btn_jump_to_shotgrid.setLayoutDirection(Qt.LeftToRight)
        self.btn_jump_to_shotgrid.setStyleSheet(u"")
        self.btn_jump_to_shotgrid.setAutoRepeatInterval(98)
        self.btn_jump_to_shotgrid.setFlat(False)

        self.gridLayout.addWidget(self.btn_jump_to_shotgrid, 2, 1, 1, 1)

        self.btn_connect_debugger = QPushButton(ShotPanel)
        self.btn_connect_debugger.setObjectName(u"btn_connect_debugger")
        sizePolicy1.setHeightForWidth(self.btn_connect_debugger.sizePolicy().hasHeightForWidth())
        self.btn_connect_debugger.setSizePolicy(sizePolicy1)
        self.btn_connect_debugger.setFlat(False)

        self.gridLayout.addWidget(self.btn_connect_debugger, 5, 1, 1, 1)

        self.btn_jump_to_file_system = QPushButton(ShotPanel)
        self.btn_jump_to_file_system.setObjectName(u"btn_jump_to_file_system")
        sizePolicy1.setHeightForWidth(self.btn_jump_to_file_system.sizePolicy().hasHeightForWidth())
        self.btn_jump_to_file_system.setSizePolicy(sizePolicy1)
        self.btn_jump_to_file_system.setStyleSheet(u"")
        self.btn_jump_to_file_system.setFlat(False)

        self.gridLayout.addWidget(self.btn_jump_to_file_system, 3, 1, 1, 1)

        self.btn_show_console = QPushButton(ShotPanel)
        self.btn_show_console.setObjectName(u"btn_show_console")
        sizePolicy1.setHeightForWidth(self.btn_show_console.sizePolicy().hasHeightForWidth())
        self.btn_show_console.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.btn_show_console, 8, 1, 1, 1)

        self.spc_left = QLabel(ShotPanel)
        self.spc_left.setObjectName(u"spc_left")
        sizePolicy.setHeightForWidth(self.spc_left.sizePolicy().hasHeightForWidth())
        self.spc_left.setSizePolicy(sizePolicy)
        self.spc_left.setMaximumSize(QSize(16, 16))

        self.gridLayout.addWidget(self.spc_left, 10, 0, 1, 1)

        self.toolButton_2 = QToolButton(ShotPanel)
        self.toolButton_2.setObjectName(u"toolButton_2")
        self.toolButton_2.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.toolButton_2.sizePolicy().hasHeightForWidth())
        self.toolButton_2.setSizePolicy(sizePolicy1)
        self.toolButton_2.setMaximumSize(QSize(16, 16))
        self.toolButton_2.setAutoRaise(True)
        self.toolButton_2.setArrowType(Qt.LeftArrow)

        self.gridLayout.addWidget(self.toolButton_2, 0, 0, 1, 1)

        self.spc_right = QLabel(ShotPanel)
        self.spc_right.setObjectName(u"spc_right")
        sizePolicy.setHeightForWidth(self.spc_right.sizePolicy().hasHeightForWidth())
        self.spc_right.setSizePolicy(sizePolicy)
        self.spc_right.setMaximumSize(QSize(16, 16))

        self.gridLayout.addWidget(self.spc_right, 10, 2, 1, 1)

        self.btn_open_log_folder = QPushButton(ShotPanel)
        self.btn_open_log_folder.setObjectName(u"btn_open_log_folder")
        sizePolicy1.setHeightForWidth(self.btn_open_log_folder.sizePolicy().hasHeightForWidth())
        self.btn_open_log_folder.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.btn_open_log_folder, 7, 1, 1, 1)

        self.line = QFrame(ShotPanel)
        self.line.setObjectName(u"line")
        sizePolicy1.setHeightForWidth(self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy1)
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line, 4, 0, 1, 3)

        self.line_2 = QFrame(ShotPanel)
        self.line_2.setObjectName(u"line_2")
        sizePolicy1.setHeightForWidth(self.line_2.sizePolicy().hasHeightForWidth())
        self.line_2.setSizePolicy(sizePolicy1)
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line_2, 1, 0, 1, 3)


        self.retranslateUi(ShotPanel)

        self.btn_work_area_info.setDefault(False)
        self.btn_back.setDefault(False)
        self.btn_jump_to_shotgrid.setDefault(False)
        self.btn_connect_debugger.setDefault(False)
        self.btn_jump_to_file_system.setDefault(False)


        QMetaObject.connectSlotsByName(ShotPanel)
    # setupUi

    def retranslateUi(self, ShotPanel):
        ShotPanel.setWindowTitle(QCoreApplication.translate("ShotPanel", u"Form", None))
        self.btn_work_area_info.setText(QCoreApplication.translate("ShotPanel", u"Work Area Info...", None))
        self.btn_back.setText(QCoreApplication.translate("ShotPanel", u"Back", None))
        self.btn_jump_to_shotgrid.setText(QCoreApplication.translate("ShotPanel", u"Jump to ShotGrid", None))
        self.btn_connect_debugger.setText(QCoreApplication.translate("ShotPanel", u"Connect remote debugger (localhost)...", None))
        self.btn_jump_to_file_system.setText(QCoreApplication.translate("ShotPanel", u"Jump to File System", None))
        self.btn_show_console.setText(QCoreApplication.translate("ShotPanel", u"Show Console", None))
        self.spc_left.setText("")
        self.toolButton_2.setText(QCoreApplication.translate("ShotPanel", u"...", None))
        self.spc_right.setText("")
        self.btn_open_log_folder.setText(QCoreApplication.translate("ShotPanel", u"Open Log Folder", None))
    # retranslateUi

################################################################################

class ShotPanel(QWidget, Ui_ShotPanel):
    def __init__(self, parent):
        super(ShotPanel, self).__init__(parent)
        self.setupUi(self)