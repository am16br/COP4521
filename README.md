# COP4521 Group Project
Financial Advisor and Stock Analysis
Problem to solve:We wanted to create a web application that would allow users to easily find and analyze stocks while storing information regarding their portfolio. This application is a website that allows users to search for stocks and view data. The site generates a chart of the adjusted closing price for any stock where the user can choose the timeframe displayed. It also creates a table that includes the date, open, high, low, close, and adjusted close prices as well as daily volume. The site includes a page that allows users to create a stock portfolio that stores the stock information and fetches a live price. The portfolio shows individual stock growth as well an overall view of initial investment, current value, and growth/losses. The portfolio and stock data is stores in tables within an SQLite3 database. We planned to have additional analysis of individual stocks to help user's decide where their money is best placed, but we are still waiting for that to be implemented.
Interface: The interface is fairly straightforward and can be used without any instruction. Users can click buttons to determine stock timeframe, changes pages from the side dashboard, manage table to filter data in ascending/descending order for any field, or search for certain data. They are able to add stock to their portfolio and see any growth.
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
requests.
Other resources: Bootstrap templates to create aesthetically pleasing web-pages, course notes and resources for SQLite3 and flask. Other websites to help solve individual issues.
Division of Work:
Aidan Martin: Web scraping of stock data dating back up to 5 years, moving data into database, creation of portfolio and addition into database.
Alexander Marcano: Creation of webpages to be visually appealing, HTML site and coding, creation of charts using Charts.js in HTML, creation of tables.
Douglas Kendall: Stock analysis, including using stock data to create time series and any other relevant analysis to be outputted as .pdf reports


