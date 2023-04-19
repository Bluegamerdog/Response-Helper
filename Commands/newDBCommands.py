import discord
import asyncio
#Embed types: Success, Warning, Error
from Functions.formattingFunctions import embedBuilder
from discord.ext import commands
from discord import app_commands
from Database_Functions.MaindbFunctions import *
from Database_Functions.UserdbFunction import *
from Functions.mainVariables import *
from Functions.permFunctions import *
from Functions.randFunctions import *
from Functions.formattingFunctions import *

### UPDATE FOR DATABASES ###



def CheckPermissions(userRole: discord.role, targetRole: discord.role):
    pass

#Gave up and decided to rewrite it myself, command uses profile link and then discovers the rest on it's own
class SealDBCommands(commands.GroupCog, group_name='TRURegistry'):
    def __init__(self, bot: commands.bot):
        self.bot = bot
    @app_commands.command(name="register", description="Register yourself with the TRU bot!")
    
    async def register(self, interaction: discord.Interaction, profileLink: str):
        pass


#How does this even work? Does it work???
class RegistryCmds(commands.GroupCog, group_name='devreg'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        @app_commands.command(name="new", description="This command is used to add new data to the registry database.")
        async def register_new(self, interaction: discord.Interaction, roblox_profile_link: str,
                               user: discord.Member = None):
            if not TRUMEMBER(interaction.user):
                return await interaction.response.send_message(
                    embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Registry failed!",
                                        description=f"Only TRU Private First Class or above may register.",
                                        color=ErrorCOL))
            if user and user != interaction.user and not TRULEAD(interaction.user):
                return await interaction.response.send_message(
                    embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Registry failed!",
                                        description=f"You must be a member of TRUPC or above to register other users.",
                                        color=ErrorCOL), ephemeral=True)
            if user == None or user == interaction.user:
                try:
                    if db_register_new(str(interaction.user), interaction.user.id, roblox_profile_link):
                        embed = discord.Embed(title="<:dsbbotSuccess:953641647802056756> Successfully registered!",
                                              description=f"`Username:` {interaction.user}\n`User ID:` {interaction.user.id}\n`Roblox Profile:` {roblox_profile_link}",
                                              color=discord.Color.green())
                    else:
                        embed = discord.Embed(title="<:dsbbotFailed:953641818057216050> Failed to register!",
                                              description=f"You are already in the database.\n*If you wish to update your data, use `/database update`.*",
                                              color=ErrorCOL)
                except Exception as e:
                    embed = discord.Embed(title="<:dsbbotFailed:953641818057216050> Registry failed!",
                                          description=f"An error occured: {str(e)}", color=ErrorCOL)
            else:
                try:
                    if db_register_new(str(user), user.id, roblox_profile_link):
                        embed = discord.Embed(
                            title=f"<:dsbbotSuccess:953641647802056756> Successfully registered {user}!",
                            description=f"`Username:` {user}\n`User ID:` {user.id}\n`Roblox Profile:` {roblox_profile_link}",
                            color=discord.Color.green())
                    else:
                        embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Failed to register!",
                                              description=f"User is already in the database.", color=ErrorCOL)
                except Exception as e:
                    embed = discord.Embed(title="<:dsbbotFailed:953641818057216050> Registry failed!",
                                          description=f"An error occured: {str(e)}", color=ErrorCOL)