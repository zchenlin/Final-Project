import json
import unittest
import os
import requests
import sqlite3

api_key = "aa22fc25508e6ebea46f7992e6395391"

def request_url(company_name):
    url = "https://financialmodelingprep.com/api/v3/income-statement/{}?period=quarter&limit=3&apikey=7a45eead1c6d464025fc42c7d0a4bf2e"
    final_url = url.format(company_name)
    return final_url 

def get_etf_company(etf): 
    result = [] 
    url = "https://financialmodelingprep.com/api/v3/etf-holder/{}?apikey=7a45eead1c6d464025fc42c7d0a4bf2e"
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
    try: 
        result = []
        for i in k: 
            info = {} 
            info["quarter"] = i["date"]
            info["revenue"] = i["revenue"]
            info['grossProfit'] = i["grossProfit"]
            info['grossProfitRatio'] = i["grossProfitRatio"]
            result.append(info)
        return result 
    except:
        print("Error")
        return None 

def setupDatabase(file_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+ file_name)
    cur = conn.cursor()
    return cur, conn

def setupCompanyTable(company_list, cur, conn):
    id = 1
    cur.execute('DROP TABLE IF EXISTS Companies')
    cur.execute('CREATE TABLE Companies (company_id INTEGER PRIMARY KEY, name TEXT)') 
    for company in company_list:
        comapny_id = id 
        name = company 
        cur.execute("INSERT INTO Companies (company_id, name) VALUES (?,?)", (comapny_id, name)) 
        id = id + 1 
        conn.commit() 


def setupIncomeDataTable(json_data, company_list, cur, conn):
    cur.execute('DROP TABLE IF EXISTS IncomeData')
    cur.execute('CREATE TABLE IncomeData (company_id integer, quarter TEXT, revenue INTEGER, grossProfit INTEGER, grossProfitRatio REAL)')
    number = 1 
    for company in company_list: 
        for data in json_data[company]: 
            cur.execute("SELECT company_id FROM Companies WHERE name = ?", (company,))
            company_id = cur.fetchone()[0] 
            quarter = data['quarter']
            revenue = data['revenue']
            grossProfit = data['grossProfit']
            grossProfitRatio = data['grossProfitRatio']
            cur.execute('INSERT INTO IncomeData (company_id, quarter, revenue, grossProfit, grossProfitRatio) VALUES (?,?,?,?,?)', (company_id, quarter, revenue, grossProfit, grossProfitRatio))
            conn.commit() 
        number = number + 1 
        
         
def main(): 
    count = 0
    final_data = {}
    eft = "XRT"
    company_names = get_etf_company(eft)
    for company_name in company_names: 
        a = get_data_json(company_name)
        final_data[company_name] = a
    json_data = json.dumps(final_data)
    cur, conn = setupDatabase('Companies.db')
    setupCompanyTable(company_names, cur, conn)
    setupIncomeDataTable(final_data, company_names, cur, conn)

    conn.close() 

    
 

    


if __name__ == "__main__":
    main()

