
# Part 1 #######################################################################

import pyodbc

conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=cities;UID=__;PWD=__')

cursor = conn.cursor()

try:
    cursor.execute('create table usa ( city nvarchar(50), state nvarchar(50))')
    conn.commit()
except:
    print("Cities database was already initialized. Moving on...")

# Part 2 #######################################################################

import PyPDF2 as pydf

pdf = open('500-cities-listed-by-state.pdf', 'rb')
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

import pickle, os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
spreadsheet_id = '__'
range_name = '__'
api = '__'

creds = None

if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scope)
        creds = flow.run_local_server(port = 0)
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('sheets', 'v4', credentials=creds)

sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId = spreadsheet_id, range=range_name).execute()
values = result.get('values', [])

job_links = []

if not values:
    print('No data found.')
else:
    print('Compiling and Updating the Job Repository Sources...\n\n\n')
    for row in values:
        job_links.append((row[0], row[2]))

# Part 4 #######################################################################

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time, sys, re, unicodedata

print('I am starting to process the data from the job pages. Please wait a few')
print('moments for me to finish this task...\n\n\n')

options = webdriver.ChromeOptions()
options.add_argument('headless')
browser = webdriver.Chrome(options=options)

job_opps = []

for company, url in job_links:
    browser.get(url)
    time.sleep(0.2)

    if 'hubspot' in url.lower():
        browser.find_element(By.CLASS_NAME, 'sc-kkGfuU').click()

    html = browser.page_source

    sp = BeautifulSoup(html, 'html.parser')

    print(company + ': ', end = '')
    if 'greenhouse' in url.lower():
        sections = sp.find_all('div', class_ = 'opening')
        print(len(sections), 'job opportunities!', end = '')
        for job in sections:
            title = unicodedata.normalize('NFKD', job.a.string).strip()
            link = '/'.join(url.split('/')[0:-1]) + job.a.get('href')
            loc = unicodedata.normalize('NFKD', job.span.string).strip()
            job_opps.append((company, title, link))

    if 'ultipro' in url.lower():
        while True:
            load_more = browser.find_element(By.CSS_SELECTOR, "[data-bind='visible: skip() + pageSize < totalCount() && totalCount() > 0']")
            if load_more.get_attribute('style') == '':
                load_more.click()
                browser.implicitly_wait(10)
                time.sleep(0.4)
            else:
                break
        sp = BeautifulSoup(browser.page_source, 'html.parser')
        sections = sp.find_all('div', class_='opportunity')
        print(len(sections), 'job opportunities!', end = '')
        for opp in sections:
            t_n_l = opp.find_all('a')[0]
            title = t_n_l.string
            link = '/'.join(url.split('/')[0:3]) + t_n_l.get('href')
            job_opps.append((company, title, link))
            loc = opp.find_all(attrs = {'data-bind' : 'text: Address().CityStatePostalCodeAndCountry()'})[0].string
            more_locs = opp.find('small', attrs = {'data-automation' : 'job-location-more'})
            if more_locs.string != "+0 more":
                browser.get(link)
                jl = BeautifulSoup(browser.page_source, 'html.parser')
                jl_locs = list(dict.fromkeys(jl.find_all(attrs = {'data-bind' : 'text: Address().CityStatePostalCodeAndCountry()'})))
                for new_place in jl_locs[1:]:
                    additional_job_location = new_place.string

    if 'hubspot' in url.lower():
        sections = sp.find_all('a', class_='sc-bdVaJa bKWNxX')
        print(len(sections), 'job opportunities!', end = '')
        for opp in sections:
            title = opp.find_all('p', class_ = 'sc-htpNat iUzPVU')[0].string
            loc = opp.find_all('p', class_ = 'sc-ifAKCX gHfmgn')[0].string
            link = '/'.join(url.split('/')[0:3]) + opp.get('href')
            job_opps.append((company, title, link))

    if 'lever' in url.lower():
        sections = sp.find_all('div', class_='posting')
        print(len(sections), 'job opportunities!', end = '')
        for opp in sections:
            title = opp.find_all('h5')[0].string
            loc = opp.find_all('span', class_ = 'sort-by-location posting-category small-category-label')[0].string
            link = opp.find_all('a')[0].get('href')
            job_opps.append((company, title, link))

    if 'tripactions' in url.lower():
        sections = sp.find_all('li', class_='posting')
        print(len(sections), 'job opportunities!', end = '')
        for opp in sections:
            title = opp.find_all('div', class_ = 'title')[0].string
            loc = opp.find_all('div', class_ = 'location')[0].string
            link = '/'.join(url.split('/')[0:3]) + opp.find_all('a')[0].string
            job_opps.append((company, title, link))

    if 'bird' in url.lower():
        sections = sp.find_all('div', class_='job-title')
        print(len(sections), 'job opportunities!', end = '')
        for opp in sections:
            title = opp.find_all('span', class_ = 'job-meta strong')[0].string
            loc = opp.find_all('span', class_ = 'job-meta location')[0].string
            link = opp.find_all('a')[0].get('href')
            job_opps.append((company, title, link))

    if 'breezy' in url.lower():
        sections = sp.find_all('li', class_='position transition')
        print(len(sections), 'job opportunities!', end = '')
        for opp in sections:
            title = opp.find_all('h2')[0].string
            loc = opp.find_all('li', class_ = 'location')[0].string
            link = url + opp.find_all('a')[0].get('href')
            job_opps.append((company, title, link))

    if 'scale' in url.lower():
        sections = sp.find_all('li', class_ = 'Jobs_itemWrapper__3u3uA bg-white py-2 px-4 rounded-1 shadow-md hover:shadow-xl transition-shadow duration-250 ease-out')
        print(len(sections), 'job opportunities!', end = '')
        for opp in sections:
            title = opp.find_all('h3', class_ = 'font-normaexport default Jobs;l text-base text-black mb-2')[0].string
            loc = opp.find_all('div', class_ = 'font-normal text-sm text-gray-600 mb-2')[0].string
            link = '/'.join(url.split('/')[0:3]) + opp.find_all('a')[0].get('href')
            job_opps.append((company, title, link))

    if 'activision' in url.lower():
        job_count = 0
        while True:
            sp = BeautifulSoup(browser.page_source, 'html.parser')
            sections = sp.find_all('div', class_ = 'information')
            job_count += len(sections)
            for opp in sections:
                title = opp.find_all('span')[0].string
                loc = opp.find_all('p', class_ = 'job-info')[0].find_all('span')[1].string
                link = opp.find_all('a')[0].get('href')
                job_opps.append((company, title, link))
            next_page = browser.find_elements(By.CSS_SELECTOR, "[aria-label='View next page']")[0]
            if next_page.get_attribute('href') != None:
                browser.execute_script('arguments[0].click();', next_page)
                browser.implicitly_wait(10)
                time.sleep(0.4)
            else:
                break
        print(job_count, 'job opportunities!', end = '')

    if 'coursera' in url.lower():
        categories = browser.find_elements(By.CLASS_NAME, 'role')
        jobs = 0
        for cat_num in range(len(categories)):
            browser.execute_script('arguments[0].click();', categories[cat_num])
            browser.implicitly_wait(10)
            time.sleep(0.4)
            sp = BeautifulSoup(browser.find_element(By.CLASS_NAME, 'dept-roles-wrapper').get_attribute('outerHTML'), 'html.parser')
            sections = sp.find_all('a', class_='role-block')
            jobs += len(sections)
            for opp in sections:
                title = opp.find_all('h2')[0].string
                loc = opp.find_all('div')[0].string
                link = '/'.join(url.split('/')[0:3]) + opp.get('href')
                job_opps.append((company, title, link))
            browser.execute_script('arguments[0].click();', categories[cat_num])
            browser.implicitly_wait(10)
        print(jobs, 'job opportunities!', end = '')

    if 'coinbase' in url.lower():
        categories = browser.find_elements(By.CLASS_NAME, 'Department__Wrapper-sc-1n8uxi6-0.jItAmd')
        for category in categories:
            browser.execute_script('arguments[0].scrollIntoView(true);', category)
            browser.execute_script('window.scrollBy(0, -200);')
            browser.implicitly_wait(10)
            webdriver.ActionChains(browser).move_to_element(category).click(on_element = category).perform()
            browser.implicitly_wait(10)
            time.sleep(0.4)
        sp = BeautifulSoup(browser.find_element(By.CLASS_NAME, 'Positions__PositionsColumn-jve35q-7.jmaYDM').get_attribute('outerHTML'), 'html.parser')
        sections = sp.find_all('div', class_='Department__Job-sc-1n8uxi6-6 cgTJyi')
        print(len(sections), 'job opportunities!', end = '')
        for opp in sections:
            title = opp.find_all('a')[0].string
            loc = opp.find_all('div', class_ = 'Department__JobLocation-sc-1n8uxi6-8 iuVWuT')[0].string
            link = opp.find_all('a')[0].get('href')
            job_opps.append((company, title, link))

    if 'intuitive' in url.lower():
        browser.find_element(By.CSS_SELECTOR, '.mat-select-arrow.ng-tns-c64-33').click()
        browser.implicitly_wait(10)
        browser.find_elements(By.TAG_NAME, 'mat-option')[3].click()
        browser.implicitly_wait(10)
        jobs = 0
        while True:
            section_tag = browser.find_element(By.TAG_NAME, 'mat-accordion')
            sp = BeautifulSoup(section_tag.get_attribute('innerHTML'), 'html.parser')
            sections = sp.find_all('mat-expansion-panel-header')
            jobs += len(sections)
            if len(sections) == 0:
                sys.exit()
            for section in sections:
                title = section.contents[0].contents[0].contents[1].string
                link = '/'.join(url.split('/')[0:3]) + section.contents[0].contents[0].contents[1].contents[0]['href']
                loc = section.contents[0].contents[1].contents[0].contents[0].contents[0].contents[0].contents[1].string
                job_opps.append((company, title, link))
            next_page = browser.find_element(By.CSS_SELECTOR, "[aria-label='Next Page of Job Search Results']")
            if next_page.get_attribute('disabled') == None:
                browser.execute_script('arguments[0].click();', next_page)
                browser.implicitly_wait(20)
                browser.refresh()
                browser.implicitly_wait(10)
            else:
                break
        print(jobs, 'job opportunities!', end = '')

    if 'ttcportals' in url.lower():
        opportunities = 0
        page_count = len(sp.find_all('a', href = lambda href: href and '/jobs/search?page=' in href)) // 2
        for page in range(page_count):
            sp = BeautifulSoup(browser.page_source, 'html.parser')
            sections = [section for section in sp.find_all('div') if len(section.contents) > 0 and 'h3' in [sec.name for sec in section.contents]]
            for job in sections[1:]:
                title = job.find_all('h3')[0].find_all('a')[0].string
                link = job.find_all('h3')[0].find_all('a')[0]['href']
                loc = job.find_all('div')[0].find_all('div')[0].find_all('a')[0].string
                job_opps.append((company, title, link))
            opportunities += len(sections)

            if page < page_count - 1:
                browser.find_element(By.CLASS_NAME, 'next_page').click()
                browser.implicitly_wait(10)

        job_opps = list(dict.fromkeys(job_opps))
        print(opportunities, 'job opportunities!', end = '')

    while(True):
        try:
            if 'docusign' in url.lower():
                categs = browser.find_elements(By.CLASS_NAME, 'careers-fpp')
                times = len(categs)
                before = len(job_opps)
                #print("Times:", times)
                for count in range(times):
                    #print('Time:', count, end = '; ')
                    category = browser.find_elements(By.CLASS_NAME, 'careers-fpp')[count]

                    dept_id = category.get_attribute('data-department-id')
                    #print(dept_id)
                    WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-department-id='" + dept_id + "']"))).click()
                    browser.implicitly_wait(10)
                    sp_ = BeautifulSoup(browser.page_source, 'html.parser')
                    table = sp_.find('table', class_ = 'job-table-' + dept_id)

                    for job in table.find_all('tr', class_ = 'tr-row'):
                        title = job.contents[0].a.string
                        link = job.contents[0].a['href']
                        loc = job.contents[1].string
                        job_opps.append((company, title, link))

                    browser.refresh()
                    browser.implicitly_wait(10)
            else:
                break

            print((len(job_opps) - before), 'job opportunities!', end = '')
            break
        except KeyboardInterrupt:
            sys.exit()
        except:
            job_opps = [job for job in job_opps if job[0] != company]
            print('\n\nUmmm. This is embarrassing... Something went wrong, but I am')
            print('going to try again right now. Please be patient, but feel')
            print('free to restart the program as you wish.\n\n')

    print()

print('\n\n')

browser.close()

print('Based on the resources that I have on hand, I am ready to start')
print('displaying this information for you!')

# Part 5 #######################################################################

import tkinter as tk
import sys

top = tk.Tk(className = ' Job Post Listings ')
w, h = 400, 400
top.geometry(str(w + 16) + 'x' + str(h))
top_status = 1

button_canvas = tk.Text(top, wrap = 'none')
jobs = tk.Text(top, wrap = tk.WORD)

def end_state(event):
    if top_status == 1:
        top.destroy()
        sys.exit()
    elif top_status == 2:
        print('Going back to main screen...')
        start()

def company_jobs(company_name):
    global top_status, jobs, button_canvas
    top_status = 2
    top.resizable(True, True)
    print(company_name)
    jobs.destroy()
    button_canvas.destroy()
    jobs = tk.Text(top, wrap = tk.WORD)
    jobs.pack(fill = tk.BOTH, expand = True)
    minimum = False
    for job in job_opps:
        if company_name == job[0]:
            jobs.insert(tk.END, job[1] + '\n')
            minimum = True

    if not minimum:
        jobs.insert(tk.END, 'I am sorry to say that no job was detected on this page. Please contact the program creator at anmol1227@yahoo.com.')

    jobs.configure(state = 'disabled')

def start():
    global top_status, jobs, button_canvas
    top_status = 1
    top.resizable(False, False)
    jobs.destroy()
    button_canvas.destroy()
    button_canvas = tk.Text(top, wrap = 'none')
    button_canvas.pack(fill = tk.BOTH, expand = True)
    
    columns = 2
    col_index = 0
    row_frame = None

    for company_name, _ in job_links:
        if col_index == 0:
            row_frame = tk.Frame(top, height = (h // 2) - 3, bd = 0)
        cont_frame = tk.Frame(row_frame, height = (h // 2) - 3, width = (w // 2) - 3, bd = 0)
        cont_frame.pack_propagate(0)
        if col_index == 0:
            cont_frame.pack(side = tk.LEFT)
        elif col_index == 1:
            cont_frame.pack(side = tk.RIGHT)
        company_button = tk.Button(cont_frame, text = company_name, command = lambda s = company_name: company_jobs(s))
        company_button.pack(fill = tk.BOTH, expand = 1)
        if col_index == 1 or company_name == job_links[-1][0]:
            button_canvas.window_create(tk.END, window = row_frame)
            button_canvas.insert(tk.END, '\n')
        col_index = (col_index + 1) % 2

    button_canvas.configure(state = 'disabled')

    scroller = tk.Scrollbar(button_canvas)
    scroller.config(command = button_canvas.yview)
    button_canvas.configure(yscrollcommand = scroller.set)
    scroller.pack(side = tk.RIGHT, fill = tk.Y)

if __name__ == '__main__':
    top.bind('<Escape>', end_state)
    start()
    tk.mainloop()
