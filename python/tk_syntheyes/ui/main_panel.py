# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_panelIKXneX.ui'
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
        self.spc_center = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

        self.gridLayout.addItem(self.spc_center, 2, 1, 1, 1)

        self.btn_context = QPushButton(MainPanel)
        self.btn_context.setObjectName(u"btn_context")
        self.btn_context.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.btn_context.sizePolicy().hasHeightForWidth())
        self.btn_context.setSizePolicy(sizePolicy1)
        self.btn_context.setAutoFillBackground(False)
        self.btn_context.setStyleSheet(u"")
        self.btn_context.setCheckable(False)
        self.btn_context.setFlat(False)

        self.gridLayout.addWidget(self.btn_context, 0, 1, 1, 1)

        self.spc_right = QLabel(MainPanel)
        self.spc_right.setObjectName(u"spc_right")
        sizePolicy.setHeightForWidth(self.spc_right.sizePolicy().hasHeightForWidth())
        self.spc_right.setSizePolicy(sizePolicy)
        self.spc_right.setMaximumSize(QSize(16, 16))

        self.gridLayout.addWidget(self.spc_right, 2, 2, 1, 1)

        self.line_2 = QFrame(MainPanel)
        self.line_2.setObjectName(u"line_2")
        sizePolicy1.setHeightForWidth(self.line_2.sizePolicy().hasHeightForWidth())
        self.line_2.setSizePolicy(sizePolicy1)
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line_2, 1, 0, 1, 3)

        self.tlbtn_context = QToolButton(MainPanel)
        self.tlbtn_context.setObjectName(u"tlbtn_context")
        self.tlbtn_context.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.tlbtn_context.sizePolicy().hasHeightForWidth())
        self.tlbtn_context.setSizePolicy(sizePolicy1)
        self.tlbtn_context.setMaximumSize(QSize(16, 16))
        self.tlbtn_context.setAutoRaise(True)
        self.tlbtn_context.setArrowType(Qt.RightArrow)

        self.gridLayout.addWidget(self.tlbtn_context, 0, 2, 1, 1)

        self.spc_left = QLabel(MainPanel)
        self.spc_left.setObjectName(u"spc_left")
        sizePolicy.setHeightForWidth(self.spc_left.sizePolicy().hasHeightForWidth())
        self.spc_left.setSizePolicy(sizePolicy)
        self.spc_left.setMaximumSize(QSize(16, 16))

        self.gridLayout.addWidget(self.spc_left, 2, 0, 1, 1)


        self.retranslateUi(MainPanel)

        self.btn_context.setDefault(False)


        QMetaObject.connectSlotsByName(MainPanel)
    # setupUi

    def retranslateUi(self, MainPanel):
        MainPanel.setWindowTitle(QCoreApplication.translate("MainPanel", u"Form", None))
        self.btn_context.setText(QCoreApplication.translate("MainPanel", u"comp, Shot", None))
        self.spc_right.setText("")
        self.tlbtn_context.setText(QCoreApplication.translate("MainPanel", u"...", None))
        self.spc_left.setText("")
    # retranslateUi

################################################################################

from .base_panel import SynthEyesPanel

class MainPanel(QWidget, Ui_MainPanel, SynthEyesPanel):
    def __init__(self, parent=None):
        super(MainPanel, self).__init__(parent)
        self.setupUi(self)