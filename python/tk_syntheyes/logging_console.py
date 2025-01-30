# Copyright (c) 2015 Sebastian Kral
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the MIT License included in this
# distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the MIT License. All rights not expressly granted therein are
# reserved by Sebastian Kral.

from PySide2 import QtCore, QtWidgets


class LogConsole(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(LogConsole, self).__init__(parent)

        self.setWindowTitle('Shotgun SynthEyes Logs')
        self.layout = QtWidgets.QVBoxLayout(self)
        self.logs = QtWidgets.QPlainTextEdit(self)
        self.layout.addWidget(self.logs)

        # configure the text widget
        self.logs.setLineWrapMode(self.logs.NoWrap)
        self.logs.setReadOnly(True)

        # load up previous size
        self.settings = QtCore.QSettings("Shotgun Software", "tk-syntheyes.log_console")
        self.resize(self.settings.value("size", QtCore.QSize(800, 400)))

    def closeEvent(self, event):
        self.settings.setValue("size", self.size())
        event.accept()

    def append_to_log(self, text):
        self.logs.appendHtml(text)
        cursor = self.logs.textCursor()
        cursor.movePosition(cursor.End)
        cursor.movePosition(cursor.StartOfLine)
        self.logs.setTextCursor(cursor)
        self.logs.ensureCursorVisible()