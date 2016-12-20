'''
    This file should implement the following methods:
        - For the first time create a repo
        - Post the cockpit API with Json bp
        - Run this bp
'''
from cockpit_testing.Framework.utils.utils import BaseTest
import json
import time


class RequestCockpitAPI(BaseTest):
    def __init__(self):
        super(RequestCockpitAPI, self).__init__()
        self.repo = {'name': self.random_string()}
        self.blueprint = {'name': self.random_string()}

    def create_new_repository(self, repository):
        '''
            POST :  /ays/repository
        '''
        self.logging.info('* creating new repository .....')
        API = self.build_api(['repository'])

        API_BODY = self.build_json({"git_url": self.random_string(),
                                    "name": repository,
                                    "path": ""})

        response = self.requests.post(url=API, headers=self.header, data=API_BODY)
        if response.status_code == 201:
            self.logging.info('* CREATED : %s repo' % self.repo['name'])
        else:
            self.logging.error('* ERROR : response status code %i' % response.status_code)
            self.logging.error('* ERROR : response content %s ' % response.content)
            raise NameError('ERROR : response status code %i' % response.status_code)

    def send_blueprint(self, repository, blueprint):
        self.logging.info('* sending blueprint .....')
        '''
            POST :  /ays/repository/{repository}/blueprint
        '''
        API = self.build_api(['repository', repository, 'blueprint'])

        API_BODY = self.build_json({'name': self.blueprint['name'],
                                    'content': blueprint})

        response = self.requests.post(url=API, headers=self.header, data=API_BODY)

        if response.status_code == 201:
            self.logging.info('CREATED : %s blueprint in %s repo' % (self.blueprint['name'], self.repo['name']))
        else:
            self.logging.error('ERROR : response status code %i' % response.status_code)
            self.logging.error('ERROR : response content %s ' % response.content)
            raise NameError('ERROR : response status code %i' % response.status_code)

    def execute_blueprint(self, repository='', blueprint=''):
        '''
            POST :  /ays/repository/{repository}/blueprint/{blueprint}
        '''
        API = self.build_api(['repository', self.repo['name'], 'blueprint', self.blueprint['name']])

        API_BODY = self.build_json({'blueprint': blueprint,
                                    'repository': repository})

        response = self.requests.post(url=API, headers=self.header, data=API_BODY)
        if response.status_code == 200:
            self.logging.info('EXECUTED : %s blueprint in %s repo' % (self.blueprint['name'], self.repo['name']))
        else:
            self.logging.error('ERROR : response status code %i %s ' % (response.status_code, response.content))
            self.logging.error('ERROR : response content %s ' % response.content)
            raise NameError('ERROR : response status code %i %s ' % (response.status_code, response.content))

    def run_repository(self, repository):
        '''
            POST :  /ays/repository/{repository}/aysrun
        '''
        API = self.build_api(['repository', repository, 'aysrun'])

        API_BODY = self.build_json({'callback_url ': self.random_string(),
                                    'simulate': False})

        response = self.requests.post(url=API, headers=self.header, data=API_BODY)
        if response.status_code == 200:
            self.logging.info('RAN : %s repo' % self.repo['name'])
            self.repo['key'] = response.json()['key']
            self.logging.info('key : %s' % self.repo['key'])
            self.start_time = time.time()
        else:
            self.logging.error('ERROR : response status code %i' % response.status_code)
            self.logging.error('ERROR : response content %s ' % response.content)
            raise NameError('ERROR : response status code %i' % response.status_code)

    def get_run_status(self, repository, run_key):
        '''
            GET : /ays/repository/{repository}/aysrun/{aysrun}
        '''

        API = self.build_api(['repository', repository, 'aysrun', run_key])

        for _ in range(300):
            response = self.requests.get(url=API, headers=self.header)

            if response.status_code == 200:
                content = json.loads(response.content)
                state = str(content['state'])

                if state == 'Running' or state == 'new':
                    self.logging.info('The Running state is %s' % state)
                    time.sleep(10)
                    continue
                elif state == 'ok':
                    self.logging.info('The Running state is %s' % state)
                    return True
                elif state == 'error':
                    self.logging.error('ERROR : The Running state is %s' % state)
                    self.blueprint['log'] = content['steps']
                    return False
            else:
                self.logging.error('ERROR : response status code %i' % response.status_code)
                self.logging.error('ERROR : response content %s ' % response.content)
                raise NameError('ERROR : response status code %i' % response.status_code)
        else:
            raise NameError('ERROR : Time out')

    def get_service_data(self, repository, role, service):
        '''
            Get :  /ays/repository/{repository}/service/{role}/{name}
        '''
        API = self.build_api(['repository', repository, 'service', role, service])

        response = self.requests.get(url=API, headers=self.header)

        if response.status_code == 200:
            temp = json.loads(response.content)['data']
            result = temp['result']
            self.logging.info('RESULT: %s' % result)
            self.testcase_time = '{:0.2f}'.format(time.time() - self.start_time)
            return [result, self.testcase_time]
        else:
            self.logging.error('ERROR : response status code %i' % response.status_code)
            self.logging.error('ERROR : response content %s ' % response.content)
            raise NameError('ERROR : response status code %i' % response.status_code)
