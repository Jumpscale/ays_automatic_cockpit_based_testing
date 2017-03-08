from cockpit_testing.Framework.utils.utils import BaseTest
import paramiko
import requests
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
        print(' * Connecting to the virtual machine .. ')
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
        print(' * Updating virtual machine OS ... ')
        command = 'echo %s | sudo -S apt-get update' % self.password
        self.execute_command(command=command)


    def install_js(self, branch):
        self.baseTest.logging.info(' * Creating jsInstaller file .... ')
        print(' * Creating jsInstaller file .... ')
        command = """echo 'cd $TMPDIR;\nexport JSBRANCH=%s;\ncurl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/$JSBRANCH/install/install.sh?$RANDOM > install.sh;\nbash install.sh;' > jsInstaller.sh""" % branch
        self.execute_command(command=command)

        self.baseTest.logging.info(' * Executing jsInstaller from %s branch .... ' % branch)
        print(' * Executing jsInstaller .... ')
        command = 'echo %s | sudo -S bash jsInstaller.sh' % self.password
        result = self.execute_command(command=command)

        if len(result) == 0:
            self.baseTest.logging.error(' * FAIL : fail in executing jsInstaller file .... ')
            print(' * FAIL : fail in executing jsInstaller file .... ')
            #raise NameError(' * FAIL : fail in executing jsInstaller file .... ')

    def install_cockpit(self, branch):
        self.baseTest.logging.info(' * Creating cockpitInstaller.py file ... ')
        print(' * Creating cockpitInstaller.py file ... ')
        command = """echo 'from JumpScale import j\ncuisine = j.tools.cuisine.local\ncuisine.solutions.cockpit.install_all_in_one(start=True, branch="%s", reset=True, ip="%s")' >  cockpitInstaller.py""" % (
        branch, self.ip)
        self.execute_command(command=command)

        self.baseTest.logging.info(' * Executing cockpitInstaller from %s brnach ... ' % branch)
        print(' * Executing cockpitInstaller.py file ... ')
        command = 'echo %s | sudo -S jspython cockpitInstaller.py' % self.password
        result = self.execute_command(command=command)
        if len(result) == 0:
            self.baseTest.logging.error(' * FAIL : fail in executing cockpitInstaller file .... ')
            print((' * FAIL : fail in executing cockpitInstaller file .... '))
            #raise NameError(' * FAIL : fail in executing cockpitInstaller file .... ')

    def execute_command(self, command):
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            tracback = stdout.readlines()
            return tracback
        except:
            self.baseTest.logging.error(" * ERROR : Can't execute %s command" % command)

    def check_cockpit_portal(self, cockpit_ip):
        url = 'http://' + cockpit_ip
        for _ in range(5):
            try:
                response = requests.get(url=url)
            except:
                time.sleep(5)
                continue
            else:
                if response.status_code == 200:
                    self.baseTest.logging.info(' * You can access the new cockpit on : http:%s ' % self.ip)
                    print((' * You can access the new cockpit on : http://%s ' % self.ip))
                    break
                else:
                    time.sleep(5)
                    continue
        else:
            print(' * FAIL : Please, Check installtion files in %s vm ' % cockpit_ip)
            self.baseTest.logging.error(' * FAIL : Please, Check installtion files in %s vm ' % cockpit_ip)

    def check_branchs_values(self, branch):
        self.baseTest.logging.info(' * Getting branches versions ... ')
        print(' * Getting branches versions ... ')
        dir = ['ays_jumpscale8', 'jscockpit', 'jumpscale_core8', 'jumpscale_portal8']
        for item in dir:
            command = 'cd /opt/code/github/jumpscale/%s && git branch' % item
            result = self.execute_command(command=command)
            if len(result) == 0:
                self.baseTest.logging.error(' * FAIL : fail in getting %s branch .... ' % item)
                print(' * FAIL : fail in getting %s branch version .... ' % item)
            elif branch not in result[0]:
                self.baseTest.logging.error(' * ERROR : %s branch is not matching with %s:%s branch' % (branch, item, result))
                print(' * ERROR : %s branch is not matching with %s:%s branch' % (branch, item, result))
            else:
                self.baseTest.logging.error(' * OK : %s branch is matching with %s:%s branch' % (branch, item, result))
                print(' * OK : %s branch is matching with %s:%s branch' % (branch, item, result))
                