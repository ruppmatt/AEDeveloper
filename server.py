from flask import Flask, render_template, send_from_directory, request
import json
import mysql.connector
from datetime import datetime


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
    print(request)
    try:
        cnx = mysql.connector.connect(**db_options)
        cursor = cnx.cursor()

        to_store = {'date':datetime.now(), 'data':'foo'}

        #We need to play around to get the MySQL statement correct
        #when we're dealing with a dictionary worth of data
        ncol = len(to_store)
        cols = ', '.join(to_store.keys())  #List of our columns in order
        val_placeholder = ', '.join(map(lambda x: '{'+x+'}', to_store)) #Create our placeholders]

        insert_cmd =\
            'INSERT INTO ReceivedData ({columns}) VALUES ({values})'.format(
            columns=cols, values=val_placeholder)
        print(insert_cmd)

        #The execute cmd will substitute the %s of values with to_store
        #keys
        print(insert_cmd.format(**to_store))
        cursor.execute(insert_cmd.format(**to_store))
        cnx.commit()
        cursor.close()
        return json.dumps({'success':True}, 200, {'ContentType':'application/json'})
    except Exception as e:
        print('There was a problem connecting to the database: {}'.format(e))
        return json.dumps({'success':False}, 400, {'ContentType':'application/json'})
    finally:
        cnx.close()

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
