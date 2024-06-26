# Copyright (c) 2015 Sebastian Kral
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the MIT License included in this
# distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the MIT License. All rights not expressly granted therein are
# reserved by Sebastian Kral.

# log console
import logging

from .util import callback_event

from sgtk.platform.qt import QtGui
from sgtk.platform.qt import QtCore

COLOR_MAP = {
    'CRITICAL': 'indianred',
    '   ERROR': 'indianred',
    ' WARNING': 'khaki',
    '    INFO': 'lightgray',
}


def append_to_log(widget, text):
    widget.appendHtml(text)
    cursor = widget.textCursor()
    cursor.movePosition(cursor.End)
    cursor.movePosition(cursor.StartOfLine)
    widget.setTextCursor(cursor)
    widget.ensureCursorVisible()
append_to_log._tkLog = False


class QtLogHandler(logging.Handler):
    def __init__(self, widget):
        logging.Handler.__init__(self)
        self.widget = widget
        pattern = "%(asctime)s [%(levelname) 8s] %(message)s"
        self.formatter = logging.Formatter(pattern)

    def emit(self, record):
        message = self.formatter.format(record)
        for (k, v) in COLOR_MAP.items():
            if ('[%s]' % k) in message:
                message = '<font color="%s">%s</font>' % (v, message)
                break
        callback_event.send_to_main_thread(append_to_log, self.widget,
                                           "<pre>%s</pre>" % message)


class LogConsole(QtGui.QWidget):
    def __init__(self, parent=None):
        super(LogConsole, self).__init__(parent)

        self.setWindowTitle('Shotgun SynthEyes Logs')
        self.layout = QtGui.QVBoxLayout(self)
        self.logs = QtGui.QPlainTextEdit(self)
        self.layout.addWidget(self.logs)

        # configure the text widget
        self.logs.setLineWrapMode(self.logs.NoWrap)
        self.logs.setReadOnly(True)

        # load up previous size
        self.settings = QtCore.QSettings("Shotgun Software",
                                         "tk-syntheyes.log_console")
        self.resize(self.settings.value("size", QtCore.QSize(800, 400)))


    def closeEvent(self, event):
        self.settings.setValue("size", self.size())
        event.accept()
