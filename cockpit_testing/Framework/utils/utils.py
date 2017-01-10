import requests
import json
import uuid
import os, re
from subprocess import Popen, PIPE
from xml.etree.ElementTree import Element, SubElement, tostring
from bs4 import BeautifulSoup
from client import Client
import logging
import time


class BaseTest(object):
    def __init__(self):
        self.clone = True
        self.account = ''
        self.values = {'environment': '',
                       'username': '',
                       'password': '',
                       'location': '',
                       'account': '',
                       'cockpit_url': '',
                       'client_id': '',
                       'client_secret': '',
                       'jwt': '',
                       'repo': '',
                       'branch': '',
                       'threads_number': ''
                       }
        self.get_config_values()
        # self.get_jwt()
        self.header = {'Authorization': 'bearer ' + self.values['jwt'],
                       'content-type': 'application/json'}

        self.Testcases_results = {'Blueprint Name': ['Test Result', 'Execution Time']}
        self.requests = requests
        self.logging = logging

    def setup(self):
        print ' * Execute setup method ..... '
        self.get_testcases_templates()

        if not self.values['password']:
            self.values['password'] = str(input("Please, Enter %s's password : " % self.values['username']))

        self.create_account()

    def teardown(self):
        print ' * Execute teardown method .... '
        # Delete account
        api = 'https://' + self.values['environment'] + '/restmachine/cloudbroker/account/delete'
        client_header = {'Content-Type': 'application/x-www-form-urlencoded',
                         'Accept': 'application/json'}
        client_body = {'accountId': self.account_id,
                       'reason': 'TearDown by Cockpit Driver'}
        client_response = self.client._session.post(url=api, headers=client_header, data=client_body)

        if client_response.status_code == 200:
            self.logging.info('DONE: Delete %s account' % self.values['account'])
        else:
            client_response.raise_for_status()

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

    def create_account(self):
        for _ in range(30):
            try:
                self.client = Client('https://' + self.values['environment'], self.values['username'],
                                     self.values['password'])
                break
            except:
                time.sleep(1)
        else:
            self.client = Client('https://' + self.values['environment'], self.values['username'],
                                 self.values['password'])

        # create new account
        if not self.account:
            self.logging.info(' * Create new account .... ')
            self.account = self.random_string()
            api = 'https://' + self.values['environment'] + '/restmachine/cloudbroker/account/create'
            client_header = {'Content-Type': 'application/x-www-form-urlencoded',
                             'Accept': 'application/json'}
            client_data = {'name': self.account,
                           'username': self.values['username'],
                           'maxMemoryCapacity': -1,
                           'maxVDiskCapacity': -1,
                           'maxCPUCapacity': -1,
                           '&maxNASCapacity': - 1,
                           'maxArchiveCapacity': -1,
                           'maxNetworkOptTransfer': - 1,
                           'maxNetworkPeerTransfer': - 1,
                           'maxNumPublicIP': - 1,
                           'location': self.values['location']}
            client_response = self.client._session.post(url=api, headers=client_header, data=client_data)

            if client_response.status_code == 200:
                self.account_id = client_response.text
                self.values['account'] = self.account
                self.logging.info(' * DONE : Create %s account' % self.account)
            else:
                self.logging.error(' * ERROR : response status code %i' % client_response.status_code)
                self.logging.error(' * ERROR : response content %s' % client_response.content)
                client_response.raise_for_status()

    def run_cmd_via_subprocess(self, cmd):
        sub = Popen([cmd], stdout=PIPE, stderr=PIPE, shell=True)
        out, err = sub.communicate()
        if sub.returncode == 0:
            return out.decode('utf-8')
        else:
            error_output = err.decode('utf-8')
            raise RuntimeError("Failed to execute command.\n\ncommand:\n{}\n\n".format(cmd, error_output))

    def get_testcases_templates(self):
        repo = self.values['repo']
        branch = self.values['branch']
        bps_driver_path = 'TestCasesTemplate'
        match = re.search(r'/(\S+).git', repo)
        repo_name = match.group(1)

        # make directory to clone repos on
        if self.clone:
            self.run_cmd_via_subprocess('cd cockpit_testing/Framework/; mkdir %s' % bps_driver_path)
            dirs = self.run_cmd_via_subprocess('ls').split('\n')[:-1]
            if 'repos' not in dirs:
                print '* create repos directory'
                self.run_cmd_via_subprocess('mkdir repos')
            else:
                print '* repos directory already exists'

            dirs = self.run_cmd_via_subprocess('ls repos').split('\n')[:-1]
            if repo_name in dirs:
                self.run_cmd_via_subprocess('cd repos; rm -rf %s' % repo_name)
            print ' * clone repo %s' % repo
            print ' * branch %s' % branch
            self.run_cmd_via_subprocess('cd repos; git clone -b %s %s' % (branch, repo))
        # copy blueprints test templates
        self.run_cmd_via_subprocess(
            'cp -r repos/%s/tests/bp_test_templates/. cockpit_testing/Framework/%s' % (repo_name, bps_driver_path))

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
        print ' * Generate XML results'
        Succeeded = 0
        Errors = 0
        Failures = 0
        Skip = 0
        # remove first one
        self.Testcases_results.pop("Blueprint Name")

        for key in self.Testcases_results:
            if 'ERROR' in self.Testcases_results[key][0]:
                Errors += 1
            elif 'FAILED' in self.Testcases_results[key][0]:
                Failures += 1
            elif 'Skip' in self.Testcases_results[key][0]:
                Skip += 1
            elif 'OK' in self.Testcases_results[key][0]:
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
            testcase_params = {'classname': "/cockpit_testing/Framework/TestCases/" + key,
                               'name': key,
                               'time': str(self.Testcases_results[key][1])}

            testcase = SubElement(testsuit, 'testcase', testcase_params)
            if 'ERROR' in self.Testcases_results[key][0]:
                error = SubElement(testcase, 'error')
                error.text = str(self.Testcases_results[key][0])
            elif 'FAILED' in self.Testcases_results[key][0]:
                failuer = SubElement(testcase, 'failure')
                failuer.text = str(self.Testcases_results[key][0])
            elif 'Skip' in self.Testcases_results[key][0]:
                skipped = SubElement(testcase, 'skipped')
                skipped.text = str(self.Testcases_results[key][0])

        resultFile = open('testresults.xml', 'w')
        resultFile.write(BeautifulSoup((tostring(testsuit)), 'xml').prettify())

    def get_jobs(self, specific_blueprint):
        # Return : All paths which is under TestCases dir.
        utils_dir = os.path.dirname(__file__)
        test_cases_directory = os.path.join(utils_dir, "../TestCases/")
        test_cases_files = os.listdir(test_cases_directory)
        test_cases_path = []
        for file in test_cases_files:
            if specific_blueprint:
                # if specific_blueprint != file[file.find('TestCases/') + 10:]:
                if specific_blueprint != file:
                    continue
                else:
                    test_cases_path.append(os.path.join(test_cases_directory, file))
                    break
            else:
                test_cases_path.append(os.path.join(test_cases_directory, file))

        if len(test_cases_path) == 0 and len(test_cases_files) > 0:
            raise NameError('There is no %s blueprint in TestCases dir' % specific_blueprint)
        return test_cases_path

    def log(self):
        self.logging.basicConfig(filename="log.log", filemode='w', level=logging.INFO)
        '''
        How to use:
            self.logging.debug("This is a debug message")
            self.logging.info("Informational message")
            self.logging.error("An error has happened!")
        '''

    def request_handling(self, method, api, headers, body, expected_responce_code=200):
        # This method handle the api request errors for 10 times.

        if method not in ['post', 'get']:
            raise NameError(" * %s method isn't handled" % method)

        for _ in range(300):
            try:
                if method == 'get':
                    response = self.requests.get(url=api, headers=headers, data=body)
                elif method == 'post':
                    response = self.requests.post(url=api, headers=headers, data=body)

                if response.status_code == expected_responce_code:
                    return [True, response]
                else:
                    time.sleep(2)
                    print '..',
            except:
                time.sleep(2)
                print '..',

        return [False, response]

