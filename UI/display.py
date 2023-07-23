import cv2
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel


class ResizeParas(object):
    off_x = 0  # offset x for UI canvas
    off_y = 0  # offset y for UI canvas
    nx = 0  # nx for UI canvas
    ny = 0  # ny for UI canvas
    raw_nx = 0  # the number of pixel for real image
    raw_ny = 0  # the number of pixel for real image


class Transform(object):
    def __init__(self):
        self.resize_paras = ResizeParas()
        self.raw_sx = 0  # the number of pixel of start point for real image, only for tile
        self.raw_sy = 0  # the number of pixel of start point for real image, only for tile

    def set_resize_paras(self, resize_paras):
        self.resize_paras.nx = resize_paras.nx
        self.resize_paras.ny = resize_paras.ny
        self.resize_paras.raw_nx = resize_paras.raw_nx
        self.resize_paras.raw_ny = resize_paras.raw_ny
        self.resize_paras.off_x = resize_paras.off_x
        self.resize_paras.off_y = resize_paras.off_y

    # input is UI coordinate
    def convert_ui_to_image_xy(self, x, y):
        tx = -1
        ty = -1

        if not self.inside_img(x, y):
            return tx, ty
        else:
            tx = x - self.resize_paras.off_x
            ty = y - self.resize_paras.off_y

        if (self.resize_paras.raw_nx / self.resize_paras.raw_ny) > (self.resize_paras.nx / self.resize_paras.ny):
            if tx >= 0:
                tx = int(tx * self.resize_paras.raw_nx / self.resize_paras.nx)
            if ty >= 0:
                ty = int(ty * self.resize_paras.raw_nx / self.resize_paras.nx)
        else:
            if tx >= 0:
                tx = int(tx * self.resize_paras.raw_ny / self.resize_paras.ny)
            if ty >= 0:
                ty = int(ty * self.resize_paras.raw_ny / self.resize_paras.ny)

        # Add offset if this is cropped tile in order to map this tile to whole raw image
        tx += self.raw_sx
        ty += self.raw_sy
        return tx, ty

    def inside_img(self, x, y):
        return self.resize_paras.off_x <= x < self.resize_paras.off_x + self.resize_paras.nx and self.resize_paras.off_y <= y < self.resize_paras.off_y + self.resize_paras.ny


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
        self.transform = Transform()
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

    def display(self, img, rgb_swap=True):
        self.reset()
        self.is_displaying = True
        self.raw = img
        img, self.transform.resize_paras = self.resize_image(img)
        self.__update_image(img, rgb_swap)

    def update_image(self, img, rgb_swap=True):
        self.__update_image(img, rgb_swap)

    def set_constant_mouse_move_tracking(self, value):
        if self.mouseMoveCallback is not None:
            self.setMouseTracking(value)

    def reset(self):
        self.is_displaying = False

    def __update_image(self, img, rgb_swap=True):
        if img is None:
            return
        self.img = img
        height, width, channel = self.img.shape
        # print("{}, {}, {}".format(height, width, channel))
        if rgb_swap:
            if channel == 3:
                self.q_img = QImage(self.img, width, height, channel * width, QImage.Format_RGB888).rgbSwapped()
            elif channel == 4:
                self.q_img = QImage(self.img, width, height, channel * width, QImage.Format_ARGB32).rgbSwapped()
        else:
            if channel == 3:
                self.q_img = QImage(self.img, width, height, channel * width, QImage.Format_RGB888)
            elif channel == 4:
                self.q_img = QImage(self.img, width, height, channel * width, QImage.Format_ARGB32)
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
        if not self.transform.inside_img(x, y):
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

    def resize_image(self, img):
        nx = img.shape[1]  # the number of pixel for real image
        ny = img.shape[0]  # the number of pixel for real image
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

        resize_paras = ResizeParas()
        resize_paras.raw_nx = nx  # the number of pixel for real image
        resize_paras.raw_ny = ny  # the number of pixel for real image
        resize_paras.nx = new_nx  # nx for UI image
        resize_paras.ny = new_ny  # ny for UI image
        resize_paras.off_x = off_x  # offset x for UI image
        resize_paras.off_y = off_y  # offset y for UI image
        return new_img, resize_paras
