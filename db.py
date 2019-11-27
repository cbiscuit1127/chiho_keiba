import sqlite3
import csv

def db_initialize():
    with sqlite3.connect('nar.db') as con:
        # 日別・場所別開催情報テーブル
        con.execute('drop table if exists kaisai')
        con.execute('create table kaisai (raceDate, babaCode)')

        # レース情報テーブル
        con.execute('drop table if exists race_info')
        con.execute('create table race_info (raceDate, babaCode, raceNo, race_name, race_condition, track, distance, weather, track_condition, agari4, agari3, furlong, corners)')

        # 競走成績テーブル
        con.execute('drop table if exists horse_result')
        con.execute('create table horse_result (raceDate, babaCode, raceNo, rank, wakuban, umaban, horse_name, horse_id, belong, sex_and_age, handicap, jockey_id, trainer_id, weight, weight_change, time, margin, last_3f)')

        # 払戻しテーブル
        con.execute('drop table if exists payout')
        con.execute('create table payout (raceDate, babaCode, raceNo, type, combination, payout)')

        # 騎手・調教師情報テーブル
        con.execute('drop table if exists code')
        con.execute('create table code (type, id, name)')

        # パドックテーブル
        con.execute('drop table if exists padock')
        con.execute('create table padock (raceDate, babaCode, raceNo, horse_id, comment)')

        con.commit()

def babaCode_initialize():
    with open('babaCode.csv', 'r', encoding='utf-8') as f:
        list_ = []
        reader = csv.reader(f)
        for i in reader:
            list_.append(i)
    with sqlite3.connect('nar.db') as con:
        sql = 'delete from code where type="babaCode"'
        con.execute(sql)
        for i in list_:
            sql = 'insert into code values(?, ?, ?)'
            payload = ['babaCode'] + i
            con.execute(sql, payload)
        else:
            con.commit()

if __name__ == '__main__':
    db_initialize()
    babaCode_initialize()
