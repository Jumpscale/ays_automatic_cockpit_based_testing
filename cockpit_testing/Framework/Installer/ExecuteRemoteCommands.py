from cockpit_testing.Framework.utils.utils import BaseTest
import paramiko, requests, time, subprocess, os, re


class ExecuteRemoteCommands:
    def __init__(self, ip, port, username, password):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password

        self.baseTest = BaseTest()
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connect_to_virtual_machine()
        self.sftp = self.ssh.open_sftp()

        script_dir = os.path.dirname(__file__)
        self.portal_config_source = os.path.join(script_dir, '../../production_config/portal_config_source.hrd')
        self.api_config_source = os.path.join(script_dir, '../../production_config/api_config_source.toml')
        self.api_config = os.path.join(script_dir, '../../production_config/api_config.toml')
        self.portal_config = os.path.join(script_dir, '../../production_config/portal_config.hrd')

    def connect_to_virtual_machine(self):
        self.baseTest.logging.info(' [*] Connecting to the virtual machine .. ')
        print(' [*] Connecting to the virtual machine .. ')
        for _ in range(300):
            try:
                self.ssh.connect(self.ip, port=self.port, username=self.username, password=self.password)
                break
            except:
                time.sleep(2)
                self.baseTest.logging.info(' [*] Trying to connect to the virtual machine .. ')
        else:
            self.ssh.connect(self.ip, port=self.port, username=self.username, password=self.password)

    def update_machine(self):
        self.baseTest.logging.info(' [*] Updating virtual machine OS ... ')
        print(' [*] Updating virtual machine OS ... ')
        command = 'echo %s | sudo -S apt-get update' % self.password
        self.execute_command(command=command)

    def install_js(self, branch):
        self.baseTest.logging.info(' [*] Creating jsInstaller file .... ')
        print(' [*] Creating jsInstaller file .... ')
        command = """echo 'cd $TMPDIR;\nexport JSBRANCH=%s;\ncurl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core8/$JSBRANCH/install/install.sh?$RANDOM > install.sh;\nbash install.sh;' > jsInstaller.sh""" % branch
        self.execute_command(command=command)

        self.baseTest.logging.info(' [*] Executing jsInstaller from %s branch .... ' % branch)
        print(' [*] Executing jsInstaller .... ')
        command = 'echo %s | sudo -S bash jsInstaller.sh' % self.password
        result = self.execute_command(command=command)

        if len(result) == 0:
            self.baseTest.logging.error(' [*] FAIL : fail in executing jsInstaller file .... ')
            print(' [*] FAIL : fail in executing jsInstaller file .... ')
            # raise NameError(' [*] FAIL : fail in executing jsInstaller file .... ')

    def install_cockpit(self, branch):
        self.baseTest.logging.info(' [*] Creating cockpitInstaller.py file ... ')
        print(' [*] Creating cockpitInstaller.py file ... ')
        if branch == '8.1.0' or branch == '8.1.1':
            command = """echo 'from JumpScale import j\ncuisine = j.tools.cuisine.local\ncuisine.solutions.cockpit.install_all_in_one(start=True, branch="%s", reset=True, ip="%s")' >  cockpitInstaller.py""" % (
                branch, self.ip)
        else:
            command = """echo 'from JumpScale import j\ncuisine = j.tools.cuisine.local\ncuisine.apps.portal.install()' >  cockpitInstaller.py"""

        self.execute_command(command=command)

        self.baseTest.logging.info(' [*] Executing cockpitInstaller from %s brnach ... ' % branch)
        print(' [*] Executing cockpitInstaller.py file ... ')
        command = 'echo %s | sudo -S jspython cockpitInstaller.py' % self.password
        result = self.execute_command(command=command)
        if len(result) == 0:
            self.baseTest.logging.error(' [*] FAIL : fail in executing cockpitInstaller file .... ')
            print((' [*] FAIL : fail in executing cockpitInstaller file .... '))
        elif branch != '8.1.0' and branch != '8.1.1':
            command = 'echo %s | sudo -S ays start' % self.password
            result = self.execute_command(command=command)
            if len(result) == 0:
                self.baseTest.logging.error(' [*] FAIL : fail in running "ays start" .... ')
                print((' [*] FAIL :fail in running "ays start" .... '))

    def execute_command(self, command):
        try:
            stdin, stdout, stderr = self.ssh.exec_command(command)
            tracback = stdout.readlines()
            return tracback
        except:
            self.baseTest.logging.error(" [*] ERROR : Can't execute %s command" % command)

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
                    self.baseTest.logging.info(' [*] You can access the new cockpit on : http:%s ' % self.ip)
                    print((' [*] You can access the new cockpit on : http://%s ' % self.ip))
                    return True
                else:
                    time.sleep(5)
                    continue
        else:
            print(' [*] [X] FAIL : Please, Check installtion files in %s vm ' % cockpit_ip)
            self.baseTest.logging.error(' [*] FAIL : Please, Check installtion files in %s vm ' % cockpit_ip)
            return False

    def check_branchs_values(self, branch):
        self.baseTest.logging.info(' [*] Getting branches versions ... ')
        print(' [*] Getting branches versions ... ')
        dir = ['ays_jumpscale8', 'jscockpit', 'jumpscale_core8', 'jumpscale_portal8']
        for item in dir:
            command = 'cd /opt/code/github/jumpscale/%s && git branch' % item
            result = self.execute_command(command=command)
            if len(result) == 0:
                self.baseTest.logging.error(' [*] FAIL : fail in getting %s branch .... ' % item)
                print(' [*] FAIL : fail in getting %s branch version .... ' % item)
            elif branch not in result[0]:
                self.baseTest.logging.error(
                    ' [*] ERROR : %s branch is not matching with %s:%s branch' % (branch, item, result))
                print(' [*] ERROR : %s branch is not matching with %s:%s branch' % (branch, item, result))
            else:
                self.baseTest.logging.error(
                    ' [*] OK : %s branch is matching with %s:%s branch' % (branch, item, result))
                print(' [*] OK : %s branch is matching with %s:%s branch' % (branch, item, result))

    def trasport_file(self, filepath):
        file_name = filepath.split('/')[-1]
        self.sftp.put(filepath, file_name)

    def generat_production_config_files(self):
        client_id = self.baseTest.values['client_id']
        client_secret = self.baseTest.values['client_secret']

        open("tmp", "w").writelines([l for l in open(self.portal_config_source).readlines()])
        with open(self.portal_config, 'w') as portal:
            with open('tmp') as tmp:
                for line in tmp:
                    if 'param.cfg.production' in line:
                        portal.write('param.cfg.production = true\n')
                    elif 'param.cfg.client_scope' in line:
                        portal.write("param.cfg.client_scope = 'user:email:main,user:memberof:%s'\n" % client_id)
                    elif 'param.cfg.force_oauth_instance' in line:
                        portal.write("param.cfg.force_oauth_instance = 'itsyou.online'\n")
                    elif 'param.cfg.client_id' in line:
                        portal.write("param.cfg.client_id = '%s'\n" % client_id)
                    elif 'param.cfg.client_secret' in line:
                        portal.write("param.cfg.client_secret = '%s'\n" % client_secret)
                    elif 'param.cfg.redirect_url' in line:
                        portal.write(
                            "param.cfg.redirect_url = 'http://%s/restmachine/system/oauth/authorize'\n" % self.ip)
                    elif 'param.cfg.client_user_info_url' in line:
                        portal.write("param.cfg.client_user_info_url = 'https://itsyou.online/api/users/'\n")
                    elif 'param.cfg.token_url' in line:
                        portal.write("param.cfg.token_url = 'https://itsyou.online/v1/oauth/access_token'\n")
                    elif 'param.cfg.organization =' in line:
                        portal.write("param.cfg.organization = '%s'\n" % client_id)
                    elif 'param.cfg.oauth.default_groups' in line:
                        portal.write("param.cfg.oauth.default_groups = 'admin', 'user',\n")
                    else:
                        portal.write(line)
        portal.close()
        open("tmp", "w").writelines([l for l in open(self.api_config_source).readlines()])
        with open(self.api_config, 'w') as api:
            with open('tmp') as tmp:
                for line in tmp:
                    if 'prod = false' in line:
                        api.write('prod = true\n')
                    elif 'organization = ' in line:
                        api.write('organization = "%s" \n' % client_id)
                    elif 'redirect_uri = ' in line:
                        api.write('redirect_uri = "http://%s/api/oauth/callback"\n' % self.ip)
                    elif 'client_secret =' in line:
                        api.write('client_secret = "%s"\n' % client_secret)
                    elif 'client_id = ' in line:
                        api.write('client_id = "%s" \n' % client_id)
                    elif 'jwt' in line:
                        api.write(
                            'jwt_key = "-----BEGIN PUBLIC KEY-----\\nMHYwEAYHKoZIzj0CAQYFK4EEACIDYgAES5X8XrfKdx9gYayFITc89wad4usrk0n2\\n7MjiGYvqalizeSWTHEpnd7oea9IQ8T5oJjMVH5cc0H5tFSKilFFeh//wngxIyny6\\n6+Vq5t5B0V0Ehy01+2ceEon2Y0XDkIKv\\n-----END PUBLIC KEY-----\\n"')
                    else:
                        api.write(line)
        api.close()

    def move_produciton_file(self):
        self.baseTest.logging.info(' [*] Moving production config files .... ')
        print(' [*] Moving production config files .... ')

        command = 'echo %s | sudo -S mv -f /home/cloudscalers/api_config.toml /optvar/cfg/cockpit_api/config.toml' % self.password
        self.execute_command(command=command)

        command = 'echo %s | sudo -S mv -f /home/cloudscalers/portal_config.hrd /optvar/cfg/portals/main/config.hrd' % self.password
        self.execute_command(command=command)

    def restart_cockpit_services(self):
        self.baseTest.logging.info(' [*] Restarting cockpit services .... ')
        print(' [*] Restarting cockpit services .... ')
        command = 'echo %s | sudo -S service portal restart && sudo -S service cockpit_main restart && sudo -S service cockpit_daemon_main restart' % self.password
        self.execute_command(command=command)

    def remove_tmp_files(self):
        subprocess.call('rm %s' % self.api_config, shell=True)
        subprocess.call('rm %s' % self.portal_config, shell=True)
        script_dir = os.path.dirname(__file__)
        subprocess.call('rm %s' % os.path.join(script_dir, '../../../tmp'), shell=True)

    def production_mode(self):
        self.generat_production_config_files()
        self.trasport_file(self.portal_config)
        self.trasport_file(self.api_config)
        self.move_produciton_file()
        self.restart_cockpit_services()
        self.remove_tmp_files()
        print(
            ' [*] Please, Update the callback url of ITSYOUONLINE to be http://%s/restmachine/system/oauth/authorize' % self.ip)
