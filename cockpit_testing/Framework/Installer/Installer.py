from RequestEnvAPI import RequestEnvAPI
from ExecuteRemoteCommands import ExecuteRemoteCommands
from UpdateConfig import UpdateConfigFile
from optparse import OptionParser

if __name__ == '__main__':
    print(' * Installer is running .... ')

    parser = OptionParser()
    parser.add_option('-b', help=' * branch, Default : 8.1.0 ', dest='branch', default='8.1.0', action='store')
    parser.add_option('-a', '--use-account', help=' * use a specific account', dest='account', default='',
                      action='store')
    parser.add_option('--teardown', help=' * Tear down the cockpit after installation', dest='tearDown',
                      default=False, action='store_true')
    (options, args) = parser.parse_args()

    JS_branch = options.branch
    CP_branch = options.branch
    DefaultAccount = options.account
    tearDown = options.tearDown

    requestEnvAPI = RequestEnvAPI()
    if DefaultAccount:
        requestEnvAPI.get_account_ID(account=options.account)
    else:
        requestEnvAPI.create_account()
    requestEnvAPI.create_cloudspace()
    requestEnvAPI.create_virtualmachine()
    requestEnvAPI.create_port_forward(publicPorts={22: 2222,
                                                   82: 80,
                                                   5000: 5000})

    executeRemoteCommands = ExecuteRemoteCommands(ip=requestEnvAPI.cloudspace['ip'],
                                                  port=2222,
                                                  username='cloudscalers',
                                                  password=requestEnvAPI.virtualmahine['password']
                                                  )
    executeRemoteCommands.update_machine()
    executeRemoteCommands.install_js(branch=JS_branch)
    executeRemoteCommands.install_cockpit(branch=CP_branch)
    executeRemoteCommands.check_cockpit_portal(cockpit_ip=requestEnvAPI.cloudspace['ip'])
    executeRemoteCommands.check_branchs_values(branch=JS_branch)

    if not DefaultAccount and tearDown:
        requestEnvAPI.teardown()
    else:
        updateConfigFile = UpdateConfigFile()
        updateConfigFile.update_config_file(cockpit_ip=requestEnvAPI.cloudspace['ip'],
                                            account=requestEnvAPI.values['account'])

