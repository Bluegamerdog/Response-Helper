import asyncio
import datetime

import discord
from discord import app_commands
from discord.ext import commands

import Database_Functions.PrismaFunctions as dbFuncs
from Database_Functions.UserdbFunction import *
from Functions import permFunctions
from Functions.formattingFunctions import embedBuilder
from Functions.mainVariables import *
from Functions.permFunctions import *
from Functions.randFunctions import *

## Awaiting transfer ##

class registryCmds(commands.GroupCog, group_name='operative'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @app_commands.command(name="register", description="Add a new operator to the registry.")
    async def operative_register(self, interaction: discord.Interaction, profilelink: str, user:discord.Member=None):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.logPermissionRole))):
            if user and not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.commandRole))):
                return await interaction.response.send_message(embed=discord.Embed(title="Missing permission!", description="Only TRU leadership and above may register other users.", color=ErrorCOL))
            Operative = user if user else interaction.user
            operativeName = Operative.nick.rsplit(maxsplit=1)[-1]
            dbResponse = await dbFuncs.registerUser(Operative, profilelink, operativeName)
            if dbResponse:
                successEmbed = discord.Embed(title="<:trubotAccepted:1096225940578766968> Successfully registered!",
                                            description="New registry entry:", color=SuccessCOL)

                successEmbed.add_field(name="Username:", value=dbResponse.userName, inline=True)
                successEmbed.add_field(name="TRU Rank:", value=dbResponse.rank, inline=True)
                successEmbed.add_field(name="Profile Link:", value=f"[{dbResponse.userName}]({dbResponse.profileLink})", inline=True)
                successEmbed.set_footer(text=f"Registered on: {datetime.datetime.utcnow().strftime('%m/%d/%Y %H:%M')}Z")
                await interaction.response.send_message(embed=successEmbed)
            else:
                errEmbed = embedBuilder("Error", embedTitle="An error occured:",
                                        embedDesc="Error: " + str(dbResponse))
                await interaction.response.send_message(embed=errEmbed)



        else:
            errEmbed = embedBuilder("Error", embedTitle="Permission error:",
                                    embedDesc="You are not: <@&" + str(serverConfig.logPermissionRole) + ">")
            await interaction.response.send_message(embed=errEmbed)
    

    @app_commands.command(name="update", description="Update someone's registry data.")
    async def operative_update(self, interaction: discord.Interaction, profilelink:str=None, user:discord.Member=None):
        return await interaction.response.send_message("This command isn't complete.", ephemeral=True)
        
        
    @app_commands.command(name="remove", description="Remove someone from the registry.")
    async def operative_remove(self, interaction: discord.Interaction, user:discord.Member=None, userid:str=None):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.commandRole))):
            errEmbed = embedBuilder("Error", embedTitle="Permission error:", embedDesc="You are not: <@&" + str(serverConfig.commandRole) + ">")
            return await interaction.response.send_message(embed=errEmbed)
        if userid:
            userid = int(userid)
        if user is None and userid is None:
            return await interaction.response.send_message(embed=discord.Embed(title="Invalid arguments", description="Please provide a user or user ID.", color=ErrorCOL))

        if user and userid and userid != user.id:
            return await interaction.response.send_message(embed=discord.Embed(title="User error!", description="You specified two different users.", color=ErrorCOL))
        if not userid:
            userid = user.id
        dbResponse = await dbFuncs.removeOperative(userid)

        if dbResponse == True:
            successEmbed = embedBuilder("Success", embedTitle="Success!",
                                        embedDesc=f"Operative with ID {userid} has been removed from the registry." if user is None else f"{user.mention} has been removed from the registry.")
            await interaction.response.send_message(embed=successEmbed)
        else:
            errEmbed = embedBuilder("Error", embedTitle="An error occurred:",
                                    embedDesc="Error: " + str(dbResponse))
            await interaction.response.send_message(embed=errEmbed)
        
    @app_commands.command(name="view", description="View someone's registry data.")
    async def operative_view(self, interaction: discord.Interaction, user:discord.Member=None):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.logPermissionRole))):
            return await interaction.response.send_message("This command isn't complete.", ephemeral=True)
        if not user:
            user = interaction.user
        requested_operative = await dbFuncs.viewOperative(user.id)
        if not requested_operative:
            return await interaction.response.send_message(embed = discord.Embed(title="<:trubotDenied:1099642433588965447> Error!", description=f"{user.mention} was not found in the registry.", color=ErrorCOL))
        embed = discord.Embed(title=f"<:trubotAccepted:1096225940578766968> User found!", description=f"**Username:** {requested_operative.userName}\n**TRU Rank:** {requested_operative.rank}\n**Roblox Profile:** {requested_operative.profileLink}", color=SuccessCOL)
        return await interaction.response.send_message(embed=embed)

