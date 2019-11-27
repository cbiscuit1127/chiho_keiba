import requests
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib.parse import parse_qs
from bs4 import BeautifulSoup
from main2 import race_info

url = 'http://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/DebaTable'
query = {'k_raceDate': '2019/04/09', 'k_raceNo': 1, 'k_babaCode': 20}
r = requests.get(url, params=query)
r.encoding = r.apparent_encoding
soup = BeautifulSoup(r.text, 'lxml')
horse_name_tags = soup.select('a.horseName')
# 馬ごとにレース履歴を取得
for horse_name_tag in horse_name_tags:
    horse_link = urljoin(url, horse_name_tag['href'])
    r = requests.get(horse_link)
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, 'lxml')
    horse_result_link_tags = soup.select('.dbdata3')
    for horse_result_link_tag in horse_result_link_tags:
        try:
            horse_result_link = urljoin(url, horse_result_link_tag.a['href'])
            query = parse_qs(urlparse(horse_result_link).query)
            print(query)
        except:
            pass
