import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUiType
from PyQt5.QtGui import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from statsmodels.tsa.arima_model import ARMA
import datetime
from pytz import timezone

form_class_main = loadUiType("stock_analysis_program.ui")[0]
form_class_search = loadUiType("search_stock.ui")[0]
form_class_analysis = loadUiType("detail_and_analysis.ui")[0]
form_class_delete_yn = loadUiType("delete_yn.ui")[0]

class AnotherWindow_1(QDialog, form_class_search):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("search stock")

        # self.search_text.textChanged.connect(self.lineeditTextFunction)
        self.search_text.returnPressed.connect(self.reset_comboBox)
        self.search_button.clicked.connect(self.reset_comboBox)
        self.add_button.clicked.connect(self.pick_stock)
        self.ok_button.clicked.connect(self.add_stock)
        self.retry_button.clicked.connect(self.back_dialog)

        self.textBrowser_second.hide()
        self.ok_button.hide()
        self.retry_button.hide()

        self.choice_stock = None

        stock_data = pd.read_csv("C:\software_exercise\Stock_Analysis_Program\data\Pick_stock_list.csv")
        self.stock_name_list = stock_data["Name"].tolist()

        for stock in self.stock_name_list:
            self.stocklist_comboBox.addItem(stock)

    def reset_comboBox(self):
        self.stocklist_comboBox.clear()

        for stock in self.stock_name_list:
            if self.search_text.text() in stock:
                self.stocklist_comboBox.addItem(stock)

    def pick_stock(self):
        self.choice_stock = self.stocklist_comboBox.currentText()
        self.textBrowser_first.hide()
        self.textBrowser_second.show()
        self.result_label.setText("'%s' 추가하시겠습니까?" % self.choice_stock)

        self.add_button.hide()
        self.ok_button.show()
        self.retry_button.show()

    def add_stock(self):
        self.close()

    def back_dialog(self):
        self.choice_stock = None
        self.textBrowser_second.hide()
        self.textBrowser_first.show()
        self.result_label.clear()

        self.ok_button.hide()
        self.retry_button.hide()
        self.add_button.show()


class AnotherWindow_2(QDialog , form_class_analysis):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("analysis")

        self.pq = [(0,1), (0,2), (1,0), (1,1), (1,2), (2,0), (2,1), (2,2)]

        self.fig1 = plt.Figure()
        self.fig2 = plt.Figure()
        self.canvas1 = FigureCanvas(self.fig1)
        self.canvas2 = FigureCanvas(self.fig2)
        self.verticalLayout.addWidget(self.canvas1)
        self.verticalLayout.addWidget(self.canvas2)

        self.info_list = [self.yesterday_end_price, self.high, self.volume, self.open, self.low, self.trade_price,
                          self.PER, self.EPS]

        self.df = None
        self.cips = pd.read_csv("C:\software_exercise\Stock_Analysis_Program\data\company_info_per_score.csv")

        self.analysis_button.clicked.connect(self.analysis_info)

        self.groupBox_detail.hide()
        self.groupBox_analysis.hide()
        self.canvas1.hide()
        self.canvas2.hide()

    def now_data(self):
        self.df = pd.read_csv("C:\software_exercise\Stock_Analysis_Program\data\csv\\" + self.now_company_name + "_" + self.now_company_symbol + ".csv")

    # self.now_company는 현재 선택한 groupBox 회사의 종목번호 / 해당 그룹박스 클릭 시 자동으로 열림
    def detail_info(self):
        self.canvas1.show()
        self.groupBox_detail.show()

        info_data_list = list(self.get_candle_chart_data(self.now_company_symbol) + self.get_per_eps_data(self.now_company_symbol))
        info_data_list[5] = info_data_list[5] + '백만'
        info_data_list[6] = info_data_list[6] + '배'
        info_data_list[7] = info_data_list[7] + '원'

        for i in range(8):
            self.info_list[i].setText(info_data_list[i])

        self.stockGraph()

    def analysis_info(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.canvas1.hide()
        self.groupBox_detail.hide()
        self.canvas2.show()
        self.groupBox_analysis.show()

        # 시계열 분석
        y = self.df['Close']
        best_aic, best_pq = self.find_best_pq(y)
        fore = self.make_ts_model(y, best_pq)
        fore_price = str(int(fore))

        if 3 < len(fore_price) <= 6:
            fore_price = fore_price[:-3] + ',' + fore_price[-3:]
        elif 6 < len(fore_price):
            fore_price = fore_price[:-6] + ',' + fore_price[:-3] + ',' + fore_price[-3:]

        self.ts_result_label.setText("시계열 분석 결과 다음 거래일 종가는 %s원으로 예상됩니다. <ARMA(%d, %d) 모델 이용>" % (fore_price, best_pq[0], best_pq[1]))

        # 이동평균선 분석
        self.ma_result_label.setText("이동평균선 분석 결과 주가는 %s 추세를 보일 것으로 예상됩니다." % self.ma_analysis())

        # PER분석
        company_per = float(self.cips[self.cips['Symbol'] == self.now_company_symbol]['PER'])
        average_per = float(self.cips[self.cips['Symbol'] == self.now_company_symbol]['similar_PER'])
        w1, w2 = self.per_analysis(company_per, average_per)

        self.per_result_label.setText("동종업종 평균 PER (%0.2f) 대비 해당기업의 PER (%0.2f)는 %s 편으로, 이는 %s평가 된 종목임을 의미합니다." %(average_per, company_per, w1, w2))

        self.analysisGraph(fore)
        QApplication.restoreOverrideCursor()

    def stockGraph(self):
        self.fig1.clear()

        ax = self.fig1.add_subplot(111)
        ax.plot(self.df['High'], label='stock_price')

        ax.set_xlabel("Date")
        ax.set_ylabel("Price")

        ax.set_title(self.now_company_symbol)
        ax.legend()

        self.canvas1.draw()

    def analysisGraph(self, fore):
        self.fig2.clear()

        ma20 = self.df['MA20']
        ma60 = self.df['MA60']

        ax = self.fig2.add_subplot(111)
        ax.scatter(self.df.index[-1] + 1, fore, c='red', label = "Time Series Forecast")
        ax.plot(self.df['High'], label='stock_price')
        ax.plot(ma20, label="Moving Average (window=20)", linestyle='-.')
        ax.plot(ma60, label="Moving Average (window=60)", linestyle="--")

        ax.set_xlabel("Date")
        ax.set_ylabel("Price")

        ax.set_title("Moving Average")
        ax.legend()

        self.canvas2.draw()

    def find_best_pq(self, y):
        best_aic = np.inf
        best_pq = None

        for param in self.pq:
            try:
                temp_model = ARMA(y, order=param)
                res = temp_model.fit()

                if res.aic < best_aic:
                    best_aic = res.aic
                    best_pq = param

            except:
                pass

        return best_aic, best_pq

    def make_ts_model(self, y, pq):
        model = ARMA(y, order=pq)
        result = model.fit()
        fore = result.forecast(steps=1)
        return fore[0]

    def ma_analysis(self):
        now_ma20 = self.df.loc[self.df.index[-1], 'MA20']
        now_ma60 = self.df.loc[self.df.index[-1], 'MA60']

        if now_ma20 > now_ma60:
            return "상승"
        else:
            return "하락"

    def per_analysis(self, company_per, average_per):
        if company_per > average_per:
            return '높은', '고'
        else:
            return '낮은', '저'

    def get_bs_obj(self, company_code):
        url = 'https://finance.naver.com/item/main.nhn?code=' + company_code
        result = requests.get(url)
        bs_obj = BeautifulSoup(result.content, "html.parser")  # url의 전체 소스코드 받아온 것
        return bs_obj

    # return : 전일(종가), 고가, 거래량, 시가, 저가, 거래대금
    def get_candle_chart_data(self, company_code):
        bs_obj = self.get_bs_obj(company_code)
        table = bs_obj.find("table", {"class": "no_info"})

        first_tr = table.find("tr")
        first_tds = first_tr.findAll("td")

        # 전일(종가)

        first_span = first_tds[0].find("span", {"class": "blind"})
        yesterday_end = first_span.text

        # 고가

        second_span = first_tds[1].find("span", {"class": "blind"})
        now_high = second_span.text

        # 거래량
        third_span = first_tds[2].find("span", {"class": "blind"})
        now_volume = third_span.text

        second_tr = table.findAll("tr")[1]
        second_tds = second_tr.findAll("td")

        # 시가
        fourth_span = second_tds[0].find("span", {"class": "blind"})
        now_open = fourth_span.text

        # 저가
        fifth_span = second_tds[1].find("span", {"class": "blind"})
        now_low = fifth_span.text

        # 거래대금
        sixth_span = second_tds[2].find("span", {"class": "blind"})
        now_trade_price = sixth_span.text

        return yesterday_end, now_high, now_volume, now_open, now_low, now_trade_price

    # return : per, eps
    def get_per_eps_data(self, company_code):
        bs_obj = self.get_bs_obj(company_code)

        table = bs_obj.find("table", {"class": "per_table"})
        tbody = table.find("tbody")
        tr = tbody.find("tr")
        td = tr.find("td")
        ems = td.findAll("em")
        return ems[0].text, ems[1].text

    # return : 동종업종 per
    def get_similar_company_per_data(self, company_code):
        bs_obj = self.get_bs_obj(company_code)
        table = bs_obj.find("table", {"summary": "동일업종 PER 정보"})
        tr = table.find("tr", {"class": "strong"})
        em = tr.find("em")
        return em.text



class AnotherWindow_3(QDialog , form_class_delete_yn):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.del_yn = False

        self.yes_button.clicked.connect(self.delete_stock)
        self.no_button.clicked.connect(self.back)

    def delete_stock(self):
        self.del_yn = True
        self.close()

    def back(self):
        self.close()


class Mainwindow(QMainWindow, form_class_main):
    def __init__(self, parent = None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)

        now = datetime.datetime.now(timezone('Asia/Seoul'))
        self.update.setText("마지막 업데이트 : %s년 %s월 %s일 %s시 %s분 %s초" % (now.year, now.month, now.day, now.hour, now.minute, now.second))

        # 추가/삭제하기 버튼 클릭
        self.add_del_button.clicked.connect(self.add_del_stock)

        self.yesterday_list = [self.yesterdaylabel_1, self.yesterdaylabel_2, self.yesterdaylabel_3, self.yesterdaylabel_4,
                               self.yesterdaylabel_5, self.yesterdaylabel_6, self.yesterdaylabel_7, self.yesterdaylabel_8,
                               self.yesterdaylabel_9, self.yesterdaylabel_10, self.yesterdaylabel_11, self.yesterdaylabel_12]

        for val in self.yesterday_list:
            val.hide()

        # 처음 프로그램 실행 시, 추가/삭제 버튼 숨기기
        self.add_del_list = [self.add_del_1, self.add_del_2, self.add_del_3, self.add_del_4,
                        self.add_del_5, self.add_del_6, self.add_del_7, self.add_del_8,
                        self.add_del_9, self.add_del_10, self.add_del_11, self.add_del_12]

        for button in self.add_del_list:
            button.hide()

        for button in self.add_del_list:
            button.clicked.connect(self.show_search_stock_window)

        # 각 그룹박스 영역 클릭시, 이벤트 활성화
        self.groupBox_dic = {"0": [(0, 560, 0, 140), self.name_1, self.symbol_1, self.price_1, self.updown_1, self.changeprice_1, self.changerate_1],
                             "1": [(0, 560, 141, 280), self.name_2, self.symbol_2, self.price_2, self.updown_2, self.changeprice_2, self.changerate_2],
                             "2": [(0, 560, 281, 420), self.name_3, self.symbol_3, self.price_3, self.updown_3, self.changeprice_3, self.changerate_3],
                             "3": [(0, 560, 421, 560), self.name_4, self.symbol_4, self.price_4, self.updown_4, self.changeprice_4, self.changerate_4],
                             "4": [(0, 560, 561, 700), self.name_5, self.symbol_5, self.price_5, self.updown_5, self.changeprice_5, self.changerate_5],
                             "5": [(0, 560, 701, 840), self.name_6, self.symbol_6, self.price_6, self.updown_6, self.changeprice_6, self.changerate_6],
                             "6": [(561, 1120, 0, 140), self.name_7, self.symbol_7, self.price_7, self.updown_7, self.changeprice_7, self.changerate_7],
                             "7": [(561, 1120, 141, 280), self.name_8, self.symbol_8, self.price_8, self.updown_8, self.changeprice_8, self.changerate_8],
                             "8": [(561, 1120, 281, 420), self.name_9, self.symbol_9, self.price_9, self.updown_9, self.changeprice_9, self.changerate_9],
                             "9": [(561, 1120, 421, 560), self.name_10, self.symbol_10, self.price_10, self.updown_10, self.changeprice_10, self.changerate_10],
                             "10": [(561, 1120, 561, 700), self.name_11, self.symbol_11, self.price_11, self.updown_11, self.changeprice_11, self.changerate_11],
                             "11": [(561, 1120, 701, 840), self.name_12, self.symbol_12, self.price_12, self.updown_12, self.changeprice_12, self.changerate_12]}

        # 클릭 된 add_del 버튼의 index 값
        self.gb_loc = None

        # [name, symbol]
        self.choice_stock_list = [[None, None], [None, None], [None, None], [None, None], [None, None], [None, None],
                                  [None, None], [None, None], [None, None], [None, None], [None, None], [None, None]]

        self.df = pd.read_csv("C:\software_exercise\Stock_Analysis_Program\data\company_info_per_score.csv")
        self.stock_name_list = self.df['Name'].tolist()
        self.stock_symbol_list = self.df['Symbol'].tolist()

        # 주가 급등 종목 테이블 함수
        self.pricejump_section()

        # 거래량 급등 종목 테이블 함수
        self.volumejump_section()

        # 종목 추천
        self.combobox_list = [self.recom_cb_1, self.recom_cb_2, self.recom_cb_3, self.recom_cb_4]
        self.checkbox_list = [self.recom_check_1, self.recom_check_2, self.recom_check_3, self.recom_check_4]

        self.recom_table.hide()
        self.recom_button_2.hide()

        for combobox in self.combobox_list:
            combobox.hide()

        for checkbox in self.checkbox_list:
            checkbox.stateChanged.connect(self.combobox_show)

        self.recom_button.clicked.connect(self.score_calc)
        self.recom_button_2.clicked.connect(self.back_to_choice)

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:
            self.origin = QPoint(event.pos())

            for key, value in self.groupBox_dic.items():
                if (value[0][0] < self.origin.x() < value[0][1]) and (value[0][2] < self.origin.y() < value[0][3]):
                    select_groupBox = key
                    break
                else:
                    select_groupBox = None

            if select_groupBox != None and self.choice_stock_list[int(select_groupBox)][0] != None:
                QApplication.setOverrideCursor(Qt.WaitCursor)
                dlg2 = AnotherWindow_2()
                dlg2.now_company_name = self.choice_stock_list[int(select_groupBox)][0]
                dlg2.now_company_symbol = self.choice_stock_list[int(select_groupBox)][1]
                dlg2.now_data()
                dlg2.detail_info()
                QApplication.restoreOverrideCursor()
                dlg2.exec_()

    def add_del_stock(self):
        for button in self.add_del_list:
            button.show()

    def add_del_stock_hide(self):
        for button in self.add_del_list:
            button.hide()

    def show_search_stock_window(self):
        for i in range(len(self.add_del_list)):
            if self.sender() == self.add_del_list[i]:
                self.gb_loc = i
                break

        if self.add_del_list[self.gb_loc].text() == '+':
            dlg = AnotherWindow_1()
            dlg.exec_()
            self.add_del_stock_hide()
            choice_stock = dlg.choice_stock
            self.push_now_stock(self.gb_loc, choice_stock)
            self.add_del_list[self.gb_loc].setText("-")

        elif self.add_del_list[self.gb_loc].text() == '-':
            dlg3 = AnotherWindow_3()
            dlg3.exec_()
            del_yn = dlg3.del_yn

            if del_yn == True:
                self.groupBox_dic[str(self.gb_loc)][1].clear()
                self.groupBox_dic[str(self.gb_loc)][2].clear()
                self.groupBox_dic[str(self.gb_loc)][3].clear()
                self.yesterday_list[self.gb_loc].hide()
                self.groupBox_dic[str(self.gb_loc)][4].clear()
                self.groupBox_dic[str(self.gb_loc)][5].clear()
                self.groupBox_dic[str(self.gb_loc)][6].clear()

                self.add_del_stock_hide()
                self.add_del_list[self.gb_loc].setText("+")

    def push_now_stock(self, gb_loc, company_name):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        idx = self.stock_name_list.index(company_name)
        choice_stock_symbol = self.stock_symbol_list[idx]

        updown, changeprice, plusminus, changerate = self.get_change_price(choice_stock_symbol)

        if plusminus == '+':
            clr = 'red'
        elif plusminus == '-':
            clr = 'blue'

        self.groupBox_dic[str(gb_loc)][1].setText(company_name)
        self.groupBox_dic[str(gb_loc)][2].setText(choice_stock_symbol)
        self.groupBox_dic[str(gb_loc)][3].setText(self.get_price(choice_stock_symbol))
        self.groupBox_dic[str(gb_loc)][3].setStyleSheet("Color : %s" % clr)

        self.yesterday_list[gb_loc].show()
        self.up_down_image(plusminus, gb_loc)
        self.groupBox_dic[str(gb_loc)][5].setText(changeprice)
        self.groupBox_dic[str(gb_loc)][5].setStyleSheet("Color : %s" % clr)
        self.groupBox_dic[str(gb_loc)][6].setText("(" + plusminus + changerate + "%)")
        self.groupBox_dic[str(gb_loc)][6].setStyleSheet("Color : %s" % clr)

        self.choice_stock_list[gb_loc][0] = company_name
        self.choice_stock_list[gb_loc][1] = choice_stock_symbol

        now = datetime.datetime.now(timezone('Asia/Seoul'))
        self.update.setText("마지막 업데이트 : %s년 %s월 %s일 %s시 %s분 %s초 기준" %(now.year, now.month, now.day, now.hour, now.minute, now.second))
        QApplication.restoreOverrideCursor()

    def up_down_image(self, pm, loc):
        if pm =='+':
            pixmap = QPixmap("up_red.png")
        elif pm == '-':
            pixmap = QPixmap("down_blue.png")

        pixmap = pixmap.scaled(50, 40, aspectRatioMode=True)
        self.groupBox_dic[str(loc)][4].setPixmap(QPixmap(pixmap))


    def get_bs_obj(self, company_code):
        url = 'https://finance.naver.com/item/main.nhn?code=' + company_code
        result = requests.get(url)
        bs_obj = BeautifulSoup(result.content, "html.parser")  # url의 전체 소스코드 받아온 것
        return bs_obj

    # return : 실시간 주가
    def get_price(self, company_code):
        bs_obj = self.get_bs_obj(company_code)
        no_today = bs_obj.find("p", {"class": "no_today"})
        blind_now = no_today.find("span", {"class": "blind"})
        return blind_now.text

    # return : 상승or하강, 금액, (+)or(-), 비율
    def get_change_price(self, company_code):
        bs_obj = self.get_bs_obj(company_code)
        p = bs_obj.find("p", {"class": "no_exday"})
        ems = p.findAll("em")
        first_span = ems[0].findAll("span")
        second_span = ems[1].findAll("span")

        # 상승or하강
        up_or_down = first_span[0]

        # 금액
        amount = first_span[1]

        # (+)or(-)
        plus_or_minus = second_span[0]

        # 비율
        ratio = second_span[1]

        return up_or_down.text, amount.text, plus_or_minus.text, ratio.text

    # return : per, eps
    def get_per_eps_data(self, company_code):
        bs_obj = self.get_bs_obj(company_code)

        table = bs_obj.find("table", {"class": "per_table"})
        tbody = table.find("tbody")
        tr = tbody.find("tr")
        td = tr.find("td")
        ems = td.findAll("em")
        return ems[0].text, ems[1].text

    # return : 동종업종 per
    def get_similar_company_per_data(self, company_code):
        bs_obj = self.get_bs_obj(company_code)
        table = bs_obj.find("table", {"summary": "동일업종 PER 정보"})
        tr = table.find("tr", {"class": "strong"})
        td = tr.find("td")
        return td.text

    def pricejump_section(self):
        pj_idx = self.df[self.df['diff_magnificant'] > 2].index
        self.pricejump_table.setRowCount(len(pj_idx))
        pj_sort_list = sorted(pj_idx, key=lambda x: self.df.loc[x, 'diff_magnificant'], reverse=True)

        for i in range(len(pj_sort_list)):
            qTableWidgetItemVar_name = QTableWidgetItem(self.df.loc[pj_sort_list[i], 'Name'])
            qTableWidgetItemVar_magni = QTableWidgetItem(str('%0.2f' % (self.df.loc[pj_sort_list[i], 'diff_magnificant']))+' 배')
            self.pricejump_table.setItem(i, 0, qTableWidgetItemVar_name)
            self.pricejump_table.setItem(i, 1, qTableWidgetItemVar_magni)

    def volumejump_section(self):
        vj_idx = self.df[self.df['vol_magnificant'] > 5].index
        self.volumejump_table.setRowCount(len(vj_idx))
        vj_sort_list = sorted(vj_idx, key=lambda x: self.df.loc[x, 'vol_magnificant'], reverse=True)

        for i in range(len(vj_sort_list)):
            qTableWidgetItemVar_name = QTableWidgetItem(self.df.loc[vj_sort_list[i], 'Name'])
            qTableWidgetItemVar_magni = QTableWidgetItem(str('%0.2f' % (self.df.loc[vj_sort_list[i], 'vol_magnificant']))+' 배')
            self.volumejump_table.setItem(i, 0, qTableWidgetItemVar_name)
            self.volumejump_table.setItem(i, 1, qTableWidgetItemVar_magni)

    def combobox_show(self):
        if self.recom_check_1.isChecked():
            self.recom_cb_1.show()
        else:
            self.recom_cb_1.hide()
        if self.recom_check_2.isChecked():
            self.recom_cb_2.show()
        else:
            self.recom_cb_2.hide()
        if self.recom_check_3.isChecked():
            self.recom_cb_3.show()
        else:
            self.recom_cb_3.hide()
        if self.recom_check_4.isChecked():
            self.recom_cb_4.show()
        else:
            self.recom_cb_4.hide()

    def score_calc(self):
        for combobox in self.combobox_list:
            combobox.hide()

        for checkbox in self.checkbox_list:
            checkbox.hide()

        self.recom_table.show()
        self.recom_button.hide()
        self.recom_button_2.show()

        ma_score = self.df['standard_MA_score'] * int(self.recom_cb_1.currentText())
        per_score = self.df['standard_PER_score'] * int(self.recom_cb_2.currentText())
        diff_score = self.df['standard_diff_score'] * int(self.recom_cb_3.currentText())
        vol_score = self.df['standard_vol_score'] * int(self.recom_cb_4.currentText())

        score = ma_score + per_score + diff_score + vol_score
        score_df = pd.DataFrame()
        score_df['Name'] = self.df['Name']
        score_df['score'] = score

        sort_score_df = score_df.sort_values(by=['score'], axis=0, ascending=False)
        sort_score_df['Index'] = range(0, len(sort_score_df))
        sort_score_df.set_index('Index', inplace=True)

        for i in range(0, 10):
            qTableWidgetItemVar_name = QTableWidgetItem(sort_score_df.loc[i, 'Name'])
            qTableWidgetItemVar_score = QTableWidgetItem(str('%0.2f' % (sort_score_df.loc[i, 'score'])))
            self.recom_table.setItem(i, 0, qTableWidgetItemVar_name)
            self.recom_table.setItem(i, 1, qTableWidgetItemVar_score)

    def back_to_choice(self):
        self.recom_table.hide()
        self.recom_button_2.hide()
        self.recom_button.show()

        for checkbox in self.checkbox_list:
            checkbox.show()

        for combobox in self.combobox_list:
            combobox.clear()
            for i in range(0, 11):
                combobox.addItem(str(i))

        self.combobox_show()

app = QApplication(sys.argv)
myWindow = Mainwindow(None)
myWindow.show()
app.exec_()