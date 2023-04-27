import math
import re
import discord
import os
from discord.ext import commands
from discord import app_commands
from discord import ui
import datetime
from Functions.mainVariables import *
from Functions.permFunctions import *
import Database_Functions.PrismaFunctions as dbFuncs
from Database_Functions.PrismaFunctions import *
#from Functions.formattingFunctions import embedBuilder

### Completed? ###
# Need to add some error handling like checking if the user already has the requested medal/role.
        
class medalButtons(discord.ui.View):
    def __init__(self, requested_medal:discord.Role, serverconfigs):
        super().__init__()
        discord.ui.View.timeout = None
        self.requested_medal = requested_medal
        self.serverconfigs = serverconfigs
    
    @discord.ui.button(emoji="<:trubotAccepted:1096225940578766968>", label="Accept", style=discord.ButtonStyle.grey)
    async def AcceptButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(self.serverconfigs.commandRole))):
            return
        else:
            try:
                await interaction.message.interaction.user.add_roles(self.requested_medal)
                embed = interaction.message.embeds[0]
                embed.title= embed.title.replace("<:trubotBeingLookedInto:1099642414303559720>", "<:trubotAccepted:1096225940578766968> Accepted")
                embed.color = SuccessCOL
                embed.set_footer(text=f"Accepted by {interaction.user.display_name} • {datetime.now().strftime('%d.%m.%y at %H:%M')}")
                await interaction.message.edit(embed=embed, view=None)
                await interaction.response.defer()
            except Exception as e:
                await interaction.response.send_message(f"{e}", ephemeral=True)

    @discord.ui.button(emoji="<:trubotDenied:1099642433588965447>", label="Deny", style=discord.ButtonStyle.grey)
    async def DenyButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(self.serverconfigs.commandRole))):
            return
        else:
            try:
                embed = interaction.message.embeds[0]
                embed.title= embed.title.replace("<:trubotBeingLookedInto:1099642414303559720>", "<:trubotDenied:1099642433588965447> Denied")
                embed.color = DarkRedCOL
                embed.set_footer(text=f"Denied by {interaction.user.display_name} • {datetime.now().strftime('%d.%m.%y at %H:%M')}")
                await interaction.message.edit(embed=embed, view=None)
                await interaction.response.defer()
            except Exception as e:
                await interaction.response.send_message(f"{e}", ephemeral=True)
        
    @discord.ui.button(emoji="❌", label="Cancel", style=discord.ButtonStyle.grey)
    async def CancelButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.user == interaction.message.interaction.user:
            await interaction.message.delete()
        else:
            return

class RequestCmds(commands.GroupCog, group_name='request'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @app_commands.command(name="medal", description="Request a medal within TRU.")
    @app_commands.describe(medal="Which medal are you requesting?", evidence_link="You only need to fill one evidence prompt! This one is for links.", evidence_file="You only need to fill one evidence prompt! This one is for links.", completion_date="When did you take the evidence? [MM/DD/YYYY or DD.MM/YYYY]")
    @app_commands.choices(medal=[
        app_commands.Choice(name="Rapid Multikill", value="Rapid Multikill"),
        app_commands.Choice(name="Duo Defense", value="Duo Defense"),
        app_commands.Choice(name="Swift Sweep", value="Swift Sweep"),
        app_commands.Choice(name="Key Guardian", value="Key Guardian"),
        app_commands.Choice(name="Glass Electrician", value="Glass Electrician"),
        app_commands.Choice(name="Cavern Champion", value="Cavern Champion")])
    async def request_ex(self, interaction: discord.Interaction, medal:app_commands.Choice[str],completion_date:str ,evidence_link:str=None, evidence_file:discord.Attachment=None):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.logPermissionRole))):
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:trubotDenied:1099642433588965447> Missing permissions!", description=f"Only TRU Operators or above may request medals."), ephemeral=True)
        else:
            requested_role:discord.Role = discord.utils.get(interaction.guild.roles, name=f"{medal.value}")
            request_embed = discord.Embed(title="<:trubotBeingLookedInto:1099642414303559720> Medal Request", description=f"**{interaction.user.nick}** is requesting the {requested_role.mention} medal.", color=discord.Color.dark_theme())
            request_embed.add_field(name="Date of completion", value=completion_date)
            if evidence_file:
                filename = evidence_file.filename
                _, extension = os.path.splitext(filename)
                if extension not in ['.mp4', '.mov', '.avi']:
                    return await interaction.response.send_message(embed=discord.Embed(title="<:trubotDenied:1099642433588965447> Invalid file type!", description="Only MP4, MOV, and AVI files are accepted as evidence.", color=ErrorCOL), ephemeral=True)
                request_embed.add_field(name="Evidence", value=f"[File download link]({evidence_file.url})")
            elif evidence_link:
                if len(evidence_link) > 30:
                    evidence_link = f"[LONGASS Link]({evidence_link})"
                request_embed.add_field(name="Evidence", value=evidence_link)
            else:
                return await interaction.response.send_message(embed=discord.Embed(title="<:trubotDenied:1099642433588965447> No evidence found!", description="You need to fill out one of the two evidence prompts. Either in form of a link or a file.", color=ErrorCOL), ephemeral=True)
            return await interaction.response.send_message(embed=request_embed, view=medalButtons(requested_role, serverConfig))
