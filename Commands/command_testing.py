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
from Functions.trelloFunctions import (create_response_card, get_member,
                                       get_members, get_card_comments, get_total_comment_amount, get_comments_timeframe)

truAccept = discord.PartialEmoji(name="trubotAccepted", id=1096225940578766968)

# Just to test random shit

class testingCmds(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="trello_testing", description="Testing trello functions")
    async def trello_testing(self, interaction:discord.Interaction, user:discord.Member = None, start_time:str = None, end_time:str = None):
        #return await interaction.response.send_message("This command is currently not in use!", ephemeral=True)
        
        if user == None:
            user = interaction.user
        operativeName = user.nick.rsplit(maxsplit=1)[-1]
        comments = get_card_comments(operativeName)
        
        if start_time is None and end_time is None:
            amount = get_total_comment_amount(comments)
        elif start_time:
            amount = get_comments_timeframe(comments, start_time, end_time)
        
        await interaction.response.send_message(f"{operativeName} || <t:{start_time}> - <t:{end_time}>\n\nResponses attended: {amount}")
        
    @app_commands.command(name="text_testing", description="Previewing text and embeds")
    async def testing2(self, interaction:discord.Interaction, user:discord.Member = None):
        #return await interaction.response.send_message("This command is currently not in use!", ephemeral=True
        await interaction.response.send_message(embed=embedBuilder(responseType="cust", embedTitle="Testing"), ephemeral=True)
        


    @app_commands.command(name="testing", description="Current: time")
    async def testing3(self, interaction:discord.Interaction):
        #return await interaction.response.send_message("This command is currently not in use!", ephemeral=True)
        quotadata = await get_all_quota_data()
        await interaction.response.send_message(f"{quotadata}", ephemeral=True)
        
        
        
        
    
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
