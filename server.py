from flask import Flask, render_template, send_from_directory, request
from flask_cors import cross_origin
#from flask_login import LoginManager, UserMixin, login_required
import json
import mysql.connector
from datetime import datetime
from colorama import Fore, Back, Style
import os, sys
from collections import namedtuple
from dbutils import *
from dbopts import db_options

app = Flask(__name__);  # Create flask application


# Routes are how one maps URLs to what actions are taken
# We use decorators to map particular functions onto a route

# This route just gives access to the javascript files in the libs directory
# The return value is how the request was handled; in this case return
# the file from libs
@app.route('/libs/<path:path>')
def send_javascript(path):
    return send_from_directory('libs', path)



# This route returns our index page if the localhost URL is requested.
# Templates can contain fields that may be modified using Flask tools.
# We don't have any in index.html, but I'm using the render_template
# method anyway.
@app.route('/')
def show_root_page():
    return render_template('index.html')



# This route will be the location that we'll use to handle our POST request,
# put the data in the database, and send back a response
# The return value is in the format
# ResponseString, HTTP_CODE (int), HTTP_HEADERS (dict)
# The helper function generate_response will handing creating that
# Login is not required for this resource; it must be cross-origin
@app.route('/receive', methods=['POST'])
@cross_origin()
def process_post():
    print(Fore.BLUE + str(request.form) + Style.RESET_ALL)
    global db_options #Expose our options map
    try:
        #Open the database and a cursor
        cnx = mysql.connector.connect(**db_options)
        cursor = cnx.cursor()

        #Get the data and substituion string ready
        #request.form is a dictionary containing values sent by the client
        to_store = combine_data({'date':datetime.utcnow()}, request.form)

        #I'm using a helper method to generate the insertion command
        insert_cmd = generate_insertion('ReceivedData', to_store)

        #Execute the command and comit it
        try:
            cursor.execute(insert_cmd, to_store)
            cnx.commit()
        finally:
            cursor.close()

        #Send a success response
        return generate_response({'success':True}, 200)
    except Exception as e:
        print(e)
        #Note that something went wrong and send a fail response
        return generate_response({'success':False}, 400)
    finally:
        #Cleanup
        cnx.close()


# Try to be RESTful and return the URIs (based on IDs) and comments for each
# entry in our database.  We're not going to send the entire log entry because
# that will be quite large in practice.  Clicking the log ID will redirect
# us to a page that contains the entire log
# Login is required for this resource.
# It should not be cross-origin
@app.route('/getlogs', methods=['GET'])
#@login_required
def send_table():
    global db_options #Expose our database options
    try:
        #Open the database and a cursor
        cnx = mysql.connector.connect(**db_options)
        cursor = cnx.cursor(buffered=True)
        fields = ['id', 'date', 'comment', 'email', 'method']
        cmd = generate_get('ReceivedData', fields)
        try:
            cursor.execute(cmd)
            results = []
            CursorFields = namedtuple("CursorFields", fields)
            for cfields in map(CursorFields._make, cursor):
                d_results = {}
                for f in fields:
                    d_results[f] = str(getattr(cfields,f))
                results.append(d_results)
        finally:
            cursor.close()
        return generate_response({'success':True,'results':results}, 200)
    except Exception as e:
        print(e)
        return generate_response({'success':False}, 400)
    finally:
        cnx.close()



# This method will return the log given how the URL is setup.
# In this case if we wanted the events log for entry 10:
# http://foo.com/log/10/events
# Either the log will be returned or a 404 error
# Login is required for this resource_exists
# It should not be cross-origin
@app.route('/log/<string:id>/<string:logtype>')
#@login_required
def get_log(id, logtype):
    global db_options #Expose our database options
    try:
        #Open the database and a cursor
        cnx = mysql.connector.connect(**db_options)
        cursor = cnx.cursor(buffered=True)
        cmd = generate_get('ReceivedData', [logtype], 'WHERE id=' + id)
        try:
            cursor.execute(cmd)
            if not cursor.with_rows:
                return '', 404
            elif cursor.rowcount == 1:
                retval = cursor.fetchone()[0]
                return 'NULL' if retval is None else retval.replace('\n','<br/>'), 200, {'ContentType':'text/plain'}
            else:
                return '', 404
        except Exception as e:
            print(e)
            return '', 404
        finally:
            cursor.close()
    except Exception as e:
        print(e)
        return '', 404
    finally:
        cnx.close()



# Serve up our webpage template
# Login is required for this resource
@app.route('/logs')
#@login_required
def table_view():
    return render_template('logs.html')



# Run the Flask app
if __name__ == '__main__':
    port = 5000 if not len(sys.argv) == 2 else int(sys.argv[1])
    app.run('127.0.0.1', port=port)
