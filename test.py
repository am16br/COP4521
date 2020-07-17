import os
import datetime as dt
from datetime import date
import pandas as pd
import pandas_datareader.data as web
import sqlite3  #importing sqlite3
import csv
 
ticker = input ("Enter stock ticker: ")
csvname = (ticker + '.csv')
dbname = (ticker + '.db')
if os.path.exists(csvname):
  os.remove(csvname)
years = int(input("Enter number of years to check stock data: "))
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
