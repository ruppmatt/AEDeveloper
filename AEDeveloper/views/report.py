from flask import Blueprint, render_template,request, redirect, abort, url_for
from ..developer import csrf, login_required, cross_origin
import pprint
from .. import db


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
    s = db.session()
    report = db.Report.from_post_request(request)
    s.add(report)
    s.add(db.Log(report_id=report.id, name='log', data=request.form['log']))
    s.commit()
    #for log in request.form['details']:
    #    l = db.Log(report_id=report.id, name=log.key(), data=log.value())
    #    s.commit()
    s.commit()
    return '', 400


# Try to be RESTful and return the URIs (based on IDs) and comments for each
# entry in our database.  We're not going to send the entire log entry because
# that will be quite large in practice.  Clicking the log ID will redirect
# us to a page that contains the entire log
# Login is required for this resource.
# It should not be cross-origin
@report.route('/report/all', methods=['GET'])
@login_required
def send_logs():
    global db_options #Expose our database options
    try:
        cnx = mysql.connector.connect(**db_options)
        cursor = cnx.cursor(buffered=True)
        fields = ['id', 'date', 'comment', 'email', 'method']
        cmd = generate_get('ReceivedData', fields)
        cursor.execute(cmd)
        CursorFields = namedtuple("CursorFields", fields)
        results = []
        for cfields in map(CursorFields._make, cursor):
            d_results = {}
            for f in fields:
                d_results[f] = str(getattr(cfields,f))
            results.append(d_results)
        cursor.close()
        return generate_response({'results':results}, 200)
    except Exception as e:
        return str(e), 500


# This method will return the log given how the URL is setup.
# In this case if we wanted the events log for entry 10:
# http://foo.com/log/10/events
# Either the log will be returned or a 404 error
# Login is required for this resource_exists
# It should not be cross-origin
@report.route('/report/<string:id>/<string:log>/<string:mode>')
@login_required
@csrf.exempt
def get_log(id, logtype):
    global db_options #Expose our database options
    try:
        #Open the database and a cursor
        cnx = mysql.connector.connect(**db_options)
        cursor = cnx.cursor(buffered=True)
        cmd = generate_get('ReceivedData', [logtype], 'WHERE id=' + id)
        try:
            cursor.execute(cmd)
            if not cursor.with_rows:
                return '', 404
            elif cursor.rowcount == 1:
                retval = cursor.fetchone()[0]
                return 'NULL' if retval is None else retval.replace('\n','<br/>'), 200, {'ContentType':'text/plain'}
            else:
                return '', 404
        except Exception as e:
            print(e)
            return '', 404
        finally:
            cursor.close()
    except Exception as e:
        print(e)
        return '', 404
    finally:
        cnx.close()



# Serve up our webpage template
# Login is required for this resource
@report.route('/report')
@login_required
def table_view():
    this_page = 'logs.html'
    return render_template(this_page, request=request, user=current_user)
