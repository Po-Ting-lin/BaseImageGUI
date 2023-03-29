import cv2
import numpy as np
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout, QFileDialog
from PyQt5.QtCore import Qt
from UI.zoom_display import ZoomDisplay


class FirstPage(QWidget):
    def __init__(self, parent=None):
        super(FirstPage, self).__init__(parent)
        self.img = None
        self.q_img = None
        self.display = ZoomDisplay(1000, 800,
                                   mouseLDownCallback=self.update_left_down_coordinate,
                                   mouseLUpCallback=self.update_left_up_coordinate,
                                   mouseMoveCallback=self.update_left_track_coordinate,
                                   tileInfoCallback=self.update_tile_info)
        self.display.set_constant_mouse_move_tracking(True)
        self.set_blank_image(1000, 800)

        layout = QGridLayout(self)
        self.label = QLabel("First Page")
        layout.addWidget(self.label, 0, 0, 1, 1)
        layout.addWidget(self.display, 1, 0, 20, 4)

        self.open_image_button = QPushButton('Open Image', self)
        self.open_image_button.clicked.connect(self.open_image)
        layout.addWidget(self.open_image_button, 1, 4, 1, 1)

        self.coordinate_label = QLabel("Mouse Tracking coordinate: (0, 0)", self)
        layout.addWidget(self.coordinate_label, 2, 4, 1, 1)

        self.down_coordinate_label = QLabel("Mouse Down coordinate: (0, 0)", self)
        layout.addWidget(self.down_coordinate_label, 3, 4, 1, 1)

        self.up_coordinate_label = QLabel("Mouse Up coordinate: (0, 0)", self)
        layout.addWidget(self.up_coordinate_label, 4, 4, 1, 1)

        self.tile_label = QLabel("Box info sx, sy, w, h: (0, 0, 0, 0)", self)
        layout.addWidget(self.tile_label, 5, 4, 1, 1)

    def open_image(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open Image', 'Image', '*.png *.jpg *.bmp')
        if filename is '':
            return
        self.img = cv2.imread(filename, -1)
        self.display.display(self.img)
        self.display.set_enable_zoom(True)

    def set_blank_image(self, width, height):
        channel = 3
        self.img = np.zeros((height, width, channel), dtype=np.uint8)
        self.display.display(self.img)
        self.display.set_enable_zoom(False)

    def add_display(self):
        pass

    def update_left_track_coordinate(self, x, y):
        self.coordinate_label.setText("Mouse Tracking coordinate: ({}, {})".format(x, y))

    def update_left_down_coordinate(self, x, y):
        self.down_coordinate_label.setText("Mouse Down coordinate: ({}, {})".format(x, y))

    def update_left_up_coordinate(self, x, y):
        self.up_coordinate_label.setText("Mouse Up coordinate: ({}, {})".format(x, y))

    def update_tile_info(self, sx, sy, w, h):
        self.tile_label.setText("Box info sx, sy, w, h: ({}, {}, {}, {})".format(sx, sy, w, h))

    def update_zoom(self, x, y, scale):
        pass
