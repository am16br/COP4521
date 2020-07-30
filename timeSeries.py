

import fbprophet as prophet
import numpy as np
import pandas as pd
import pandas_datareader.data as pdr
import datetime
import featureSelection as fs


class timeseries:
  def __init__(self):
    self.regressors = pd.DataFrame()

  def addRegressors(self,start,end):
    symbols = pdr.get_nasdaq_symbols

  def run(self,stock,useFS = False):

    start = datetime.datetime(2017,1,1)
    end = datetime.datetime.now()
    df = pdr.DataReader(stock,'yahoo',start,end)
    df = df.reset_index()
    print(df)
    # df.reset_index(inplace=True)
    # df.set_index('Date', inplace=True)
    # df = df.drop('Symbol', axis=1)
    d=pd.DataFrame()
    d['y'] = df['High']
    d['DS'] = pd.to_datetime(df['Date'])


    p = prophet.Prophet()

    p.fit(d)
    future = p.make_future_dataframe(periods=30,freq='D')
    forecast = p.predict(future)
    return forecast

