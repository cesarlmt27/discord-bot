import global_vars as gv
import functions as f
import discord
from discord.ext import commands
from constant_values import *   #File to store guilds IDs, channels/threads IDs, my ID, and other data.
import subprocess
import asyncio
import sqlite3

con = sqlite3.connect("database.db")
cur = con.cursor()

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
            await ctx.send("A server is running, can't shutdown/reboot")
        else:
            file_quantity = f.backup_status()
            if(file_quantity == 'cached'):
                if(state == "shutdown"):
                    await ctx.send("Shutting down...")
                    con.close()
                    subprocess.Popen('sudo shutdown now', stdout=True, text=True, shell=True, stdin=subprocess.PIPE)
                elif(state == "reboot" or state == "restart"):
                    await ctx.send("Rebooting...")
                    con.close()
                    subprocess.Popen('sudo reboot', stdout=True, text=True, shell=True, stdin=subprocess.PIPE)
                else:
                    await ctx.send("Invalid power state")
            else:
                await ctx.send(f"A backup is running; wait some time to shutdown or reboot/restart.\nRemaining files = {file_quantity}")


    @commands.command(help="Start/stop streaming app.")
    @commands.guild_only()
    async def stream(self, ctx):
        if(self.streaming == False):
            subprocess.Popen('sudo systemctl start gdm3', stdout=True, text=True, shell=True, stdin=subprocess.PIPE)
            self.streaming = True
            await ctx.send('Starting streaming')
        else:
            subprocess.run('sudo systemctl stop gdm3',  capture_output=True, shell=True, text=True)
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


    @commands.command(help="Create a minecraft server.")
    @commands.is_owner()
    async def create_minecraft(self, ctx, modded, url=None):
        guild_name = ctx.guild.name.replace(" ","_")
        guild_id = ctx.guild.id
        channel_name = ctx.message.channel.parent.name
        channel_id = ctx.message.channel.id

        cur.execute("SELECT id FROM channel WHERE id = ?", (channel_id,))
        res = cur.fetchone()

        if(res is None):
            if(modded == "forge" and url is None):
                await ctx.send("You must type a Forge URL as an argument")
            elif(modded == "vanilla" or modded == "forge"):
                subprocess.run(f"./shell-scripts/create_minecraft_{modded}_server.sh {guild_name} {channel_name} {url}",  stdout=subprocess.PIPE, shell=True, text=True)

                params = (channel_id, guild_id, guild_name, f"~/games-servers/minecraft-java/{guild_name}/{channel_name}/start.sh", f"Starting {modded} server",
                "Minecraft Java Edition", f"~/games-servers/minecraft-java/{guild_name}/{channel_name}/backup.sh", f"Making a backup of the {modded} server...",
                f"~/games-servers/minecraft-java/{guild_name}/{channel_name}/latest_backup.sh")
                
                cur.execute("INSERT INTO channel VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", params)
                con.commit()

                if(modded == "vanilla"):
                    await ctx.send("Vanilla server at the latest version created")
                else:
                    await ctx.send("Forge server created")
            else:
                await ctx.send("You have mistyped the command")
        else:
            await ctx.send("This channel already has a Minecraft server")


    @commands.command(help="Delete a minecraft server.")
    @commands.is_owner()
    async def delete_minecraft(self, ctx):
        guild_name = ctx.guild.name.replace(" ","_")
        channel_name = ctx.message.channel.parent.name
        channel_id = ctx.message.channel.id

        cur.execute("SELECT id FROM channel WHERE id = ?", (channel_id,))
        res = cur.fetchone()

        if(res is not None):
            subprocess.run(f"cd ~/games-servers/minecraft-java/{guild_name} && rm -r {channel_name}",  stdout=subprocess.PIPE, shell=True, text=True)

            cur.execute("DELETE FROM channel WHERE id = ?", (channel_id,))
            con.commit()

            await ctx.send("Minecraft server deleted")
        else:
            await ctx.send("This channel doesn't have a Minecraft server")



#Cog: Server
class Server(commands.Cog, name='Minecraft server'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Run Minecraft server.")
    @commands.guild_only()
    async def run(self, ctx):
        file_quantity = f.backup_status()
        channel_id = ctx.message.channel.id   #Store channel/thread ID where the message was sent.

        if(file_quantity == 'cached'):
                if(gv.server.poll() == None):  #When the server is running, "server.poll()" has a value of "None".
                    await ctx.send("The server is already running, or another server is running")
                else:
                    cur.execute("SELECT server_starter_path, start_message, bot_presence FROM channel WHERE id = ?", (channel_id,))
                    res = cur.fetchone()

                    if(res is not None):
                        asyncio.create_task(f.start_minecraft_server(ctx, self.bot, res[0], res[1], res[2], channel_id))
                    else:
                        await ctx.send("Use this command in the proper channel/thread")
        else:
            await ctx.send(f"A backup is running, and the server can't start; wait some time to start the server.\nRemaining files = {file_quantity}")


    @commands.command(help="Stop Minecraft server.")
    @commands.guild_only()
    async def stop(self, ctx):
        channel_id = ctx.message.channel.id   #Store channel/thread ID where the message was sent.
        if(gv.server.poll() == None and gv.started_in == channel_id):
            gv.server.communicate(input='stop')
            await ctx.send("Server stopped. Remember to make a backup")
            await bot.change_presence(activity=None)
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
        
        cur.execute("SELECT backup_file_path, backup_message FROM channel WHERE id = ?", (channel_id,))
        res = cur.fetchone()

        if(res is not None):
            asyncio.create_task(f.make_backup(ctx, res[0], res[1]))
        else:
            await ctx.send("Use this command in the proper channel/thread")


    @commands.command(help="Date and time of latest backup.")
    @commands.guild_only()
    async def latestb(self, ctx):
        channel_id = ctx.message.channel.id   #Store channel/thread ID where the message was sent.

        cur.execute("SELECT lat_backup_msg_path FROM channel WHERE id = ?", (channel_id,))
        res = cur.fetchone()
        
        if(res is not None):
            asyncio.create_task(f.latest_backup_info(ctx, res[0]))
        else:
            await ctx.send("Use this command in the proper channel/thread")



async def main():
    async with bot:
        await bot.add_cog(General(bot))
        await bot.add_cog(Admin(bot))
        await bot.add_cog(Server(bot))
        await bot.start(token)

asyncio.run(main())