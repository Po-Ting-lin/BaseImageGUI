from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt


class SecondPage(QWidget):
    def __init__(self, parent=None):
        super(SecondPage, self).__init__(parent)

        layout = QVBoxLayout(self)
        self.label = QLabel("Second Page")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
