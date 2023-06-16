import discord
import datetime
import time
import random
from discord.ext import commands
from discord import app_commands

from Functions.mainVariables import *
from Functions.permFunctions import *
from Functions.randFunctions import *

### COMPLETED ####

class otherCmds(commands.Cog):
    def __init__(self, bot: commands.Bot, start_time):
        self.bot = bot
        self.start_time = start_time

    @app_commands.command(name="uptime", description="Shows how long the bot has been online for.")
    async def uptime(self, interation:discord.Interaction):
        current_time = datetime.datetime.now()
        uptime = current_time - self.start_time
        unix_time = int(time.mktime(self.start_time.timetuple()))
        await interation.response.send_message(embed=discord.Embed(color=TRUCommandCOL,title="TRU Helper Uptime", description=f"➥ TRU Helper started <t:{unix_time}:R> (<t:{unix_time}>)"))

    @app_commands.command(name="ping",description="Shows the bot's response time.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🏓Pong! Took `{round(self.bot.latency * 1000)}`ms")


