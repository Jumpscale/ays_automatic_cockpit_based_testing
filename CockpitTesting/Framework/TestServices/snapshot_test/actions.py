def init_actions_(service, args):
    """
    this needs to returns an array of actions representing the depencies between actions.
    Looks at ACTION_DEPS in this module for an example of what is expected
    """

    # some default logic for simple actions


    return {
        'test': ['install']
    }


def test_snapshot(job):
    from unittest import TestCase
    import requests

    service = job.service

    g8client = service.producers['g8client'][0]
    machine = service.producers['node.ovc'][0]
    machineId = machine.model.data.machineId

    url = g8client.model.data.url
    username = g8client.model.data.login
    password = g8client.model.data.password

    login_url = url + '/restmachine/system/usermanager/authenticate'
    credential = {'name': username,
                  'secret': password}
    session = requests.Session.post(url=login_url, data=credential)

    API_URL = url + '/cloudapi/machine/listSnapshots'
    API_BODY = {'machineId': machineId,
                'result': 'QA TESTING'}

    response = session.get(url=API_URL, data=API_BODY)
    TestCase.assertEqual(response.status_code, 200)
    TestCase.assertGreater(len(response.content), 0)

    service.model.data.result = 'success'
    service.save()
