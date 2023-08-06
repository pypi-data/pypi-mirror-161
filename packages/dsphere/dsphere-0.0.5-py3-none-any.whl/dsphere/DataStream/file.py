import dsphere.defaults as defaults
import os
import json
import datetime
import shutil
import psutil
import subprocess
import re
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import dsphere.DataStream.executors as executors
import dsphere.connectors as con
import dsphere.DataStream.syncs as sync
import dsphere.DataStream.modelers as model
import dsphere.DataStream.archive as archive
from dsphere.FeatureSpace import FeatureSpace
import tempfile
import sys

class dotdict(dict):
    """dot.notation access to dictionary properties"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
DEFAULTS = dotdict(defaults.DEFAULTS)


def _create_filename(self, notebook_filename):
    # Remove all non-word characters (everything except numbers and letters)
    output_filename = re.sub(r"[^\w\s\.]", '', notebook_filename)

    # Replace all runs of whitespace with a single dash
    output_filename = re.sub(r"\s+", '_', output_filename)

    # Replace .ipynb with .py
    output_filename = re.sub(r".ipynb", ".py", output_filename)

    return output_filename.lower()

def _convert_ipynb_to_py(self, ipynb_json, output_py_file, comment_linemagic=True):
    code = json.load(open(ipynb_json))

    with open(output_py_file, 'w') as f:
        for cell in code['cells']:
            if cell['cell_type'] == 'code':
                #f.write('# -------- code --------')
                for line in cell['source']:
                    if (line[0]=='%' or line[0]=='!') and comment_linemagic:
                        f.write('\n#{}'.format(line)) #, end='')
                    else:
                        f.write(line) #, end='')
                f.write('\n')
            elif cell['cell_type'] == 'markdown':
                #f.write('# -------- markdown --------')
                for line in cell['source']:
                    f.write("\n#{}".format(line)) #, end='')
                f.write('\n')

# https://realpython.com/python-send-email/
def _send_email(self, from_cnx, to_cnx, subject, body):
    port = from_cnx['port'] 
    password = from_cnx['password']
    smtp_host = from_cnx['host']
    sender_email = from_cnx['address'] 
    sender_name = from_cnx.get('name', None)
    receiver_name = to_cnx.get('name', None)
    receiver_email = to_cnx['address']

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = "{} <{}>".format(sender_name, sender_email) or sender_email
    message["To"] = "{} <{}>".format(receiver_name, receiver_email) or receiver_email

    # Create the plain-text and HTML version of your message
    text = """\
    {}""".format(body)
    html = """\
    <html>
      <body>
        <p>{}
        </p>
      </body>
    </html>
    """.format(body)

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create a secure SSL context
    context = ssl.create_default_context()
    print("Connecting to SMTP server using SSL...")

    # Try to log in to server and send email
    server = None
    try:
        server = smtplib.SMTP(smtp_host, port)
        print("...created server: {}:{}".format(smtp_host, port))
        #server.ehlo(sender_name) # Can be omitted
        #print("...ehlo")
        server.starttls(context=context) # Secure the connection
        print("...TTLS started")
        #server.ehlo(sender_name) # Can be omitted
        #print("...connected")
        server.login(sender_email, password)
        print("...logged in")
        server.sendmail(sender_email, receiver_email, message.as_string())
        print("...email sent")
    except Exception as e:
        # Print any error messages to stdout
        print("Error in SFTP send occurred:", e)
    finally:
        if server is not None:
            server.quit() 

def _create_log_file(self, flow_label):
    # Set the logs location for all flows
    logs_folder = os.path.join(self.datastream_path, DEFAULTS.DEFAULT_LOGS_FOLDER) 
    #logs_folder = dataflow_def.get(self.DEFAULT_LOGS_FOLDER, os.path.join(self.datastream_path, 
    #                                                                      self.DEFAULT_LOGS_FOLDER)) 

    # Default is a _logs/ folder in same place as run_dataflow.py
    print("Using logs folder:", logs_folder)

    # Make sure _logs folder exists
    if not os.path.exists(logs_folder):
        print("...creating _logs base folder:", logs_folder)
        os.mkdir(logs_folder)

    currdatetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    logdir = os.path.join(self.base_folder, logs_folder, flow_label) #"{}/{}/".format(logs_folder, flow_label)
    if not os.path.exists(logdir):
        print("...creating logs directory:", logdir)
        os.mkdir(logdir)

    logfile = os.path.join(logdir, "log_{}_{}.txt".format(flow_label, currdatetime))
    print("Writing logs to: {}".format(logfile))
    return logfile

# Returns a list of the files at the given path using the given connector
def list(self, path, connector=None, sort=False):
    if connector is not None:
        if connector in self.connectors:
            if sort:
                return sorted(self.connectors[connector].read(path, type='list'))
            else:
                return self.connectors[connector].read(path, type='list')
    print("No results returned")
    return None