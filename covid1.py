import json
import os
import requests
import sqlite3
import datetime

'''
This is a function that creates a table in the database titled 'Covid' with columns Date, Positives, Negatives, and Deaths - all type 
INTEGER.
'''
def create_covid_table(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Covid (Date INTEGER, Positives INTEGER, Negatives INTEGER, Deaths INTEGER)')
    conn.commit()
    return cur, conn

'''
This is a function that creates the API request URL. The API url is formatted in 'https://api.covidtracking.com/v1/us/{}.json'
where the date changes for each call. The date must be in the integer format eg. 20200311.
'''
def create_request_url(date):
    base_url = 'https://api.covidtracking.com'
    request_url = base_url + '/v1/us/{}.json'.format(date) #date must be in integer format eg. 20200311
    return request_url

'''
This is a function that retrieves the data from the API and json and adds the data to the database finalproj.db.
Call create_request_url with the date parameter and set it to a variable url.
Then check if the date exists in the database already to account for duplicates in the database by using a SELECT statement with the date
If that SELECT statement fetches something, then the data already exists in the database, so return 0.
Else, use a try and except statement to retrieve data from the API. The try succeeds when the API JSON data are retrieved and loaded into
json_results. The except happens when there is an error grabbing data from the API and returns None, exiting the function.
If we are still within the function (meaning the data retrieval succeeds) then we set the data's variables to our variables.
Then insert the data into the Covid table and return 1.
'''
def get_add_data(cur, conn, date):
    url = create_request_url(date)
    cur.execute("SELECT * FROM Covid WHERE Covid.Date = ?", (date, ))
    conn.commit()
    check = cur.fetchone() #checks if the date/data exists in the database first to account for duplicates
    conn.commit()
    if check != None: #if the date already exists
        print(date, 'already exists')
        return 0 #returns false when data is already in database
    else:
        try:
            response = requests.get(url) #gets data from the json from API
            json_results = json.loads(response.text) 
        except:
            print("Exception")
            return None #returns none when there is an error grabbing data from API
        date = json_results['date']
        positives = json_results['positive']
        negatives = json_results['negative']
        deaths = json_results['death']
        print(json_results) #prints out dictionary of our data
        cur.execute('INSERT INTO Covid (Date, Positives, Negatives, Deaths) VALUES (?,?,?,?)', (date, positives, negatives, deaths))
        conn.commit() 
        return 1 #returns true when data is inserted into database

'''
This is the main function. 
Set up the database with the SQLite3 Connection.
Create the Covid table. 
The datetime module allows us to work with time objects with the right formatting.
Start the data collection from March 11, 2020. End the data collection on November 25, 2020.
Delta represents a change of 1 day.
Set the current_date (date that we collect data on) to start_date
Loop through the dates between start and end date
the_date is a variable of the date in a format compatible with the API call format
Call get_add_data, and if the data retrieval and addition is successful (returns 1)...
Increment the count. (initialized to be 0)
If count exceeds 25, then break and exit the loop to limit the data collection to 25 dates/rows at a time.
Increment the current_date with delta (1 day)
'''
def main():

    #sets up the database with SQLite3 connection
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/finalproj.db')
    cur = conn.cursor()

    create_covid_table(cur, conn) #creates Covid table in db

    count = 0
    start_date = datetime.date(2020,3,11) #start data collection from March 11, 2020
    end_date = datetime.date(2020,11,25) #end data collection on November 25, 2020
    delta = datetime.timedelta(days=1)
    current_date = start_date
    while current_date <= end_date: #loops through all dates between start and end date
        the_date = int(current_date.strftime("%Y%m%d")) #formats the date to be compatible with API call format (integer value)
        conn = sqlite3.connect(path+'/finalproj.db')
        cur = conn.cursor()
        if get_add_data(cur, conn, the_date) == 1: #performs the get_add_data function, and if the insertion is successful...
            count += 1 #increments the number of times get_add_data runs and gets data for each date
            if count >= 25: #limits data collection to 25 dates/rows at a time before breaking and exiting the loop
                break
        current_date += delta #increments time in datetime object
        

if __name__ == "__main__":
    main()