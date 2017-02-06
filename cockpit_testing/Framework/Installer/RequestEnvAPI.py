from cockpit_testing.Framework.utils.utils import BaseTest
import time


class RequestEnvAPI(BaseTest):
    def __init__(self):
        super(RequestEnvAPI, self).__init__()
        self.get_client()
        self.log()
        self.client_header = {'Content-Type': 'application/x-www-form-urlencoded',
                              'Accept': 'application/json'}
        self.cloudspace = {}
        self.virtualmahine = {}

    def create_cloudspace(self):
        self.logging.info(' * Create new cloudspace .... ')
        print(' * Create new cloudspace .... ')
        self.cloudspace['name'] = self.random_string()
        api = 'https://' + self.values['environment'] + '/restmachine/cloudbroker/cloudspace/create'
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

        client_response = self.client._session.post(url=api, headers=self.client_header, data=client_data)

        if client_response.status_code == 200:
            self.cloudspace['id'] = client_response.text
            self.logging.info(' * DONE : Create %s cloudspace' % self.cloudspace['name'])
        else:
            self.logging.error(' * ERROR : response status code %i' % client_response.status_code)
            self.logging.error(' * ERROR : response content %s' % client_response.content)
            client_response.raise_for_status()

    def create_virtualmachine(self):
        self.logging.info(' * Create new virtual mahcine .... ')
        print(' * Create new virtual mahcine .... ')
        self.virtualmahine['name'] = self.random_string()

        api = 'https://' + self.values['environment'] + '/restmachine/cloudbroker/machine/create'

        client_data = {
            'cloudspaceId': self.cloudspace['id'],
            'name': self.virtualmahine['name'],
            'sizeId': 4,
            'imageId': self.get_ubunut_16_image_id(),
            'disksize': 50}

        for _ in range(5):
            client_response = self.client._session.post(url=api, headers=self.client_header, data=client_data)
            if client_response.status_code == 200:
                self.virtualmahine['id'] = client_response.text
                self.logging.info(' * DONE : Create %s virtual machine' % self.virtualmahine['name'])
                self.get_virtualmachine_password()
                break
            else:
                self.logging.error(' * ERROR : response status code %i' % client_response.status_code)
                self.logging.error(' * ERROR : response content %s' % client_response.content)
                time.sleep(1)

                continue
        else:
            client_response.raise_for_status()

    def get_ubunut_16_image_id(self):
        api = 'https://' + self.values['environment'] + '/restmachine/cloudapi/images/list'
        client_response = self.client._session.post(url=api, headers=self.client_header)
        if client_response.status_code == 200:

            for temp in list(client_response.json()):
                if 'Ubuntu 16.04' in temp['name']:
                    self.image_id = temp['id']
                    self.logging.info(' * Get the Ubunut 16.04 id')
                    return self.image_id
        else:
            self.logging.error(' * ERROR : response status code %i' % client_response.status_code)
            self.logging.error(' * ERROR : response content %s' % client_response.content)
            client_response.raise_for_status()

    def create_port_forward(self, publicPorts):
        self.logging.info(' * Get cloudpsace public IP')
        print(' * Get cloudpsace public IP')
        self.get_cloudspace_ip()

        for key in publicPorts:
            self.logging.info(' * START : port forward creation ...')
            api = 'https://' + self.values['environment'] + '/restmachine/cloudapi/portforwarding/create'
            client_data = {'cloudspaceId': self.cloudspace['id'],
                           'publicIp': self.cloudspace['ip'],
                           'publicPort': publicPorts[key],
                           'machineId': self.virtualmahine['id'],
                           'localPort': key,
                           'protocol': 'tcp'}

            for _ in range(300):
                try:
                    client_response = self.client._session.post(url=api, headers=self.client_header, data=client_data)

                    if client_response.status_code == 200:
                        self.logging.info(' * DONE : Create ssh port forwarding')
                        break
                    else:
                        client_response.raise_for_status()
                except:
                    time.sleep(2)
            else:
                client_response.raise_for_status()
                self.logging.error(' * ERROR : response status code %i' % client_response.status_code)
                self.logging.error(' * ERROR : response content %s' % client_response.content)

    def get_cloudspace_ip(self):
        api = 'https://' + self.values['environment'] + '/restmachine/cloudapi/cloudspaces/get'
        client_data = {'cloudspaceId': self.cloudspace['id']}

        client_response = self.client._session.post(url=api, headers=self.client_header, data=client_data)

        if client_response.status_code == 200:
            self.cloudspace['ip'] = client_response.json()['publicipaddress']
            self.logging.info(' * cloudpsace public IP : %s ' % self.cloudspace['ip'])
        else:
            self.logging.error(' * ERROR : response status code %i' % client_response.status_code)
            self.logging.error(' * ERROR : response content %s' % client_response.content)
            client_response.raise_for_status()

    def get_virtualmachine_password(self):
        api = 'https://' + self.values['environment'] + '/restmachine/cloudapi/machines/get'
        client_data = {'machineId': self.virtualmahine['id']}

        client_response = self.client._session.post(url=api, headers=self.client_header, data=client_data)

        if client_response.status_code == 200:
            self.virtualmahine['password'] = client_response.json()['accounts'][0]['password']
            self.logging.info(' * Virtual machine password : %s' % self.virtualmahine['password'])
        else:
            self.logging.error(' * ERROR : response status code %i' % client_response.status_code)
            self.logging.error(' * ERROR : response content %s' % client_response.content)
            client_response.raise_for_status()

    def delete_cloudspace(self):
        api = 'https://' + self.values['environment'] + '/restmachine/cloudbroker/cloudspace/destroy'
        client_data = {'accountId': self.account_id,
                       'cloudspaceId': self.cloudspace['id'],
                       'reason': 'Test'}

        client_response = self.client._session.post(url=api, headers=self.client_header, data=client_data)

        if client_response.status_code == 200:
            self.logging.info(' * Delete %s cloudspace' % self.cloudspace['name'])
        else:
            self.logging.error(' * ERROR : response status code %i' % client_response.status_code)
            self.logging.error(' * ERROR : response content %s' % client_response.content)
            client_response.raise_for_status()
