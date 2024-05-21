import manager.server as ser
import discord
from discord.ext import commands
from discord import app_commands

class Server(commands.GroupCog, name="server"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Server cog loaded')


    @app_commands.command(name="start", description="Start the server.")
    @app_commands.guild_only()
    async def start(self, interaction, target_channel:str):
        channel_id = int(target_channel[2:-1])
        guild_name = interaction.guild.name.replace(" ","_")
        channel_name = self.bot.get_channel(channel_id)

        await interaction.response.defer()
        output = ser.start_server(channel_id, guild_name, channel_name)

        message = output[0]
        game_name = output[1]

        await self.bot.change_presence(activity=discord.Game(name=game_name))
        await interaction.followup.send(message)

    
    @app_commands.command(name="stop", description="Stop the server.")
    @app_commands.guild_only()
    async def stop(self, interaction, target_channel:str):
        channel_id = int(target_channel[2:-1])
        guild_name = interaction.guild.name.replace(" ","_")
        channel_name = self.bot.get_channel(channel_id)

        await interaction.response.defer()
        output = ser.stop_server(channel_id, guild_name, channel_name)

        message = output[0]

        await self.bot.change_presence(activity=None)
        await interaction.followup.send(message)


    @app_commands.command(name="status", description="Check a server status.")
    @app_commands.guild_only()
    async def status(self, interaction, target_channel:str):
        channel_id = int(target_channel[2:-1])
        guild_name = interaction.guild.name.replace(" ","_")
        channel_name = self.bot.get_channel(channel_id)

        await interaction.response.defer()
        output = ser.status_server(channel_id, guild_name, channel_name)

        status = output[0]
        game_name = output[1]

        await interaction.followup.send(f"{game_name} is {status}")


    @app_commands.command(name="backup", description="Make a backup of a server data")
    @app_commands.guild_only()
    async def backup(self, interaction, target_channel:str):
        channel_id = int(target_channel[2:-1])
        guild_name = interaction.guild.name.replace(" ","_")
        channel_name = self.bot.get_channel(channel_id)

        await interaction.response.defer()
        game_name = ser.backup_server(channel_id, guild_name, channel_name)

        await interaction.followup.send(f"{game_name} backup is in progress...")


async def setup(bot):
    await bot.add_cog(Server(bot))