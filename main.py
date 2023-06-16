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
from Functions.permFunctions import *
from Commands.bot_cmds import botCmds, serverconfigCmds, rolebindCmds
from Commands.command_testing import testingCmds, oldpatrolCmds
from Commands.misc_cmds import otherCmds
from Commands.quota_cmds import patrolCmds, viewdataCommand, quotaCmds
from Commands.operator_cmds import operatorCmds
from Commands.TBD_response_cmds import responseCmds
#from Commands.strike_cmds import strikecmds











bot = commands.Bot(command_prefix=">", intents=discord.Intents().all())
tree = app_commands.CommandTree(discord.Client(intents=discord.Intents().all()))
start_time = datetime.datetime.now()
@bot.event  
async def on_ready():
    print("Loading imports...")
    
    #bot_cmds.py
    await bot.add_cog(botCmds(bot, start_time))
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
    #await bot.add_cog(responseCmds(bot))
    
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

  

# INFOBOARD COMMAND #
class InfoboardOptions(discord.ui.Select):
    def __init__(self):
        options=[
            discord.SelectOption(label="TRU Helper Infoboard", description="Information and details about the TRU Helper", value="1"),
            discord.SelectOption(label="Miscellaneous Commands", description="All other commands that are not in a command group.", value="misc"),
            discord.SelectOption(label="Patrol Commands", description="A list of commands related to patrol logs.", value="2"),
            discord.SelectOption(label="Operator Commands", description="A list of commands specific to managing operators within the Unit.", value="3"),
            discord.SelectOption(label="Response Commands", description="Commands used by response leaders for managing responses.", value="4"),
            discord.SelectOption(label="Strike Commands", description="Commands related to issuing strikes or infractions.", value="5"),
            discord.SelectOption(label="Serverconfig Commands", description="Used to configure server settings.", value="6"),
            discord.SelectOption(label="Rolebind Commands", description="All commands for managing rolebinds.", value="7"),
        ]
        super().__init__(placeholder="Select a dropdown...", options=options, min_values=1, max_values=1)
        
    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "1":
            embed = discord.Embed(title="**<:trubotTRU:1096226111458918470> TRU Helper Infoboard**", description="Provided below are infoboards with various commands and information related to the bot. See the dropdown menu below.", color=TRUCommandCOL)
            embed.set_footer(text="TRU Helper | Python Version 1.1")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1096146212245221496/1119208937061879859/TRU.png")
        elif self.values[0] == "misc":
            embed = discord.Embed(title="**Miscellaneous Commands**", description="Here are all other commands that are not in a command group.", color=TRUCommandCOL)
            embed.add_field(name="</viewdata:1116998760178921472>", value="Gets an operators quota information.", inline=False)
            embed.add_field(name="</ping:1096148299058270367>", value="Gets the bots response time in miliseconds.", inline=False)
            embed.add_field(name="</uptime:1096148298919850051>", value="Shows how long the bot has been online for.", inline=False)
            embed.add_field(name="</reload:1096148298919850048>", value="Restarts the bot. [BotDevs only]", inline=False)
            embed.add_field(name="</shutdown:1096148298919850049>", value="Shuts the bot down. [BotDevs only]", inline=False)
            embed.add_field(name="", value="More to be added...", inline=False)
            ###       
        elif self.values[0] == "2":
            embed = discord.Embed(title="**Patrol Commands**", description="This command group is limited to Operators and above.", color=TRUCommandCOL)
            embed.add_field(name="</patrol start:1101469326097264693>", value="Used to start a new patrol log.", inline=False)
            embed.add_field(name="</patrol end:1101469326097264693>", value="Used to end an on-going patrol log.", inline=False)
            embed.add_field(name="</patrol cancel:1101469326097264693>", value="Used to cancel an on-going patrol log.", inline=False)
            embed.add_field(name="</patrol overview:1101469326097264693>", value="Used to view a certain or some recent patrol logs.", inline=False)
        elif self.values[0] == "3":
            embed = discord.Embed(title="**Operator Commands**", description="This command group is used the general managment of the Unit's members.", color=TRUCommandCOL)
            embed.add_field(name="</operator register:1119208502674595850>", value="Registers and operator and adds them to the database.", inline=False)
            embed.add_field(name="</operator update:1119208502674595850>", value="Updated a registed operators data in the database.", inline=False)
            embed.add_field(name="</operator view:1119208502674595850>", value="Gives database information about an operator.", inline=False)
            embed.add_field(name="</operator remove:1119208502674595850>", value="Removed a registed operator from the database. [TRUCapt+]", inline=False)
            embed.add_field(name="</operator rank:1119208502674595850>", value="Sets an operator to the specified rank. [TRUCapt+]", inline=False)
        elif self.values[0] == "4":
            embed = discord.Embed(title="**Response Commands**", description="This command group is limited to Vanguard Officers and above.", color=TRUCommandCOL)
            embed.add_field(name="To be added...", value="", inline=False)
            ###
        elif self.values[0] == "5":
            embed = discord.Embed(title="**Strike Commands**", description="TRU Leadership and above has access to these. They are represented by the color black.", color=HRCommandsCOL)
            embed.add_field(name="/strike overview", value="Gets a list of strikes for a specific operator.", inline=False)
            embed.add_field(name="/strike view", value="Gets details about a specific strike.", inline=False)
            embed.add_field(name="/strike give", value="Gives an operator a strike.", inline=False)
            embed.add_field(name="/strike delete", value="Deleted a strike using the ID.", inline=False)
        elif self.values[0] == "6":
            embed = discord.Embed(title="**Serverconfig Commands**", description="Only <@&1099648545314848858>s have access to these.", color=HRCommandsCOL)
            embed.add_field(name="</serverconfigs set:1101469326097264691>", value="Sets and links up specific permissions and channels in a database.", inline=False)
            embed.add_field(name="</serverconfigs edit:1101469326097264691>", value="Updates existing server configurations.", inline=False)
            embed.add_field(name="</serverconfigs view:1101469326097264691>", value="Provides all set server configurations for that server.", inline=False)
        elif self.values[0] == "7":
            embed = discord.Embed(title="**Rolebind Commands**", description="Only <@&1099648545314848858>s have access to these.", color=HRCommandsCOL)
            embed.add_field(name="</rolebind add:1101469326097264692>", value="Adds a discord-roblox rolebind to the database.", inline=False)
            embed.add_field(name="</rolebind remove:1101469326097264692>", value="Deletes an existing rolebind from the database.", inline=False)
            embed.add_field(name="</rolebind overview:1101469326097264692>", value="Provies a list of all set rolebinds.", inline=False)
        
        await interaction.response.edit_message(embed=embed)
        
class InfoboardView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(InfoboardOptions())

@bot.tree.command(name="infoboard",description="Shows bot information and a list of commands.")
async def infoboard(interaction: discord.Interaction):
    embed = discord.Embed(title="**<:trubotTRU:1096226111458918470> TRU Helper Infoboard**", description="Provided below are infoboards with various commands and information related to the bot. See the dropdown menu below.", color=TRUCommandCOL)
    embed.set_footer(text="TRU Helper | Python Version 1.1")
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1096146212245221496/1119208937061879859/TRU.png")
    await interaction.response.send_message(embed=embed, view=InfoboardView())



bot.run(TOKEN)