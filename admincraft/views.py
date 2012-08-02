#!/usr/bin/env python

import subprocess, os.path
import sqlite3
import shutil
import tarfile
import datetime
import csv
from time import sleep
import datetime

from flask import Flask
from flask import request
from flask import render_template
from flask import Markup
from flask import session, redirect, url_for, escape, request
from flask import Blueprint
from flask import g

import config
from tasks import startTaskDaemon, stopTaskDaemon, checkStatus

admincraft = Blueprint('admincraft', __name__, template_folder='templates', static_folder='static')

#Main index.html page.
@admincraft.route("/")
def index(name=None):

    #Check if username and password in session are valid. If not, redirect to login
    if config.USERNAME != session.get('username') or config.PASSWORD != session.get('password'):
        return redirect(url_for('admincraft.login'))

    #If user session, then display "Logged in as %"
    if 'username' in session:
        username = 'Logged in as %s' % escape(session['username'])
    else:
        username = 'You are not logged in'

    #Open and read -10 lines from the server.log file into object. Used to get last line for activeUsers below.
    loggingFile = config.MINECRAFTDIR + config.SERVERLOG
    loggingFile = open(loggingFile, "r")
    logging = loggingFile.readlines()[-10:]


	
    #Read ops.txt to display Server Operators on Users section.
    opsFile = config.MINECRAFTDIR + config.SERVEROPS
    ops = open(opsFile, "r").readlines()
    ops = [i.rstrip() for i in ops]

    #Read white-list.txt to display Whitelisted on Users section.
    whiteListFile = config.MINECRAFTDIR + config.WHITELIST
    whiteListUsers = open(whiteListFile, "r").readlines()


    #Read banned-ips.txt to display Banned IPs on Users section.
    bannedIPsFile = config.MINECRAFTDIR + config.BANNEDIPS
    bannedIPs = csv.reader(open(bannedIPsFile, "r").readlines(), delimiter='|')
    #bannedIPs = [i.rstrip() for i in bannedIPs] #pre 1.3
    for b in bannedIPs:
        print b
    
    #Read server.properties to display Server Properties on Server Config section. -2 first lines.
    propertiesFile = config.MINECRAFTDIR + config.SERVERPROPERTIES
    properties = open(propertiesFile, "r").readlines()[2:]


    #Capturing status by running status command to /etc/init.d/minecraft and returning as stdout.
    stdout = subprocess.Popen([config.MINECRAFTDAEMON + " status"], stdout=subprocess.PIPE, shell=True).communicate()[0]
    
    #Check status and display Online or Offline to index.html (bottom-right corner) page.
    serverStatus = stdout
    print serverStatus
    if "online" in serverStatus:
        serverStatus = Markup('<font color="#339933"><strong>Online</strong></font>')

    elif "offline" in serverStatus:
        serverStatus = Markup('<font color="#339933"><strong>Offline</strong></font>')
    else:
        serverStatus = "Unable to check server status."

    LOGINTERVAL = config.LOGINTERVAL

    return render_template('index.html', username=username, name=name, ops=ops, logging=logging, whiteListUsers=whiteListUsers, bannedIPs=bannedIPs, properties=properties, serverStatus=serverStatus, LOGINTERVAL=LOGINTERVAL)


#/server is used to send GET requests to Restart, Start, Stop or Backup server.
@admincraft.route("/server", methods=['GET'])
def serverState():

    #Check if username and password in session are valid. If not, redirect to login
    if config.USERNAME != session.get('username') or config.PASSWORD != session.get('password'):
        return redirect(url_for('admincraft.login'))

    #Grab option value from GET request.
    keyword = request.args.get('option')

    #Check status value and run /etc/init.d/minecraft command to restart/start/stop/backup.
    if keyword == "restart":
        subprocess.Popen(config.MINECRAFTDAEMON + ' restart', shell=True)
        return 'Restarting Minecraft Server...'
    elif keyword == "start":
        subprocess.Popen(config.MINECRAFTDAEMON + ' start', shell=True)
        return 'Starting Minecraft Server...'
    elif keyword == "stop":
        subprocess.Popen(config.MINECRAFTDAEMON + ' stop', shell=True)
        return 'Stopping Minecraft Server...'
    elif keyword == "backup":
        subprocess.Popen(config.MINECRAFTDAEMON + ' backup', shell=True)
        return 'Backing Up Minecraft Server...'

    #If option value is 'status', then capture output and return 'Server is Online' or 'Server is Offline'
    elif keyword == "status":
        stdout = subprocess.Popen([config.MINECRAFTDAEMON + " status"], stdout=subprocess.PIPE, shell=True).communicate()[0]
        serverStatus = stdout
        if "online" in serverStatus:
            serverStatus = Markup('Server is <font color="#339933"><strong>Online</strong></font>')

        elif "offline" in serverStatus:
            serverStatus = Markup('Server is <font color="#FF0000"><strong>Offline</strong></font>')
        else:
            serverStatus = "Unable to check server status."
        return serverStatus
    else: 
        return 'Invalid Option'

#/command is used when sending commands to '/etc/init.d/minecraft command' from the GUI. Used on mainConsole on index.html.
@admincraft.route("/command", methods=['GET'])
def sendCommand():
    #server.log file for logging command entered
    loggingFile = config.MINECRAFTDIR + config.SERVERLOG
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    print time

    #Check if username and password in session are valid. If not, redirect to login
    if config.USERNAME != session.get('username') or config.PASSWORD != session.get('password'):
        return redirect(url_for('admincraft.login'))

    #Grabs operater value from GET request. say/give/command
    consoleOperator = str(request.args.get('operator'))

    #If the value was "command", then set as '' to remove redundancies when Popen is executed below.
    if consoleOperator == "command":
        consoleOperator = ''
    #Otherwise, keep the value. (say/give)
    else:
        consoleOperator = consoleOperator + ' '


    #Grab value from command GET request. This was entered via user from textInput box.
    command = str(request.args.get('command'))

    #Initiate full command via Popen. Return "Sending Command..."
    commandProc = config.MINECRAFTDAEMON + ' command "' + consoleOperator + command + '"'
    subprocess.Popen(commandProc, shell=True)
    print commandProc
    
    # Post Minecraft 1.3, Console logging was removed, so appending command entered to file manually.
    with open(loggingFile, "a") as f:
        f.write(time + " [CONSOLE] " + command + "\n")
    return 'Sending Command...'

#/logging reads the last X amount of lines from server.log to be parsed out on GUI #mainConsole.
@admincraft.route("/logging", methods=['GET'])
def logs():

    #Check if username and password in session are valid. If not, redirect to login
    if config.USERNAME != session.get('username') or config.PASSWORD != session.get('password'):
        return redirect(url_for('admincraft.login'))

    #Open and read last 40 lines. This needs to be configurable eventually.
    loggingFile = config.MINECRAFTDIR + config.SERVERLOG
    loggingFile = open(loggingFile, "r")
    loggingHTML = loggingFile.readlines()[-config.LOGLINES:]

    return render_template('logging.html', loggingHTML=loggingHTML)

#/dataValues is used to create a dataIcons.html view, which is then imported to Index. Used for "Give" on GUI.
@admincraft.route("/dataValues", methods=['GET'])
def dataValues():
    #Check if username and password in session are valid. If not, redirect to login
    if config.USERNAME != session.get('username') or config.PASSWORD != session.get('password'):
        return redirect(url_for('admincraft.login'))

    return render_template('dataIcons.html')

#/login will be for sessions. So far, only username is accepted with any value. Needs work here.
@admincraft.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        return redirect(url_for('admincraft.index'))
    return render_template('login.html')

#Kill or Pop session when hitting /logout
@admincraft.route('/logout')
def logout():
    # remove the username from the session if its there
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('admincraft.index'))

#/commandList is used to create a commandList.html view, which is then imported to Index. Used for "Command" on GUI.
@admincraft.route('/commandList', methods=['GET', 'POST'])
def commandList():

    #Check if username and password in session are valid. If not, redirect to login
    if config.USERNAME != session.get('username') or config.PASSWORD != session.get('password'):
        return redirect(url_for('admincraft.login'))

    return render_template('commandList.html')

@admincraft.route('/tabs', methods=['GET', 'POST'])
def tabs():

    #Check if username and password in session are valid. If not, redirect to login
    if config.USERNAME != session.get('username') or config.PASSWORD != session.get('password'):
        return redirect(url_for('admincraft.login'))

    #Read server.properties to display Server Properties on Server Config section. -2 first lines.
    propertiesFile = config.MINECRAFTDIR + config.SERVERPROPERTIES
    properties = open(propertiesFile, "r").readlines()[2:]

    #Read ops.txt to display Server Operators on Users section.
    opsFile = config.MINECRAFTDIR + config.SERVEROPS
    ops = open(opsFile, "r").readlines()
    ops = [i.rstrip() for i in ops]

    #Read white-list.txt to display Whitelisted on Users section.
    whiteListFile = config.MINECRAFTDIR + config.WHITELIST
    whiteListUsers = open(whiteListFile, "r").readlines()
    whiteListUsers = [i.rstrip() for i in whiteListUsers]
    
    #Read banned-players.txt to display Banned Players on Users section.
    bannedUsersFile = config.MINECRAFTDIR + config.BANNEDPLAYERS
    bannedUsers = csv.reader(open(bannedUsersFile, "r").readlines()[3:], delimiter='|', quoting=csv.QUOTE_ALL)
    #bannedUsers = [i.rstrip() for i in bannedUsers] #pre 1.3
    bannedUsersList = []
    for u in bannedUsers:
        bannedUsersList.append(u[0])

    #Read banned-ips.txt to display Banned IPs on Users section.
    bannedIPsFile = config.MINECRAFTDIR + config.BANNEDIPS
    bannedIPs = csv.reader(open(bannedIPsFile, "r").readlines()[3:], delimiter='|', quoting=csv.QUOTE_ALL)
    #bannedIPs = [i.rstrip() for i in bannedIPs]
    bannedIPsList = []
    for i in bannedIPs:
        bannedIPsList.append(i[0])
    
    
    #Ghetto method of shelling out the 'list' command to minecraft init script, which returns
    #the list of players in server.log. Grab last line of server.log, strip time/date
    #and determine whether players are connected or not. Rest of logic in Jinja2 tabs.html.
    subprocess.Popen(config.MINECRAFTDAEMON + ' command list', shell=True)
    sleep(1) #Unfortunately, the minecraft init commands lag a bit, so this is required to grab the last line correctly.
    activeUsersFile = config.MINECRAFTDIR + config.SERVERLOG
    activeUsers = open(activeUsersFile, "r").readlines()[-1:]
    activeUsers = [i.rstrip()[46:] for i in activeUsers]
    noUsers = "No players connected" #If activeUsers list is empty, Jinja2 will use this variable instead.

    backupDir = config.BACKUPDIR

    isRunning = Markup('Task Scheduler <font color="#339933"><strong>Online</strong></font>')

    #Connects to db to list scheduled jobs in a table
    dbpath = config.DATABASE

    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    c.execute('select * from tasks order by type')
    a = c.fetchall()
    conn.commit()
    c.close()

    return render_template('tabs.html', a=a, activeUsers=activeUsers, isRunning=isRunning, backupDir=backupDir, ops=ops, whiteListUsers=whiteListUsers, bannedUsersList=bannedUsersList, bannedIPsList=bannedIPsList, properties=properties)

#/serverConfig is used for GET request via server property configurations.
@admincraft.route('/serverConfig', methods=['GET'])
def serverConfig():

    #Check if username and password in session are valid. If not, redirect to login
    if config.USERNAME != session.get('username') or config.PASSWORD != session.get('password'):
        return redirect(url_for('admincraft.login'))

    #Grab Vars from GET request
    allowNetherValue = request.args.get('allow-nether')
    levelNameValue = request.args.get('level-name')
    allowFlightValue = request.args.get('allow-flight')
    enableQueryValue = request.args.get('enable-query')
    serverPortValue = request.args.get('server-port')
    levelTypeValue = request.args.get('level-type')
    enableRconValue = request.args.get('enable-rcon')
    levelSeedValue = request.args.get('level-seed')
    serverIPValue = request.args.get('server-ip')
    maxBuildHeightValue = request.args.get('max-build-height')
    spawnNPCsValue = request.args.get('spawn-npcs')
    whitelistValue = request.args.get('white-list')
    spawnAnimalsValue = request.args.get('spawn-animals')
    onlineModeValue = request.args.get('online-mode')
    pvpValue = request.args.get('pvp')
    difficultyValue = request.args.get('difficulty')
    gamemodeValue = request.args.get('gamemode')
    maxPlayersValue = request.args.get('max-players')
    spawnMonstersValue = request.args.get('spawn-monsters')
    generateStructuresValue = request.args.get('generate-structures')
    viewDistanceValue = request.args.get('view-distance')
    motdValue = request.args.get('motd')

    #Set server.properties
    p = config.MINECRAFTDIR + config.SERVERPROPERTIES

    #Open properties as f and read-only. 
    f = open(p, "r")
    pText = f.readlines()

    #Each line is read. If line-item contains X text, then use value. Set as pOutput.
    for pItem in pText:
        if "allow-nether" in pItem:
            pOutput = [w.replace(pItem, "allow-nether" + '=' + allowNetherValue + '\n') for w in pText]

    for pItem in pOutput:
        if "level-name" in pItem:
            pOutput = [w.replace(pItem, "level-name" + '=' + levelNameValue + '\n') for w in pOutput]

    for pItem in pOutput:
        if "allow-flight" in pItem:
            pOutput = [w.replace(pItem, "allow-flight" + '=' + allowFlightValue + '\n') for w in pOutput]

    for pItem in pOutput:
        if "enable-query" in pItem:
            pOutput = [w.replace(pItem, "enable-query" + '=' + enableQueryValue + '\n') for w in pOutput]

    for pItem in pOutput:
        if "server-port" in pItem:
            pOutput = [w.replace(pItem, "server-port" + '=' + serverPortValue + '\n') for w in pOutput]

    for pItem in pOutput:
        if "level-type" in pItem:
            pOutput = [w.replace(pItem, "level-type" + '=' + levelTypeValue + '\n') for w in pOutput]

    for pItem in pOutput:
        if "enable-rcon" in pItem:
            pOutput = [w.replace(pItem, "enable-rcon" + '=' + enableRconValue + '\n') for w in pOutput]

    for pItem in pOutput:
        if "level-seed" in pItem:
            pOutput = [w.replace(pItem, "level-seed" + '=' + levelSeedValue + '\n') for w in pOutput]

    for pItem in pOutput:
        if "server-ip" in pItem:
            pOutput = [w.replace(pItem, "server-ip" + '=' + serverIPValue + '\n') for w in pOutput]

    for pItem in pOutput:
        if "max-build-height" in pItem:
            pOutput = [w.replace(pItem, "max-build-height" + '=' + maxBuildHeightValue + '\n') for w in pOutput]

    for pItem in pOutput:
        if "spawn-npcs" in pItem:
            pOutput = [w.replace(pItem, "spawn-npcs" + '=' + spawnNPCsValue + '\n') for w in pOutput]

    for pItem in pOutput:
        if "white-list" in pItem:
            pOutput = [w.replace(pItem, "white-list" + '=' + whitelistValue + '\n') for w in pOutput]

    for pItem in pOutput:
        if "spawn-animals" in pItem:
            pOutput = [w.replace(pItem, "spawn-animals" + '=' + spawnAnimalsValue + '\n') for w in pOutput]

    for pItem in pOutput:
        if "snooper-enabled" in pItem:
            pOutput = [w.replace(pItem, "snooper-enabled" + '=' + snooperEnabledValue + '\n') for w in pOutput]
            
    for pItem in pOutput:
        if "texture-pack" in pItem:
            pOutput = [w.replace(pItem, "texture-pack" + '=' + texturePackValue + '\n') for w in pOutput]
            
    for pItem in pOutput:
        if "online-mode" in pItem:
            pOutput = [w.replace(pItem, "online-mode" + '=' + onlineModeValue + '\n') for w in pOutput]

    for pItem in pOutput:
        if "pvp" in pItem:
            pOutput = [w.replace(pItem, "pvp" + '=' + pvpValue + '\n') for w in pOutput]

    for pItem in pOutput:
        if "difficulty" in pItem:
            pOutput = [w.replace(pItem, "difficulty" + '=' + difficultyValue + '\n') for w in pOutput]

    for pItem in pOutput:
        if "gamemode" in pItem:
            pOutput = [w.replace(pItem, "gamemode" + '=' + gamemodeValue + '\n') for w in pOutput]

    for pItem in pOutput:
        if "max-players" in pItem:
            pOutput = [w.replace(pItem, "max-players" + '=' + maxPlayersValue + '\n') for w in pOutput]

    for pItem in pOutput:
        if "spawn-monsters" in pItem:
            pOutput = [w.replace(pItem, "spawn-monsters" + '=' + spawnMonstersValue + '\n') for w in pOutput]

    for pItem in pOutput:
        if "generate-structures" in pItem:
            pOutput = [w.replace(pItem, "generate-structures" + '=' + generateStructuresValue + '\n') for w in pOutput]

    for pItem in pOutput:
        if "view-distance" in pItem:
            pOutput = [w.replace(pItem, "view-distance" + '=' + viewDistanceValue + '\n') for w in pOutput]

    for pItem in pOutput:
        if "motd" in pItem:
            pOutput = [w.replace(pItem, "motd" + '=' + motdValue + '\n') for w in pOutput]

    #Close file for reading. Re-open as write and write out pOutput to file.
    f.close()
    o = open(p, "w")
    o.writelines(pOutput)
    o.close()
    return redirect(url_for('admincraft.index'))
    #return render_template('serverConfig.html', pOutput=pOutput)

#/usersConfig - Adds/Removes users from User Config
@admincraft.route('/addUser', methods=['GET', 'POST'])
def addUser():

    #Check if username and password in session are valid. If not, redirect to login
    if config.USERNAME != session.get('username') or config.PASSWORD != session.get('password'):
        return redirect(url_for('admincraft.login'))

    addType = request.args.get('type')
    addValue = request.args.get('user')

    if addType == "operators":
        f = config.MINECRAFTDIR + config.SERVEROPS
    elif addType == "whitelist":
        f =  config.MINECRAFTDIR + config.WHITELIST
    elif addType == "banned-players":
        f = config.MINECRAFTDIR + config.BANNEDPLAYERS
    elif addType == "banned-ips":
        f = config.MINECRAFTDIR + config.BANNEDIPS
    else:
        print "Error reading Add Type"

    #Open f as o and append value. 
    with open(f, "a") as o:
        o.write(addValue + "\n")
    
    o.close()

    return "User Added"

@admincraft.route('/removeUser', methods=['GET', 'POST'])
def removeUser():

    #Check if username and password in session are valid. If not, redirect to login
    if config.USERNAME != session.get('username') or config.PASSWORD != session.get('password'):
        return redirect(url_for('admincraft.login'))
    
    #Grab vars from GET request
    removeType = request.args.get('type')
    removeValue = request.args.get('user')

    if removeType == "operators":
        f = config.MINECRAFTDIR + config.SERVEROPS
    elif removeType == "whitelist":
        f =  config.MINECRAFTDIR + config.WHITELIST
    elif removeType == "banned-players":
        f = config.MINECRAFTDIR + config.BANNEDPLAYERS
    elif removeType == "banned-ips":
        f = config.MINECRAFTDIR + config.BANNEDIPS
    else:
        print "Error reading Remove Type"

    #Open f and read out lines
    o = open(f, "r").readlines()

    #Create a list as ops, minus the removeValue
    ops = []
    ops = [names for names in o if names != removeValue + "\n"]

    #Open ops.txt again for writing and write out new lines
    o = open(f, "w")
    o.writelines(ops)
    o.close()

    return "User Removed"

@admincraft.route('/task', methods=['GET'])
def taskService():

    #Check if username and password in session are valid. If not, redirect to login
    if config.USERNAME != session.get('username') or config.PASSWORD != session.get('password'):
        return redirect(url_for('admincraft.login'))

    command = request.args.get("command")

    if command == "stop":   
        stopTaskDaemon()
        return 'Shutting down task daemon...'
    elif command == "start":
        startTaskDaemon()
        return 'Starting task daemon...'
    elif command == "restart":
        stopTaskDaemon()
        startTaskDaemon()
        return 'Restarting task daemon...'
    elif command == "status":
        status = checkStatus()
    return status

@admincraft.route('/addTask', methods=['POST', 'GET'])
def addTask():

    #Check if username and password in session are valid. If not, redirect to login
    if config.USERNAME != session.get('username') or config.PASSWORD != session.get('password'):
        return redirect(url_for('admincraft.login'))    

    dbpath = config.DATABASE

    task = request.args.get("type")
    dom = request.args.get("dom")
    dow = request.args.get("dow")
    hour = request.args.get("hour")
    minute = request.args.get("minute")

    v = [task, dom, dow, hour, minute]

    if not os.path.exists(dbpath):
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        c.execute('''create table tasks (type text, month text, day text, hour text, minute text)''')

        conn.commit()
        c.close()

    else:
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        c.execute("INSERT into tasks VALUES (?,?,?,?,?)", v)
        c.execute('select * from tasks order by type')

        for row in c:
            print row

        conn.commit()
        c.close()
        
    return 'Task saved.'

#Turn on later
#@admincraft.errorhandler(500)
#def not_found(error):
#    return render_template('500.html'), 500


