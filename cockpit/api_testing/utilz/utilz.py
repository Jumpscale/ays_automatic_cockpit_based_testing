import requests
import json
import uuid


class BaseTest(object):
    def __init__(self):
        self.base_url = 'https://cockpit1.aydo2.com/api/ays'
        self.jwt = 'eyJhbGciOiJFUzM4NCIsInR5cCI6IkpXVCJ9.eyJhdWQiOlsicXVhbGl0eV9jb2NrcGl0XyIsInF1YWxpdHlfY29ja3BpdF8iXSwiZXhwIjoxNDc5MzEyODY2LCJpc3MiOiJpdHN5b3VvbmxpbmUiLCJzY29wZSI6InVzZXI6bWVtYmVyb2Y6cXVhbGl0eV9jb2NrcGl0XyIsInVzZXJuYW1lIjoiaXNsYW10ZXN0In0.gru8xu32eYyG1b7pOAaGJICUE61kG3lo8vEGsEMnP5P0Ho_2e0EPUrBB-manpmlGo6g8odvsqjTfdVLZtfwSuolAooAEiYphVs4LynP981tGQpI0IqJXsVAQaZMAnMzt'
        self.values = {'environment':'be-scale-3.demo.greenitglobe.com',
                       'username':'ramez',
                       'password':'saeedramez1',
                       'account':'Automated QA',
                       'location':'be-scale-3'
                       }
        self.header = {'Authorization': 'bearer ' + self.jwt,
                       'content-type': 'application/json'}
        self.requests = requests

    def random_string(self):
        return str(uuid.uuid4()).replace("-", "")[:10]

    def build_api(self, api_list):
        api = self.base_url + '/'
        for value in api_list:
            api += value + '/'
        return api[:-1]

    def build_json(self, data):
        # This method take dict data and return json data.
        return json.dumps(data)

    def build_env_api(self, api_list):
        api = self.values['environment'] + '/'
        for value in api_list:
            api += value + '/'
        return api[:-1]
