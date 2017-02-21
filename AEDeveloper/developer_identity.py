from flask_login import UserMixin
import bcrypt
from db import session, User, Token
from sqlalchemy.sql.expression import exists
from colorama import Fore, Back, Style
import hashlib
from itertools import cycle
import base64
from enum import Enum

class SessionType(Enum):
    NONE = 0
    USER = 1
    TOKEN = 2


class DeveloperIdentityException(Exception):
    pass

class IdentityExistsException(DeveloperIdentityException):
    def __str__(self):
        return 'User exists.'

class IdentityIsNotValid(DeveloperIdentityException):
    def __str__(self):
        return 'Invalid identity.'

class IdentityMultipleFoundException(DeveloperIdentityException):
    def __str__(self):
        return 'Multiple identities were found.'

class IdentityNotFoundException(DeveloperIdentityException):
    def __str__(self):
        return 'Identity not found.'

class IdentityNotAuthenticated(DeveloperIdentityException):
    def __str__(self):
        return 'Identity not authenticated.'


"""
DeveloperIdentity

A developer identity is the class that flask login users to handle user
sessions.  It can be initialized in one of two ways: either by providing the
initializer a tokenhash, which is either a unicode representation of an
access token or both a unicode username in password.

Because the login retrieval session used by flask_login can only handle a
single unicode input for the callback, username/password combinations are
changed into a token that is stored in the database's user table.  Tokens
are simply stored in the token table.
"""
class DeveloperIdentity(UserMixin):

    def __init__(self, **kw):
        self.id = None
        self.username = None
        self.session_type = SessionType.NONE
        if 'tokenhash' in kw:
            self.id = kw['tokenhash']
            u = query_id(kw['tokenhash'])
            if isinstance(u, User):
                self.username = u.username
                self.session_type = SessionType.USER
            elif isinstance(u, Token):
                self.username = '(Token)'
                self.session_type = SessionType.TOKEN
        else:
            u = query_username(kw['username'])
            if u is not None and password_ok(kw['password'], u.password):
                self.id = u.tokenhash
                self.username = u.username
                self.session_type = SessionType.USER


    def get_id(self):
        return self.id if self.id is not None and self.is_authenticated and self.is_active else None

    def is_user(self):
        return self.session_type == SessionType.USER


    @property
    def is_authenticated(self):
        token = query_id(self.id)
        if token is not None and token.activated and not token.deleted:
            return True
        return False

    @property
    def is_active(self):
        token = query_id(self.id)
        if token is not None and token.activated and not token.deleted:
            return True
        return False


"""
Retrieve either a single user or token based upon identity id.  Return
None if it is not available.
"""
def query_id(id):
    s = session()
    q = s.query(User).filter(User.tokenhash == id)
    try:
        if q.one():
            u = q.first()
            if u.activated and not u.deleted:
                return u
        else:
            q = s.query(Token).filter(Token.token == id)
            if q.one():
                t = q.first()
                if t.activated and not t.deleted:
                    return t
    except Exception as e:
        return None



def query_username(u):
    s = session()
    q = s.query(User).filter(User.username == u)
    try:
        if q.one():
            return q.first()
        else:
            return None
    except Exception as e:
        return None



"""
Create a user from a WTF Form.
"""
def create_user(form):
    s = session()
    if s.query(User).filter(User.username == form.username.data).count() > 0:
        raise IdentityExistsException
    password = crypt_password(form.password1.data)
    tokenhash = generate_tokenhash(form.username.data, form.password1.data)
    u = User(username = form.username.data,
        password = password,
        tokenhash = tokenhash,
        fullname = form.fullname.data,
        email = form.email.data)
    u.activated = True
    u.deleted = False
    s.add(u)
    s.commit()



"""
Update a user's information.
"""
def update_user(form, current_user):
    s = session()
    u = s.query(User).filter(User.username == current_user.username).first()
    if u is None:
        raise IdentityIsNotValid
    if not password_ok(form.oldpassword.data, u.password):
        raise IdentityNotAuthenticated
    u.username = form.username.data
    u.password = crypt_password(form.password1.data)
    u.tokenhash = generate_tokenhash(form.username.data, form.password1.data)
    u.fullname = form.fullname.data
    u.email = form.email.data
    s.commit()
    return DeveloperIdentity(tokenhash=u.tokenhash)



"""
Check a user's password
"""
def password_ok(pwd, pwd_hash):
    return bcrypt.checkpw(unicode_b64_sha256(pwd), pwd_hash)

"""
Encode SHA256 value of byte string in base64
"""
def bytes_b64_sha256(b):
    return base64.b64encode(hashlib.sha256(b).digest())


"""
Encode SHA256 value of a unicode string in base64
"""
def unicode_b64_sha256(s):
    return bytes_b64_sha256(bytes(s, 'utf-8'))


"""
Encrypt password
"""
def crypt_password(s):
    return crypt_sha256(s)



"""
Encrypt a string
sha256 is used because bcrypt has a limit of 72 characters
"""
def crypt_sha256(s):
    return bcrypt.hashpw(unicode_b64_sha256(s), bcrypt.gensalt())


"""
Because tokens and usernames/passwords need to be stored the same for retrieval,
(and the latter pair needs to be aware of password changes), a token is created
from the hashes of the username and password and stored in the User table.
"""
def generate_tokenhash(username, password):
     return base64.b64encode(
        bytes_xor(
            hashlib.sha256(bytes(username, 'utf-8')).digest(),
            hashlib.sha256(bytes(password, 'utf-8')).digest()
            )
        )


"""
xor two byte strings
"""
def bytes_xor(b1, b2):
    if len(b1) <= len(b2):
        b2,b1 = b1,b2
    return bytes(''.join(map(lambda x: chr( x[0]  ^ x[1] ), zip(b1, cycle(b2)))), 'utf-8')
