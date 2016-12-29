import threading
import Queue
from cockpit_testing.Framework.utils.utils import BaseTest
import time, traceback, sys
from optparse import OptionParser

from RequestEnvAPI import RequestEnvAPI
from ExecuteRemoteCommands import ExecuteRemoteCommands


requestEnvAPI = RequestEnvAPI()
ERC = ExecuteRemoteCommands()

requestEnvAPI.create_account()
requestEnvAPI.create_cloudspace()
requestEnvAPI.create_virtualmachine()
'''
requestEnvAPI.create_ssh_port_forward()

ERC.connect_to_machine()
ERC.execute_command(' install js commands ')
ERC.execute_command(' install cockpit commands ' )
'''

