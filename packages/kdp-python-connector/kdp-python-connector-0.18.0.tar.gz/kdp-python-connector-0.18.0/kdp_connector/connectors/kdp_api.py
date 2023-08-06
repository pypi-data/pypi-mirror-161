import kdp_api as kdp_api_client
from kdp_api.api.datasets_api import DatasetsApi
from kdp_api.api.workspaces_api import WorkspacesApi
from kdp_api.api.indexes_api import IndexesApi
from kdp_api.api.jobs_api import JobsApi
from kdp_api.api.users_api import UsersApi

class KdpApi(object):

    @staticmethod
    def create_dataset(config, name: str, workspace_id: str, description: str = '', auto_create_indexes: bool = True,
                       schema: str = '{}', search_any_field: bool = True, record_count: int = 0):
        """This method will create a new KDP dataset

            :param str name: Name of dataset to create
            :param str workspace_id: Workspace that dataset will be created in
            :param str description: Description of dataset
            :param bool auto_create_indexes: Whether to automatically index new data
            :param str schema: Schema of dataset
            :param bool search_any_field: Whether to search any field
            :param int record_count: Whether to search any field

            :returns: New dataset

            :rtype: Dataset
        """
        with kdp_api_client.ApiClient(config) as api_client:
            request_body = {
                    'name': name,
                    'record_count': record_count,
                    'description': description,
                    'auto_create_indexes': auto_create_indexes,
                    'schema': schema,
                    'search_any_field': search_any_field,
                    'workspace_id': workspace_id
                }

            datasets_api = DatasetsApi(api_client)
            return datasets_api.post_datasets(dataset_create_request=request_body)

    @staticmethod
    def create_workspace(config, name: str, workspace_id: str = None):
        """This method will create a new KDP workspace

            :param str name: Name of workspace to create
            :param str workspace_id: ID of workspace if specified (defaults to name)

            :returns: New workspace

            :rtype: Workspace
        """
        with kdp_api_client.ApiClient(config) as api_client:

            request_body = {
                'name': name,
                'id': workspace_id if workspace_id is not None else name
            }
            workspaces_api = WorkspacesApi(api_client)
            return workspaces_api.post_workspaces(workspace_create_request=request_body)

    @staticmethod
    def delete_workspace(config, workspace_id: str):
        """This method will delete a workspace by id

            :param Configuration config: Connection configuration
            :param str workspace_id: ID of workspace

            :returns: Deleted workspace

            :rtype: Workspace
        """
        with kdp_api_client.ApiClient(config) as api_client:

            workspaces_api = WorkspacesApi(api_client)
            return workspaces_api.delete_workspaces_id(workspace_id)


    @staticmethod
    def get_workspace(config, workspace_id: str):
        """This method will get a workspace by id
            :param Configuration config: Connection configuration
            :param str workspace_id: ID of workspace

            :returns: Workspace

            :rtype: Workspace
        """
        with kdp_api_client.ApiClient(config) as api_client:

            workspaces_api = WorkspacesApi(api_client)
            return workspaces_api.get_workspaces_id(workspace_id)

    @staticmethod
    def get_dataset(config, dataset_id: str):
        """This method will get a dataset by id

            :param Configuration config: Connection configuration
            :param str dataset_id: ID of dataset

            :returns: Dataset

            :rtype: Dataset
        """
        with kdp_api_client.ApiClient(config) as api_client:

            datasets_api = DatasetsApi(api_client)
            return datasets_api.get_datasets_id(dataset_id)


    @staticmethod
    def patch_dataset(config, dataset_id: str, payload):
        """This method will update fields in a dataset

           :param Configuration config: Connection configuration
           :param str dataset_id: ID of dataset
           :param PatchDataset payload: Payload with the fields to update

           :returns: Dataset

           :rtype: Dataset
       """
        with kdp_api_client.ApiClient(config) as api_client:
            datasets_api = DatasetsApi(api_client)
            return datasets_api.patch_datasets_id(id=dataset_id, dataset_patch_request=payload)


    @staticmethod
    def get_indexes(config, dataset_id: str, limit: int = 10):
        """This method will get indexes for a dataset

            :param Configuration config: Connection configuration
            :param str dataset_id: ID of dataset
            :param int limit: Limit number of results returned (default 10)

            :returns: Paginator with indexes

            :rtype: IndexPaginator
        """
        with kdp_api_client.ApiClient(config) as api_client:
            indexes_api = IndexesApi(api_client)
            return indexes_api.get_indexes(dataset_id=dataset_id, limit=limit)

    @staticmethod
    def get_index(config, index_id: str):
        """This method will get an index by ID

            :param Configuration config: Connection configuration
            :param str index_id: ID of index

            :returns: Index object

            :rtype: Index
        """
        with kdp_api_client.ApiClient(config) as api_client:
            indexes_api = IndexesApi(api_client)
            return indexes_api.get_indexes_id(id=index_id)

    @staticmethod
    def get_jobs(config, dataset_id: str, **kwargs):
        """This method will get a list of all jobs for a dataset

            :param Configuration config: Connection configuration
            :param str dataset_id: ID of dataset
            :param kwargs:
                See below
            :Keyword Args:
                workspace_id (str): workspaceId. [optional]
                limit (int): Number of results to return. [optional]
                skip (int): Number of results to skip. [optional]
                sort ({str: (bool, date, datetime, dict, float, int, list, str, none_type)}): Property to sort results. [optional]
                filter ({str: (bool, date, datetime, dict, float, int, list, str, none_type)}): Query parameters to filter. [optional]
                _return_http_data_only (bool): response data without head status
                    code and headers. Default is True.
                _preload_content (bool): if False, the urllib3.HTTPResponse object
                    will be returned without reading/decoding response data.
                    Default is True.
                _request_timeout (int/float/tuple): timeout setting for this request. If
                    one number provided, it will be total request timeout. It can also
                    be a pair (tuple) of (connection, read) timeouts.
                    Default is None.
                _check_input_type (bool): specifies if type checking
                    should be done one the data sent to the server.
                    Default is True.
                _check_return_type (bool): specifies if type checking
                    should be done one the data received from the server.
                    Default is True.
                _spec_property_naming (bool): True if the variable names in the input data
                    are serialized names, as specified in the OpenAPI document.
                    False if the variable names in the input data
                    are pythonic names, e.g. snake case (default)
                _content_type (str/None): force body content-type.
                    Default is None and content-type will be predicted by allowed
                    content-types and body.
                _host_index (int/None): specifies the index of the server
                    that we want to use.
                    Default is read from the configuration.

            :returns: A paginator with a list of jobs

            :rtype: JobPaginator
        """
        with kdp_api_client.ApiClient(config) as api_client:
            jobs_api = JobsApi(api_client)
            return jobs_api.get_jobs(dataset_id=dataset_id, **kwargs)


    @staticmethod
    def delete_user(config, user_id: str):
        """This method will delete a user by id

            :param Configuration config: Connection configuration
            :param str user_id: ID of user

            :returns: Deleted user

            :rtype: User
        """
        with kdp_api_client.ApiClient(config) as api_client:
            user_api = UsersApi(api_client)
            return user_api.delete_users_id(user_id)
