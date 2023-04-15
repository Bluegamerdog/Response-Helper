import discord
import asyncio
import math
from discord.ext import commands
from discord import app_commands
import datetime
from Database_Functions.MaindbFunctions import *
from Functions.mainVariables import *
from Functions.permFunctions import *
#from Functions.randFunctions import 
from Functions.trelloFunctions import (create_response_card, get_members, get_member)

truAccept = discord.PartialEmoji(name="trubotAccepted", id=1096225940578766968)


class testingCmds(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="trello_testing", description="Trello")
    @app_commands.choices(op_type=[
        app_commands.Choice(name="ALPHA", value="ALPHA"),
        app_commands.Choice(name="BRAVO", value="BRAVO"),
        app_commands.Choice(name="CHARLIE", value="CHARLIE"),
        app_commands.Choice(name="DELTA-CHARLIE", value="DELTA-CHARLIE"),
        app_commands.Choice(name="ECHO", value="ECHO"),
        app_commands.Choice(name="DELTA-ECHO", value="DELTA-ECHO"),
        app_commands.Choice(name="FOXTROT", value="FOXTROT"),
        app_commands.Choice(name="DELTA-FOXTROT", value="DELTA-FOXTROT"),
        app_commands.Choice(name="GOLF", value="GOLF"),
        app_commands.Choice(name="DELTA-GOLF", value="DELTA-GOLF"),
        app_commands.Choice(name="HOTEL", value="HOTEL"),
        ])
    async def testing(self, interaction: discord.Interaction, op_type:app_commands.Choice[str], unix_start:str, length:str, purpose:str ,co_host:discord.Member=None, supervisor:discord.Member=None,):
        operation = None #op_type.value + str(random_oppal(3))
        #newcard = await create_op_card(operation=operation, ringleader=interaction.user.display_name, length=length, purpstat=purpose,co_host=co_host, supervisor=supervisor, spontaneus=True)
        #await interaction.response.send_message(f"Success!\n\n{newcard}", suppress_embeds=True)
        pass
        
    @app_commands.command(name="text_testing", description="Texts")
    async def testing2(self, interaction:discord.Interaction, member:discord.Member, reason:str):
        logsch = self.bot.get_channel(1054705433971003412) # 1008449677210943548 #audit-logs
        kickembed = discord.Embed(title=f"<:TRU:1060271947725930496> Kicked TRU Member", description=f"{member.mention} has been kicked from TRU by {interaction.user.mention}.\n\n**Reason:** {reason}", color=DarkRedCOL)
        kickembed.set_thumbnail(url=member.avatar.url)
        kickembed.set_footer(text=f"ID: {member.id} • {datetime.datetime.now().strftime('%m/%d/%Y %H:%M %p')}")
        logmsg = await logsch.send(embed=kickembed)
        await interaction.response.send_message(embed = discord.Embed(title=f"<:dsbbotSuccess:953641647802056756> Member removed", description=f"Successfully removed {member.mention} from TRU.\n\n**Reason:** {reason}\n→ [Audit Log]({logmsg.jump_url})", color=DarkRedCOL),ephemeral=True)
        await member.send(embed = discord.Embed(title=f"You have been kicked from Defensive Squadron Bravo.",description=f"**Reason:** {reason}", color=DarkRedCOL))

    @app_commands.command(name="testing", description="Free")
    async def testing3(self, interaction:discord.Interaction, id:str=None):
        await interaction.response.send_message("<:trubotAccepted:1096225940578766968>")
        
        await interaction.edit_original_response(content=truAccept)

    @app_commands.command(name="length", description="Temporary command to get time/points ratio.")
    async def pointscmddiw(self, interaction:discord.Interaction, length:int):
        if length <= 60:
            amount = 2
        else:
            amount = 2
            extra = math.floor((length - 60+7) / 30)
            amount += extra
        await interaction.response.send_message(f"`{length}` == `{amount}`")
        
    
class patrolCmds(commands.GroupCog, group_name="patrol"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="start", description="Start a log.")
    async def startlog(self, interaction:discord.Interaction):
        loginfo = discord.Embed(title="<:TRU:1060271947725930496> New TRU log!", description=f"**Your log ID is `xxxxxx`.**\nUse this to interact with your log.\n\nEnsure you have joined a voice channel before you begin your patrol!")
        loginfo.add_field(name="Useful links", value="[TRU Infoboard](https://discord.com/channels/949470602366976051/954443926264217701)\nTo be added...\nTo be added...\nTo be added...")
        loginfo.set_footer(text="The current centralised time is " + str(datetime.utcnow()))
        if await interaction.user.send(embed=loginfo):
            startedlog = discord.Embed(title="<:dsbbotSuccess:953641647802056756> Your log has begun!", description="More information has been sent to your DMs.\n*Have a nice patrol!*", color=0x0b9f3f)
            await interaction.response.send_message(embed=startedlog)
        else:
            faillog = discord.Embed(title="<:dsbbotFailed:953641818057216050> Process failed!", description="Something went wrong!", color=0xb89715)
            await interaction.response.send_message(embed=faillog)
