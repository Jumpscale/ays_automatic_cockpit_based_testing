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
        self.log('Driver.log')
        self.repo = {'name': self.random_string()}
        self.blueprint = {'name': self.random_string()}
        self.response_error_content = ''

    def create_new_repository(self, repository):
        '''
            POST :  /ays/repository
        '''
        self.logging.info('* creating new repository .....')
        API = self.build_api(['repository'])

        API_BODY = self.build_json({"git_url": self.random_string(),
                                    "name": repository,
                                    "path": ""})

        result, response = self.request_handling(method='post',
                                                 api=API,
                                                 headers=self.header,
                                                 body=API_BODY,
                                                 expected_responce_code=201)

        if result:
            self.logging.info('* CREATED : %s repo' % self.repo['name'])
            print(' * CREATED : %s repo' % self.repo['name'])
        else:
            self.logging.error(
                '* ERROR : response status code %i response content %s ' % (response.status_code, response.content))
            print(' * ERROR : response status code %i response content %s ' % (response.status_code, response.content))
            self.response_error_content = response.content
            raise NameError('ERROR : response status code %i' % response.status_code)

    def send_blueprint(self, repository, blueprint):
        self.logging.info('* sending blueprint .....')
        '''
            POST :  /ays/repository/{repository}/blueprint
        '''
        API = self.build_api(['repository', repository, 'blueprint'])

        API_BODY = self.build_json({'name': self.blueprint['name'],
                                    'content': blueprint})

        result, response = self.request_handling(method='post',
                                                 api=API,
                                                 headers=self.header,
                                                 body=API_BODY,
                                                 expected_responce_code=201)

        if result:
            self.logging.info(' * CREATED : %s blueprint in %s repo' % (self.blueprint['name'], self.repo['name']))
            print((' * CREATED : %s blueprint in %s repo' % (self.blueprint['name'], self.repo['name'])))
        else:
            self.logging.error(
                '* ERROR : response status code %i response content %s ' % (response.status_code, response.content))
            print(' * ERROR : response status code %i response content %s ' % (response.status_code, response.content))
            self.response_error_content = response.content
            raise NameError('ERROR : response status code %i' % response.status_code)

    def execute_blueprint(self, repository='', blueprint=''):
        '''
            POST :  /ays/repository/{repository}/blueprint/{blueprint}
        '''
        API = self.build_api(['repository', self.repo['name'], 'blueprint', self.blueprint['name']])

        API_BODY = self.build_json({'blueprint': blueprint,
                                    'repository': repository})

        result, response = self.request_handling(method='post',
                                                 api=API,
                                                 headers=self.header,
                                                 body=API_BODY,
                                                 expected_responce_code=200)

        if result:
            self.logging.info(' * EXECUTED : %s blueprint in %s repo' % (self.blueprint['name'], self.repo['name']))
            print(' * EXECUTED : %s blueprint in %s repo' % (self.blueprint['name'], self.repo['name']))
        else:
            self.logging.error(
                '* ERROR : response status code %i response content %s ' % (response.status_code, response.content))
            print(' * ERROR : response status code %i response content %s ' % (response.status_code, response.content))
            self.response_error_content = response.content
            raise NameError('ERROR : response status code %i %s ' % (response.status_code, response.content))

    def run_repository(self, repository):
        '''
            POST :  /ays/repository/{repository}/aysrun
        '''
        API = self.build_api(['repository', repository, 'aysrun'])

        API_BODY = self.build_json({'callback_url ': self.random_string(),
                                    'simulate': False})

        result, response = self.request_handling(method='post',
                                                 api=API,
                                                 headers=self.header,
                                                 body=API_BODY,
                                                 expected_responce_code=200)

        if result:
            self.logging.info(' * RAN : %s repo' % self.repo['name'])
            print(' * RAN : %s repo' % self.repo['name'])
            self.repo['key'] = response.json()['key']
            self.logging.info('key : %s' % self.repo['key'])
            self.start_time = time.time()
        else:
            self.logging.error(
                '* ERROR : response status code %i response content %s ' % (response.status_code, response.content))
            print(' * ERROR : response status code %i response content %s ' % (response.status_code, response.content))
            self.response_error_content = response.content
            raise NameError('ERROR : response status code %i' % response.status_code)

    def get_run_status(self, repository, run_key, bpFileName):
        '''
            GET : /ays/repository/{repository}/aysrun/{aysrun}
        '''

        API = self.build_api(['repository', repository, 'aysrun', run_key])

        waiting_time = self.get_waiting_time(bpFileName) or 100
        for _ in range(waiting_time):
            response = self.requests.get(url=API, headers=self.header)

            if response.status_code == 200:
                content = response.json()
                state = str(content['state'])

                if state == 'running' or state == 'new':
                    self.logging.info(' %s : The Running state is %s' % (run_key, state))
                    time.sleep(10)
                    continue
                elif state == 'ok':
                    self.logging.info(' %s : The Running state is %s' % (run_key, state))
                    print(' * The Running state is %s ' % state)
                    self.testcase_time = '{:0.2f}'.format(time.time() - self.start_time)
                    return self.testcase_time
                elif state == 'error':
                    self.logging.error('%s : ERROR : The Running state is %s' % (run_key, state))
                    print(' * %s : ERROR : The Running state is %s' % (run_key, state))
                    self.blueprint['log'] = content['steps']
                    return False
            else:
                self.logging.error(
                    '* ERROR : response status code %i response content %s ' % (response.status_code, response.content))
                print(
                    ' * ERROR : response status code %i response content %s ' % (
                    response.status_code, response.content))
                self.response_error_content = response.content
                raise NameError('ERROR : response status code %i' % response.status_code)
        else:
            raise NameError('ERROR : Time out')

    def get_service_data(self, repository, role, service):
        '''
            Get :  /ays/repository/{repository}/service/{role}/{name}
        '''
        API = self.build_api(['repository', repository, 'service', role, service])

        result, response = self.request_handling(method='get',
                                                 api=API,
                                                 headers=self.header,
                                                 body='',
                                                 expected_responce_code=200)

        if result:
            temp = response.json()['data']
            result = temp['result']
            self.logging.info(' * RESULT: %s' % result)
            print(' * RESULT: %s' % result)
            return [result, service]
        else:
            self.logging.error(
                ' * ERROR : response status code %i response content %s ' % (response.status_code, response.content))
            print(' * ERROR : response status code %i %s ' % (response.status_code, response.content))
            self.response_error_content = response.content
            raise NameError('ERROR : response status code %i' % response.status_code)

    def clean_cockpit(self):
        repo = self.repo['name']
        self.logging.info(' * Deleting %s repository .....' % repo)
        API = self.build_api(['repository', repo])

        result, response = self.request_handling(method='delete',
                                                 api=API,
                                                 headers=self.header,
                                                 body='',
                                                 expected_responce_code=204)

        if result:
            self.logging.info(' * DELETED : %s repo' % repo)
            print(' * DELETED : %s repo' % repo)
        else:
            self.logging.error(
                ' * ERROR : response status code %i response content %s ' % (response.status_code, response.content))
            print(' * ERROR : response status code %i %s ' % (response.status_code, response.content))
            self.response_error_content = response.content
            raise NameError('ERROR : response status code %i' % response.status_code)
