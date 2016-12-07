from client import Client
from utils import BaseTest
import uuid


class atest(BaseTest):
    def __init__(self):
        super(atest, self).__init__()
        self.name = ''
        for i in range(100000):
            self.name += uuid.uuid4().hex
        print self.name


    def post(self):
        api = 'https://' + self.values['environment'] + '/restmachine/cloudbroker/account/create'
        client_header = {'Content-Type': 'application/x-www-form-urlencoded',
                         'Accept': 'application/json'}
        client_body = {'name': 2,
                       'username': self.values['username'],
                       'maxMemoryCapacity': -1,
                       'maxVDiskCapacity': -1,
                       'maxCPUCapacity': -1,
                       '&maxNASCapacity': - 1,
                       'maxArchiveCapacity': -1,
                       'maxNetworkOptTransfer': - 1,
                       'maxNetworkPeerTransfer': - 1,
                       'maxNumPublicIP': - 1,
                       'inject':'Hello'}
        _ = self.client._session.post(url=api, headers=client_header, data=client_body, timeout=600)
        print _.status_code
        print _.content
        import ipdb; ipdb.set_trace()


o = atest()
o.post()