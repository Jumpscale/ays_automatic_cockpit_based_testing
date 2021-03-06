import requests
import json
import uuid
import os, re
from subprocess import Popen, PIPE
from xml.etree.ElementTree import Element, SubElement, tostring
from bs4 import BeautifulSoup
from .client import Client
import logging
import time
import configparser
from cockpit_testing.Framework.utils.blueprintExecutionTime import ExecutionTime
from random import randint
from cockpit_testing.Framework.utils.skiptest import skiptests
class BaseTest(object):
    def __init__(self):
        self.clone = False
        self.account = ''
        self.account_id = ''
        self.logging = logging
        #self.log()
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
        self.execution_time = ExecutionTime
        self.skiptests=skiptests.copy()

    def setup(self):
        self.get_testcases_templates()

        if not self.values['password']:
            self.values['password'] = str(input("Please, Enter %s's password : " % self.values['username']))

    def teardown(self):
        print(' [*] Execute teardown method .... ')
        # Delete account
        if not self.account_id:
            self.get_account_ID(account=self.account)

        api = 'https://' + self.values['environment'] + '/restmachine/cloudbroker/account/delete'
        client_header = {'Content-Type': 'application/x-www-form-urlencoded',
                         'Accept': 'application/json'}
        client_body = {'accountId': self.account_id,
                       'reason': 'TearDown by Cockpit Driver'}
        client_response = self.client._session.post(url=api, headers=client_header, data=client_body)
        if client_response.status_code == 200:
            self.logging.info('DONE: Delete %s account' % self.values['account'])
            print(' [*] DONE: Deleted %s account' % self.values['account'])
        else:
            client_response.raise_for_status()

    @staticmethod
    def random_string():
        return str(uuid.uuid4()).replace("-", "")[:10]

    @staticmethod
    def random_integer(min_val, max_val):
        return randint(int(min_val), int(max_val))

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
        config = configparser.ConfigParser()
        config.read(config_path)
        section = config.sections()[0]
        options = config.options(section)
        for option in options:
            value = config.get(section, option)
            self.values[option] = value

    def create_account(self):
        # create new account
        if not self.values['account']:
            self.logging.info(' [*] Create new account .... ')
            print(' [*] Create new account .... ')
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
                self.logging.info(' [*] DONE : Create %s account' % self.account)
            else:
                self.logging.error(' [*] ERROR : response status code %i' % client_response.status_code)
                self.logging.error(' [*] ERROR : response content %s' % client_response.content)
                client_response.raise_for_status()
        else:
            self.account = self.values['account']
            self.get_account_ID(self.account)
            self.logging.info(' [*] Use %s account' % self.values['account'])

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
        if 'https' in repo:
            temp = repo.split('/')[-1]
            repo_name = temp[:temp.find('.')]
        else:
            match = re.search(r'/(\S+).git', repo)
            repo_name = match.group(1)

        # make directory to clone repos on
        if self.clone:
            dir_path = os.getcwd() + '/cockpit_testing/Framework/%s' % bps_driver_path
            if os.path.exists(dir_path):
                self.run_cmd_via_subprocess('rm -rf %s' % dir_path)
            self.run_cmd_via_subprocess('cd cockpit_testing/Framework/; mkdir %s' % bps_driver_path)
            dirs = self.run_cmd_via_subprocess('ls').split('\n')[:-1]
            if 'repos' not in dirs:
                print(' [*] create repos directory')
                self.run_cmd_via_subprocess('mkdir repos')
            else:
                print(' [*] repos directory already exists')

            dirs = self.run_cmd_via_subprocess('ls repos').split('\n')[:-1]
            if repo_name in dirs:
                self.run_cmd_via_subprocess('cd repos; rm -rf %s' % repo_name)
            print(' [*] clone repo %s' % repo)
            print(' [*] branch %s' % branch)
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
        print(' [*] Generate XML results')
        Succeeded = 0
        Errors = 0
        Failures = 0
        Skip = 0
        # remove first one
        self.Testcases_results.pop("Blueprint Name")

        for key in self.Testcases_results:
            for item in self.Testcases_results[key]:
                if 'ERROR' in item[0]:
                    Errors += 1
                    break
                elif 'FAILED' in item[0]:
                    Failures += 1
                    break
                elif 'Skip' in item[0]:
                    Skip += 1
                    break
                elif 'OK' in item[0]:
                    Succeeded += 1
                    break
                elif 'Time' in item[0]:
                    continue
                else:
                    print('The result is missing an indicator element')
                    break

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
                               'time': str(self.Testcases_results[key][0][1])}

            testcase = SubElement(testsuit, 'testcase', testcase_params)
            for item in self.Testcases_results[key]:
                if 'ERROR' in item[0]:
                    error = SubElement(testcase, 'error')
                    error_message = str(item[0])
                    service_name = str(item[1])
                    error.text = " service: %s - Message: %s" % (service_name, error_message)
                elif 'FAILED' in item[0]:
                    failuer = SubElement(testcase, 'failure')
                    failuer_message = str(item[0])
                    service_name = str(item[1])
                    failuer.text = " service: %s - Message: %s" % (service_name, failuer_message)
                elif 'Skip' in item[0]:
                    skipped = SubElement(testcase, 'skipped')
                    skipped_message = str(item[2])
                    service_name = str(item[3])
                    skipped.text = " service: %s - Message: %s" % (service_name, skipped_message)
        resultFile = open('testresults.xml', 'w')
        resultFile.write(BeautifulSoup((tostring(testsuit)), 'xml').prettify())

    def get_jobs(self, specific_blueprint_list):
        # Return : All paths which is under TestCases dir.
        utils_dir = os.path.dirname(__file__)
        test_cases_directory = os.path.join(utils_dir, "../TestCases/")
        test_cases_files = os.listdir(test_cases_directory)
        test_cases_path = []
        skip_testcases=[]
        if specific_blueprint_list:
            for specific_blueprint in specific_blueprint_list:
                if '.yaml' not in specific_blueprint:
                    specific_blueprint += '.yaml'

                if specific_blueprint in self.skiptests:
                    print((' [*] Test case : %s --skip' % specific_blueprint))
                    self.Testcases_results[specific_blueprint] = [['Skip', 0, skiptests[specific_blueprint], specific_blueprint]]
                    skip_testcases.append(specific_blueprint)
                    continue

                for file in test_cases_files:
                    if specific_blueprint != file:
                        continue
                    else:
                        test_cases_path.append(os.path.join(test_cases_directory, file))
                        break
        else:
            for file in test_cases_files:
                if file in self.skiptests:
                    print((' [*] Test case : %s --skip' % file))
                    self.Testcases_results[file] = [['Skip', 0, skiptests[file], file]]
                    skip_testcases.append(file)
                    continue
                test_cases_path.append(os.path.join(test_cases_directory, file))

        if len(test_cases_path) == 0 and len(test_cases_files) > 0 and len(skip_testcases) == 0:
            raise NameError('There is no %s blueprint in TestCases dir' % str(specific_blueprint_list))
        return test_cases_path

    def log(self, log_file_name='log.log'):
        self.logging.basicConfig(filename=log_file_name, filemode='w', level=logging.INFO,
                                 format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        '''
        How to use:
            self.logging.debug("This is a debug message")
            self.logging.info("Informational message")
            self.logging.error("An error has happened!")
        '''

    def request_handling(self, method, api, headers, body, expected_responce_code=200):
        # This method handle the api request errors for 10 times.

        if method not in ['post', 'get', 'delete']:
            raise NameError(" [*] %s method isn't handled" % method)

        for _ in range(30):
            try:
                if method == 'get':
                    response = self.requests.get(url=api, headers=headers, data=body)
                elif method == 'post':
                    response = self.requests.post(url=api, headers=headers, data=body)
                elif method == 'delete':
                    response = self.requests.delete(url=api, headers=headers, data=body)

                if response.status_code == expected_responce_code:
                    return [True, response]
                else:
                    time.sleep(2)
                    # print response.url, response.status_code, response.content
            except:
                time.sleep(2)

        return [False, response]

    def get_client(self):
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

    def get_account_ID(self, account):
        client_header = {'Content-Type': 'application/x-www-form-urlencoded',
                         'Accept': 'application/json'}
        self.logging.info(' [*] Get %s account ID .... ' % account)
        api = 'https://' + self.values['environment'] + '/restmachine/cloudapi/accounts/list'
        client_response = self.client._session.post(url=api, headers=client_header)

        if client_response.status_code == 200:
            for element in client_response.json():
                if account == element['name']:
                    self.account_id = element['id']
                    self.logging.info(' [*] DONE : Account ID : % d' % self.account_id)
                    break
            else:
                self.logging.error(
                    " [*] ERROR : Can't get %s account ID. Please, Make sure that %s username can get this account ID" % (
                        account, self.values['username']))
                print(
                    " [*] ERROR : Can't get %s account ID. Please, Make sure that %s username can get this account ID" % (
                        account, self.values['username']))
                raise NameError(
                    " [*] ERROR : Can't get '%s' account ID. Please, Make sure that '%s' username can get this account ID" % (
                        account, self.values['username']))
        else:
            self.logging.error(' [*] ERROR : response status code %i' % client_response.status_code)
            self.logging.error(' [*] ERROR : response content %s' % client_response.content)
            client_response.raise_for_status()

    def check_cockpit_is_exist(self):
        tmp = self.values['cockpit_url']
        url = tmp[:tmp.find(':5')]

        try:
            response = self.requests.get(url=url)
            if response.status_code != 200:
                self.logging.error('ERROR : response status code %i' % response.status_code)
                self.logging.error('ERROR : response content %s ' % response.content)
                raise NameError('ERROR : response status code %i' % response.status_code)
        except:
            self.logging.error("Can't Create a connection to the '%s' cockpit machine" % url)
            raise NameError("Can't Create a connection to the '%s' cockpit machine" % url)

    def get_waiting_time(self, bpFileName):
        if bpFileName in self.execution_time:
            time = self.execution_time[bpFileName]
            if time > 10:
                return int(time / 10)
            else:
                return int(time)
