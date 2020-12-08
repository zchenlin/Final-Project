import json
import unittest
import os
import requests
import sqlite3
import matplotlib
import matplotlib.pyplot as plt 

api_key = "aa22fc25508e6ebea46f7992e6395391"

def request_url(company_name):
    url = "https://financialmodelingprep.com/api/v3/income-statement/{}?period=quarter&limit=2&apikey=a9cab2ec0ba9cc37205ce27eaa565bbb"
    final_url = url.format(company_name)
    return final_url 

def get_etf_company(etf): 
    result = [] 
    url = "https://financialmodelingprep.com/api/v3/etf-holder/{}?apikey=a9cab2ec0ba9cc37205ce27eaa565bbb"
    final_url = url.format(etf)
    r = requests.get(final_url)
    try:
        k = json.loads(r.text) 
        for i in k: 
            if i["asset"] != None :
                result.append(i["asset"])  
        return result 
    except:
        print("Error")
        return None 
    
    
def get_data_json(company_name):
    url = request_url(company_name)
    r = requests.get(url)
    k = json.loads(r.text)  
#    print(k)
    try:  
        info = {} 
        info["grossProfit_quarter_1"] = k[0]['grossProfitRatio']
        info["grossProfit_quarter_2"] = k[1]['grossProfitRatio']
        return info 
    except:
        print("Error")
        return None 

def setupDatabase(file_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+ file_name)
    cur = conn.cursor()
    return cur, conn

"""def setupCompanyTable(company_list, cur, conn):
    id = 1
    cur.execute('DROP TABLE IF EXISTS Companies')
    cur.execute('CREATE TABLE Companies (company_id INTEGER PRIMARY KEY, name TEXT)') 
    for company in company_list:
        comapny_id = id 
        name = company 
        cur.execute("INSERT INTO Companies (company_id, name) VALUES (?,?)", (comapny_id, name)) 
        id = id + 1 
        conn.commit()"""


def setupIncomeDataTable(json_data, company_list, cur, conn):
    cur.execute('DROP TABLE IF EXISTS IncomeData')
    cur.execute('CREATE TABLE IncomeData (company_name TEXT PRIMARY KEY, grossProfitRatio_quarter_1 REAL, grossProfitRatio_quarter_2 REAL )')
    for company in company_list: 
        ratio_1 = json_data[company]['grossProfit_quarter_1']
        ratio_2 = json_data[company]['grossProfit_quarter_2']
        cur.execute('INSERT INTO IncomeData (company_name, grossProfitRatio_quarter_1, grossProfitRatio_quarter_2) VALUES (?,?,?)', (company, ratio_1, ratio_2))
        conn.commit() 

def dataCalculation(cur, conn):
    result = [] 
    cur.execute('SELECT grossProfitRatio_quarter_1, grossProfitRatio_quarter_2 FROM IncomeData')
    for row in cur:
        diff = row[0] - row[1] 
        result.append(diff)
    return result 

def visualization(data):
    plt.hist(data, range=[-1,1], density=1, bins=20, edgecolor = 'black')
    plt.xlabel('GrossProfitRatio Difference')
    plt.ylabel('Probability')
    plt.show() 
        
def main(): 
    final_data = {}
    eft = "SPY"
    company_names = get_etf_company(eft)
    for company_name in company_names: 
        a = get_data_json(company_name)
        if a != None:
            final_data[company_name] = a
    final_data_keys = final_data.keys()
    cur, conn = setupDatabase('Companies.db')
    setupIncomeDataTable(final_data, final_data_keys, cur, conn)
    visualization_data = dataCalculation(cur,conn)
    conn.close() 
    visualization(visualization_data)

    
 

    


if __name__ == "__main__":
    main()

