import requests
import json
import uuid
import os
import urllib


class BaseTest(object):
    def __init__(self):
        self.values = {'environment': '',
                       'username': '',
                       'password': '',
                       'account': '',
                       'location': '',
                       'cockpit_url': '',
                       'jwt': ''
                       }
        self.get_config_values()
        self.get_jwt()
        self.header = {'Authorization': 'bearer ' + self.values['jwt'],
                       'content-type': 'application/json'}
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
        organization_name = 'quality_cockpit_'
        secret_key = 'ymVtPAgrm8AQB7cpdpY0d7yBFE1YtUFc_Z84F0uESzg7ErxiPWK_'

        params = {
                'grant_type': 'client_credentials',
                'client_id': organization_name,
                'client_secret': secret_key
        }

        url = 'https://itsyou.online/v1/oauth/access_token?'
        resp = requests.post(url, params=params)
        resp.raise_for_status()
        access_token = resp.json()['access_token']
        url = 'https://itsyou.online/v1/oauth/jwt'
        headers = {'Authorization': 'token %s' % access_token}
        data = {'scope': 'user:memberOf:%s' % organization_name}
        resp = requests.post(url, data=json.dumps(data), headers=headers)
        self.values['jwt'] = resp.content
