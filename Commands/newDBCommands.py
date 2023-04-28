import asyncio
import datetime
import time

import discord
from discord import app_commands
from discord.ext import commands

import Database_Functions.PrismaFunctions as dbFuncs
import Database_Functions.PrismaFunctions as DBFunc
from Database_Functions.PrismaFunctions import *
from Database_Functions.UserdbFunction import *
from Functions import permFunctions
# Embed types: Success, Warning, Error
from Functions.formattingFunctions import *
from Functions.formattingFunctions import embedBuilder
from Functions.mainVariables import *
from Functions.permFunctions import *
from Functions.randFunctions import *

### UPDATE FOR DATABASES ###


# Gave up and decided to rewrite it myself, command uses profile link and then discovers the rest on it's own

# Need group role IDs to complete setup here, as of now it works manually


class SealDBCommands(commands.GroupCog, group_name='sealtest'):
    def __init__(self, bot: commands.bot):
        self.bot = bot
            
    #Temporary command
    @app_commands.command(name="emojis", description="Just to send all the emojis of TRU bot.")
    async def emojiembed(self, interaction:discord.Interaction):
        embed = embedBuilder("Success", embedTitle="TRU Helper emojis:", 
                             embedDesc="<:trubotAccepted:1096225940578766968> `<:trubotAccepted:1096225940578766968>`\n<:trubotDenied:1099642433588965447> `<:trubotDenied:1099642433588965447>`\n<:trubotAbstain:1099642858505515018> `<:trubotAbstain:1099642858505515018>`\n<:trubotWarning:1099642918974783519> `<:trubotWarning:1099642918974783519>`\n<:trubotBeingLookedInto:1099642414303559720> `<:trubotBeingLookedInto:1099642414303559720>`\n<:trubotApproved:1099642447526637670> `<:trubotApproved:1099642447526637670>`\n<:trubotTRU:1096226111458918470> `<:trubotTRU:1096226111458918470>`")
        await interaction.response.send_message(embed=embed)
    



    """
    @app_commands.command(name="sanity", description="Register yourself with the TRU bot!")
    async def sanity(self, interaction: discord.Interaction, profileLink: str):
        interaction.response.send_message("Sanity check: ",
                                          permFunctions.checkPermission(interaction.user.top_role, DBFunc.findRole()))
    """

#????
class DBCmds(commands.GroupCog, group_name='devreg'):
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
                        embed = discord.Embed(title="<:trubotAccepted:1096225940578766968> Successfully registered!",
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
                            title=f"<:trubotAccepted:1096225940578766968> Successfully registered {user}!",
                            description=f"`Username:` {user}\n`User ID:` {user.id}\n`Roblox Profile:` {roblox_profile_link}",
                            color=discord.Color.green())
                    else:
                        embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Failed to register!",
                                              description=f"User is already in the database.", color=ErrorCOL)
                except Exception as e:
                    embed = discord.Embed(title="<:dsbbotFailed:953641818057216050> Registry failed!",
                                          description=f"An error occured: {str(e)}", color=ErrorCOL)
