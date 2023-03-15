import sys
import traceback
from PyQt5.QtWidgets import (QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QApplication, QStackedWidget, QLabel)
from PyQt5.QtCore import Qt, QT_VERSION, qFatal
from UI.first_page import FirstPage
from UI.second_page import SecondPage


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.resize(1600, 700)
        self.stacked_widget = QStackedWidget()
        self.button_layout = QHBoxLayout()
        self.first_page = None
        self.second_page = None
        self.second_page_button = None
        self.first_page_button = None

        self.add_page_button()
        self.add_pages()
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.stacked_widget)
        main_layout.addLayout(self.button_layout)
        self.setWindowTitle("Multi-page UI")

    def add_pages(self):
        self.first_page = FirstPage()
        self.second_page = SecondPage()
        self.stacked_widget.addWidget(self.first_page)
        self.stacked_widget.addWidget(self.second_page)

    def add_page_button(self):
        self.second_page_button = QPushButton("Second Page")
        self.first_page_button = QPushButton("First Page")
        self.first_page_button.clicked.connect(lambda: self.go_page(0))
        self.second_page_button.clicked.connect(lambda: self.go_page(1))

        self.button_layout.addWidget(self.first_page_button)
        self.button_layout.addWidget(self.second_page_button)

    def go_page(self, index):
        self.stacked_widget.setCurrentIndex(index)


if QT_VERSION >= 0x50501:
    def new_except_hook(type_, value, traceback_):
        traceback.print_exception(type_, value, traceback_)
        qFatal('')


def main_app():
    sys.excepthook = new_except_hook

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

