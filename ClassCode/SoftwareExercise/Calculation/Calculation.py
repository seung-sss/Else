import sys
import math

from PyQt5.QtWidgets import QMainWindow,QApplication
from PyQt5.uic import loadUiType

form_class = loadUiType("Calculation.ui")[0]
class CalcClass(QMainWindow, form_class):
    def __init__(self, parent=None):
        QMainWindow.__init__(self,parent)
        self.setupUi(self)
        nums = [self.b0, self.b1, self.b2, self.b3, self.b4, self.b5, self.b6, self.b7, self.b8, self.b9]
        for number in nums:
            number.clicked.connect(self.Nums)
        self.bDel.clicked.connect(self.bDelClick)
        self.bClear.clicked.connect(self.bClearClick)
        self.bRun.clicked.connect(self.bRunClick)
        self.bPlus.clicked.connect(self.bPlusClick)
        self.bMinus.clicked.connect(self.bMinusClick)
        self.bMult.clicked.connect(self.bMultClick)
        self.bDivide.clicked.connect(self.bDivideClick)
        self.bDot.clicked.connect(self.bDotClick)
        self.bPercent.clicked.connect(self.bPercentClick)
        self.bLParenthesis.clicked.connect(self.bLParenthesisClick) # 왼쪽 괄호
        self.bRParenthesis.clicked.connect(self.bRParenthesisClick) # 오른쪽 괄호
        self.bMemoryclear.clicked.connect(self.bMemoryclearClick)
        self.bMemoryplus.clicked.connect(self.bMemoryplusClick)
        self.bMemoryminus.clicked.connect(self.bMemoryminusClick)
        self.bMemoryresult.clicked.connect(self.bMemoryresultClick)
        self.bSquare.clicked.connect(self.bSquareClick) # 제곱
        self.bCubing.clicked.connect(self.bCubingClick) # 세제곱
        self.bSquareXY.clicked.connect(self.bSquareXYClick) # X의 Y승
        self.bSquareroot.clicked.connect(self.bSquarerootClick)
        self.bCuberoot.clicked.connect(self.bCuberootClick)
        self.bFactorial.clicked.connect(self.bFactorialClick)
        self.bPi.clicked.connect(self.bPiClick)
        self.bCombination.clicked.connect(self.bCombinationClick)
        self.bLog10.clicked.connect(self.bLog10Click)
        self.temp_num = []
        self.temp_comb = []

    def Nums(self):
        global num
        sender = self.sender() # 어떤 버튼이 클릭됐는지에 대한 정보가 들어
        newNum = int(sender.text())
        setNum = str(newNum)
        if self.result.text() == "0":
            self.result.setText(setNum)
        else:
            self.result.setText(self.result.text() + setNum)

    def bDotClick(self):
        self.result.setText(self.result.text()+".")

    def bPlusClick(self):
        self.result.setText(self.result.text()+"+")

    def bMinusClick(self):
        self.result.setText(self.result.text()+"-")

    def bDivideClick(self):
        self.result.setText(self.result.text()+"/")

    def bMultClick(self):
        self.result.setText(self.result.text()+"*")

    def bDelClick(self):
        n=len(self.result.text())
        self.result.setText(self.result.text()[0:n-1])
        if self.result.text() == "":
            self.result.setText("0")

    def bClearClick(self):
        self.result.setText("0")

    def bRunClick(self):
        if "C" in self.result.text():
            n, r = map(int, self.result.text().split("C"))
            self.result.setText(str(self._Factorial(n) / (self._Factorial(r) * self._Factorial(n-r))))
        else:
            self.result.setText(str(eval(self.result.text())))

    def bPercentClick(self):
        self.result.setText(str(int(self.result.text()) / 100))

    def bLParenthesisClick(self):
        if self.result.text() == "0":
            self.result.setText("(")
        else:
            self.result.setText(self.result.text() + "(")

    def bRParenthesisClick(self):
        if self.result.text() == "0":
            self.result.setText(")")
        else:
            self.result.setText(self.result.text() + ")")

    def bMemoryclearClick(self):
        self.temp_num = []

    def bMemoryplusClick(self):
        self.temp_num.append(int(self.result.text()))
        self.result.setText("0")

    def bMemoryminusClick(self):
        self.temp_num.append(int("-" + self.result.text()))
        self.result.setText("0")

    def bMemoryresultClick(self):
        self.result.setText(str(sum(self.temp_num)))

    def bSquareClick(self):
        self.result.setText(str(int(self.result.text()) ** 2))

    def bCubingClick(self):
        self.result.setText(str(int(self.result.text()) ** 3))

    def bSquareXYClick(self):
        self.result.setText(self.result.text() + "**")

    def bSquarerootClick(self):
        self.result.setText(str(int(self.result.text()) ** (1 / 2)))

    def bCuberootClick(self):
        self.result.setText(str(int(self.result.text()) ** (1 / 3)))

    def _Factorial(self, n):
        _tmp = 1
        for i in range(1, n + 1):
            _tmp *= i
        return _tmp

    def bFactorialClick(self):
        self.result.setText(str(self._Factorial(int(self.result.text()))))

    def bPiClick(self):
        self.result.setText(str(math.pi))

    def bCombinationClick(self):
        self.result.setText(self.result.text() + "C")

    def bLog10Click(self):
        self.result.setText(str(math.log10(int(self.result.text()))))

app = QApplication(sys.argv)
myWindow = CalcClass(None)
myWindow.show()
app.exec_()