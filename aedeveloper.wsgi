import os, sys

APP_DIR = '/var/www/wsgi-scripts/AEDeveloper'

activate_this = os.path.join(APP_DIR, 'venv/bin', 'activate_this.py')
exec(activate_this, dict(__file__=activate_this))
sys.path.insert(0,APP_DIR)

from AEDeveloper.developer import app as application

