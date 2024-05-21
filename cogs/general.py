import manager.general as gen
import discord
from discord.ext import commands
from discord import app_commands

class General(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('General cog loaded')


    # Ping command
    @app_commands.command(name="ping", description="Test if bot responds.")
    async def ping(self, interaction):
        await interaction.response.send_message("pong")

    
    # Power command (shutdown, reboot/restart, windows)
    @app_commands.command(name="power", description="Power state selector.")
    @app_commands.guild_only()
    @app_commands.describe(state='Select a power state')
    @app_commands.choices(state=[
        app_commands.Choice(name='shutdown', value='shutdown'),
        app_commands.Choice(name='restart', value='restart'),
        app_commands.Choice(name='windows', value='windows')
    ])
    async def power(self, interaction:discord.Interaction, state:app_commands.Choice[str]):
        if state.value == "shutdown":
            await interaction.response.send_message("Hibernating...")
        
        elif state.value == "restart":
            await interaction.response.send_message("Rebooting...")

        elif state.value == "windows":
            await interaction.response.send_message("Rebooting to Windows...")

        output = gen.power_mode(state.value)
        await interaction.edit_original_response(content=output)


    # Backup status command
    @app_commands.command(name="backup_status", description="Check a backup status.")
    @app_commands.guild_only()
    async def backup_status(self, interaction):
        if gen.backup_status():
            await interaction.response.send_message("A backup is in progress")
        else:
            await interaction.response.send_message("No backup in progress")


    # Latest backup info command
    @app_commands.command(name="latestb", description="Date and time of latest backup.")
    @app_commands.guild_only()
    async def latestb(self, interaction, target_channel:str):
        channel_id = int(target_channel[2:-1])
        guild_name = interaction.guild.name.replace(" ","_")
        channel_name = self.bot.get_channel(channel_id)

        output = gen.latest_backup_info(channel_id, guild_name, channel_name)
        await interaction.response.send_message(output)


async def setup(bot):
    await bot.add_cog(General(bot))