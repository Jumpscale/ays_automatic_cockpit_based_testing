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
    import unittest
    vdc = job.service.producers['vdc'][0]
    g8client = vdc.producers['g8client'][0]
    
    cl = j.clients.openvcloud.getFromService(g8client)
    acc = cl.account_get(vdc.model.data.account)

    space = acc.space_get(vdc.model.dbobj.name, vdc.model.data.location)
    #unittest.TestCase.assertEqual(space.model['name'], vdc.model.dbobj.name)
    result = ''
    log = open('/optvar/log.log', 'w')
    if space.model['name'] ==  vdc.model.dbobj.name:
        log.write('SUCCEEDED: %s == %s' % (space.model['name'], vdc.model.dbobj.name))
        log.write('/n')
        result = 'succeeded'
    else:
        log.write('FAIL: %s != %s' % (space.model['name'], vdc.model.dbobj.name))
        log.write('/n')
        result = 'fail'
    job.service.model.data.result = result
