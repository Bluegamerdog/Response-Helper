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
from Functions.formattingFunctions import embedBuilder
from Functions.mainVariables import *
from Functions.randFunctions import (change_nickname, get_user_id_from_link,
                                     in_roblox_group, get_promotion_message, is_valid_profile_link)
from Functions.rolecheckFunctions import *

roblox_client = Client("_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_D5064A0C1DB1D5FD5C66ED677C3B797A10523AEE48D18912BB5D6F2E08BE04F39C4E056585CDE8C410971D4BE9C674A66E86C9BD29BBC99B41A5720149F0C5B2C16FF8088846DDB8004B1C206F0B3FB837A4263111612CA93E448C7AC999EC9D326AB762CB74A7BB0B8D246F192BAC4C5139D77CC634D9C3F06A836D43712B6FA65E7DD315AB471C41A0CDD683A633624BFE8A91DD3BA85F34612556A0525401AD16743318C61B208D1A894FFAB372E157342BF65B78E06FB33543F74A8A600256582EBA8A56062BEA431246332E270A4EA1F77B811BBB7678C3A10020251B8FBF3D015BD391A219400A803A9A07B5B971785639B08E9F1E85230E630D7D1680E1AA7D9815C4C9DA3D9FE5064EFECDB50123CD8E6E7A7527624721D77F7D2542B833E49C14F35356C57F74AF16B4A2E553BBB56B1398F7F8F8F4E141C149D7499DE92ABFDA759F3634D395FB1333BC1F2709919B573DE87E1ED3412022B26BEF5544DD44F23BFE968E6BA37DCCDA3B87060A1930")

class operatorCmds(commands.GroupCog, group_name='operator'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @app_commands.command(name="register", description="Add a new operator to the registry.")
    async def operative_register(self, interaction: discord.Interaction, profilelink: str, user:discord.Member=None):
        serverConfig = await fetch_config(interaction=interaction)
        if TRUMember(user=interaction.user):
            
            if user and user != interaction.user and not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.commandRole))):
                return await interaction.response.send_message(embed = embedBuilder(responseType="perms", embedDesc="Only TRU leadership and above may register other users."))

                    # Check if the profile link is a valid Roblox profile link
            if not is_valid_profile_link(profilelink):
                return await interaction.response.send_message(embed=embedBuilder(responseType="err", embedDesc="Invalid Roblox profile link. Please provide a valid link."))
            
            if await getOperator(user.id if user else interaction.user.id):
                return await interaction.response.send_message(embed=embedBuilder(responseType="err", embedDesc=f"{user.mention} is already registered." if user else f"You are already registered"))
            
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
        
        responseEmbed = embedBuilder(responseType="succ", embedTitle="User found!", embedDesc=f"Here is {user.mention}'s registry information.")
        responseEmbed.add_field(name="Roblox Username", value=f"[{roblox_user.display_name} (@{roblox_user.name})]({requested_operative.profileLink})", inline=False)
        responseEmbed.add_field(name="TRU Rank", value=f"{requested_operative.rank}")
        if userSuspended(user):
            responseEmbed.add_field(name="Suspended", value="True")
        return await interaction.response.send_message(embed=responseEmbed)
