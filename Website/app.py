from flask import *
import os
import datetime as dt
from datetime import date
import pandas as pd
import pandas_datareader.data as web
import sqlite3  #importing sqlite3
import csv

app = Flask(__name__)
#Default port is '127.0.0.1:5000'

#takes you to the home page
@app.route('/')                                                 #home page
def home():
    csvname = ('^GSPC.csv')         #naming for s&P500
    if os.path.exists(csvname):     #removing if it exists
        os.remove(csvname)
    endDate = date.today()
    startDate = date(endDate.year - 5, endDate.month, endDate.day)
    df = web.DataReader(^GSPC, 'yahoo', startDate, endDate) #reading open, high, low, close, and volume daily for S&P500 for last 5 years
    df.to_csv(csvname)                              #dding dt to csv
    return render_template('index.html')

#if index is typed directly it redirects to '/'
@app.route('/index', methods=['GET'])                           #takes you to the route
def index():
    return redirect(url_for('home'))

#takes you to the home page
@app.route('/charts')                                                 #home page
def charts():
    #ticker = input ("Enter stock ticker: ")
    ticker = request.form['ticker']
    years = request.form['years']
    csvname = (ticker + '.csv')
    dbname = (ticker + '.db')
    if os.path.exists(csvname):
      os.remove(csvname)
    #years = int(input("Enter number of years to check stock data: "))
    endDate = date.today()
    startDate = date(endDate.year - years, endDate.month, endDate.day)

    df = web.DataReader(ticker, 'yahoo', startDate, endDate)
    df.to_csv(csvname)
 
    conn = sqlite3.connect(dbname) #connecting to/creating/opening database

    cur = conn.cursor()                     #setting cursor
    cur.execute('''CREATE TABLE IF NOT EXISTS Stock (
                        Date DATE,
                        High FLOAT,
                        Low FLOAT,
                        Open FLOAT,
                        Close FLOAT,
                        Volume FLOAT,
                        AdjClose FLOAT);''')
    conn.close()

    with sqlite3.connect(dbname) as con:  #connecting database
       cur = con.cursor()
       cur.execute("""DELETE FROM Stock""")
       with open(csvname) as csv_file:
           csv_reader = csv.reader(csv_file, delimiter=',')
           line_count = 0
           for row in csv_reader:
               Date = row[0]
               High = row[1]
               Low = row[2]
               Open = row[3]
               Close = row[4]
               Volume = row[5]
               AdjClose = row[6]
               cur.execute("""INSERT INTO Stock
                           (Date, High, Low , Open, Close, Volume, AdjClose)
                           VALUES (?, ?, ?, ?, ?, ?, ?);""", (Date, High, Low, Open, Close, Volume, AdjClose))
    return render_template('charts.html')

#takes you to the home page
@app.route('/tables')                                                 #home page
def tables():
    return render_template('tables.html')

#if this were the main module, run the application
if __name__ == '__main__':
    app.run()
