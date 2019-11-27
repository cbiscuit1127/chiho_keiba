import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urlparse
from urllib.parse import parse_qs

# レース番号 発走時刻
# 馬名
# 履歴
# をすべて表示

url = 'http://www.keiba.go.jp/'
r = requests.get(url + '/KeibaWeb/TodayRaceInfo/TopTodayRaceInfoMini')
r.encoding = r.apparent_encoding
soup = BeautifulSoup(r.text, 'lxml')

race_info_today = soup.select('#raceInfoToday')[0]
rows = race_info_today.find_all('tr')
for row in rows:
    place = row.find_all('td')[0].text
    race_list = row.find('a', text='出馬表')['href']
    r = requests.get(url + race_list)
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, 'lxml')
    race_table = soup.select('.raceTable')[0]
    races = race_table.select('tr.data')
    for race in races:
        cols = race.find_all('td')
        race_num = cols[0].text
        hassou_time = cols[1].text
        race_name = cols[4].text
        print(race_num, hassou_time, race_name)

        race_link = cols[4].find('a')['href']
        race_link = race_link.replace('..', 'KeibaWeb')
        r = requests.get(url + race_link)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'lxml')
        horses = soup.select('a.horseName')
        for horse in horses:
            horse_name = horse.text
            print(horse_name)
            horse_link = horse['href']
            horse_link = horse_link.replace('..', 'KeibaWeb')
            r = requests.get(url + horse_link)
            r.encoding = r.apparent_encoding
            soup = BeautifulSoup(r.text, 'lxml')
            db_tbl = soup.select('.dbtbl')[0].table
            db_data = db_tbl.select('tr.dbdata')
            for db_datum in db_data:
                datum_cols = db_datum.find_all('td')
                try:
                    past_race_link = datum_cols[3].a['href']
                    queries = parse_qs(urlparse(past_race_link).query)
                    print(queries)
                except TypeError:
                    print(datum_cols[3])

        race_course = cols[5].text

    live = row.find('a', text='映像')['href']
    browser = webdriver.Chrome()
    browser.get(live)
