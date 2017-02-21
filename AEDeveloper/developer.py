from flask import Flask, render_template, send_from_directory, request, redirect, abort, url_for
from flask_cors import cross_origin, CORS
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
import json
import mysql.connector
from datetime import datetime
import os, sys
from collections import namedtuple
from dbutils import *
from urllib.parse import urlparse, urljoin
from developer_identity import DeveloperIdentity, create_user, update_user, query_username
from aeforms import *
from db import init_db
import traceback
from colorama import Fore as F
from colorama import Style as S


# Setup our app
app = Flask(__name__);  # Create flask application
app.secret_key = 'Atefyej/ucithAmHasshacivyass2Om5'
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Reload our templates as we go along


# Cross-site support
CORS(app, supports_credentials=True)


# Create and initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# This is the callback that flask login uses to retrieve a "user"
# In this case a "user" is a token for either a username/password in
# the database or a token token.
@login_manager.user_loader
def load_identity(user_id):
    print(F.CYAN + str(user_id) + S.RESET_ALL)
    identity = DeveloperIdentity(tokenhash=user_id)
    retval = identity if identity.get_id() is not None else None
    ret_id = retval.get_id() if retval is not None else 'Unauthorized'
    print(F.YELLOW + ret_id + S.RESET_ALL)
    return retval


# CSRF setup
csrf = CSRFProtect()
csrf.init_app(app)



# Routes are how one maps URLs to what actions are taken
# We use decorators to map particular functions onto a route

# This route just gives access to the javascript files in the libs directory
# The return value is how the request was handled; in this case return
# the file from libs
@app.route('/libs/<path:path>')
def send_javascript(path):
    return send_from_directory('libs', path)


# Expose our CSS folder
@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)


# This route returns our index page if the localhost URL is requested.
# Templates can contain fields that may be modified using Flask tools.
# We don't have any in index.html, but I'm using the render_template
# method anyway.
@app.route('/')
@login_required
def developer_root():
    return render_template('developer.html', request=request)


@app.route('/test')
def show_test():
    return render_template('test.html')

# This route will be the location that we'll use to handle our POST request,
# put the data in the database, and send back a response
# The return value is in the format
# ResponseString, HTTP_CODE (int), HTTP_HEADERS (dict)
# The helper function generate_response will handing creating that
# Login is not required for this resource; it must be cross-origin
@app.route('/receive', methods=['POST'])
@cross_origin()
@csrf.exempt
def process_post():
    try:
        return 500
    except Exception as e:
        print(e)
        return 500



# Try to be RESTful and return the URIs (based on IDs) and comments for each
# entry in our database.  We're not going to send the entire log entry because
# that will be quite large in practice.  Clicking the log ID will redirect
# us to a page that contains the entire log
# Login is required for this resource.
# It should not be cross-origin
@app.route('/getlogs', methods=['GET'])
@login_required

@csrf.exempt
def send_logs():
    global db_options #Expose our database options
    try:
        cnx = mysql.connector.connect(**db_options)
        cursor = cnx.cursor(buffered=True)
        fields = ['id', 'date', 'comment', 'email', 'method']
        cmd = generate_get('ReceivedData', fields)
        cursor.execute(cmd)
        CursorFields = namedtuple("CursorFields", fields)
        results = []
        for cfields in map(CursorFields._make, cursor):
            d_results = {}
            for f in fields:
                d_results[f] = str(getattr(cfields,f))
            results.append(d_results)
        cursor.close()
        return generate_response({'results':results}, 200)
    except Exception as e:
        return str(e), 500


# This method will return the log given how the URL is setup.
# In this case if we wanted the events log for entry 10:
# http://foo.com/log/10/events
# Either the log will be returned or a 404 error
# Login is required for this resource_exists
# It should not be cross-origin
@app.route('/log/<string:id>/<string:logtype>')
@login_required
@csrf.exempt
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
@login_required
def table_view():
    this_page = 'logs.html'
    return render_template(this_page, request=request, user=current_user)



# Default login page
# Successful logins will be registered
# Pages will redirect if available
@app.route('/login', methods=['GET', 'POST'])
def login():
    this_page = 'login.html'
    form = AELoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = DeveloperIdentity(username=form.username.data, password=form.password.data)
            if not user.is_authenticated:
                return render_template(this_page, form=form, login_error='Not authenticated')
            redirect_to = request.args.get('next')
            if not is_url_safe(redirect_to):
                return abort(400)
            login_user(user)
            return redirect(redirect_to) if redirect_to is not None else redirect('/')
        else:
            return render_template(this_page, form=form, login_error='Invalid username/password.')
    return render_template(this_page, form=form)



# Logout user
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))



# Change user settings
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    this_page = 'update_user.html'
    form = AEChangeUserForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                new_user = update_user(form, current_user)
                redirect_to = request.args.get('next')
                logout_user()
                login_user(new_user)
                if not is_url_safe(redirect_to):
                    return 'User updated.', 200
                print(F.GREEN + redirect_to + S.RESET_ALL)
                return redirect(redirect_to) if redirect_to is not None else redirect('/')
            except Exception as e:
                return render_template(this_page, request=request, form=form, error='Unable to update user. ' + str(e))
        else:
            return render_template(this_page, request=request, form=form, error='Unable to update user. ')
    if current_user.username is None:
        return 'No user session.', 400
    u = query_username(current_user.username)
    form = AEChangeUserForm(obj=u, password1="", password2="", oldpassword="")
    return render_template(this_page, request=request, form=form)



# User Management
@app.route('/manage')
@login_required
def show_management():
    return render_template('management.html')



@app.route('/newuser', methods=['GET', 'POST'])
#@login_required
def newuser():
    this_page = 'new_user.html'
    form = AENewUserForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                create_user(form)
                return 'User created.', 200
            except Exception as e:
                return render_template(this_page, request=request, form=form, error='Unable to add user.' + str(e))
        else:
            return render_template(this_page, request=request, form=form, error='Unable to add user.')
    return render_template(this_page, request=request, form=form)



def is_url_safe(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


# Run the Flask app
if __name__ == '__main__':
    init_db()
    port = 5000 if not len(sys.argv) == 2 else int(sys.argv[1])
    app.run('127.0.0.1', port=port, debug=True)
