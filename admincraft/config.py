# config.py reads config.ini and sets variable. This file does not need to be modified.

import os
import sys
from ConfigParser import SafeConfigParser

path = os.path.split(sys.argv[0])[0]

config = SafeConfigParser()
config.read('config.ini')
print path

# Main options required.
USERNAME = config.get('global', 'USERNAME')
PASSWORD = config.get('global', 'PASSWORD')
MINECRAFTDIR = config.get('global', 'MINECRAFTDIR')
SERVERHOST = config.get('global', 'SERVERHOST')
SERVERPORT = config.getint('global', 'SERVERPORT')
SECRETKEY = config.get('global', 'SECRETKEY')
BACKUPDIR = config.get('global', 'BACKUPDIR')

# Extra options, but not required.
LOGINTERVAL = config.getint('global', 'LOGINTERVAL')
LOGLINES = config.getint('global', 'LOGLINES')
MINECRAFTDAEMON = config.get('global', 'MINECRAFTDAEMON')
DATABASE = config.get('global', 'DATABASE')

# Default Minecraft Config files. 
SERVERLOG = config.get('global', 'SERVERLOG')
SERVERPROPERTIES = config.get('global', 'SERVERPROPERTIES')
SERVEROPS = config.get('global', 'SERVEROPS')
WHITELIST = config.get('global', 'WHITELIST')
BANNEDPLAYERS = config.get('global', 'BANNEDPLAYERS')
BANNEDIPS = config.get('global', 'BANNEDIPS')

AUTORELOADER = config.getboolean('global', 'AUTORELOADER')
DEBUGMODE = config.getboolean('global', 'DEBUGMODE')
