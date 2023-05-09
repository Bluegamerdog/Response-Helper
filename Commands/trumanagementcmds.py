import discord
import os
import sys
import datetime
import random
from Functions.mainVariables import *
from Functions.permFunctions import *
from Functions.formattingFunctions import embedBuilder
from Functions.randFunctions import (get_user_id_from_link)
from Database_Functions.UserdbFunction import (db_register_get_data)
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
    @app_commands.choices(rank=[
    app_commands.Choice(name="Elite Vanguard", value="20"),
    app_commands.Choice(name="Vanguard", value="15"),
    app_commands.Choice(name="Elite Operator", value="5"),
    app_commands.Choice(name="Senior Operator", value="4"),
    app_commands.Choice(name="Operator", value="3"),
    app_commands.Choice(name="Entrant", value="2"),])
    async def trurank_user(self, interaction:discord.Interaction, member:discord.Member, rank:app_commands.Choice[str]):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.commandRole))):
            return await interaction.response.send_message(embed=discord.Embed(title="Missing permission!", description="Only TRU leadership and above may use this command.", color=ErrorCOL))
        ranked_operative = await dbFuncs.viewOperative(member.id)
        if ranked_operative == None:
            return await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, description=f"<:trubotDenied:1099642433588965447> {member.mention} was not found in the registry."), ephemeral=True)
        requested_role = await dbFuncs.fetch_rolebind(int(rank.value))
        if not requested_role:
            return await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, description=f"<:trubotDenied:1099642433588965447> Unable to find rolebind for Roblox rank ID `{rank.value}` and `{rank.name}`"), ephemeral=True)
        await interaction.response.send_message(embed=discord.Embed(description=f"{requested_role}"))
        
        
        
        '''
        if not TRULEAD(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotDeny:1073668785262833735> Missing permissions!", description="You must be a member of TRUPC or above to use this command.", color=ErrorCOL), ephemeral=True)
        elif not TRUROLE(user):
            return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotDeny:1073668785262833735> Denied!", description="You can only rank TRU members.", color=ErrorCOL), ephemeral=True)
        else:
            userrank = getrank(user)
            if rank.value=="SSgt" and userrank[1] <=18:
                if userrank[1] == 18:
                    oldrank_role = discord.utils.get(interaction.guild.roles, name="Supervised Staff Sergeant")
                    newrank_role = discord.utils.get(interaction.guild.roles, name="Staff Sergeant")
                    await user.edit(nick=change_nickname("Staff Sergeant", user.display_name))
                    await user.add_roles(newrank_role)
                    await user.remove_roles(oldrank_role)
                    embed = discord.Embed(title="<:trubotAccepted:1096225940578766968> Congrats!", description=f"You can now host your own operations, without the need for supervision! <a:dsbbotCelebration:1084176617993162762>", color=SuccessCOL)
                    embed.set_footer(icon_url=interaction.user.avatar, text=f"Processed by {interaction.user.display_name}  •  {datetime.datetime.now().strftime('%d.%m.%y')}")
                    return await interaction.response.send_message(content=f"{user.mention}", embed=embed)
                else:
                    return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Rank Error!", description="You can only promote **Supervised Staff Sergeants** to **Staff Sergeant**.", color=ErrorCOL), ephemeral=True)
            data = db_register_get_data(user.id)
            newrank = changerank(rank.value)
                        
            if userrank[1] >= 252 or userrank==None:
                return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Unable!", description="I cannot rank members of TRU Pre-Command and above.", color=ErrorCOL), ephemeral=True)
            else:
                if userrank[1] == newrank[1]:
                    return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Already at that rank!", description=f"**{user.mention}** is already a **{userrank[0]}**.", color=ErrorCOL), ephemeral=True)
                elif newrank[1] > userrank[1]:   
                    #promote 
                    try:
                        
                        userrank_role = discord.utils.get(interaction.guild.roles, name=str(userrank[0]))
                        newrank_role = discord.utils.get(interaction.guild.roles, name=str(newrank[0]))
                        
                        group = await roblox.get_group(15155104)
                        await user.edit(nick=change_nickname(newrank[0], user.display_name))
                        if data:
                            await group.get_member(get_user_id_from_link(data[2])).set_rank(newrank[1])
                        else:
                            username = await roblox.get_user_by_username(str(user.display_name).split()[-1])
                            print(username.id)
                            success = await group.get_member(username.id).set_rank(newrank[1])
                            print(success)
                            if userrank[1] != 1:
                                await interaction.user.send(f"{user} was promoted, but not found in the database.")
                            else:
                                if rank.value == "PFC":
                                    await user.send(embed= discord.Embed(title="Congratulations on successfully passing your Private phase!", description=f"You are now a full-fledged operative of TRU who's ready to stand their ground in the face of danger. 🛡️\n\nNow that you're a Private First Class, be sure to register with me by running the command `/user register` in <#1058677991238008913> and follow the subsequent instructions.\n\nI will shortly add you to the <#1058758885361594378>. Here is where you will log your patrols to meet your points quota. All other information regarding logging patrols is in the pinned messages.\n\nLastly, be sure to request your 'Defensive Squadron Bravo' role in main QSO by pinging any online member of QSO Precommand in <#937473342716395543>.\n\nIf any of this information is unclear, don't hesitate to ping anyone in TRU management. <:TRU:1060271947725930496>", color=TRUCommandCOL))
                                    thread = self.bot.get_channel(1091329264764321843)
                                    ondutychannel = self.bot.get_channel(1091329185500381235)
                                    await thread.send(f"{user.mention}")
                                    await ondutychannel.send(f"Please congragulate **{user.display_name}** on passing their Private phase!")
                        await user.add_roles(newrank_role) 
                        await user.remove_roles(userrank_role)
                        if newrank[1] >= 18 and userrank[1] < 18:
                            mr_role = discord.utils.get(interaction.guild.roles, name="Operation Ringleader")
                            await user.add_roles(mr_role)
                        if newrank[1] >= 20 and userrank[1] < 20:
                            soup_role = discord.utils.get(interaction.guild.roles, name="Operation Supervisor")
                            await user.add_roles(soup_role)
                        embed = discord.Embed(title="<:trubotAccepted:1096225940578766968> Promotion!", description=f"You have been promoted from **{userrank[0]}** to **{newrank[0]}**! <a:dsbbotCelebration:1084176617993162762>", color=SuccessCOL)
                        embed.set_footer(icon_url=interaction.user.avatar, text=f"Processed by {interaction.user.display_name}  •  {datetime.datetime.now().strftime('%d.%m.%y')}")
                        return await interaction.response.send_message(content=f"{user.mention}", embed=embed)
                    except Exception as e:
                        embed = discord.Embed(title="<:dsbbotFailed:953641818057216050> Error!", description=f"{e}", color=ErrorCOL)
                        return await interaction.response.send_message(embed=embed, ephemeral=True)
                        
                elif newrank[1] < userrank[1]:
                    #demote
                    try:
                        data = db_register_get_data(user.id)
                        group = await roblox.get_group(15155104)
                        await group.get_member(get_user_id_from_link(data[2])).set_rank(newrank[1])
                        userrank_role = discord.utils.get(interaction.guild.roles, name=str(userrank[0]))
                        newrank_role = discord.utils.get(interaction.guild.roles, name=str(newrank[0]))
                        await user.edit(nick=change_nickname(newrank[0], user.display_name))
                        await user.add_roles(newrank_role)
                        await user.remove_roles(userrank_role)
                        if userrank[1] >= 16 and newrank[1] <16:
                            mr_role = discord.utils.get(interaction.guild.roles, name="Operation Ringleader")
                            await user.remove_roles(mr_role)
                        if userrank[1] >= 20 and newrank[1] < 20:
                            soup_role = discord.utils.get(interaction.guild.roles, name="Operation Supervisor")
                            await user.remove_roles(soup_role)
                        embed = discord.Embed(title="<:trubotWarning:1099642918974783519> Demotion!", description=f"You have been demoted from **{userrank[0]}** to **{newrank[0]}**.", color=ErrorCOL)
                        embed.set_footer(icon_url=interaction.user.avatar, text=f"Processed by {interaction.user.display_name}  •  {datetime.datetime.now().strftime('%d.%m.%y')}")
                        return await interaction.response.send_message(content=f"{user.mention}", embed=embed)
                    except Exception as e:
                        print(e)
                        embed = discord.Embed(title="<:dsbbotFailed:953641818057216050> Error!", description=f"{e}", color=ErrorCOL)
                        return await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    print("Something was missed...")

    '''   
    @app_commands.command(name="truaccept", description="Used to accept new TRU members into the roblox group.")
    async def truaccept_group(self, interaction:discord.Interaction, member:discord.Member):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.commandRole))):
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotDeny:1073668785262833735> Missing Permission!", description=f"You must be a member of TRU leadership or above to use this command."), ephemeral=True)
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
        




