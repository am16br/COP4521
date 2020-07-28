#########################################################################
# Alexander Marcano, Aidan Martin, Douglas Kendall
# due 07/30/2020
# The project is the cumulative work of everyone above
######################################################################

from flask import *
import os
import datetime as dt
from datetime import date
import pandas as pd
import pandas_datareader.data as web
import sqlite3  #importing sqlite3
import csv

#python-env\Scripts\activate.bat
#Line used to enter python env in windows cmd

app = Flask(__name__, instance_relative_config=True)
#Default port is '127.0.0.1:5000'

#takes you to the home page
@app.route('/', methods = ['POST','GET'])                                                 #home page
def home():
    if request.method == 'GET':     #initially loads S&P500
        ticker = '^GSPC'
    if request.method == 'POST':    #loads new stock
        ticker = request.form["ticker"]
    csvname = (ticker + '.csv')     #creating file to hold data
    dbname = ('Projecto.db')        #creating database
    labels = []
    values = []

    if os.path.exists(csvname):     #ensuring data is most recent
      os.remove(csvname)
    endDate = date.today()          #setting dates to load data from
    startDate = date(endDate.year - 1, endDate.month, endDate.day)

    df = web.DataReader(ticker, 'yahoo', startDate, endDate)    #scraping stock data from web for range of dates
    df.to_csv(csvname)

    con = sqlite3.connect(dbname)                   #connecting to/creating/opening database
    con.row_factory = sqlite3.Row
    cur = con.cursor()                              #setting cursor

    #Delete old table, to avoid duplicates
    cur.execute("""DROP TABLE IF EXISTS STOCK""")
    #create table to hold relevant data
    cur.execute('CREATE TABLE Stock(Date TEXT, High REAL, Low REAL, Open REAL, Close REAL, Volume REAL, AdjClose REAL);')

    try:
        with open(csvname) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:  #moving data from csv to database
                iterations = 0
                Date = row[0]
                High = row[1]
                Low = row[2]
                Open = row[3]
                Close = row[4]
                Volume = row[5]
                AdjClose = row[6]
                cur.execute("""INSERT INTO Stock(Date, High, Low , Open, Close, Volume, AdjClose)
                            VALUES (?, ?, ?, ?, ?, ?, ?);""", (Date, High, Low, Open, Close, Volume, AdjClose))
                con.commit()    #committing data to database

                if iterations < 200:
                    labels.append(Date)
                    # print('row 6 is ', row[6])
                    values.append(row[6])
                    iterations += 1
        cur.execute('SELECT * FROM Stock')
        rows = cur.fetchall();
    except:
        con.rollback()                                      #in the event of an error rollback database
        print("error in insert operation")
        rows = 'error'
    finally:
        min=float(values[0])        #setting min and max values for y-axis of chart
        max=float(values[0])
        for item in values:         #modifying min and max values from list of stock values
            if float(item)>max:
                max=float(item)
            if float(item)<min:
                min=float(item)
        min=min-(min*0.25)
        max=max+(max*0.25)
        if ticker=="^GSPC":
            ticker="S&P500"
        return render_template('index.html', ticker=ticker, rows=rows, labels=labels, values=values, min=min, max=max)
        con.close()         #closing connection

#if index is typed directly it redirects to '/'
@app.route('/index', methods=['GET','POST'])                           #takes you to the route
def index():
    return redirect(url_for('home'))

@app.route('/stock', methods=['POST'])
def stock():
    #similar to index for individual stocks
    ticker = request.form["ticker"]
    csvname = (ticker + '.csv')
    dbname = ('Projecto.db')
    labels = []
    values = []
    if os.path.exists(csvname):
      os.remove(csvname)
    endDate = date.today()
    startDate = date(endDate.year - 1, endDate.month, endDate.day)

    df = web.DataReader(ticker, 'yahoo', startDate, endDate)
    df.to_csv(csvname)

    con = sqlite3.connect(dbname)                   #connecting to/creating/opening database
    con.row_factory = sqlite3.Row
    cur = con.cursor()                              #setting cursor

    #Delete old table, to avoid duplicates
    cur.execute("""DROP TABLE IF EXISTS STOCK""")

    cur.execute('CREATE TABLE Stock(Date TEXT, High REAL, Low REAL, Open REAL, Close REAL, Volume REAL, AdjClose REAL);')

    try:
        with open(csvname) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                iterations = 0
                Date = row[0]
                High = row[1]
                Low = row[2]
                Open = row[3]
                Close = row[4]
                Volume = row[5]
                AdjClose = row[6]
                cur.execute("""INSERT INTO Stock(Date, High, Low , Open, Close, Volume, AdjClose)
                            VALUES (?, ?, ?, ?, ?, ?, ?);""", (Date, High, Low, Open, Close, Volume, AdjClose))
                con.commit()

                if iterations < 200:
                    labels.append(Date)
                    # print('row 6 is ', row[6])
                    values.append(row[6])
                    iterations += 1
        cur.execute('SELECT * FROM Stock')
        rows = cur.fetchall();
    except:
        con.rollback()                                      #in the event of an error rollback database
        print("error in insert operation")
        rows = 'error'
    finally:
        min=float(values[0])
        max=float(values[0])
        for item in values:
            if float(item)>max:
                max=float(item)
            if float(item)<min:
                min=float(item)
        min=min-(min*0.25)
        max=max+(max*0.25)
        return render_template('index.html', ticker=ticker, rows=rows, labels=labels, values=values, min=min, max=max)
        con.close()
@app.route('/portfolio',methods=['POST'])                                                 #home page
def portfolio():
     portfolio = []
     ticker = request.form["ticker"]
     qty = request.form["qty"]
     purprice = request.form["price"]
     portfolio.append(Stock(ticker,qty,purprice))
     inv = 0
     val = 0
     con = sqlite3.connect("Portfolio.db")                   #connecting to/creating/opening database
     con.row_factory = sqlite3.Row
     cur = con.cursor()                              #setting cursor

     cur.execute('CREATE TABLE Stock(Ticker TEXT, Quantity REAL, Cost REAL, Price REAL, Investment REAL, Value, REAL, Growth REAL);')
     try:
         for obj in portfolio:
             ticker = obj.get_tick()
             qty = obj.get_qty()
             cost = obj.get_purprice()
             price = obj.get_price()
             investment = obj.get_inv()
             value = obj.get_val()
             growth = obj.get_growth()
             cur.execute("""INSERT INTO Stock(Ticker, Quantity, Cost, Price, Investment, Value, Growth)
                         VALUES (?, ?, ?, ?, ?, ?, ?);""", (ticker, qty, cost, price, investment, value, growth))
             con.commit()
             inv = inv + obj.get_inv()
             val = val + obj.get_val()
         growth = val/inv *100.00
         cur.execute('SELECT * FROM Stock')
         rows = cur.fetchall();`
     except:
         con.rollback()                                      #in the event of an error rollback database
         print("error in insert operation")
         rows = 'error'
     finally:
         return render_template('portfolio.html', rows=rows, investment=inv, value=val, growth=growth)
# @app.route('/tables')                                                 #home page
# def tables():
#     return render_template('tables.html')

#if this were the main module, run the application
if __name__ == '__main__':
    app.run()
