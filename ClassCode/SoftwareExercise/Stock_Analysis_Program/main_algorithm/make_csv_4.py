import pandas as pd
import numpy as np
import os
import glob

data = pd.read_csv("C:\software_exercise\Stock_Analysis_Program\data\company_info_per.csv")
dir = 'C:\software_exercise\Stock_Analysis_Program\data\csv'
files = []
for file in glob.glob(os.path.join(dir, '*.csv')):
    files.append(file)

ma_score_list = []
for stock in files:
    df = pd.read_csv(stock)
    ma_score = (df.loc[df.index[-1], 'MA20'] - df.loc[df.index[-1], 'MA60']) / df.loc[df.index[-1], 'MA60']
    ma_score_list.append(ma_score)

data['MA_score'] = ma_score_list

data['PER_score'] = (data['similar_PER'] - data['PER']) / data['similar_PER']

data['standard_MA_score'] = data['MA_score'] - data['MA_score'].min() / (data['MA_score'].max() - data['MA_score'].min())
data['standard_PER_score'] = data['PER_score'] - data['PER_score'].min() / (data['PER_score'].max() - data['PER_score'].min())
data['standard_diff_score'] = data['diff_magnificant'] - data['diff_magnificant'].min() / (data['diff_magnificant'].max() - data['diff_magnificant'].min())
data['standard_vol_score'] = data['vol_magnificant'] - data['vol_magnificant'].min() / (data['vol_magnificant'].max() - data['vol_magnificant'].min())

data = data.fillna(0)

data.to_csv("C:\software_exercise\Stock_Analysis_Program\data\company_info_per_ma.csv")



