import discord
from colorama import Back, Fore, Style
from discord.ext import commands
from discord import app_commands
from discord import ui
from Database_Functions.MaindbFunctions import *
from Functions.mainVariables import *
from Functions.permFunctions import *
from Functions.randFunctions import (getrank)
from Database_Functions.OperationdbFunctions import (op_get_info, op_create_spontaneous, op_create_scheduled, op_cancel, op_conclude, op_edit, generate_pals)
from Database_Functions.UserdbFunction import (get_roblox_link)

### REDO ####

class DossierModal(ui.Modal, title="Operation Dossier"):
    def __init__(self, operation:str, picture:discord.Attachment, ringleader:discord.Member, attendees:str, co_host:str=None, soups:str=None):
        super().__init__(timeout=None)
        self.operation = operation
        self.picture = picture
        self.ringleader = ringleader
        self.attendees = attendees
        self.co_host = co_host
        self.soups = soups
        self.opinfo = op_get_info(operation)
        
    summary = ui.TextInput(label='Operation Summary', style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        dossierem = discord.Embed(title=f"OPERATIONS DOSSIER: {self.opinfo[0]} {self.opinfo[1]}", color=TRUCommandCOL)
        dossierem.add_field(name="", value=f"`Time & Date:` <t:{self.opinfo[2]}:t> | <t:{self.opinfo[2]}:d>", inline=False)
        if self.co_host == None and self.soups == None:
            dossierem.add_field(name="", value=f"`Ringleader:` {self.ringleader.mention}\n`Attendees:` {self.attendees}", inline=False)
        elif self.co_host !=None and self.soups==None:
            dossierem.add_field(name="", value=f"`Ringleader:` {self.ringleader.mention} || `Co-hosts:` {self.co_host}\n`Attendees:` {self.attendees}", inline=False)
        elif self.soups !=None and self.co_host==None:
            dossierem.add_field(name="", value=f"`Ringleader:` {self.ringleader.mention} || `Supervisors:` {self.soups}\n`Attendees:` {self.attendees}", inline=False)
        elif self.soups != None and self.co_host != None:
            dossierem.add_field(name="", value=f"`Ringleader:` {self.ringleader.mention} || `Co-hosts:` {self.co_host}\n`Supervisors:` {self.soups}\n`Attendees:` {self.attendees}", inline=False)
            
        dossierem.add_field(name="", value=f"\n`Operation Summary:` {self.summary}", inline=False)
        dossierem.set_image(url=self.picture)
        await interaction.response.send_message(embed=dossierem)
        await interaction.followup.send(embed=discord.Embed(description="<#1058758885361594378> ", color=TRUCommandCOL), ephemeral=True)


class OperationCmds(commands.GroupCog, group_name='operation'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @app_commands.command(name="announce", description="Used to schedule up-coming operations.")
    @app_commands.describe(type="Which operation type?", unix_start="Provide the start time in form of an Unix code.", length="How long will your operation be? Example: '45 minutes'", co_host="Is anyone planed to co-host your operation?",supervisor="Is anyone planned to supervise your operation?")
    @app_commands.choices(type=[
        app_commands.Choice(name="ALPHA", value="ALPHA"),
        app_commands.Choice(name="DELTA-ALPHA", value="DELTA-ALPHA"),
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
    async def announce(self, interaction: discord.Interaction, type:app_commands.Choice[str], unix_start:int, length:str, co_host:discord.Member=None, supervisor:discord.Member=None,):
        user = interaction.user
        if ITMR_A(user):
            operation_PLs = generate_pals(3)
            dsbrole:discord.Role = discord.utils.get(interaction.guild.roles, name="DSB")
            operationinfo = discord.Embed(title=f"<:DSB:1060271947725930496> New Scheduled Operation!", description=f"Operation **`{type.value} {operation_PLs}`** has been scheduled and will take place <t:{unix_start}:R>.", color=TRUCommandCOL)
            operationinfo.add_field(name="", value="", inline=False)
            if co_host and supervisor:
                co_host=co_host.display_name
                supervisor=supervisor.display_name
                operationinfo.add_field(name="Operation Details", value=f"`Time & Date` - <t:{unix_start}:f>\n`Ringleader` - {str(user.display_name)}\n`Co-host` - {co_host}\n`Soupervisor` - {supervisor}\n`Length` - The operation will last for {length}.\n`Trello Card` - Soon:tm:")
            elif co_host:
                co_host=co_host.display_name
                operationinfo.add_field(name="Operation Details", value=f"`Time & Date` - <t:{unix_start}:f>\n`Ringleader` - {str(user.display_name)}\n`Co-host` - {co_host}\n`Length` - The operation will last for {length}.\n`Trello Card` - Soon:tm:")
            elif supervisor:
                supervisor=supervisor.display_name
                operationinfo.add_field(name="Operation Details", value=f"`Time & Date` - <t:{unix_start}:f>\n`Ringleader` - {str(user.display_name)}\n`Soupervisor` - {supervisor}\n`Length` - The operation will last for {length}.\n`Trello Card` - Soon:tm:")
            else:
                operationinfo.add_field(name="Operation Details", value=f"`Time & Date` - <t:{unix_start}:f>\n`Ringleader` - {str(user.display_name)}\n`Length` - The operation will last for {length}.\n`Trello Card` - Soon:tm:")
            operationinfo.add_field(name="", value="", inline=False)
            operationinfo.add_field(name="Able to attend?", value="React below to confirm your attendance.", inline=False)
            allowed_mentions = discord.AllowedMentions.all()
            await interaction.response.send_message(dsbrole, allowed_mentions=None)
            msg_sent = await interaction.edit_original_response(embed=operationinfo)
            op_create_scheduled(type.value, operation_PLs, unix_start, "link", msg_sent.id)
            await msg_sent.add_reaction("<:DSB:1060271947725930496>")
        else:
            embed = discord.Embed(color=ErrorCOL, description=f"You do not have permission run this command.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="start", description="Used to start scheduled operations as well as spontaneous ones.")
    @app_commands.choices(vc=[
        app_commands.Choice(name="[QSO] On Duty 1", value="937473342884179980"),
        app_commands.Choice(name="[QSO] On Duty 2", value="937473342884179981"),
        app_commands.Choice(name="[QSO] On Duty 3", value="937473342884179982"),
        app_commands.Choice(name="[QSO] On Duty 4", value="937473342884179983"),
        app_commands.Choice(name="[QSO] On Duty 5", value="937473342884179984"),
        app_commands.Choice(name="[QSO] VIP Raid", value="937473342884179985"),
        app_commands.Choice(name="[QSO] Events", value="992865433059340309"),
        app_commands.Choice(name="[DSB] On Duty 1", value="949869157552390154"),
        app_commands.Choice(name="[DSB] On Duty 2", value="949869187168370718"),
        app_commands.Choice(name="[DSB] On Duty 3", value="949869232663986226"),
        app_commands.Choice(name="[DSB] Events", value="950145200087511130"),
        app_commands.Choice(name="[SQD] On Duty 1", value="949470602366976055"),
        app_commands.Choice(name="[SQD] On Duty 2", value="949867772643520522"),
        app_commands.Choice(name="[SQD] On Duty 3", value="949867813789630574"),
        app_commands.Choice(name="[SQD] Events", value="950145105040388137"),
        ])
    @app_commands.choices(op_type=[
        app_commands.Choice(name="ALPHA", value="ALPHA"),
        app_commands.Choice(name="DELTA-ALPHA", value="DELTA-ALPHA"),
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
    async def commence(self, interaction:discord.Interaction, status:str, vc:app_commands.Choice[str], operation_pal:str=None, op_type:str=None):
        user = interaction.user
        if ITMR_A(user):
            dsbrole:discord.Role = discord.utils.get(interaction.guild.roles, name="DSB")
            vc_id_u = int(vc.value)
            profile_link_u = get_roblox_link(interaction.user.id)
            if operation_pal == None and op_type:
                operation_pal = generate_pals(3)
                operationinfo = discord.Embed(title=f"<:DSB:1060271947725930496> Spontaneous operation!", description=f"Operation `{op_type} {operation_pal}` is currently being hosted by **{user.display_name}**.\n\n`Voice Channel` - <#{vc_id_u}>\n`Profile link` - {profile_link_u}\n`Current status` - {status}.", color=TRUCommandCOL)
                allowed_mentions = discord.AllowedMentions.all()
                await interaction.response.send_message(dsbrole, allowed_mentions=None)
                msg_sent = await interaction.edit_original_response(embed=operationinfo)
                op_create_spontaneous(op_type, operation_pal, msg_sent.id)
            else:
                opinfo = op_get_info(operation_pal)
                if opinfo:
                    op_ann = await interaction.channel.fetch_message(opinfo[6])
                    embed = discord.Embed(title=f"<:DSB:1060271947725930496> Scheduled operation!", description=f"Operation `{opinfo[0]} {opinfo[1]}` is now commencing.\n\n`Voice Channel` - <#{vc_id_u}>\n`Profile link` - {profile_link_u}\n`Current status` - {status}", color=TRUCommandCOL)
                    allowed_mentions = discord.AllowedMentions.all()
                    await op_ann.reply(dsbrole, allowed_mentions=None, embed=embed)
                    succemb = discord.Embed(description="Operation started successfully.", color=TRUCommandCOL)
                    await interaction.response.send_message(embed=succemb, ephemeral=True)  
                else:
                    embed = discord.Embed(description=f"Could not find operation `{operation_pal}` not found!", color=ErrorCOL)
                    await interaction.response.send_message(embed=embed, ephemeral=True)   
        else:
            embed = discord.Embed(color=ErrorCOL, description=f"You do not have permission run this command.")
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="end", description="Used to conclude an operations.")
    async def conclude(self, interaction:discord.Interaction, pal:str):
        user = interaction.user
        if DSBMEMBER(user):
            if ITMR_A(user):
                result = op_get_info(pal)
                if result:
                    op_ann = await interaction.channel.fetch_message(result[6])
                    op_emb = op_ann.embeds[0]
                    op_emb.title = "<:DSB:1060271947725930496> Concluded Operation!"
                    embed = discord.Embed(description=f"Operation `{result[0]} {result[1]}` has concluded, thank you for attending.", color=TRUCommandCOL)
                    op_conclude(pal)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    await op_ann.edit(embed=op_emb)
                    await op_ann.reply(embed=embed)
                else:
                    embed = discord.Embed(description=f"Operation with PALs `{pal}` not found!", color=ErrorCOL)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(color=ErrorCOL, description=f"You do not have permission run this command.")
                await interaction.response.send_message(embed=embed)

    @app_commands.command(name="dossier", description="Used to write an operation dossier.")
    @app_commands.describe(pals="Example: XYZ", ringleader="The host of the operation, normally that would be you.", co_hosts="If anyone co-hosted your operation they would go here.", supervisors="If anyone soupervised your operation, they would go here.", attendees="Your attendance list goes here. Make sure to seperate the mentions using a comma.")
    async def dossier(self, interaction:discord.Interaction, pals:str, picture:discord.Attachment, ringleader:discord.Member, attendees:str=None, supervisors:str=None, co_hosts:str=None):
        if ITMR_A(interaction.user):
            if op_get_info(pals) == None:
                embed = discord.Embed(description=f"Operation with PALs `{pals}` not found!", color=ErrorCOL)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                return await interaction.response.send_modal(DossierModal(operation=pals, picture=picture, ringleader=ringleader, co_host=co_hosts, soups=supervisors, attendees=attendees))

    @app_commands.command(name="cancel", description="Used to cancel an existing operation.")
    async def cancel(self, interaction:discord.Interaction, pal:str, reason:str):
        if DSBMEMBER(interaction.user):
            if ITMR_A(interaction.user):
                result = op_get_info(pal)
                if result:
                    op_ann = await interaction.channel.fetch_message(result[6])
                    op_ann.clear_reactions()
                    op_emb = op_ann.embeds[0]
                    op_emb.title = "<:DSB:1060271947725930496> Cancelled Operation!"
                    embed = discord.Embed(description=f"Operation `{result[0]} {result[1]}` has been cancelled.", color=ErrorCOL)
                    op_cancel(pal)
                    embed.add_field(name="", value=f"*Reason: {reason}*")
                    await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotSuccess:953641647802056756> Successfully cancelled "), ephemeral=True)
                    await op_ann.edit(embed=op_emb)
                    await op_ann.reply(embed=embed)
                else:
                    embed = discord.Embed(description=f"Operation with PALs `{pal}` not found!", color=ErrorCOL)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
     
class soupCmd(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        
    @app_commands.command(name="toggle_soup",description="Adds or removes the `Operation Supervisor` role. [SMaj+]")
    async def soup(self, interaction:discord.Interaction):
        userrank = getrank(interaction.user)
        if userrank[1] <20:
            return await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Missing permissions!", description=f"This command is DSB Elite Defense Specializst+."))
        else:
            role = discord.utils.get(interaction.guild.roles, name="[DSB] Operation Supervisors")
            if role in interaction.user.roles:
                try:
                    await interaction.user.remove_roles(role)
                    embed = discord.Embed(color=TRUCommandCOL, description=f"<:dsbbotSuccess:953641647802056756> Role successfully removed.")
                    await interaction.response.send_message(embed=embed)
                except Exception as e:
                    print(e)
                    embed = discord.Embed(color=ErrorCOL, description=f"An error occurred while trying to remove the role.\nError: {e}")
                    await interaction.response.send_message(embed=embed)
            else:
                try:
                    await interaction.user.add_roles(role)
                    embed = discord.Embed(color=TRUCommandCOL, description=f"<:dsbbotSuccess:953641647802056756> Role successfully added.")
                    await interaction.response.send_message(embed=embed)
                except Exception as e:
                    print(e)
                    embed = discord.Embed(color=ErrorCOL, description=f"An error occurred while trying to add the role.\nError: {e}")
                    await interaction.response.send_message(embed=embed)