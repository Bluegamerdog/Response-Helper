import asyncio
import datetime
import os
import random
import sys

import discord
from discord import app_commands, ui
#from Database_Functions.UserdbFunction import (db_register_get_data)
from discord.ext import commands
from roblox import *

import Database_Functions.PrismaFunctions as dbFuncs
#from Commands.strike_cmds import roblox_client
from Database_Functions.UserdbFunction import *
from Functions import permFunctions
from Functions.formattingFunctions import embedBuilder
from Functions.mainVariables import *
from Functions.permFunctions import *
from Functions.randFunctions import *
from Functions.randFunctions import (change_nickname, get_user_id_from_link,
                                     in_roblox_group)

roblox_client = Client("_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_D5064A0C1DB1D5FD5C66ED677C3B797A10523AEE48D18912BB5D6F2E08BE04F39C4E056585CDE8C410971D4BE9C674A66E86C9BD29BBC99B41A5720149F0C5B2C16FF8088846DDB8004B1C206F0B3FB837A4263111612CA93E448C7AC999EC9D326AB762CB74A7BB0B8D246F192BAC4C5139D77CC634D9C3F06A836D43712B6FA65E7DD315AB471C41A0CDD683A633624BFE8A91DD3BA85F34612556A0525401AD16743318C61B208D1A894FFAB372E157342BF65B78E06FB33543F74A8A600256582EBA8A56062BEA431246332E270A4EA1F77B811BBB7678C3A10020251B8FBF3D015BD391A219400A803A9A07B5B971785639B08E9F1E85230E630D7D1680E1AA7D9815C4C9DA3D9FE5064EFECDB50123CD8E6E7A7527624721D77F7D2542B833E49C14F35356C57F74AF16B4A2E553BBB56B1398F7F8F8F4E141C149D7499DE92ABFDA759F3634D395FB1333BC1F2709919B573DE87E1ED3412022B26BEF5544DD44F23BFE968E6BA37DCCDA3B87060A1930")

class operatorCmds(commands.GroupCog, group_name='operator'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @app_commands.command(name="register", description="Add a new operator to the registry.")
    async def operative_register(self, interaction: discord.Interaction, profilelink: str, user:discord.Member=None):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.logPermissionRole))):
            if user and user != interaction.user and not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.commandRole))):
                return await interaction.response.send_message(embed=discord.Embed(title="Missing permission!", description="Only TRU leadership and above may register other users.", color=ErrorCOL))
            Operative = user if user else interaction.user
            roblox_user = await roblox_client.get_user(get_user_id_from_link(profilelink))
            dbResponse = await dbFuncs.registerUser(Operative, profilelink, roblox_user.name)
            if type(dbResponse) is not str:
                successEmbed = discord.Embed(title="<:trubotAccepted:1096225940578766968> Successfully registered!",
                                            description="New registry entry:", color=SuccessCOL)

                successEmbed.add_field(name="Username:", value=dbResponse.userName, inline=True)
                successEmbed.add_field(name="TRU Rank:", value=dbResponse.rank, inline=True)
                successEmbed.add_field(name="Profile Link:", value=f"[{roblox_user.display_name} (@{roblox_user.name})]({dbResponse.profileLink})", inline=True)
                successEmbed.set_footer(text=f"Registered on: {datetime.datetime.utcnow().strftime('%m/%d/%Y %H:%M')}Z")
                await interaction.response.send_message(embed=successEmbed)
            else:
                errEmbed = embedBuilder("Error", embedTitle="An error occured:",
                                        embedDesc="Error: " + str(dbResponse))
                await interaction.response.send_message(embed=errEmbed)



        else:
            errEmbed = embedBuilder("Error", embedTitle="Permission error:",
                                    embedDesc="You are not: <@&" + str(serverConfig.logPermissionRole) + ">")
            await interaction.response.send_message(embed=errEmbed)

    @app_commands.command(name="update", description="Update someone's registry data.")
    async def operative_update(self, interaction: discord.Interaction, profilelink:str=None, user:discord.Member=None):
        return await interaction.response.send_message("This command isn't complete.", ephemeral=True)

    @app_commands.command(name="remove", description="Remove someone from the registry.")
    async def operative_remove(self, interaction: discord.Interaction, user:discord.Member=None, userid:str=None):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.commandRole))):
            return await interaction.response.send_message(embed=discord.Embed(title="<:trubotDenied:1099642433588965447> Missing permission!", description="Only TRU leadership and above may use this command.", color=ErrorCOL))
        if userid:
            userid = int(userid)
        if user is None and userid is None:
            return await interaction.response.send_message(embed=discord.Embed(title="Invalid arguments", description="Please provide a user or user ID.", color=ErrorCOL))

        if user and userid and userid != user.id:
            return await interaction.response.send_message(embed=discord.Embed(title="User error!", description="You specified two different users.", color=ErrorCOL))
        if not userid:
            userid = user.id
        dbResponse = await dbFuncs.removeOperative(userid)

        if dbResponse == True:
            successEmbed = embedBuilder("Success", embedTitle="Success!",
                                        embedDesc=f"Operative with ID {userid} has been removed from the registry." if user is None else f"{user.mention} has been removed from the registry.")
            await interaction.response.send_message(embed=successEmbed)
        else:
            errEmbed = embedBuilder("Error", embedTitle="An error occurred:",
                                    embedDesc="Error: " + str(dbResponse))
            await interaction.response.send_message(embed=errEmbed)
        
    @app_commands.command(name="view", description="View someone's registry data.")
    async def operative_view(self, interaction: discord.Interaction, user:discord.Member=None):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.logPermissionRole))):
            return await interaction.response.send_message("This command isn't complete.", ephemeral=True)
        if not user:
            user = interaction.user
        requested_operative = await dbFuncs.viewOperative(user.id)
        if not requested_operative:
            return await interaction.response.send_message(embed = discord.Embed(title="<:trubotDenied:1099642433588965447> Error!", description=f"{user.mention} was not found in the registry.", color=ErrorCOL))
        embed = discord.Embed(title=f"<:trubotAccepted:1096225940578766968> User found!", description=f"**Username:** {requested_operative.userName}\n**TRU Rank:** {requested_operative.rank}\n**roblox_client Profile:** {requested_operative.profileLink}", color=SuccessCOL)
        return await interaction.response.send_message(embed=embed)

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
            return await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, title="<:trubotDenied:1099642433588965447> Rolebind/Rank Error!", description=f"Could not find a rolebind for the requested rank!\n`Rank details: Specified roblox_client role ID '{rank.value}' and rank name '{rank.name}' are not binded`"), ephemeral=True)
        current_rank = await dbFuncs.fetch_rolebind(rankName=ranked_operative.rank)
        if not current_rank:
            return await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, title="<:trubotDenied:1099642433588965447> Rolebind/Rank Error!", description=f"Could not find a rolebind for {member.mention}'s current rank!\n`Rank without rolebind: '{ranked_operative.rank}'`"), ephemeral=True)
        #Ranking Errors
        if int(current_rank.RobloxRankID) == int(requested_rank.RobloxRankID):
            return await interaction.response.send_message(embed=discord.Embed(title="<:trubotDenied:1099642433588965447> Ranking Error!", description=f"{member.mention} is already ranked as **{requested_rank.rankName}**.", color=ErrorCOL), ephemeral=True)
        if int(current_rank.RobloxRankID) >= 250 and int(requested_rank.RobloxRankID) < 250: #hehe
            return await interaction.response.send_message(embed=discord.Embed(title="<:trubotDenied:1099642433588965447> Permission Error!", description=f"Blue said I can't demote TRU Leadership or above. {member.mention} is a member of TRU Leadership or above.", color=ErrorCOL))
        #roblox_client Group
        TRU_ROBLOX_group = await roblox_client.get_group(15155175)
        group_members = await TRU_ROBLOX_group.get_members().flatten()
        roblox_user = await roblox_client.get_user(get_user_id_from_link(ranked_operative.profileLink))
        if in_roblox_group(group_members, roblox_user) is False:
            return await interaction.response.send_message(embed=discord.Embed(title="<:trubotDenied:1099642433588965447> roblox_client Group Error!", description=f"Could not find {member.mention} to be a member of the `{TRU_ROBLOX_group.name}` roblox_client group. ([roblox_client Group Link](https://www.roblox_client.com/groups/15155175/QSO-Tactical-Response-Unit))", color=ErrorCOL), ephemeral=True)
        
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
