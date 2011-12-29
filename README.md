# AdminCraft #

AdminCraft is an open source Administration Web GUI Console for administering a
Linux Minecraft Server. Admincraft is in early, but active development.

AdminCraft provides the following features:

- Start, Stop, Restart the Minecraft server
- Create backups of worlds to a separate location or mounted filesystem
- Web Console to monitor server logs
- Ability to chat with users or send manual commands
- Built-in reference for Block/Item Dec codes
- Configure server properties via Web GUI
- Server Status (Online/Offline/Restarting/Backing Up)
- View User Status (Connected players, Ops, Banned IPs|Players)

Features in progress for 1.0:

- Reworking item/block ID reference
- Configure Ops, Whitelisted, Banned Players|IPs via GUI
- Login sessions, security and support for multiple Admin Users
- Schedule tasks (such as backing up world every X hours/days)
- Support for viewing Log History

Features to add Post 1.0:

- Support to deploy and administer multiple instances of Minecraft Servers
- Support to deploy AdminCraft on a separate server than the Minecraft Server
- More server and Minecraft monitoring features

## Requirements ##

- A Linux OS. AdminCraft has only been tested on Ubuntu 11.04,
but should be compatible with at least 9.04+
- Python 2.6+. Python 3 is not yet supported
- Python dependencies: Flask Framework 0.8
- Enough server power to run a Minecraft Server. Basically at least
a P4 with a minimum of 2GB of RAM. Minecraft likes to eat memory. :)
- Basic Linux knowledge. :)

## Installation (Ubuntu 9.04+) ##

**BEFORE INSTALLING ADMINCRAFT, PLEASE READ NOTES AT THE BOTTOM OF THIS README**

**Note** Upon 1.0 release, I will have an install script as well as a deb
package. For now, you'll have to deal with the manual installation. :D

Assuming you have at least Python 2.6+ installed and the minecraft_server.jar 
downloaded, please follow the steps below: 

1. If not installed already, please install easy_install:

        $ sudo apt-get install python-setuptools

2. Install Flask via easy_install:

        $ sudo easy_install Flask

3. Clone AdminCraft.git:

        $ git clone git://github.com/alf-/AdminCraft.git

4. Open AdminCraft.py and set the minecraftDir variable to point to your 
    Minecraft Server's directory.

5. Copy the Minecraft daemon to /etc/init.d/

        $ sudo cp scripts/minecraft /etc/init.d/

6. Configure USERNAME, WORLD, MCPATH, BACKUPPATH in
    /etc/init.d/minecraft in the text editor of your choice

7. Set required permissions to the Minecraft daemon:

        $ sudo chmod a+x /etc/init.d/minecraft

8. Run update-rc.d to create sym links:

        $ sudo update-rc.d minecraft defaults

9. Now finally, run AdminCraft.py:

        $ python AdminCraft.py

or to run in the background:

        $ python Admincraft.py &

10. Using your preferred web browser, open localhost:5000 (or your server's hostname:5000)

11. Great success! (I hope)


## Notes ##

AdminCraft is in very early, but active development. Therefore, I cannot guarantee this will install, run, or work properly. 

AdminCraft runs under Flask's builtin server with debugging enabled by default. You can turn this off in by changing debugEnabled to "False" in AdminCraft.py Global Config. It is recommended to disable debugging if deploying to an externally accessible server.

There is much cleanup and refactoring that needs to be done. So expect major changes in future maintenance versions. 

There is NO security yet. This is still under development. So be advised, anyone who can access your AdminCraft console can control your Minecraft server.

Support is limited as the project is still under early active development. But if you need help installing, or run into any problems, feel free to contact me at alf.g.jr[at]gmail.com. I can only support Ubuntu 9.04+ installations at this time. 

