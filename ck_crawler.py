# coding = UTF-8
import sys
import requests
from bs4 import BeautifulSoup, element

# request ck101.com 需要模擬瀏覽器
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

def get_novel_title():

	# info_list 儲存小說資訊
	info_list = []

	# 結果
	res = ""

		# 讀取小說資料，並搜尋有無更新
	with open("ck_list.txt", "r", encoding = "utf8") as novels:
		for novel in novels:
			info = novel.split()
			if len(info) < 4:
				info.append("")

			# request 取得網站
			url = 'https://ck101.com/thread-' + info[0] + '-' + info[2] + '-1.html'
			response = requests.get(url, headers=headers)
			pageSource = response.text.encode(sys.stdin.encoding, "replace").decode(sys.stdin.encoding)

			# beautifulsoup 處理
			soup = BeautifulSoup(pageSource, "html.parser")
			# 先找到目前最新的那篇，再往後查詢是否有後面的章節
			if info[3]:
				articles = soup.find("td",  class_ = "t_f", id = info[3]).find_all_next("td",  class_ = "t_f")
			else:
				articles = soup.find("div", id = "postlist").find_all_next("td",  class_ = "t_f")

			# 取得後面章節名稱，並將章節id存為最新
			title_list = ""
			for article in articles:			
				info[3] = article["id"]

				# 取得章節名稱，章節名前面有可能出現 \n，章節名也可能會被包在很多Tag之內
				i = 0
				while article.contents[i] == '\n':
					i += 1
				title = article.contents[i]

				# 一層一層找下去直到拿到章節名
				while type(title) == element.Tag:
					title = title.contents[0]
				title_list += title.strip() + "\n"

			# 若有下一頁按鈕，則繼續搜尋下一頁
			while soup.find("div", id = "pgt").find("a", class_ = "nxt"):
				info[2] = str(int(info[2]) + 1)
				url = 'https://ck101.com/thread-' + info[0] + '-' + info[2] + '-1.html'
				response = requests.get(url, headers=headers)
				pageSource = response.text.encode(sys.stdin.encoding, "replace").decode(sys.stdin.encoding)
				soup = BeautifulSoup(pageSource, "html.parser")
				articles = soup.find("div", id = "postlist").find_all_next("td",  class_ = "t_f")
				for article in articles:			
					info[3] = article["id"]
					# 取得章節名稱，章節名前面有可能出現 \n，章節名也可能會被包在很多Tag之內
					i = 0
					while article.contents[i] == '\n':
						i += 1
					title = article.contents[i]

					# 一層一層找下去直到拿到章節名
					while type(title) == element.Tag:
						title = title.contents[0]
					title_list += title.strip() + "\n"

			if title_list != "":
				res += "---" + info[1] + "---\n" + title_list 

			info_list.append(info)

	with open("ck_list.txt", "w", encoding = "utf8") as novels:
		for info in info_list:
			novels.write(info[0] + " " + info[1] + " " + info[2] + " " + info[3] + "\n")

	if res != "":
		print(res)
	return res

if __name__ == '__main__':
	get_novel_title()
