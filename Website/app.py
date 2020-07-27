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
            for row in csv_reader:
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

                labels.append(Date)
                values.append(50000)
        cur.execute('SELECT * FROM Stock')
        rows = cur.fetchall();
    except:
        con.rollback()                                      #in the event of an error rollback database
        print("error in insert operation")
    finally:
        return render_template('index.html', rows=rows, labels=labels, values=values)

#if index is typed directly it redirects to '/'
@app.route('/index', methods=['GET'])                           #takes you to the route
def index():
    return redirect(url_for('home'))

# @app.route('/charts')                                                 #home page
# def charts():
    
#     return render_template('charts.html')

# @app.route('/tables')                                                 #home page
# def tables():
#     return render_template('tables.html')

#if this were the main module, run the application
if __name__ == '__main__':
    app.run()
