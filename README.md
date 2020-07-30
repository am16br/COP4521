# COP4521 Group Project
Financial Advisor and Stock Analysis
This application is a website that allows users to search for stocks and view data. The site generates a chart of the adjusted closing price for any stock where the user can choose the timeframe displayed. It also creates a table that includes the date, open, high, low, close, and adjusted close prices as well as daily volume. The site includes a page that allows users to create a stock portfolio that stores the stock information and fetches a live price. The portfolio shows individual stock growth as well an overall view of initial investment, current value, and growth/losses. The portfolio and stock data is stores in tables within an SQLite3 database. We planned to have additional analysis of individual stocks to help user's decide where their money is best placed, but we are still waiting for that to be implemented.
Required Libraries:
(may need to be installed depending on current system packages)
flask,
sqlite3,
os,
csv,
pandas,
pandas_datareader.data,
datetime  (date),
yahoo_fin (stock_info),
requests,


