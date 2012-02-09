#!/usr/bin/env python

# runBackup.py is imported by runserver.py. This module runs the
# backup commands on a scheduled basis. Configured in config.ini.
import sqlite3
import shutil
import tarfile
import datetime

from flask import Markup

from apscheduler.scheduler import Scheduler
from time import sleep

import config


#Initialize and start the Scheduler
sched = Scheduler(daemon=False)

# Called as a GET/POST request from views to start or stop the daemons.
def startTaskDaemon():
    if sched.get_jobs() == []:
        print "Starting Task daemon..."
        sched.start()
        createJobs()
    else:
        print "Job already running!"
        print sched.get_jobs()

def stopTaskDaemon():
    print "Shutting down Task daemon..."
    sched.shutdown(wait=False, shutdown_threadpool=False)
    sched.unschedule_func(runBackupJobs)
    print sched.print_jobs()

def checkStatus():
    if sched.get_jobs() == []:
        print "Offline"
        status = Markup('Task Scheduler is <font color="#FF0000">Offline</font>')

    else:
        print "Online"
        status = Markup('Task Scheduler is <font color="#339933">Online</font>')
    return status


def createJobs():

    dbpath = config.DATABASE

    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    c.execute('''SELECT * FROM tasks''')
    print c

    for task, dom, dow, hour, minute in c:
        if "all" in dom:
            dom = dom.replace("all", "*")
        if "all" in dow:
            dow = dow.replace("all", "*")
        if "all" in hour:
            hour = hour.replace("all", "*")
        if "all" in minute:
            minute = minute.replace("all", "*")
            
        print task, dom, dow, hour, minute
        sched.add_cron_job(runBackupJobs, day=dom, day_of_week=dow, hour=hour, minute=minute)

    c.close()

# All Cron Jobs go here.

# Backup task to copytree of source to backup destination, 
# tars the directory, then removes the copied directory.
def runBackupJobs():

    print "Running backup..."
    src = config.MINECRAFTDIR + "world"
    dst = config.BACKUPDIR + "world"
    
    print "Copying file to backup source..."
    shutil.copytree(src, dst)
    
    print "File copy completed"
    print "Tarballing files"

    now = datetime.datetime.now()
    filedate = now.strftime("%Y.%m.%d_%H.%M")
    print filedate

    tar = tarfile.open(dst + "_" + filedate + ".tar.gz", "w:gz")

    tar.add(dst, arcname="world")
    tar.close()
    print "File zipped"

    print "Removing copied files..."
    shutil.rmtree(dst)
    print dst +  " directory removed"

    return "Archive Completed"
