import requests
import json
import uuid
import os
from xml.etree.ElementTree import Element, SubElement, tostring


class BaseTest(object):
    def __init__(self):
        self.values = {'environment': '',
                       'username': '',
                       'password': '',
                       'account': '',
                       'location': '',
                       'cockpit_url': '',
                       'jwt': '',
                       'client_id': '',
                       'client_secret': ''
                       }
        self.get_config_values()
        self.get_jwt()
        self.header = {'Authorization': 'bearer ' + self.values['jwt'],
                       'content-type': 'application/json'}

        self.Testcases_results = {'Blueprint Name': ['Test Result', 'Execution Time']}
        self.requests = requests

    @staticmethod
    def random_string():
        return str(uuid.uuid4()).replace("-", "")[:10]

    def build_api(self, api_list):
        api = self.values['cockpit_url'] + '/'
        for value in api_list:
            api += value + '/'
        return api[:-1]

    @staticmethod
    def build_json(data):
        # This method take dict data and return json data.
        return json.dumps(data)

    def get_config_values(self):
        script_dir = os.path.dirname(__file__)
        config_file = "../../Config/config.ini"
        config_path = os.path.join(script_dir, config_file)

        config = open(config_path, 'r')
        for line in config:
            if '=' in line:
                key = line[:line.index('=') - 1]
                value = line[line.index('=') + 2:]
                value = value.replace('\n', '')
                self.values[key] = value

        config.close()

    def get_jwt(self):
        client_id = self.values['client_id']
        client_secret = self.values['client_secret']

        params = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }

        url = 'https://itsyou.online/v1/oauth/access_token?'
        resp = requests.post(url, params=params)
        resp.raise_for_status()
        access_token = resp.json()['access_token']
        url = 'https://itsyou.online/v1/oauth/jwt'
        headers = {'Authorization': 'token %s' % access_token}
        data = {'scope': 'user:memberOf:%s' % client_id}
        resp = requests.post(url, data=json.dumps(data), headers=headers)
        self.values['jwt'] = resp.content

    def generate_xml_results(self):
        Succeeded = 0
        Errors = 0
        Failures = 0
        Skip = 0
        self.Testcases_results.pop("Blueprint Name")

        for key in self.Testcases_results:
            if 'Errors' in self.Testcases_results[key][0]:
                Errors += 1
            elif 'Failures' in self.Testcases_results[key][0]:
                Failures += 1
            elif 'Skip' in self.Testcases_results[key][0]:
                Skip += 1
            elif 'Succeeded' in self.Testcases_results[key][0]:
                Succeeded += 1
            else:
                print 'The result is missing an indicator element'

        testsuit_params = {'name': 'Cockpit_Testing',
                           'tests': str(len(self.Testcases_results)),
                           'succeeded': str(Succeeded),
                           'errors': str(Errors),
                           'failures': str(Failures),
                           'skip': str(Skip)}

        testsuit = Element('testsuite', testsuit_params)

        for key in self.Testcases_results:
            testcase_params = {'blueprint_template': 'CockpitTesting/Framework/TestCasesTemplate',
                               'name': 'create_cloudspace',
                               'result': str(self.Testcases_results[key][0]),
                               'time': str(self.Testcases_results[key][1])}
            testcase = SubElement(testsuit, 'testcase', testcase_params)

        print tostring(testsuit)

    def get_jobs(self, specific_blueprint):
        # Return : All paths which is under TestCases dir.
        utils_dir = os.path.dirname(__file__)
        test_cases_directory = os.path.join(utils_dir, "../TestCases/")
        test_cases_files = os.listdir(test_cases_directory)
        test_cases_path = []
        for file in test_cases_files:
            if specific_blueprint:
                if specific_blueprint != file[file.find('TestCases/')+10:]:
                    continue
                else:
                    test_cases_path.append(os.path.join(test_cases_directory, file))
                    break
            else:
                test_cases_path.append(os.path.join(test_cases_directory, file))

        if len(test_cases_path) == 0 and len(test_cases_files) > 0:
            raise NameError('There is no %s blueprint in TestCases dir' % specific_blueprint)
        return test_cases_path
