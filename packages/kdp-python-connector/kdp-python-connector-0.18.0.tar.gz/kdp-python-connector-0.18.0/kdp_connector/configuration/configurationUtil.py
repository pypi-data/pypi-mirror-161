import kdp_api


class ConfigurationUtil(object):

    @staticmethod
    def create_configuration(host: str, jwt: str, path_to_ca_file: str = '', discard_unknown_keys: bool = True):
        """This method will be used to create the connection configuration

            :param str host: KDP host
            :param str jwt: JWT token
            :param str path_to_ca_file: Path to Certificate Authority file
            :param bool discard_unknown_keys: Whether to discard unknown keys, defaults to True

            :returns: KDP connection configuration

            :rtype: Configuration
        """
        # Defining the host is optional and defaults to https://api.app.koverse.com
        # See configurationUtil.py for a list of all supported configuration parameters.
        config = kdp_api.Configuration(
            host=host
        )

        # The client must configure the authentication and authorization parameters
        # in accordance with the API server security policy.
        # Examples for each auth method are provided below, use the example that
        # satisfies your auth use case.

        # provide JWT
        config.access_token = jwt

        ##############################
        ##### SSL configuration  #####
        ##############################
        ## Option 1: disable verifying SSL by not providing a file path to ca file. This will result in warning messages in the log.
        config.verify_ssl = path_to_ca_file != ''

        ## Option 2: specify the location to the CA file (path_to_ca_file). If you are using mkcert, you can find out by running "mkcert -CAROOT" command.
        if config.verify_ssl:
            config.ssl_ca_cert = path_to_ca_file
            config.assert_hostname = False

        ##### end of SSL configuration #####

        # When true will not fail deserializing extra properties that are not defined in schema.
        config.discard_unknown_keys = discard_unknown_keys

        return config
