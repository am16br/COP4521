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
      stock = input("\nEnter stock ticker: ")
      #check for validity with function
      #Export data to csv
      #use csv to make charts/analysis
      # menus to choose timeframe, price (avg, adj close, etc), volume
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

