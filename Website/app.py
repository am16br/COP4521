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
from yahoo_fin import stock_info as si

class Stock(object):
    def __init__(self, tick, qty, purprice):
        self.tick = tick
        self.qty = qty
        self.purprice = purprice
        self.price = si.get_live_price(tick)   #input current data from web
    def modify(self, qty, price):
        self.purprice = (self.purprice*self.qty + qty*purprice) / (self.qty+qty)
        self.qty = self.qty + qty
    def get_tick(self):
        return self.tick
    def get_qty(self):
        return self.qty
    def get_purprice(self):
        return round(float(self.purprice),2)
    def get_price(self):
        p = si.get_live_price(self.get_tick())    #import current price
        return round(float(p),2)
    def get_inv(self):
        return round(float(self.qty)*float(self.purprice),2)
    def get_val(self):
        return round(float(self.qty)*float(self.price),2)   #change to price
    def get_growth(self):
        return round((float(self.get_val())-float(self.get_inv()))/(float(self.get_inv()))*100,2)

#python-env\Scripts\activate.bat
#Line used to enter python env in windows cmd

app = Flask(__name__, instance_relative_config=True)
app.config['ENV'] = True
#Default port is '127.0.0.1:5000'

#takes you to the home page
@app.route('/')                                                 #home page
def home():
    ticker = '^GSPC'
    csvname = (ticker + '.csv')
    dbname = ('Projecto.db')
    labels = []
    values = []

    if os.path.exists(csvname):
        os.remove(csvname)

    #years = int(input("Enter number of years to check stock data: "))
    endDate = date.today()
    startDate = date(endDate.year-5, endDate.month, endDate.day)

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
                High = round(float(row[1]), 2)
                Low = round(float(row[2]), 2)
                Open = round(float(row[3]), 2)
                Close = round(float(row[4]), 2)
                Volume = round(float(row[5]))
                AdjClose = round(float(row[6]), 2)
                cur.execute("""INSERT INTO Stock(Date, High, Low , Open, Close, Volume, AdjClose)
                            VALUES (?, ?, ?, ?, ?, ?, ?);""", (Date, High, Low, Open, Close, Volume, AdjClose))
                con.commit()

                labels.append(Date)
                values.append(row[6])
        cur.execute('SELECT * FROM Stock')
        rows = cur.fetchall();
    except:
        con.rollback()                                      #in the event of an error rollback database
        print("error in insert operation")
        rows = 'error'
    finally:
        con.close()
        return render_template('index.html', rows=rows, labels=labels, values=values)

#if index is typed directly it redirects to '/'
@app.route('/index', methods=['GET','POST'])                           #takes you to the route
def index():
    return redirect(url_for('home'))

@app.route('/stock', methods=['GET','POST'])
def stock():
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
    startDate = date(endDate.year - 5, endDate.month, endDate.day)

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
        con.close()
    return render_template('stock.html', ticker=ticker, rows=rows, labels=labels, values=values, min=min, max=max)


@app.route('/portfolio',methods=['GET','POST'])                                                 #home page
def portfolio():
    inv = 0
    val = 0
    con = sqlite3.connect("Projecto.db")                   #connecting to/creating/opening database
    con.row_factory = sqlite3.Row
    cur = con.cursor()                              #setting cursor
    cur.execute("""DROP TABLE IF EXISTS PORTFOLIO""")
    cur.execute('CREATE TABLE IF NOT EXISTS Portfolio(Ticker TEXT, Quantity REAL, Cost REAL, Price REAL, Investment REAL, Value, REAL, Growth REAL);')

    if request.method == 'POST':
        ticker = request.form["ticker"]
        qty = request.form["qty"]
        purprice = request.form["price"]
        obj = Stock(ticker,qty,purprice)
        try:
            ticker = obj.get_tick()
            qty = obj.get_qty()
            cost = obj.get_purprice()
            price = obj.get_price()
            investment = obj.get_inv()
            value = obj.get_val()
            growth = obj.get_growth()
            cur.execute("""INSERT INTO Portfolio(Ticker, Quantity, Cost, Price, Investment, Value, Growth)
                            VALUES (?, ?, ?, ?, ?, ?, ?);""", (ticker, qty, cost, price, investment, value, growth))
            con.commit()
            cur.execute('SELECT * FROM Portfolio')
            rows = cur.fetchall()
            cur.execute('SELECT SUM(Investment) FROM Portfolio')
            inv = cur.fetchall()
            cur.execute('SELECT SUM(Value) FROM Portfolio')
            val = cur.fetchall()
        except:
            con.rollback()                                      #in the event of an error rollback database
            print("error in insert operation")
            rows = 'error'
        finally:
            con.close()
            return render_template('portfolio.html', rows=rows, investment=inv, value=val)
    else:
        cur.execute('SELECT * FROM Portfolio')
        rows = cur.fetchall()
        cur.execute('SELECT SUM(Investment) FROM Portfolio')
        inv = cur.fetchall()
        cur.execute('SELECT SUM(Value) FROM Portfolio')
        val = cur.fetchall()
        return render_template('portfolio.html', rows=rows, investment=inv, value=val)





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
        con.close()
    return render_template('test.html', ticker=ticker, rows=rows, labels=labels, values=values, min=min, max=max)







#if this were the main module, run the application
if __name__ == '__main__':
    app.run(debug=True)
