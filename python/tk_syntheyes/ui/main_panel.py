# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_paneluZoTlK.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainPanel(object):
    def setupUi(self, MainPanel):
        if not MainPanel.objectName():
            MainPanel.setObjectName(u"MainPanel")
        MainPanel.resize(238, 320)
        sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainPanel.sizePolicy().hasHeightForWidth())
        MainPanel.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(MainPanel)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setVerticalSpacing(6)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.toolButton = QToolButton(MainPanel)
        self.toolButton.setObjectName(u"toolButton")
        self.toolButton.setEnabled(False)
        sizePolicy1 = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.toolButton.sizePolicy().hasHeightForWidth())
        self.toolButton.setSizePolicy(sizePolicy1)
        self.toolButton.setMaximumSize(QSize(16, 16))
        self.toolButton.setAutoRaise(True)
        self.toolButton.setArrowType(Qt.RightArrow)

        self.gridLayout.addWidget(self.toolButton, 0, 2, 1, 1)

        self.btn_file_publish = QPushButton(MainPanel)
        self.btn_file_publish.setObjectName(u"btn_file_publish")
        sizePolicy1.setHeightForWidth(self.btn_file_publish.sizePolicy().hasHeightForWidth())
        self.btn_file_publish.setSizePolicy(sizePolicy1)
        self.btn_file_publish.setFlat(False)

        self.gridLayout.addWidget(self.btn_file_publish, 4, 1, 1, 1)

        self.spc_center = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

        self.gridLayout.addItem(self.spc_center, 9, 1, 1, 1)

        self.btn_file_open = QPushButton(MainPanel)
        self.btn_file_open.setObjectName(u"btn_file_open")
        sizePolicy1.setHeightForWidth(self.btn_file_open.sizePolicy().hasHeightForWidth())
        self.btn_file_open.setSizePolicy(sizePolicy1)
        self.btn_file_open.setLayoutDirection(Qt.LeftToRight)
        self.btn_file_open.setStyleSheet(u"")
        self.btn_file_open.setAutoRepeatInterval(98)
        self.btn_file_open.setFlat(False)

        self.gridLayout.addWidget(self.btn_file_open, 2, 1, 1, 1)

        self.toolButton_2 = QToolButton(MainPanel)
        self.toolButton_2.setObjectName(u"toolButton_2")
        self.toolButton_2.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.toolButton_2.sizePolicy().hasHeightForWidth())
        self.toolButton_2.setSizePolicy(sizePolicy1)
        self.toolButton_2.setMaximumSize(QSize(16, 16))
        self.toolButton_2.setAutoRaise(True)
        self.toolButton_2.setArrowType(Qt.RightArrow)

        self.gridLayout.addWidget(self.toolButton_2, 7, 2, 1, 1)

        self.btn_scene_breakdown = QPushButton(MainPanel)
        self.btn_scene_breakdown.setObjectName(u"btn_scene_breakdown")
        sizePolicy1.setHeightForWidth(self.btn_scene_breakdown.sizePolicy().hasHeightForWidth())
        self.btn_scene_breakdown.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.btn_scene_breakdown, 8, 1, 1, 1)

        self.btn_file_save = QPushButton(MainPanel)
        self.btn_file_save.setObjectName(u"btn_file_save")
        sizePolicy1.setHeightForWidth(self.btn_file_save.sizePolicy().hasHeightForWidth())
        self.btn_file_save.setSizePolicy(sizePolicy1)
        self.btn_file_save.setStyleSheet(u"")
        self.btn_file_save.setFlat(False)

        self.gridLayout.addWidget(self.btn_file_save, 3, 1, 1, 1)

        self.btn_to_shot = QPushButton(MainPanel)
        self.btn_to_shot.setObjectName(u"btn_to_shot")
        self.btn_to_shot.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.btn_to_shot.sizePolicy().hasHeightForWidth())
        self.btn_to_shot.setSizePolicy(sizePolicy1)
        self.btn_to_shot.setAutoFillBackground(False)
        self.btn_to_shot.setStyleSheet(u"")
        self.btn_to_shot.setCheckable(False)
        self.btn_to_shot.setFlat(False)

        self.gridLayout.addWidget(self.btn_to_shot, 0, 1, 1, 1)

        self.btn_load = QPushButton(MainPanel)
        self.btn_load.setObjectName(u"btn_load")
        sizePolicy1.setHeightForWidth(self.btn_load.sizePolicy().hasHeightForWidth())
        self.btn_load.setSizePolicy(sizePolicy1)
        self.btn_load.setFlat(False)

        self.gridLayout.addWidget(self.btn_load, 5, 1, 1, 1)

        self.btn_to_sanity_checks = QPushButton(MainPanel)
        self.btn_to_sanity_checks.setObjectName(u"btn_to_sanity_checks")
        sizePolicy1.setHeightForWidth(self.btn_to_sanity_checks.sizePolicy().hasHeightForWidth())
        self.btn_to_sanity_checks.setSizePolicy(sizePolicy1)

        self.gridLayout.addWidget(self.btn_to_sanity_checks, 7, 1, 1, 1)

        self.spc_left = QLabel(MainPanel)
        self.spc_left.setObjectName(u"spc_left")
        sizePolicy.setHeightForWidth(self.spc_left.sizePolicy().hasHeightForWidth())
        self.spc_left.setSizePolicy(sizePolicy)
        self.spc_left.setMaximumSize(QSize(16, 16))

        self.gridLayout.addWidget(self.spc_left, 9, 0, 1, 1)

        self.spc_right = QLabel(MainPanel)
        self.spc_right.setObjectName(u"spc_right")
        sizePolicy.setHeightForWidth(self.spc_right.sizePolicy().hasHeightForWidth())
        self.spc_right.setSizePolicy(sizePolicy)
        self.spc_right.setMaximumSize(QSize(16, 16))

        self.gridLayout.addWidget(self.spc_right, 9, 2, 1, 1)

        self.line_2 = QFrame(MainPanel)
        self.line_2.setObjectName(u"line_2")
        sizePolicy1.setHeightForWidth(self.line_2.sizePolicy().hasHeightForWidth())
        self.line_2.setSizePolicy(sizePolicy1)
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line_2, 1, 0, 1, 3)

        self.line = QFrame(MainPanel)
        self.line.setObjectName(u"line")
        sizePolicy1.setHeightForWidth(self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy1)
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line, 6, 0, 1, 3)


        self.retranslateUi(MainPanel)

        self.btn_file_publish.setDefault(False)
        self.btn_file_open.setDefault(False)
        self.btn_file_save.setDefault(False)
        self.btn_to_shot.setDefault(False)
        self.btn_load.setDefault(False)


        QMetaObject.connectSlotsByName(MainPanel)
    # setupUi

    def retranslateUi(self, MainPanel):
        MainPanel.setWindowTitle(QCoreApplication.translate("MainPanel", u"Form", None))
        self.toolButton.setText(QCoreApplication.translate("MainPanel", u"...", None))
        self.btn_file_publish.setText(QCoreApplication.translate("MainPanel", u"Publish...", None))
        self.btn_file_open.setText(QCoreApplication.translate("MainPanel", u"File Open...", None))
        self.toolButton_2.setText(QCoreApplication.translate("MainPanel", u"...", None))
        self.btn_scene_breakdown.setText(QCoreApplication.translate("MainPanel", u"Scene Breakdown...", None))
        self.btn_file_save.setText(QCoreApplication.translate("MainPanel", u"File Save...", None))
        self.btn_to_shot.setText(QCoreApplication.translate("MainPanel", u"comp, Shot", None))
        self.btn_load.setText(QCoreApplication.translate("MainPanel", u"Load...", None))
        self.btn_to_sanity_checks.setText(QCoreApplication.translate("MainPanel", u"Sanity Checks", None))
        self.spc_left.setText("")
        self.spc_right.setText("")
    # retranslateUi

################################################################################

class MainPanel(QWidget, Ui_MainPanel):
    def __init__(self, parent=None):
        super(MainPanel, self).__init__(parent)
        self.setupUi(self)