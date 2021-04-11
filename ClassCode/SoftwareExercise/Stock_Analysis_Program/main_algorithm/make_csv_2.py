import FinanceDataReader as fdr
import pandas as pd
import datetime
import numpy as np

data = pd.read_csv("C:\software_exercise\Stock_Analysis_Program\data\Pick_stock_list.csv")
name_list = data['Name'].tolist()
symbol_list = data['Symbol'].tolist()

def make_diff_avg_std(company_code):
    # 주가 급등 종목 관련 데이터 수집
    df = fdr.DataReader(company_code, datetime.datetime.now() - datetime.timedelta(days=32))[['Close', 'Volume']]

    diff_list = []
    for i in range(1, len(df.index) - 1):
        diff_list.append(df.loc[df.index[i], 'Close'] - df.loc[df.index[i-1], 'Close'])
    diff_np = np.array(diff_list)

    diff_std = diff_np.std()

    diff_target = df.loc[df.index[-1], 'Close'] - df.loc[df.index[-2], 'Close']

    # 거래량 급등 종목 관련 데이터 수집
    vol_avg = df.loc[:df.index[-1] - datetime.timedelta(days=1), 'Volume'].mean()
    vol_target = df.loc[df.index[-1], 'Volume']

    return [diff_std, diff_target, vol_avg, vol_target]

total_diff_list = []
for symbol in symbol_list:
    total_diff_list.append(make_diff_avg_std(symbol))
    print(symbol)

total_diff_np = np.array(total_diff_list)

data['diff_std'] = total_diff_np[:, 0]
data['diff_target'] = total_diff_np[:, 1]
data['diff_magnificant'] = data['diff_target'] / data['diff_std']
data['vol_avg'] = total_diff_np[:, 2]
data['vol_target'] = total_diff_np[:, 3]
data['vol_magnificant'] = data['vol_target'] / data['vol_avg']

data.to_csv("C:\software_exercise\Stock_Analysis_Program\data\company_info.csv")

