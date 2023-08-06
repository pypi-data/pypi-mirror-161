import json
import urllib3
import logging

from urllib3.util import Timeout

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class IndexManagementApi(object):
    def __init__(self, configuration=None):
        self.configuration = configuration
        host=self.configuration.host.replace('https://', '')

        self.http = urllib3.HTTPSConnectionPool(host, port=443, cert_reqs='CERT_NONE', assert_hostname=False,
        timeout=Timeout(connect=2.0, read=10.0))


    def modify_indexes(self, dataset_id: str, create: list, remove: list,
        autoCreateIndexes: bool = False, searchAnyField: bool = False) -> object :
        """This method will modify existing indexes on a dataset

            :param str dataset_id: ID of dataset
            :param list create: List of indexes to create
            :param list remove: List of indexes to delete
            :param bool autoCreateIndexes: Whether to automatically create indexes when data is written
            :param bool searchAnyField: Whether to automatically search any field

            :returns: Job ID

            :rtype: str
       """
        request={}
        request['action']='modifyIndexes'
        request['datasetId']=dataset_id
        request['remove']=remove
        request['create']=create
        request['autoCreateIndexes']=autoCreateIndexes
        request['searchAnyField']=searchAnyField

        encoded_data = json.dumps(request).encode('utf-8')

        logging.info('modify_indexes payload: %s' % json.dumps(request))

        result: urllib3.response.HTTPResponse = self.http.request(
            'POST',
            self.configuration.host + "/index-management",
            body=encoded_data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + self.configuration.access_token
                }
            )

        if result.status == 201:
            return json.loads(result.data)
        else:
            logging.error('unexpected response code returned. status: %s, reason: %s, message: %s' %
                (result.status, result.reason, result.msg))
            raise Exception('Failed to modify indexes')

