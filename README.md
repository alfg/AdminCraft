# AdminCraft #

AdminCraft is an open source Administration Web GUI Console for administering a
Linux Minecraft Server. Admincraft is still in early development.

AdminCraft provides the following features:

- Start, stop and restart a Minecraft server
- Create backups of worlds to a separate location or a mounted filesystem
- Web Console to monitor server logs
- Username/Password protected
- Ability to chat with users or send custom commands
- Built-in reference for Block/Item Dec codes
- Configure server properties via Web GUI
- Server Status (Online/Offline/Restarting/Backing Up)
- View and configure user status (Connected players, Ops, Banned IPs or Players)
- Ability to schedule 'cron-like' backup jobs on set intervals

TODO:

- Reworking item/block ID reference
- Login sessions, security and support for multiple Admin Users
- Support for viewing Log History
- Support to deploy and administer multiple instances of Minecraft Servers
- Support to deploy AdminCraft on a separate server than the Minecraft Server
- More server and Minecraft monitoring features

## Requirements ##

- Minecraft Server 1.6.2+
- A Linux OS. AdminCraft has only been tested on Ubuntu 11.04,
but should be compatible with at least Ubuntu 9.04+
- Python 2.6+. Python 3 is not yet supported
- Python dependencies: Flask Framework 0.8
- Enough server power to run a Minecraft Server. Basically at least
a P4 with a minimum of 2GB of RAM. Minecraft likes to eat memory. :)
- Basic Linux knowledge. :)

## Installation (Ubuntu 9.04+) ##

Assuming you have at least Python 2.6+ installed and the minecraft_server.jar 
downloaded, please follow the steps below: 

1. If not installed already, please install sqlite3 and python-setuptools:

        $ sudo apt-get install sqlite3 python-setuptools

2. Clone AdminCraft.git:

        $ git clone git://github.com/alfg/AdminCraft.git

3. Run setup.py to install dependencies:

        $ python setup.py install

4. Open config.ini and set the required variables.

5. Copy the Minecraft daemon to /etc/init.d/

        $ sudo cp scripts/minecraft /etc/init.d/

6. Configure USERNAME, WORLD, MCPATH, BACKUPPATH in
    /etc/init.d/minecraft in the text editor of your choice

        $ sudo vim /etc/init.d/minecraft

7. Set required permissions to the Minecraft daemon:

        $ sudo chmod a+x /etc/init.d/minecraft

8. Run update-rc.d to create sym links:

        $ sudo update-rc.d minecraft defaults

9. Now finally, run run.py:

        $ python run.py

    Or to run in the background:

        $ nohup python run.py &

    If you wish to view the nohup output:

        $ tail -f nohup.out

10. Using your preferred web browser, open 0.0.0.0:5000 (or your server's hostname:5000)

11. Great success! (I hope)


## Notes ##

AdminCraft is in very early development. Therefore, I cannot guarantee this will install, run, or work properly. 

AdminCraft runs under Flask's built-in server with debugging and auto-reloading disabled by default. You can turn this on by changing DEBUGMODE and AUTORELOADER to "True" in config.ini. It is recommended to disable debugging if deploying to an externally accessible server.

There is much cleanup and refactoring that needs to be done. So expect major changes in future versions. 

Support is limited as the project is still in early development. But if you need help installing, or run into any problems, feel free to contact me at alf.g.jr[at]gmail.com. I can only support Ubuntu 9.04+ installations at this time.
