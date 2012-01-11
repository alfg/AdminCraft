from ConfigParser import SafeConfigParser
config = SafeConfigParser()
config.read('config.ini')
# Main options required. Configure these.
USERNAME = config.get('global', 'USERNAME')
PASSWORD = config.get('global', 'PASSWORD')
MINECRAFTDIR = config.get('global', 'MINECRAFTDIR')       #Directory of Minecraft Server. Must have trailing slash.
SERVERHOST = config.get('global', 'SERVERHOST')                              #The hostname to listen on. Set this to '0.0.0.0' to have the server available externally
SERVERPORT = config.getint('global', 'SERVERPORT')                                  #The Port AdminCraft will use
SECRETKEY = config.get('global', 'SECRETKEY')                         #Set the secret sessions/cookies key here. Keep this key a secret!

# Extra options, but not required.
LOGINTERVAL = config.getint('global', 'LOGINTERVAL')                              #How often to refresh server log. 1000 = 1s
LOGLINES = config.getint('global', 'LOGLINES')                                    #How many lines to display in log
MINECRAFTDAEMON = config.get('global', 'MINECRAFTDAEMON')          #Location of minecraft init script

# Default Minecraft Config files. Only change if you know what youre doing.
SERVERLOG = config.get('global', 'SERVERLOG')
SERVERPROPERTIES = config.get('global', 'SERVERPROPERTIES')
SERVEROPS = config.get('global', 'SERVEROPS')
WHITELIST = config.get('global', 'WHITELIST')
BANNEDPLAYERS = config.get('global', 'BANNEDPLAYERS')
BANNEDIPS = config.get('global', 'BANNEDIPS')

AUTORELOADER = config.getboolean('global', 'AUTORELOADER') 								#Auto Reload on code changes
DEBUGMODE = config.getboolean('global', 'DEBUGMODE')
