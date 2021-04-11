import FinanceDataReader as fdr
import pandas as pd

data = pd.read_csv("C:\software_exercise\Stock_Analysis_Program\data\Pick_stock_list.csv")
name_list = data['Name'].tolist()
symbol_list = data['Symbol'].tolist()

def make_csv(company_name, company_code):
    df = fdr.DataReader(company_code, '2020-01-01')

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

for i in range(len(name_list)):
    make_csv(name_list[i], symbol_list[i])


