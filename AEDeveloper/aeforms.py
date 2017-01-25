from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField
from wtforms.validators import DataRequired, EqualTo, Length

pwd_length_msg = 'Passwords must be between 6 and 32 characters long'
user_length_msg = 'Username must be less than 32 characters.'
pwd_length_valid = Length(min=6, max=32, message=pwd_length_msg)

class AELoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired(), pwd_length_valid])

class AENewUserForm(FlaskForm):
    username = StringField('username',\
        validators=[DataRequired(), Length(min=1,max=32)])
    password1 = StringField('password',\
        validators=[DataRequired(), pwd_length_valid] )
    password2 = StringField('confirm password',\
        validators=[DataRequired(), pwd_length_valid, EqualTo('password1', message='Passwords must match')])
