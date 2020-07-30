import timeSeries
import pandas as pd 

t = timeSeries.timeseries()
df = t.run('aapl')
print (df)