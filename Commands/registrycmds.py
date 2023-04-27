import discord
import asyncio
from discord.ext import commands
from discord import app_commands
from Database_Functions.UserdbFunction import *
from Functions.mainVariables import *
from Functions.permFunctions import *
from Functions.randFunctions import *

## Awaiting transfer ##

class RegistryCmds(commands.GroupCog, group_name='registry'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    

    # Need to transfer and add from newDBCommands.py
    # Need update, remove and maybe view as well for this
