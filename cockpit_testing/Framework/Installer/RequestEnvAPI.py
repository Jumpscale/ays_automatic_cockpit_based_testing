from cockpit_testing.Framework.utils.utils import BaseTest
import json
import time


class RequestEnvAPI(BaseTest):
    def __init__(self):
        super(RequestEnvAPI, self).__init__()
        self.log()
        self.cloudspace = {}
        self.virtualmahine = {}


    def create_cloudspace(self):
        self.logging.info(' * Create new cloudspace .... ')
        self.cloudspace['name'] = self.random_string()
        api = 'https://' + self.values['environment'] + '/restmachine/cloudbroker/cloudspace/create'
        client_header = {'Content-Type': 'application/x-www-form-urlencoded',
                         'Accept': 'application/json'}
        client_data = {
            'accountId': self.account_id,
            'name': self.cloudspace['name'],
            'access': self.values['username'],
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
            self.cloudspace['id'] = client_response.text
            self.logging.info(' * DONE : Create %s cloudspace' % self.cloudspace['name'])
        else:
            self.logging.error(' * ERROR : response status code %i' % client_response.status_code)
            self.logging.error(' * ERROR : response content %s' % client_response.content)
            client_response.raise_for_status()

    def create_virtualmachine(self):
        self.logging.info(' * Create new virtual mahcine .... ')
        self.virtualmahine['name'] = self.random_string()
        api = 'https://' + self.values['environment'] + '/restmachine/cloudapi/images/list'
        client_header = {'Content-Type': 'application/x-www-form-urlencoded',
                         'Accept': 'application/json'}
        client_data = {
            'cloudspaceId': self.cloudspace['id'],
            'name': self.virtualmahine['name'],
            'sizeId':2,
            'imageId':1,
            'disksize':50}


        client_response = self.client._session.post(url=api, headers=client_header, data=client_data)

        if client_response.status_code == 200:
            self.virtualmahine['id'] = client_response.text
            self.logging.info(' * DONE : Create %s virtual machine' % self.virtualmahine['name'])
        else:
            self.logging.error(' * ERROR : response status code %i' % client_response.status_code)
            self.logging.error(' * ERROR : response content %s' % client_response.content)
            client_response.raise_for_status()

    def create_ssh_port_forward(self):
        pass
