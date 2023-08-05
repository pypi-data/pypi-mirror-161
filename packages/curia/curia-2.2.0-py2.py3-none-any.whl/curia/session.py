import logging

from logzero import setup_logger

from curia.api import swagger_client
from curia.api.swagger_client import configuration

DEFAULT_LOG_LEVEL = logging.INFO


class Session():
    """Creates a Curia authentication session"""

    def __init__(self, api_token: str = None, host: str = None, debug: bool = False):
        """

        Parameters
        ----------
        api_token: str :
        host: str :
        debug: bool :
        """
        self.api_token = api_token
        self.debug = debug
        self.logger = setup_logger(name='curia', level=DEFAULT_LOG_LEVEL)
        self.api_client = swagger_client

        if debug:
            self.logger.setLevel(logging.DEBUG)

        api_config = configuration.Configuration()
        api_config.debug = self.debug
        api_config.api_key['Api-Key'] = self.api_token
        if host:
            api_config.host = host

        self.api_instance = swagger_client.PlatformApi(swagger_client.ApiClient(api_config))
