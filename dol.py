import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import json
from datetime import datetime
from datetime import date
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.ticker import MaxNLocator
from selenium import webdriver
import csv
from selenium.webdriver.support.ui import Select

driver = webdriver.Chrome()

'''
The get_data function extracts data on weekly initial unemployment claims since 1967 from the Department of Labor website. It requires a database cursor and connector as well as a url as parameters. The function uses Selenium and ChromeDriver to automatically set parameters for the request (namely, the start year) and submit the request form in order to access the webpage with the data. It then reads values from the webpage starting with the most recent ones and stores them in the unemployment_dict dictionary. That dictionary is ultimately returned by the function. The first four executions of the code are limited to just 25 values, and the fifth execution extracts all the remaining values from the webpage at once.
'''
def get_data(url, cur, conn):
    driver.get(url)
    ddelement = Select(driver.find_element_by_xpath('//*[@id="content"]/table/tbody/tr[2]/td/select'))
    ddelement.select_by_value('1967')
    sub_button = driver.find_element_by_xpath('/html/body/div/div[2]/div[2]/table/tbody/tr[6]/td/input').click()
    page_content = driver.page_source
    driver.close()
    soup = BeautifulSoup(page_content, 'html.parser')
    table = soup.find('table')
    rows = list(reversed(table.find_all('tr')))

    unemployment_dict = {}

    for row in rows[21:-3]:
        date_in_row = row.find('th').text
        formatted_date = datetime.strptime(date_in_row, '%m/%d/%Y').date()
        if check_unemployment_table(cur, conn, formatted_date) == True:
            if check_table_size(cur, conn) == False:
                header_string = date_in_row + ' nsa_initial_claims'
                row_value = row.find('td', headers = header_string).text
                unemployment_dict[formatted_date] = int(row_value.replace(",", ""))
                if len(unemployment_dict) >= 25:
                    break
            else:
                header_string = date_in_row + ' nsa_initial_claims'
                row_value = row.find('td', headers = header_string).text
                unemployment_dict[formatted_date] = int(row_value.replace(",", ""))
        else:
            continue
    return unemployment_dict

'''
The create_unemployment_table function takes a database cursor and connector as parameters and creates a table where unemployment data is stored. It does not return anything.
'''
def create_unemployment_table(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Unemployment (Date DATE, WeeklyInitialClaims INTEGER)')
    conn.commit()

'''
The check_unemployment_table function takes a database cursor and connector as well as a date as parameters. It checks whether the specified date already exists in the database. It returns True if the date is in the database and False otherwise.
'''
def check_unemployment_table(cur, conn, date):
    cur.execute('SELECT * FROM Unemployment WHERE (Unemployment.Date = ?)', (date, ))
    conn.commit()
    check = cur.fetchone()
    conn.commit()
    if check != None:
        #print(date, 'already exists')
        return False
    else:
        return True

'''
The check_table_size function takes a database cursor and connector as parameters. It checks if the table has reached 100 items in which case it returns True. Otherwise, the function returns False.
'''
def check_table_size(cur, conn):
    cur.execute('SELECT * FROM Unemployment')
    collected_data = cur.fetchall()
    if len(collected_data) == 100:
        return True
    else:
        return False

'''
The populate_unemployment_table function takes a database cursor and connector as well as a dictionary as parameters. It then fills the Unemployment table in the database with values from the dictionary. It does not return anything.
'''
def populate_unemployment_table(cur, conn, data):
    for date in data:
        cur.execute('INSERT INTO Unemployment (Date, WeeklyInitialClaims) VALUES (?, ?)', (date, data[date]))
    conn.commit()

'''
The write_calculations function takes a database cursor and connector as parameters. First, it extracts data from the specified database table and calculates the total number of items as well as the average of the values in different years. Then, the function creates a file (calcUnemployment) in the same directory and writes the results of the calculations (averages of values in different years).
'''
def write_calculations(cur, conn):
    cur.execute('SELECT * FROM Unemployment')
    collected_data = cur.fetchall()
    collected_dates = []
    date_value_dict = {}
    collected_years = []
    for date in collected_data:
        collected_dates.append(datetime.strptime(date[0], '%Y-%m-%d').date())
        date_value_dict[datetime.strptime(date[0], '%Y-%m-%d').date()] = date[1]
        year_in_date = datetime.strptime(date[0], '%Y-%m-%d').year
        if year_in_date not in collected_years:
            collected_years.append(year_in_date)

    year_sum_dictionary = {}
    year_all_claims = {}
    for year in collected_years:
        this_years_dict = []
        for date1 in collected_dates:
            if date1.year == year:
                year_sum_dictionary[year] = year_sum_dictionary.get(year, 0) + date_value_dict[date1]
                this_years_dict.append(date_value_dict[date1])
        year_all_claims[year] = this_years_dict

    year_average_dict = {}
    for year1 in collected_years:
        year_avg = sum(year_all_claims[year1]) / len(year_all_claims[year1])
        year_average_dict[year1] = int(year_avg)

    full_path = os.path.join(os.path.dirname(__file__), 'calcUnemployment.csv')
    dir = os.path.dirname(__file__)
    outFile = open(os.path.join(dir, 'calcUnemployment.csv'), 'w')
    csv_writer = csv.writer(outFile, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
    title = ['Year', 'Average Number of Claims per Week']
    csv_writer.writerow(title)
    for year_row in year_average_dict:
        csv_writer.writerow([year_row, year_average_dict[year_row]])
    outFile.close()

'''
The visualization function takes a database cursor and connector as parameters. First, it extracts data from the specified database table and calculates the total number of items as well as the average of the values in different years. The function creates two visualizations: a line graph depicting weekly unemployment claims and a bar chart showing the average number of claims per week in the years for which data has been collected.
'''
def visualization(cur, conn):

    cur.execute('SELECT * FROM Unemployment')
    collected_data = cur.fetchall()
    collected_dates = []
    collected_values = []
    date_value_dict = {}
    collected_years = []
    for date in collected_data:
        collected_dates.append(datetime.strptime(date[0], '%Y-%m-%d').date())
        collected_values.append(date[1])
        date_value_dict[datetime.strptime(date[0], '%Y-%m-%d').date()] = date[1]
        year_in_date = datetime.strptime(date[0], '%Y-%m-%d').year
        if year_in_date not in collected_years:
            collected_years.append(year_in_date)

    # calculations for the second visualization
    year_sum_dictionary = {}
    year_all_claims = {}
    for year in collected_years:
        this_years_dict = []
        for date1 in collected_dates:
            if date1.year == year:
                year_sum_dictionary[year] = year_sum_dictionary.get(year, 0) + date_value_dict[date1]
                this_years_dict.append(date_value_dict[date1])
        year_all_claims[year] = this_years_dict

    year_average_dict = {}
    for year1 in collected_years:
        year_avg = sum(year_all_claims[year1]) / len(year_all_claims[year1])
        year_average_dict[year1] = int(year_avg)

    fig = plt.figure(figsize = (16, 8))
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    ax1.plot(collected_dates, collected_values, color = 'red')
    ax1.set_title('Weekly Unemployment Insurance Claims')
    ax1.set_xlabel('Report Date')
    ax1.set_ylabel('Weekly Initial Claims')
    ax1.grid(True)

    ax2.bar(collected_years, list(year_average_dict.values()), color = 'red')
    ax2.set_title('Average Number of Claims per Week')
    ax2.set_ylabel('Weekly Initial Claims')
    ax2.set_xlabel('Year')
    ax2.set_xlim(collected_years[-1]-1, collected_years[0]+1)
    ax2.ticklabel_format(useOffset=False)
    #ax2.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
    ax2.xaxis.set_major_locator(MaxNLocator(integer = True))
    #ax2.set_xticks(collected_years)
    fig.savefig('double_dol.png')

    plt.show()

def main():
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/finalproj.db')
    cur = conn.cursor()
    create_unemployment_table(cur, conn)

    url = 'https://oui.doleta.gov/unemploy/claims.asp'
    data = get_data(url, cur, conn)

    populate_unemployment_table(cur, conn, data)

    visualization(cur, conn)

    write_calculations(cur, conn)

    conn.close()

if __name__ == "__main__":
    main()
