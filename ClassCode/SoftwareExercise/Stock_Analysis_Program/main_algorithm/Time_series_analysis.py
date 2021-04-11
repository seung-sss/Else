import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima_model import ARMA, ARMAResults

# data 불러오기 및 Date부분 datetime으로 변환
data = pd.read_csv("C:\software_exercise\Stock_Analysis_Program\data\csv\DB하이텍_000990.csv")
data.Date = pd.to_datetime(data.Date)

# High부분 뽑기
y = data['Close']

# init부분에 미리 (p,q) 리스트 만들어 놓기
pq = [(0,1), (0,2), (1,0), (1,1), (1,2), (2,0), (2,1), (2,2)]

# return : best_aic, best_pq, best_model
def find_best_pq(y):
    best_aic = np.inf
    best_pq = None
    best_model = None

    for param in pq:
        try:
            temp_model = ARMA(y, order=param)
            res = temp_model.fit()

            if res.aic < best_aic:
                best_aic = res.aic
                best_pq = param
                best_model = temp_model

        except:
            continue

    return best_aic, best_pq, best_model

def make_ts_model(y, pq):
    model = ARMA(y, order = pq)
    result = model.fit()
    fore = result.forecast(steps=1)
    return fore[0], result

best_aic, best_pq, best_model = find_best_pq(y)
fore, res = make_ts_model(y, best_pq)

# plt.plot(y, color='blue', linestyle='--')
res.plot_predict()
plt.show()
print(fore)

