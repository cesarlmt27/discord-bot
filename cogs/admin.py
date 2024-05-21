import manager.admin as adm
import discord
from discord.ext import commands
from discord import app_commands


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Admin cog loaded')

    def is_owner():
        def predicate(interaction:discord.Interaction):
            if interaction.user.id == interaction.guild.owner_id:
                return True
        return app_commands.check(predicate)


    @app_commands.command(name="setup", description="Setup a game sever.")
    @app_commands.guild_only()
    @is_owner()
    async def setup(self, interaction, target_channel:str, game_name:str, directory_name:str, executable_name:str):
        guild_id = interaction.guild.id
        guild_name = interaction.guild.name.replace(" ","_")
        channel_id = int(target_channel[2:-1])
        channel_name = self.bot.get_channel(channel_id)

        await interaction.response.defer()
        output = adm.add_game_server(game_name, directory_name, executable_name, guild_name, channel_name, guild_id, channel_id)
        await interaction.followup.send(output)


    @app_commands.command(name="remove", description="Remove a game sever.")
    @app_commands.guild_only()
    @is_owner()
    async def remove(self, interaction, target_channel:str):
        guild_name = interaction.guild.name.replace(" ","_")
        channel_id = int(target_channel[2:-1])
        channel_name = self.bot.get_channel(channel_id)

        await interaction.response.defer()
        output = adm.remove_game_server(channel_id, guild_name, channel_name)
        await interaction.followup.send(output)


async def setup(bot):
    await bot.add_cog(Admin(bot))