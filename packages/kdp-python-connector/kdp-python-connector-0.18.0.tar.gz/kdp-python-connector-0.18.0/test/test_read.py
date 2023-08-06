import unittest
from unittest.mock import Mock, call, ANY

from kdp_api.model.json_record import JsonRecord
from pandas._testing import assert_frame_equal

import pandas as pd

from kdp_connector.connectors.read import ReadApi
from kdp_api.models import RecordBatch
from kdp_connector.main import KdpConn


class TestRead(unittest.TestCase):

    def setup(self):
        self.jwt = 'eyJhbGciOiJIUzI1NiIs'
        self.workspace_id = 'abc'
        self.dataset_id = '8c6718fa-348f-4019-a28f-c85037fc4b85'
        self.host = 'https://api.koverse.localhost'
        self.batch_size = 50000
        self.starting_record_id = ''

    def test_read_dataset_to_dictionary_list(self):
        self.setup()
        read_api = ReadApi()
        read_api.read_batch_in_sequence = Mock()
        # Returning different values for each call to read_batch_in_sequence.
        read_api.read_batch_in_sequence.side_effect = [self.getRecordBatch(), self.getRecordBatch(),
                                                       self.getRecordBatchNoMoreRecords()]
        kdp_conn = KdpConn()
        config = kdp_conn.create_configuration(self.jwt)
        dictionary_list = read_api.read_dataset_to_dictionary_list(config=config,
                                                                   dataset_id=self.dataset_id,
                                                                   starting_record_id=self.starting_record_id,
                                                                   batch_size=self.batch_size)
        expected_list = []
        expected_list.extend(self.getDataStoreList(self.getRecords()))
        expected_list.extend(self.getDataStoreList(self.getRecords()))
        expected_list.extend(self.getDataStoreList(self.getRecords()))
        self.assertEqual(expected_list, dictionary_list)

        expected_first_call = call(api_instance=ANY,
                                   dataset_id=self.dataset_id,
                                   starting_record_id='',
                                   batch_size=50000)
        self.assertEqual(expected_first_call, read_api.read_batch_in_sequence.mock_calls[0])
        expected_additional_call = call(api_instance=ANY,
                                        dataset_id=self.dataset_id,
                                        starting_record_id='2.' + self.dataset_id + '.recordId',
                                        batch_size=50000)
        self.assertEqual(expected_additional_call, read_api.read_batch_in_sequence.mock_calls[1])
        self.assertEqual(expected_additional_call, read_api.read_batch_in_sequence.mock_calls[2])

    def test_read_dataset_to_pandas_dataframe(self):
        self.setup()
        read_api = ReadApi()
        read_api.read_batch_in_sequence = Mock()
        # Returning different values for each call to read_batch_in_sequence.
        kdp_conn = KdpConn()
        config = kdp_conn.create_configuration(self.jwt)
        read_api.read_batch_in_sequence.side_effect = [self.getRecordBatch(), self.getRecordBatch(),
                                                       self.getRecordBatchNoMoreRecords()]
        dataframe = read_api.read_dataset_to_pandas_dataframe(config=config,
                                                              dataset_id=self.dataset_id,
                                                              starting_record_id=self.starting_record_id,
                                                              batch_size=self.batch_size)
        expected_list = []
        expected_list.extend(self.getDataStoreList(self.getRecords()))
        expected_list.extend(self.getDataStoreList(self.getRecords()))
        expected_list.extend(self.getDataStoreList(self.getRecords()))
        expected_dataframe = pd.DataFrame(expected_list)

        assert_frame_equal(expected_dataframe, dataframe)

    @staticmethod
    def getRecords():
        # Including data to test that the dataframe gets the correct data
        first_json_record = JsonRecord(record={'a': 3})
        second_json_record = JsonRecord(record={'b': 4})
        return [first_json_record, second_json_record]

    @staticmethod
    def getDataStoreList(json_record_list):
        result_list = []
        for json_record in json_record_list:
            result_list.append(json_record['_data_store'])

        return result_list


    def getRecordBatch(self):
        record_batch = RecordBatch()
        record_batch.records = self.getRecords()
        record_batch.last_record_id = '2.' + self.dataset_id + '.recordId'
        record_batch.more = bool(True)
        return record_batch

    def getRecordBatchNoMoreRecords(self):
        record_batch = RecordBatch()
        record_batch.records = self.getRecords()
        record_batch.last_record_id = '3.' + self.dataset_id + '.recordId'
        record_batch.more = bool(False)
        return record_batch


if __name__ == '__main__':
    unittest.main()
