from ..framework.utilz import BaseTest
import requests
import json


class RepositoryBlueprint(BaseTest):
    def __init__(self, *args, **kwargs):
        super(RepositoryBlueprint, self).__init__(*args, **kwargs)
        self.url = self.base_url

    def test01_post_method(self):
        '''
            Test the post method of this api
        :return:
        '''
        API_values = ['repository', 'test', 'blueprint', 'weza2']

        for value in API_values:
            self.url = self.get_api(self.url, value)
        print self.url
        response = requests.post(self.url, headers=self.header)

        self.assertEqual(response.status_code, 200, 'The status code is %i'% response.status_code)
