import asyncio
import datetime
import os
import random
import sys

import discord
import requests
from discord import app_commands, ui
#from Database_Functions.UserdbFunction import (db_register_get_data)
from discord.ext import commands
from roblox import *

from Database_Functions.PrismaFunctions import *
#from Commands.strike_cmds import roblox_client
from Database_Functions.UserdbFunction import *
from Functions.formattingFunctions import embedBuilder
from Functions.mainVariables import *
from Functions.randFunctions import (change_nickname, get_user_id_from_link,
                                     in_roblox_group, get_promotion_message)
from Functions.rolecheckFunctions import *

roblox_client = Client("_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_D5064A0C1DB1D5FD5C66ED677C3B797A10523AEE48D18912BB5D6F2E08BE04F39C4E056585CDE8C410971D4BE9C674A66E86C9BD29BBC99B41A5720149F0C5B2C16FF8088846DDB8004B1C206F0B3FB837A4263111612CA93E448C7AC999EC9D326AB762CB74A7BB0B8D246F192BAC4C5139D77CC634D9C3F06A836D43712B6FA65E7DD315AB471C41A0CDD683A633624BFE8A91DD3BA85F34612556A0525401AD16743318C61B208D1A894FFAB372E157342BF65B78E06FB33543F74A8A600256582EBA8A56062BEA431246332E270A4EA1F77B811BBB7678C3A10020251B8FBF3D015BD391A219400A803A9A07B5B971785639B08E9F1E85230E630D7D1680E1AA7D9815C4C9DA3D9FE5064EFECDB50123CD8E6E7A7527624721D77F7D2542B833E49C14F35356C57F74AF16B4A2E553BBB56B1398F7F8F8F4E141C149D7499DE92ABFDA759F3634D395FB1333BC1F2709919B573DE87E1ED3412022B26BEF5544DD44F23BFE968E6BA37DCCDA3B87060A1930")

class operatorCmds(commands.GroupCog, group_name='operator'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @app_commands.command(name="register", description="Add a new operator to the registry.")
    async def operative_register(self, interaction: discord.Interaction, profilelink: str, user:discord.Member=None):
        serverConfig = await fetch_config(interaction=interaction)
        if checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.logPermissionRole))):
            
            if user and user != interaction.user and not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.commandRole))):
                return await interaction.response.send_message(embed = embedBuilder(responseType="perms", embedDesc="Only TRU leadership and above may register other users."))
            Operative = user if user else interaction.user
            roblox_user = await roblox_client.get_user(get_user_id_from_link(profilelink))
            dbResponse = await registerOperator(Operative, profilelink, roblox_user.name)
            if type(dbResponse) is not str:
                successEmbed = embedBuilder(responseType="succ", embedTitle="Added to registry!",
                                            embedDesc="New registry entry:")

                successEmbed.add_field(name="Username:", value=dbResponse.userName, inline=True)
                successEmbed.add_field(name="TRU Rank:", value=dbResponse.rank, inline=True)
                successEmbed.add_field(name="Profile Link:", value=f"[{roblox_user.display_name} (@{roblox_user.name})]({dbResponse.profileLink})", inline=True)
                successEmbed.set_footer(text=f"Registered on: {datetime.datetime.utcnow().strftime('%m/%d/%Y %H:%M')}Z")
                await interaction.response.send_message(embed=successEmbed)
            else:
                errEmbed = embedBuilder("err",
                                        embedDesc="Error: " + str(dbResponse))
                await interaction.response.send_message(embed=errEmbed)



        else:
            errEmbed = embedBuilder("perms",
                                    embedDesc="Only Operators and above may use this command.")
            return await interaction.response.send_message(embed=errEmbed)

    @app_commands.command(name="update", description="Update someone's registry data.")
    async def operative_update(self, interaction: discord.Interaction, profilelink: str = None, user: discord.Member = None):
        serverConfig = await fetch_config(interaction=interaction)
        if not user:
            user = interaction.user
        requested_operator = await getOperator(user.id)
        if type(requested_operator) is str or requested_operator is None:
            return await interaction.response.send_message(embed = embedBuilder(responseType="err", embedTitle="Operator not found...", embedDesc=f"{user.mention} was not found in the database, and can therefore not be updated. Please double check that they are registered."))
        if user and user != interaction.user and not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.commandRole))):
            return await interaction.response.send_message(embed = embedBuilder(responseType="perms", embedDesc="Only TRU leadership and above may update other users."))
        Operative = user if user else interaction.user
        roblox_user = await roblox_client.get_user(get_user_id_from_link(profilelink))
        dbResponse = await updateOperator(Operative, profilelink, roblox_user.name)
        if type(dbResponse) is not str and dbResponse is not False:
            successEmbed = embedBuilder(responseType="succ", embedTitle="Operator updated!",
                                        embedDesc="Updated registry entry:")

            successEmbed.add_field(name="Username:", value=dbResponse.userName, inline=True)
            successEmbed.add_field(name="TRU Rank:", value=dbResponse.rank, inline=True)
            successEmbed.add_field(name="Profile Link:",
                                value=f"[{roblox_user.display_name} (@{roblox_user.name})]({dbResponse.profileLink})",
                                inline=True)
            successEmbed.set_footer(text=f"Updated on: {datetime.datetime.utcnow().strftime('%m/%d/%Y %H:%M')}Z")
            await interaction.response.send_message(embed=successEmbed)
        else:
            errEmbed = embedBuilder("err", embedDesc="Error: " + str(dbResponse))
            await interaction.response.send_message(embed=errEmbed, ephemeral=True)

    @app_commands.command(name="remove", description="Remove someone from the registry.")
    async def operative_remove(self, interaction: discord.Interaction, user:discord.Member=None, userid:str=None):
        serverConfig = await fetch_config(interaction=interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.commandRole))):
            return await interaction.response.send_message(embed = embedBuilder(responseType="perms", embedDesc="Only TRU leadership and above may use this command."))
        if userid:
            userid = int(userid)
        if user is None and userid is None:
            return await interaction.response.send_message(embed = embedBuilder(responseType="err", embedTitle="Invalid arguments", embedDesc="Please provide a user or user ID."))

        if user and userid and userid != user.id:
            return await interaction.response.send_message(embed = embedBuilder(responseType="err", embedTitle="Invalid arguments!", embedDesc="You specified two different users."))
        if not userid:
            userid = user.id
        dbResponse = await removeOperator(userid)

        if dbResponse == True:
            successEmbed = embedBuilder("succ", embedTitle="User removed!",
                                        embedDesc=f"An Operator with ID `{userid}` has been removed from the registry." if user is None else f"{user.mention} has been removed from the registry.")
            await interaction.response.send_message(embed=successEmbed)
        else:
            errEmbed = embedBuilder("err",
                                    embedDesc="Error: " + str(dbResponse))
            await interaction.response.send_message(embed=errEmbed)
        
    @app_commands.command(name="view", description="View someone's registry data.")
    async def operative_view(self, interaction: discord.Interaction, user:discord.Member=None):
        serverConfig = await fetch_config(interaction=interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.logPermissionRole))):
            return await interaction.response.send_message(embed = embedBuilder(responseType="perms", embedDesc="You do not have permission to use this command."), ephemeral=True)
        if not user:
            user = interaction.user
        requested_operative = await getOperator(user.id)
        if not requested_operative:
            return await interaction.response.send_message(embed = embedBuilder(responseType="err", embedTitle="User not found!" , embedDesc=f"{user.mention} was not found in the registry."))
        
        roblox_user = await roblox_client.get_user(get_user_id_from_link(requested_operative.profileLink))
        log = await get_most_recent_patrol(user)
        
        responseEmbed = embedBuilder(responseType="succ", embedTitle="User found!", embedDesc=f"Here is {user.mention}'s registry information.")
        responseEmbed.add_field(name="Roblox Username", value=f"[{roblox_user.display_name} (@{roblox_user.name})]({requested_operative.profileLink})", inline=False)
        responseEmbed.add_field(name="TRU Rank", value=f"{requested_operative.rank}")
        if userSuspended(user):
            responseEmbed.add_field(name="Suspended", value="True")
        #responseEmbed.add_field(name="Last Rank Change", value="To be added...", inline=False)
        if log:
            if not log.timeEnded or str(log.timeEnded) == "Null":
                time_elapsed = (datetime.datetime.fromtimestamp(int(time.time())) - datetime.datetime.fromtimestamp(int(log.timeStarted))).total_seconds() // 60
                responseEmbed.add_field(name=f"Last Log `{log.logID}`", value=f"Started: <t:{log.timeStarted}>\nTime Elapsed: `{int(time_elapsed)} minutes`\nStatus: *In progress*", inline=False)
            elif not log.logProof or str(log.logProof) == "Null" or str(log.logProof) == "No proof provided":
                responseEmbed.add_field(name=f"Last Log `{log.logID}`", value=f"Started: <t:{log.timeStarted}>\nEnded: <t:{log.timeEnded}>\nLength: `{round(float(log.timeElapsed))} minutes`\nProof: *No proof provided*", inline=False)
            else:
                responseEmbed.add_field(name=f"Last Log `{log.logID}`", value=f"Started: <t:{log.timeStarted}>\nEnded: <t:{log.timeEnded}>\nLength: `{round(float(log.timeElapsed))} minutes`\nProof: [image]({log.logProof})", inline=False)
        else:
            responseEmbed.add_field(name="Last Log", value="*No recent log found!*", inline=False)
        return await interaction.response.send_message(embed=responseEmbed)

    @app_commands.command(name="rank", description="Used to promote/demoted TRU members.")
    @app_commands.describe(member="Who are you ranking?", rank="To what rank?", reason="[DEMOTIONS ONLY] Why are they being demoted?")
    @app_commands.choices(rank=[
    app_commands.Choice(name="totally a real rank", value="25"),
    app_commands.Choice(name="Vanguard Officer", value="20"),
    app_commands.Choice(name="Vanguard", value="15"),
    app_commands.Choice(name="Elite Operator", value="5"),
    app_commands.Choice(name="Senior Operator", value="4"),
    app_commands.Choice(name="Operator", value="3"),
    app_commands.Choice(name="Entrant", value="1"),])
    async def trurank_user(self, interaction:discord.Interaction, member:discord.Member, rank:app_commands.Choice[str], reason:str=None):
        serverConfig = await fetch_config(interaction=interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.commandRole))):
            return await interaction.response.send_message(embed = embedBuilder(responseType="perms", embedDesc="Only TRU leadership and above may use this command."))
        ranked_operative = await getOperator(member.id)
        if ranked_operative == None: # User not in database
            return await interaction.response.send_message(embed = embedBuilder(responseType="err", embedTitle="User not found!", embedDesc=f"{member.mention} was not found in the registry."), ephemeral=True)
        requested_rank = await fetch_rolebind(robloxID=int(rank.value))
        if not requested_rank: # If the requested rank is not in the rolebind database
            return await interaction.response.send_message(embed = embedBuilder(responseType="err", embedTitle="Rolebind not found!" , embedDesc=f"Could not find a rolebind for the requested rank!\n`Rank details: Specified roblox_client role ID '{rank.value}' and rank name '{rank.name}' are not binded`"), ephemeral=True)
        current_rank = await fetch_rolebind(rankName=ranked_operative.rank)
        if not current_rank: # If no rolebind is found in the database for the users current rank
            return await interaction.response.send_message(embed = embedBuilder(responseType="err", embedTitle="Rolebind not found!", embedDesc=f"Could not find a rolebind for {member.mention}'s current rank!\n`Rank without rolebind: '{ranked_operative.rank}'`"), ephemeral=True)
        #Ranking Errors
        if int(current_rank.RobloxRankID) == int(requested_rank.RobloxRankID): # Cant promote to current rank
            return await interaction.response.send_message(embed = embedBuilder(responseType="err", embedTitle="While ranking..." , embedDesc=f"{member.mention} is already ranked as **{requested_rank.rankName}**."), ephemeral=True)
        if int(current_rank.RobloxRankID) >= 250 and int(requested_rank.RobloxRankID) < 250: # Cant demote TRU Leadership
            return await interaction.response.send_message(embed = embedBuilder(responseType="perms", embedDesc=f"Blue said I can't demote TRU Leadership or above. {member.mention} is a member of TRU Leadership or above."))
        
        #roblox_client Group
        TRU_ROBLOX_group = await roblox_client.get_group(15155175)
        group_members = await TRU_ROBLOX_group.get_members().flatten()
        requestedRobloxUser = await roblox_client.get_user(get_user_id_from_link(ranked_operative.profileLink))
        if in_roblox_group(group_members, requestedRobloxUser) is False:
            return await interaction.response.send_message(embed = embedBuilder(responseType="err", embedTitle="ROBLOX Group", embedDesc=f"Could not find {member.mention} to be a member of the `{TRU_ROBLOX_group.name}` roblox group. ([Roblox Group Link](https://www.roblox_client.com/groups/15155175/QSO-Tactical-Response-Unit))"), ephemeral=True)
        
        #Defer
        await interaction.response.defer(thinking=True, ephemeral=True)
        AuditLogs_channel = interaction.guild.get_channel(1095835491485622323) #Audit Logs
        tru_on_duty_channel = interaction.guild.get_channel(1121081165697265684) #bot-testing
        
    
        await member.edit(nick=change_nickname(requested_rank.rankName, requestedRobloxUser.name)) # Change nickname
        await member.add_roles(interaction.guild.get_role(int(requested_rank.discordRoleID))) # Discord role add
        await member.remove_roles(interaction.guild.get_role(int(current_rank.discordRoleID))) # Discord role remove
        await updateOperator_rank(member, requested_rank.rankName) # Database update
        await TRU_ROBLOX_group.get_member(requestedRobloxUser.id).set_rank(int(requested_rank.RobloxRankID)) # Roblox group update
        
        
        if int(current_rank.RobloxRankID) < int(requested_rank.RobloxRankID): #Promotion
            try:

                
                dm_notification = discord.Embed(title="<a:trubotCelebration:1099643172012949555> TRU Promotion!", description=f"You have been promoted from **{current_rank.rankName}** to **{requested_rank.rankName}**!\n\n{get_promotion_message(str(requested_rank.rankName))}", color=DarkGreenCOL)
                dm_notification.set_footer(icon_url=interaction.user.avatar, text=f"Processed by {interaction.user.display_name}  •  {datetime.datetime.now().strftime('%d.%m.%y')}")
                audit_log = discord.Embed(title="<:trubotWarning:1099642918974783519> User Promoted!", description=f"{member.mention} was promoted from **{current_rank.rankName}** to **{requested_rank.rankName}**.", color=HRCommandsCOL)
                audit_log.set_footer(icon_url=interaction.user.avatar, text=f"Processed by {interaction.user.display_name}  •  {datetime.datetime.now().strftime('%d.%m.%y')}")
                
                await AuditLogs_channel.send(embed = audit_log)
                await member.send(embed=dm_notification)
                await tru_on_duty_channel.send(f"Please congragulate **{member.display_name}** on their promotion to **{requested_rank.rankName}**! <a:trubotCelebration:1099643172012949555>")
                return await interaction.edit_original_response(embed=discord.Embed(title="<:trubotAccepted:1096225940578766968> Promotion Successful!", description=f"{member.mention} has been promoted from **{current_rank.rankName}** to **{requested_rank.rankName}**.", color=SuccessCOL))
            except Exception as e:
                print(e)
                embed = embedBuilder(responseType="err", embedTitle="While promoting...", embedDesc=f"{e}")
                return await interaction.edit_original_response(embed=embed, ephemeral=True)
        
        
        elif int(current_rank.RobloxRankID) > int(requested_rank.RobloxRankID): #Demotion
            try:
                dm_notification = discord.Embed(title="<:trubotWarning:1099642918974783519> TRU Demotion!", description=f"You have been demoted from **{current_rank.rankName}** to **{requested_rank.rankName}**.\n\n**Reason:** {reason}", color=DarkRedCOL)
                dm_notification.set_footer(icon_url=interaction.user.avatar, text=f"Processed by {interaction.user.display_name}  •  {datetime.datetime.now().strftime('%d.%m.%y')}")
                audit_log = discord.Embed(title="<:trubotWarning:1099642918974783519> User Demoted!", description=f"{member.mention} was demoted from **{current_rank.rankName}** to **{requested_rank.rankName}**.\n\n**Reason:** {reason}", color=HRCommandsCOL)
                audit_log.set_footer(icon_url=interaction.user.avatar, text=f"Processed by {interaction.user.display_name}  •  {datetime.datetime.now().strftime('%d.%m.%y')}")
                
                await AuditLogs_channel.send(embed = audit_log)
                await member.send(embed=dm_notification)
                return await interaction.edit_original_response(embed=discord.Embed(title="<:trubotAccepted:1096225940578766968> Demotion Successful!", description=f"{member.mention} has been demoted from **{current_rank.rankName}** to **{requested_rank.rankName}**.", color=SuccessCOL))
            except Exception as e:
                print(e)
                embed = embedBuilder(responseType="err", embedTitle="While demoting...", embedDesc=f"{e}")
                return await interaction.edit_original_response(embed=embed, ephemeral=True)
            
        else:
            return await interaction.response.send_message("If you're seeting this, Blue majorly missed something here.......", ephemeral=True)

    @app_commands.command(name="accept", description="Used to remotely accept new TRU members into the roblox group, if they have a pending request.")
    async def join_tru(self, interaction:discord.Interaction, member:discord.Member):
        serverConfig = await fetch_config(interaction=interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.commandRole))):
            return await interaction.response.send_message(embed = embedBuilder(responseType="perms", embedDesc=f"Only TRU leadership and above may use this command."), ephemeral=True)
        try:
            username = str(member.display_name).split()[-1]
            group = await roblox_client.get_group(15155104)
            user = await roblox_client.get_user_by_username(username)
            await group.accept_user(user)
            await interaction.response.send_message(embed=discord.Embed(color=TRUCommandCOL, title=f"<:trubotAccepted:1096225940578766968> Accepted {username}!"), ephemeral=True)
            await member.send(embed = discord.Embed(description=f"Your request to join the `{group.name}` ROBLOX group has been accepted.", color=TRUCommandCOL))
        except Exception as e:
            print(e)
            await interaction.response.send_message(embed = embedBuilder(responseType="err", embedTitle="While accepting...", embedDesc=f"An error occurred while accepting {username}: {str(e)}"), ephemeral=True)


