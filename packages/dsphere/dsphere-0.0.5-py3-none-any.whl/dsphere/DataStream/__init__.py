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
# from typing import Optional
# import fnmatch
import tempfile
import sys

import dsphere.defaults as defaults
class dotdict(dict):
    """dot.notation access to dictionary properties"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
DEFAULTS = dotdict(defaults.DEFAULTS)

class DataStream:
    from dsphere.DataStream.file import _create_filename, _convert_ipynb_to_py, _send_email, _create_log_file, list
    from dsphere.DataStream.prefect import deploy, run
    from dsphere.DataStream.load import reload, _load_config
    from dsphere.DataStream.save import read, download, archive, restore
    
    def __init__(self, directory=DEFAULTS.DEFAULT_BASE_PATH,
        status_logfile=DEFAULTS.DEFAULT_LOGFILE,
        config=DEFAULTS.DEFAULT_CONFIG_FILE, **kwargs):
        self.status_logfile = status_logfile
        self.datastream_config_file = config
        self.datastream_path = directory
        self.library_path = os.path.dirname(os.path.abspath(__file__))

        print("Using logfile:", self.status_logfile)
        print("Using config file:", self.datastream_config_file)
        
        self.datastream_config = None
        self.dataflows = None
        self.alerts = None
        self.parameters = {}
        self.streams = {}
        self.schedule = {}
        self.executors = {}
        self.sources = {}
        self.connectors = {}
        self.connector_definitions = {} # Temporary to pass into FeatureSpace
        self.syncs = {}
        self.modelers = {}
        self.FeatureSpace = None
        self.base_folder = DEFAULTS.DEFAULT_BASE_PATH
        self.flows_folder = DEFAULTS.DEFAULT_BASE_PATH
        self.temp_file = os.path.join(self.base_folder, DEFAULTS.DEFAULT_TEMPFILE)
        self.other_config_details = kwargs
        
        # Initiate the first load of the config file
        self._load_config()

        
