import discord
import os
import sys
import datetime
import random
from Functions.mainVariables import *
from Functions.permFunctions import *
from Functions.formattingFunctions import embedBuilder
from Database_Functions.MaindbFunctions import (get_quota, set_active_block, get_all_quota_data)
from Functions.randFunctions import (get_quota, getrank, changerank, change_nickname, get_user_id_from_link)
from Database_Functions.UserdbFunction import (db_register_get_data)
from discord.ext import commands
from discord import app_commands
from discord import ui
from roblox import *

roblox = Client("_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_A249C7CBC0AD0C2157CF1D7468ADA824736AA27889516B8B6CE8ECDB36DFDA0E8060ADEB457C5E09FC7A1890499AE2CCB105774F5110EDA6967AE9F8874F2DFC554568F0B2FA0E495127FBB713B39EBD7E807009540475DE2E6F6BA203325747382D6C7E8C43A382240F49576850B55B885A0A662C1FBD19A3653331C1BFA49D9CBBFFE01FCF21CD676E01981AE859ECAF81BD219052904AB26A81F39E9ADB0B3F3D7C2A24533E9849EE3B183192EBD3F039E51530411037FC26143AD12687A31F0B087AA57FDBB2B4C562A3F7CCD909F418D6EC6F04E8031C523C20B475A4A85D0E0DED5DD0DDEDB4D417B12C2944870F884D3B6D6734DE67C97982D678E45007C16AC1E218D4A5DA104D7CF57B79F6039C257AC8782FC4505F4D193D269DB05439E3C0E49D59AB39EA77A8335CA77126CD1B4CAABCC3826905C6CBFB11A19860B85B78300560974E04A0B5F40CCCC40062C91554179133B4284E15DFE0AB4B114605E45BA8FE25F718E36753BCC60DB8DD76E")    

class QuotaCmds(commands.GroupCog, group_name='quota'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
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
                        return await interaction.response.send_message(embed= discord.Embed(color=YellowCOL, title=f"<:dsbbotCaution:1067970676041982053> Quota Block {blockdata[0]} is already active!", description=f"Start Date: <t:{blockdata[1]}:F>\nEnd Date: <t:{blockdata[2]}:F>"), ephemeral=True)
                    else: # If there was an active block but it is now changed
                        set_active_block(block_num=block)
                        new_blockdata = get_quota()
                        return await interaction.response.send_message(embed= discord.Embed(color=HRCommandsCOL, title=f"<:dsbbotSuccess:953641647802056756> Successfully changed Quota Block!", description=f"*Quota Block {blockdata[0]} is now inactive and Quota Block {new_blockdata[0]} has been set as active!*\n**Before**\n<t:{blockdata[1]}:F> - <t:{blockdata[2]}:F>\n\n**After**\n<t:{new_blockdata[1]}:F> - <t:{new_blockdata[2]}:F>"))
                else: # There is now an active quota block
                    set_active_block(block_num=block)
                    new_blockdata = get_quota()
                    return await interaction.response.send_message(embed= discord.Embed(color=HRCommandsCOL, title=f"<:dsbbotSuccess:953641647802056756> Successfully set Quota Block!", description=f"*Quota Block {new_blockdata[0]} has been set to active!*\n**Start Date:** <t:{new_blockdata[1]}:F>\n**End Date:** <t:{new_blockdata[2]}:F>"))
        else:
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title=f"<:dsbbotFailed:953641818057216050> No quota information for block number {block} found!", description=f"If you feel something is wrong with the database, please ping <@776226471575683082>."), ephemeral=True)

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

    
class ManagementCmds(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    ## TRU MANAGEMENT ##
    @app_commands.command(name="rank", description="Used to promote/demoted TRU members.")
    @app_commands.choices(rank=[
    app_commands.Choice(name="Elite Vanguard", value="EVGD"),
    app_commands.Choice(name="Vanguard", value="VGD"),
    app_commands.Choice(name="Elite Operator", value="EOPR"),
    app_commands.Choice(name="Operator", value="OPR"),
    app_commands.Choice(name="Entrant", value="ENT"),])
    async def rank_cmd(self, interaction:discord.Interaction, user:discord.Member, rank:app_commands.Choice[str]):
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
                    embed = discord.Embed(title="<:dsbbotSuccess:953641647802056756> Congrats!", description=f"You can now host your own operations, without the need for supervision! <a:dsbbotCelebration:1084176617993162762>", color=SuccessCOL)
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
                        embed = discord.Embed(title="<:dsbbotSuccess:953641647802056756> Promotion!", description=f"You have been promoted from **{userrank[0]}** to **{newrank[0]}**! <a:dsbbotCelebration:1084176617993162762>", color=SuccessCOL)
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
                        embed = discord.Embed(title="<:dsbbotCaution:1067970676041982053> Demotion!", description=f"You have been demoted from **{userrank[0]}** to **{newrank[0]}**.", color=ErrorCOL)
                        embed.set_footer(icon_url=interaction.user.avatar, text=f"Processed by {interaction.user.display_name}  •  {datetime.datetime.now().strftime('%d.%m.%y')}")
                        return await interaction.response.send_message(content=f"{user.mention}", embed=embed)
                    except Exception as e:
                        print(e)
                        embed = discord.Embed(title="<:dsbbotFailed:953641818057216050> Error!", description=f"{e}", color=ErrorCOL)
                        return await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    print("Something was missed...")
            
    @app_commands.command(name="truwelcome", description="Used to induct new TRU members once they've joined the server.")
    async def welcome_pvt(self, interaction:discord.Interaction, member:discord.Member):
        if not TRULEAD(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotDeny:1073668785262833735> Missing Permission!", description=f"You must be a member of TRUPC or above to use this command."), ephemeral=True)
        TRUPvt = discord.utils.get(interaction.guild.roles, name="TRU Private")
        TRURole = discord.utils.get(interaction.guild.roles, name="TRU")
        ServerAccessRole = discord.utils.get(interaction.guild.roles, name="Server Access")
        await member.edit(nick=change_nickname("TRU Private", member.display_name))
        TRUondutychannel = await self.bot.fetch_channel(1091329185500381235) # Channel ID
        await member.add_roles(TRUPvt, TRURole, ServerAccessRole)
        await TRUondutychannel.send(f"TRU, please welcome {member.mention}!")
        await member.send(embed=discord.Embed(color=TRUCommandCOL, title=f"Welcome to Defensive Squadron Bravo {member.name}!", description=f"Alrighty...you should now have your roles...\n\nHello and welcome to QSO's Defensive Squadron Bravo. I am TRU Helper and as my name already suggests, I help manage this squadron.\n\nFirst things first, please update to your nickname to include `TRU Pvt` as your rank tag and your Roblox username. Additionally please add the `| TRU` suffix to your name in main QSO, you'll receive the TRU role once you pass your private phase. The TRU Private phase, in short, is our version of the OiT phase from main QSO, with a couple of amendments. You can find more information about the Private phase in <#960601856298602617> and an end date for said Private phase will be given to you as soon as possible.\n\nNext, please read through  <#954443926264217701>, <#957983615315222529>, <#957789241813917766> and all the other miscellaneous infoboards. I should also note that while in TRU, you are to never speak ill of other squadrons or display an form of squadron elitism or egotism. If found to be participating in these actions, you will be swiftly removed without warning.\n\nAnd on that note, TRU Management wishes you the best of luck on your Private phase, and we hope to see you excel as a defensive operative.\n\n<:TRU:1060271947725930496> *In the face of danger, we stand our ground!* <:TRU:1060271947725930496>"))
        await interaction.response.send_message(embed=discord.Embed(color=TRUCommandCOL, title=f"<:dsbbotSuccess:953641647802056756> Success!",description=f"{member.name} should now have their roles and should have received the welcome message :D"), ephemeral=True)
        
    @app_commands.command(name="truaccept", description="Used to accept new TRU members into the roblox group.")
    async def join_tru(self, interaction:discord.Interaction, member:discord.Member):
        if not TRULEAD(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotDeny:1073668785262833735> Missing Permission!", description=f"You must be a member of TRUPC or above to use this command."), ephemeral=True)
        try:
            username = str(member.display_name).split()[-1]
            group = await roblox.get_group(15155104)
            user = await roblox.get_user_by_username(username)
            await group.accept_user(user)
            await interaction.response.send_message(embed=discord.Embed(color=TRUCommandCOL, title=f"<:dsbbotSuccess:953641647802056756> Accepted {username}!"), ephemeral=True)
            await member.send(embed = discord.Embed(description=f"Your request to join the `Defensive Squadron Bravo` Roblox group has been accepted.", color=TRUCommandCOL))
        except Exception as e:
            print(e)
            await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Error!", description=f"An error occurred while accepting {username}: {str(e)}"), ephemeral=True)

    @app_commands.command(name="trukick", description="Used to kick TRU members.")
    async def kick_tru(self, interaction:discord.Interaction, member:discord.Member, reason:str):
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
            await interaction.response.send_message(embed = discord.Embed(title=f"<:dsbbotSuccess:953641647802056756> Member removed", description=f"Successfully removed {member.mention} from TRU.\n\n**Reason:** {reason}\n→ [Audit Log]({logmsg.jump_url})", color=DarkRedCOL))
            await member.send(embed = discord.Embed(title=f"You have been kicked from Defensive Squadron Bravo.",description=f"**Reason:** {reason}", color=DarkRedCOL))
            await group.kick_user(user)
            await member.kick(reason=reason)
        except Exception as e:
            print(e)
            await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Error!", description=f"An error occurred while accepting {username}: {str(e)}"), ephemeral=True)        

    @app_commands.command(name="trustrike", description="Used to give out strikes in TRU.")
    async def tru_stike(self, interaction:discord.Interaction, member:discord.Member, reason:str):
        if not TRULEAD(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotDeny:1073668785262833735> Missing Permission!", description=f"You must be a member of TRUPC or above to use this command."), ephemeral=True)
        else:
            strikeemb = discord.Embed(title=f"<:TRU:1060271947725930496> Striked TRU Member", description=f"{member.mention} has recieved a strike in TRU from {interaction.user.mention}.\n\n**Reason:** {reason}", color=DarkRedCOL)
            #strikeemb.set_thumbnail(url=member.avatar.url)
            strikeemb.set_footer(text=f"ID: {member.id} • {datetime.datetime.now().strftime('%m/%d/%Y %H:%M %p')}")
            logsch = self.bot.get_channel(1054705433971003412) # 1008449677210943548 #audit-logs
            logmsg = await logsch.send(embed=strikeemb)
            await interaction.response.send_message(embed = discord.Embed(title=f"<:dsbbotSuccess:953641647802056756> Member striked", description=f"Successfully striked {member.mention}.\n\n**Reason:** {reason}\n→ [Audit Log]({logmsg.jump_url})", color=DarkRedCOL))
            await member.send(embed = discord.Embed(title=f"You have received a strike in Defensive Squadron Bravo.",description=f"**Reason:** {reason}", color=DarkRedCOL))
            pass
    
    @app_commands.command(name="trustrikes", description="Used to view strikes in TRU.")
    async def tru_strikes(self, interaction:discord.Interaction, member:discord.Member=None):
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
                        title="<:dsbbotDisabled2:1067970678608908288> No warnings found",
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
            
        




