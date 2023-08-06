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


# Reload the config file if it's changed
def reload(self):
    self._load_config(output=True)

# Load initial DataStream configuration file 
def _load_config(self, output=False):
    datastream_config_filepath = os.path.join(self.datastream_path, self.datastream_config_file)
    with open(datastream_config_filepath, 'r') as config_file:
        # Load the JSON config file defining this DataStream's flows
        self.datastream_config = json.load(config_file)
        #print(self.datastream_config)

        # Find the base folder from the config file (if set there)
        if DEFAULTS.DEFAULT_BASE_PATH_CONFIG_VAR in self.datastream_config:
            self.base_folder = self.datastream_config[DEFAULTS.DEFAULT_BASE_PATH_CONFIG_VAR]

        # Find the temp file from the config file (if set there)
        if DEFAULTS.DEFAULT_TEMP_FILE_CONFIG_VAR in self.datastream_config:
            self.temp_file = self.datastream_config[DEFAULTS.DEFAULT_TEMP_FILE_CONFIG_VAR]

        # Flows folder
        if DEFAULTS.DEFAULT_FLOWS_PATH_CONFIG_VAR in self.datastream_config:
            self.flows_folder = self.datastream_config[DEFAULTS.DEFAULT_FLOWS_PATH_CONFIG_VAR]                
            if output:
                print("Using flows folder:", self.flows_folder)

        # Dataflows
        if DEFAULTS.DEFAULT_DATAFLOWS_CONFIG_VAR in self.datastream_config:
            self.dataflows = self.datastream_config[DEFAULTS.DEFAULT_DATAFLOWS_CONFIG_VAR]

        # Alerts
        if DEFAULTS.DEFAULT_ALERTS_CONFIG_VAR in self.datastream_config:
            self.alerts = self.datastream_config[DEFAULTS.DEFAULT_ALERTS_CONFIG_VAR]

        # Connectors / Sources
        if DEFAULTS.DEFAULT_CONNECTORS_CONFIG_VAR in self.datastream_config:
            connector_defs = self.datastream_config[DEFAULTS.DEFAULT_CONNECTORS_CONFIG_VAR]

            # Temporarily store these definitions to pass into FeatureSpace below
            self.connector_definitions = connector_defs

            # Initiate each connector
            for connector in connector_defs:
                this_connector_def = connector_defs[connector]
                self.connectors[connector] = con._GetConnector(this_connector_def)

        # FeatureSpace 
        if DEFAULTS.DEFAULT_PARAMETERS_CONFIG_VAR in self.datastream_config:
            self.parameters = self.datastream_config[DEFAULTS.DEFAULT_PARAMETERS_CONFIG_VAR]
            if 'project' in self.parameters:
                if self.FeatureSpace is None:
                    if output:
                        print("\nLoading FeatureSpace using parameters:", self.parameters)
                    self.FeatureSpace = FeatureSpace(self.parameters['project'],
                                                     batch=self.parameters.get('batch', None),
                                                     directory=self.parameters.get('directory', '.'),
                                                     sources=self.connector_definitions # {} if no connectors were loaded
                                                    )
                else:
                    # Reload the FeatureSpace
                    self.FeatureSpace._reload()

        # Syncs
        if DEFAULTS.DEFAULT_SYNCS_CONFIG_VAR in self.datastream_config:
            sync_defs = self.datastream_config[DEFAULTS.DEFAULT_SYNCS_CONFIG_VAR]
            # Initiate each connector
            for sync_label in sync_defs:
                this_sync_def = sync_defs[sync_label]
                new_sync = sync._GetSync(DataStream=self, **this_sync_def)
                if new_sync is not None:
                    self.syncs[sync_label] = new_sync
                    if output:
                        print("\nCreated Sync '{}' of type '{}'".format(sync_label, new_sync.type))

        # Modelers
        if DEFAULTS.DEFAULT_MODELERS_CONFIG_VAR in self.datastream_config:
            modeler_defs = self.datastream_config[DEFAULTS.DEFAULT_MODELERS_CONFIG_VAR]
            # Initiate each connector
            for modeler_label in modeler_defs:
                this_modeler_def = modeler_defs[modeler_label]
                new_modeler = model._GetModeler(DataStream=self, **this_modeler_def)
                if new_modeler is not None:
                    self.modelers[modeler_label] = new_modeler
                    if output:
                        print("\nCreated Modeler '{}' of type '{}'".format(modeler_label, new_modeler.type))

        # Streams (series of Flows)
        if DEFAULTS.DEFAULT_STREAMS_CONFIG_VAR in self.datastream_config:
            self.streams = self.datastream_config[DEFAULTS.DEFAULT_STREAMS_CONFIG_VAR]

        # Find the default schedule in the config file (if any)
        if DEFAULTS.DEFAULT_STREAMS_SCHEDULE_VAR in self.datastream_config:
            self.schedule = self.datastream_config[DEFAULTS.DEFAULT_STREAMS_SCHEDULE_VAR]

        # Find any specification of Executors to use
        if DEFAULTS.DEFAULT_STREAMS_EXECUTOR_VAR in self.datastream_config:
            executor_defs = self.datastream_config[DEFAULTS.DEFAULT_STREAMS_EXECUTOR_VAR]
            #for executor in self.executors:
            for executor in executor_defs:
                # Instantiate each Executor
                this_executor_def = executor_defs[executor]
                self.executors[executor] = executors._GetExecutor(this_executor_def,
                                                                  streams=self.streams,
                                                                  schedule=self.schedule,
                                                                  datastream={'directory': self.datastream_path,
                                                                               'status_logfile': self.status_logfile,
                                                                               'config': self.datastream_config_file,
                                                                               **self.other_config_details}
                                                                 )
