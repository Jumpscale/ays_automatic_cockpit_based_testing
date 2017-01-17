import os


class UpdateConfigFile(object):

    def update_config_file(self, cockpit_ip, account):
        script_dir = os.path.dirname(__file__)
        config_file = "../../Config/config.ini"
        config_path = os.path.join(script_dir, config_file)

        config = open(config_path, 'r')
        flag = True
        temp = []
        for line in config:
            if 'cockpit_url' in line:
                temp.append('cockpit_url = http://%s:5000/ays\n' % cockpit_ip)
            elif 'account' in line and account:
                temp.append('\n')
                temp.append('account = %s' % account)
                flag = False
            else:
                temp.append(line)
        if flag:
            temp.append('\n')
            temp.append('account = %s' % account)
        config.close()

        config = open(config_path, 'w')
        for line in temp:
            config.write(line)
        config.close()
