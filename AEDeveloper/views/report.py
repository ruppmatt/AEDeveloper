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
        s.add(report)
        s.commit()
        logs = request.get_json(force=True)['logs']
        for name,data in logs.items():
            print(Fore.RED + name + Style.RESET_ALL)
            l = db.Log(report_id=report.id, name=name, data=data)
            s.add(l)
        s.commit()
        return '', 200
    except Exception as e:
        return '', 403


# Try to be RESTful and return the URIs (based on IDs) and comments for each
# entry in our database.  We're not going to send the entire log entry because
# that will be quite large in practice.  Clicking the log ID will redirect
# us to a page that contains the entire log
# Login is required for this resource.
# It should not be cross-origin
@report.route('/report/all', methods=['GET'])
@login_required
def send_all_report_metadata():
    s = db.session()
    rquery = s.query(db.Report).order_by(desc(db.Report.date))
    arr = []
    for report in rquery.all():
        arr.append(generate_report_metadata_dict(report))
    return json.dumps(arr), 200


@report.route('/report/<int:id>')
@login_required
def send_report_metadata(id):
    try:
        s = db.session()
        rquery = s.query(db.Report).filter(db.Report.id == id)
        if rquery.count() == 1:
            return json.dumps(generate_report_metadata_dict(rquery.one()))
        else:
            raise IndexError
    except Exception as e:
        return str(e), 404



def generate_report_metadata_dict(report):
    d = {}
    fields = ['id', 'date', 'triggered', 'email', 'comment', 'version', 'userAgent', 'userInfo', 'vars', 'screenSize', 'error']
    for f in fields:
        if f != 'date':
            d[f] = report.__getattribute__(f)
        else:
            d[f] = report.date.isoformat()
    l = []

    for log in report.logs:
        l.append(log.name)
    d['logs'] = l
    return d


# This method will return the log given how the URL is setup.
# In this case if we wanted the events log for entry 10:
# http://foo.com/log/10/events
# Either the log will be returned or a 404 error
# Login is required for this resource_exists
# It should not be cross-origin
@report.route('/report/<int:id>/<string:log>/<string:mode>')
@login_required
def get_log(id, log, mode):
    session_parsing = {'ui-avida':'--uiA', 'avida-ui':'--Aui', 'ui-debug':'--uiD', 'avida-debug':'--avD', 'user-actions':'--usr'}
    s = db.session()
    parse_session_log = True if log in session_parsing.keys() else False
    log_name = log if not parse_session_log else 'session'
    lquery = s.query(db.Log).filter(db.Log.report_id==id, db.Log.name==log_name)
    try:
        log_entry = lquery.one()
        if mode == 'raw':
            log_data = log_entry.data if not parse_session_log else parse_session_data(session_parsing[log], log_entry.data)
            log_data = log_data.replace('\n','<br>')
            return log_data, 200
        elif mode == 'html':
            return render_template('log_html.html', report_id=id, log_name=log);
        else:
            return '', 404
    except Exception as e:
        return str(e), 500


# Serve up our webpage template
# Login is required for this resource
@report.route('/report')
@login_required
def report_table_view():
    return render_template('reports.html')
