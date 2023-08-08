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
        
    @app_commands.command(name="delete", description="Delete a log by ID.")
    async def deletelog(self, interaction: discord.Interaction, log_id: str):
        if not DEVACCESS(interaction.user):
            errEmbed = embedBuilder("perms", embedDesc="This command is limited to Bot Developers.")
            await interaction.response.send_message(embed=errEmbed)
            return

        try:
            db = Prisma()
            await db.connect()
            log = await db.logs.find_unique(where={'logID': log_id})
            if log:
                await db.logs.delete(where={'logID': log_id})
                successEmbed = embedBuilder("succ", embedTitle="Log deleted!", embedDesc=f"A log with ID `{log_id}` has been deleted.")
                await interaction.response.send_message(embed=successEmbed)
            else:
                errEmbed = embedBuilder("err", embedTitle="Log not found!", embedDesc="No log was found with the specified ID.")
                await interaction.response.send_message(embed=errEmbed)
        except Exception as e:
            errEmbed = embedBuilder("err", embedTitle="Error!", embedDesc=str(e))
            await interaction.response.send_message(embed=errEmbed)

        
    @app_commands.command(name="start", description="Start a log.")
    async def startlog(self, interaction: discord.Interaction):
        serverConfig = await fetch_config(interaction=interaction)
        if checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.logPermissionRole))):
            requestedOperator = await getOperator(int(interaction.user.id))
            if requestedOperator.activeLog == True:
                return await interaction.response.send_message(embed = embedBuilder(responseType="warn", embedTitle="Process denied!", embedDesc="You still have an on-going log."))      
                      
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
            errEmbed = embedBuilder("perms",
                                    embedDesc="Only Operators and above may use this command.")
            await interaction.response.send_message(embed=errEmbed)

    @app_commands.command(name="end", description="End your current log.")
    async def endlog(self, interaction: discord.Interaction, proof_url:str = None, proof_img:discord.Attachment=None):
        serverConfig = await fetch_config(interaction)
        requestedOperator = await getOperator(int(interaction.user.id))
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.logPermissionRole))):
            errEmbed = embedBuilder("perms", embedDesc="Only Operators and above may use this command.")
            await interaction.response.send_message(embed=errEmbed)
            return
        if not requestedOperator:
            errEmbed = embedBuilder("err", embedTitle="Operative not found!", embedDesc="Please make sure you/they are registered with the TRU bot before running commands!")
            return await interaction.response.send_message(embed=errEmbed, ephemeral=True)

        proof = proof_url if proof_url else proof_img.url if proof_img else None
        
        if proof is None:
            errEmbed = embedBuilder("err", embedTitle="No Proof Provided!", embedDesc="Please provide either a proof URL or an proof image.")
            return await interaction.response.send_message(embed=errEmbed, ephemeral=True)

        date_time = datetime.now()
        unixTime = int(time.mktime(date_time.timetuple()))
        

        dbMessage, dbSuccess = await prismaEndLog(interaction, str(unixTime), proof)

        if dbSuccess:
            successEmbed = embedBuilder("succ", embedTitle="Log ended!", embedDesc="Your patrol has successfully ended! *Thank you for patrolling!*")
            await interaction.response.send_message(embed=successEmbed)
        else:
            errorEmbed = embedBuilder("err", embedTitle="Unable to end log!", embedDesc="**Reason:** " + str(dbMessage))
            await interaction.response.send_message(embed=errorEmbed, ephemeral=True)

    @app_commands.command(name="cancel", description="Cancel current log.")
    async def cancellog(self, interaction: discord.Interaction):
        serverConfig = await fetch_config(interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.logPermissionRole))):
            errEmbed = embedBuilder("perms",
                                    embedDesc="Only Operators and above may use this command.")
            return await interaction.response.send_message(embed=errEmbed)
            
        requestedOperator = await getOperator(int(interaction.user.id))
        log, logResponse = await checkLog(interaction)
        if not requestedOperator:
            errEmbed = embedBuilder("err", embedTitle="Operator not found!",
                                    embedDesc="Please make sure you are regsitered with the TRU bot before running commands!")
            await interaction.response.send_message(embed=errEmbed)
        if not logResponse:
            errEmbed = embedBuilder("err", embedTitle="Log not found!",
                                    embedDesc="No active log was found under your id.")
            await interaction.response.send_message(embed=errEmbed)
        if logResponse:
            await prismaCancelLog(interaction)
            successEmbed = embedBuilder("succ", embedTitle="Log cancelled!",
                                        embedDesc="Successfully deleted your patrol!")
            await interaction.response.send_message(embed=successEmbed)
            
    

    @app_commands.command(name="overview", description="See a specific or 10 of your most recent patrols.")
    @app_commands.describe(operator="Which operator's logs? [TRUCapt+]", log_id = "The ID of the log to show info about.")
    async def logoverview(self, interaction: discord.Interaction, operator:discord.Member = None, log_id:str = None):
        serverConfig = await fetch_config(interaction)
        if operator and not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.commandRole))):
            return await interaction.response.send_message(embed = embedBuilder(responseType="perms", embedDesc="Only TRU leadership and above may view the logs of others."), ephemeral=True)
       
        
        if operator is None:
            operator = interaction.user
        requestedOperator = await getOperator(operator.id)
        if not requestedOperator:
            return await interaction.response.send_message(embed = embedBuilder(responseType="err", embedTitle="Operator not found...", embedDesc=f"{operator.mention} was not found in the database. Please double check that they are registered."))
        
        if log_id:
            # Fetch information about a specific log
            if checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.commandRole))):
                log = await fetch_log_by_id(log_id)
                acc = True
            else:
                log = await fetch_log_by_id_for_user(operator, log_id)
                acc = False
                
            if log:
                embed = embedBuilder("succ", embedTitle=f"Log found!")
                if not log.timeEnded or str(log.timeEnded) == "Null":
                    time_elapsed = (datetime.fromtimestamp(int(time.time())) - datetime.fromtimestamp(int(log.timeStarted))).total_seconds() // 60
                    embed.add_field(name=f"Log `{log.logID}`", value=f"Started: <t:{log.timeStarted}>\nTime Elapsed: `{int(time_elapsed)} minutes`\nStatus: *In progress*")
                elif not log.logProof or str(log.logProof) == "Null" or str(log.logProof) == "No proof provided":
                    embed.add_field(name=f"Log `{log.logID}`", value=f"Started: <t:{log.timeStarted}>\nEnded: <t:{log.timeEnded}>\nLength: `{round(float(log.timeElapsed))} minutes`\nProof: *No proof provided*")
                else:
                    embed.add_field(name=f"Log `{log.logID}`", value=f"Started: <t:{log.timeStarted}>\nEnded: <t:{log.timeEnded}>\nLength: `{round(float(log.timeElapsed))} minutes`\nProof: [image]({log.logProof})")
                return await interaction.response.send_message(embed=embed)
            else:
                if acc == True:
                    return await interaction.response.send_message(embed = embedBuilder("err", embedTitle="No log found!", embedDesc=f"Could not find a patrol with id `{log_id}`."), ephemeral=True)
                else:
                    return await interaction.response.send_message(embed = embedBuilder("warn", embedTitle="No log found!", embedDesc=f"This is either the log id of another operator or I could not find a patrol with id `{log_id}`."), ephemeral=True)
        
        else:
            # Fetch the last 5 logs for the specified operator
            logs = await get_last_5_logs_for_user(operator.id)

            if not logs:
                return await interaction.response.send_message(embed = embedBuilder("warn", embedTitle="No logs found!", embedDesc=f"Could not find any patrols for {operator.mention}."), ephemeral=True)
            else:
                embed = embedBuilder("succ", embedTitle=f"Logs found!")
                for log in logs:
                    if not log.timeEnded or str(log.timeEnded) == "Null":
                        time_elapsed = (datetime.fromtimestamp(int(time.time())) - datetime.fromtimestamp(int(log.timeStarted))).total_seconds() // 60
                        embed.add_field(name=f"Log `{log.logID}`", value=f"Started: <t:{log.timeStarted}>\nTime Elapsed: `{int(time_elapsed)} minutes`\nStatus: *In progress*")
                    elif not log.logProof or str(log.logProof) == "Null" or str(log.logProof) == "No proof provided":
                        embed.add_field(name=f"Log `{log.logID}`", value=f"Started: <t:{log.timeStarted}>\nEnded: <t:{log.timeEnded}>\nLength: `{round(float(log.timeElapsed))} minutes`\nProof: *No proof provided*")
                    else:
                        embed.add_field(name=f"Log `{log.logID}`", value=f"Started: <t:{log.timeStarted}>\nEnded: <t:{log.timeEnded}>\nLength: `{round(float(log.timeElapsed))} minutes`\nProof: [image]({log.logProof})")
                return await interaction.response.send_message(embed=embed)
        
    
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
            
            if requested_operator is None:
                return await interaction.edit_original_response(embed=embedBuilder("err", embedDesc=f"Unable to find userdata on {member.mention}. Maybe they aren't registered?", embedTitle="No user found!"))
            
            else:
                operator_logs = await getallLogs(member)
                quotaBlock = await get_quotablock()
                comments = get_card_comments(requested_operator.userName)
                operator_quota = await get_quota_by_rank(requested_operator.rank)
                if comments is False:
                    responses_attended = f"No card named \n`{requested_operator.userName}` found!"
                else:
                    responses_attended = f"> {get_comments_timeframe(comments, quotaBlock.unix_starttime)}/{operator_quota.responseRequirement}" \
                                        if operator_quota and (operator_quota.responseRequirement and operator_quota.quotaActive is True and str(operator_quota.responseRequirement) != "None") \
                                        and userOnLoA(member) is False \
                                        else f"> {get_comments_timeframe(comments, quotaBlock.unix_starttime)}"
                    
                
                
                embed = embedBuilder("succ", embedTitle=f"User found!", embedDesc=f"Displaying {member.mention}'s data for block **{quotaBlock.blockNum}**.")
                embed.add_field(name="TRU Rank", value=f"> {requested_operator.rank}", inline=True)
                embed.add_field(name="Activity Status", value=f"> On Leave of Absence" if userOnLoA(member) else f"> On Active Duty", inline=True)
                embed.add_field(name="", value="", inline=False) # Filler for 2x2 field config because discord
                embed.add_field(name="Responses Attended",
                                value=responses_attended,
                                inline=True)

                embed.add_field(name="Patrols Logged",
                                value=f"> {len(operator_logs)}/{operator_quota.logRequirement}"
                                if operator_quota and (operator_quota.logRequirement and operator_quota.quotaActive is True and str(operator_quota.logRequirement) != "None")
                                and userOnLoA(member) is False
                                else f"> {len(operator_logs)}",
                                inline=True)

                return await interaction.edit_original_response(embed=embed)
        except Exception as e:
            errEmbed = embedBuilder("err", embedDesc=str(e), embedTitle="An error occurred.")
            return await interaction.edit_original_response(embed=errEmbed)
                


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

        # Update the quota data with the provided values
        new_quota_data = {}
        if patrol_req is not None:
            new_quota_data["logRequirement"] = str(patrol_req)
        else:
            new_quota_data["logRequirement"] = None
        if response_req is not None:
            new_quota_data["responseRequirement"] = str(response_req)
        else:
            new_quota_data["responseRequirement"] = None
        if quota_active is not None:
            new_quota_data["quotaActive"] = quota_active
        else:
            new_quota_data["quotaActive"] = None

        updated_quota = await upsert_quota(rank_name, new_quota_data)

        return await interaction.response.send_message(embed=embedBuilder(responseType="succ", embedTitle="Quota Updated!", embedDesc=f"The quota requirements for the rank {rank.name} have been updated successfully."), ephemeral=True)
    
    @app_commands.command(name="overview", description="View all set quotas for all ranks.")
    async def viewquota(self, interaction: discord.Interaction, rank:discord.Role=None):
        try:
            if rank:
                quotas = await get_quota_by_rank(rank.name)
                quotas = [quotas] if quotas else []
            else:
                quotas = await get_all_quotas()

            if len(quotas) > 0:
                quota_list = embedBuilder(responseType="cust", embedTitle="TRU Quotas", embedColor=TRUCommandCOL)
                for quota in quotas:
                    if quota.quotaActive == True:
                        active = "Active"
                    else:
                        active = "Inactive"
                    quota_list.add_field(name=f"➣ {quota.rankName} | {active}", value=f"> Log Requirement: {quota.logRequirement}\n> Response Requirement: {quota.responseRequirement}", inline=False)
                await interaction.response.send_message(embed=quota_list, ephemeral=True)
            else:
                await interaction.response.send_message(embed = embedBuilder("warn", embedTitle="Quota not set!", embedDesc=f"Unable to find a quota for {rank.mention}." if rank else "No quotas were found in the database."), ephemeral=True)
        except Exception as e:
            errEmbed = embedBuilder(responseType="err", embedDesc=str(e))
            await interaction.response.send_message(embed=errEmbed, ephemeral=True)
            
    @app_commands.command(name="delete", description="Delete a quota for a specified rank.")
    async def delete_quota(self, interaction: discord.Interaction, rank: discord.Role):
        serverConfig = await fetch_config(interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.commandRole))):
            return await interaction.response.send_message(embed=embedBuilder(responseType="perms", embedDesc="Only TRU leadership and above may use this command."), ephemeral=True)

        rank_name = rank.name
        deleted_quota = await delete_quota(rank_name)

        if deleted_quota is not None:
            return await interaction.response.send_message(embed=embedBuilder(responseType="succ", embedTitle="Quota Deleted!", embedDesc=f"The quota for the rank {rank_name} has been deleted successfully."), ephemeral=True)
        else:
            return await interaction.response.send_message(embed=embedBuilder(responseType="err", embedTitle="Quota Not Found!", embedDesc=f"No quota found for the rank {rank_name}."), ephemeral=True)


class quotablockCommands(commands.GroupCog, group_name='quotablock'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="setactive", description="Set the active quota block by block number.")
    async def set_active_block(self, interaction: discord.Interaction, block_num: int):
        serverConfig = await fetch_config(interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.commandRole))):
            return await interaction.response.send_message(embed=embedBuilder(responseType="perms", embedDesc="Only TRU leadership and above may use this command."), ephemeral=True)

        await set_active_block(block_num)
        return await interaction.response.send_message(embed=embedBuilder(responseType="succ", embedTitle="Active Quota Block Updated!", embedDesc=f"The active quota block has been updated to block number {block_num}."), ephemeral=True)

    @app_commands.command(name="overview", description="View all quota blocks.")
    async def view_quota_blocks(self, interaction: discord.Interaction):
        try:
            quota_blocks = await get_all_quota_data()

            if len(quota_blocks) > 0:
                quota_blocks_list = embedBuilder(responseType="cust", embedTitle="TRU Quota Blocks", embedColor=TRUCommandCOL)
                for block in quota_blocks:
                    block_active = "Active" if block.blockActive else "Inactive"
                    quota_blocks_list.add_field(name=f"➣ Block Number {block.blockNum} | Active" if block.blockActive is True else f"➣ Block Number {block.blockNum}", value=f"<t:{block.unix_starttime}> - <t:{block.unix_endtime}>", inline=False)
                await interaction.response.send_message(embed=quota_blocks_list, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embedBuilder("warn", embedTitle="No Quota Blocks Found!", embedDesc="No quota blocks were found in the database."), ephemeral=True)
        except Exception as e:
            errEmbed = embedBuilder(responseType="err", embedDesc=str(e))
            await interaction.response.send_message(embed=errEmbed, ephemeral=True)

    @app_commands.command(name="get", description="Get a specific of the active quota block.")
    @app_commands.describe(block="Blocks 1-17 are available.")
    async def get_active_block(self, interaction: discord.Interaction, block:int=None):
        try:
            active_block = await get_quotablock(block_num=block)
            if active_block:
                active_block_info = embedBuilder(responseType="succ", embedTitle="Quota Block found!")
                block_active = "Active" if active_block.blockActive else "Inactive"
                active_block_info.add_field(name=f"➣ Block Number {active_block.blockNum} | {block_active}", value=f"<t:{active_block.unix_starttime}> - <t:{active_block.unix_endtime}>", inline=False)
                await interaction.response.send_message(embed=active_block_info, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embedBuilder("warn", embedTitle="No data found!", embedDesc="Your requested quota block was not found in the database."), ephemeral=True)
        except Exception as e:
            errEmbed = embedBuilder(responseType="err", embedDesc=str(e))
            await interaction.response.send_message(embed=errEmbed, ephemeral=True)




