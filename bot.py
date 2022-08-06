import discord
from discord.ext import commands
from dotenv import load_dotenv      #type: ignore
import os
import datetime
import subprocess
import time

load_dotenv()

bot = commands.Bot(command_prefix='$', description='This bot is in beta.', help_command=commands.DefaultHelpCommand(no_category = 'Help'))

guilds = [os.environ['TESTING_GUILD'], os.environ['ABI_GUILD']]

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


class Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Run Minecraft server")
    @commands.guild_only()
    async def run(self, ctx):
        id = ctx.message.guild.id       #Store guild ID where the message was sent.
        if(id == int(guilds[1])):
            file_quantity = backup_status()
            if(file_quantity == 'cached'):
                global server
                try:
                    if(server.returncode == None):  #When the server is running, "server.returncode" has a value of "None".
                        await ctx.send("Server is already running")
                    else:   #If the server was stopped once, "server.returncode" has a value of "0".
                        raise NameError
                except NameError:   #When trying to start the server for the first time, the code doesn't have a "server" variable defined; this produces the "NameError" exception.
                    server = subprocess.Popen('./start-minecraft-server.sh', stdout=True, text=True, shell=True, stdin=subprocess.PIPE)
                    time.sleep(1)
                    if(server.poll() == None):
                        await bot.change_presence(activity=discord.Game(name="Minecraft BE"))
                        await ctx.send("Server started")
                    else:
                        await ctx.send("Server starting failed")
            else:
                await ctx.send(f"A backup is running, and the server can't start; wait some time to start the server.\nFile quantity = {file_quantity}")
        else:
            await ctx.send("This isn't allowed yet")

    @commands.command(help="Stop Minecraft server")
    @commands.guild_only()
    async def stop(self, ctx):
        try:
            if(server.poll() == None):
                server.communicate(input='stop', timeout=20)
                await bot.change_presence(activity=None)
                await ctx.send("Server stopped. Remember to make a backup")
            else:
                raise NameError
        except NameError:
            await ctx.send("Server isn't running")

    @commands.command(help="Check if the server is running or closed")
    @commands.guild_only()
    async def status(self, ctx):
        try:
            if(server.poll() == None):
                await ctx.send("Server is running")
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
        try:
            if(server.poll() == None):
                await ctx.send("Server is running, can't make a backup")
            else:
                raise NameError
        except NameError:
            file_quantity = backup_status()
            if(file_quantity == 'cached'):
                subprocess.Popen('./backup_server.sh', stdout=True, text=True, shell=True, stdin=subprocess.PIPE)
                await ctx.send("Making backup...")
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


bot.add_cog(General(bot))
bot.add_cog(Server(bot))
bot.run(os.environ['TOKEN'])