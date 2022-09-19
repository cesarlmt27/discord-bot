# Discord bot
## Purpose
The main purpose of this bot was open and close dedicated Minecraft servers; however, was also implemented a Minecraft server backup and a few Minecraft servers' not-related basics features.

## How does it work?
This Discord bot is written with the Discord.py package and implements Python's subprocess module to run Bash scripts that contain the commands to execute the wanted task. Besides, Python's Dotenv package is used to store data like Minecraft servers starter files path; Discord token, guilds, and channels IDs; my Discord ID, and the Discord's bot presence text. Maybe this isn't the best way to store this specific data, but is the only easy way that I know to store data in another file and use it in the code; however, if this isn't the most efficient way, I would appreciate other ideas to make it (I don't know too much about environment variables).
