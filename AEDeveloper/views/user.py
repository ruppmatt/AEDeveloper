from flask import Blueprint, render_template, request, redirect, abort, url_for
from flask.globals import current_app
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from colorama import Fore as F
from colorama import Style as S
from werkzeug.local import LocalProxy
from ..userforms import *
from ..developer_identity import DeveloperIdentity, create_user, update_user, query_username
from ..web_utils import is_url_safe



user = Blueprint('user', __name__, template_folder='../templates/user')


# Create and initialize login manager
login_manager = LoginManager()
login_manager.login_view = "user.login"


# Get our app setup with the login manager
@user.record_once
def on_load(state):
    login_manager.init_app(state.app)


# This is the callback that flask login uses to retrieve a "user"
# In this case a "user" is a token for either a username/password in
# the database or a token token.
@login_manager.user_loader
def load_identity(user_id):
    #print(F.CYAN + str(user_id) + S.RESET_ALL)
    identity = DeveloperIdentity(tokenhash=user_id)
    retval = identity if identity.get_id() is not None else None
    ret_id = retval.get_id() if type(retval) != type(None) else 'Unauthorized'
    #print(F.YELLOW + str(ret_id) + S.RESET_ALL)
    return retval


# Default login page
# Successful logins will be registered
# Pages will redirect if available
@user.route('/login', methods=['GET', 'POST'])
def login():
    this_page = 'login.html'
    form = AELoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = DeveloperIdentity(username=form.username.data, password=form.password.data)
            if not user.is_authenticated:
                return render_template(this_page, form=form, login_error='Not authenticated')
            redirect_to = request.args.get('next')
            if not is_url_safe(redirect_to, request.host_url):
                return abort(400)
            login_user(user)
            return redirect(redirect_to) if redirect_to is not None else redirect('/')
        else:
            return render_template(this_page, form=form, login_error='Invalid username/password.')
    return render_template(this_page, form=form)



# Logout user
@user.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user.login'))



# Change user settings
@user.route('/user/settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    this_page = 'update_user.html'
    if request.method == 'POST':
        form = AEChangeUserForm()
        if form.validate_on_submit():
            try:
                new_user = update_user(form, current_user)
                redirect_to = request.args.get('next')
                logout_user()
                login_user(new_user)
                if not is_url_safe(redirect_to, request.host_url):
                    return 'User updated.', 200
                return redirect(redirect_to) if redirect_to is not None else redirect('/')
            except Exception as e:
                return render_template(this_page, request=request, form=form, error='Unable to update user. ' + str(e))
        else:
            return render_template(this_page, request=request, form=form, error='Unable to update user. ')
    if current_user.username is None:
        return 'No user session.', 400
    u = query_username(current_user.username)
    form = AEChangeUserForm(obj=u, password1='', password2='', oldpassword='')
    return render_template(this_page, request=request, form=form)



# User Management
@user.route('/user/manage')
@login_required
def show_management():
    return render_template('management.html')



@user.route('/user/create', methods=['GET', 'POST'])
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
