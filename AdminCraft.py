#!/usr/bin/env python

import shlex, os
import string, re
import json
import subprocess
import fileinput
from flask import Flask
from flask import request
from flask import render_template
from flask import Markup
from flask import session, redirect, url_for, escape, request

import config

app = Flask(__name__)

#Main index.html page.
@app.route("/")
def index(name=None):

    if config.USERNAME != session.get('username') or config.PASSWORD != session.get('password'):
        return redirect(url_for("login"))

    #If user session, then display "Logged in as %"
    if 'username' in session:
        username = 'Logged in as %s' % escape(session['username'])
    else:
        username = 'You are not logged in'

    #Open and read -10 lines from the server.log file into object. Used to get last line for activeUsers below.
    loggingFile = config.MINECRAFTDIR + config.SERVERLOG
    loggingFile = open(loggingFile, "r")
    logging = loggingFile.readlines()[-10:]

    #Query active users by making the command call, then reading the last line. Needs re-factoring.
    queryActiveUsers = subprocess.Popen(config.MINECRAFTDAEMON + ' command list', shell=True)
    activeUsers = logging[-1:]
    for users in activeUsers:
        activeUsers = users[26:]
	
    #Read ops.txt to display Server Operators on Users section.
    opsFile = config.MINECRAFTDIR + config.SERVEROPS
    ops = open(opsFile, "r").readlines()
    ops = [i.rstrip() for i in ops]

    #Read white-list.txt to display Whitelisted on Users section.
    whiteListFile = config.MINECRAFTDIR + config.WHITELIST
    whiteListUsers = open(whiteListFile, "r").readlines()
    
    #Read banned-players.txt to display Banned Players on Users section.
    bannedUsersFile = config.MINECRAFTDIR + config.BANNEDPLAYERS
    bannedUsers = open(bannedUsersFile, "r").readlines()
    bannedUsers = [i.rstrip() for i in bannedUsers]

    #Read banned-ips.txt to display Banned IPs on Users section.
    bannedIPsFile = config.MINECRAFTDIR + config.BANNEDIPS
    bannedIPs = open(bannedIPsFile, "r").readlines()
    bannedIPs = [i.rstrip() for i in bannedIPs]

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

    return render_template('index.html', username=username, name=name, ops=ops, logging=logging, activeUsers=activeUsers, whiteListUsers=whiteListUsers, bannedUsers=bannedUsers, bannedIPs=bannedIPs, properties=properties, serverStatus=serverStatus, LOGINTERVAL=LOGINTERVAL)

#/server is used to send GET requests to Restart, Start, Stop or Backup server.
@app.route("/server", methods=['GET'])
def serverState():
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
@app.route("/command", methods=['GET'])
def sendCommand():
    
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
    return 'Sending Command...'

#/logging reads the last X amount of lines from server.log to be parsed out on GUI #mainConsole.
@app.route("/logging", methods=['GET'])
def logs():

    #Open and read last 40 lines. This needs to be configurable eventually.
    loggingFile = config.MINECRAFTDIR + config.SERVERLOG
    loggingFile = open(loggingFile, "r")
    loggingHTML = loggingFile.readlines()[-config.LOGLINES:]

    return render_template('logging.html', loggingHTML=loggingHTML)

#/dataValues is used to create a dataIcons.html view, which is then imported to Index. Used for "Give" on GUI.
@app.route("/dataValues", methods=['GET'])
def dataValues():
    return render_template('dataIcons.html')

#/login will be for sessions. So far, only username is accepted with any value. Needs work here.
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        return redirect(url_for('index'))
    return render_template('login.html')

#Kill or Pop session when hitting /logout
@app.route('/logout')
def logout():
    # remove the username from the session if its there
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('index'))



#/commandList is used to create a commandList.html view, which is then imported to Index. Used for "Command" on GUI.
@app.route('/commandList', methods=['GET', 'POST'])
def commandList():
    return render_template('commandList.html')

@app.route('/rightColumn', methods=['GET', 'POST'])
def rightColumn():

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
    bannedUsers = open(bannedUsersFile, "r").readlines()
    bannedUsers = [i.rstrip() for i in bannedUsers]

    #Read banned-ips.txt to display Banned IPs on Users section.
    bannedIPsFile = config.MINECRAFTDIR + config.BANNEDIPS
    bannedIPs = open(bannedIPsFile, "r").readlines()
    bannedIPs = [i.rstrip() for i in bannedIPs]


    return render_template('rightColumn.html', ops=ops, whiteListUsers=whiteListUsers, bannedUsers=bannedUsers, bannedIPs=bannedIPs, properties=properties)


#/serverConfig is used for GET request via server property configurations.

@app.route('/serverConfig', methods=['GET'])
def serverConfig():
    #Grab Vars from GET request
    allowNetherValue = request.args.get('allow-nether')
    levelNameValue = request.args.get('level-name')
    allowFlightValue = request.args.get('allow-flight')
    enableQueryValue = request.args.get('enable-query')
    serverPortValue = request.args.get('server-port')
    enableRconValue = request.args.get('enable-rcon')
    levelSeedValue = request.args.get('level-seed')
    serverIPValue = request.args.get('server-ip')
    whitelistValue = request.args.get('white-list')
    spawnAnimalsValue = request.args.get('spawn-animals')
    onlineModeValue = request.args.get('online-mode')
    pvpValue = request.args.get('pvp')
    difficultyValue = request.args.get('difficulty')
    gamemodeValue = request.args.get('gamemode')
    maxPlayersValue = request.args.get('max-players')
    spawnMonstersValue = request.args.get('spawn-monsters')
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
        if "enable-rcon" in pItem:
            pOutput = [w.replace(pItem, "enable-rcon" + '=' + enableRconValue + '\n') for w in pOutput]

    for pItem in pOutput:
        if "level-seed" in pItem:
            pOutput = [w.replace(pItem, "level-seed" + '=' + levelSeedValue + '\n') for w in pOutput]

    for pItem in pOutput:
        if "server-ip" in pItem:
            pOutput = [w.replace(pItem, "server-ip" + '=' + serverIPValue + '\n') for w in pOutput]

    for pItem in pOutput:
        if "white-list" in pItem:
            pOutput = [w.replace(pItem, "white-list" + '=' + whitelistValue + '\n') for w in pOutput]

    for pItem in pOutput:
        if "spawn-animals" in pItem:
            pOutput = [w.replace(pItem, "spawn-animals" + '=' + spawnAnimalsValue + '\n') for w in pOutput]

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
    return redirect(url_for('index'))
    #return render_template('serverConfig.html', pOutput=pOutput)

#/usersConfig - Adds/Removes users from User Config
@app.route('/addUser', methods=['GET', 'POST'])
def addUser():

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

@app.route('/removeUser', methods=['GET', 'POST'])
def removeUser():
    
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



#Turn on later
#@app.errorhandler(500)
#def not_found(error):
#    return render_template('500.html'), 500

#Run App, with debugging enabled.

app.secret_key = config.SECRETKEY                      #Set the secret sessions/cookies key here. Keep this key a secret!

if __name__ == "__main__":
    app.run(host=config.SERVERHOST, port=config.SERVERPORT, debug=config.DEBUGMODE, use_reloader=config.AUTORELOADER)






#Old code, not used. Saving, just in case.
@app.route('/serverConfigOld', methods=['GET'])
def serverConfig():
    #Grab Vars from GET request
    option = request.args.get('option')
    value = request.args.get('value')

    #Set server.properties
    p = MINECRAFTDIR + "/testconfig.properties"

    #Open properties as f and read-only. 
    f = open(p, "r")
    pText = f.readlines()

    #Each line is read. If line-item contains X text, then use value. Set as pOutput.
    for pItem in pText:
        if option in pItem:
            pOutput = [w.replace(pItem, option + '=' + value + '\n') for w in pText]

    #Close file for reading. Re-open as write and write out pOutput to file.
    f.close()
    o = open(p, "w")
    o.writelines(pOutput)
    o.close()

    return render_template('serverConfig.html', pOutput=pOutput)

