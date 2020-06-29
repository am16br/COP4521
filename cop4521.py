#Aidan Martin   am16br@my.fsu.edu   6/28/20
#The program in this file is the individual work of Aidan Martin

import datetime as dt
from datetime import date
import matplotlib.pyplot as plt
from matplotlib import style
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mdates
import pandas as pd
import pandas_datareader.data as web


print ("Welcome to the COP4521 Python Financial Advisor")

class Stock(object):
    def __init__(self, tick, qty, purprice):
        self.tick = tick
        self.qty = qty
        self.purprice = purprice
        self.price = 1000   #input current data from web
    def modify(self, qty, price):
        self.purprice = (self.purprice*self.qty + qty*purprice) / (self.qty+qty)
        self.qty = self.qty + qty
    def get_tick(self):
        return self.tick
    def get_qty(self):
        return self.qty
    def get_purprice(self):
        return self.purprice
    def get_price(self):
        return self.price    #import current price
    def get_inv(self):
        return self.qty*self.purprice
    def get_val(self):
        return self.qty*self.price   #change to price
    def get_growth(self):
        return (self.qty*self.price)/(self.qty*self.purprice)*100

def Menu():
    print("""
    1. Display Menu
    2. Add to Portfolio
    3. Analyze stock
    4. Display Portfolio
    5. Exit/Quit
    """)

Menu()
portfolio = []
ans=True
while ans:
    ans = input("> ")
    if ans=="1":
        Menu()
    elif ans=="2":
      tick = input ("Enter stocker ticker: ")
      #check for validity with function
      qty = int(input ("Enter number of shares puchased: "))
      purprice = int(input ("Enter purchase price: "))
      #modify if already in portfolio
      portfolio.append( Stock(tick, qty, purprice) )    #add to list of stocks
    elif ans=="3":
      ticker = input ("Enter stock ticker: ")
      csvname = (ticker + '.csv')
      years = int(input("Enter number of years to check stock data: "))
      endDate = date.today()
      startDate = date(endDate.year - years, endDate.month, endDate.day)

      df = web.DataReader(ticker, 'yahoo', startDate, endDate)
      df.to_csv(csvname)

      style.use('ggplot')

      df=pd.read_csv(csvname,parse_dates=True, index_col=0)

      df_ohlc = df['Adj Close'].resample('10D').ohlc()
      # can have any time frame to resample, or mean/sum/else instead of ohlc
      df_volume = df['Volume'].resample('10D').sum()

      df_ohlc.reset_index(inplace=True)

      df_ohlc['Date'] = df_ohlc['Date'].map(mdates.date2num)

      ax1 = plt.subplot2grid((6,1),(0,0), rowspan=5,colspan=1)
      ax2 = plt.subplot2grid((6,1),(5,0), rowspan=1,colspan=1,sharex=ax1)
      ax1.xaxis_date()
      candlestick_ohlc(ax1, df_ohlc.values, width=2, colorup='g')
      ax2.fill_between(df_volume.index.map(mdates.date2num), df_volume.values, 0)
      plt.show()

    elif ans=="4":
      print ("Portfolio")
      x = 0
      inv = 0
      val = 0
      for obj in portfolio:
          x = x+1
          print("\n"+str(x) + ". " + obj.get_tick())
          print("Shares: " + str(obj.get_qty()))
          print("Initial Investment: $" + str(obj.get_inv()))
          print("Current Value: $" +  str(obj.get_val()))
          print("Growth: " +  str(obj.get_growth())+"%")
          inv = inv + obj.get_inv()
          val = val + obj.get_val()
      print ("\nTotal Initial Investment: $" + str(inv))
      print ("Current Value: $" + str(val))
      growth = val/inv *100.00
      print ("Overall Growth: " + str(growth) +"%")

    elif ans=="5":
      print ("\n Goodbye")
      ans = None
    else:
       print ("\n Not Valid Choice Try again")
