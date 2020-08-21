
# Part 1 #######################################################################

import pyodbc

conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=cities;UID=********;PWD=********')

cursor = conn.cursor()

try:
    cursor.execute('create table usa ( city nvarchar(50), state nvarchar(50))')
    conn.commit()
except:
    print("Cities database was already initialized. Moving on...")

# Part 2 #######################################################################

import PyPDF2 as pydf

pdf = open('/home/anmol/Public/WebScrape/500-cities-listed-by-state.pdf', 'rb')
reader = pydf.PdfFileReader(pdf)

text = ''
for page in reader.pages:
    if reader.getPageNumber(page) < 12:
        page_lines = page.extractText().split('\n')[4:-3]
    else:
        page_lines = page.extractText().split('\n')[4:-8]
    for line in page_lines:
        if not line[0].isdigit():
            name = line
            if any((character.isdigit() or character == "'") for character in name):
                done = False
                for charID in range(len(name)):
                    if done:
                        done = False
                        continue
                    if name[charID].isdigit():
                        name = name[:charID] + '\n'
                        break
                    if name[charID] == "'":
                        name = name[:charID] + "\'\'" + name[charID + 1:]
                        done = True
            text += name + '\n'
        else:
            text += '\n'

lines = text.split('\n')
cities = []
states, state = [], None
for index in range(len(lines)):
    if lines[index] != '' and lines[index + 1] != '':
        state = lines[index]
    elif lines[index] != '':
        cities.append(lines[index])
        states.append(state)

command = "insert into usa(city, state) values "
for i in range(len(cities)):
    command += "('" + cities[i] + "','" + states[i] + "')"
    if i != len(cities) - 1:
        command += ','

cursor.execute("select count(*) from usa;")
items = cursor.fetchone()[0]

if items == 0:
    cursor.execute(command)
    conn.commit()
else:
    print("Cities Database for the USA seems to have already been uploaded.")
    print("If you think something is wrong with the database, please do:")
    print("run 'drop table usa' in sqlcmd program, & run this program again.")
    print("\n\n")

# Part 3 #######################################################################

'''Need to access Google Sheets where all the links are'''

# Part 4 #######################################################################

from selenium import webdriver
from bs4 import BeautifulSoup
import time, sys

url = 'https://recruiting2.ultipro.com/SAM1001SFG/JobBoard/59c82705-8c95-46e8-b791-861d75ac197d/'

options = webdriver.ChromeOptions()
options.add_argument('headless')
browser = webdriver.Chrome(options=options)
browser.get(url)
time.sleep(0.2)
html = browser.page_source

sp = BeautifulSoup(html, 'html.parser')

def exiting():
    browser.close()
    sys.exit()

if 'greenhouse' in url.lower():
    sections = sp.findAll('section')
    for section_tag in sections:
        for h_n_jobdiv in section_tag.children:
            if h_n_jobdiv.name == 'section' or h_n_jobdiv.name == None:
                continue
            #elif 'h' in h_n_jobdiv.name:
                #print('\t\t\t' + h_n_jobdiv.string)
            elif h_n_jobdiv.name == 'div':
                title = h_n_jobdiv.a.string
                link = '/'.join(url.split('/')[0:-1]) + h_n_jobdiv.a.get('href')
                loc = h_n_jobdiv.span.string
                #print(title, link, loc)

        if section_tag == sections[-1]:
            continue
        #print('\n')

if 'ultipro' in url.lower():
    sections = sp.findAll('div', class_='opportunity')
    print(len(sections), "job opportunities:\n")
    for opp in sections:
        t_n_l = opp.find_all('a')[0]
        title = t_n_l.string
        link = '/'.join(url.split('/')[0:3]) + t_n_l.get('href')
        loc = opp.find_all(attrs = {'data-bind' : 'text: Address().CityStatePostalCodeAndCountry()'})[0].string
        #print(title, link, loc)
        print(title, loc)
        more_locs = opp.find('small', attrs = {'data-automation' : 'job-location-more'})
        if more_locs.string != "+0 more":
            print("\t" + more_locs.string + " locations for this job")
            browser.get(link)
            #time.sleep(0.1)
            jl = BeautifulSoup(browser.page_source, 'html.parser')
            jl_locs = list(dict.fromkeys(jl.find_all(attrs = {'data-bind' : 'text: Address().CityStatePostalCodeAndCountry()'})))
            for new_place in jl_locs[1:]:
                print("More Places:", new_place.string)
        print('\n\n\n')

browser.close()
