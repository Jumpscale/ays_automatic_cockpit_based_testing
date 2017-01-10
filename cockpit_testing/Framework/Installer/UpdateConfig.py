import os


class UpdateConfigFile(object):

    def update_config_file(self, cockpit_ip):
        script_dir = os.path.dirname(__file__)
        config_file = "../../Config/config.ini"
        config_path = os.path.join(script_dir, config_file)

        config = open(config_path, 'r')
        temp = []
        for line in config:
            if 'cockpit_url' in line:
                temp.append('cockpit_url = http://%s:5000/ays\n' % cockpit_ip)
            else:
                temp.append(line)
        config.close()

        config = open(config_path, 'w')
        for line in temp:
            config.write(line)
        config.close()
