import cv2
from UI.display import Display
from PyQt5.QtCore import Qt


class Tile(object):
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
                 mouseWheelCallback=None,
                 tileInfoCallback=None):
        super(ZoomDisplay, self).__init__(width, height,
                                          mouseLDownCallback,
                                          mouseLUpCallback,
                                          mouseRDownCallback,
                                          mouseRUpCallback,
                                          mouseMoveCallback,
                                          mouseWheelCallback)
        self.tile = Tile()
        self.enable_zoom = True
        self.is_show = False
        self.is_mag = False
        self.clean_img = None
        self.tileInfoCallback = tileInfoCallback

    def display(self, img):
        self.reset()
        self.is_displaying = True
        self.raw = img
        img = self.resize_image(img)
        self.update_image(img)

    def reset(self):
        self.is_displaying = False
        self.is_show = False
        self.is_mag = False
        self.enable_zoom = True

    def set_enable_zoom(self, value):
        self.enable_zoom = value

    def mousePressEvent(self, event):
        x = event.x()
        y = event.y()
        if not self.inside_img(x, y):
            return
        if event.button() == Qt.LeftButton:
            if self.enable_zoom and not self.is_mag:
                self.is_show = True
                self.tile.sx = x
                self.tile.sy = y
                self.clean_img = self.img.copy()
            if self.mouseLDownCallback is not None:
                self.mouseLDownCallback(x, y)
        elif event.button() == Qt.RightButton:
            if self.enable_zoom and self.is_mag:
                img = self.resize_image(self.raw, False)
                self.update_image(img)
                self.is_show = False
                self.is_mag = False
            if self.mouseRDownCallback is not None:
                self.mouseRDownCallback(x, y)

    def mouseMoveEvent(self, event):
        x = event.x()
        y = event.y()
        if not self.inside_img(x, y):
            return
        if self.enable_zoom and not self.is_mag and self.is_show:
            self.tile.w = x - self.tile.sx
            self.tile.h = y - self.tile.sy
            self.plot_tile()
        if self.mouseMoveCallback is not None:
            self.mouseMoveCallback(x, y)

    def mouseReleaseEvent(self, event):
        x = event.x()
        y = event.y()
        if not self.inside_img(x, y):
            return
        if event.button() == Qt.LeftButton:
            if self.enable_zoom and not self.is_mag and self.is_show:
                self.update_image(self.clean_img)
                self.show_crop_tile()
                if self.tileInfoCallback is not None:
                    img_x1, img_y1 = self.ui_xy_convert_to_img_xy(self.tile.sx, self.tile.sy)
                    img_x2, img_y2 = self.ui_xy_convert_to_img_xy(self.tile.sx + self.tile.w, self.tile.sy + self.tile.h)
                    self.tileInfoCallback(img_x1, img_y1, abs(img_x2 - img_x1), abs(img_y2 - img_y1))
                self.is_mag = True
            if self.mouseLUpCallback is not None:
                self.mouseLUpCallback(x, y)
        elif event.button() == Qt.RightButton:
            if self.mouseRUpCallback is not None:
                self.mouseRUpCallback(x, y)

    def plot_tile(self):
        if self.tile.w != 0 and self.tile.h != 0:
            dirty = self.clean_img.copy()
            cv2.rectangle(dirty, (self.tile.sx, self.tile.sy), (self.tile.sx + self.tile.w, self.tile.sy + self.tile.h), color=(0, 0, 255), thickness=2)
            self.update_image(dirty)

    def show_crop_tile(self):
        if self.is_show and self.tile.w != 0 and self.tile.h != 0:
            img_x1, img_y1 = self.ui_xy_convert_to_img_xy(self.tile.sx, self.tile.sy)
            img_x2, img_y2 = self.ui_xy_convert_to_img_xy(self.tile.sx + self.tile.w, self.tile.sy + self.tile.h)
            crop = self.raw[min(img_y1, img_y2):max(img_y1, img_y2), min(img_x1, img_x2):max(img_x1, img_x2)]
            crop = self.resize_image(crop, False)
            self.update_image(crop)

    def ui_xy_convert_to_img_xy(self, x, y):
        img_x = int(round((x - self.resize_paras.off_x) * self.resize_paras.raw_nx / self.resize_paras.nx))
        img_y = int(round((y - self.resize_paras.off_y) * self.resize_paras.raw_ny / self.resize_paras.ny))
        return img_x, img_y
