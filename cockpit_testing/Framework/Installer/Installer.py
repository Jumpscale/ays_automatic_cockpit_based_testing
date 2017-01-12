from RequestEnvAPI import RequestEnvAPI
from ExecuteRemoteCommands import ExecuteRemoteCommands
from UpdateConfig import UpdateConfigFile
from optparse import OptionParser

if __name__ == '__main__':
    print ' * Installer is running .... '

    parser = OptionParser()
    parser.add_option('-b', help=' * Jumpscale branch, Default : 8.1.0 ', dest='JS_branch', default='8.1.0', action='store')
    parser.add_option('-s', help=' * Cockpit branch, Default : 8.1.0 ', dest='CP_branch', default='8.1.0', action='store')
    parser.add_option('-u', '--use-account', help='use a specific account', dest='account', default='', action='store')
    (options, args) = parser.parse_args()

    JS_branch = options.JS_branch
    CP_branch = options.CP_branch

    requestEnvAPI = RequestEnvAPI()
    if options.account:
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

    updateConfigFile = UpdateConfigFile()
    updateConfigFile.update_config_file(cockpit_ip=requestEnvAPI.cloudspace['ip'])
