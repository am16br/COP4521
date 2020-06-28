#########################################################################
# Alexander Marcano - agm18h
# due 07/30/2020
# The program in this file is the work of Alexander Marcano, ..., ...
######################################################################

#python-env\Scripts\activate.bat
#Line used to enter python env in windows cmd

from flask import *

app = Flask(__name__)
#Default port is '127.0.0.1:5000'

#takes you to the home page
@app.route('/')                                                 #home page
def home():
    return render_template('index.html')

#if index is typed directly it redirects to '/'
@app.route('/index', methods=['GET'])                           #takes you to the route
def index():
    return redirect(url_for('home'))

#takes you to the home page
@app.route('/charts')                                                 #home page
def charts():
    return render_template('charts.html')

#takes you to the home page
@app.route('/tables')                                                 #home page
def tables():
    return render_template('tables.html')

#if this were the main module, run the application
if __name__ == '__main__':
    app.run()