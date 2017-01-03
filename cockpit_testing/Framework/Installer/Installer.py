from RequestEnvAPI import RequestEnvAPI
from ExecuteRemoteCommands import ExecuteRemoteCommands
from UpdateConfig import UpdateConfigFile

requestEnvAPI = RequestEnvAPI()
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
executeRemoteCommands.install_js()
executeRemoteCommands.install_cockpit()

updateConfigFile = UpdateConfigFile()
updateConfigFile.update_config_file(cockpit_ip='2.2.2.2')
