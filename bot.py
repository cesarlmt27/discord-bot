import global_vars as gv
import functions as f
import discord
from discord.ext import commands
from constant_values import *   #File to store bot token and my user id.
import subprocess
import asyncio
import sqlite3

con = sqlite3.connect("database.db")
cur = con.cursor()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or('$'), description='Gaming server manager', help_command=commands.DefaultHelpCommand(no_category = 'Help'), intents = intents)


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
        print(f"{error}")
    elif isinstance(error, commands.NotOwner):
        await ctx.send("You don't have permission to do this")
        print(f"{error}")
    elif(str(error) == str("Command raised an exception: AttributeError: 'TextChannel' object has no attribute 'parent'")):
        await ctx.send("Use this command in the proper channel/thread")
        print(f"{error}")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(error)
    elif(str(error) == str("Command raised an exception: TypeError: 'NoneType' object is not subscriptable")):
        await ctx.send("Invalid given channel")
        print(f"{error}")
    else:
        print(f"{error}")



#Cog: General
class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.streaming = False


    @commands.command(help="Test if bot responds.")
    @commands.guild_only()
    async def ping(self, ctx):
        await ctx.send('pong')


    @commands.command(help="Shutdown, reboot/restart or boot to Windows.")
    @commands.guild_only()
    async def power(self, ctx, state):
        if(gv.server.poll() == None):
            await ctx.send("A server is running, can't shutdown/reboot")
            return

        file_quantity = f.backup_status()
        if(file_quantity != 'cached'):
            await ctx.send(f"A backup is running; wait some time to shutdown or reboot/restart.\nRemaining files = {file_quantity}")
            return
        
        if(gv.started_by is not None and (ctx.message.author.id != gv.started_by and ctx.message.author.id != me)):
            await ctx.send("Another user started the streaming. You aren't allowed to use this command right now")
            return

        if(state == "shutdown"  or state == "off"):
            await ctx.send("Hibernating...")
            subprocess.Popen('sudo systemctl hibernate', stdout=True, text=True, shell=True, stdin=subprocess.PIPE)
        elif(state == "reboot" or state == "restart"):
            await ctx.send("Rebooting...")
            con.close()
            subprocess.Popen('sudo reboot', stdout=True, text=True, shell=True, stdin=subprocess.PIPE)
        elif(state == "windows"):
            await ctx.send("Rebooting to Windows...")
            con.close()
            subprocess.Popen('sudo grub-reboot 2 && sudo reboot', stdout=True, text=True, shell=True, stdin=subprocess.PIPE)
        else:
            await ctx.send("Invalid power state")


    @commands.command(help="Start/stop streaming app.")
    @commands.guild_only()
    async def stream(self, ctx):
        cur.execute("SELECT game_id FROM Channel WHERE Channel.id = ?", (gv.started_in,))
        game_id = cur.fetchone()

        if(game_id is not None and game_id[0] != 1):
            await ctx.send("You aren't allowed to use this command right now")
            return

        if(self.streaming == False):
            subprocess.Popen('sudo systemctl start gdm3', stdout=True, text=True, shell=True, stdin=subprocess.PIPE)
            self.streaming = True
            gv.started_by = ctx.message.author.id
            await ctx.send('Starting streaming')
        else:
            if(ctx.message.author.id != gv.started_by and ctx.message.author.id != me):
                await ctx.send("Another user started the streaming. You aren't allowed to use this command right now")
                return

            subprocess.run('sudo systemctl stop gdm3',  capture_output=True, shell=True, text=True)
            self.streaming = False
            gv.started_by = None
            await ctx.send("Stopping streaming")



#Cog: Admin
class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(help="Send command to running server.")
    @commands.is_owner()
    async def server(self, ctx, msg):
        if(gv.server.poll() == None):
            gv.server.stdin.write(msg + "\n")
            gv.server.stdin.flush()
            if(msg == "stop" or msg == "quit"):
                await bot.change_presence(activity=None)
                await ctx.send("Server stopped. Remember to make a backup")
            await ctx.send("Command received")
        else:
            await ctx.send("Server is closed")


    @commands.command(help="Set up a minecraft server.")
    @commands.is_owner()
    async def setup_minecraft(self, ctx, target_channel, url=None):
        if(url is None):
            await ctx.send("Arguments were not given correctly")
            await ctx.send("Arguments: `target_channel, url`")
            return

        guild_id = ctx.guild.id
        guild_name = ctx.guild.name.replace(" ","_")
        channel_id = int(target_channel[2:-1])
        channel_name = bot.get_channel(channel_id)

        cur.execute("SELECT id FROM Channel WHERE id = ?", (channel_id,))
        res = cur.fetchone()

        if(res is None):
            subprocess.run(f"./shell-scripts/create_minecraft_server.sh {guild_name} {channel_name} {url}",  stdout=subprocess.PIPE, shell=True, text=True)

            params = (channel_id, guild_id, 1)
            
            cur.execute("INSERT INTO Channel VALUES (?, ?, ?)", params)
            con.commit()

            await ctx.send("Minecraft server created")
        else:
            await ctx.send("This channel already has a Minecraft server; therefore, it will be updated")
            p = subprocess.run(f"cd ~/games-servers/minecraft-java/{guild_name}/{channel_name} && rm server.jar && wget {url}",  stdout=subprocess.PIPE, shell=True, text=True)

            if(p.returncode == 0):
                await ctx.send("Minecraft server updated")
            else:
                await ctx.send("Minecraft server couldn't be updated: this is a Forge server, or another error occurred")


    @commands.command(help="Delete a minecraft server.")
    @commands.is_owner()
    async def delete_minecraft(self, ctx, target_channel):
        guild_name = ctx.guild.name.replace(" ","_")
        channel_id = int(target_channel[2:-1])
        channel_name = bot.get_channel(channel_id)

        cur.execute("SELECT id FROM Channel WHERE id = ?", (channel_id,))
        res = cur.fetchone()

        if(res is None):
            await ctx.send("This channel doesn't have a Minecraft server")
            return

        subprocess.run(f"cd ~/games-servers/minecraft-java/{guild_name} && rm -r {channel_name}",  stdout=subprocess.PIPE, shell=True, text=True)

        cur.execute("DELETE FROM Channel WHERE id = ?", (channel_id,))
        con.commit()

        await ctx.send("Minecraft server deleted")



#Cog: Server
class Server(commands.Cog, name='Games servers'):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(help="Run server.")
    @commands.guild_only()
    async def run(self, ctx, target_channel):
        if(gv.server.poll() == None):  #When the server is running, "server.poll()" has a value of "None".
            await ctx.send("The server is already running, or the given channel is invalid")
            return

        file_quantity = f.backup_status()
        if(file_quantity != 'cached'):
            await ctx.send(f"A backup is running, and the server can't start; wait some time to start the server.\nRemaining files = {file_quantity}")
            return

        channel_id = int(target_channel[2:-1])
        guild_name = ctx.guild.name.replace(" ","_")
        channel_name = bot.get_channel(channel_id)

        cur.execute("""SELECT directory, name FROM Game
                    JOIN Channel ON Game.id = Channel.game_id WHERE Channel.id = ?""", (channel_id,))
        res = cur.fetchone()

        directory = res[0]
        game_name = res[1]

        asyncio.create_task(f.start_minecraft_server(ctx, self.bot, channel_id, guild_name, channel_name, directory, game_name))


    @commands.command(help="Stop server.")
    @commands.guild_only()
    async def stop(self, ctx, target_channel):
        channel_id = int(target_channel[2:-1])

        if(gv.server.poll() != None or gv.started_in != channel_id):
            await ctx.send("This server isn't running, or the given channel is invalid")
            return
        
        cur.execute("SELECT game_id FROM Channel WHERE Channel.id = ?", (channel_id,))
        game_id = cur.fetchone()

        if(game_id[0] == 1):
            gv.server.communicate(input='stop')
        elif(game_id[0] == 2):
            gv.server.communicate(input='quit')

        await ctx.send("Server stopped. Remember to make a backup")
        gv.started_in = None
        await bot.change_presence(activity=None)


    @commands.command(help="Check if a server and a backup are running.")
    @commands.guild_only()
    async def status(self, ctx):
        if(gv.server.poll() == None):
            await ctx.send("A server is running")
            return

        file_quantity = f.backup_status()
        if(file_quantity == 'cached'):
            await ctx.send("Server is closed, and there isn't a backup running")
        else:
            await ctx.send(f"Server is closed, and there is a backup running.\nRemaining files = {file_quantity}")


    @commands.command(help="Make a backup of a server data.")
    @commands.guild_only()
    async def backup(self, ctx, target_channel):
        channel_id = int(target_channel[2:-1])
        guild_name = ctx.guild.name.replace(" ","_")
        channel_name = bot.get_channel(channel_id)
        
        cur.execute("""SELECT directory, name FROM Game
                    JOIN Channel ON Game.id = Channel.game_id WHERE Channel.id = ?""", (channel_id,))
        res = cur.fetchone()

        directory = res[0]
        game_name = res[1]

        asyncio.create_task(f.make_backup(ctx, guild_name, channel_name, directory, game_name))


    @commands.command(help="Date and time of latest backup.")
    @commands.guild_only()
    async def latestb(self, ctx, target_channel):
        channel_id = int(target_channel[2:-1])
        guild_name = ctx.guild.name.replace(" ","_")
        channel_name = bot.get_channel(channel_id)

        cur.execute("""SELECT directory FROM Game
                    JOIN Channel ON Game.id = Channel.game_id WHERE Channel.id = ?""", (channel_id,))
        res = cur.fetchone()

        directory = res[0]

        asyncio.create_task(f.latest_backup_info(ctx, guild_name, channel_name, directory))



async def main():
    async with bot:
        await bot.add_cog(General(bot))
        await bot.add_cog(Admin(bot))
        await bot.add_cog(Server(bot))
        await bot.start(token)

asyncio.run(main())