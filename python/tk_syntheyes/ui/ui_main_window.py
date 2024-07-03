# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'maineqYTLS.ui'
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
        self.actionOpen_Console = QAction(MainWindow)
        self.actionOpen_Console.setObjectName(u"actionOpen_Console")
        self.actionAuto_Resize = QAction(MainWindow)
        self.actionAuto_Resize.setObjectName(u"actionAuto_Resize")
        self.actionAuto_Resize.setCheckable(True)
        self.actionAuto_Resize.setChecked(True)
        self.actionStays_On_Top = QAction(MainWindow)
        self.actionStays_On_Top.setObjectName(u"actionStays_On_Top")
        self.actionStays_On_Top.setCheckable(True)
        self.actionStays_On_Top.setChecked(True)
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

        self.main_split_layout = QVBoxLayout()
        self.main_split_layout.setSpacing(0)
        self.main_split_layout.setObjectName(u"main_split_layout")
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

        self.main_split_layout.addWidget(self.sca_quick_select)

        self.panel_split_layout = QHBoxLayout()
        self.panel_split_layout.setSpacing(0)
        self.panel_split_layout.setObjectName(u"panel_split_layout")
        self.panel_split_layout.setContentsMargins(9, 9, 9, 0)
        self.sca_left = QScrollArea(self.centralwidget)
        self.sca_left.setObjectName(u"sca_left")
        sizePolicy2.setHeightForWidth(self.sca_left.sizePolicy().hasHeightForWidth())
        self.sca_left.setSizePolicy(sizePolicy2)
        self.sca_left.setFrameShape(QFrame.NoFrame)
        self.sca_left.setWidgetResizable(True)
        self.pnl_left = QWidget()
        self.pnl_left.setObjectName(u"pnl_left")
        self.pnl_left.setGeometry(QRect(0, 0, 207, 341))
        self.layout_left = QVBoxLayout(self.pnl_left)
        self.layout_left.setSpacing(0)
        self.layout_left.setObjectName(u"layout_left")
        self.layout_left.setContentsMargins(0, 0, 0, 0)
        self.sca_left.setWidget(self.pnl_left)

        self.panel_split_layout.addWidget(self.sca_left)

        self.sca_right = QScrollArea(self.centralwidget)
        self.sca_right.setObjectName(u"sca_right")
        sizePolicy2.setHeightForWidth(self.sca_right.sizePolicy().hasHeightForWidth())
        self.sca_right.setSizePolicy(sizePolicy2)
        self.sca_right.setFrameShape(QFrame.NoFrame)
        self.sca_right.setWidgetResizable(True)
        self.pnl_right = QWidget()
        self.pnl_right.setObjectName(u"pnl_right")
        self.pnl_right.setGeometry(QRect(0, 0, 16, 324))
        self.layout_right = QVBoxLayout(self.pnl_right)
        self.layout_right.setSpacing(0)
        self.layout_right.setObjectName(u"layout_right")
        self.layout_right.setContentsMargins(0, 0, 0, 0)
        self.sca_right.setWidget(self.pnl_right)

        self.panel_split_layout.addWidget(self.sca_right)

        self.panel_split_layout.setStretch(0, 1000)

        self.main_split_layout.addLayout(self.panel_split_layout)

        self.main_split_layout.setStretch(1, 1000)

        self.vertical_layout.addLayout(self.main_split_layout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 227, 21))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName(u"menuFile")
        self.menuSettings = QMenu(self.menubar)
        self.menuSettings.setObjectName(u"menuSettings")
        MainWindow.setMenuBar(self.menubar)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        self.statusBar.setSizeGripEnabled(False)
        MainWindow.setStatusBar(self.statusBar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menuFile.addAction(self.actionOpen_Console)
        self.menuFile.addAction(self.actionExit_SynthEyes)
        self.menuSettings.addAction(self.actionAuto_Resize)
        self.menuSettings.addAction(self.actionStays_On_Top)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        self.actionExit_SynthEyes.setText(QCoreApplication.translate("MainWindow", u"Exit SynthEyes", None))
        self.actionOpen_Console.setText(QCoreApplication.translate("MainWindow", u"Open Console", None))
        self.actionAuto_Resize.setText(QCoreApplication.translate("MainWindow", u"Auto Resize", None))
        self.actionStays_On_Top.setText(QCoreApplication.translate("MainWindow", u"Stays On Top", None))
        self.btn_quick_select.setText("")
        self.menuFile.setTitle(QCoreApplication.translate("MainWindow", u"File", None))
        self.menuSettings.setTitle(QCoreApplication.translate("MainWindow", u"Settings", None))
        pass
    # retranslateUi

