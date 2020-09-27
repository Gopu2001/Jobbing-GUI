from flask import Flask
from flask_restful import Resource, Api
import pyodbc

app = Flask(__name__)
api = Api(app)

class Jobbing(Resource):
    def get(self):
        connection = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};Server=localhost;Database=jobs;UID=__;PWD=__')
        cursor = connection.cursor()
        command = "select company, title, link from job_listings"
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

api.add_resource(Jobbing, '/')

if __name__ == '__main__':
    app.run(debug = True)
