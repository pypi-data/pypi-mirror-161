import json
import urllib3
import logging
from urllib3.util import Timeout


class UploadApi(object):
    def __init__(self, configuration=None):
        self.configuration = configuration
        host = self.configuration.host.replace('https://', '')

        self.http = urllib3.HTTPSConnectionPool(host, port=443, cert_reqs='CERT_NONE',
                                                assert_hostname=False, timeout=Timeout(connect=2.0, read=10.0))

    def upload(self, dataset_id: str, file_config: object):
        """This method will upload a file to KDP

            :param str dataset_id: ID of dataset that file will be uploaded to
            :param object file_config: JSON containing filename and path ex. { "filename": "test.csv", "path": "/path/to/file" }

        """
        response = self.http.request(
            'POST',
            self.configuration.host + '/uploads',
            headers={
                'Authorization': 'Bearer ' + self.configuration.access_token
            },
            fields={
                'datasetId': dataset_id,
                'files': (file_config['filename'], open(file_config['path'], 'rb').read()),
            }
        )

        return response
