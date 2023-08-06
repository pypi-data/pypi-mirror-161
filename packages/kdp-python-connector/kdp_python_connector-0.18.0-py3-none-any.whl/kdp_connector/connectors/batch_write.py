import kdp_api
from pprint import pprint
from kdp_api.api import write_api
from kdp_api.models import WriteBatchResponse
from pandas import DataFrame

class WriteApi(object):

    def batch_write(self, config, dataset_id: str, dataframe: DataFrame, batch_size: int):
        """This method will be used to write batches of data to KDP

            :param Configuration config: Connection configuration
            :param str dataset_id: ID of the KDP dataset where the data will be written
            :param DataFrame dataframe: Data to write to KDP
            :param int batch_size: Defaults to 100

            :returns: Set of partitions data was written to

            :rtype: set
        """
        with kdp_api.ApiClient(config) as api_client:

            # Create an instance of the API class
            api_instance = write_api.WriteApi(api_client)

            partitions_set = set()

            try:
                # Convert dataframe into dict. The result is an array of json.
                json_record_array = dataframe.to_dict(orient='records')

                for i in range(0, len(json_record_array), batch_size):

                    batch = json_record_array[i:i + batch_size]

                    write_batch_response: WriteBatchResponse = api_instance.post_write_id(
                        dataset_id=dataset_id,
                        json_record=batch,
                        is_async=False
                    )

                    partitions_set.update(write_batch_response.partitions)

                return partitions_set

            except kdp_api.ApiException as e:
                pprint("Exception : %s\n" % e)
