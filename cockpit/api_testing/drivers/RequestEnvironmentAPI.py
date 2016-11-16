from cockpit.api_testing.utilz.utilz import BaseTest
from cockpit.api_testing.drivers.client import Client


class RequestEnvironmentAPI(BaseTest):
    def __init__(self):
        super(RequestEnvironmentAPI, self).__init__()
        self.client = Client(self.values['environment'], self.values['username'], self.values['password'])
        self.session = self.client.session()

    def get_cloudspaces_list(self):
        API = self.build_env_api(['restmachine', '/cloudapi', 'cloudspaces', 'list'])
        return self.session.get(API)
