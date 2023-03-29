import cv2
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel


class ResizeParas(object):
    off_x = 0
    off_y = 0
    nx = 0
    ny = 0
    raw_nx = 0
    raw_ny = 0


class Display(QLabel):
    def __init__(self, width, height, 
                 mouseLDownCallback=None,
                 mouseLUpCallback=None,
                 mouseRDownCallback=None,
                 mouseRUpCallback=None,
                 mouseMoveCallback=None,
                 mouseWheelCallback=None):
        super(Display, self).__init__()
        self.width = width
        self.height = height
        self.q_img = None
        self.img = None
        self.raw = None
        self.resize_paras = ResizeParas()
        self.mouseLDownCallback = None
        self.mouseLUpCallback = None
        self.mouseRDownCallback = None
        self.mouseRUpCallback = None
        self.mouseMoveCallback = None
        self.mouseWheelCallback = None
        self.is_displaying = False

        if mouseLDownCallback is not None:
            self.mouseLDownCallback = mouseLDownCallback
        if mouseLUpCallback is not None:
            self.mouseLUpCallback = mouseLUpCallback
        if mouseRDownCallback is not None:
            self.mouseRDownCallback = mouseRDownCallback
        if mouseRUpCallback is not None:
            self.mouseRUpCallback = mouseRUpCallback
        if mouseMoveCallback is not None:
            self.mouseMoveCallback = mouseMoveCallback
        if mouseWheelCallback is not None:
            self.mouseWheelCallback = mouseWheelCallback

    def display(self, img):
        self.reset()
        self.is_displaying = True
        self.raw = img
        img = self.resize_image(img)
        self.__update_image(img)

    def update_image(self, img):
        self.__update_image(img)

    def set_constant_mouse_move_tracking(self, value):
        if self.mouseMoveCallback is not None:
            self.setMouseTracking(value)

    def reset(self):
        self.is_displaying = False

    def __update_image(self, img):
        if img is None:
            return
        self.img = img
        height, width, channel = self.img.shape
        # print("{}, {}, {}".format(height, width, channel))
        if channel == 3:
            self.q_img = QImage(self.img, width, height, channel * width, QImage.Format_RGB888).rgbSwapped()
        elif channel == 4:
            self.q_img = QImage(self.img, width, height, channel * width, QImage.Format_ARGB32).rgbSwapped()
        self.setPixmap(QPixmap.fromImage(self.q_img))

    def mousePressEvent(self, event):
        x = event.x()
        y = event.y()
        if not self.inside_img(x, y):
            return
        if event.button() == Qt.LeftButton:
            if self.mouseLDownCallback is not None:
                self.mouseLDownCallback(x, y)
        elif event.button() == Qt.RightButton:
            if self.mouseRDownCallback is not None:
                self.mouseRDownCallback(x, y)

    def mouseReleaseEvent(self, event):
        x = event.x()
        y = event.y()
        if not self.inside_img(x, y):
            return
        if event.button() == Qt.LeftButton:
            if self.mouseLUpCallback is not None:
                self.mouseLUpCallback(x, y)
        elif event.button() == Qt.RightButton:
            if self.mouseRUpCallback is not None:
                self.mouseRUpCallback(x, y)

    def mouseMoveEvent(self, event):
        x = event.x()
        y = event.y()
        if not self.inside_img(x, y):
            return
        if self.mouseMoveCallback is not None:
            self.mouseMoveCallback(x, y)

    def wheelEvent(self, event):
        x = event.x()
        y = event.y()
        num_degrees = event.angleDelta() / 8
        num_steps = num_degrees / 15
        scale = 1.0
        if num_steps.y() == -1:
            if scale >= 0.1:
                scale -= 0.05
        else:
            if scale <= 2.0:
                scale += 0.05
        # do stuff

    def resize_image(self, img, record_paras=True):
        nx = img.shape[1]
        ny = img.shape[0]
        ch = img.shape[2]
        new_nx = 0
        new_ny = 0
        off_x = 0
        off_y = 0
        if nx == 0 or ny == 0 or self.width == 0 or self.height == 0:
            return
        if (nx / ny) > (self.width / self.height):
            new_nx = self.width
            new_ny = int(round(self.width * ny / nx))
            off_y = int(round((self.height - new_ny) / 2))
        else:
            new_nx = int(round(self.height * nx / ny))
            new_ny = self.height
            off_x = int(round((self.width - new_nx) / 2))
        new_img = np.zeros((self.height, self.width, ch), dtype=np.uint8)
        resized_img = cv2.resize(img, (new_nx, new_ny), cv2.INTER_LINEAR)
        new_img[off_y:off_y+new_ny, off_x:off_x+new_nx, :] = resized_img
        if record_paras:
            self.resize_paras.raw_nx = nx
            self.resize_paras.raw_ny = ny
            self.resize_paras.nx = new_nx
            self.resize_paras.ny = new_ny
            self.resize_paras.off_x = off_x
            self.resize_paras.off_y = off_y
        return new_img

    def inside_img(self, x, y):
        return x >= self.resize_paras.off_x and y >= self.resize_paras.off_y and x < self.resize_paras.off_x + self.resize_paras.nx and y < self.resize_paras.off_y + self.resize_paras.ny
