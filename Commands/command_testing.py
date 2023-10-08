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
# Embed types: Success, Warning, Error
from Functions.formattingFunctions import *
from Functions.formattingFunctions import embedBuilder
from Functions.mainVariables import *
from Functions.rolecheckFunctions import *
from Functions.randFunctions import *
from Functions.trelloFunctions import (create_response_card, get_card_comments, get_comments_timeframe)
import requests
import datetime

# Just to test random shit

class testingCmds(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="trello_testing", description="Testing trello functions")
    async def trello_testing(self, interaction:discord.Interaction, user:discord.Member = None, start_time:str = None, end_time:str = None):
        if DEVACCESS(interaction.user):
            return await interaction.response.send_message("This command is currently not in use!", ephemeral=True)
        
        
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