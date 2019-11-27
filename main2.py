from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from urllib.parse import parse_qs
import csv
import os
import re
import sqlite3
from tqdm import tqdm

con = sqlite3.connect('nar.db')
cur = con.cursor()

def kaisai_get(year, month):
    url = 'http://www2.keiba.go.jp/KeibaWeb/MonthlyConveneInfo/MonthlyConveneInfoTop'
    query = {'k_year': year, 'k_month': month}
    r = requests.get(url, params=query)
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, 'lxml')
    link_tags = soup.select('a.day')
    links = list(map(lambda x: x['href'], link_tags))
    queries = list(map(lambda x: parse_qs(urlparse(x).query), links))

    '''
    with sqlite3.connect('nar.db') as con:
        cur = con.cursor()
    '''

    # 開催情報を日別・場所別開催情報テーブルに追加
    '''
    for query in queries:
        raceDate = query['k_raceDate'][0]
        babaCode = query['k_babaCode'][0]
        sql = 'select * from kaisai where raceDate=? and babaCode=?'
        cur.execute(sql, [raceDate, babaCode])
        kaisai_exists = len(cur.fetchall()) > 0
        if kaisai_exists:
            sql = 'insert into kaisai values(?, ?)'
            con.execute(sql, [raceDate, babaCode])
    else:
        con.commit()
    '''

    return queries

'''
payload = {'k_raceDate': ~~~, 'k_babaCode': ~~~, ('k_raceNo': ~~~)}
'''
def extract_url(a_tag):
    try:
        return a_tag['href']
    except KeyError:
        return None

def races(payload):
    url = 'http://www2.keiba.go.jp/KeibaWeb/TodayRaceInfo/RaceList'
    r = requests.get(url, params=payload)
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, 'lxml')
    link_tags = soup.find_all('a', text='成績')
    links = list(map(extract_url, link_tags))
    links = list(filter(lambda x: x != None, links))
    queries = list(map(lambda x: parse_qs(urlparse(x).query), links))
    return queries

# year/month/date/babaCode/ なるディレクトリ構造を生成する関数
def dirs(payload):
    dir_path = payload['k_raceDate'][0] + '/' + payload['k_babaCode'][0]
    os.makedirs(dir_path, exist_ok=True)

def bs_obj(payload):
    url = 'http://www2.keiba.go.jp/KeibaWeb/TodayRaceInfo/RaceMarkTable'
    r = requests.get(url, params=payload)
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, 'lxml')
    return soup

'''payload = {'k_raceDate': ~~~, 'k_babaCode': ~~~, ('k_raceNo': ~~~)}'''
def race_info(payload):
    url = 'http://www2.keiba.go.jp/KeibaWeb/TodayRaceInfo/RaceMarkTable'
    r = requests.get(url, params=payload)
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, 'lxml')

    header1 = soup.select('.plus1bold01')[0].parent.text

    # トラック区分
    try:
        track = re.search('(芝|ダート)', header1).group()
    except:
        track = 'ばんえい'

    # 距離
    distance = re.search('(\d+)ｍ', header1).group(1)

    # 天候
    weather_tag = soup.find(text=re.compile('天候：.+\u3000'))
    weather = re.search('天候：(.+)\u3000', weather_tag).group(1)

    # 馬場状態
    try:
        track_condition = re.search('(良|稍重|重|不良)', header1).group()
    except:
        track_condition = re.search('\d+\.\d', header1).group()

    header2 = soup.select('.plus1bold02')[0]
    # レース名
    race_name = header2.text
    # 競走条件
    race_condition = re.search('（(.*)）', header2.parent.parent.contents[-1]).group(1)#バグ修正済だがやや危険か

    # 上がり
    try:
        agari = soup.find('td', text=re.compile('上り')).text
        try:
            agari3 = re.search('3F[^0-9]+(\d+\.\d).+\n', agari).group(1)
        except:
            agari3 = '0.0'
        try:
            agari4 = re.search('4F[^0-9]+(\d+\.\d).+\n', agari).group(1)
        except:
            agari4 = '0.0'
    except:
        agari = ''
        agari3 = '0.0'
        agari4 = '0.0'

    # ハロンタイム
    try:
        furlong_tag = soup.find(text=re.compile('ハロンタイム')).parent.text
        furlong = re.search('(\d+\.\d(- )?)+', furlong_tag).group()
    except:
        furlong = ''

    # コーナー通過順
    try:
        corners = soup.find(text=re.compile('コーナー通過順')).parent.text.replace('\n\n\n', '|')
    except:
        corners = ''

    return [race_name, race_condition, track, distance, weather, track_condition, agari4, agari3, furlong, corners]

def corner_parser(corners):
    if len(corners):
        list_ = corners.split('|')[1:]
        result = list(map(lambda x: x.strip(), list_))
    else:
        result = []
    return result

def dbtbl(payload):
    url = 'http://www2.keiba.go.jp/KeibaWeb/TodayRaceInfo/RaceMarkTable'
    r = requests.get(url, params=payload)
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, 'lxml')
    dbtbl = soup.select('.dbtbl')
    return dbtbl

'''↓'''
def race_details(dbtbl):
    tree = list(map(lambda x: x.find_all('td'), dbtbl.find_all('tr')))
    result = []
    for i in tree:
        try:
            rank = i[0].text
            wakuban = i[1].text
            umaban = i[2].text
            horse_name = i[3].text.strip()
            horse_id = parse_qs(urlparse(i[3].a['href']).query)['k_lineageLoginCode'][0].strip()
            belong = i[4].text
            sex_and_age = i[5].text.replace(' ', '')
            handicap = i[6].text
            jockey_id = parse_qs(urlparse(i[7].a['href']).query)['k_riderLicenseNo'][0]
            trainer_id = parse_qs(urlparse(i[8].a['href']).query)['k_trainerLicenseNo'][0]
            weight = i[9].text
            weight_change = i[10].text
            time = i[11].text.strip()
            margin = i[12].text
            last_3f = i[13].text
            # TODO: jockey_id, trainer_id と名前の紐付け

            row = [rank, wakuban, umaban, horse_name, horse_id, belong, \
            sex_and_age, handicap, jockey_id, trainer_id, weight, \
            weight_change, time, margin, last_3f]
            result.append(row)
        except:
            pass
    return result

def payouts(dbtbl):
    tree = list(map(lambda x: x.find_all('td'), dbtbl.find_all('tr')))
    types = tree[1]
    details = tree[3]
    result = []
    for i in range(1, len(types)):
        type = types[i].text
        combination = details[3*i-2].contents
        payout = details[3*i-1].contents
        if len(combination) > 2:
            br_tag = combination[1]
            combination = list(filter(lambda x: x != br_tag, combination))
            payout = list(filter(lambda x: x != br_tag, payout))
            for j in range(len(combination)):
                row = [type, combination[j].strip(), payout[j].strip().replace(',', '')]
                result.append(row)
        else:
            combination = combination[0]
            payout = payout[0]
            row = [type, combination.strip(), payout.strip().replace(',', '')]
            result.append(row)
    else:
        return result

if __name__ == '__main__':
    for year in range(2011, 2020):
        for month in range(1, 13):
            kaisai_list = kaisai_get(year, month)
            pbar = tqdm(total=len(kaisai_list))
            print()
            for kaisai in kaisai_list:
                race_list = races(kaisai)
                for race in race_list:
                    race_header = race['k_raceDate'] + race['k_babaCode'] + race['k_raceNo']
                    cur.execute('select * from race_info where raceDate=? and babaCode=? and raceNo=?', race_header)
                    if len(cur.fetchall()) == 0:
                        rinfo = race_info(race)
                        sql = 'insert into race_info values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
                        con.execute(sql, race_header + rinfo)

                        dbtbl_ = dbtbl(race)
                        details = race_details(dbtbl_[0])
                        for detail in details:
                            sql = 'insert into horse_result values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
                            con.execute(sql, race_header + detail)

                        payouts_ = payouts(dbtbl_[1])
                        for payout in payouts_:
                            sql = 'insert into payout values(?, ?, ?, ?, ?, ?)'
                            con.execute(sql, race_header + payout)
                con.commit()
                pbar.update(1)
            pbar.close()
