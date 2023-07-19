import asyncio
import datetime
import math
import time
#from Functions.randFunctions import 
import uuid

import discord
from discord import app_commands
from discord.ext import commands

import Database_Functions.PrismaFunctions as dbFuncs
import Database_Functions.PrismaFunctions as DBFunc
from Database_Functions.PrismaFunctions import *
from Database_Functions.UserdbFunction import *
from Functions import rolecheckFunctions
# Embed types: Success, Warning, Error
from Functions.formattingFunctions import *
from Functions.formattingFunctions import embedBuilder
from Functions.mainVariables import *
from Functions.rolecheckFunctions import *
from Functions.randFunctions import *
from Functions.trelloFunctions import (create_response_card, get_card_comments, get_comments_timeframe)

truAccept = discord.PartialEmoji(name="trubotAccepted", id=1096225940578766968)


import requests
import datetime

def get_last_rank_update(group_id, user_id):
    url = f"https://groups.roblox.com/v1/groups/{group_id}/users/{user_id}"
    response = requests.get(url)
    data = response.json()
    
    if "updated" in data:
        last_updated = data["updated"]
        last_updated_timestamp = datetime.datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%S.%fZ")
        return last_updated_timestamp
    else:
        return None

# Just to test random shit

class testingCmds(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="trello_testing", description="Testing trello functions")
    async def trello_testing(self, interaction:discord.Interaction, user:discord.Member = None, start_time:str = None, end_time:str = None):
        if DEVACCESS(interaction.user):
            return await interaction.response.send_message("This command is currently not in use!", ephemeral=True)

    @app_commands.command(name="forcecancel", description="Testing")
    async def cancel_log_force(self, interaction:discord.Interaction, user:discord.Member):
        if DEVACCESS(interaction.user):
            #return await interaction.response.send_message("This command is currently not in use!", ephemeral=True)
            results1, result2 = await forceCancellog(user)
            if result2 == True:
                embed = embedBuilder("succ", f"Log was cancelled and deleted.\n\n{results1}")
            else:
                embed = embedBuilder("err", f"{results1}")
            return await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="text_testing", description="Previewing text and embeds")
    @app_commands.choices(rank=[
    app_commands.Choice(name="totally a real rank", value="25"),
    app_commands.Choice(name="Vanguard Officer", value="20"),
    app_commands.Choice(name="Vanguard", value="15"),
    app_commands.Choice(name="Elite Operator", value="5"),
    app_commands.Choice(name="Senior Operator", value="4"),
    app_commands.Choice(name="Operator", value="3"),
    app_commands.Choice(name="Entrant", value="1"),])
    async def testing2(self, interaction:discord.Interaction, rank:app_commands.Choice[str]):
        #return await interaction.response.send_message("This command is currently not in use!", ephemeral=True
        if DEVACCESS(interaction.user):
            await interaction.response.send_message(embed=discord.Embed(title="<a:trubotCelebration:1099643172012949555> TRU Promotion!", description=f"You have been promoted from **placeholder** to **{rank.name}**!\n\n{get_promotion_message(str(rank.name))}", color=DarkGreenCOL), ephemeral=True)
        


    @app_commands.command(name="testing", description="Current: roblox group")
    async def testing3(self, interaction:discord.Interaction):
        if DEVACCESS(interaction.user):
            #return await interaction.response.send_message("This command is currently not in use!", ephemeral=True)
            group_id = 15155175  # Replace with your Roblox group ID
            user_id = 334150937  # Replace with the user ID you want to check

            last_update = get_last_rank_update(group_id, user_id)
            if last_update is not None:
                return await interaction.response.send_message(f"Last Rank Update: {last_update}", ephemeral=True )
            else:
                return await interaction.response.send_message("Failed to retrieve rank information.", ephemeral=True)
            
            #uotadata = await get_all_quota_data()
            #await interaction.response.send_message(f"{quotadata}", ephemeral=True)
        
        
        
        
    
class oldpatrolCmds(commands.GroupCog, group_name="patrol"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="start", description="Start a log.")
    async def startlog(self, interaction:discord.Interaction):
        loginfo = discord.Embed(title="<:TRU:1060271947725930496> New TRU log!", description=f"**Your log ID is `xxxxxx`.**\nUse this to interact with your log.\n\nEnsure you have joined a voice channel before you begin your patrol!")
        loginfo.add_field(name="Useful links", value="[TRU Infoboard](https://discord.com/channels/949470602366976051/954443926264217701)\nTo be added...\nTo be added...\nTo be added...")
        loginfo.set_footer(text="The current centralised time is " + str(datetime.utcnow()))
        if await interaction.user.send(embed=loginfo):
            startedlog = discord.Embed(title="<:trubotAccepted:1096225940578766968> Your log has begun!", description="More information has been sent to your DMs.\n*Have a nice patrol!*", color=0x0b9f3f)
            await interaction.response.send_message(embed=startedlog)
        else:
            faillog = discord.Embed(title="<:dsbbotFailed:953641818057216050> Process failed!", description="Something went wrong!", color=0xb89715)
            await interaction.response.send_message(embed=faillog)
