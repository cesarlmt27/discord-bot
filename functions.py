import global_vars as gv
import subprocess
import discord
import time

#Functions
async def start_minecraft_server(ctx, bot, starter, start_msg, presence, channel_id):
    gv.server = subprocess.Popen(starter, stdout=True, text=True, shell=True, stdin=subprocess.PIPE)
    time.sleep(1)
    if(gv.server.poll() == None):
        await bot.change_presence(activity=discord.Game(name=presence))
        await ctx.send(start_msg)
        gv.started_in = channel_id
    else:
        await ctx.send("Server starting failed")


def backup_status():
    output = subprocess.run('cd ~/.pcloud/Cache && ls | wc -l',  capture_output=True, shell=True, text=True)
    file_quantity = int(output.stdout)  #Stored quantity of files inside the folder "Cache" of ".pcloud"
    if(file_quantity == 1):
        output2 = subprocess.run('cd ~/.pcloud/Cache && ls',  capture_output=True, shell=True, text=True)
        file_name = output2.stdout.strip()      #Store file name inside the folder "Cache" and remove whitespace at the beginning and the end
        return file_name
    else:
        return file_quantity


async def make_backup(ctx, backup_file, backup_msg):
    try:
        if(gv.server.poll() == None):
            await ctx.send("A server is running, can't make a backup")
        else:
            raise NameError
    except NameError:
        file_quantity = backup_status()
        if(file_quantity == 'cached'):
            subprocess.Popen(backup_file, stdout=True, text=True, shell=True, stdin=subprocess.PIPE)
            await ctx.send(backup_msg)
        else:
            await ctx.send(f"Another backup is running; wait some time to start a backup.\nRemaining files = {file_quantity}")


async def latest_backup_info(ctx, shell_script):
    p = subprocess.run(shell_script, capture_output=True, shell=True, text=True)
    await ctx.send(p.stdout)