'''
    This file should implement the following methods:
        - For the first time create a repo
        - Post the cockpit API with Json bp
        - Run this bp
'''
from cockpit.Framework.utils.utils import BaseTest
import json


class RequestCockpitAPI(BaseTest):
    def __init__(self):
        super(RequestCockpitAPI, self).__init__()
        self.repo = {'name': self.random_string()}
        self.blueprint = {'name' : self.random_string()}

    def create_new_repository(self, repository):
        '''
            POST :  /ays/repository
        '''
        API = self.build_api(['repository'])

        API_BODY = self.build_json({"git_url": self.random_string(),
                                    "name": repository,
                                    "path": ""})

        response = self.requests.post(url=API, headers=self.header, data=API_BODY)
        if response.status_code == 201:
            print 'CREATED : %s repo' % self.repo['name']
        else:
            print ('ERROR : response status code %i' % response.status_code)
            raise NameError('ERROR : response status code %i' % response.status_code)

    def send_blueprint(self, repository, blueprint):
        '''
            POST :  /ays/repository/{repository}/blueprint
        '''
        API = self.build_api(['repository', repository, 'blueprint'])

        API_BODY = self.build_json({'name': self.blueprint['name'],
                                    'content': blueprint})

        response = self.requests.post(url=API, headers=self.header, data=API_BODY)
        if response.status_code == 201:
            print 'CREATED : %s blueprint in %s repo' % (self.blueprint['name'], self.repo['name'])
        else:
            print ('ERROR : response status code %i' % response.status_code)
            raise NameError('ERROR : response status code %i' % response.status_code)

    def execute_blueprint(self, repository='', blueprint=''):
        '''
            POST :  /ays/repository/{repository}/blueprint/{blueprint}
        '''
        API = self.build_api(['repository', self.repo['name'], 'blueprint', self.blueprint['name']])

        response = self.requests.post(url=API, headers=self.header)
        if response.status_code == 200:
            print 'EXECUTED : %s blueprint in %s repo' % (self.blueprint['name'], self.repo['name'])
        else:
            print ('ERROR : response status code %i %s ' % (response.status_code, response.content))
            raise NameError('ERROR : response status code %i %s ' % (response.status_code, response.content))

    def run_repository(self, repository):
        API = self.build_api(['repository', repository, 'aysrun'])

        API_BODY = self.build_json({'callback_url ': self.random_string(),
                                    'simulate': False})

        response = self.requests.post(url=API, headers=self.header, data=API_BODY)
        if response.status_code == 200:
            print 'RAN : %s repo' % self.repo['name']
            self.repo['key'] = json.loads(response.content)['key']
        else:
            print ('ERROR : response status code %i' % response.status_code)
            raise NameError('ERROR : response status code %i' % response.status_code)

    def get_service_data(self, repository, role, service):
        '''
            Get :  /ays/repository/{repository}/service/{role}/{name}
        '''
        API = self.build_api(['repository', repository, 'service', role, service])

        response = self.requests.get(url=API, headers=self.header)
        if response.status_code == 200:
            print 'RESULT: %s' % json.loads(response.content)['data']
        else:
            print ('ERROR : response status code %i' % response.status_code)
            raise NameError('ERROR : response status code %i' % response.status_code)
