from .handlers import RouteHandler
from jupyter_server.extension.application import ExtensionApp
from traitlets import Unicode, Bool, List
import pathlib
import os
import re


class ETCJupyterLabTelemetryCourseraApp(ExtensionApp):

    name = "etc_jupyterlab_telemetry_coursera"

    url = Unicode("").tag(config=True)
    bucket = Unicode("").tag(config=True)
    path = Unicode("").tag(config=True)
    bucket_url = Unicode("").tag(config=True)
    env_path_segment_names = List([]).tag(config=True)
    telemetry_file_path = Unicode("").tag(config=True)
    telemetry = Bool(None, allow_none=True).tag(config=True)
    
    def initialize_settings(self):

        try:
            assert self.url, "The c.ETCJupyterLabTelemetryCourseraApp.url configuration setting must be set."
            assert self.bucket, "The c.ETCJupyterLabTelemetryCourseraApp.bucket configuration setting must be set."

            self.url = self.url.strip()
            self.bucket = self.bucket.strip()
            self.path = self.path.strip()
            self.telemetry_file_path = self.telemetry_file_path.strip()

            #
            parts = [part.strip() for part in [
                self.url, self.bucket, self.path] if part]
            self.bucket_url = '/'.join(parts)
            #  Construct the bucket_url from the url, bucket, and path.

            #
            for env_path_segment_name in self.env_path_segment_names:
                env_path_segment_value = os.getenv(env_path_segment_name, None)
                if env_path_segment_value:
                    self.bucket_url = f'{self.bucket_url}/{env_path_segment_value.strip()}'
            #  Append the values of specified environment variables to the bucket_url.

            if self.telemetry is None and self.telemetry_file_path:
                #  The telemetry_file_path provides a path to the telemetry file.
                telemetry_file_path = pathlib.Path(os.getcwd(), self.telemetry_file_path)
                if telemetry_file_path.is_file():
                    #  If telemetry isn't explicitly enabled then look for the
                    #  presence of the touch file in order to activate telemetry.
                    #  This is useful when telemetry should be activated by the 
                    #  presence of a file in the Lab home directory.
                    self.telemetry = True
                    #  Telemetry is on and there is a telemetry touch file; 
                    #  hence, read its contents and append it to the bucket_url.
                    with open(telemetry_file_path, 'r') as f:
                        segment = f.read().strip()
                        acs = '[a-z0-9-]'
                        regex = rf'^(?:{acs}|(?<={acs})/(?={acs}))+$'
                        if segment and re.search(regex, segment, flags=re.IGNORECASE):
                            self.bucket_url = f'{self.bucket_url}/{segment}'

            if self.telemetry is None:
                #  Telemetry was not turned on explicitely and it was not turned on by a touch file; hence, set its state to False.
                self.telemetry = False

        except Exception as e:
            self.log.error(str(e))
            raise e

    def initialize_handlers(self):
        try:
            self.handlers.extend([(r"/etc-jupyterlab-telemetry-coursera/(.*)", RouteHandler)])
        except Exception as e:
            self.log.error(str(e))
            raise e
