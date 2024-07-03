from ui_base_panel import Ui_BasePanel

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

class BasePanel(QWidget, Ui_BasePanel):
    def __init__(self, parent=None):
        super(BasePanel, self).__init__(parent)
        self.setupUi(self)

        self.menu_indicator_size = 16
        self.max_button_width = 0
        self.update_preferred_width()

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

        width = btn.sizeHint().width()
        if width > self.max_button_width:
            self.max_button_width = width
            self.update_preferred_width()
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
        tlbtn.setMaximumSize(QSize(self.menu_indicator_size, self.menu_indicator_size))
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

    def update_preferred_width(self):
        self.preferred_width = 2 * (self.menu_indicator_size + self.gridLayout.horizontalSpacing()) + self.max_button_width
