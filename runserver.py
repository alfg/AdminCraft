#!/usr/bin/env python

import os.path
import sqlite3

from flask import Flask

import config
import views

app = Flask(__name__)

#Registering view module
app.register_blueprint(views.app)

#Setting session key from config
app.secret_key = config.SECRETKEY

#Create database if it does not exist
dbpath = config.DATABASE

if not os.path.exists(dbpath):
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    c.execute('''create table tasks (type text, month text, day text, hour text, minute text)''')

    conn.commit()
    c.close()


#Start App
if __name__ == "__main__":
    app.run(host=config.SERVERHOST, port=config.SERVERPORT, debug=config.DEBUGMODE, use_reloader=config.AUTORELOADER)


