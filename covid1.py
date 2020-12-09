import json
import os
import requests
import sqlite3
import datetime
import matplotlib.pyplot as plt

'''
This is a function that creates a table in the database titled 'Covid' with columns Date, Positives, PositiveInc, Negatives, and Deaths - all type 
INTEGER.
'''
def create_covid_table(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Covid (Date DATE, Positives INTEGER, PositiveInc INTEGER, Negatives INTEGER, Deaths INTEGER)')
    conn.commit()
    return cur, conn

'''
This is a function that creates a table in the database titled 'Hospitalized' with columns Date, Hospitalized, HospitalizedInc, ICU, and Ventilator - all type 
INTEGER.
'''
def create_hospitalized_table(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Hospitalized (Date DATE, Hospitalized INTEGER, HospitalizedInc INTEGER, ICU INTEGER, Ventilator INTEGER)')
    conn.commit()
    return cur, conn

'''
This is a function that creates the API request URL. The API url is formatted in 'https://api.covidtracking.com/v1/us/{}.json'
where the date changes for each call. The date must be in the integer format eg. 20200311.
'''
def create_request_url(date):
    base_url = 'https://api.covidtracking.com'
    request_url = base_url + '/v1/us/{}.json'.format(date.strftime('%Y%m%d')) #date must be in integer format eg. 20200311
    return request_url

'''
This is a function that retrieves the data from the API and json and adds the data to the database finalproj.db.
Call create_request_url with the date parameter and set it to a variable url.
Then check if the date exists in the database already to account for duplicates in the database before even grabbing data from API by using a SELECT statement with the date
If that SELECT statement fetches something, then the data already exists in the database, so return 0.
Else, use a try and except statement to retrieve data from the API. The try succeeds when the API JSON data are retrieved and loaded into
json_results. The except happens when there is an error grabbing data from the API and returns None, exiting the function.
If we are still within the function (meaning the data retrieval succeeds) then we set the data's variables to our variables.
Then insert the data into the Covid table and return 1.
'''
def get_add_data(cur, conn, date):
    url = create_request_url(date)
    cur.execute("SELECT * FROM Covid WHERE Covid.Date = ?", (date.strftime('%Y-%m-%d'), ))
    conn.commit()
    check = cur.fetchone() 
    conn.commit()
    if check != None: 
        print(date, 'already exists')
        return 0 #returns false when data is already in database
    else:
        try:
            response = requests.get(url) #gets data from the json from API
            json_results = json.loads(response.text) 
        except:
            print("Exception")
            return None #returns none when there is an error grabbing data from API
        date = datetime.datetime.strptime(str(json_results['date']), '%Y%m%d')
        positives = json_results['positive']
        positiveinc = json_results['positiveIncrease']
        negatives = json_results['negative']
        deaths = json_results['death']
        hospitalized = json_results['hospitalizedCurrently']
        hospitalizedinc = json_results['hospitalizedIncrease']
        icu = json_results['inIcuCurrently']
        ventilator = json_results['onVentilatorCurrently']

        print(json_results) #prints out dictionary of our data
        cur.execute('INSERT INTO Covid (Date, Positives, PositiveInc, Negatives, Deaths) VALUES (?,?,?,?,?)', (date.strftime('%Y-%m-%d'), positives, positiveinc, negatives, deaths))
        conn.commit()
        cur.execute('INSERT INTO Hospitalized (Date, Hospitalized, HospitalizedInc, ICU, Ventilator) VALUES (?,?,?,?,?)', (date.strftime('%Y-%m-%d'), hospitalized, hospitalizedinc, icu, ventilator))
        conn.commit()
        return 1 #returns true when data is inserted into database

'''
This function joins the Covid and Hospitalized tables together, and performs sum calculations on the
increases in COVID-19 cases and increases in hospitalizations. Returns data on these calculations.
'''
def jointables(cur, conn):
    cur.execute("SELECT strftime('%m', c.Date) as Month, sum(c.PositiveInc), sum(h.HospitalizedInc) FROM Covid c INNER JOIN Hospitalized h ON c.Date = h.Date GROUP BY Month") 
    conn.commit()
    data = cur.fetchall()
    #print(data)
    return data

'''
This function creates a file from the passed data made from the jointables function, called 'calculations'.
'''
def createcalcfile(data):
    calclist = []
    for d in data:
        calcdict = {}
        calcdict['month'] = d[0]
        calcdict['Total Positive Cases'] = d[1]
        calcdict['Total Hospitalizations'] = d[2]
        calclist.append(calcdict)
    print(calclist)

    full_path = os.path.join(os.path.dirname(__file__), 'calculations.txt')
    f = open(full_path, 'w', encoding ='utf-8')
    json.dump(calclist, f)
    f.close()

'''
This is a function that uses matplotlib to create two visualizations:
a bar graph of total COVID-19 cases per month in the US; and a bar graph of total hospitalizations per month in the US.
First, create lists for months, positive cases, and hospitalizations using the passed data from the calculated data in database.
Initialize two plots, and pass through lists in corresponding plot axes, and label title and axes. Graph.
'''
def visualization(data):
    month_list = []
    pos_list = []
    hos_list = []
    for month in data:
        month_list.append(month[0])
        pos_list.append((month[1] or 0)/1e6)
        hos_list.append((month[2] or 0)/1e6)

    fig = plt.figure(figsize = (16, 8))
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    ax1.bar(month_list, pos_list, color='red')
    ax1.set_title('Total Positive COVID-19 Cases per Month in US')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Number of Positive Cases (millions)')

    ax2.bar(month_list, hos_list, color='red')
    ax2.set_title('Total Hospitalizations per Month in US')
    ax2.set_xlabel('Month')
    ax2.set_ylabel('Number of Hospitalizations (millions)')
    
    plt.show()

'''
This is the main function. 
Set up the database with the SQLite3 Connection.
Create the Covid table. 
The datetime module allows us to work with time objects with the right formatting.
Start the data collection from February 1, 2020. End the data collection on December 6, 2020.
Delta represents a change of 1 day.
Set the current_date (date that we collect data on) to start_date
Loop through the dates between start and end date
the_date is a variable of the date in a format compatible with the API call format
Call get_add_data, and if the data retrieval and addition is successful (returns 1)...
Increment the count. (initialized to be 0)
If count exceeds 25, then break and exit the loop to limit the data collection to 25 dates/rows at a time.
Increment the current_date with delta (1 day).
Call the createcalcfile function to create a file of our calculations.
Call the visualization function to create 2 plots.
'''
def main():

    #sets up the database with SQLite3 connection
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/finalproj.db')
    cur = conn.cursor()

    create_covid_table(cur, conn) #creates Covid table in db
    create_hospitalized_table(cur, conn)

    count = 0
    start_date = datetime.date(2020,2,1) #start data collection from March 11, 2020
    end_date = datetime.date(2020,12,6) #end data collection on December 5, 2020
    delta = datetime.timedelta(days=1)
    current_date = start_date
    while current_date <= end_date: #loops through all dates between start and end date
        # can delete the_date = int(current_date.strftime("%Y%m%d")) #formats the date to be compatible with API call format (integer value)
        conn = sqlite3.connect(path+'/finalproj.db')
        cur = conn.cursor()
        if get_add_data(cur, conn, current_date) == 1: #performs the get_add_data function, and if the insertion is successful...
            count += 1 #increments the number of times get_add_data runs for each date
            if count >= 25: #limits data collection to 25 dates/rows at a time before breaking and exiting the loop
                break
        current_date += delta #increments time in datetime object

    createcalcfile(jointables(cur,conn))
    visualization(jointables(cur,conn))
    
        

if __name__ == "__main__":
    main()