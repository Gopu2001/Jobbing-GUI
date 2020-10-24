#!/usr/bin/python3.8
# Anmol Kapoor

from flask import Flask, render_template
from flask_restful import Resource, Api
from os import getcwd
import sqlite3 as sql
import jinja2

app = Flask(__name__)
api = Api(app)

my_loader = jinja2.ChoiceLoader([app.jinja_loader, jinja2.FileSystemLoader(getcwd()),])
app.jinja_loader = my_loader

class Jobbing(Resource):
    def get(self):
        connection = sql.connect('jobs.db')
        cursor = connection.cursor()
        command = "select company, title, link from jobs"
        cursor.execute(command)
        opportunities = cursor.fetchall()
        cursor.close()
        connection.close()
        jobbing = {}
        for job in opportunities:
            jobber = {}
            jobber['company'] = job[0]
            jobber['title'] = job[1]
            jobber['application link'] = job[2]
            jobbing[opportunities.index(job)] = jobber
        return jobbing

api.add_resource(Jobbing, '/jobs.json')

@app.route('/')
def home_page(data=None):
    connection = sql.connect('jobs.db')
    cursor = connection.cursor()
    command = "select distinct company from jobs"
    cursor.execute(command)
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('home.html', data=data)

@app.route('/companies/<company>/')
def sub_pages(company, data=None):
    base = '/companies/'
    connection = sql.connect('jobs.db')
    cursor = connection.cursor()
    command = f"select title, link from jobs where company = '{company}'"
    cursor.execute(command)
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('company.html', data=data)

if __name__ == '__main__':
    app.run(debug = True)
