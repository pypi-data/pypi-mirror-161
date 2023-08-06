import dsphere.DataStream as ds

def reload(self, *args, **kwargs):
    self.ds.reload(*args, **kwargs)

def _load_config(self, *args, **kwargs):
    self.ds._load_config(*args, **kwargs)

def _create_filename(self, *args, **kwargs):
    self.ds._create_filename(*args, **kwargs)

def _convert_ipynb_to_py(self, *args, **kwargs):
    self.ds._convert_ipynb_to_py(*args, **kwargs)

def _send_email(self, *args, **kwargs):
    self.ds._send_email(*args, **kwargs)

def deploy(self, *args, **kwargs):
    self.ds.deploy(*args, **kwargs)

def _create_log_file(self, *args, **kwargs):
    self.ds._create_log_file(*args, **kwargs)

def run(self, *args, **kwargs):
    self.ds.run(*args, **kwargs)

def on_terminate(self, *args, **kwargs):
    self.ds.on_terminate(*args, **kwargs)

def list(self, *args, **kwargs):
    return self.ds.list(*args, **kwargs)

def read(self, *args, **kwargs):
    self.ds.read(*args, **kwargs)

def download(self, *args, **kwargs):
    self.ds.download(*args, **kwargs)

def archive(self, *args, **kwargs):
    self.ds.archive(*args, **kwargs)

def restore(self, *args, **kwargs):
    self.ds.restore(*args, **kwargs)

def archive_files_to_s3(self, *args, **kwargs):
    self.ds.archive_files_to_s3(*args, **kwargs)

def archive_featureset(self, *args, **kwargs):
    self.ds.archive_featureset(*args, **kwargs)

def restore_featureset(self, *args, **kwargs):
    self.ds.restore_featureset(*args, **kwargs)
