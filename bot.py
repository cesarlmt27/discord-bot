import manager.games as gam
import manager.general as gen
import discord
from discord.ext import commands
import asyncio
from private.config import token

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


    @commands.command(help="Test if bot responds.")
    @commands.guild_only()
    async def ping(self, ctx):
        await ctx.send('pong')


    @commands.command(help="Start/stop streaming app.")
    @commands.guild_only()
    async def stream(self, ctx):
        output = gen.toggle_stream(ctx.message.author.id)
        await ctx.send(output)


    @commands.command(help="Shutdown, reboot/restart or boot to Windows.")
    @commands.guild_only()
    async def power(self, ctx, state):
        if(state == "shutdown"  or state == "off"):
            await ctx.send("Hibernating...")
            output = gen.power_mode(ctx.message.author.id, state)
            await ctx.send(output)

        elif(state == "reboot" or state == "restart"):
            await ctx.send("Rebooting...")
            output = gen.power_mode(ctx.message.author.id, state)
            await ctx.send(output)

        elif(state == "windows"):
            await ctx.send("Rebooting to Windows...")
            output = gen.power_mode(ctx.message.author.id, state)
            await ctx.send(output)

        else:
            await ctx.send("Invalid power state")



#Cog: Admin
class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(help="Send command to running server.")
    @commands.is_owner()
    async def server(self, ctx, msg):
        output = gam.send_command(msg)
        
        await ctx.send(output)

        if(msg == "stop" or msg == "quit"):
            await bot.change_presence(activity=None)
            await ctx.send("Server stopped. Remember to make a backup")


    @commands.command(help="Set up a server (game, target_channel, url).")
    @commands.is_owner()
    async def setup(self, ctx, target_channel, url=None):
        if(url is None):
            await ctx.send("Arguments were not given correctly")
            await ctx.send("Arguments: `target_channel, url`")
            return

        guild_id = ctx.guild.id
        guild_name = ctx.guild.name.replace(" ","_")
        channel_id = int(target_channel[2:-1])
        channel_name = bot.get_channel(channel_id)

        output = gam.setup_minecraft(url, guild_id, guild_name, channel_id, channel_name)
        
        if(isinstance(output, str)):
            await ctx.send(output)
        else:
            await ctx.send("This channel already has a Minecraft server; therefore, it will be updated")

            if(output.returncode == 0):
                await ctx.send("Minecraft server updated")
            else:
                await ctx.send("Minecraft server couldn't be updated: this is a Forge server, or another error occurred")


    @commands.command(help="Delete a minecraft server.")
    @commands.is_owner()
    async def delete_minecraft(self, ctx, target_channel):
        guild_name = ctx.guild.name.replace(" ","_")
        channel_id = int(target_channel[2:-1])
        channel_name = bot.get_channel(channel_id)

        output = gam.delete_minecraft(guild_name, channel_id, channel_name)
        await ctx.send(output)



#Cog: Server
class Server(commands.Cog, name='Games servers'):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(help="Run server.")
    @commands.guild_only()
    async def run(self, ctx, target_channel):
        channel_id = int(target_channel[2:-1])
        guild_name = ctx.guild.name.replace(" ","_")
        channel_name = bot.get_channel(channel_id)

        output = gam.run_server(channel_id, guild_name, channel_name)

        if(isinstance(output, str)):
            await ctx.send(output)
        else:
            success = output[0]
            game_name = output[1]

            if(success):
                await bot.change_presence(activity=discord.Game(name=game_name))
                await ctx.send(f"Starting {game_name} server")
            else:
                await ctx.send(f"{game_name} server starting failed")


    @commands.command(help="Stop server.")
    @commands.guild_only()
    async def stop(self, ctx, target_channel):
        channel_id = int(target_channel[2:-1])

        output = gam.stop_server(channel_id)
        
        if(output):
            await ctx.send("Server stopped. Remember to make a backup")
            await bot.change_presence(activity=None)
        else:
            await ctx.send("This server isn't running, or the given channel is invalid")


    @commands.command(help="Check if a server and a backup are running.")
    @commands.guild_only()
    async def status(self, ctx):
        output = gam.server_status()
        await ctx.send(output)


    @commands.command(help="Make a backup of a server data.")
    @commands.guild_only()
    async def backup(self, ctx, target_channel):
        channel_id = int(target_channel[2:-1])
        guild_name = ctx.guild.name.replace(" ","_")
        channel_name = bot.get_channel(channel_id)

        await ctx.send("If I don't respond to commands, it's because I'm doing the backup")

        ouput = gam.make_backup(channel_id, guild_name, channel_name)
        await ctx.send(ouput)


    @commands.command(help="Date and time of latest backup.")
    @commands.guild_only()
    async def latestb(self, ctx, target_channel):
        channel_id = int(target_channel[2:-1])
        guild_name = ctx.guild.name.replace(" ","_")
        channel_name = bot.get_channel(channel_id)

        output = gam.latest_backup_info(channel_id, guild_name, channel_name)
        await ctx.send(output)



async def main():
    async with bot:
        await bot.add_cog(General(bot))
        await bot.add_cog(Admin(bot))
        await bot.add_cog(Server(bot))
        await bot.start(token)

asyncio.run(main())