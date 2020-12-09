import json
import unittest
import os
import requests
import sqlite3
import matplotlib
import matplotlib.pyplot as plt 
import csv 
from matplotlib.ticker import PercentFormatter

# documentation, 25 limits, write caluculations to a file, change the sql file name 
api_key = "989b7d0dacf40d04a9e654615aa9cafe"

def request_url(company_name):
    """
    This function formats and returns the url which
    helps extract the information about of comanies' revenues
    """

    url = "https://financialmodelingprep.com/api/v3/income-statement/{}?period=quarter&limit=3&apikey=989b7d0dacf40d04a9e654615aa9cafe"
    final_url = url.format(company_name)
    return final_url 


def get_etf_company(etf): 
    """
    This function formats and returns a list of companies 
    in the etf index 
    """
    result = [] 
    url = "https://financialmodelingprep.com/api/v3/etf-holder/{}?apikey=989b7d0dacf40d04a9e654615aa9cafe"
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
    
def setupDatabase(file_name):
    """
    This function directs the path file and 
    sets up the databse for sql
    """
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+ file_name)
    cur = conn.cursor()
    return cur, conn


def setupIncomeDataTable(company_list, cur, conn):
    """This function first creates a IncomeData table, which is the table storing 
    all the information. Next, it will extract inforamtion and insert these information 
    to the table 25 companies each time
    """
    cur.execute('CREATE TABLE IF NOT EXISTS IncomeData (company_name TEXT PRIMARY KEY, grossProfitRatio_quarter_1 REAL, grossProfitRatio_quarter_2 REAL, grossProfitRatio_quarter_3 REAL )')
    cur.execute('SELECT company_name FROM IncomeData')
    company_exist = cur.fetchall()
    #Check whether the there are 100 rows in sql database 
    if len(company_exist) < 100: 
        count = 0 
        for company in company_list:
            #Limit the request and insert times to 25 
            if company not in company_exist and count < 25:
                try:
                    url = request_url(company)
                    r = requests.get(url)
                    k = json.loads(r.text)   
                    cur.execute('INSERT INTO IncomeData (company_name, grossProfitRatio_quarter_1, grossProfitRatio_quarter_2, grossProfitRatio_quarter_3) VALUES (?,?,?,?)', (company, k[2]['grossProfitRatio'], k[1]['grossProfitRatio'], k[0]['grossProfitRatio']))
                    print("Insert Data for " + company)
                    conn.commit() 
                    count = count + 1 
                except:
                    print("Companies exists")
    #If the data base has already have 100 data, request and insert the rest of the data to the databse
    else: 
        for company in company_list:
            if company not in company_exist:
                    try:
                        url = request_url(company)
                        r = requests.get(url)
                        k = json.loads(r.text)   
                        cur.execute('INSERT INTO IncomeData (company_name, grossProfitRatio_quarter_1, grossProfitRatio_quarter_2, grossProfitRatio_quarter_3) VALUES (?,?,?,?)', (company, k[2]['grossProfitRatio'], k[1]['grossProfitRatio'], k[0]['grossProfitRatio']))
                        print("Insert Data for " + company)
                        conn.commit() 
                    except:
                        print("Companies exists")
                
def dataCalculation(cur, conn):
    """
    When the database has more than 100 data rows, this
    function extract some of the data from the databse 
    and calculate the difference between two quarters 
    for each company. Then write the calculating results to 
    a file
    """
    cur.execute('SELECT company_name FROM IncomeData')
    company_exist = cur.fetchall()
    #number = len(company_exist)

    #Only when the database has more than 100 data, it will start to calculate and write the results to a file 
    #if number < 101: 
    #    return None, None 

    #else: 
    result_1 = [] 
    result_2 = []  
    file_result = [] 
    title = ['Difference between Quarter 1 and Quarter 2', 'Difference between Quarter 2 and Quarter 3']
    cur.execute('SELECT grossProfitRatio_quarter_1, grossProfitRatio_quarter_2, grossProfitRatio_quarter_3 FROM IncomeData')
    for row in cur:
            if (row[0] != 0 and row[1] != 0 and row[2] != 0) and (row[0] != 1 and row[1] != 1 and row[2] != 1):
                diff_1 = row[1] - row[0] #The difference between quarter 1 and quarter 2
                diff_2 = row[2] - row[1] #The difference between quarter 2 and quarter 3 
                file_list = [] 
                result_1.append(diff_1)  
                result_2.append(diff_2)
                file_list.append(diff_1)  #Append calculation results to temporary list 
                file_list.append(diff_2)  #Append calculation results to temporary list
                file_result.append(file_list) #Append the temporary list to the result list 

    full_path = os.path.join(os.path.dirname(__file__), 'calculations_revenueDiff.csv')
    f = open(full_path, 'w', newline='', encoding ='utf-8')
    title = ['Difference between Quarter 1 and Quarter 2', 'Difference between Quarter 2 and Quarter 3']
    csvwriter = csv.writer(f)
    csvwriter.writerow(title)
    csvwriter.writerows(file_result) #Write the result list to a csv file 
    f.close() 
    return result_1, result_2 


def visualization(data_1, data_2):
    """
    This function visualizes the calculating results 
    in a histogram
    """
    fig = plt.figure(figsize=(10,5))
    fig.suptitle('Gross Profit Ratio Changes during Covid-19 period')
    fig_1 = fig.add_subplot(121)
    fig_2 = fig.add_subplot(122) 
    fig_1.hist(data_1, range=[-1,1], color='red',  bins=20, edgecolor = 'black')
    fig_2.hist(data_2, range=[-1,1], color='red', bins=20, edgecolor = 'black')
    fig_1.set_xlabel('Change from March to June')
    fig_1.set_ylabel('Percentage')
    fig_2.set_xlabel('Change from June to September')
    fig_2.set_ylabel('Percentage')
    fig_1.yaxis.set_major_formatter(PercentFormatter(xmax=len(data_1))) 
    fig_2.yaxis.set_major_formatter(PercentFormatter(xmax=len(data_2)))
    fig.savefig('Revenue_Change.png')
    plt.show() 
    

def main(): 
    eft = "SPY"  #"SPY" refers to S&P 500 Index, which have approximately 500 companies representing U.S economy
    company_names = get_etf_company(eft) #Get the comapny names of SPY in a list
    cur, conn = setupDatabase('finalproj.db') 
    setupIncomeDataTable(company_names, cur, conn) #Get the infomration for 25 companies if database has less than 100 rows and insert them to the databse 
    visualization_data_1, visualization_data_2 = dataCalculation(cur,conn) #Calculate the data from the databse 
    conn.close() 
    #Only when the database has more than 100 data, it will return the calculation result 
    #Otherwise, it will return two Nones 
    if visualization_data_1 != None and visualization_data_2 != None: 
        visualization(visualization_data_1, visualization_data_2) #Visualize the data from the calculations 

    

if __name__ == "__main__":
    main()

