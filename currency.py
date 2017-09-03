import requests
from bs4 import BeautifulSoup

def get_name():
	cur_list = []
	res = requests.get("http://rate.bot.com.tw/xrt?Lang=zh-TW")
	soup = BeautifulSoup(res.text, "html.parser")
	table = soup.find("tbody").find_all("tr")
	for tr in table:
		text = tr.find("div", class_ = "visible-phone print_hide").string.strip()
		curs = text.split("(")
		for cur in curs:
			cur_list.append(cur[:-1])


def get_currency(curr):
	# 抓匯率資料
	res = requests.get("http://rate.bot.com.tw/xrt?Lang=zh-TW")
	soup = BeautifulSoup(res.text, "html.parser")
	table = soup.find("tbody").find_all("tr")
	for tr in table:
		text = tr.find("div", class_ = "visible-phone print_hide").string.strip()
		if text.find(curr) != -1:
			# cash_buy = tr.find("td", attrs = {"data-table" : "本行現金買入"}).string
			cash_sell = tr.find("td", attrs = {"data-table" : "本行現金賣出"}).string
			# sight_buy = tr.find("td", attrs = {"data-table" : "本行即期買入"}).string
			# sight_sell = tr.find("td", attrs = {"data-table" : "本行即期賣出"}).string
			# info = [cash_buy, cash_sell, sight_buy, sight_sell]
			return cash_sell

if __name__ == '__main__':
	get_name()
