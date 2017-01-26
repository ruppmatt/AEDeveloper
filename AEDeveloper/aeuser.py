from flask_login import LoginManager, UserMixin
from dbopts import db_options
from dbutils import *
import mysql.connector
import pdb
import bcrypt

class AEUserException(Exception):
    pass

class UserExistsException(AEUserException):
    def __str__(self):
        return 'User exists.'


class AEUser(UserMixin):

    def __init__(self, username):
        self.id = username



def validate_user(username, password):
    #Open the database and a cursor
    try:
        cnx = mysql.connector.connect(**db_options)
        cursor = cnx.cursor(buffered=True)
        print(mysql.connector.paramstyle)
        cursor.execute("SELECT password FROM Users WHERE username = %(username)s", {'username':username})
        if cursor.rowcount == 1:
            hashedpw = cursor.fetchone()[0]
            retval = bcrypt.checkpw(password.encode('utf-8'), hashedpw)
            return retval
        else:
            print('Other problems.')
            return False
    except Exception as e:
        print(str(e))


def create_user(username, password):
    #Open the database and a cursor
    cnx = mysql.connector.connect(**db_options)
    cursor = cnx.cursor(buffered=True)
    cmd = generate_get('Users', ['username'], 'WHERE username=\'' + username + '\'')
    results = cursor.execute(cmd)
    print(results, cursor.rowcount)
    if not cursor.rowcount == 0:
        raise UserExistsException
    userdata = {\
        'username':username,\
        'password':bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())\
        }
    cmd = generate_insertion('Users', userdata)
    cursor.execute(cmd, userdata)
    cnx.commit()
