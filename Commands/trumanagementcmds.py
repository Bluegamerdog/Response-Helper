import discord
import os
import sys
import datetime
import random
from Functions.mainVariables import *
from Functions.permFunctions import *
from Functions.formattingFunctions import embedBuilder
from Functions.randFunctions import (get_user_id_from_link, in_roblox_group, change_nickname)
#from Database_Functions.UserdbFunction import (db_register_get_data)
from discord.ext import commands
from discord import app_commands
from discord import ui
from roblox import *
import Database_Functions.PrismaFunctions as dbFuncs

roblox = Client("_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_D5064A0C1DB1D5FD5C66ED677C3B797A10523AEE48D18912BB5D6F2E08BE04F39C4E056585CDE8C410971D4BE9C674A66E86C9BD29BBC99B41A5720149F0C5B2C16FF8088846DDB8004B1C206F0B3FB837A4263111612CA93E448C7AC999EC9D326AB762CB74A7BB0B8D246F192BAC4C5139D77CC634D9C3F06A836D43712B6FA65E7DD315AB471C41A0CDD683A633624BFE8A91DD3BA85F34612556A0525401AD16743318C61B208D1A894FFAB372E157342BF65B78E06FB33543F74A8A600256582EBA8A56062BEA431246332E270A4EA1F77B811BBB7678C3A10020251B8FBF3D015BD391A219400A803A9A07B5B971785639B08E9F1E85230E630D7D1680E1AA7D9815C4C9DA3D9FE5064EFECDB50123CD8E6E7A7527624721D77F7D2542B833E49C14F35356C57F74AF16B4A2E553BBB56B1398F7F8F8F4E141C149D7499DE92ABFDA759F3634D395FB1333BC1F2709919B573DE87E1ED3412022B26BEF5544DD44F23BFE968E6BA37DCCDA3B87060A1930")    

## Needs a rework still ##
## -> Waiting on roblox group as well
## Commands turned into comments had broken functions and need a rework

class quotaCmds(commands.GroupCog, group_name='quota'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
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
        
    
    

    
class managementCmds(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    ## TRU MANAGEMENT ##
    
    @app_commands.command(name="rank", description="Used to promote/demoted TRU members.")
    @app_commands.describe(member="Who are you ranking?", rank="To what rank?", reason="[DEMOTIONS ONLY] Why are they being demoted?")
    @app_commands.choices(rank=[
    app_commands.Choice(name="totally real rank", value="25"),
    app_commands.Choice(name="Elite Vanguard", value="20"),
    app_commands.Choice(name="Vanguard", value="15"),
    app_commands.Choice(name="Elite Operator", value="5"),
    app_commands.Choice(name="Senior Operator", value="4"),
    app_commands.Choice(name="Operator", value="3"),
    app_commands.Choice(name="Entrant", value="2"),])
    async def trurank_user(self, interaction:discord.Interaction, member:discord.Member, rank:app_commands.Choice[str], reason:str=None):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.commandRole))):
            return await interaction.response.send_message(embed=discord.Embed(title="<:trubotDenied:1099642433588965447> Missing permission!", description="Only TRU leadership and above may use this command.", color=ErrorCOL))
        ranked_operative = await dbFuncs.viewOperative(member.id)
        if ranked_operative == None:
            return await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, description=f"<:trubotDenied:1099642433588965447> {member.mention} was not found in the registry."), ephemeral=True)
        requested_rank = await dbFuncs.fetch_rolebind(robloxID=int(rank.value))
        if not requested_rank:
            return await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, title="<:trubotDenied:1099642433588965447> Rolebind/Rank Error!", description=f"Could not find a rolebind for the requested rank!\n`Rank details: Specified Roblox role ID '{rank.value}' and rank name '{rank.name}' are not binded`"), ephemeral=True)
        current_rank = await dbFuncs.fetch_rolebind(rankName=ranked_operative.rank)
        if not current_rank:
            return await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, title="<:trubotDenied:1099642433588965447> Rolebind/Rank Error!", description=f"Could not find a rolebind for {member.mention}'s current rank!\n`Rank without rolebind: '{ranked_operative.rank}'`"), ephemeral=True)
        #Ranking Errors
        if int(current_rank.RobloxRankID) == int(requested_rank.RobloxRankID):
            return await interaction.response.send_message(embed=discord.Embed(title="<:trubotDenied:1099642433588965447> Ranking Error!", description=f"{member.mention} is already ranked as **{requested_rank.rankName}**.", color=ErrorCOL), ephemeral=True)
        if int(current_rank.RobloxRankID) >= 250 and int(requested_rank.RobloxRankID) < 250: #hehe
            return await interaction.response.send_message(embed=discord.Embed(title="<:trubotDenied:1099642433588965447> Permission Error!", description=f"Blue said I can't demote TRU Leadership or above. {member.mention} is a member of TRU Leadership or above.", color=ErrorCOL))
        #Roblox Group
        TRU_ROBLOX_group = await roblox.get_group(15155175)
        group_members = await TRU_ROBLOX_group.get_members().flatten()
        roblox_user = await roblox.get_user(get_user_id_from_link(ranked_operative.profileLink))
        if in_roblox_group(group_members, roblox_user) is False:
            return await interaction.response.send_message(embed=discord.Embed(title="<:trubotDenied:1099642433588965447> ROBLOX Group Error!", description=f"Could not find {member.mention} to be a member of the `{TRU_ROBLOX_group.name}` ROBLOX group. ([ROBLOX Group Link](https://www.roblox.com/groups/15155175/QSO-Tactical-Response-Unit))", color=ErrorCOL), ephemeral=True)
        
        #Defer
        await interaction.response.defer(thinking=True, ephemeral=True)
        logs_channel = interaction.guild.get_channel(1095835491485622323) #Audit Logs
        tru_on_duty_channel = interaction.guild.get_channel(1096216219192926248) #bot-testing 
        
        #Promotion
        if int(current_rank.RobloxRankID) < int(requested_rank.RobloxRankID):
            try:
                await member.edit(nick=change_nickname(requested_rank.rankName, member.display_name))
                await member.add_roles(interaction.guild.get_role(int(requested_rank.discordRoleID)))
                await member.remove_roles(interaction.guild.get_role(int(current_rank.discordRoleID)))
                updated_operative = await dbFuncs.updateOperative_rank(member, requested_rank.rankName)
                await TRU_ROBLOX_group.get_member(roblox_user.id).set_rank(int(requested_rank.RobloxRankID))
                #print(updated_operative)
                dm_notification = discord.Embed(title="<a:trubotCelebration:1099643172012949555> TRU Promotion!", description=f"You have been promoted from **{current_rank.rankName}** to **{requested_rank.rankName}**!\n\nRank Specific Information:\n> TBA", color=DarkGreenCOL)
                dm_notification.set_footer(icon_url=interaction.user.avatar, text=f"Processed by {interaction.user.display_name}  •  {datetime.datetime.now().strftime('%d.%m.%y')}")
                audit_log = discord.Embed(title="<:trubotWarning:1099642918974783519> User Promoted!", description=f"{member.mention} was promoted from **{current_rank.rankName}** to **{requested_rank.rankName}**.", color=HRCommandsCOL)
                audit_log.set_footer(icon_url=interaction.user.avatar, text=f"Processed by {interaction.user.display_name}  •  {datetime.datetime.now().strftime('%d.%m.%y')}")
                await logs_channel.send(embed = audit_log)
                await member.send(embed=dm_notification)
                await tru_on_duty_channel.send(f"Please congragulate **{member.display_name}** on their promotion to **{requested_rank.rankName}**! <a:trubotCelebration:1099643172012949555>")
                return await interaction.edit_original_response(embed=discord.Embed(title="<:trubotAccepted:1096225940578766968> Promotion Successful!", description=f"{member.mention} has been promoted from **{current_rank.rankName}** to **{requested_rank.rankName}**.", color=SuccessCOL))
            except Exception as e:
                print(e)
                embed = discord.Embed(title="<:trubotDenied:1099642433588965447> Promotion Error!", description=f"{e}", color=ErrorCOL)
                return await interaction.edit_original_response(embed=embed, ephemeral=True)
        
        #Demotions
        elif int(current_rank.RobloxRankID) > int(requested_rank.RobloxRankID):
            try:
                await member.edit(nick=change_nickname(requested_rank.rankName, member.display_name))
                await member.add_roles(interaction.guild.get_role(int(requested_rank.discordRoleID)))
                await member.remove_roles(interaction.guild.get_role(int(current_rank.discordRoleID)))
                updated_operative = await dbFuncs.updateOperative_rank(member, requested_rank.rankName)
                await TRU_ROBLOX_group.get_member(roblox_user.id).set_rank(int(requested_rank.RobloxRankID))
                #print(updated_operative)
                dm_notification = discord.Embed(title="<:trubotWarning:1099642918974783519> TRU Demotion!", description=f"You have been demoted from **{current_rank.rankName}** to **{requested_rank.rankName}**.\n\n**Reason:** {reason}", color=DarkRedCOL)
                dm_notification.set_footer(icon_url=interaction.user.avatar, text=f"Processed by {interaction.user.display_name}  •  {datetime.datetime.now().strftime('%d.%m.%y')}")
                audit_log = discord.Embed(title="<:trubotWarning:1099642918974783519> User Demoted!", description=f"{member.mention} was demoted from **{current_rank.rankName}** to **{requested_rank.rankName}**.\n\n**Reason:** {reason}", color=HRCommandsCOL)
                audit_log.set_footer(icon_url=interaction.user.avatar, text=f"Processed by {interaction.user.display_name}  •  {datetime.datetime.now().strftime('%d.%m.%y')}")
                await logs_channel.send(embed = audit_log)
                await member.send(embed=dm_notification)
                return await interaction.edit_original_response(embed=discord.Embed(title="<:trubotAccepted:1096225940578766968> Demotion Successful!", description=f"{member.mention} has been demoted from **{current_rank.rankName}** to **{requested_rank.rankName}**.", color=SuccessCOL))
            except Exception as e:
                print(e)
                embed = discord.Embed(title="<:trubotDenied:1099642433588965447> Demotion Error!", description=f"{e}", color=ErrorCOL)
                return await interaction.edit_original_response(embed=embed, ephemeral=True)
            
        else:
            return print("Bro I think you majorly missed something...")
  
    @app_commands.command(name="truaccept", description="Used to accept new TRU members into the roblox group.")
    async def truaccept_group(self, interaction:discord.Interaction, member:discord.Member):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.commandRole))):
            return await interaction.response.send_message(embed=discord.Embed(title="<:trubotDenied:1099642433588965447> Missing permission!", description="Only TRU leadership and above may use this command.", color=ErrorCOL))
        try:
            username = str(member.display_name).split()[-1]
            group = await roblox.get_group(15155175)
            user = await roblox.get_user_by_username(username)
            await group.accept_user(user)
            await interaction.response.send_message(embed=discord.Embed(color=TRUCommandCOL, title=f"<:trubotAccepted:1096225940578766968> Accepted {username}!"), ephemeral=True)
            await member.send(embed = discord.Embed(description=f"Your request to join the `QSO Tactical Response Unit` Roblox group has been accepted! <:trubotTRU:1096226111458918470>", color=TRUCommandCOL))
        except Exception as e:
            print(e)
            await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Error!", description=f"An error occurred while accepting {username}: {str(e)}"), ephemeral=True)
    '''
    @app_commands.command(name="trukick", description="Used to kick TRU members.")
    async def trukick_user(self, interaction:discord.Interaction, member:discord.Member, reason:str):
        if not TRULEAD(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotDeny:1073668785262833735> Missing Permission!", description=f"You must be a member of TRUPC or above to use this command."), ephemeral=True)
        try:
            username = str(member.display_name).split()[-1] 
            group = await roblox.get_group(15155104) # Currently DSB
            user = await roblox.get_user_by_username(username)
            logsch = self.bot.get_channel(1096146385830690866) # Currently #startup || 1008449677210943548 #audit-logs
            kickembed = discord.Embed(title=f"<:TRU:1060271947725930496> Kicked TRU Member", description=f"{member.mention} has been kicked from TRU by {interaction.user.mention}.\n\n**Reason:** {reason}", color=DarkRedCOL)
            kickembed.set_thumbnail(url=member.avatar.url)
            kickembed.set_footer(text=f"ID: {member.id} • {datetime.datetime.now().strftime('%m/%d/%Y %H:%M %p')}")
            logmsg = await logsch.send(embed=kickembed)
            await interaction.response.send_message(embed = discord.Embed(title=f"<:trubotAccepted:1096225940578766968> Member removed", description=f"Successfully removed {member.mention} from TRU.\n\n**Reason:** {reason}\n→ [Audit Log]({logmsg.jump_url})", color=DarkRedCOL))
            await member.send(embed = discord.Embed(title=f"You have been kicked from Defensive Squadron Bravo.",description=f"**Reason:** {reason}", color=DarkRedCOL))
            await group.kick_user(user)
            await member.kick(reason=reason)
        except Exception as e:
            print(e)
            await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Error!", description=f"An error occurred while accepting {username}: {str(e)}"), ephemeral=True)        

    @app_commands.command(name="trustrike", description="Give out strikes in TRU.")
    async def trustrike_user(self, interaction:discord.Interaction, member:discord.Member, reason:str):
        if not TRULEAD(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotDeny:1073668785262833735> Missing Permission!", description=f"You must be a member of TRUPC or above to use this command."), ephemeral=True)
        else:
            strikeemb = discord.Embed(title=f"<:TRU:1060271947725930496> Striked TRU Member", description=f"{member.mention} has recieved a strike in TRU from {interaction.user.mention}.\n\n**Reason:** {reason}", color=DarkRedCOL)
            #strikeemb.set_thumbnail(url=member.avatar.url)
            strikeemb.set_footer(text=f"ID: {member.id} • {datetime.datetime.now().strftime('%m/%d/%Y %H:%M %p')}")
            logsch = self.bot.get_channel(1054705433971003412) # 1008449677210943548 #audit-logs
            logmsg = await logsch.send(embed=strikeemb)
            await interaction.response.send_message(embed = discord.Embed(title=f"<:trubotAccepted:1096225940578766968> Member striked", description=f"Successfully striked {member.mention}.\n\n**Reason:** {reason}\n→ [Audit Log]({logmsg.jump_url})", color=DarkRedCOL))
            await member.send(embed = discord.Embed(title=f"You have received a strike in Defensive Squadron Bravo.",description=f"**Reason:** {reason}", color=DarkRedCOL))
            pass
    
    @app_commands.command(name="trustrikes", description="See a users moderation history in TRU.")
    async def trustrikesview_user(self, interaction:discord.Interaction, member:discord.Member=None):
        if member == None:
            member = interaction.user
        if member != interaction.user and TRULEAD(interaction.user) == False:
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotDeny:1073668785262833735> Missing Permission!", description=f"You must be a member of TRUPC or above to view someone else's strikes."), ephemeral=True)
        else:
            # Get the user's warnings from the database
            warnings = None #await self.db.get_warnings(member.id)
            if not warnings:
                return await interaction.response.send_message(
                    embed=discord.Embed(
                        title="<:trubotAbstain:1099642858505515018> No warnings found",
                        description=f"No warnings found for {member.mention}.",
                        color=DarkRedCOL
                    )
                )

            # Create the embed to display the warnings
            embed = discord.Embed(title=f"Warnings for {member}", color=TRUCommandCOL)
            for i, warn in enumerate(warnings):
                embed.add_field(name=f"Warning {i+1}",value=f"**Reason:** {warn['reason']}\n**Moderator:** {await self.bot.fetch_user(warn['moderator'])}\n**Date:** {warn['date'].strftime('%m/%d/%Y %I:%M %p')}"
                )

            await interaction.response.send_message(embed=embed)
    '''        
        




