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
    
class viewdataCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.client = bot
    
    @app_commands.command(name="quotastatus",description="View your own of someone else's current quota status.")
    @app_commands.describe(member="Who's quota activity you would like to view. [Optional]", quota_block="From which quota block you'd like to see the activity from.")
    async def quota_status(self, interaction: discord.Interaction, member:discord.Member=None, quota_block:str=None):
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
                
        
                # Check if quota_block is provided and valid
                if quota_block:
                    try:
                        quota_block = int(quota_block)
                    except ValueError:
                        quota_block = None
                            # If quota_block is provided and valid, get the specific quota block
                
                if quota_block:
                    quotaBlock = await get_quotablock(block_num=quota_block)
                    if not quotaBlock:
                        return await interaction.edit_original_response(embed=embedBuilder("err", embedDesc=f"Quota block {quota_block} not found.", embedTitle="Invalid quota block"))     

                if not quota_block or not quotaBlock:
                    quotaBlock = await get_quotablock()
                
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




