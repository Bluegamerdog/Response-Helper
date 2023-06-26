import asyncio
import datetime
import json
import platform
import random
import re
import string
import sys
import time
import discord
import time
from colorama import Back, Fore, Style
from discord import app_commands
from discord.ext import commands



from Functions.mainVariables import *
from Functions.rolecheckFunctions import *
from Commands.bot_cmds import botCmds, serverconfigCmds, rolebindCmds
from Commands.command_testing import testingCmds, oldpatrolCmds
from Commands.misc_cmds import otherCmds
from Commands.quota_cmds import patrolCmds, viewdataCommand, quotaCmds
from Commands.operator_cmds import operatorCmds
from Commands.response_cmds import responseCmds
#from Commands.strike_cmds import strikecmds











bot = commands.Bot(command_prefix=">", intents=discord.Intents().all())
tree = app_commands.CommandTree(discord.Client(intents=discord.Intents().all()))
start_time = datetime.datetime.now()
@bot.event  
async def on_ready():
    print("Loading imports...")
    
    #bot_cmds.py
    await bot.add_cog(botCmds(bot))
    await bot.add_cog(serverconfigCmds(bot))
    await bot.add_cog(rolebindCmds(bot))
    
    #misc_cmds.py
    await bot.add_cog(otherCmds(bot, start_time))
    
    #quota_cmds.py
    await bot.add_cog(patrolCmds(bot))
    await bot.add_cog(quotaCmds(bot))
    await bot.add_cog(viewdataCommand(bot))
    
    #operator_cmds.py
    await bot.add_cog(operatorCmds(bot))
    
    #TBA_response_cmds.py
    await bot.add_cog(responseCmds(bot))
    
    #command_testing.py
    await bot.add_cog(testingCmds(bot))
    #await bot.add_cog(oldpatrolCmds(bot))

    #strike_cmds.py
    #await bot.add_cog(strikeCmds(bot))
    
    

    
    
    # Console output
    prfx = (Back.BLACK + Fore.BLUE) + Back.RESET + Fore.WHITE + Style.BRIGHT
    print(prfx + "|| Logged in as " + Fore.BLUE + bot.user.name + "  at  " + time.strftime("%H:%M:%S UTC", time.gmtime()))
    print(prfx + "|| Bot ID: " + Fore.BLUE + str(bot.user.id))
    print(prfx + "|| Discord Version: " + Fore.BLUE + discord.__version__)
    print(prfx + "|| Python Version: " + Fore.BLUE + str(platform.python_version()))
    print(prfx + "Syncing commands...")
    try:
        synced = await bot.tree.sync()
        print("\033[2K" + prfx + f"|| Slash CMDs Synced: {Fore.BLUE}{len(synced)} Commands")
    except Exception as e:
        print(f"Error syncing commands: {e}")
        synced = []
    # Quota and notes output
    print(prfx + f"|| That is all for now. (Remove quota blocks for now)")
    
    # Embed message
    embed = discord.Embed(title="Bot Startup Info • InDev", color=discord.Color.green())
    embed.add_field(name="Bot Name", value=bot.user.name, inline=True)
    embed.add_field(name="Bot ID", value=bot.user.id, inline=True)
    embed.add_field(name="Runtime Information", value=f"Discord Version: {discord.__version__} || Python Version: {platform.python_version()}", inline=False)
    embed.add_field(name="Synced Slash Commands", value=len(synced), inline=False)
    embed.add_field(name="Notes", value="That is all for now. (Remove quota blocks for now).", inline=False)
    
    channel = bot.get_channel(1096146385830690866)  # Startup-channel ID
    await channel.send(embed=embed)
with open('token.json', 'r') as f:
    data = json.load(f)
    TOKEN = data['TOKEN']

  
bot.run(TOKEN)