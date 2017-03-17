from flask import Blueprint, render_template,request, redirect, abort, url_for
from ..developer import csrf, login_required, cross_origin
import pprint
from .. import db
from sqlalchemy import asc, desc
import json
from colorama import Fore, Style
import urllib

report = Blueprint('report', __name__, template_folder='../templates/report')



# This route will be the location that we'll use to handle our POST request,
# put the data in the database, and send back a response
# The return value is in the format
# ResponseString, HTTP_CODE (int), HTTP_HEADERS (dict)
# The helper function generate_response will handing creating that
# Login is not required for this resource; it must be cross-origin
@report.route('/report/receive', methods=['POST'])
@cross_origin()
@csrf.exempt
def process_post():
    try:
        s = db.session()
        report = db.Report.from_post_request(request)
        print(Fore.YELLOW, 'Here1', Style.RESET_ALL)
        s.add(report)
        print(Fore.YELLOW, 'Here2', Style.RESET_ALL)
        s.commit()
        print(Fore.YELLOW, 'Here3', Style.RESET_ALL)
        logs = request.get_json(force=True)['logs']
        for name,data in logs.items():
            print(Fore.BLUE, name, data, Style.RESET_ALL)
            l = db.Log(report_id=report.id, name=name, data=data)
            s.add(l)
        s.commit()
        print(Fore.YELLOW, 'Here', Style.RESET_ALL)
        return 'OK', 200
    except Exception as e:
        print(Fore.RED, str(e), Style.RESET_ALL)
        return str(e), 403


# Try to be RESTful and return the URIs (based on IDs) and comments for each
# entry in our database.  We're not going to send the entire log entry because
# that will be quite large in practice.  Clicking the log ID will redirect
# us to a page that contains the entire log
# Login is required for this resource.
# It should not be cross-origin
@report.route('/report/all', methods=['GET'])
@login_required
def send_log_metadata():
    s = db.session()
    rquery = s.query(db.Report,db.Log).order_by(desc(db.Report.date))
    fields = ['id', 'date', 'triggered', 'email', 'comment', 'version', 'userAgent', 'userInfo', 'vars', 'screenSize', 'error']
    arr = []
    print(rquery.count())
    for report in rquery.all():
        d = {}

        for f in fields:
            if f != 'date':
                d[f] = report.Report.__getattribute__(f)
            else:
                d[f] = report.Report.date.isoformat()
        l = []
        print(Fore.MAGENTA, len(report.Report.logs), Style.RESET_ALL)
        for log in report.Report.logs:
            l.append(log.name)
        print(l)
        d['logs'] = l
        arr.append(d)
    return json.dumps(arr), 200


# This method will return the log given how the URL is setup.
# In this case if we wanted the events log for entry 10:
# http://foo.com/log/10/events
# Either the log will be returned or a 404 error
# Login is required for this resource_exists
# It should not be cross-origin
@report.route('/report/<string:id>/<string:log>/<string:mode>')
@login_required
def get_log(id, logtype, mode):
    s = db.session()
    lquery = s.query(Log).filter(db.Log.report_id==id, db.Log.name==name)
    try:
        log = lquery.one()
        return log['data'], 290
    except Exception as e:
        return '', 404


# Serve up our webpage template
# Login is required for this resource
@report.route('/report')
@login_required
def table_view():
    this_page = 'logs.html'
    return render_template(this_page, request=request, user=current_user)
