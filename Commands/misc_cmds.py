import discord
import datetime
import time
from datetime import timedelta
from discord.ext import commands
from discord import app_commands
from discord.utils import sleep_until

from Functions.mainVariables import *
from Functions.rolecheckFunctions import *
from Functions.randFunctions import *
from Database_Functions.PrismaFunctions import *
from Database_Functions.UserdbFunction import *


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
            embed.add_field(name="</infoboard:1096148298919850046>", value="Provides lists of all available commands.", inline=False)
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
            embed = discord.Embed(title="**Operator Commands**", description="This command group is used for the general managment of the Unit's members.", color=TRUCommandCOL)
            embed.add_field(name="</operator register:1119208502674595850>", value="Registers and operator and adds them to the database.", inline=False)
            embed.add_field(name="</operator update:1119208502674595850>", value="Updated a registed operators data in the database.", inline=False)
            embed.add_field(name="</operator view:1119208502674595850>", value="Gives database information about an operator.", inline=False)
            embed.add_field(name="</operator remove:1119208502674595850>", value="Removed a registed operator from the database. [TRUCapt+]", inline=False)
            embed.add_field(name="</operator rank:1119208502674595850>", value="Sets an operator to the specified rank. [TRUCapt+]", inline=False)
        elif self.values[0] == "4":
            embed = discord.Embed(title="**Response Commands**", description="This command group is mostly limited to Vanguard Officers and above.", color=TRUCommandCOL)
            embed.add_field(name="</response cancel:1120762927306248284>", value="Used to cancel a scheduled or spontanteous response.", inline=False)
            embed.add_field(name="</response commence:1120762927306248284>", value="Used to commence a scheduled response.", inline=False)
            embed.add_field(name="</response schedule:1120762927306248284>", value="Allows response leaders to automatically schedule a response.", inline=False)
            embed.add_field(name="</response spontaneous:1120762927306248284>", value="Response leaders use this command to start a spontaneous responses.", inline=False)
            embed.add_field(name="</response view:1120762927306248284>", value="Provides a list of recent responses or responses specific to a response leaders.", inline=False)
            embed.add_field(name="</response delete:1120762927306248284>", value="Used to delete a response from the database. [BotDevs only]", inline=False)
            embed.add_field(name="</response create:1120762927306248284>", value="Used to manually add responses to the database. [BotDevs only]", inline=False)
        elif self.values[0] == "5":
            embed = discord.Embed(title="**Strike Commands**", description="TRU Leadership and above has access to these. They are represented by the color black.", color=HRCommandsCOL)
            embed.add_field(name="", value="To be added...", inline=False)
            embed.add_field(name="/strike overview", value="Gets a list of strikes for a specific operator.", inline=False)
            embed.add_field(name="/strike view", value="Gets details about a specific strike.", inline=False)
            embed.add_field(name="/strike give", value="Gives an operator a strike.", inline=False)
            embed.add_field(name="/strike add", value="Adds a strike directly to the database, without DMing the operator recieving the strike.", inline=False)
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
        self.timeout = None
        self.add_item(InfoboardOptions())



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
        
    @app_commands.command(name="infoboard",description="Shows bot information and a list of commands.")
    async def infoboard(self, interaction: discord.Interaction):
        embed = discord.Embed(title="**<:trubotTRU:1096226111458918470> TRU Helper Infoboard**", description="Provided below are infoboards with various commands and information related to the bot. See the dropdown menu below.", color=TRUCommandCOL)
        embed.set_footer(text="TRU Helper | Python Version 1.1")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1096146212245221496/1119208937061879859/TRU.png")
        await interaction.response.send_message(embed=embed, view=InfoboardView())  
        



