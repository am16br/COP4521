#########################################################################
# Alexander Marcano, Aidan Martin, Douglas Kendall
# due 07/30/2020
# The project is the cumulative work of everyone above
######################################################################

from flask import *         #libraries
import os
import datetime as dt
from datetime import date
import pandas as pd
import pandas_datareader.data as web
import sqlite3  #importing sqlite3
import csv
from yahoo_fin import stock_info as si
import requests


class Stock(object):                        #stock class to create object/calculate values for portfolio Aidan
    def __init__(self, tick, qty, purprice):    #initializing with ticker, quantity, and purchase price
        self.tick = tick
        self.qty = qty
        self.purprice = purprice
        self.price = si.get_live_price(tick)   #input current data from web
    def modify(self, qty, price):
        self.purprice = (self.purprice*self.qty + qty*purprice) / (self.qty+qty)
        self.qty = self.qty + qty
    def get_tick(self):                     #getters
        return self.tick
    def get_qty(self):
        return self.qty
    def get_purprice(self):
        return round(float(self.purprice),2)    #returning float rounded to 2 decimal places
    def get_price(self):
        p = si.get_live_price(self.get_tick())    #import current price
        return round(float(p),2)
    def get_inv(self):
        return round(float(self.qty)*float(self.purprice),2)
    def get_val(self):
        return round(float(self.qty)*float(self.price),2)   #calculating current value
    def get_growth(self):
        return round((float(self.get_val())-float(self.get_inv()))/(float(self.get_inv()))*100,2)   #calculating growth

def movingAvg(time, values):
    v = []
    length = int(len(values)/time)
    for i in range(length):
        total = 0
        a = values[i]
        for x in range(time):
            total = total + values[(x*i)+x]
            b = values[(x*i)+x]
        total = round(float(total/time),2)
        diff = b - a
        slope = diff / time
        for x in range(time):
            intermed = round((slope * (x+1))+total,2)
            v.append(intermed)
    return v
#python-env\Scripts\activate.bat
#Line used to enter python env in windows cmd

app = Flask(__name__, instance_relative_config=True)
app.config['ENV'] = True
#Default port is '127.0.0.1:5000'

#takes you to the home page
@app.route('/', methods=['GET','POST'])                                                 #home page
def home():
    endDate = date.today()                  #fetching todays date
    if request.method == 'POST':
        if request.form["1"] == "1 Week":                   #buttons to set timeframe
            startDate = date(endDate.year, endDate.month, endDate.day - 7)  #modifying start date for data to 1 week, month, year, etc
            mod = 1
        elif request.form["1"] == "1 Month":
            startDate = date(endDate.year, endDate.month - 1, endDate.day)
            mod = 2
        elif request.form["1"] == "3 Months":
            startDate = date(endDate.year, endDate.month - 3, endDate.day)
            mod = 2
        elif request.form["1"] == "6 Months":
            startDate = date(endDate.year, endDate.month - 6, endDate.day)
            mod = 2
        elif request.form["1"] == "1 Year":
            startDate = date(endDate.year - 1, endDate.month, endDate.day)
            mod = 5
        elif request.form["1"] == "5 Years":
            startDate = date(endDate.year - 5, endDate.month, endDate.day)
            mod = 10
    else:
        startDate = date(endDate.year, endDate.month, endDate.day - 7)    #getting date 1 week in the past
        mod = 1
    ticker = '^GSPC'                        #for S&P500
    csvname = (ticker + '.csv')
    dbname = ('Projecto.db')
    labels = []
    values = []
    if os.path.exists(csvname):             #removing previous csv to pull most recent data
        os.remove(csvname)

    df = web.DataReader(ticker, 'yahoo', startDate, endDate)        #scraping stock data dating back 5 years
    df.to_csv(csvname)

    con = sqlite3.connect(dbname)                   #connecting to/creating/opening database
    con.row_factory = sqlite3.Row
    cur = con.cursor()                              #setting cursor

        #Delete old table, to avoid duplicates, and ensure most recent data
    cur.execute("""DROP TABLE IF EXISTS STOCK""")
    cur.execute('CREATE TABLE Stock(Date TEXT, High REAL, Low REAL, Open REAL, Close REAL, Volume INTEGER, AdjClose REAL);')
    #creating table Stock to hold data (date, ohlc, volume, and adjusted close)
    iterations = 0
    try:                            #exception handling
        with open(csvname) as csv_file:                 #opening csv to transfer to database
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:  #looping through csv
                Date = row[0]                   #getting data from row/column to add to database
                High = round(float(row[1]), 2)  #rounding float value to 2 decimal places
                Low = round(float(row[2]), 2)
                Open = round(float(row[3]), 2)
                Close = round(float(row[4]), 2)
                Volume = int(row[5])
                AdjClose = round(float(row[6]), 2)
                cur.execute("""INSERT INTO Stock(Date, High, Low , Open, Close, Volume, AdjClose)
                                VALUES (?, ?, ?, ?, ?, ?, ?);""", (Date, High, Low, Open, Close, Volume, AdjClose))
                    #inserting data, row by row, into database
                con.commit()        #commiting data to db
                if iterations % mod == 0:           #choosing values to add for chart
                    labels.append(Date)     #adding date to labels list for chart
                    values.append(round(float(row[6]), 2))   #adding AdjClose to values list for chart
                iterations += 1
        cur.execute('SELECT * FROM Stock')  #selecting all data for table
        rows = cur.fetchall();
    except:
        con.rollback()                                      #in the event of an error rollback database
        return render_template('500.html')
    finally:
        min=float(values[0])        #calculating min and max by setting to first adjClose value
        max=float(values[0])
        for item in values:         #looping through all values
            if float(item)>max:     #changing min and max if value is less than or greater than respectively
                max=float(item)
            if float(item)<min:     #used for y axis of chart
                min=float(item)
        con.close()             #closing connection
        os.remove(csvname)
        return render_template('index.html', rows=rows, labels=labels, values=values, min=min, max=max)   #rendering html page and sending data over

#if index is typed directly it redirects to '/'
@app.route('/index', methods=['GET','POST'])                           #takes you to the route
def index():
    return redirect(url_for('home'))

@app.route('/stock', methods=['GET','POST'])    #similar to above
def stock():
    ticker = '^DJI'
    endDate = date.today()                  #fetching todays date
    short = 1
    long = 7
    if request.method == 'POST':
        ticker = request.form["ticker"]     #getting user entered stock ticker
        if request.form["1"] == "1 Week":   #getting timeframe to pull data from
            startDate = date(endDate.year, endDate.month, endDate.day - 7)
            mod = 1
            short = 1
            long = 3
        elif request.form["1"] == "1 Month":
            startDate = date(endDate.year, endDate.month - 1, endDate.day)
            mod = 2
            short = 5
            long = 10
        elif request.form["1"] == "3 Months":
            startDate = date(endDate.year, endDate.month - 3, endDate.day)
            mod = 2
            short = 10
            long = 20
        elif request.form["1"] == "6 Months":
            startDate = date(endDate.year, endDate.month - 6, endDate.day)
            mod = 2
            short = 10
            long = 30
        elif request.form["1"] == "1 Year":
            startDate = date(endDate.year - 1, endDate.month, endDate.day)
            mod = 5
            short = 20
            long = 50
        else:
            startDate = date(endDate.year - 5, endDate.month, endDate.day)
            mod = 10
            short = 50
            long = 100

    else:
        startDate = date(endDate.year, endDate.month, endDate.day - 7)
        mod = 1
    csvname = (ticker + '.csv')
    dbname = ('Projecto.db')
    labels = []
    values = []
    if os.path.exists(csvname):
        os.remove(csvname)
    #using pandas datareader to pull stock's data from yahoo from start to end date
    df = web.DataReader(ticker, 'yahoo', startDate, endDate)
    df.to_csv(csvname)
    #same as for homepage
    con = sqlite3.connect(dbname)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("""DROP TABLE IF EXISTS STOCK""")
    cur.execute('CREATE TABLE Stock(Date TEXT, High REAL, Low REAL, Open REAL, Close REAL, Volume INTEGER, AdjClose REAL);')

    iterations = 0
    try:
        with open(csvname) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                Date = row[0]
                High = round(float(row[1]), 2)
                Low = round(float(row[2]), 2)
                Open = round(float(row[3]), 2)
                Close = round(float(row[4]), 2)
                Volume = float(row[5])
                AdjClose = round(float(row[6]), 2)
                cur.execute("""INSERT INTO Stock(Date, High, Low , Open, Close, Volume, AdjClose)
                            VALUES (?, ?, ?, ?, ?, ?, ?);""", (Date, High, Low, Open, Close, Volume, AdjClose))
                con.commit()
                if iterations % 1 == 0:
                    labels.append(Date)
                    values.append(AdjClose)
                iterations += 1
        cur.execute('SELECT * FROM Stock')
        rows = cur.fetchall();
    except:
        con.rollback()                                      #in the event of an error rollback database
        return render_template('500.html')
    finally:
        min=float(values[0])        #calculating min and max by setting to first adjClose value
        max=float(values[0])
        for item in values:         #looping through all values
            if float(item)>max:     #changing min and max if value is less than or greater than respectively
                max=float(item)
            if float(item)<min:
                min=float(item)
        shortma = movingAvg(short, values)
        longma = movingAvg(long, values)
        default = ticker    #setting default value for request form
        #yahoo finance standard way to get long name from ticker
        url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(ticker.upper())
        result = requests.get(url).json()
        for x in result['ResultSet']['Result']:
            if x['symbol'] == ticker:
                ticker= x['name']
        #end of yahoo standard way to get long name
        con.close()
        os.remove(csvname)
    return render_template('stock.html', default=default, ticker=ticker, rows=rows, labels=labels, values=values, shortma=shortma, longma=longma, short=short, long=long, min=min, max=max)

@app.route('/portfolio',methods=['GET','POST'])   #page to display user's portfolio
def portfolio():
    con = sqlite3.connect("Projecto.db")                   #connecting to/creating/opening database
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS Portfolio(Ticker TEXT, Quantity REAL, Cost REAL, Price REAL, Investment REAL, Value, REAL, Growth REAL);')
    #creating table to hold portfolio positions
    if request.method == 'POST':    #POST to get info from user (stock ticker, quantity purchases, and purchase price
        ticker = request.form["ticker"]
        qty = request.form["qty"]
        purprice = request.form["price"]
        obj = Stock(ticker,qty,purprice)    #creating object from user data with class previously defined
        try:
            ticker = obj.get_tick()         #using getters from class to send data to database
            qty = obj.get_qty()
            cost = obj.get_purprice()
            price = obj.get_price()
            investment = obj.get_inv()
            value = obj.get_val()
            growth = obj.get_growth()
            cur.execute("""INSERT INTO Portfolio(Ticker, Quantity, Cost, Price, Investment, Value, Growth)
                            VALUES (?, ?, ?, ?, ?, ?, ?);""", (ticker, qty, cost, price, investment, value, growth))
            #inserting data to db
            con.commit()    #commiting data to db
            cur.execute('SELECT * FROM Portfolio')
            for row in cur: #looping though database to get live price and recalculate any values
                ticker = row[0]
                qty = row[1]
                cost = row[2]
                price = si.get_live_price(ticker)
                price = round(price,2)
                inv = round((cost * qty),2)
                val = round((price * qty),2)
                growth = round(((val-inv)/inv)*100,2)
                #updating each row in portfolio
                cur.execute('UPDATE Portfolio SET Price = ?, Investment = ?, Value = ?, Growth = ? WHERE Ticker = ?', (price, inv, val, growth, ticker,))
            cur.execute('SELECT * FROM Portfolio')
            rows = cur.fetchall()
            cur.execute('SELECT SUM(Investment) FROM Portfolio')    #getting sum of investment to show overall initial investment
            inv = round((cur.fetchone()[0]),2)
            cur.execute('SELECT SUM(Value) FROM Portfolio')         #getting sum of current value to show growth/losses
            val = round((cur.fetchone()[0]),2)
            growth = round(((val-inv)/inv)*100,2)
        except:
            con.rollback()                                      #in the event of an error rollback database
            return render_template('500.html')
        finally:
            con.close()
            return render_template('portfolio.html', rows=rows, investment=inv, value=val, growth=growth)  #rendering page/sending data
    else:                                       #if page just loaded, nothing added to db
        cur.execute('SELECT * FROM Portfolio')
        for row in cur:
            #updating price and recalculating data
            ticker = row[0]
            qty = row[1]
            cost = row[2]
            price = si.get_live_price(ticker)
            price = round(price,2)
            inv = round((cost * qty),2)
            val = round((price * qty),2)
            growth = round(((val-inv)/inv)*100,2)
            cur.execute('UPDATE Portfolio SET Price = ?, Investment = ?, Value = ?, Growth = ? WHERE Ticker = ?', (price, inv, val, growth, ticker,))
        cur.execute('SELECT * FROM Portfolio')
        rows = cur.fetchall()
        if len(rows) == 0:  #ensuring empty databse does not cause any errors
            inv=0
            val=0
            growth = 0
        else:
            cur.execute('SELECT SUM(Investment) FROM Portfolio')    #getting sum of investment column
            inv = round((cur.fetchone()[0]),2)                  #fetching sum value
            cur.execute('SELECT SUM(Value) FROM Portfolio')         #same for current value
            val = round((cur.fetchone()[0]),2)
            growth = round(((val-inv)/inv)*100,2)               #calculating growth percent
        return render_template('portfolio.html', rows=rows, investment=inv, value=val, growth=growth)

@app.route('/login',methods=['GET','POST'])   #page to display user's portfolio
def login():
    return render_template('login.html')

@app.route('/password',methods=['GET','POST'])   #page to display user's portfolio
def password():
    return render_template('password.html')

@app.route('/register',methods=['GET','POST'])   #page to display user's portfolio
def register():
    return render_template('register.html')

@app.route('/readme',methods=['GET','POST'])   #page to display user's portfolio
def readme():
    return render_template('README.html')

#if this were the main module, run the application
if __name__ == '__main__':
    app.run(debug=True)
