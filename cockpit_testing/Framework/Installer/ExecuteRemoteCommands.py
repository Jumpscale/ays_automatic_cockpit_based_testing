from cockpit_testing.Framework.utils.utils import BaseTest
import paramiko
import json
import time


class ExecuteRemoteCommands():
    def __init__(self, ip, port, username, password):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password

        self.baseTest = BaseTest()
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connect_to_virtual_machine()

    def connect_to_virtual_machine(self):
        self.baseTest.logging.info(' * Connecting to the virtual machine .. ')
        for _ in range(300):
            try:
                self.ssh.connect(self.ip, port=self.port, username=self.username, password=self.password)
                break
            except:
                time.sleep(2)
                self.baseTest.logging.info(' * Trying to connect to the virtual machine .. ')
        else:
            self.ssh.connect(self.ip, port=self.port, username=self.username, password=self.password)


    def update_machine(self):
        self.baseTest.logging.info(' * Updating virtual machine OS ... ')
        command = 'echo %s | sudo -S apt-get update' % self.password
        self.execute_command(command=command)

    def install_js(self):
        self.baseTest.logging.info(' * Creating jsInstaller file .... ')
        command = """echo 'cd $TMPDIR;\nexport JSBRANCH="8.1.0";\ncurl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/$JSBRANCH/install/install.sh?$RANDOM > install.sh;\nbash install.sh;' > jsInstaller.sh"""
        self.execute_command(command=command)

        self.baseTest.logging.info(' * Executing jsInstaller .... ')
        command = 'echo %s | sudo -S bash jsInstaller.sh' % self.password
        self.execute_command(command=command)

    def install_cockpit(self):
        self.baseTest.logging.info(' * Creating cockpitInstaller.py file ... ')
        command = """echo 'from JumpScale import j\ncuisine = j.tools.cuisine.local\ncuisine.solutions.cockpit.install_all_in_one(start=True, branch="8.1.0", reset=True, ip="%s")' >  cockpitInstaller.py""" % self.ip
        self.execute_command(command=command)

        self.baseTest.logging.info(' * Executing cockpitInstaller.py file ... ')
        command = 'echo %s | sudo -S jspython cockpitInstaller.py' % self.password
        self.execute_command(command=command)

    def execute_command(self, command):
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            self.baseTest.logging.info(stdout.readlines())
        except:
            self.baseTest.logging.error(" * ERROR : Can't execute %s command" % command)
