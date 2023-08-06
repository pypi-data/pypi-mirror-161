import unittest
from dataclasses import dataclass
from unittest import mock
from unittest.mock import Mock, call

import pandas as pd
from kdp_api.models import WriteBatchResponse

from kdp_connector.main import KdpConn


class TestIngest(unittest.TestCase):
    def setup(self):
        self.JWT = 'eyJhbGciOiJIUzI1NiI'
        self.workspace_id = 'abc'
        self.dataset_id = 'd851a97f-b94a-465a-ae9c-207df0a8260f'
        self.host = 'https://api.koverse.localhost'
        self.input_file = '~/documents/Test documents/WithDates.csv'
        self.write_batch_response = WriteBatchResponse(workspace=self.workspace_id,
                                                       dataset_id=self.dataset_id,
                                                       partitions=[0, 1])
        self.api_instance = Mock()
        self.api_instance.post_write_id.return_value = self.write_batch_response

    @staticmethod
    def getDataframe(size: int):
        data = []
        for x in range(size):
            data.append({'name': 'tom', 'age': 20 + x})
        return pd.DataFrame(data)

    def test_ingest_batch_sizing(self):
        @dataclass
        class TestCase:
            records: int
            batch_size: int
            expected_batches: int

        test_cases = [
            TestCase(records=1, batch_size=1, expected_batches=1),
            TestCase(records=2, batch_size=1, expected_batches=2),
            TestCase(records=10, batch_size=1, expected_batches=10),
            TestCase(records=1, batch_size=2, expected_batches=1),
            TestCase(records=1, batch_size=10, expected_batches=1),
            TestCase(records=0, batch_size=10, expected_batches=0),
            TestCase(records=10, batch_size=1000, expected_batches=1),
            TestCase(records=11, batch_size=10, expected_batches=2),
        ]
        for case in test_cases:
            self.setup()
            mock_api_instance = self.api_instance

            with(mock.patch('kdp_api.ApiClient')):
                with(mock.patch('kdp_api.Configuration')):
                    with(mock.patch('kdp_api.api.write_api.WriteApi', side_effect=[mock_api_instance])):
                        kdp_conn = KdpConn()
                        partitions_set = kdp_conn.batch_write(self.getDataframe(case.records), self.dataset_id, self.JWT,
                                                              case.batch_size)
                        self.assertEqual(len(mock_api_instance.post_write_id.mock_calls), case.expected_batches,
                                         'FAILURE: for records=' + str(case.records) +
                                         ' and batch_size=' + str(case.batch_size) +
                                         ' expected_batches did not equal ' + str(case.expected_batches))

    def test_ingest_dataframe(self):
        self.setup()
        self.batch_size = 10
        mock_api_instance = self.api_instance
        expected_write_calls = [call(dataset_id=self.dataset_id,
                                     json_record=[{'name': 'tom', 'age': 20}, {'name': 'tom', 'age': 21},
                                                  {'name': 'tom', 'age': 22}, {'name': 'tom', 'age': 23}],
                                     is_async=False)]

        with(mock.patch('kdp_api.ApiClient')):
            with(mock.patch('kdp_api.Configuration')):
                with(mock.patch('kdp_api.api.write_api.WriteApi', side_effect=[mock_api_instance])):
                    self.setup()
                    self.batch_size = 10
                    kdp_conn = KdpConn()
                    partitions_set = kdp_conn.batch_write(self.getDataframe(4), self.dataset_id, self.JWT,
                                                          self.batch_size)
                    mock_api_instance.post_write_id.assert_has_calls(expected_write_calls)

        expected_partitions_set = {0, 1}
        self.assertEqual(expected_partitions_set, partitions_set)


if __name__ == '__main__':
    unittest.main()
