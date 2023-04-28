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
        
    @app_commands.command(name="register", description="Register in the DB")
    async def register(self, interaction: discord.Interaction, profilelink: str):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.logPermissionRole))):
            operativeName_list = list(interaction.user.nick.split(" "))
            operativeName = operativeName_list[len(operativeName_list) - 1]
            dbResponse = await dbFuncs.registerUser(interaction, interaction.user.id, profilelink, operativeName)
            if dbResponse:
                successEmbed = embedBuilder("Success", embedTitle="Success!",
                                            embedDesc="An operative with the following details was created: ")

                successEmbed.add_field(name="Operative name: ", value=operativeName)
                successEmbed.add_field(name="Operative profile link: ", value=profilelink)
                successEmbed.add_field(name="Operative rank: ", value=str(interaction.user.top_role.name))
                successEmbed.add_field(name="Registered on: ", value=str(datetime.datetime.utcnow()) + "Z")
                await interaction.response.send_message(embed=successEmbed)
            else:
                errEmbed = embedBuilder("Error", embedTitle="An error occured:",
                                        embedDesc="Error: " + str(dbResponse))
                await interaction.response.send_message(embed=errEmbed)



        else:
            errEmbed = embedBuilder("Error", embedTitle="Permission error:",
                                    embedDesc="You are not: <@&" + str(serverConfig.logPermissionRole) + ">")
            await interaction.response.send_message(embed=errEmbed)
    

    # Need to transfer and add from newDBCommands.py
    # Need update, remove and maybe view as well for this
