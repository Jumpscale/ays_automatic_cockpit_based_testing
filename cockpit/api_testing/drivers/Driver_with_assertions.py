from unittest import TestCase

from cockpit.api_testing.drivers.CreateBluePrint import CreateBluePrint
from cockpit.api_testing.drivers.RequestCockpitAPI import RequestCockpitAPI
from cockpit.api_testing.drivers.RequestEnvironmentAPI import RequestEnvironmentAPI


class BaseTest(TestCase):
    '''
    call_create_repo()
    call_create_bp()
    send_bp(load_yaml_bp())
    ays_blueprint()
    ays_run()

    ASSERTION:
        Call ASSERTION PART
    '''

    def __init__(self, *args, **kwargs):
        super(BaseTest, self).__init__(*args, **kwargs)
        self.create_blueprint = CreateBluePrint()
        self.request_cockpit_api = RequestCockpitAPI()
        self.request_environment_api = RequestEnvironmentAPI()

    def test_create_cloud_space(self):
        self.create_blueprint.create_blueprint()
        self.request_cockpit_api.create_new_repo()
        self.request_cockpit_api.send_blueprint(self.create_blueprint.load_bp())

        self.request_cockpit_api.execute_blueprint()
        self.request_cockpit_api.run_repo()

        cloudspaces_list_response = self.request_environment_api.get_cloudspaces_list()
        self.assertEqual(cloudspaces_list_response.status_code, 200)
        self.assertIn(self.create_blueprint.values['random_vdc'], cloudspaces_list_response.content)
