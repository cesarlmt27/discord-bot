import global_vars as gv
import functions as f
import discord
from discord.ext import commands
from constant_values import *   #File to store guilds IDs, channels/threads IDs, my ID, and other data.
import subprocess
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or('$'), description='Bot for Minecraft servers.', help_command=commands.DefaultHelpCommand(no_category = 'Help'), intents = intents)


#Events
@bot.event
async def on_ready():
    print('Bot is ready')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("That command doesn't exist")
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send("Don't send private messages")
        raise error
    elif isinstance(error, commands.NotOwner):
        await ctx.send("You don't have permission to do this")
        raise error
    else:
        raise error



#Cog: General
class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.streaming = False

    @commands.command(help="Test if bot responds.")
    @commands.guild_only()
    async def ping(self, ctx):
        await ctx.send('pong')

    @commands.command(help="Shutdown or reboot/restart bot.")
    @commands.guild_only()
    async def power(self, ctx, state):
        if(gv.server.poll() == None):
            await ctx.send("A server is running, can't shutdown")
        else:
            file_quantity = f.backup_status()
            if(file_quantity == 'cached'):
                if(state == "shutdown"):
                    await ctx.send("Shutting down...")
                    subprocess.Popen('sudo shutdown now', stdout=True, text=True, shell=True, stdin=subprocess.PIPE)
                elif(state == "reboot" or state == "restart"):
                    await ctx.send("Rebooting...")
                    subprocess.Popen('sudo reboot', stdout=True, text=True, shell=True, stdin=subprocess.PIPE)
                else:
                    await ctx.send("Invalid power state")
            else:
                await ctx.send(f"A backup is running; wait some time to shutdown or reboot/restart.\nRemaining files = {file_quantity}")
            

    @commands.command(help="Start/stop streaming app.")
    @commands.guild_only()
    async def stream(self, ctx):
        if(self.streaming == False):
            subprocess.Popen('startx', stdout=True, text=True, shell=True, stdin=subprocess.PIPE)
            self.streaming = True
            await ctx.send('Starting streaming')
        else:
            subprocess.run('killall xinit',  capture_output=True, shell=True, text=True)
            self.streaming = False
            await ctx.send("Stopping streaming")



#Cog: Admin
class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Send command to running Minecraft server.")
    @commands.is_owner()
    async def server(self, ctx, msg):
        if(gv.server.poll() == None):
            gv.server.stdin.write(msg + "\n")
            gv.server.stdin.flush()
            if(msg == "stop"):
                await bot.change_presence(activity=None)
                await ctx.send("Server stopped. Remember to make a backup")
            await ctx.send("Command received")
        else:
            await ctx.send("Server is closed")
            



#Cog: Server
class Server(commands.Cog, name='Minecraft server'):
    def __init__(self, bot):
        self.bot = bot
        self.servers_param = {
            ms_je_bot : [ms_bss_sp, "Starting vanilla server", "Minecraft Java Edition", "./shell-scripts/make-backup/backup_ms_bss_server.sh", "Making a backup of the vanilla server...", "./shell-scripts/latest-backup-info/ms_bss_server.sh"],
            ms_dbc_bot : [ms_dbc_sp, "Starting DBC server", "Dragon Block C", "./shell-scripts/make-backup/backup_ms_dbc_server.sh", "Making a backup of the DBC server...", "./shell-scripts/latest-backup-info/ms_dbc_server.sh"],
            abi_mse_bot : [abi_sp, "Starting vanilla server", "Minecraft Java Edition", "./shell-scripts/make-backup/backup_abi_server.sh", "Making a backup of the server...", "./shell-scripts/latest-backup-info/abi_server.sh"],
            testing_bot : [testing_sp, "Starting vanilla server", "Minecraft testing server", "./shell-scripts/make-backup/backup_testing_server.sh", "Making a backup of the server...", "./shell-scripts/latest-backup-info/testing_server.sh"]
        }

    @commands.command(help="Run Minecraft server.")
    @commands.guild_only()
    async def run(self, ctx):
        file_quantity = f.backup_status()
        channel_id = ctx.message.channel.id   #Store channel/thread ID where the message was sent.
        if(file_quantity == 'cached'):
                if(gv.server.returncode == None):  #When the server is running, "server.returncode" has a value of "None".
                    await ctx.send("The server is already running, or another server is running")
                else:   #If the server was stopped once, "server.returncode" has a value of "0".
                    if channel_id in self.servers_param:
                        param_list = self.servers_param[channel_id]
                        asyncio.create_task(f.start_minecraft_server(ctx, self.bot, param_list[0], param_list[1], param_list[2], channel_id))
                    else:
                        await ctx.send("Use this command in the proper channel/thread")
        else:
            await ctx.send(f"A backup is running, and the server can't start; wait some time to start the server.\nRemaining files = {file_quantity}")

    @commands.command(help="Stop Minecraft server.")
    @commands.guild_only()
    async def stop(self, ctx):
        channel_id = ctx.message.channel.id   #Store channel/thread ID where the message was sent.
        if(gv.server.poll() == None and gv.started_in == channel_id):
            gv.server.communicate(input='stop', timeout=20)
            await bot.change_presence(activity=None)
            await ctx.send("Server stopped. Remember to make a backup")
        else:
            await ctx.send("This server isn't running, or you didn't use the command in a proper channel/thread")
            

    @commands.command(help="Check if a server and a backup are running.")
    @commands.guild_only()
    async def status(self, ctx):
        if(gv.server.poll() == None):
            await ctx.send("A Minecraft server is running")
        else:
            file_quantity = f.backup_status()
            if(file_quantity == 'cached'):
                await ctx.send("Server is closed, and there isn't a backup running")
            else:
                await ctx.send(f"Server is closed, and there is a backup running.\nRemaining files = {file_quantity}")
            

    @commands.command(help="Make a backup of a Minecraft server.")
    @commands.guild_only()
    async def backup(self, ctx):
        channel_id = ctx.message.channel.id   #Store channel/thread ID where the message was sent.
        if channel_id in self.servers_param:
            param_list = self.servers_param[channel_id]
            asyncio.create_task(f.make_backup(ctx, param_list[3], param_list[4]))
        else:
            await ctx.send("Use this command in the proper channel/thread")

    @commands.command(help="Date and time of latest backup.")
    @commands.guild_only()
    async def latestb(self, ctx):
        channel_id = ctx.message.channel.id   #Store channel/thread ID where the message was sent.
        if channel_id in self.servers_param:
            param_list = self.servers_param[channel_id]
            asyncio.create_task(f.latest_backup_info(ctx, param_list[5]))
        else:
            await ctx.send("Use this command in the proper channel/thread")



async def main():
    async with bot:
        await bot.add_cog(General(bot))
        await bot.add_cog(Admin(bot))
        await bot.add_cog(Server(bot))
        await bot.start(token)

asyncio.run(main())