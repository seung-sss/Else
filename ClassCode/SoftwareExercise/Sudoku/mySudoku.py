import sys
import random
from PyQt5.QtWidgets import QMainWindow,QApplication
from PyQt5.uic import loadUiType
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtCore import Qt
import time

form_class=loadUiType("Sudoku.ui")[0]

class SudokuUI(QMainWindow, form_class):

    def __init__(self, parent=None):
        QMainWindow.__init__(self,parent)
        self.setupUi(self)
        global AVal, ButtonList, Dif

        ButtonList = [[self.A00, self.A01, self.A02, self.A03, self.A04, self.A05, self.A06, self.A07, self.A08],
                      [self.A10, self.A11, self.A12, self.A13, self.A14, self.A15, self.A16, self.A17, self.A18],
                      [self.A20, self.A21, self.A22, self.A23, self.A24, self.A25, self.A26, self.A27, self.A28],
                      [self.A30, self.A31, self.A32, self.A33, self.A34, self.A35, self.A36, self.A37, self.A38],
                      [self.A40, self.A41, self.A42, self.A43, self.A44, self.A45, self.A46, self.A47, self.A48],
                      [self.A50, self.A51, self.A52, self.A53, self.A54, self.A55, self.A56, self.A57, self.A58],
                      [self.A60, self.A61, self.A62, self.A63, self.A64, self.A65, self.A66, self.A67, self.A68],
                      [self.A70, self.A71, self.A72, self.A73, self.A74, self.A75, self.A76, self.A77, self.A78],
                      [self.A80, self.A81, self.A82, self.A83, self.A84, self.A85, self.A86, self.A87, self.A88]]

        for i in range(0,9):
            for number in ButtonList[i]:
                number.clicked.connect(self.NumClick)

        AVal=[]

        for i in range(0,9):
            temp=[]
            for j in range(0,9):
                temp.append(str(ButtonList[i][j].text()))
            AVal.append(temp)

        Dif = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        self.Dif_idx = 6

        self.count = 3

        self.correct = []

        self.startTime = time.time()
        self.endTime = 0

        self.countEdit.setText("%d회 중 %s회 사용 가능" %(3, self.count))
        self.ShuffleClick()
        self.shuffleButton.clicked.connect(self.ShuffleClick)
        self.finishButton.clicked.connect(self.CompleteTestClick)
        self.downButton.clicked.connect(self.DownClick)
        self.upButton.clicked.connect(self.UpClick)
        self.hintButton.clicked.connect(self.HintClick)

    def ShuffleClick(self):
        random19 = list(range(1,10))
        random.shuffle(random19)
        self.resEdit.setText("Let's start!!")
        self.correct = []
        self.count = 3
        self.countEdit.setText("%d회 중 %s회 사용 가능" % (3, self.count))

        for i in range(9):
            for j in range(9):
                ButtonList[i][j].setText(str(random19[int(AVal[i][j]) - 1]))
                ButtonList[i][j].setStyleSheet('QPushButton {color: black;}')

        for i in range(0,9):
            temp=[]
            for j in range(0,9):
                temp.append(str(ButtonList[i][j].text()))
            self.correct.append(temp)

        for i in range(9):
            for j in range(9):
                if random.random() > float(self.pEdit.text()):
                    ButtonList[i][j].setText("")


    def NumClick(self):
        global XLoc, YLoc
        for i in range(0, 9):
            for j in range(0, 9):
                if self.sender() == ButtonList[i][j]:
                    XLoc = i
                    YLoc = j

    def keyPressEvent(self, event):
        if type(event) == QKeyEvent:
            if event.key() == Qt.Key_1:
                ButtonList[XLoc][YLoc].setText("1")
            elif event.key() == Qt.Key_2:
                ButtonList[XLoc][YLoc].setText("2")
            elif event.key() == Qt.Key_3:
                ButtonList[XLoc][YLoc].setText("3")
            elif event.key() == Qt.Key_4:
                ButtonList[XLoc][YLoc].setText("4")
            elif event.key() == Qt.Key_5:
                ButtonList[XLoc][YLoc].setText("5")
            elif event.key() == Qt.Key_6:
                ButtonList[XLoc][YLoc].setText("6")
            elif event.key() == Qt.Key_7:
                ButtonList[XLoc][YLoc].setText("7")
            elif event.key() == Qt.Key_8:
                ButtonList[XLoc][YLoc].setText("8")
            elif event.key() == Qt.Key_9:
                ButtonList[XLoc][YLoc].setText("9")
            else:
                print ("Error")
        ButtonList[XLoc][YLoc].setStyleSheet('QPushButton {color: red;}')

    def CompleteTestClick(self):
        self.endTime = time.time()
        err = 0
        self.resEdit.setText("")
        for i in range(0,9):
            for j in range(0,9):
                AVal[i][j] = ButtonList[i][j].text()

    # row test
        for i in range(0,9):
            if len(set(AVal[i])) != 9:
                self.resEdit.setText("%dth row Error" %(i+1))
                err += 1
                break

    # column test
        for i in range(0,9):
            _tmp = []
            for j in range(0,9):
                _tmp.append(AVal[i][j])
            if len(set(_tmp)) != 9:
                self.resEdit.setText("%dth column Error" %(i+1))
                err += 1
                break

    # matrix test
        index = [0, 3, 6]
        for i in index:
            for j in index:
                _tmp = []
                for k in range(0,3):
                    _tmp.append(AVal[i][j + k])
                    _tmp.append(AVal[i + 1][j + k])
                    _tmp.append(AVal[i + 2][j + k])
                if len(set(_tmp)) != 9:
                    if i == 0:
                        if j == 0:
                            num_text = "1, 1"
                        elif j == 3:
                            num_text = "1, 2"
                        elif j == 6:
                            num_text = "1, 3"
                    elif i == 3:
                        if j == 0:
                            num_text = "2, 1"
                        elif j == 3:
                            num_text = "2, 2"
                        elif j == 6:
                            num_text = "2, 3"
                    elif i == 6:
                        if j == 0:
                            num_text = "3, 1"
                        if j == 3:
                            num_text = "3, 2"
                        if j == 6:
                            num_text = "3, 3"
                    self.resEdit.setText(num_text + "th 3*3 matrix Error")
                    err += 1
                    break

        if err == 0:
            self.resEdit.setText("~~~ 축하합니다!!! 총 소요시간은 %d초 입니다!!! ~~~" %(self.endTime - self.startTime))

    def DownClick(self):
        if 0 < self.Dif_idx:
            self.Dif_idx -= 1
            self.pEdit.setText(str(Dif[self.Dif_idx]))
            self.ShuffleClick()

    def UpClick(self):
        if self.Dif_idx < 8:
            self.Dif_idx += 1
            self.pEdit.setText(str(Dif[self.Dif_idx]))
            self.ShuffleClick()

    def HintClick(self):

        if self.count != 0:
            ButtonList[XLoc][YLoc].setText(str(self.correct[XLoc][YLoc]))
            ButtonList[XLoc][YLoc].setStyleSheet('QPushButton {color: blue;}')
            self.count -= 1
            if self.count == 0:
                self.countEdit.setText("힌트를 전부 사용하였습니다!")
            else:
                self.countEdit.setText("%d회 중 %s회 사용 가능" % (3, self.count))

app=QApplication(sys.argv)
myWindow=SudokuUI(None)
myWindow.show()
app.exec_()
