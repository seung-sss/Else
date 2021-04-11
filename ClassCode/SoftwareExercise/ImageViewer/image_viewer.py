import sys
from PyQt5.QtWidgets import QMainWindow,QApplication, qApp, QFileDialog, QWidget, QRubberBand
from PyQt5.QtCore import QPoint, QRect, QSize, Qt
from PyQt5.uic import loadUiType
from PyQt5.QtGui import *
import os
import glob
import numpy as np
import cv2
import fortcode

form_class1 = loadUiType("image_viewer.ui")[0]
form_class2 = loadUiType("rotate_change.ui")[0]

class AnotherWindow(QWidget, form_class2):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

class ViewerClass(QMainWindow, form_class1):
    def __init__(self, parent = None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.qPixmapVar = QPixmap()
        self.action_FileS.triggered.connect(self.FileSelect)
        self.action_FolderS.triggered.connect(self.FolderSelect)
        self.action_Exit.triggered.connect(qApp.quit)

        self.action_toGray.triggered.connect(self.toGraySelect)
        self.action_Left.triggered.connect(self.shiftLeft)
        self.action_Right.triggered.connect(self.shiftRight)
        self.action_Up.triggered.connect(self.shiftUp)
        self.action_Down.triggered.connect(self.shiftDown)
        self.action_Rotate.triggered.connect(self.show_new_window)
        self.action_Crop.triggered.connect(self.imageCrop)
        self.action_MedBlur.triggered.connect(self.blur_median)
        self.action_GausBlur.triggered.connect(self.blur_gaussian)
        self.action_Next.triggered.connect(self.MoveNext)

        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()
        self.idx = 0
        self.hh = 1200
        self.ww = 1200
        self.cropEnable = False

    def img2label(self, img):
        self.qPixmapVar = QPixmap(self.img2QImage(img))
        self.qPixmapVar = self.qPixmapVar.scaled(self.hh, self.ww, aspectRatioMode=True)
        self.label.setPixmap(self.qPixmapVar)

    def img2QImage(self, img):
        # qPixmap에 넣기 위해서 QImage가 input 되어야 함
        return QImage(img, img.shape[1], img.shape[0], img.shape[1] * 3, QImage.Format_RGB888)

    def img2QImageGray(self, img):
        return QImage(img, img.shape[1], img.shape[0], img.shape[1], QImage.Format_Grayscale8)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = QPoint(event.pos()) # QPoint 좌표로 바꿔주는 것
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()

    def mouseMoveEvent(self, event):
        if not self.origin.isNull():
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.rubberBand.hide()

        if self.cropEnable == True:
            self.selStart = self.origin - self.startPos - QPoint(10, 10)
            self.selEnd = event.pos() - self.startPos - QPoint(10, 10)
            cut_begin_x = int((self.img_width_origin / self.img_width_tran) * self.selStart.x())
            cut_begin_y = int((self.img_height_origin / self.img_height_tran) * self.selStart.y())
            cut_end_x = int((self.img_width_origin / self.img_width_tran) * self.selEnd.x())
            cut_end_y = int((self.img_height_origin / self.img_height_tran) * self.selEnd.y())
            self.img = self.img[cut_begin_y:cut_end_y, cut_begin_x:cut_end_x, :].astype('uint8')
            self.img2label(self.img)
            self.cropEnable = False

    def FileSelect(self):
        self.fName = QFileDialog.getOpenFileName(self, 'Open file', 'C:/software_exercise/imageviewer/image', "image files (*.jpg)")[0]
        self.img = cv2.imread(self.fName) # 읽으면 3차원 matrix가 옴(BGR순서)
        self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB) # RGB순서로 바꿈
        self.img_height_origin = self.img.shape[0]
        self.img_width_origin = self.img.shape[1]
        self.img2label(self.img)

    def FolderSelect(self):
        dirName = QFileDialog.getExistingDirectory(self, 'Open Folder', 'C:/software_exercise/imageviewer/image')
        self.files = []
        for file in glob.glob(os.path.join(dirName, '*.jpg')):
            self.files.append(file)

        self.img = cv2.imread(self.files[0])
        self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        self.img_height_origin = self.img.shape[0]
        self.img_width_origin = self.img.shape[1]
        self.img2label(self.img)

    def MoveNext(self):
        self.idx += 1
        self.img = cv2.imread(self.files[self.idx])
        self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        self.img_height_origin = self.img.shape[0]
        self.img_width_origin = self.img.shape[1]
        self.img2label(self.img)

    def toGraySelect(self):
        self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        self.qPixmapVar = QPixmap(self.img2QImageGray(self.img))
        self.qPixmapVar = self.qPixmapVar.scaled(self.hh, self.ww, aspectRatioMode=True)
        self.label.setPixmap(self.qPixmapVar)

    def imageCrop(self):
        self.cropEnable = True
        self.hw_ratio = self.img_height_origin / self.img_width_origin # > 1이면 세로사진, < 1은 가로사진

        if self.hw_ratio > 1: # 세로사진이면 높이가 최대 길이가 되고 너비는 비례로 작아진다
            self.img_height_tran = self.hh
            self.img_width_tran = int((self.img_height_tran / self.img_height_origin) * self.img_width_origin)
            self.startPos = QPoint((self.ww - self.img_width_tran) // 2, 0)
            self.endPos = QPoint(self.startPos.x() + self.img_width_tran, self.hh)
        else: # 가로사진이면 너비가 최대 길이가 되고 높이는 비례로 작아진다
            self.img_width_tran = self.ww
            self.img_height_tran = int((self.img_width_tran / self.img_width_origin) * self.img_height_origin)
            self.startPos = QPoint(0, (self.hh - self.img_height_tran) // 2)
            self.endPos = QPoint(self.ww, self.startPos.y() + self.img_height_tran)

    # # Fortran 사용 전 코드
    # def rotate_image(self):
    #     angle = self.w.horizontalSlider.value()
    #     rad = np.pi / (180 / angle)
          # 이미지 중심좌표 구하기
    #     x0 = self.img_height_origin // 2
    #     y0 = self.img_width_origin // 2
    #
    #     newImg = np.zeros((self.img_height_origin, self.img_width_origin, 3)).astype('uint8') # 빈 이미지를 만든다
    #
    #     for k in range(3):
    #         for i in range(self.img_height_origin):
    #             for j in range(self.img_width_origin):
    #                 # 이미지의 모든 i, j에 대해 중심을 원점으로 rad만큼 회전한 좌표를 구한다.
    #                 x = int((i - x0) * np.cos(rad) - (j - y0) * np.sin(rad) + x0)
    #                 y = int((i - x0) * np.sin(rad) + (j - y0) * np.cos(rad) + y0)
    #                 # 해당 좌표가 이미지 공간을 벗어나지 않으면 회전된 위치에 값을 복사한다.
    #                 if (x < self.img_height_origin) and (x >= 0):
    #                     if (y < self.img_width_origin) and (y >= 0):
    #                         newImg[x, y, k] = self.img[i, j, k]
    #     self.img2label(newImg)

    def rotate_image(self):
        angle = self.w.horizontalSlider.value()
        rad = np.pi / (180 / angle)

        rotateImg = fortcode.rotate(self.img, self.img_height_origin, self.img_width_origin, rad)
        rotateImg = np.require(rotateImg, np.uint8, 'C') # fortran array to numpy array
        self.img2label(rotateImg)

    # # Fortran 사용 전 코드
    # def medFilter(self, img):
    #     return np.median(img)
    #
    # def blur_median(self):
    #     QApplication.setOverrideCursor(Qt.WaitCursor)
    #     img_median = self.img[:,:,:]
    #     for k in range(3):
    #         for i in range(1, self.img_height_origin - 1):
    #             for j in range(1, self.img_width_origin - 1):
    #                 med = self.medFilter(self.img[i -1 : i + 2, j - 1 : j + 2, k])
    #                 img_median[i, j, k] = int(med)
    #
    #     self.img2label(img_median)
    #     QApplication.restoreOverrideCursor()

    def blur_median(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        img_median = fortcode.med_filter(self.img, self.img_height_origin, self.img_width_origin)
        img_median = np.require(img_median, np.uint8, 'C') # fortran array to numpy array
        self.img2label(img_median)
        QApplication.restoreOverrideCursor()

    # # Fortran 사용 전 코드
    # def gausFilter(self, img):
    #     _tmp = img[0, 0] + img[0, 1] * 2 + img[0, 2] + img[1, 0] * 2 + img[1, 1] * 4 + img[1, 2] * 2 + img[2, 0] + img[2, 1] * 2 + img[2, 2]
    #     return (_tmp / 16)

    # def blur_gaussian(self):
    #     QApplication.setOverrideCursor(Qt.WaitCursor)
    #     img_gaussian = self.img[:,:,:]
    #     for k in range(3):
    #         for i in range(1, self.img_height_origin - 1):
    #             for j in range(1, self.img_width_origin - 1):
    #                 gaus = self.gausFilter(self.img[i-1 : i + 2, j - 1 : j + 2, k])
    #                 img_gaussian[i, j, k] = int(gaus)
    #     self.img2label(img_gaussian)
    #     QApplication.restoreOverrideCursor()

    def blur_gaussian(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        img_gauss = fortcode.gauss_filter(self.img, self.img_height_origin, self.img_width_origin)
        img_gauss = np.require(img_gauss, np.uint8, 'C') # fortran array to numpy array
        self.img2label(img_gauss)
        QApplication.restoreOverrideCursor()

    def show_new_window(self):
        self.w = AnotherWindow()
        self.w.horizontalSlider.valueChanged.connect(self.rotate_image)
        self.w.show()

    def shiftLeft(self):
        _tmp = np.zeros((self.img_height_origin, 100, 3))
        self.img = np.concatenate((_tmp, self.img), axis = 1)
        self.img = self.img[:, :self.img_width_origin, :].astype('uint8')
        self.img2label(self.img)

    def shiftRight(self):
        _tmp = np.zeros((self.img_height_origin, 100, 3))
        self.img = np.concatenate((self.img, _tmp), axis = 1)
        self.img = self.img[:, 100:, :].astype('uint8')
        self.img2label(self.img)

    def shiftUp(self):
        _tmp = np.zeros((100, self.img_width_origin, 3))
        self.img = np.concatenate((self.img, _tmp), axis = 0)
        self.img = self.img[100:, :, :].astype('uint8')
        self.img2label(self.img)

    def shiftDown(self):
        _tmp = np.zeros((100, self.img_width_origin, 3))
        self.img = np.concatenate((_tmp, self.img), axis = 0)
        self.img = self.img[:self.img_height_origin, :, :].astype('uint8')
        self.img2label(self.img)

app = QApplication(sys.argv)
myWindow = ViewerClass(None)
myWindow.show()
app.exec_()