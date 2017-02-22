from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField
from wtforms.validators import DataRequired, EqualTo, Length
from  . import field_sizes as size

pwd_length_msg = 'Passwords must be between 6 and 32 characters long'
user_length_msg = 'Username must be betweeb 1 abd 32 characters.'
fullname_length_msg = 'Full names must be between 1 and 128 characters long'

pwd_length_valid = Length(min=1, max=size.password, message=pwd_length_msg)

class AELoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired(), pwd_length_valid])


class AENewUserForm(FlaskForm):
    fullname = StringField('full name', \
            validators=[DataRequired(), Length(min=1,max=size.fullname, message=fullname_length_msg)])
    email = StringField('email', validators=[Length(max=size.email)])
    username = StringField('username',\
        validators=[DataRequired(), Length(min=1,max=size.username, message=user_length_msg)])
    password1 = StringField('password',\
        validators=[DataRequired(), pwd_length_valid] )
    password2 = StringField('confirm password',\
        validators=[DataRequired(), pwd_length_valid, EqualTo('password1', message='Passwords must match')])


class AEChangeUserForm(AENewUserForm):
    oldpassword = StringField('old password',
        validators=[DataRequired(), pwd_length_valid])
