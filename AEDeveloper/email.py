import hashlib
from flask_mail import Message
from .db import session
from .developer import mail
from .config import dev_email


def get_emailed_users():
    s = session()
    user_emails = []
    try:
        users = s.query(User).filter(User.email == True)
        for u in users:
            user_emails.append(u.email)
    except Exception as e:
        pass
    finally:
        s.close()
    return user_emails


def attach_receipents(msg):
    for email in get_emailed_users():
        msg.add_recepient(email)


def store_received_payload(received):
    fn = hashlib.md5().update(bytes(received)).hexdigest()




def mail_report_success(report):
    subject = 'AvidaED Report #{}'.format(report.id)
    body = 'Error report received.\n\n'
    fields = ['id', 'date', 'email', 'comment', '', 'version', 'userInfo', 'triggered']
    for f in fields:
        if f != '':
            body += '{}: {}\n'.format(f, report[f])
        else:
            body += '\n'
    msg = Message(subject, sender=dev_email, body=body)
    attach_recepients(msg)
    mail.send(msg)


def mail_report_error(received):
    store_payload(received)
    subject = 'AvidaED -- Unable to add report'
    body = 'A report was received that could not be processed.\n\n'
    body += 'The report payload is stored at {}.'
    msg = Message(subject, sender=dev_email, body=body)
    attach_recepients(msg)
    mail.send(msg)
