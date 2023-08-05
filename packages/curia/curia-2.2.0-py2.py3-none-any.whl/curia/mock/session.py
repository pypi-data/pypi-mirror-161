from curia.mock.api import MockApiInstance


class MockSession:
    def __init__(self, api_token: str = None, host: str = None, debug: bool = False):
        self.api_token = api_token
        self.host = host
        self.debug = debug
        self.api_instance = MockApiInstance()

