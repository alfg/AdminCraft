#!/usr/bin/env python

from flask import Flask

import config
import views

app = Flask(__name__)

#Registering view module
app.register_blueprint(views.app)

#setting session key from config
app.secret_key = config.SECRETKEY

if __name__ == "__main__":
    app.run(host=config.SERVERHOST, port=config.SERVERPORT, debug=config.DEBUGMODE, use_reloader=config.AUTORELOADER)


