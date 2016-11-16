'''
    This file should implement the following methods:
        - For the first time create a repo
        - Post the cockpit API with Json bp
        - Run this bp
'''
from cockpit.api_testing.utilz.utilz import BaseTest


class RequestCockpitAPI(BaseTest):
    def __init__(self):
        super(RequestCockpitAPI, self).__init__()
        self.url = self.base_url
        self.repo = {'name': self.random_string()}
        self.blueprint = {'name' : self.random_string()}

    def create_new_repo(self):
        API = self.build_api(['repository'])

        API_BODY = self.build_json({"git_url": self.random_string(),
                                    "name": self.repo['name'],
                                    "path": ""})

        response = self.requests.post(url=API, headers=self.header, data=API_BODY)
        if response.status_code == 201:
            print 'CREATED : %s repo' % self.repo['name']
        else:
            print ('ERROR : response status code %i' % response.status_code)

    def send_blueprint(self, bp):
        API = self.build_api(['repository', self.repo['name'], 'blueprint'])

        API_BODY = self.build_json({'name': self.blueprint['name'],
                                    'content': bp})

        response = self.requests.post(url=API, headers=self.header, data=API_BODY)
        if response.status_code == 201:
            print 'CREATED : %s blueprint in %s repo' % (self.blueprint['name'], self.repo['name'])
        else:
            print ('ERROR : response status code %i' % response.status_code)

    def execute_blueprint(self):
        API = self.build_api(['repository', self.repo['name'], 'blueprint', self.blueprint['name']])

        response = self.requests.post(url=API, headers=self.header)
        if response.status_code == 200:
            print 'EXECUTED : %s blueprint in %s repo' % (self.blueprint['name'], self.repo['name'])
        else:
            print ('ERROR : response status code %i %s ' % (response.status_code, response.content))

    def run_repo(self):
        API = self.build_api(['repository', self.repo['name'], 'aysrun'])

        API_BODY = self.build_json({'callback_url ': self.random_string(),
                                    'simulate': False})

        response = self.requests.post(url=API, headers=self.header, data=API_BODY)
        if response.status_code == 200:
            print 'RAN : %s repo' % self.repo['name']
        else:
            print ('ERROR : response status code %i' % response.status_code)
