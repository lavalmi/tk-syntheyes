# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'base_paneliJeFCG.ui'
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
        BasePanel.resize(203, 272)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(BasePanel.sizePolicy().hasHeightForWidth())
        BasePanel.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(BasePanel)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.spc_right = QLabel(BasePanel)
        self.spc_right.setObjectName(u"spc_right")
        sizePolicy1 = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.spc_right.sizePolicy().hasHeightForWidth())
        self.spc_right.setSizePolicy(sizePolicy1)
        self.spc_right.setMaximumSize(QSize(16, 16))

        self.gridLayout.addWidget(self.spc_right, 0, 2, 1, 1)

        self.spc_left = QLabel(BasePanel)
        self.spc_left.setObjectName(u"spc_left")
        sizePolicy1.setHeightForWidth(self.spc_left.sizePolicy().hasHeightForWidth())
        self.spc_left.setSizePolicy(sizePolicy1)
        self.spc_left.setMaximumSize(QSize(16, 16))

        self.gridLayout.addWidget(self.spc_left, 0, 0, 1, 1)

        self.spc_center = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)

        self.gridLayout.addItem(self.spc_center, 0, 1, 1, 1)


        self.retranslateUi(BasePanel)

        QMetaObject.connectSlotsByName(BasePanel)
    # setupUi

    def retranslateUi(self, BasePanel):
        BasePanel.setWindowTitle(QCoreApplication.translate("BasePanel", u"Form", None))
        self.spc_right.setText("")
        self.spc_left.setText("")
    # retranslateUi

################################################################################

class SynthEyesPanel(object):
    def make_sub_panel(self, panel):
        btn = self.insert_menu_button(panel, is_back_button=True)
        self.insert_line()
        return btn

    def insert_widget(self, widget: QWidget, row=-1, column=1, row_span=1, column_span=1):
        if row < 0:
            row = self.gridLayout.rowCount() - 1
        size_policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(widget.sizePolicy().hasHeightForWidth())
        widget.setSizePolicy(size_policy)
        self.gridLayout.addWidget(widget, row, column, row_span, column_span)
        
        # If the new widget was inserted in the last item, reattach the spacers
        #if self.gridLayout.rowCount() - 1 > row:
        self.update_spacers()

    def insert_button(self, icon:QIcon=None, text="", row=-1, callback=None):
        btn = QPushButton(icon, text, self)
        btn.setText(text)
        if callback:
            btn.clicked.connect(callback)
        self.insert_widget(btn, row, 1, 1, 1)
        return btn
    
    def insert_menu_button(self, panel, icon:QIcon=None, row=-1, is_back_button=False):
        if row < 0:
            row = self.gridLayout.rowCount() - 1

        right = self.panel_depth <= panel.panel_depth        
        self.insert_menu_indicator(right, row)
        btn = self.insert_button(icon, "Back" if is_back_button else panel.name, row)
        return btn
    
    def insert_menu_indicator(self, right=True, row=-1):
        tlbtn = QToolButton(self)
        tlbtn.setEnabled(False)
        tlbtn.setMaximumSize(QSize(16, 16))
        tlbtn.setAutoRaise(True)
        tlbtn.setArrowType(Qt.RightArrow if right else Qt.LeftArrow)
        self.insert_widget(tlbtn, row, 2 if right else 0, 1, 1)
        return tlbtn

    def insert_line(self, row=-1):
        line = QFrame(self)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        self.insert_widget(line, row, 0, 1, 3)
        return line
    
    def update_spacers(self):
        self.gridLayout.removeWidget(self.spc_left)
        self.gridLayout.removeItem(self.spc_center)
        self.gridLayout.removeWidget(self.spc_right)        
        row = self.gridLayout.rowCount()
        self.gridLayout.addWidget(self.spc_left, row, 0, 1, 1)
        self.gridLayout.addItem(self.spc_center, row, 1, 1, 1)
        self.gridLayout.addWidget(self.spc_right, row, 2, 1, 1)


class BasePanel(QWidget, Ui_BasePanel, SynthEyesPanel):
    def __init__(self, parent=None):
        super(BasePanel, self).__init__(parent)
        self.setupUi(self)