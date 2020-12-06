import json
import os
import requests
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt

base_url = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
api_key = 'dbf9e0c1a06e4d48b47797e4c537a6c5'

def get_data(series_id, start_year, end_year):
    headers = {'Content-type': 'application/json'}
    data = json.dumps({'seriesid': series_id, 'startyear': start_year, 'endyear': end_year, 'registrationKey': api_key})
    p = requests.post(base_url, data=data, headers=headers)
    json_data = json.loads(p.text)
    return json_data

def create_unemployment_table(cur, conn, lst):
    cur.execute('CREATE TABLE IF NOT EXISTS Unemployment (Month INTEGER PRIMARY KEY, UnemploymentRate REAL)')
    for month in lst:
        cur.execute('INSERT INTO Unemployment (Month, UnemploymentRate) VALUES (?, ?)', (month[0], month[1]))
    conn.commit()

def create_cpi_table(cur, conn, lst):
    cur.execute('CREATE TABLE IF NOT EXISTS CPI (Month INTEGER PRIMARY KEY, CPI REAL)')
    for month in lst:
        cur.execute('INSERT INTO CPI (Month, CPI) VALUES (?, ?)', (month[0], month[1]))
    conn.commit()

def vizualization(lst):
    month_list = []
    value_list = []
    for month in lst:
        month_list.append(month[0])
        value_list.append(month[1])
    plt.bar(range(len(lst)), value_list, align = 'center')
    plt.xticks(range(len(lst)), month_list)
    plt.show()

def main():
    series_id = ['LNS14000000','CUUR0000SA0']
    start_year = '2020'
    end_year = '2020'
    data = get_data(series_id, start_year, end_year)['Results']['series']

    list_unemployment = []
    dict_unemployment = {}
    for period_ur in data[0]['data']:
        dict_unemployment[int(datetime.strptime(period_ur['periodName'], '%B').month)] = float(period_ur['value'])
    list_unemployment = sorted(dict_unemployment.items())
    print(list_unemployment)

    list_cpi = []
    dict_cpi = {}
    for period_cpi in data[1]['data']:
        dict_cpi[int(datetime.strptime(period_cpi['periodName'], '%B').month)] = float(period_cpi['value'])
    list_cpi = sorted(dict_cpi.items())
    print(list_cpi)

    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/bls.db')
    cur = conn.cursor()
    create_unemployment_table(cur, conn, list_unemployment)
    create_cpi_table(cur, conn, list_cpi)
    conn.close()

    vizualization(list_unemployment)
    vizualization(list_cpi)

if __name__ == "__main__":
    main()
