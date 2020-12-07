import requests
from bs4 import BeautifulSoup
import sqlite3
import os
from datetime import datetime
from datetime import date
import matplotlib.pyplot as plt
from selenium import webdriver
from selenium.webdriver.support.ui import Select

driver = webdriver.Chrome()

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

def create_unemployment_table(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Unemployment (Date DATE, WeeklyInitialClaims INTEGER)')
    conn.commit()

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

def check_table_size(cur, conn):
    cur.execute('SELECT * FROM Unemployment')
    collected_data = cur.fetchall()
    if len(collected_data) == 100:
        return True
    else:
        return False

def populate_unemployment_table(cur, conn, data):
    for date in data:
        cur.execute('INSERT INTO Unemployment (Date, WeeklyInitialClaims) VALUES (?, ?)', (date, data[date]))
    conn.commit()

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

    # create two charts
    if len(collected_data) >= 100:

        fig = plt.figure(figsize = (16, 8))
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)

        ax1.plot(collected_dates, collected_values)
        ax1.set_title('Weekly Unemployment Insurance Claims')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Initial Claims')
        ax1.grid(True)

        ax2.bar(collected_years, list(year_average_dict.values()))
        ax2.set_title('Average Number of Claims per Week')
        ax2.set_ylabel('Weekly Claims')
        ax2.set_xlabel('Year')

        fig.savefig('double_dol.png')

    # create one graph
    else:
        fig, ax1 = plt.subplots()

        ax1.plot(collected_dates, collected_values)
        ax1.set_title('Weekly Unemployment Insurance Claims')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Initial Claims')
        ax1.grid(True)
        fig.savefig('dol.png')

    plt.show()

def main():
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/dol.db')
    cur = conn.cursor()
    create_unemployment_table(cur, conn)

    url = 'https://oui.doleta.gov/unemploy/claims.asp'
    data = get_data(url, cur, conn)

    populate_unemployment_table(cur, conn, data)

    visualization(cur, conn)

    conn.close()

if __name__ == "__main__":
    main()
