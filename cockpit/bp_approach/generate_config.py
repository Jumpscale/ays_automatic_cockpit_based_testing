#!/usr/bin/python
from configparser import ConfigParser
import sys


cmdargs = sys.argv
config = ConfigParser()
config.read('config.ini')
if not config.has_section('main'):
    config.add_section('main')
config.set('main', 'environment', cmdargs[1])
config.set('main', 'username', cmdargs[2])
config.set('main', 'password', cmdargs[3])
config.set('main', 'account', cmdargs[4])
config.set('main', 'location', cmdargs[5])
config.set('main', 'cockpit_url', cmdargs[6])
config.set('main', 'jwt', cmdargs[7])
with open('config.ini', 'w') as configfile:
    config.write(configfile)