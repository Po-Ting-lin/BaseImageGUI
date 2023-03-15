import cv2
import numpy as np
from UI.display import Display
from PyQt5.QtCore import Qt


class Tile(object):
    isShow = False
    sx = 0
    sy = 0
    w = 0
    h = 0


class ZoomDisplay(Display):
    def __init__(self, width, height,
                 mouseLDownCallback=None,
                 mouseLUpCallback=None,
                 mouseRDownCallback=None,
                 mouseRUpCallback=None,
                 mouseMoveCallback=None,
                 mouseWheelCallback=None):
        super(ZoomDisplay, self).__init__(width, height,
                                          mouseLDownCallback,
                                          mouseLUpCallback,
                                          mouseRDownCallback,
                                          mouseRUpCallback,
                                          mouseMoveCallback,
                                          mouseWheelCallback)
        self.tile = Tile()
        self.clean_img = None

    def mousePressEvent(self, event):
        x = event.x()
        y = event.y()
        if x >= self.width or y >= self.height:
            return
        if event.button() == Qt.LeftButton:
            self.tile.isShow = True
            self.tile.sx = x
            self.tile.sy = y
            self.clean_img = self.img.copy()
            if self.mouseLDownCallback is not None:
                self.mouseLDownCallback(x, y)
        elif event.button() == Qt.RightButton:
            if self.mouseRDownCallback is not None:
                self.mouseRDownCallback(x, y)

    def mouseReleaseEvent(self, event):
        x = event.x()
        y = event.y()
        if x >= self.width or y >= self.height:
            return
        if self.tile.isShow:
            if event.button() == Qt.LeftButton:
                self.update_image(self.clean_img)
                self.show_crop_tile()
                if self.mouseLUpCallback is not None:
                    self.mouseLUpCallback(x, y)
            elif event.button() == Qt.RightButton:
                self.tile.isShow = False
                img = self.resize_image(self.raw, False)
                self.update_image(img)
                if self.mouseRUpCallback is not None:
                    self.mouseRUpCallback(x, y)

    def mouseMoveEvent(self, event):
        x = event.x()
        y = event.y()
        if x >= self.width or y >= self.height:
            return
        if self.tile.isShow:
            self.tile.w = x - self.tile.sx
            self.tile.h = y - self.tile.sy
            self.plot_tile()
            if self.mouseLMoveCallback is not None:
                self.mouseLMoveCallback(x, y)

    def plot_tile(self):
        if self.tile.w != 0 and self.tile.h != 0:
            dirty = self.clean_img.copy()
            cv2.rectangle(dirty, (self.tile.sx, self.tile.sy), (self.tile.sx + self.tile.w, self.tile.sy + self.tile.h), color=(0, 0, 255), thickness=2)
            self.update_image(dirty)

    def show_crop_tile(self):
        if self.tile.isShow and self.tile.w != 0 and self.tile.h != 0:
            p1x, p1y = self.tile.sx, self.tile.sy
            p2x, p2y = self.tile.sx + self.tile.w, self.tile.sy + self.tile.h
            raw_p1x = int(round((p1x - self.resize_paras.off_x) * self.resize_paras.raw_nx / self.resize_paras.nx))
            raw_p1y = int(round((p1y - self.resize_paras.off_y) * self.resize_paras.raw_ny / self.resize_paras.ny))
            raw_p2x = int(round((p2x - self.resize_paras.off_x) * self.resize_paras.raw_nx / self.resize_paras.nx))
            raw_p2y = int(round((p2y - self.resize_paras.off_y) * self.resize_paras.raw_ny / self.resize_paras.ny))
            crop = self.raw[raw_p1y:raw_p2y, raw_p1x:raw_p2x]
            crop = self.resize_image(crop, False)
            self.update_image(crop)
