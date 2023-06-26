import asyncio
import datetime
import time

import discord
from discord import app_commands
from discord.ext import commands

from Database_Functions.PrismaFunctions import *
from Database_Functions.PrismaFunctions import *
from Database_Functions.UserdbFunction import (add_points, get_points,
                                               remove_points, reset_points)
from Functions.formattingFunctions import embedBuilder
from Functions.mainVariables import *
from Functions.rolecheckFunctions import *
from Functions.trelloFunctions import *
from prisma import Prisma

# Embed types: Success, Warning, Error

class patrolCmds(commands.GroupCog, group_name="patrol"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="start", description="Start a log.")
    async def startlog(self, interaction: discord.Interaction):
        serverConfig = await fetch_config(interaction=interaction)
        if checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.logPermissionRole))):
            requestedOperator = await getOperator(int(interaction.user.id))
            if requestedOperator.activeLog == True:
                return await interaction.response.send_message(embed = embedBuilder(responseType="err", embedTitle="Process failed", embedDesc="You still have an on-going log."))      
                      
            if requestedOperator:
                date_time = datetime.now()
                startTime_unix = int(time.mktime(date_time.timetuple()))
                endTime = int(startTime_unix) + 300 #1500 = 25 minutes
                dbResponse, dbResponseBool = await prismaCreatelog(interaction, str(startTime_unix))
                if dbResponseBool == True:
                    successEmbed = embedBuilder("succ", embedTitle="Log started!", embedDesc=f"Don't forget to end your log when you're done. You can end your log at <t:{endTime}:t> using </patrol end:1101469326097264693> or you can cancel your log anytime using </patrol cancel:1101469326097264693>.\n*Have a nice patrol!*")
                    await interaction.response.send_message(embed=successEmbed)
                else:
                    errorEmbed = embedBuilder("err", embedDesc="Error details: " + str(dbResponse))
                    await interaction.response.send_message(embed=errorEmbed)
            else:
                errorEmbed = embedBuilder("err",
                                          embedDesc="Error details: " + str(requestedOperator))
                await interaction.response.send_message(embed=errorEmbed)


        else:
            errEmbed = embedBuilder("err", embedTitle="Permission error:",
                                    embedDesc="You are not: <@&" + str(serverConfig.logPermissionRole) + ">")
            await interaction.response.send_message(embed=errEmbed)

    @app_commands.command(name="end", description="End your current log.")
    async def endlog(self, interaction: discord.Interaction):
        serverConfig = await fetch_config(interaction)
        op, opResponse = await getOperator(interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.logPermissionRole))):
            errEmbed = embedBuilder("err", embedTitle="Permission error:",
                                    embedDesc="You are not: <@&" + str(serverConfig.logPermissionRole) + ">")
            await interaction.response.send_message(embed=errEmbed)
            return
        if not opResponse:
            errEmbed = embedBuilder("err", embedTitle="Operative not found!",
                                    embedDesc="Please make sure you are registered with the TRU bot before running commands!")
            await interaction.response.send_message(embed=errEmbed)
            return
        if checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.logPermissionRole))):
            date_time = datetime.datetime.now()
            unixTime = int(time.mktime(date_time.timetuple()))
            dbMessage, dbSuccess = await prismaEndLog(interaction, str(unixTime))
            if dbSuccess:
                successEmbed = embedBuilder("succ", embedTitle="Log ended successfully!", embedDesc="A log with the following details below was ended.")
                successEmbed.add_field(name="Time ended: ", value= "<t:" + str(unixTime) + ":f>")
                successEmbed.add_field(name="Log Time: ", value= str(dbMessage) + " minutes")
                await interaction.response.send_message(embed=successEmbed)
            else:
                errorEmbed = embedBuilder("err", embedTitle="Unable to end log:", embedDesc="**Reason:** " + str(dbMessage))
                await interaction.response.send_message(embed=errorEmbed)
        else:
            errEmbed = embedBuilder("err", embedTitle="Permission error:",
                                    embedDesc="You are not: <@&" + str(serverConfig.logPermissionRole) + ">")
            await interaction.response.send_message(embed=errEmbed)

    @app_commands.command(name="cancel", description="Cancel current log.")
    async def cancellog(self, interaction: discord.Interaction):
        serverConfig = await fetch_config(interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.logPermissionRole))):
            errEmbed = embedBuilder("err", embedTitle="Permission error:",
                                    embedDesc="You are not: <@&" + str(serverConfig.logPermissionRole) + ">")
            return await interaction.response.send_message(embed=errEmbed)
            
        requestedOperator = await getOperator(int(interaction.user.id))
        log, logResponse = await checkLog(interaction)
        if not requestedOperator:
            errEmbed = embedBuilder("err", embedTitle="Operative not found!",
                                    embedDesc="Please make sure you are regsitered with the TRU bot before running commands!")
            await interaction.response.send_message(embed=errEmbed)
        if not logResponse:
            errEmbed = embedBuilder("err", embedTitle="Log not found!",
                                    embedDesc="No active log was found under your operative id.")
            await interaction.response.send_message(embed=errEmbed)
        if logResponse:
            print("Found a log")
            await prismaCancelLog(interaction)
            successEmbed = embedBuilder("err", embedTitle="Log cancelled.",
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
    
    @app_commands.command(name="viewstatus",description="View someones current quota status.")
    async def mypoints(self, interaction: discord.Interaction, member:discord.Member=None):
        await interaction.response.defer(thinking=True)
        try:
            if member==None:
                member = interaction.user
            
            requested_operator = await getOperator(member.id)
            operator_logs = await getallLogs(member)
            quotaBlock = await get_quotablock()
            comments = get_card_comments(requested_operator.userName)
            #operator_quota = getrankQuota
            
            if requested_operator is None:
                return await interaction.edit_original_response(embed=embedBuilder("err", embedDesc=f"Unable to find userdata on {member.mention}. Maybe they aren't registered?", embedTitle="No data found!"))
            else:
                embed = embedBuilder("succ", embedTitle=f"<:trubotAccepted:1096225940578766968> User data found!", embedDesc=f"Displaying {member.mention}'s data for block **{quotaBlock.blockNum}**.")
                embed.add_field(name="TRU Rank", value=f"> {requested_operator.rank}", inline=True)
                embed.add_field(name="Activity Status", value=f"> On Leave of Absence" if userOnLoA(member) else f"> Active Duty", inline=True)
                embed.add_field(name="", value="", inline=False) # Filler for 2x2 field config because discord
                embed.add_field(name="Responses Attended", value=f"> {get_comments_timeframe(comments, quotaBlock.unix_starttime)}", inline=True) # Need to add response attendance count
                embed.add_field(name="Patrols Logged", value=f"> {len(operator_logs)}/Quota", inline=True) #(need to add something and be able to change quota at will)
                return await interaction.edit_original_response(embed=embed)
        except Exception as e:
            errEmbed = embedBuilder("err", embedDesc=str(e), embedTitle="An error occurred.")
            return await interaction.edit_original_response(embed=errEmbed, ephemeral=True)
                

class quotaCmds(commands.GroupCog, group_name='quota'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        

    @app_commands.command(name="set", description="Updates specified activity requirement for specified rank.")
    async def set_quota(self, interaction: discord.Interaction, rank: discord.Role, patrol_req: int = None, response_req: int = None, quota_active: bool = None):
        serverConfig = await fetch_config(interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.commandRole))):
            return await interaction.response.send_message(embed = embedBuilder(responseType="perms", embedDesc="Only TRU leadership and above may use this command."), ephemeral=True)

        rank_name = rank.name
        db = Prisma()
        # Retrieve the existing quota data for the specified rank
        existing_quota = await db.quotas.find_unique(where={"rankName": rank_name})

        if existing_quota is None:
            return await interaction.response.send_message(embed = embedBuilder(responseType="err", embedTitle="No quota found", embedDesc=f"No quota data found for the rank {rank.name}."), ephemeral=True)

        # Update the quota data with the provided values
        new_quota_data = {}
        if patrol_req is not None:
            new_quota_data["logRequirement"] = str(patrol_req)
        if response_req is not None:
            new_quota_data["responseRequirement"] = str(response_req)
        if quota_active is not None:
            new_quota_data["quotaActive"] = quota_active

        updated_quota = await db.quotas.update(where={"rankName": rank_name}, data=new_quota_data)

        return await interaction.response.send_message(embed=embedBuilder(responseType="succ", embedTitle="Quota Updated", embedDesc=f"The quota requirements for the rank {rank.name} have been updated successfully."), ephemeral=True)
    
    @app_commands.command(name="overview",description="View all set quotas for all ranks.")
    async def viewquota(self, interaction:discord.Interaction):
        return await interaction.response.send_message(embed=embedBuilder("warn", embedDesc="This command isn't done yet.", embedTitle="No worki yeti"), ephemeral=True)
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
        return await interaction.response.send_message(embed=embedBuilder("warn", embedDesc="This command isn't done yet.",embedTitle="No worki yeti"), ephemeral=True)
        # Will work on after some sleep but needs a DB integration

