import global_vars as gv
import subprocess
import discord
import time

#Functions
async def start_minecraft_server(ctx, bot, channel_id, guild_name, channel_name, directory, game_name):
    gv.server = subprocess.Popen(f"~/{directory}/{guild_name}/{channel_name}/start.sh", stdout=True, text=True, shell=True, stdin=subprocess.PIPE)
    time.sleep(1)
    if(gv.server.poll() == None):
        await bot.change_presence(activity=discord.Game(name=game_name))
        await ctx.send(f"Starting {game_name} server")
        gv.started_in = channel_id
    else:
        await ctx.send(f"{game_name} server starting failed")


def backup_status():
    output = subprocess.run('cd ~/.pcloud/Cache && ls | wc -l',  capture_output=True, shell=True, text=True)
    file_quantity = int(output.stdout)  #Stored quantity of files inside the folder "Cache" of ".pcloud"
    if(file_quantity == 1):
        output2 = subprocess.run('cd ~/.pcloud/Cache && ls',  capture_output=True, shell=True, text=True)
        file_name = output2.stdout.strip()      #Store file name inside the folder "Cache" and remove whitespace at the beginning and the end
        return file_name
    else:
        return file_quantity


async def make_backup(ctx, guild_name, channel_name, directory, game_name):
    if(gv.server.poll() == None):
        await ctx.send("A server is running, can't make a backup")
    else:
        file_quantity = backup_status()
        if(file_quantity == 'cached'):
            # Compressing
            await ctx.send(f"Compressing {game_name} server data… I won't respond to commands until finished")
            subprocess.run(f"cd ~/{directory}/{guild_name} && tar -czvf {channel_name}.tar.gz {channel_name}",  capture_output=True, shell=True, text=True)
            await ctx.send(f"{game_name} server data compressed")

            # Backup in pCloud
            subprocess.Popen(f"mv -f ~/{directory}/{guild_name}/{channel_name}.tar.gz ~/pCloudDrive/{directory}/{guild_name}", stdout=True, text=True, shell=True, stdin=subprocess.PIPE)
            await ctx.send(f"Making a backup of the {game_name} server...")
        else:
            await ctx.send(f"Another backup is running; wait some time to start a backup.\nRemaining files = {file_quantity}")


async def latest_backup_info(ctx, guild_name, channel_name, directory):
    p = subprocess.run(f'date -d "@$(stat -c "%Y" ~/pCloudDrive/{directory}/{guild_name}/{channel_name}.tar.gz)" "+%A, %d %B %Y - %H:%M:%S"', capture_output=True, shell=True, text=True)
    await ctx.send(p.stdout)