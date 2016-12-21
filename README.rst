README
======

The purpose of these files is to demonstrate how data from a webpage can be
set asynchronously using HTTP POST.  In this demonstration a JSON object is
sent to our Flask python server, which handles the request.  The data from the
POST is stored in a local mysql server and a response is sent back.

The following ports will be opened:

  + 5000  python Flask server

  + 3306  mysql server

The following webpages will be available at localhost:5000

  + /  The index
  + /logs  List all logs
  + /log/id/logname  Where id and logname are the log primary key and logname


SETUP
-----

PYTHON VIRTUAL ENVIRONMENT
~~~~~~~~~~~~~~~~~~~~~~~~~~

Python 3 is required for this particular setup.  A mysql server must be setup
and run on 3306 of localhost.  (Modify server.py to change the port).

In order to not corrupt the local python environment, we're going to be using
a virtual environment.  virtualenv should be installed.  (pip should also be
installed if you are using a modern distribution of python3).  If it is not
installed:

  shell> pip-3.x install virtualenv

where x is the python subversion.

You should then be able to create and use the python virtual environment.  To
do so you must first setup the venv folder, which will store our virtual
environment libraries:

  shell> virtualenv venv  #venv is folder where the python virtual environment library is stored

If you are having problems, you can manually specify the python executable:

  shell> virtualenv --python=/opt/local/bin/python3 venv  #For example

To switch into the virtual environment:

  shell> source venv/bin/activate

This will use the python interpreter created by virtualenv along with the
libraries we are about to install.

Once activated you'll see a (venv) above your prompt to indicate you are using
the virtual environment described by the contents of venv.

To quit the virtual environment, type:

  deactivate

Now that the virtual environment is installed, we can begin loading the
libraries we'll need.  They are listed in requirements.txt.  To install
them:

  pip install -r requirements.txt

The virtual environment is now ready.


MYSQL
~~~~~

Follow the instructions on dev.mysql.com:
  https://dev.mysql.com/doc/refman/5.7/en/osx-installation.html

Use the 'download' section of the mysql website to download the actual DMG
image.

Once installed, start the mysql server on port 3306:

  shell> sudo mysqld_safe --bind-address=127.0.0.1

Now you have to change the temporary password provided by the installer.  On
my machine (macOS), all of the executables are installed in:

  shell> /usr/local/mysql/bin

These files must be run as root because of how they were installed.  There are
directions on the Oracle MySQL site to change this behavior.

To change the password:

  shell> /usr/local/mysql/bin/mysql -u root -p'TempPassword'

And enter the password provided by the installer.

Then, in the mysql interface (Please use the password below):

  mysql> SET PASSWORD = PASSWORD('ATestingPassword');

  mysql> quit

Now we can load the sample database and tables provided:

    shell> /usr/local/mysql/bin/mysql -u root -p'ATestingPassword' -r mysql.dump

Note: There is a MySQL GUI for the Mac.  I recommend Sequel Pro.

  https://www.sequelpro.com/

When you open the sql database in Sequel Pro, make sure to select the
"Socket" type of login and provide your root credentials.

For our example, you can use the gui to navigate to the 'PostTest' database;
our requests will be stored in the ReceivedData table.



USAGE
-----

START-UP
~~~~~~~~

In a terminal window, make sure that the MySQL daemon is running:

  shell> sudo /usr/local/mysql/bin/mysql_safe --bind-address=127.0.0.1

(The bind-address part is to restrict access to the localhost.)

In another terminal window, start the python virtual environment created above:

  shell> source venv/bin/activate

As a reminder `deactivate` will exit the virtual environment.

Then start the web server:

  shell> python server.py


PAGES
~~~~~

From here, you can access the data-generation page at the URI:

  http://localhost:5000/

Clicking the button will send a JSON object to the server, which will store
it using the python mysql-connector in the database we created above.  A
response will be sent back to the webpage.

You can use Sequel Pro (above) to see the information stored in the database.
Log in via a "Socket" connection to localhost with the root username and
password.  The data is located in the database "PostTest".

To see all logs currently in the server as a table view, navigate to:

  http://localhost:5000/logs

From there you can select any of the icons after the comment section to pull
up individual logs in a separate page.  (Note the logs are formatted to be
displayed in the browser, so the text actually contains <br/> in it.  This
can be changed at a later time.  The URI for accessing the individual logs
has this scheme /log/ID/NAME where ID is the id of the log report and NAME
is the name of the log request from {log, events, messages, error}.  For
example, to get the full error log for the second bug report, the URI would
be:

  /log/2/log



SHUTDOWN
~~~~~~~~

To quit the server, type CTRL+C a few times in the terminal window to halt it.

To shutdown the MySQL server use:

  shell> sudo /usr/local/mysql/bin/mysqladmin -u root -p'ATestingPassword' shutdown
