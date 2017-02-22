from flask import Flask, render_template, send_from_directory, request
from flask_cors import cross_origin, CORS
from flask_wtf.csrf import CSRFProtect
from .db import init_db


# Prepare database
init_db()


# Setup our app
app = Flask(__name__);  # Create flask application
app.secret_key = 'Atefyej/ucithAmHasshacivyass2Om5'
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Reload our templates as we go along

# Cross-site resource sharing support
CORS(app, supports_credentials=True)

# Enable cross-site resource forgery protection
csrf = CSRFProtect(app)

from .views.user import user, login_required
from .views.report import report

# Register our blueprints
app.register_blueprint(user)
app.register_blueprint(report)






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


# Run the Flask app
if __name__ == '__main__':
    port = 5000 if not len(sys.argv) == 2 else int(sys.argv[1])
    app.run('127.0.0.1', port=port, debug=True)
