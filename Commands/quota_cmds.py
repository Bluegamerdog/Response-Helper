import asyncio
import datetime
import time

import discord
from discord import app_commands
from discord.ext import commands

import Database_Functions.PrismaFunctions as dbFuncs
from Database_Functions.PrismaFunctions import *
from Database_Functions.UserdbFunction import (add_points, get_points,
                                               remove_points, reset_points)
from Functions.formattingFunctions import embedBuilder
from Functions.mainVariables import *
from Functions.permFunctions import *
from prisma import Prisma

# Embed types: Success, Warning, Error

class patrolCmds(commands.GroupCog, group_name="patrol"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="start", description="Start a log.")
    async def startlog(self, interaction: discord.Interaction):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.logPermissionRole))):
            operativeResponse, operativeResponseBool = await dbFuncs.fetch_operative(interaction)
            if operativeResponse.activeLog == True:
                return await interaction.response.send_message(embed=discord.Embed(title="<:trubotDenied:1099642433588965447> Process failed!", description="You still have an on-going log.", color=ErrorCOL))      
                      
            if operativeResponseBool:
                date_time = datetime.datetime.now()
                unixTime = int(time.mktime(date_time.timetuple()))
                dbResponse, dbResponseBool = await dbFuncs.prismaCreatelog(interaction, str(unixTime))
                if dbResponseBool == True:
                    successEmbed = embedBuilder("Success", embedTitle="<:trubotAccepted:1096225940578766968> Log successfully started!", embedDesc=("Start time: <t:" + str(unixTime) + ":t>"))
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

    @app_commands.command(name="end", description="End your current log.")
    async def endlog(self, interaction: discord.Interaction):
        serverConfig = await fetch_config(interaction)
        op, opResponse = await fetch_operative(interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.logPermissionRole))):
            errEmbed = embedBuilder("Error", embedTitle="Permission error:",
                                    embedDesc="You are not: <@&" + str(serverConfig.logPermissionRole) + ">")
            await interaction.response.send_message(embed=errEmbed)
            return
        print(op)
        print(opResponse)
        if not opResponse:
            errEmbed = embedBuilder("Error", embedTitle="Operative not found!",
                                    embedDesc="Please make sure you are regsitered with the TRU bot before running commands!")
            await interaction.response.send_message(embed=errEmbed)
            return
        if checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.logPermissionRole))):
            date_time = datetime.datetime.now()
            unixTime = int(time.mktime(date_time.timetuple()))
            dbMessage, dbSuccess = await prismaEndLog(interaction, str(unixTime))
            if dbSuccess:
                successEmbed = embedBuilder("Success", embedTitle="Log ended successfully!", embedDesc="A log with the following details below was ended.")
                successEmbed.add_field(name="Time ended: ", value= "<t:" + str(unixTime) + ":f>")
                successEmbed.add_field(name="Log Time: ", value= str(dbMessage) + " minutes")
                await interaction.response.send_message(embed=successEmbed)
            else:
                errorEmbed = embedBuilder("Error", embedTitle="Unable to end log:", embedDesc="**Reason:** " + str(dbMessage))
                await interaction.response.send_message(embed=errorEmbed)
        else:
            errEmbed = embedBuilder("Error", embedTitle="Permission error:",
                                    embedDesc="You are not: <@&" + str(serverConfig.logPermissionRole) + ">")
            await interaction.response.send_message(embed=errEmbed)

    @app_commands.command(name="cancel", description="Cancel current log.")
    async def cancellog(self, interaction: discord.Interaction):
        serverConfig = await fetch_config(interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.logPermissionRole))):
            errEmbed = embedBuilder("Error", embedTitle="Permission error:",
                                    embedDesc="You are not: <@&" + str(serverConfig.logPermissionRole) + ">")
            await interaction.response.send_message(embed=errEmbed)
            return
        op, opResponse = await fetch_operative(interaction)
        log, logResponse = await checkLog(interaction)
        if not opResponse:
            errEmbed = embedBuilder("Error", embedTitle="Operative not found!",
                                    embedDesc="Please make sure you are regsitered with the TRU bot before running commands!")
            await interaction.response.send_message(embed=errEmbed)
        if not logResponse:
            errEmbed = embedBuilder("Error", embedTitle="Log not found!",
                                    embedDesc="No active log was found under your operative id.")
            await interaction.response.send_message(embed=errEmbed)
        if logResponse:
            print("Found a log")
            await prismaCancelLog(interaction)
            successEmbed = embedBuilder("Error", embedTitle="Log cancelled.",
                                        embedDesc="A log with the following details below was cancelled.")
            successEmbed.add_field(name="Log ID: ", value=str(log.logID))
            successEmbed.add_field(name="Log start time: ", value="<t:" + str(log.timeStarted) + ":f>")
            await interaction.response.send_message(embed=successEmbed)

    @app_commands.command(name="overview", description="Start a log.")
    async def logoverview(self, interaction: discord.Interaction):
        await interaction.response.send_message("Not done", ephemeral=True)
    
class viewdataCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.client = bot
    
    @app_commands.command(name="viewdata",description="View someones current quota status.")
    async def mypoints(self, interaction: discord.Interaction, member:discord.Member=None):
        try:
            if member==None:
                member = interaction.user
            
            db = Prisma()
            await db.connect()
            data = await db.operative.find_unique(where={"discordID": f"{member.id}"})
            log_amount = await db.logs.find_many(where={"operativeDiscordID": f"{member.id}"})
            await db.disconnect()
            
            if data == None:
                return await interaction.response.send_message(embed=embedBuilder("Error", embedDesc=f"Unable to find userdata on {member.mention}. Maybe they aren't registered?", embedTitle="No data found!"))
            else:
                embed = embedBuilder("Success", embedTitle=f"<:trubotAccepted:1096225940578766968> User data found!", embedDesc=f"Displaying {interaction.user.mention}'s data for block `TBA`.")
                embed.add_field(name="TRU Rank", value=f"> {data.rank}", inline=True)
                embed.add_field(name="Activity Status", value=f"> On Leave of Absence" if onLoA(member) else f"> Active Duty", inline=True)
                embed.add_field(name="", value="", inline=False) # Filler for 2x2 field config because discord
                embed.add_field(name="Responses Attended", value=f"> `TBA`", inline=True) # Need to add response attendance count
                embed.add_field(name="Patrols Logged", value=f"> {len(log_amount)}/Quota", inline=True) #(need to add something and be able to change quota at will)
                await interaction.response.send_message(embed=embed)
        except Exception as e:
            errEmbed = embedBuilder("Error", embedDesc=str(e), embedTitle="An error occurred.")
            await interaction.response.send_message(embed=errEmbed, ephemeral=True)
                

class quotaCmds(commands.GroupCog, group_name='quota'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @app_commands.command(name="set",description="Updates specified activity requirement for specified rank.")
    #@app_commands.describe(new_amount="Set the new quota requiremnt here if it is being changed.", activity_type="View: See the current quota. || log_amount: Set the log quota. || attendance_amount: Set the attendance quota. || toggle: Enable/disable the quota. (Quota=0)")
    @app_commands.choices(activity_type=[
        app_commands.Choice(name="patrol_requirement", value="patrol"),
        app_commands.Choice(name="response_requirement", value="response"),])
    async def set_quota(self, interaction:discord.Interaction, rank:discord.Role, activity_type:app_commands.Choice[str], new_amount:int=None):
        return await interaction.response.send_message(embed=embedBuilder("Warning", embedDesc="This command isn't done yet.",embedTitle="No worki yeti"), ephemeral=True)
    
    @app_commands.command(name="overview",description="View all set quotas for all ranks.")
    async def viewquota(self, interaction:discord.Interaction):
        return await interaction.response.send_message(embed=embedBuilder("Warning", embedDesc="This command isn't done yet.",embedTitle="No worki yeti"), ephemeral=True)
        # Will work on after some sleep but needs a DB integration
    '''
    @app_commands.command(name="block",description="Updates the quota block data. [TRUPC+]")
    @app_commands.describe(block="Enter a block number 7 through 26.", action="View: See info about a specific block. || Change: Set a new active block. || List: See a list of all pre-set blocks.")
    @app_commands.choices(action=[
        app_commands.Choice(name="view", value="view"),
        app_commands.Choice(name="change", value="change"),
        app_commands.Choice(name="list_all", value="list"),
        ])
    async def updatequota(self, interaction:discord.Interaction, action:app_commands.Choice[str], block:int=None):
        if not TRULEAD(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Missing Permission!", description="You must be a member of TRUPC or above to use this command.", color=ErrorCOL))
        all_blockdata, rows = get_all_quota_data()
        if rows == 0:
                return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> No quota block data found!", description="There are no quota blocks in the database.", color=ErrorCOL))
        if action.value == "list":
            msg = f"I found data on {rows} block!\n\n" if rows == 1 else f"I found data on {rows} blocks!\n\n"
            for data in all_blockdata:
                msg += f"**Block {data[0]}** // Active: {bool(data[3])}\n<t:{data[1]}> - <t:{data[2]}>\n\n"
            return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotInformation:1093651827234443266> List of Quota Blocks", description=msg, color=HRCommandsCOL), ephemeral=True)
        if not block:
            return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> No block found!", description="Please enter a block's number to view or activate it.", color=ErrorCOL))
        blockdata = get_quota()
        req_blockdata = get_quota(block_num=block)
        if req_blockdata:
            if action.value == "view":
                return await interaction.response.send_message(embed = discord.Embed(color=HRCommandsCOL, title=f"<:dsbbotInformation:1093651827234443266> Quota Block {req_blockdata[0]}", description=f"**Start Date:** <t:{req_blockdata[1]}:F>\n**End Date:** <t:{req_blockdata[2]}:F>\n**Active:** {bool(req_blockdata[3])}"), ephemeral=True)
            elif action.value == "change":
                if blockdata: # Check if there is an active block
                    if block == blockdata[0]: # Given block is already active
                        return await interaction.response.send_message(embed= discord.Embed(color=YellowCOL, title=f"<:trubotWarning:1099642918974783519> Quota Block {blockdata[0]} is already active!", description=f"Start Date: <t:{blockdata[1]}:F>\nEnd Date: <t:{blockdata[2]}:F>"), ephemeral=True)
                    else: # If there was an active block but it is now changed
                        set_active_block(block_num=block)
                        new_blockdata = get_quota()
                        return await interaction.response.send_message(embed= discord.Embed(color=HRCommandsCOL, title=f"<:trubotAccepted:1096225940578766968> Successfully changed Quota Block!", description=f"*Quota Block {blockdata[0]} is now inactive and Quota Block {new_blockdata[0]} has been set as active!*\n**Before**\n<t:{blockdata[1]}:F> - <t:{blockdata[2]}:F>\n\n**After**\n<t:{new_blockdata[1]}:F> - <t:{new_blockdata[2]}:F>"))
                else: # There is now an active quota block
                    set_active_block(block_num=block)
                    new_blockdata = get_quota()
                    return await interaction.response.send_message(embed= discord.Embed(color=HRCommandsCOL, title=f"<:trubotAccepted:1096225940578766968> Successfully set Quota Block!", description=f"*Quota Block {new_blockdata[0]} has been set to active!*\n**Start Date:** <t:{new_blockdata[1]}:F>\n**End Date:** <t:{new_blockdata[2]}:F>"))
        else:
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title=f"<:dsbbotFailed:953641818057216050> No quota information for block number {block} found!", description=f"If you feel something is wrong with the database, please ping <@776226471575683082>."), ephemeral=True)
'''

    @app_commands.command(name="modify",description="Updates the quota block data. [TRUPC+]")
    @app_commands.describe(new_amount="Set the new quota requiremnt here if it is being changed.", action="View: See the current quota. || log_amount: Set the log quota. || attendance_amount: Set the attendance quota. || toggle: Enable/disable the quota. (Quota=0)")
    @app_commands.choices(action=[
        app_commands.Choice(name="view", value="view"),
        app_commands.Choice(name="log_amount", value="logs"),
        app_commands.Choice(name="attendance_amount", value="attendance"),
        app_commands.Choice(name="toggle", value="toggle"),
        ])
    async def modify_quota(self, interaction:discord.Interaction, action:app_commands.Choice[str], new_amount:int=None):
        return await interaction.response.send_message(embed=embedBuilder("Warning", embedDesc="This command isn't done yet.",embedTitle="No worki yeti"), ephemeral=True)
        # Will work on after some sleep but needs a DB integration

