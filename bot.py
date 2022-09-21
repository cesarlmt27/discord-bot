import discord
from discord.ext import commands
from dotenv import load_dotenv      #type: ignore
import os
import datetime
import subprocess
import time
import asyncio

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or('$'), description='This bot is in beta.', help_command=commands.DefaultHelpCommand(no_category = 'Help'), intents = intents)

me = int(os.environ['ME'])


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
    else:
        raise error

@bot.event
async def on_message(message):
    msg = message.content
    if(msg.startswith("server:") and message.author.id == me):
        msg = msg.replace("server:", "").strip()
        try:
            if(server.poll() == None):
                server.stdin.write(msg + "\n")
                server.stdin.flush()
                if(msg == "stop"):
                    await bot.change_presence(activity=None)
                    await message.channel.send("Server stopped. Remember to make a backup")
                await message.channel.send("Command received")
            else:
                raise NameError
        except NameError:
            await message.channel.send("Server is closed")
    elif(msg.startswith("server:") and message.author.id != me):
        await message.channel.send("You don't have permission to do this")
    await bot.process_commands(message)



#Cog: General
class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Test if bot responds")
    @commands.guild_only()
    async def ping(self, ctx):
        await ctx.send('pong')

    @commands.command(help="Sum two numbers. Separate them with space")
    @commands.guild_only()
    async def sum(self, ctx, num1: int, num2: int):
        await ctx.send(num1 + num2)

    @commands.command(help="Information about the server")
    @commands.guild_only()
    async def info(self, ctx):
        embed = discord.Embed(title=f"{ctx.guild.name}", description="Lorem ipsum dolor sit amet.", timestamp=datetime.datetime.utcnow())
        embed.add_field(name="Server created at", value=f"{ctx.guild.created_at}")
        await ctx.send(embed=embed)

    @commands.command(help="Shutdown server (Diosito)")
    @commands.guild_only()
    async def shutdown(self, ctx):
        try:
            if(server.poll() == None):
                await ctx.send("A server is running, can't shutdown")
            else:
                raise NameError
        except NameError:
            file_quantity = backup_status()
            if(file_quantity == 'cached'):
                await ctx.send("Bye :)")
                subprocess.Popen('sudo shutdown now', stdout=True, text=True, shell=True, stdin=subprocess.PIPE)
            else:
                await ctx.send(f"A backup is running; wait some time to shutdown.\nFile quantity = {file_quantity}")



#Cog: Server
class Server(commands.Cog, name='Minecraft server'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Run Minecraft server")
    @commands.guild_only()
    async def run(self, ctx):
        file_quantity = backup_status()
        channel_id = ctx.message.channel.id   #Store channel/thread ID where the message was sent.
        if(file_quantity == 'cached'):
            try:
                if(server.returncode == None):  #When the server is running, "server.returncode" has a value of "None".
                    await ctx.send("The server is already running, or another server is running")
                else:   #If the server was stopped once, "server.returncode" has a value of "0".
                    raise NameError
            except NameError:   #When trying to start the server for the first time, the code doesn't have a "server" variable defined; this produces the "NameError" exception.
                if(channel_id == int(os.environ['MS_JE_BOT'])):
                    asyncio.create_task(start_minecraft_server(ctx, os.environ['MS_BSS_SERVER_STARTER_PATH'], "Vanilla server started", "Minecraft Java Edition", channel_id))
                elif(channel_id == int(os.environ['MS_DBC_BOT'])):
                    asyncio.create_task(start_minecraft_server(ctx, os.environ['MS_DBC_SERVER_STARTER_PATH'], "DBC server started", "Dragon Block C", channel_id))
                elif(channel_id == int(os.environ['ABI_MSE_BOT'])):
                    asyncio.create_task(start_minecraft_server(ctx, os.environ['ABI_SERVER_STARTER_PATH'], "Vanilla server started", "Minecraft Java Edition", channel_id))
                else:
                    await ctx.send("Use this command in the proper channel/thread")
        else:
            await ctx.send(f"A backup is running, and the server can't start; wait some time to start the server.\nFile quantity = {file_quantity}")

    @commands.command(help="Stop Minecraft server")
    @commands.guild_only()
    async def stop(self, ctx):
        channel_id = ctx.message.channel.id   #Store channel/thread ID where the message was sent.
        try:
            if(server.poll() == None and started_in == channel_id):
                server.communicate(input='stop', timeout=20)
                await bot.change_presence(activity=None)
                await ctx.send("Server stopped. Remember to make a backup")
            else:
                raise NameError
        except NameError:
            await ctx.send("This server isn't running")

    @commands.command(help="Check if a server is running or closed and if there is a backup running")
    @commands.guild_only()
    async def status(self, ctx):
        try:
            if(server.poll() == None):
                await ctx.send("A Minecraft server is running")
            else:
                raise NameError
        except NameError:
            file_quantity = backup_status()
            if(file_quantity == 'cached'):
                await ctx.send("Server is closed, and there isn't a backup running")
            else:
                await ctx.send(f"Server is closed, and there is a backup running.\nFile quantity = {file_quantity}")

    @commands.command(help="Make a backup of Minecraft server data")
    @commands.guild_only()
    async def backup(self, ctx):
        channel_id = ctx.message.channel.id   #Store channel/thread ID where the message was sent.
        if(channel_id == int(os.environ['MS_JE_BOT'])):
            asyncio.create_task(make_backup(ctx, './backup_ms_bss_server.sh', "Making a backup of the Vanilla server..."))
        elif(channel_id == int(os.environ['MS_DBC_BOT'])):
            asyncio.create_task(make_backup(ctx, './backup_ms_dbc_server.sh', "Making a backup of the DBC server..."))
        elif(channel_id == int(os.environ['ABI_MSE_BOT'])):
            asyncio.create_task(make_backup(ctx, './backup_abi_server.sh', "Making a backup of the server..."))
        else:
            await ctx.send("Use this command in the proper channel/thread")



#Functions
async def make_backup(ctx, backup_file, backup_msg):
    try:
        if(server.poll() == None):
            await ctx.send("A server is running, can't make a backup")
        else:
            raise NameError
    except NameError:
        file_quantity = backup_status()
        if(file_quantity == 'cached'):
            subprocess.Popen(backup_file, stdout=True, text=True, shell=True, stdin=subprocess.PIPE)
            await ctx.send(backup_msg)
        else:
            await ctx.send(f"Another backup is running; wait some time to start a backup.\nFile quantity = {file_quantity}")


def backup_status():
    output = subprocess.run('cd ~/.pcloud/Cache && ls | wc -l',  capture_output=True, shell=True, text=True)
    file_quantity = int(output.stdout)  #Stored quantity of files inside the folder "Cache" of ".pcloud"
    if(file_quantity == 1):
        output2 = subprocess.run('cd ~/.pcloud/Cache && ls',  capture_output=True, shell=True, text=True)
        file_name = output2.stdout.strip()      #Store file name inside the folder "Cache" and remove whitespace at the beginning and the end
        return file_name
    else:
        return file_quantity


async def start_minecraft_server(ctx, starter, start_msg, presence, channel_id):
    global server
    server = subprocess.Popen(starter, stdout=True, text=True, shell=True, stdin=subprocess.PIPE)
    time.sleep(1)
    if(server.poll() == None):
        await bot.change_presence(activity=discord.Game(name=presence))
        await ctx.send(start_msg)
        global started_in
        started_in = channel_id
    else:
        await ctx.send("Server starting failed")


async def main():
    async with bot:
        await bot.add_cog(General(bot))
        await bot.add_cog(Server(bot))
        await bot.start(os.environ['TOKEN'])

asyncio.run(main())