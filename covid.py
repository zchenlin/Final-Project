import json
import os
import requests
import sqlite3
import datetime

def create_covid_table(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Covid (Date INTEGER, Positives INTEGER, Negatives INTEGER, Deaths INTEGER)')
    return cur, conn

def create_request_url(date):
    base_url = 'https://api.covidtracking.com'
    request_url = base_url + '/v1/us/{}.json'.format(date)
    return request_url

def get_add_data(cur, conn, date):
    url = create_request_url(date)
    cur.execute("SELECT * FROM Covid WHERE Covid.Date = ?", (date, ))
    check = cur.fetchone()
    if check != None:
        print(date, 'already exists')
        return 0 #returns false when data is already in database
    else:
        try:
            response = requests.get(url)
            json_results = json.loads(response.text)
            return json_results    
        except:
            print("Exception")
            return None #returns none when there is an error grabbing data from API
        date = json_results['date']
        positives = json_results['positive']
        negatives = json_results['negative']
        deaths = json_results['death']
        cur.execute('INSERT INTO Covid (Date, Positives, Negatives, Deaths) VALUES (?,?,?,?)', (date, positives, negatives, deaths))
        conn.commit()
        return 1 #returns true when data is inserted into database

'''def add_data_to_db(date, cur, conn):
    the_data = get_data(cur, conn, date)
    if the_data != None:
        date = json_results['date']
        positives = json_results['positive']
        negatives = json_results['negative']
        deaths = json_results['death']
        cur.execute('INSERT INTO Covid (Date, Positives, Negatives, Deaths) VALUES (?,?,?,?)', (date, positives, negatives, deaths))
        conn.commit()


def add_run_to_db(runcount, cur, conn):
    runcount = runcount
    cur.execute('INSERT INTO Runs (Runcount) VALUES (?)', (runcount))
    '''

def main():

    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/finalproj.db')
    cur = conn.cursor()
    create_covid_table(cur, conn)
    #testing just one date, none and exception in output :(
    #get_data(cur, conn, 20200201)
    #add_data_to_db(20200201, cur, conn)
    #set variable = 0, stop when variable reaches 25, break,  
    #have 4 different pairs of start and end dates
    #store date pairs into list of tuples, for loop that goes through list

    #runcount = 0
    #date_list = [(datetime.date(2020,3,11), datetime.date(2020,3,25)), (datetime.data(2020,3,26), (datetime.data(2020,4,11))]
    #for dates in date_list[run]:
        #if get_data(cur, conn, the_date) == -1:
         #       continue
    count = 0
    start_date = datetime.date(2020,3,11)
    end_date = datetime.date(2020,11,25)
    delta = datetime.timedelta(days=1)
    current_date = start_date
    while current_date <= end_date:
        if count < 24:
            break
        the_date = int(current_date.strftime("%Y%m%d"))
        if get_add_data(cur, conn, the_date) == 1:
            count += 1
        current_date += delta #increments time in datetime object

if __name__ == "__main__":
    main()
