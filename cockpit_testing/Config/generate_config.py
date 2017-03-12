#!/usr/bin/python
try:
    import configparser
except:
    from six.moves import configparser
# import sys
from optparse import OptionParser

# cmdargs = sys.argv
parser = OptionParser()
parser.add_option('-e', '--env', help='environment url', dest='environment', default='', action='store')
parser.add_option('-u', '--env-user', help='environment username', dest='env_username', default='', action='store')
parser.add_option('-p', '--env-passwd', help='environment password', dest='env_passwd', default='', action='store')
parser.add_option('-l', '--location', help='environment store location', dest='location', default='', action='store')
parser.add_option('-c', '--cockpit', help='cockpit url and port', dest='cockpit', default='', action='store')
parser.add_option('-i', '--client-id', help='client_id', dest='client_id', default='', action='store')
parser.add_option('-s', '--client-secret', help='client_secret', dest='client_secret', default='', action='store')
parser.add_option('-r', '--repo', help='dev repo with bp test templates', dest='repo', default='', action='store')
parser.add_option('-b', '--branch', help='branch for dev repo with bp test templates', dest='branch', default='', action='store')
parser.add_option('-t', '--threads-number', help='Number of test cases to run in parallel', dest='threads_number', default='1', action='store')
(options, args) = parser.parse_args()

config = configparser.ConfigParser()
config.read('config.ini')
config.set('main', 'environment', options.environment)
config.set('main', 'username', options.env_username)
config.set('main', 'password', options.env_passwd)
config.set('main', 'location', options.location)
config.set('main', 'cockpit_url', options.cockpit)
config.set('main', 'client_id', options.client_id)
config.set('main', 'client_secret', options.client_secret)
config.set('main', 'repo', options.repo)
config.set('main', 'branch', options.branch)
config.set('main', 'threads_number', options.threads_number)
with open('config.ini', 'w') as configfile:
    config.write(configfile)
