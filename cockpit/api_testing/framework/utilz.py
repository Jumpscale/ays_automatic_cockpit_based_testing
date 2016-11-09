import requests
import json
import unittest
from testconfig import config


class BaseTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(BaseTest, self).__init__(*args, **kwargs)
        self.base_url = config['main']['base_url']
        self.jwt = config['main']['jwt']
        self.header = {'Authorization': 'bearer ' + self.jwt}

    def get_api(self, current_url, value):
        return current_url + '/' + value
