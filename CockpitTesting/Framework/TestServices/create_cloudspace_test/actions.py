def init_actions_(service, args):
    """
    this needs to returns an array of actions representing the depencies between actions.
    Looks at ACTION_DEPS in this module for an example of what is expected
    """

    # some default logic for simple actions


    return {
        'test': ['install']
    }


def create_cloudspace_test(job):
    import requests, sys
    service = job.service
    try:
        g8client = service.producers['g8client'][0]
        url = g8client.model.data.url
        username = g8client.model.data.login
        password = g8client.model.data.password

        login_url = url + '/restmachine/system/usermanager/authenticate'
        credential = {'name': username,
                      'secret': password}
        session = requests.Session.post(url=login_url, data=credential)

        vdc = service.producers['vdc'][0]
        vdcId = vdc.model.data.cloudspaceId

        API_URL = url + '/restmachine/cloudapi/cloudspaces/get'
        API_BODY = {'cloudspaceId': vdcId}

        response = session.get(url=API_URL, data=API_BODY)

        if response.status_code == 200:
            service.model.data.result = 'Succeeded : %s ' % create_cloudspace_test.__name__
        else:
            response_data = {'status_code': response.status_code,
                             'content': response.content}
            service.model.data.result = 'Failures : %s' % str(response_data)

    except:
        service.model.result = 'Errors : %s' % str(sys.exc_info()[:2])
    service.save()
