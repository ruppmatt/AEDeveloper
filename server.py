from flask import Flask, render_template, send_from_directory, request
import json
import mysql.connector
from datetime import datetime
from colorama import Fore, Back, Style
import os, sys


app = Flask(__name__);  # Create flask application

db_options = {
        'user':'root',
        'password':'ATestingPassword',
        'database':'PostTest',
        'host':'127.0.0.1',
        'raise_on_warnings':True
    }


#Routes are how one maps URLs to what actions are taken

#This route just gives access to the javascript files in the libs directory
#The return value is how the request was handled; in this case return
#the file from libs
@app.route('/libs/<path:path>')
def send_javascript(path):
    return send_from_directory('libs', path)


#This route returns our index page if the localhost URL is requested.
#Templates can contain fields that may be modified using Flask tools.
#We don't have any in index.html, but I'm using the render_template
#method anyway.
@app.route('/')
def show_root_page():
    return render_template('index.html')


# This route will be the location that we'll use to handle our POST request,
# put the data in the database, and send back a response
@app.route('/receive', methods=['POST'])
def process_post():
    global db_options #Expose our options map
    #Some debugging information
    #print(Fore.MAGENTA + type(request.form).__name__ + Style.RESET_ALL)
    #print(Fore.YELLOW + str(request.form) + Style.RESET_ALL)
    try:
        #Open the database and a cursor
        cnx = mysql.connector.connect(**db_options)
        cursor = cnx.cursor()

        #Get the data and substituion string ready
        to_store = combine_data({'date':datetime.now()}, request.form)
        insert_cmd = generate_insertion('ReceivedData', to_store)

        #Execute the command and comit it
        try:
            cursor.execute(insert_cmd, to_store)
            cnx.commit()
        finally:
            cursor.close()

        #Send a success response
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
    except Exception as e:
        #Note that something went wrong and send a fail response
        print('There was a problem connecting to the database: {}'.format(e))
        return json.dumps({'success':False}), 400, {'ContentType':'application/json'}
    finally:
        #Cleanup
        cnx.close()

# Try to be RESTful and return the URIs (based on IDs) and comments for each
# entry in our database.  We're not going to send the entire log entry because
# that will be quite large in practice.  Clicking the log ID will redirect
# us to a page that contains the entire log
@app.route('/tableview', methods=['GET'])
def send_table():
    global db_options #Expose our database options
    try:
        #Open the database and a cursor
        cnx = mysql.connector.connect(**db_options)
        cursor = cnx.cursor(buffered=True)
        cmd = 'SELECT id, date, comment from ReceivedData'
        try:
            cursor.execute(cmd)
            results = []
            for (id, date, comment) in cursor:
                results.append(json.dumps({'id':id, 'date':str(date), 'comment':comment}))
                #print('{} {} {}'.format(id, date, comment))
        finally:
            cursor.close()
        return json.dumps({'success':True,'results':results}), 200, {'ContentType':'application/json'}
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(Fore.RED + '{} {} {}'.format(exc_type, fname, exc_tb.tb_lineno) + Style.RESET_ALL)
        print('There was a problem retrieving the database table: {}'\
            .format(e));
        return {'success':False}, 400, {'ContentType':'application/json'}
    finally:
        cnx.close()


# Combine a base dictionary, d, with an additional dictionary j
# This function handles the case when information from outside of
# a HTTP request needs to get merged with another dictionary
def combine_data(d, j):
    for k,v in j.items():
        d[k]=v
    return d


# The MySQL connector needs the data in a particular format in order to insert
# it into the database.  It is a two part process: first create a template
# string that will be passed as the first parameter of cursor.execute.
# The string contains placeholders for the actual data.  In our case, these
# place holders are named in a Python-2 format-like manner.
# The dictionary of values to substitute the place-holding parameters is passed
# to the cursor.execute method where substitions are actually made.  (This
# method generates just the template string.)
def generate_insertion(db, data):
    #We need to play around to get the MySQL statement correct
    #when we're dealing with a dictionary worth of data
    ncol = len(data)
    cols = ', '.join(data.keys())  #List of our columns in order
    val_placeholder = ', '.join(map(lambda x: '%('+x+')s ', data.keys())) #Create our placeholders]
    insert_cmd =\
        'INSERT INTO ReceivedData ({columns}) VALUES ({values})'.format(
        columns=cols, values=val_placeholder)
    print(Fore.CYAN + insert_cmd + Style.RESET_ALL)
    return insert_cmd


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
