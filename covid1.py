import json
import os
import requests
import sqlite3
import datetime

def create_covid_table(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Covid (Date INTEGER, Positives INTEGER, Negatives INTEGER, Deaths INTEGER)')
    conn.commit()
    return cur, conn

def create_request_url(date):
    base_url = 'https://api.covidtracking.com'
    request_url = base_url + '/v1/us/{}.json'.format(date)
    return request_url

def get_add_data(cur, conn, date):
    url = create_request_url(date)
    cur.execute("SELECT * FROM Covid WHERE Covid.Date = ?", (date, ))
    conn.commit()
    check = cur.fetchone()
    conn.commit()
    if check != None:
        print(date, 'already exists')
        return 0 #returns false when data is already in database
    else:
        try:
            response = requests.get(url)
            json_results = json.loads(response.text)   
        except:
            print("Exception")
            return None #returns none when there is an error grabbing data from API
        date = json_results['date']
        positives = json_results['positive']
        negatives = json_results['negative']
        deaths = json_results['death']
        print(json_results)
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
'''
def main():

    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/finalproj.db')
    cur = conn.cursor()
    create_covid_table(cur, conn)
    # cur.close()
    # conn.close()
    #testing just one date,
    #get_add_data(cur, conn, 20200201)
    #add_data_to_db(20200201, cur, conn)
    #date_list = [(datetime.date(2020,3,11), datetime.date(2020,3,25)), (datetime.data(2020,3,26), (datetime.data(2020,4,11))]
    #for dates in date_list[run]:

    count = 0
    start_date = datetime.date(2020,3,11)
    end_date = datetime.date(2020,11,25)
    delta = datetime.timedelta(days=1)
    current_date = start_date
    while current_date <= end_date:
        # count = 0
        # while count < 25:
            # get the data from the website
            # count += 1
        # write to the sql db
        # if count >= 24:
        #     break
        the_date = int(current_date.strftime("%Y%m%d"))
        conn = sqlite3.connect(path+'/finalproj.db')
        cur = conn.cursor()
        if get_add_data(cur, conn, the_date) == 1:
            #print(count)
            count += 1
            if count >= 25:
                break
        # cur.close()
        # conn.close()
        current_date += delta #increments time in datetime object
        

if __name__ == "__main__":
    main()