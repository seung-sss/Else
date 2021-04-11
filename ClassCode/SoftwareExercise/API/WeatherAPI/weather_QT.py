import sys

from PyQt5.QtCore import QStringListModel,Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QTableWidgetItem
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
from urllib.request import urlopen
import urllib.request, json

form_class = loadUiType("weather.ui")[0]

class MyWindowClass(QMainWindow, form_class):
    def __init__(self, parent=None):
        QMainWindow.__init__(self,parent)
        self.setupUi(self)
        self.url1 = "http://api.openweathermap.org/data/2.5/weather?id="
        self.url2 = "&APPID=2ae88b3ec4b4537d15165fca377a3ca9"
        file2 = open("city.list.json", encoding='utf-8-sig').read()
        cities = json.loads(file2)

# nameID['도시명'] = 도시ID 형식의 딕셔너리를 만든다.
        self.nameID = {}
        for city in cities:
            if city['country'] == 'KR':
                self.nameID[city['name']] = city['id']

# 내가 원하는 도시를 리스트뷰에 넣고 사용자가 선택할 경우 이벤트를 처리한다.
        cities = ['Seoul', 'Incheon', 'Sokcho', 'Jeju-do']
        model = QStringListModel(cities)
        self.listView.setModel(model)
        self.selModel = self.listView.selectionModel()
        self.selModel.selectionChanged.connect(self.listView_Clicked)

    def listView_Clicked(self):
        item = self.selModel.selection().indexes()[0]
        print(item.data())
        print(self.nameID[item.data()])
        url = self.url1 + str(self.nameID[item.data()]) + self.url2
        print(url)
        file1 = urllib.request.urlopen(url)
        s = json.loads(file1.read())
        print(s)
        print(s['weather'][0]['description'], s['weather'][0]['icon'])
        print(s['main']['temp'] - 273.15, s['main']['humidity'] )

# 오픈웨더맵에 날씨 아이콘을 가져와 pixmap 형태로 저장한 후, 출력한다.
        iconURL = 'http://openweathermap.org/img/w/' + s['weather'][0]['icon'] +'.png'
        pixmap = QPixmap()
        data = urllib.request.urlopen(iconURL).read()
        pixmap.loadFromData(data)
        pixmap = pixmap.scaled(100, 100, aspectRatioMode=True)
        self.label.setPixmap(pixmap)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setHorizontalHeaderLabels(["weather", "온도", "습도"])
        print(s['weather'][0]['description'])
# 결과값을 리스트에 담고, 하나씩 꺼내 테이블에 출력한다.
        items = [QTableWidgetItem(s['weather'][0]['description']),
                 QTableWidgetItem(str(round(s['main']['temp'] - 273.15))),
                 QTableWidgetItem(str(s['main']['humidity']))]
        for i in range(len(items)):
            self.tableWidget.setItem(0, i, items[i])
            items[i].setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

app = QApplication(sys.argv)
myWindow = MyWindowClass(None)
myWindow.show()
app.exec_()