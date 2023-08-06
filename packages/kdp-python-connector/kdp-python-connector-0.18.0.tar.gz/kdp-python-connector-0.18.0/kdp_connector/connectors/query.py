from sys import api_version
import kdp_api
from kdp_api.api import query_api

class QueryApi(object):

    def post_lucene_query(self, config, dataset_id: str, expression: str, limit: int = 5, offset: int = 0):
        """This method will be used to query data in KDP datasets using the lucene syntax

            :param Configuration config: Connection configuration
            :param str dataset_id: ID of the KDP dataset where the data will queried
            :param str expression: Lucene style query expression ex. name: John

            :returns: Records matching query expression

            :rtype: RecordBatch
        """
        with kdp_api.ApiClient(config) as api_client:
            api_instance = query_api.QueryApi(api_client)

            query = {}
            query['datasetId'] = dataset_id
            query['expression'] = expression
            query['limit'] = limit
            query['offset'] = offset

            return api_instance.post_lucene_query(lucene_query_request=query)

