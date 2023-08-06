import pandas as pd
import kdp_api
from kdp_api.api import read_api
from kdp_api.models import SequenceReadRequest
from kdp_api.models import RecordBatch


class ReadApi(object):

    def read_dataset_to_dictionary_list(self, config, dataset_id: str,
                                        starting_record_id: str = '', batch_size: int = 1000):
        """This method will read records from a dataset to a dictionary list

            :param Configuration config: Connection configuration
            :param str dataset_id: ID of the KDP dataset where the data will be read from
            :param str starting_record_id: First record id to read
            :param int batch_size: Defaults to 1000

            :returns: Dictionary list of records

            :rtype: list
        """
        with kdp_api.ApiClient(config) as api_client:
            api_instance = read_api.ReadApi(api_client)
            has_more_records = bool(True)
            dictionary_list = []

            while has_more_records:
                record_batch: RecordBatch = self.read_batch_in_sequence(
                    api_instance=api_instance,
                    dataset_id=dataset_id,
                    starting_record_id=starting_record_id,
                    batch_size=batch_size)
                has_more_records = record_batch.more
                starting_record_id = record_batch.last_record_id
                for json_record in record_batch.records:
                    dictionary_list.append(json_record['_data_store'])

            return dictionary_list

    @staticmethod
    def read_batch_in_sequence(api_instance, dataset_id: str, starting_record_id: str,
                               batch_size: int):
        sequence_read_request = SequenceReadRequest(dataset_id=dataset_id,
                                                    starting_record_id=starting_record_id,
                                                    batch_size=batch_size)
        return api_instance.post_read_in_sequence(read_range_request=sequence_read_request)

    def read_dataset_to_pandas_dataframe(self, config, dataset_id: str, starting_record_id: str = '',
                                         batch_size: int = 100000):
        """This method will read KDP dataset records into a pandas dataframe

            :param Configuration config: Connection configuration
            :param str dataset_id: ID of the KDP dataset where the data will be read from
            :param str starting_record_id: First record id to read
            :param int batch_size: Defaults to 100000

            :returns: Pandas dataframe with KDP records

            :rtype: DataFrame
        """
        dictionary_list = self.read_dataset_to_dictionary_list(config, dataset_id, starting_record_id,
                                                               batch_size)
        return pd.DataFrame(dictionary_list)

    @staticmethod
    def get_splits(config, dataset_id: str):
        """This method will get a list of splits from for the dataset

            :param Configuration config: Connection configuration
            :param str dataset_id: ID of the KDP dataset to get splits from

            :returns: List of split points

            :rtype: SplitPoints
        """
        with kdp_api.ApiClient(config) as api_client:
            api_instance = read_api.ReadApi(api_client)

            return api_instance.get_splits_id(dataset_id=dataset_id)

    @staticmethod
    def read_batch(config, dataset_id: str, starting_record_id: str, ending_record_id: str,
                   exclude_starting_record_id: bool, batch_size: int = 10):
        """This method will read a batch of records from a KDP dataset

            :param Configuration config: Connection configuration
            :param str dataset_id: ID of the KDP dataset that will be read from
            :param str starting_record_id: First record id to read
            :param str ending_record_id: Last record id to read
            :param bool exclude_starting_record_id: Whether to exclude starting record id
            :param int batch_size: Size of batch to read (default is 10)

            :returns: List of records

            :rtype: RecordBatch
        """
        with kdp_api.ApiClient(config) as api_client:
            api_instance = read_api.ReadApi(api_client)

            request = {}
            request['datasetId'] = dataset_id
            request['excludeStartingRecordId'] = exclude_starting_record_id
            request['startingRecordId'] = starting_record_id
            request['endingRecordId'] = ending_record_id
            request['batchSize'] = batch_size

            return api_instance.post_read(request)
