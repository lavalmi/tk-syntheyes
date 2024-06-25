# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'base_panelIMcqun.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_BasePanel(object):
    def setupUi(self, BasePanel):
        if not BasePanel.objectName():
            BasePanel.setObjectName(u"BasePanel")
        BasePanel.resize(187, 270)
        sizePolicy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(BasePanel.sizePolicy().hasHeightForWidth())
        BasePanel.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(BasePanel)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setVerticalSpacing(6)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.spc_left = QLabel(BasePanel)
        self.spc_left.setObjectName(u"spc_left")
        sizePolicy.setHeightForWidth(self.spc_left.sizePolicy().hasHeightForWidth())
        self.spc_left.setSizePolicy(sizePolicy)
        self.spc_left.setMaximumSize(QSize(16, 16))

        self.gridLayout.addWidget(self.spc_left, 1, 0, 1, 1)

        self.spc_right = QLabel(BasePanel)
        self.spc_right.setObjectName(u"spc_right")
        sizePolicy.setHeightForWidth(self.spc_right.sizePolicy().hasHeightForWidth())
        self.spc_right.setSizePolicy(sizePolicy)
        self.spc_right.setMaximumSize(QSize(16, 16))

        self.gridLayout.addWidget(self.spc_right, 1, 2, 1, 1)

        self.spc_center = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

        self.gridLayout.addItem(self.spc_center, 1, 1, 1, 1)


        self.retranslateUi(BasePanel)

        QMetaObject.connectSlotsByName(BasePanel)
    # setupUi

    def retranslateUi(self, BasePanel):
        BasePanel.setWindowTitle(QCoreApplication.translate("EmptyPanel", u"Form", None))
        self.spc_left.setText("")
        self.spc_right.setText("")
    # retranslateUi

################################################################################

class SynthEyesPanel(object):
    def make_sub_panel(self):
        self.gridLayout.removeItem(self.spc_center)

        self.btn_back = QPushButton(self)
        self.btn_back.setObjectName(u"btn_back")
        self.btn_back.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.btn_back.sizePolicy().hasHeightForWidth())
        self.btn_back.setSizePolicy(sizePolicy1)
        self.gridLayout.addWidget(self.btn_back, 0, 1, 1, 1)
        self.btn_back.setText(QCoreApplication.translate("BasePanel", u"Back", None))

        self.tlbtn_back = QToolButton(self)
        self.tlbtn_back.setObjectName(u"tlbtn_back")
        self.tlbtn_back.setEnabled(False)
        sizePolicy1.setHeightForWidth(self.tlbtn_back.sizePolicy().hasHeightForWidth())
        self.tlbtn_back.setSizePolicy(sizePolicy1)
        self.tlbtn_back.setMaximumSize(QSize(16, 16))
        self.tlbtn_back.setAutoRaise(True)
        self.tlbtn_back.setArrowType(Qt.LeftArrow)
        self.gridLayout.addWidget(self.tlbtn_back, 0, 0, 1, 1)
        self.tlbtn_back.setText(QCoreApplication.translate("BasePanel", u"...", None))

        self.line = QFrame(self)
        self.line.setObjectName(u"ln_back")
        sizePolicy1.setHeightForWidth(self.line.sizePolicy().hasHeightForWidth())
        self.line.setSizePolicy(sizePolicy1)
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.gridLayout.addWidget(self.line, 1, 0, 1, 3)

        self.gridLayout.addItem(self.spc_center, self.gridLayout.rowCount(), 1, 1, 1)

    def insert_widget(self, widget: QWidget, row=-1, column=1, row_span=1, column_span=1):
        if row < 0:
            row = self.gridLayout.rowCount() - 1
        size_policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(widget.sizePolicy().hasHeightForWidth())
        widget.setSizePolicy(size_policy)
        # Remove spacer, add the new button and then reatach the spacer at the end
        self.gridLayout.removeItem(self.spc_center)
        self.gridLayout.addWidget(widget, row, column, row_span, column_span)
        self.gridLayout.addItem(self.spc_center, row + 1, 1, 1, 1)

class BasePanel(QWidget, Ui_BasePanel, SynthEyesPanel):
    def __init__(self, parent=None):
        super(BasePanel, self).__init__(parent)
        self.setupUi(self)