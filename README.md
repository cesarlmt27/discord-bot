# Discord bot for Minecraft servers' control
> Python implementation of a Discord bot to control your Minecraft servers using the subprocess module to execute bash commands on a Linux PC (only tested on Ubuntu Server).


## Table of Contents
* [Background](#background)
* [How does it work?](#how-does-it-work)
* [Most notable features](#most-notable-features)


## Background
When some friends and I want to play Minecraft, I create a dedicated server. I am the one who manages all the server-related things: configuring, starting, stopping, etc. Also, I have wanted to create a Discord bot for a while, but I wasn't sure what the bot should be able to do. These two things were my incentive to make this bot.


## How does it work?
This Discord bot is written with the Discord.py package and implements Python's subprocess module to run bash scripts that contain the commands to execute the desired task. Also, all data, like Minecraft server starter files path, Discord token, guilds IDs, channels/threads IDs, and my Discord ID, are stored in a python file not included in the repository (these are personal information).


## Most notable features
### Minecraft server related features
- Start and stop a Minecraft server.
- Backup of all Minecraft server files with pCloud.
- Check if a Minecraft server is running.
- Check if there is a pCloud backup running.
- Send commands to the running Minecraft server.
- Check the date and time of the latest backup.


### Various
- Message if a command does not exist.
- Comment about private messages.
- Only allow Discord guilds messages.
- Shutdown of the PC (since the purpose of the code is to use it on my PC with Ubuntu Server).
- Avoidance of running a Minecraft server when another one is running.
- pCloud console client backup check by the number of cached files.
- Avoidance of running a Minecraft server when a pCloud backup is running.
- Avoidance of running a Minecraft server backup when a pCloud backup is running.
- Check the proper channel/thread use of a Discord bot command.
