# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'base_panelWGmuGw.ui'
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

