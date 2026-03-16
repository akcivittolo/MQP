from PyQt6.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QPushButton,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame
)

from PyQt6.QtCore import Qt

from connection_subpanel import ConnectionSubpanel
from arming_subpanel import ArmingSubpanel

class ControlPanel(QWidget):
    def __init__(self, the_boat, telem_data):
        super().__init__()

        self.the_boat = the_boat
        self.telem_data = telem_data

        self.arming_subpanel = ArmingSubpanel(self.the_boat)
        self.connection_subpanel = ConnectionSubpanel(self.the_boat)

        # Create main layout
        main_layout = QVBoxLayout(self)

        # Create a title widget
        self.title = QLabel("Control")
        self.title.setObjectName("title")

        # Create a frame widget
        content_frame = QFrame()
        content_frame.setObjectName("panel")

        # Create a layout within the frame
        content_layout = QVBoxLayout(content_frame)

        # Add content to layout
        content_layout.addWidget(self.arming_subpanel)
        content_layout.addWidget(self.connection_subpanel)
        
        # Add the title and frame widgets to main widget
        main_layout.addWidget(self.title)
        main_layout.addWidget(content_frame)
        
        
