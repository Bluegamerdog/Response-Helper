import discord
import asyncio
import math
from discord.ext import commands
from discord import app_commands
import datetime

from Functions.mainVariables import *
from Functions.permFunctions import *
#from Functions.randFunctions import 
import uuid
from Functions.trelloFunctions import (create_response_card, get_members, get_member)

truAccept = discord.PartialEmoji(name="trubotAccepted", id=1096225940578766968)

# Just to test random shit

class testingCmds(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="trello_testing", description="Testing trello functions")
    async def trello_testing(self, interaction:discord.Interaction):
        return await interaction.response.send_message("This command is currently not in use!", ephemeral=True)
        
    @app_commands.command(name="text_testing", description="Previewing text and embeds")
    async def testing2(self, interaction:discord.Interaction, member:discord.Member, reason:str):
        return await interaction.response.send_message("This command is currently not in use!", ephemeral=True)
        logsch = self.bot.get_channel(1054705433971003412) # 1008449677210943548 #audit-logs
        kickembed = discord.Embed(title=f"<:TRU:1060271947725930496> Kicked TRU Member", description=f"{member.mention} has been kicked from TRU by {interaction.user.mention}.\n\n**Reason:** {reason}", color=DarkRedCOL)
        kickembed.set_thumbnail(url=member.avatar.url)
        kickembed.set_footer(text=f"ID: {member.id} • {datetime.datetime.now().strftime('%m/%d/%Y %H:%M %p')}")
        logmsg = await logsch.send(embed=kickembed)
        await interaction.response.send_message(embed = discord.Embed(title=f"<:trubotAccepted:1096225940578766968> Member removed", description=f"Successfully removed {member.mention} from TRU.\n\n**Reason:** {reason}\n→ [Audit Log]({logmsg.jump_url})", color=DarkRedCOL),ephemeral=True)
        await member.send(embed = discord.Embed(title=f"You have been kicked from Defensive Squadron Bravo.",description=f"**Reason:** {reason}", color=DarkRedCOL))

    @app_commands.command(name="testing", description="Current: responseIDs")
    async def testing3(self, interaction:discord.Interaction):
        return await interaction.response.send_message("This command is currently not in use!", ephemeral=True)
        
    
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
