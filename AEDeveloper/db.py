from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import create_engine, Column, ForeignKey, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Integer, String, Boolean, DateTime, Enum, LargeBinary, Text
import enum
from .dbopts import dbopts
from . import field_sizes as size
import datetime
import json
from colorama import Fore, Style



engine = create_engine('mysql+mysqlconnector://root:ATestingPassword@localhost/test')
session = sessionmaker()
session.configure(bind=engine)

Base = declarative_base(bind=engine)
metadata = Base.metadata


class PrivlegeType(enum.Enum):
    report = 'report'
    user = 'user'
    token = 'token'
    admin = 'admin'
    notification = 'notification'


"""
 Database tables; the foreign key constraints
 use of onupdate/ondelete requires a compatible database
 backend.  For the sake of some utilities, otherwise binary
 byte strings will be stored as UTF-8 strings.
"""

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer(), primary_key=True)
    username = Column(String(size.username))
    password = Column(LargeBinary(size.password))
    fullname = Column(String(size.fullname))
    tokenhash = Column(String(size.password))
    email = Column(String(size.email))
    activated = Column(Boolean())
    lastlogin = Column(DateTime())
    deleted = Column(Boolean())

    def __init__(self, **kw):
        self.username = kw['username']
        self.password = kw['password']
        self.tokenhash = kw['tokenhash']
        self.fullname = kw['fullname']
        self.email = kw['email'] if 'email' in kw else None
        self.activated = kw['activated'] if 'activated' in kw else False
        self.deleted = kw['deleted'] if 'deleted' in kw else False


class Token(Base):
    __tablename__ = 'token'
    id = Column(Integer(), primary_key=True)
    token = Column(LargeBinary(size.password))
    activated = Column(Boolean)
    lastlogin = Column(DateTime())
    expiration = Column(DateTime())
    deleted = Column(Boolean())

    def __init__(self, **kw):
        self.token = kw['token']
        self.activated = kw['activated']
        self.deleted = kw['deleted']


class Privilege(Base):
    __tablename__ = 'privilege'
    id = Column(Integer(), primary_key=True)
    privlege = Column(String(size.privlege))
    description = Column(String(size.privlege_description))
    category = Column(Enum(PrivlegeType))

    def __init__(self, privlege, description=None, category=None):
        self.privlege = privlege
        self.description = description
        self.category = PrivlegeType(category)



class UserPrivlege(Base):
    __tablename__ = 'user_privlege'
    id = Column(Integer(), primary_key=True)
    user_id = ForeignKey('user.id', onupdate='CASCADE', ondelete='CASCADE');
    privlege_id = Column(Integer(), ForeignKey('privilege.id', onupdate='CASCADE', ondelete='CASCADE'))


class TokenPrivlege(Base):
    __tablename__ = 'token_privlege'
    id = Column(Integer(), primary_key=True)
    token_id = ForeignKey('token.id', onupdate='CASCADE', ondelete='CASCADE')
    privlege_id = Column(Integer(), ForeignKey('privilege.id', onupdate='CASCADE', ondelete='CASCADE'))


class Report(Base):
    __tablename__ = 'report'
    id = Column(Integer(), primary_key=True)
    ip = Column(String(31,), nullable=True)
    userAgent = Column(String(size.user_agent), nullable=True)
    userInfo = Column(String(size.user_info), nullable=True)
    vars = Column(String(size.vars), nullable=True)
    date = Column(DateTime(), nullable=True)
    email = Column(String(size.email), nullable=True)
    triggered = Column(Enum('userTriggered','errorTriggered'), nullable=True)
    comment = Column(String(size.comment), nullable=True)
    logs = relationship('Log', back_populates='report')
    version = Column(String(size.version), nullable=True)
    screenSize = Column(String(size.screen_size), nullable=True)
    error = Column(String(size.error), nullable=True)

    def __init__(self, **kw):
        self.ip = kw['ip'] if 'ip' in kw else None
        self.userAgent = kw['userAgent'] if 'userAgent' in kw else None
        self.userInfo = kw['userInfo'] if 'userInfo' in kw else None
        self.vars = kw['vars'] if 'vars' in kw else None
        self.date = kw['date'] if 'date' in kw else None
        self.email = kw['email'] if 'email' in kw else None
        self.triggered = kw['triggered'] if 'triggered' in kw else None
        self.comment = kw['comment'] if 'comment' in kw else None
        self.screenSize = kw['screenSize'] if 'screenSize' in kw else None
        self.error = kw['error'] if 'error' in kw else None
        self.version = kw['version'] if 'version' in kw else None


    @classmethod
    def from_post_request(cls, r):
        f = r.get_json(force=True)
        print(Fore.MAGENTA,  f.keys(), Style.RESET_ALL)
        print(r.user_agent)
        d = {
            'ip':r.remote_addr,
            'userAgent':str(r.user_agent),
            'userInfo':f['userInfo'] if 'userInfo' in f else None,
            'vars':json.dumps(f['vars']) if 'vars' in f else None,
            'date':datetime.datetime.utcnow(),
            'email':f['email'] if 'email' in f else None,
            'triggered':f['triggered'] if 'triggered' in f else None,
            'comment':f['comment'] if 'comment' in f else None,
            'error':f['error'] if 'error' in f else None,
            'screenSize':f['screenSize'] if 'screenSize' in f else None,
            'version':f['version'] if 'version' in f else None,
        }
        return cls(**d)


class Log(Base):
    __tablename__ = 'log'
    id = Column(Integer(), primary_key=True)
    report_id = Column(Integer(), ForeignKey('report.id', onupdate='CASCADE', ondelete='CASCADE'))
    name = Column(String(size.log_name))
    data = Column(Text())
    report = relationship('Report', back_populates='logs')

    def __init__(self, **kw):
        self.report_id = kw['report_id']
        self.name = kw['name']
        self.data = kw['data']


def init_db():
    global engine, Base, session
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all()
    populate_privleges(Base, session)


def populate_privleges(Base, session):
    global Privilege
    s = session()
    s.add_all([
        Privilege('REPORT_GET', 'Retrieve report meta information and access URI', 'report'),
        Privilege('REPORT_POST', 'POST a report to the database', 'report'),
        Privilege('REPORT_DEL', 'Delete a report', 'report'),
        Privilege('REPORT_RESOLVE', 'Mark/DeMark a report as resolved.', 'report'),
        Privilege('USER_CREATE', 'Create a user', 'user'),
        Privilege('USER_ACTIVATE', 'Activate a user', 'user'),
        Privilege('USER_ALTER', 'Alter a user', 'user'),
        Privilege('USER_DEL', 'Delete a user', 'user'),
        Privilege('TOKEN_CREATE', 'Create a token', 'token'),
        Privilege('TOKEN_ALTER', 'Alter a token', 'token'),
        Privilege('TOKEN_DEL', 'Delete a token', 'token'),
        Privilege('NOTIFY_REPORT_POST', 'Notify user of a new report', 'notification'),
        Privilege('NOTIFY_USER_REQUEST', 'Notify when a new user requests access', 'notification'),
        Privilege('TOKEN_ACTIVATE', 'Activate/Deactivate a token', 'token'),
        Privilege('ADMIN_ACCESSVIEW', 'View an overview of current access privleges', 'admin')
    ])
    s.commit()
