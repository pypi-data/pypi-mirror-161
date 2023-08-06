import kdp_api
from kdp_api.api.authentication_api import AuthenticationApi
from kdp_api.api.authentication_api import Authentication


class AuthenticationUtil(object):

    @staticmethod
    def create_authentication_token(config, email: str, password: str, workspace_id: str, strategy: str = 'local'):
        """This method will be used to create a KDP authentication token

            :param Configuration config: KDP configuration
            :param str email: User email address
            :param str password: User password
            :param str workspace_id: User workspace
            :param str strategy: Defaults to "local"

            :returns: Authentication token

            :rtype: AuthenticationDetails
        """

        with kdp_api.ApiClient(config) as api_client:
            api_instance = AuthenticationApi(api_client)

            authentication = Authentication(strategy=strategy, email=email, password=password, workspaceId=workspace_id)
            return api_instance.post_authentication(authentication=authentication)
