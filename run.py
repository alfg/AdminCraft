#!/usr/bin/env python

import os.path
import sqlite3
import sys
import os

from flask import Flask

from admincraft import config
from admincraft import views

app = Flask(__name__)
currentpath = os.path.split(sys.argv[0])[0]

#Registering view module
app.register_blueprint(views.admincraft)
print app.url_map

#Setting session key from config
app.secret_key = config.SECRETKEY

#Create database if it does not exist
dbpath = currentpath + "/" + config.DATABASE

if not os.path.exists(dbpath):
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    c.execute('''create table tasks (type text, month text, day text, hour text, minute text)''')
    conn.commit()
    c.close()

if __name__ == "__main__":
    path = os.path.split(sys.argv[0])[0]
    #Start App
    app.run(host=config.SERVERHOST, port=config.SERVERPORT, debug=config.DEBUGMODE, use_reloader=config.AUTORELOADER)
