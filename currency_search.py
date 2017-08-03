import requests
from bs4 import BeautifulSoup

def yen():
	# 抓日幣資料
	res = requests.get("http://rate.bot.com.tw/xrt?Lang=zh-TW")
	soup = BeautifulSoup(res.text, "html.parser")
	table = soup.find("tbody").find_all("tr")
	tr = table[7]
	if tr.find("div", class_ = "visible-phone print_hide").string.strip() == "日圓 (JPY)":
		cash_buy = tr.find("td", attrs = {"data-table" : "本行現金買入"}).string
		cash_sell = tr.find("td", attrs = {"data-table" : "本行現金賣出"}).string
		sight_buy = tr.find("td", attrs = {"data-table" : "本行即期買入"}).string
		sight_sell = tr.find("td", attrs = {"data-table" : "本行即期賣出"}).string
		return [cash_buy, cash_sell, sight_buy, sight_sell]
	else:
		return []