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


# dataflow_label can be '*' (all flows) or just one string or a list
def deploy(self, dataflow_label, **kwargs):

    #status_logfile = "logs/dataflow_status_log.txt"
    # Example: python deploy_dataflow.py carle1a -override True
    override_filename = kwargs.get('override', False)

    # Create a single timestamp at the beginning of this script and use it in multiple places
    # For instance so we can correlate the logs with the files deployed
    currtimestamp = datetime.datetime.now()
    currdatetime_spaces = currtimestamp.strftime("%Y%m%d %H%M%S")
    currdatetime_nospaces = currtimestamp.strftime("%Y%m%d%H%M%S")

    if isinstance(dataflow_label, list):
        dataflows_to_deploy = dataflow_label
    elif dataflow_label == '*':
        dataflows_to_deploy = list(self.dataflows.keys())
    else:
        dataflows_to_deploy = [dataflow_label]

    for one_flow in dataflows_to_deploy:
        print("\nDeploying '{}'...".format(one_flow))
        if one_flow in self.dataflows:
            dataflow_def = self.dataflows[one_flow]

            # Get the input notebook folder/file from the config file
            notebook_folder = dataflow_def.get('notebook_folder', '')
            notebook_file = dataflow_def['notebook_file']
            print("Base Path:", self.base_folder)
            print("Notebook folder:", notebook_folder)
            print("Notebook file:", notebook_file)
            notebook_path = os.path.join(self.base_folder, notebook_folder, notebook_file)
            print("Notebook path:", notebook_path)

            # Get the output py folder/file from the config file
            # If not defined there, then automatically infer them based on the notebook folder/file
            py_output_folder = dataflow_def.get('folder', '{}/{}/'.format(self.datastream_path, 
                                                                                  DEFAULTS.DEFAULT_FLOWS_FOLDER))

            # Make sure this output folder exists, if not create it
            if not os.path.exists(py_output_folder):
                # Create the backups/ folder if not there yet
                print("...created _flows folder:", py_output_folder)
                os.mkdir(py_output_folder)

            old_py_filename = dataflow_def.get('script', None)
            if override_filename or override_filename=='True':
                print("Overriding current filename, using new one")
                new_py_filename = self._create_filename(notebook_file)
                print("NOTE: YOU STILL NEED TO COPY THIS FILENAME BACK INTO DATASTREAM_CONFIG.JSON!")
            elif old_py_filename is None:
                print("No filename currently stored, creating new one:")
                new_py_filename = self._create_filename(notebook_file)      
                print("NOTE: YOU STILL NEED TO COPY THIS FILENAME BACK INTO DATASTREAM_CONFIG.JSON!")
            else:
                new_py_filename = old_py_filename
                #dataflow_def.get('script', create_filename(notebook_file))
            new_py_output_path = os.path.join(self.base_folder, py_output_folder, new_py_filename)

            # TODO: If these were just created, push them back to the config file?

            # Create a timestamped backup of the Dataflow's python script (if it already exists)
            if old_py_filename is not None:
                old_py_output_path = os.path.join(self.base_folder, py_output_folder, old_py_filename)
                if os.path.exists(old_py_output_path):
                    print("Backing up existing copy of this Dataflow:", old_py_output_path)
                    py_backup_folder = os.path.join(self.base_folder, py_output_folder, 'backups')
                    if not os.path.exists(py_backup_folder):
                        # Create the backups/ folder if not there yet
                        print("...created backups folder:", py_backup_folder)
                        os.mkdir(py_backup_folder)
                    py_backup_filename = old_py_filename + '.backup_{}'.format(currdatetime_nospaces)
                    py_backup_path = os.path.join(py_backup_folder, py_backup_filename)
                    print("...backup copy created at:", py_backup_path)
                    if old_py_filename!=new_py_filename:
                        print("...moving current file to backup:", py_backup_filename)
                        shutil.move(old_py_output_path, py_backup_path)
                    else:
                        print("...copying current file to backup:", py_backup_filename)
                        shutil.copyfile(old_py_output_path, py_backup_path)

            # Now convert the .ipynb to a .py file in the given directory
            self._convert_ipynb_to_py(notebook_path, new_py_output_path)
            print("Converted notebook file to python script:")
            print("...Notebook:", notebook_path)
            print("...Script:", new_py_output_path)

            # Write to the DataStream logs
            status_logfile_path = os.path.join(self.datastream_path, self.status_logfile)
            with open(status_logfile_path, "a+") as status_file:
                print("{}: {} - Deployed Dataflow from notebook '{}' as script '{}'".format(currdatetime_spaces, one_flow, notebook_path, new_py_output_path), file=status_file)
                status_file.close()
        else:
            print("Cannot find config for dataflow '{}' needed to deploy it.".format(one_flow))

def run(self, flow_label, **kwargs):
    # First reload the config file to get the latest
    self._load_config()

    # Open the status log file
    after = kwargs.get('after', '')
    print("In ds.run() received kwargs:", kwargs)
    print("...after=", after)
    print("...parameters=", self.parameters)
    parameters_string = str(self.parameters)

    def on_terminate(proc):
    #def on_terminate(proc, project, batch):
        # Write the status to the logfile
        status_logfile_path = os.path.join(self.datastream_path, self.status_logfile)
        error_to_log = "{}: {} - Finished run of Dataflow process {} with return code: {}, params: {}".format(datetime.datetime.now().strftime("%Y%m%d %H%M%S"), flow_label, proc, proc.returncode, parameters_string)
        with open(status_logfile_path, "a+") as status_file2:                
            print(error_to_log, file=status_file2)            
            status_file2.close()

        # Check if there's another flow to initiate (or if -after flag was passed in to override this)
        dataflow_def = self.dataflows[flow_label]
        run_after = dataflow_def.get('run_after','') if after=='' else after
        print("run_after=", run_after)
        if run_after!='stop' and run_after!='' and proc.returncode == 0:
            print("inside")
            run_flow = os.path.join(self.library_path, 'run_dataflow.py')
            print("run_flow:", run_flow)
            print("dir:", self.datastream_path)
            print("config:", self.datastream_config_file)
            popen_fields = ['python', run_flow, run_after]
            all_fields = {'-dir': self.datastream_path,
                          '-config': self.datastream_config_file
                         }
            for field in all_fields:
                field_val = all_fields[field]
                if field_val is not None and field_val != '':
                    popen_fields.append(field)
                    popen_fields.append(field_val)
            print("popen_fields:", popen_fields)
            p = subprocess.Popen(popen_fields)
            print("Running dataflow '{}'".format(run_after))
        elif proc.returncode != 0:
            # If there's an error in the process, send an alert email
            subject = "{} has error code {} {}".format(flow_label, proc.returncode, parameters_string)
            body = """\
            {}
            <p>
            See logs: <a href="http://localhost:8890/tree/DataStream/logs/{}/">here</a>
            </p>
            <p>
            DataStream log: <a href="http://localhost:8890/edit/DataStream/logs/dataflow_status_log.txt">here</a>
            </p>
            <p>
            Notebooks: <a href="https://localhost:8890/G2G/tree/">here</a>
            </p>
            """.format(error_to_log, flow_label)
            # Make sure there are 'from' and 'to' connection details set for alerts
            if self.alerts is not None:
                if 'from' in self.alerts and 'to' in self.alerts:
                    from_email_cnx_details = self.alerts['from']
                    to_email_cnx_details = self.alerts['to']

                    # Initiate the email using those from/to connection details
                    self._send_email(from_email_cnx_details, to_email_cnx_details,
                                         subject, body)
                else:
                    print("Either 'from' or 'to' alerts connection details missing in the Config file")
            else:
                print("No alerts connection details found in Config file")

    # Allow run() to be called on a list of flows
    if isinstance(flow_label, list):
        for one_flow_label in flow_label:
            self.run(one_flow_label, **kwargs)
    else:
        # Run one flow at a time
        if flow_label in self.dataflows:
            # First try to run the given flow if it's a dataflow (=.py script)                
            dataflow_def = self.dataflows[flow_label]
            #folder = dataflow_def['folder']
            folder = dataflow_def.get('folder', '{}/{}/'.format(self.datastream_path, 
                                                                DEFAULTS.DEFAULT_FLOWS_FOLDER))
            script = dataflow_def['script']
            run_after_flow = dataflow_def.get('run_after', '')

            # TODO: Let the logs location be set for all dataflows, not just one at time
            #logs_folder = dataflow_def.get(self.DEFAULT_LOGS_FOLDER, os.path.join(self.datastream_path, 
            #                                                                      self.DEFAULT_LOGS_FOLDER)) 

            # Default is a logs/ folder in same place as run_dataflow.py
            #print("Using logs folder:", logs_folder)

            script_path = os.path.join(self.base_folder, folder, script)
            currdatetime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

            print("Running process: {} using file: {}, args: {}, starting at: {}, {} to run next".format(flow_label, script_path, kwargs, currdatetime, run_after_flow))

            #logdir = os.path.join(self.base_folder, logs_folder, flow_label) #"{}/{}/".format(logs_folder, flow_label)
            #if not os.path.exists(logdir):
            #    print("...creating logs directory:", logdir)
            #    os.mkdir(logdir)

            # Set up the location of the logs
            logfile = self._create_log_file(flow_label)
            #logfile = os.path.join(logdir, "log_{}_{}.txt".format(flow_label, currdatetime))
            f = open(logfile, "w")
            print("Writing logs to: {}".format(logfile))

            # Pass-in parameters set in the Config file
            popen_array = ['python', script_path]
            for param in self.parameters:
                param_value = self.parameters[param]
                popen_array.append('-{}'.format(param))
                popen_array.append(param_value)

            # INITIATE THE DATA FLOW (using any of the parameters set in the Config file)
            p = subprocess.Popen(popen_array, stdout=f, stderr=f) #env=myenv

            process_id = int(p.pid)
            print("Subprocess PID:", process_id)

            status_logfile_path = os.path.join(self.datastream_path, self.status_logfile)
            status_file = open(status_logfile_path, "a+")
            print("{}: {} - Started run of Dataflow process {} with params: {}".format(datetime.datetime.now().strftime("%Y%m%d %H%M%S"), flow_label, process_id, parameters_string), file=status_file)
            status_file.close()

            ls = [psutil.Process(process_id)]
            gone, alive = psutil.wait_procs(ls, timeout=None, callback=on_terminate)
            proc_returncode = gone[0].returncode
            print("Finished '{}' with return code '{}' at: {}".format(flow_label, proc_returncode, datetime.datetime.now()))

            # New on 6/13/20: Need to raise an error if this process terminates with an error
            if proc_returncode!=0:
                raise Exception("DataStream flow '{}' ended with an error code {}".format(flow_label, proc_returncode))

        elif flow_label in self.syncs or flow_label in self.modelers:
            # Otherwise if this flow is a "sync", run that

            # Set up the location of the logs
            logfile = self._create_log_file(flow_label)

            print("Running sync '{}', saving output to logfile: {}".format(flow_label, logfile))
            #current_stdout = sys.stdout

            # Redirect all print() statements to the logfile while running this flow
            # See: https://stackoverflow.com/questions/6796492/temporarily-redirect-stdout-stderr
            logfile_f = open(logfile, "w")
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            old_stdout.flush()
            old_stderr.flush()
            sys.stdout = logfile_f
            sys.stderr = logfile_f

            # Execute the flow with stdout/stderr going to the logfile
            if flow_label in self.syncs:
                self.syncs[flow_label].run(**kwargs)
            elif flow_label in self.modelers:
                self.modelers[flow_label].run(**kwargs)

            # Flush/close the logfile
            logfile_f.flush()
            logfile_f.close()

            # Undo the redirect
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            print("...finished running sync.")

            # Log the status of this run
            status_logfile_path = os.path.join(self.datastream_path, self.status_logfile)
            status_file = open(status_logfile_path, "a+")
            print("{}: {} - Started run of Dataflow process {} with params: {}".format(datetime.datetime.now().strftime("%Y%m%d %H%M%S"), flow_label, flow_label, parameters_string), file=status_file)
            status_file.close()

        else:
            print("Cannot find definition for flow '{}' to run it".format(flow_label))