import FinanceDataReader as fdr
import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime
import numpy as np
import os
import glob
import matplotlib.pyplot as plt
from statsmodels.tsa.arima_model import ARMA

# 전체 업데이트 =

# 기업 csv 업데이트 = 클래스.execute_make_company_csv()
# company_info 업데이트(diff, vol 데이터까지) = 클래스.add_diff_vol_data()
# company_info_per 업데이트(per까지) = 클래스.add_per_data()
# company_info_per_score 업데이트(score까지) = 클래스.add_score()
class DataCollect:
    def __init__(self):
        # 기업명, 분야, 종목번호 데이터 불러오기
        self.stock_data = pd.read_csv("C:\software_exercise\Stock_Analysis_Program\data\Pick_stock_list.csv")
        self.name_list = self.stock_data['Name'].tolist()
        self.symbol_list = self.stock_data['Symbol'].tolist()

        # 각 기업별 데이터 경로 리스트로 만들어 놓기
        self.dir = 'C:\software_exercise\Stock_Analysis_Program\data\csv'
        self.files = []                                                     # 각 기업별 csv 파일 경로
        for file in glob.glob(os.path.join(self.dir, '*.csv')):
            self.files.append(file)

        # company_info 데이터 불러오기
        self.company_info = pd.read_csv("C:\software_exercise\Stock_Analysis_Program\data\company_info.csv")

        # company_info_per 데이터 불러오기
        self.company_info_per = pd.read_csv("C:\software_exercise\Stock_Analysis_Program\data\company_info_per.csv")

        # company_info_per_score 데이터 불러오기
        self.company_info_per_score = pd.read_csv("C:\software_exercise\Stock_Analysis_Program\data\company_info_per_score.csv")

    # 원하는 시점 이후의 stock_data에 들어있는 기업들의 주가 데이터 csv로 저장
    def make_company_csv(self, company_name, company_code, date): # date = '2020-01-01'
        df = fdr.DataReader(company_code, date)

        df['Index'] = list(range(0, len(df)))
        df['Date'] = df.index.tolist()
        df.set_index('Index', inplace=True)
        df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Change']]

        # 이동평균선 넣기 (MA20, MA60)
        ma20 = df['Close'].rolling(window=20).mean()
        ma60 = df['Close'].rolling(window=60).mean()

        df['MA20'] = ma20
        df['MA60'] = ma60

        direct = "C:\software_exercise\Stock_Analysis_Program\data\csv\\" + company_name + '_' + company_code + '.csv'
        df.to_csv(direct)

    # 기업 주가데이터 생성 실행
    def execute_make_company_csv(self, date): # date = '2020-01-01'
        for i in range(len(self.name_list)):
            self.make_company_csv(self.name_list[i], self.symbol_list[i], date)

    def make_diff_vol_data(self, company_code):
        company_idx = self.symbol_list.index(company_code)
        data = pd.read_csv(self.files[company_idx])

        try:
            df = data.loc[data.index[-32]:, ['Close', 'Volume']]
        except:
            df = data.loc[:, ['Close', 'Volume']]

        # 주가 급등 종목 관련 데이터 수집
        diff_list = []
        for i in range(1, len(df) - 1):
            diff_list.append(df.loc[df.index[i], 'Close'] - df.loc[df.index[i - 1], 'Close'])

        diff_std = df.loc[:df.index[-1], 'Close'].std()
        diff_target = df.loc[df.index[-1], 'Close'] - df.loc[df.index[-2], 'Close']

        # 거래량 급등 종목 관련 데이터 수집
        vol_avg = df.loc[:df.index[-1], 'Volume'].mean()
        vol_target = df.loc[df.index[-1], 'Volume']

        return [diff_std, diff_target, vol_avg, vol_target]

    # self.stock_data에 diff, vol 관련 데이터 넣기
    def add_diff_vol_data(self):
        total_diff_list = []
        for symbol in self.symbol_list:
            total_diff_list.append(self.make_diff_vol_data(symbol))
            print(symbol)

        total_diff_np = np.array(total_diff_list)

        self.stock_data['diff_std'] = total_diff_np[:, 0]
        self.stock_data['diff_target'] = total_diff_np[:, 1]
        self.stock_data['diff_magnificant'] = self.stock_data['diff_target'] / self.stock_data['diff_std']
        self.stock_data['vol_avg'] = total_diff_np[:, 2]
        self.stock_data['vol_target'] = total_diff_np[:, 3]
        self.stock_data['vol_magnificant'] = self.stock_data['vol_target'] / self.stock_data['vol_avg']

        self.stock_data.to_csv("C:\software_exercise\Stock_Analysis_Program\data\company_info.csv")

    def add_per_data(self):
        # # per 데이터 수집
        per_list = []
        for symbol in self.symbol_list:
            per = self.get_per_eps_data(symbol)[0]

            # 크롤링 데이터 내의 콤마(,) 제거
            if ',' in per:
                per = per.replace(',', '')

            # nan 데이터 0으로 처리 (eps가 음수인 경우, per가 nan으로 나옴)
            try:
                per = float(per)
            except:
                per = 0

            per_list.append(per)

        # 업종평균 per 데이터 수집
        field = self.stock_data['Field'].unique()

        similar_per_dic = dict()
        for val in field:
            _tmp = self.stock_data[self.stock_data['Field'] == val]
            temp_sym = self.stock_data.loc[_tmp.index[0], 'Symbol']
            temp_similar_per = self.get_similar_company_per_data(temp_sym)

            if ',' in temp_similar_per:
                similar_per = float(temp_similar_per.replace(',', ''))

            similar_per_dic[val] = temp_similar_per

        # PER 추가
        self.company_info['PER'] = per_list

        # similar_PER 추가
        self.company_info['similar_PER'] = None
        for key, value in similar_per_dic.items():
            self.company_info.loc[self.company_info['Field'] == key, 'similar_PER'] = value

        self.company_info.to_csv("C:\software_exercise\Stock_Analysis_Program\data\company_info_per.csv")

    def add_score(self):
        data = self.company_info_per

        # MA score 넣기
        ma_score_list = []
        for stock in self.files:
            df = pd.read_csv(stock)
            ma_score = (df.loc[df.index[-1], 'MA20'] - df.loc[df.index[-1], 'MA60']) / df.loc[df.index[-1], 'MA60']
            ma_score_list.append(ma_score)

        data['MA_score'] = ma_score_list

        # PER score 넣기
        data['PER_score'] = (data['similar_PER'] - data['PER']) / data['similar_PER']

        # diff, vol은 앞서 구한 magnificant 그대로 이용

        # 모든 점수들의 표준화 작업 - max, min 이용
        data['standard_MA_score'] = (data['MA_score'] - data['MA_score'].mean()) / data['MA_score'].std()
        data['standard_PER_score'] = (data['PER_score'] - data['PER_score'].mean()) / data['PER_score'].std()
        data['standard_diff_score'] = (data['diff_magnificant'] - data['diff_magnificant'].mean()) / data['diff_magnificant'].std()
        data['standard_vol_score'] = (data['vol_magnificant'] - data['vol_magnificant'].mean()) / data['vol_magnificant'].std()

        data = data.fillna(0)

        data.to_csv("C:\software_exercise\Stock_Analysis_Program\data\company_info_per_score.csv")

    def get_bs_obj(self, company_code):
        url = 'https://finance.naver.com/item/main.nhn?code=' + company_code
        result = requests.get(url)
        bs_obj = BeautifulSoup(result.content, "html.parser")  # url의 전체 소스코드 받아온 것
        return bs_obj

    def get_per_eps_data(self, company_code):
        bs_obj = self.get_bs_obj(company_code)

        table = bs_obj.find("table", {"class": "per_table"})
        tbody = table.find("tbody")
        tr = tbody.find("tr")
        td = tr.find("td")
        ems = td.findAll("em")
        return ems[0].text, ems[1].text

    def get_similar_company_per_data(self, company_code):
        bs_obj = self.get_bs_obj(company_code)
        table = bs_obj.find("table", {"summary": "동일업종 PER 정보"})
        tr = table.find("tr", {"class": "strong"})
        em = tr.find("em")
        return em.text

    def update_all(self, date):
        self.execute_make_company_csv(date)
        self.add_diff_vol_data()
        self.add_per_data()
        self.add_score()

# 전체 업데이트
update = DataCollect()
update.update_all('2020-01-01')

# 부분 업데이트
# update = DataCollect()
# update.execute_make_company_csv('2020-01-01')
# update.add_diff_vol_data()
# update.add_per_data()
# update.add_score()

