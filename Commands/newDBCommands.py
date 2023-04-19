import discord
import asyncio

import Database_Functions.PrismaFunctions
from Functions import permFunctions
# Embed types: Success, Warning, Error
from Functions.formattingFunctions import embedBuilder
from discord.ext import commands
from discord import app_commands
from Database_Functions.MaindbFunctions import *
import Database_Functions.PrismaFunctions as DBFunc
from Database_Functions.UserdbFunction import *
from Functions.mainVariables import *
from Database_Functions.PrismaFunctions import *
from Functions.permFunctions import *
from Functions.randFunctions import *
from Functions.formattingFunctions import *


### UPDATE FOR DATABASES ###


# Gave up and decided to rewrite it myself, command uses profile link and then discovers the rest on it's own
class SealDBCommands(commands.GroupCog, group_name='trudbtesting'):
    def __init__(self, bot: commands.bot):
        self.bot = bot

    @app_commands.command(name="rolebind", description="Bind a role using ")
    # @app_commands.describe(roles="Roles to bind")
    async def rolebind(self, interaction: discord.Interaction, role: discord.Role,
                       robloxid: int):
        try:

            permFunctions.checkPermission(interaction.user.top_role, )
            await interaction.response.send_message("Sanity check, is the role I passed below me: " +
                                                    permFunctions.checkPermission(interaction.user.top_role, role,
                                                                                  ), ephemeral=True)
        except Exception as e:
            errEmbed = embedBuilder("Error", embedDesc=str(e), embedTitle="An error occurred.")
            await interaction.response.send_message(embed=errEmbed, ephemeral=True)

    rolebind._params["role"].required = True
    rolebind._params["robloxid"].required = True

    @app_commands.command(name="serverconfig", description="Configure bot permission settings")
    async def serverconfig(self, interaction: discord.Interaction, logrole: discord.Role, schedule_role: discord.Role,
                           announce_channel: discord.TextChannel, command_role: discord.Role,
                           developer_role: discord.Role, ping_role: discord.Role):
        db = Prisma()
        await db.connect()
        await db.server.upsert(where={
            'serverID': str(interaction.guild.id)
            },
            data={
                'create':{
                    'serverID': str(interaction.guild.id),
                    'announceRole': str(ping_role.id),
                    'announceChannel': str(announce_channel.id),
                    'logPermissionRole': str(logrole.id),
                    'announcePermissionRole': str(schedule_role.id),
                    'commandRole': str(command_role.id),
                    'developerRole': str(developer_role.id)
                }, 'update': {
                    'announceRole': str(ping_role.id),
                    'announceChannel': str(announce_channel.id),
                    'logPermissionRole': str(logrole.id),
                    'announcePermissionRole': str(schedule_role.id),
                    'commandRole': str(command_role.id),
                    'developerRole': str(developer_role.id)
                }

        })
        await db.disconnect()

        embed = embedBuilder(embedType="Success", embedTitle="Success!", embedDesc="A configuration with the following details was made: ")
        embed.add_field(name="Role to ping for announcements: ", value="<@&" + str(ping_role.id) + ">")
        embed.add_field(name="Role permission for logging: ", value="<@&" + str(logrole.id) + ">")
        embed.add_field(name="Role permission for scheduling: ", value="<@&" + str(schedule_role.id) + ">")
        embed.add_field(name="Announcements channel: ", value="<#" + str(announce_channel.id) + ">")
        embed.add_field(name="TRU Command role: ", value="<@&" + str(command_role.id) + ">")
        embed.add_field(name="Developer role: ", value="<@&" + str(developer_role.id) + ">")
        await interaction.response.send_message(embed=embed, ephemeral=False)


    """
    @app_commands.command(name="sanity", description="Register yourself with the TRU bot!")
    async def sanity(self, interaction: discord.Interaction, profileLink: str):
        interaction.response.send_message("Sanity check: ",
                                          permFunctions.checkPermission(interaction.user.top_role, DBFunc.findRole()))
    """


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
