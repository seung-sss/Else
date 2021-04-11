import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

data = pd.read_csv("C:\software_exercise\Stock_Analysis_Program\data\Pick_stock_list.csv")
name_list = data['Name'].tolist()
symbol_list = data['Symbol'].tolist()

df = pd.read_csv("C:\software_exercise\Stock_Analysis_Program\data\company_info.csv")

def get_bs_obj(company_code):
    url = 'https://finance.naver.com/item/main.nhn?code=' + company_code
    result = requests.get(url)
    bs_obj = BeautifulSoup(result.content, "html.parser")  # url의 전체 소스코드 받아온 것
    return bs_obj

def get_per_eps_data(company_code):
    bs_obj = get_bs_obj(company_code)

    table = bs_obj.find("table", {"class": "per_table"})
    tbody = table.find("tbody")
    tr = tbody.find("tr")
    td = tr.find("td")
    ems = td.findAll("em")
    return ems[0].text, ems[1].text

def get_similar_company_per_data(company_code):
    bs_obj = get_bs_obj(company_code)
    table = bs_obj.find("table", {"summary": "동일업종 PER 정보"})
    tr = table.find("tr", {"class": "strong"})
    em = tr.find("em")
    return em.text

per_list = []

for symbol in symbol_list:
    per = get_per_eps_data(symbol)[0]

    if ',' in per:
        per = per.replace(',', '')

    try:
        per = float(per)
    except:
        per = 0

    similar_per = get_similar_company_per_data(symbol)

    if ',' in similar_per:
        similar_per = float(similar_per.replace(',', ''))

    per_list.append([per, similar_per])

    print(symbol, per, similar_per)

per_np = np.array(per_list)

df['PER'] = per_np[:, 0]
df['similar_PER'] = per_np[:, 1]

df.to_csv("C:\software_exercise\Stock_Analysis_Program\data\company_info_per.csv")