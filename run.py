#!/usr/bin/env python
from admincraft.runserver import runServer

#Start App
if __name__ == "__main__":
    try:
        runServer()
    except:
        "Something went wrong"
