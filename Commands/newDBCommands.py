import discord
import asyncio

import Database_Functions.PrismaFunctions as dbFuncs
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
import datetime
import time





### UPDATE FOR DATABASES ###


# Gave up and decided to rewrite it myself, command uses profile link and then discovers the rest on it's own

# Need group role IDs to complete setup here, as of now it works manually
class SealDBCommands(commands.GroupCog, group_name='trudbtesting'):
    def __init__(self, bot: commands.bot):
        self.bot = bot

    @app_commands.command(name="register", description="Register in the DB")
    async def register(self, interaction: discord.Interaction, profilelink: str):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.logPermissionRole))):
            dbResponse = await dbFuncs.registerUser(interaction, interaction.user.id, profilelink, interaction.user.nick)
            if dbResponse:
                successEmbed = embedBuilder("Success", embedTitle="<:trubotAccepted:1096225940578766968> Successfully Registered!",
                                            embedDesc="An operative with the following details was created: ")
                operativeName = interaction.user.nick.split()[-1]
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
            
            
    @app_commands.command(name="startlog", description="Start a log.")
    async def startlog(self, interaction: discord.Interaction):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.logPermissionRole))):
            operativeResponse, operativeResponseBool = await dbFuncs.fetch_operative(interaction)
            if operativeResponseBool:
                date_time = datetime.datetime.now()
                unixTime = int(time.mktime(date_time.timetuple()))
                dbResponse, dbResponseBool = await dbFuncs.prismaCreatelog(interaction, str(unixTime))
                if dbResponseBool == True:
                    successEmbed = embedBuilder("Success", embedTitle="Log successful started! ", embedDesc=("Log started at: <t:" + str(unixTime) + ":f>"))
                    print(successEmbed)
                    await interaction.response.send_message(embed=successEmbed)
                else:
                    errorEmbed = embedBuilder("Error", embedTitle="An error occurred.", embedDesc="Error details: " + str(dbResponse))
                    await interaction.response.send_message(embed=errorEmbed)
            else:
                errorEmbed = embedBuilder("Error", embedTitle="An error occurred.",
                                          embedDesc="Error details: " + str(operativeResponse))
                await interaction.response.send_message(embed=errorEmbed)


        else:
            errEmbed = embedBuilder("Error", embedTitle="Permission error:",
                                    embedDesc="You are not: <@&" + str(serverConfig.logPermissionRole) + ">")
            await interaction.response.send_message(embed=errEmbed)


    @app_commands.command(name="rolebind", description="Bind a role using ")
    # @app_commands.describe(roles="Roles to bind")
    async def rolebind(self, interaction: discord.Interaction, role: discord.Role,
                       robloxid: int):
        try:
            serverConfig = await dbFuncs.fetch_config(interaction=interaction)
            requiredRole = interaction.guild.get_role(int(serverConfig.commandRole))
            if permFunctions.checkPermission(interaction.user.top_role, requiredRole):
                try:
                    dbresponse = await dbFuncs.createBinding(role, robloxid, interaction)
                    if dbresponse == True:
                        successEmbed = embedBuilder("Success", embedTitle="A role binding was created for the "
                                                                          "following: ",
                                                    embedDesc="Discord role: <@&" + str(role.id) + "> and Roblox role "
                                                                                                   "id of: " + str(
                                                        robloxid))
                        await interaction.response.send_message(embed=successEmbed)
                    else:
                        errEmbed = embedBuilder("Error", embedTitle="An error occured:",
                                                embedDesc="Error: " + str(dbresponse))
                        await interaction.response.send_message(embed=errEmbed)
                except Exception as e:
                    errEmbed = embedBuilder("Error", embedTitle="An error occured:",
                                            embedDesc="Error: " + str(e))
                    await interaction.response.send_message(embed=errEmbed, ephemeral=True)
            else:
                errEmbed = embedBuilder("Error", embedTitle="Permission error:",
                                        embedDesc="You are not: <@&" + str(requiredRole.id) + ">")
                await interaction.response.send_message(embed=errEmbed, ephemeral=True)

        except Exception as e:
            errEmbed = embedBuilder("Error", embedDesc=str(e), embedTitle="An error occurred.")
            await interaction.response.send_message(embed=errEmbed, ephemeral=True)

    rolebind._params["role"].required = True
    rolebind._params["robloxid"].required = True


    @app_commands.command(name="viewbinds", description="View all set binds")
    async def viewbinds(self, interaction: discord.Interaction):
        try:
            roles = await get_all_role_bindings()
            if len(roles) > 0:
                bind_list = discord.Embed(title=f"TRU Helper Rolebinds", color=TRUCommandCOL)
                for role in roles:
                    bind_list.add_field(name=f"➣ Rank Name: {role.rankName}", value=f"> Discord Role: <@&{role.discordRoleID}>\n> Roblox Rank ID: {role.RobloxRankID}", inline=False)
                await interaction.response.send_message(embed=bind_list, ephemeral=True)
            else:
                await interaction.response.send_message("No role bindings found.")
        except Exception as e:
            errEmbed = embedBuilder("Error", embedDesc=str(e), embedTitle="An error occurred.")
            await interaction.response.send_message(embed=errEmbed, ephemeral=True)
    
    #Temporary command
    @app_commands.command(name="emojis", description="Just to send all the emojis of TRU bot.")
    async def emojiembed(self, interaction:discord.Interaction):
        embed = embedBuilder("Success", embedTitle="TRU Helper emojis:", 
                             embedDesc="<:trubotAccepted:1096225940578766968> `<:trubotAccepted:1096225940578766968>`\n<:trubotDenied:1099642433588965447> `<:trubotDenied:1099642433588965447>`\n<:trubotAbstain:1099642858505515018> `<:trubotAbstain:1099642858505515018>`\n<:trubotWarning:1099642918974783519> `<:trubotWarning:1099642918974783519>`\n<:trubotBeingLookedInto:1099642414303559720> `<:trubotBeingLookedInto:1099642414303559720>`\n<:trubotApproved:1099642447526637670> `<:trubotApproved:1099642447526637670>`\n<:trubotTRU:1096226111458918470> `<:trubotTRU:1096226111458918470>`")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="setserverconfig", description="Configure bot permission settings")
    async def serverconfig(self, interaction: discord.Interaction, logrole: discord.Role, schedule_role: discord.Role,
                           announce_channel: discord.TextChannel, command_role: discord.Role,
                           developer_role: discord.Role, ping_role: discord.Role):
        db = Prisma()
        await db.connect()
        #await db.operative.
        await db.server.upsert(where={
            'serverID': str(interaction.guild.id)
        },
            data={
                'create': {
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

        embed = embedBuilder(embedType="Success", embedTitle="Success!",
                             embedDesc="A configuration with the following details was made: ")
        embed.add_field(name="Response pings: ", value="<@&" + str(ping_role.id) + ">")
        embed.add_field(name="Member role: ", value="<@&" + str(logrole.id) + ">")
        embed.add_field(name="Response Leaders: ", value="<@&" + str(schedule_role.id) + ">")
        embed.add_field(name="Response announcements channel: ", value="<#" + str(announce_channel.id) + ">")
        embed.add_field(name="TRU Leadership role: ", value="<@&" + str(command_role.id) + ">")
        embed.add_field(name="TRU Helper Dev role: ", value="<@&" + str(developer_role.id) + ">")
        await interaction.response.send_message(embed=embed, ephemeral=False)



    
    @app_commands.command(name="editconfig", description="Edit bot permission settings")
    async def editconfig(self, interaction: discord.Interaction, logrole: discord.Role = None,
                        response_leaders: discord.Role = None, resp_announcement_channel: discord.TextChannel = None,
                        leadership_role: discord.Role = None, developer_role: discord.Role = None,
                        response_pings: discord.Role = None):
        db = Prisma()
        await db.connect()

        server_config = await db.server.find_first(where={'serverID': str(interaction.guild.id)})
        if not server_config:
            await interaction.response.send_message(
                "Configuration not found. Please use the `/serverconfig` command to create a configuration first.",
                ephemeral=True)
            return

        update_data = {}
        if logrole:
            update_data['logPermissionRole'] = str(logrole.id)
        if response_leaders:
            update_data['announcePermissionRole'] = str(response_leaders.id)
        if resp_announcement_channel:
            update_data['announceChannel'] = str(resp_announcement_channel.id)
        if leadership_role:
            update_data['commandRole'] = str(leadership_role.id)
        if developer_role:
            update_data['developerRole'] = str(developer_role.id)
        if response_pings:
            update_data['announceRole'] = str(response_pings.id)

        await db.server.update(where={'serverID': str(interaction.guild.id)}, data=update_data)
        await db.disconnect()
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        embed = embedBuilder(embedType="Success", embedTitle="<:trubotAccepted:1096225940578766968> Successfully updated server configs!",
                            embedDesc=f"{interaction.guild.name}'s Server Configuration updated: ")
        if response_pings:
            embed.add_field(name="Response pings: ", value="<@&" + str(serverConfig.announceRole) + ">")
        if logrole:
            embed.add_field(name="Member role: ", value="<@&" + str(serverConfig.logPermissionRole) + ">")
        if response_leaders:
            embed.add_field(name="Response Leaders: ", value="<@&" + str(serverConfig.announcePermissionRole) + ">")
        if resp_announcement_channel:
            embed.add_field(name="Response announcements channel: ", value="<#" + str(serverConfig.announceChannel) + ">")
        if leadership_role:
            embed.add_field(name="TRU Leadership role: ", value="<@&" + str(serverConfig.commandRole) + ">")
        if developer_role:
            embed.add_field(name="TRU Helper Dev role: ", value="<@&" + str(serverConfig.developerRole) + ">")

        await interaction.response.send_message(embed=embed, ephemeral=False)



        
    @app_commands.command(name="viewconfig", description="View the current server configs.")
    async def viewconfig(self, interaction: discord.Interaction):
        db = Prisma()
        await db.connect()
        server_config = await db.server.find_first(where={"serverID": str(interaction.guild.id)})
        await db.disconnect()

        if server_config:
            embed = embedBuilder("Success", embedTitle=f"{interaction.guild.name} || Server Configurations", embedDesc=None)
            embed.add_field(name="Response pings:", value=f"<@&{server_config.announceRole}>")
            embed.add_field(name="Member role:", value=f"<@&{server_config.logPermissionRole}>")
            embed.add_field(name="Response Leaders:", value=f"<@&{server_config.announcePermissionRole}>")
            embed.add_field(name="Response announcement channel:", value=f"<#{server_config.announceChannel}>")
            embed.add_field(name="TRU Leadership role:", value=f"<@&{server_config.commandRole}>")
            embed.add_field(name="TRU Helper Dev role:", value=f"<@&{server_config.developerRole}>")
            await interaction.response.send_message(embed=embed, ephemeral=False)
        else:
            await interaction.response.send_message(content="No server configuration found", ephemeral=True)


    """
    @app_commands.command(name="sanity", description="Register yourself with the TRU bot!")
    async def sanity(self, interaction: discord.Interaction, profileLink: str):
        interaction.response.send_message("Sanity check: ",
                                          permFunctions.checkPermission(interaction.user.top_role, DBFunc.findRole()))
    """


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
