import requests
from bs4 import BeautifulSoup

def get_bs_obj(company_code):
    url = 'https://finance.naver.com/item/main.nhn?code=' + company_code
    result = requests.get(url)
    bs_obj = BeautifulSoup(result.content, "html.parser") # url의 전체 소스코드 받아온 것
    return bs_obj


# return : 실시간 주가
def get_price(company_code):
    bs_obj = get_bs_obj(company_code)
    no_today = bs_obj.find("p", {"class": "no_today"})
    blind_now = no_today.find("span", {"class": "blind"})
    return blind_now.text


# return : 전일(종가), 고가, 거래량, 시가, 저가, 거래대금
def get_candle_chart_data(company_code):
    bs_obj = get_bs_obj(company_code)
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


# return : 상승or하강, 금액, (+)or(-), 비율
def get_change_price(company_code):
    bs_obj = get_bs_obj(company_code)
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
def get_per_eps_data(company_code):
    bs_obj = get_bs_obj(company_code)

    table = bs_obj.find("table", {"class": "per_table"})
    tbody = table.find("tbody")
    tr = tbody.find("tr")
    td = tr.find("td")
    ems = td.findAll("em")
    return ems[0].text, ems[1].text


# return : 동종업종 per
def get_similar_company_per_data(company_code):
    bs_obj = get_bs_obj(company_code)
    table = bs_obj.find("table", {"summary": "동일업종 PER 정보"})
    tr = table.find("tr", {"class": "strong"})
    em = tr.find("em")
    return em.text

#sk하이닉스 000660
# print(get_price("000660"))
# print(get_candle_chart_data("000660"))
# print(get_per_eps_data("317530")[0])
# print(get_similar_company_per_data("317530"))
print(get_change_price("005930"))

