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

class Stock(object):                        #stock class to create object/calculate values for portfolio
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

#python-env\Scripts\activate.bat
#Line used to enter python env in windows cmd

app = Flask(__name__, instance_relative_config=True)
app.config['ENV'] = True
#Default port is '127.0.0.1:5000'

#takes you to the home page
@app.route('/')                                                 #home page
def home():
    ticker = '^GSPC'                        #for S&P500
    csvname = (ticker + '.csv')
    dbname = ('Projecto.db')
    labels = []
    values = []

    if os.path.exists(csvname):             #removing previous csv to pull most recent data
        os.remove(csvname)
    endDate = date.today()                  #fetching todays date
    startDate = date(endDate.year - 5, endDate.month, endDate.day)    #getting date 5 years in the past

    df = web.DataReader(ticker, 'yahoo', startDate, endDate)        #scraping stock data dating back 5 years
    df.to_csv(csvname)

    con = sqlite3.connect(dbname)                   #connecting to/creating/opening database
    con.row_factory = sqlite3.Row
    cur = con.cursor()                              #setting cursor

    #Delete old table, to avoid duplicates, and ensure most recent data
    cur.execute("""DROP TABLE IF EXISTS STOCK""")
    cur.execute('CREATE TABLE Stock(Date TEXT, High REAL, Low REAL, Open REAL, Close REAL, Volume INTEGER, AdjClose REAL);')

    iterations = 0
    try:
        with open(csvname) as csv_file:
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
                if iterations % 10 == 0:
                    labels.append(Date)     #adding date to labels list for chart
                    values.append(round(float(row[6]), 2))   #adding AdjClose to values list for chart
                iterations += 1
        cur.execute('SELECT * FROM Stock')  #selecting all data for table
        rows = cur.fetchall();
    except:
        con.rollback()                                      #in the event of an error rollback database
        print("error in insert operation")
        rows = 'error'
    finally:
        con.close()             #closing connection
        return render_template('index.html', rows=rows, labels=labels, values=values)   #rendering html page and sending data over

#if index is typed directly it redirects to '/'
@app.route('/index', methods=['GET','POST'])                           #takes you to the route
def index():
    return redirect(url_for('home'))

@app.route('/stock', methods=['GET','POST'])    #similar to above
def stock():
    if request.method == 'POST':            #getting ticker inputted by user in search bar
        ticker = request.form["ticker"]
    else:
        ticker = '^DJI'                     #defaulting to dow jones
    csvname = (ticker + '.csv')
    dbname = ('Projecto.db')
    labels = []
    values = []
    if os.path.exists(csvname):
        os.remove(csvname)
    endDate = date.today()
    startDate = date(endDate.year - 5, endDate.month, endDate.day)

    df = web.DataReader(ticker, 'yahoo', startDate, endDate)
    df.to_csv(csvname)

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
                Volume = int(row[5])
                AdjClose = round(float(row[6]), 2)
                cur.execute("""INSERT INTO Stock(Date, High, Low , Open, Close, Volume, AdjClose)
                            VALUES (?, ?, ?, ?, ?, ?, ?);""", (Date, High, Low, Open, Close, Volume, AdjClose))
                con.commit()

                if iterations % 10 == 0:
                    labels.append(Date)
                    values.append(round(float(row[6]), 2))
                iterations += 1
        cur.execute('SELECT * FROM Stock')
        rows = cur.fetchall();
    except:
        con.rollback()                                      #in the event of an error rollback database
        print("error in insert operation")
        rows = 'error'
    finally:
        min=float(values[0])        #calculating min and max by setting to first adjClose value
        max=float(values[0])
        for item in values:         #looping through all values
            if float(item)>max:     #changing min and max if value is less than or greater than respectively
                max=float(item)
            if float(item)<min:
                min=float(item)
        min=round(min-(min*0.25))          #adding 0.25% buffer for visually appealing chart
        max=round(max+(max*0.25))
        con.close()
    return render_template('stock.html', ticker=ticker, rows=rows, labels=labels, values=values, min=min, max=max)


@app.route('/portfolio',methods=['GET','POST'])   #page to display user's portfolio
def portfolio():
    inv = 0
    val = 0
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
            cur.execute('SELECT * FROM Portfolio')  #getting rows for table of positions
            rows = cur.fetchall()
            cur.execute('SELECT SUM(Investment) FROM Portfolio')    #getting sum of investment to show overall initial investment
            inv = round((cur.fetchone()[0]),2)
            cur.execute('SELECT SUM(Value) FROM Portfolio')         #getting sum of current value to show growth/losses
            val = round((cur.fetchone()[0]),2)
            growth = round(((val-inv)/inv)*100,2)
        except:
            con.rollback()                                      #in the event of an error rollback database
            print("error in insert operation")
            rows = 'error'
        finally:
            con.close()
            return render_template('portfolio.html', rows=rows, investment=inv, value=val, growth=growth)  #rendering page/sending data
    else:                                       #if page just loaded, nothing added to db
        cur.execute('SELECT * FROM Portfolio')
        rows = cur.fetchall()
        cur.execute('SELECT SUM(Investment) FROM Portfolio')
        inv = round((cur.fetchone()[0]),2)
        cur.execute('SELECT SUM(Value) FROM Portfolio')
        val = round((cur.fetchone()[0]),2)
        growth = round(((val-inv)/inv)*100,2)
        return render_template('portfolio.html', rows=rows, investment=inv, value=val, growth=growth)





@app.route('/test', methods=['GET','POST'])
def test():
    if request.method == 'POST':
        ticker = request.form["ticker"]
    else:
        ticker = '^DJI'
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
        con.close()
    return render_template('test.html', ticker=ticker, rows=rows, labels=labels, values=values, min=min, max=max)


#if this were the main module, run the application
if __name__ == '__main__':
    app.run(debug=True)
