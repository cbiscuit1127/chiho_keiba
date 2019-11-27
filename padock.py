import datetime as dt
import requests
from bs4 import BeautifulSoup
import re
import sqlite3
import sys

url = 'http://www.keiba.go.jp/KeibaWeb/TodayRaceInfo/DebaTable'
args = sys.argv
k_raceDate = dt.datetime.today().strftime('%Y/%m/%d')
try:
    k_babaCode = args[1]
except:
    k_babaCode = input('babaCode:')
try:
    k_raceNo = args[2]
except:
    k_raceNo = input('raceNo: ')
payload = {'k_raceDate': k_raceDate, 'k_babaCode': k_babaCode, 'k_raceNo': k_raceNo}
r = requests.get(url, params=payload)
r.encoding = r.apparent_encoding
soup = BeautifulSoup(r.text, 'lxml')

horse_list = []
horses = soup.select('a.horseName')
con = sqlite3.connect('nar.db')
cur = con.cursor()
for num, horse in enumerate(horses):
    horse_id = re.search('\d{11}', horse['href']).group()
    cur.execute('select comment from padock where raceDate=? and babaCode=? and raceNo=? and horse_id=?', [k_raceDate, k_babaCode, k_raceNo, horse_id])
    existing_record = cur.fetchall()
    if existing_record:
        existing_comment = existing_record[0][0]
    else:
        existing_comment = ''
    horse_list.append([num+1, horse_id, horse.text, existing_comment])
    print(num+1, horse.text, existing_comment)

while True:
    try:
        wakuban = int(input('wakuban: '))
        if wakuban-1 not in range(len(horse_list)):
            break
    except:
        break
    comment = input('comment: ')
    horse_list[wakuban-1][3] += ' ' + comment + ' ' #TODO: list.join(', ')で置き換え
print(horse_list)

for horse in horse_list:
    cur.execute('select * from padock where raceDate=? and babaCode=? and raceNo=? and horse_id=?', [k_raceDate, k_babaCode, k_raceNo, horse[1]])
    existing_record = cur.fetchall()
    if existing_record:
        sql = 'update padock set comment=? where raceDate=? and babaCode=? and raceNo=? and horse_id=?'
        payload = [horse[3], k_raceDate, k_babaCode, k_raceNo, horse[1]]
    else:
        sql = 'insert into padock values(?, ?, ?, ?, ?)'
        payload = [k_raceDate, k_babaCode, k_raceNo, horse[1], horse[3]]
    con.execute(sql, payload)
else:
    con.commit()
    con.close()
