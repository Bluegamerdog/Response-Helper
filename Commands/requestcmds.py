import math
import re
import discord
import os
from discord.ext import commands
from discord import app_commands
from discord import ui
from Database_Functions.MaindbFunctions import *
from Functions.mainVariables import *
from Functions.permFunctions import *
from Functions.randFunctions import (attendance_points, co_host_points, supervisor_points, ringleader_points)
from Database_Functions.UserdbFunction import (add_points, get_points, db_register_get_data)
import Database_Functions.PrismaFunctions as dbFuncs
from Database_Functions.PrismaFunctions import *
from Functions.formattingFunctions import embedBuilder

### REMOVE? ###


class PatrolrequestButtons(discord.ui.View):
    def __init__(self, amount:int):
        super().__init__()
        self.amount = amount
        discord.ui.View.timeout = None
    
    @discord.ui.button(emoji="<:trubotAccepted:1096225940578766968>", label="Accept", style=discord.ButtonStyle.grey)
    async def AcceptButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        if not TRULEAD(interaction.user):
            return
        else:
            try:
                add_points(interaction.message.interaction.user.id, self.amount)
                embed = interaction.message.embeds[0]
                embed.title= embed.title.replace("<:trubotBeingLookedInto:1099642414303559720>", "<:trubotAccepted:1096225940578766968>")
                embed.color=DarkGreenCOL
                await interaction.message.edit(embed=embed, view=None)
                embed=discord.Embed(color=SuccessCOL,title="<:trubotAccepted:1096225940578766968> Point Request Accepted!", description=f"Your point request has been **accepted** and {self.amount} points have been added. You now have **{get_points(interaction.message.interaction.user.id)}** points. 😎")
                embed.set_footer(icon_url=interaction.user.avatar, text=f"Reviewed by {interaction.user.display_name} • {datetime.now().strftime('%d.%m.%y at %H:%M')}")
                await interaction.response.send_message(f"{interaction.message.interaction.user.mention}", embed=embed)
            except Exception as e:
                await interaction.response.send_message(embed=discord.Embed(title="Failed to proccess request!", description=f"`Error:` {e}"), ephemeral=True)

    @discord.ui.button(emoji="<:dsbbotDeny:1073668785262833735>", label="Decline", style=discord.ButtonStyle.grey)
    async def DenyButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        if not TRULEAD(interaction.user):
            return
        else:
            embed = interaction.message.embeds[0]
            embed.title= embed.title.replace("<:trubotBeingLookedInto:1099642414303559720>", "<:dsbbotDeny:1073668785262833735>")
            embed.color=DarkRedCOL
            await interaction.message.edit(embed=embed, view=None)
            embed=discord.Embed(color=ErrorCOL, title="<:dsbbotDeny:1073668785262833735> Point Request Denied!", description=f"Your point request has been **denied**. The person who reviewed it will provide you with the reason shortly. 😄")
            embed.set_footer(icon_url=interaction.user.avatar, text=f"Reviewed by {interaction.user.display_name} • {datetime.now().strftime('%d.%m.%y at %H:%M')}")
            await interaction.response.send_message(f"{interaction.message.interaction.user.mention}", embed=embed)

    @discord.ui.button(emoji="❌", label="Cancel", style=discord.ButtonStyle.grey)
    async def CancelButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.user == interaction.message.interaction.user:
            embed = interaction.message.embeds[0]
            embed.title="<:dsbbotFailed:953641818057216050> Cancelled __Patrol__ Point Request!"
            embed.clear_fields()
            embed.set_footer(icon_url=interaction.user.avatar, text=f"Cancelled by {interaction.user.display_name} • {datetime.now().strftime('%d.%m.%y at %H:%M')}")
            embed.color=HRCommandsCOL
            await interaction.message.edit(embed=embed, view=None)
        else:
            return
            
class OperationrequestButtons(discord.ui.View):
    def __init__(self, points_dict):
        super().__init__()
        self.points_dict = points_dict
        discord.ui.View.timeout = None
    
    @discord.ui.button(emoji="<:trubotAccepted:1096225940578766968>", label="Accept", style=discord.ButtonStyle.grey)
    async def AcceptButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        if not TRULEAD(interaction.user):
            return
        else:
            try:
                for user_id, amount in self.points_dict.items():
                    add_points(user_id, amount)
                embed = interaction.message.embeds[0]
                embed.title= embed.title.replace("<:trubotBeingLookedInto:1099642414303559720>", "<:trubotAccepted:1096225940578766968>")
                embed.color=DarkGreenCOL
                await interaction.message.edit(embed=embed, view=None)
                embed=discord.Embed(color=SuccessCOL,title="<:trubotAccepted:1096225940578766968> Point Request Accepted!", description=f"The point request for this operation has been **accepted** and all points have been added. 🛡️")
                embed.set_footer(icon_url=interaction.user.avatar, text=f"Reviewed by {interaction.user.display_name} • {datetime.now().strftime('%d.%m.%y at %H:%M')}")
                await interaction.response.send_message(f"{interaction.message.interaction.user.mention}", embed=embed)
            except Exception as e:
                await interaction.response.send_message(embed=discord.Embed(title="Failed to proccess request!", description=f"`Error:` {e}"), ephemeral=True)

    @discord.ui.button(emoji="<:dsbbotDeny:1073668785262833735>", label="Decline", style=discord.ButtonStyle.grey)
    async def DenyButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        if not TRULEAD(interaction.user):
            return
        else:
            embed = interaction.message.embeds[0]
            embed.title= embed.title.replace("<:trubotBeingLookedInto:1099642414303559720>", "<:dsbbotDeny:1073668785262833735>")
            embed.color=DarkRedCOL
            await interaction.message.edit(embed=embed, view=None)
            embed=discord.Embed(color=ErrorCOL, title="<:dsbbotDeny:1073668785262833735> Point Request Denied!", description=f"The point request for this operation has been **denied**. The person who reviewed it will provide the reason shortly. 😄")
            embed.set_footer(icon_url=interaction.user.avatar, text=f"Reviewed by {interaction.user.display_name} • {datetime.now().strftime('%d.%m.%y at %H:%M')}")
            await interaction.response.send_message(f"{interaction.message.interaction.user.mention}", embed=embed)

    @discord.ui.button(emoji="❌", label="Cancel", style=discord.ButtonStyle.grey)
    async def CancelButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        if interaction.user == interaction.message.interaction.user:
            embed = interaction.message.embeds[0]
            embed.title="<:dsbbotFailed:953641818057216050> Cancelled __Operation__ Point Request!"
            embed.clear_fields()
            embed.set_footer(icon_url=interaction.user.avatar, text=f"Cancelled by {interaction.user.display_name} • {datetime.now().strftime('%d.%m.%y at %H:%M')}")
            embed.color=HRCommandsCOL
            await interaction.message.edit(embed=embed, view=None)
        else:
            return

        
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
        

    @app_commands.command(name="patrol", description="Request points for your patrols using this command.")
    @app_commands.describe(log="Message link to .qb findlog message from #bot-commands", length="The length of your patrol in minutes")
    async def request_log(self, interaction:discord.Interaction, length:int, log:str):
        if not TRUMEMBER(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Missing permissions!", description=f"Only TRU Private First Class or above may interact with TRU Helper."), ephemeral=True)
        if not db_register_get_data(interaction.user.id):
            return await interaction.response.send_message(embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Interaction failed!", description="You were not found in registry database.\n*Use `/db register` to register.*", color=ErrorCOL), ephemeral=True)   
        message_link_pattern = re.compile(r"https://(?:ptb\.)?discord(?:app)?\.com/channels/(\d+)/(\d+)/(\d+)")
        if not message_link_pattern.match(log):
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Invalid proof!", description=f"You must provide a Discord message link."), ephemeral=True)
        if length < 30 or length > 541:
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Invalid length!", description=f"The length of your patrol must be at least 30 minutes." if length < 30 else "Your patrol should not be over 9hs or 540 minutes..."), ephemeral=True)
        else:
            if length <= 60:
                amount = 2
            else:
                amount = 2
                extra = math.floor((length - 60+7) / 30)
                amount += extra
        embed = discord.Embed(color=TRUCommandCOL, title=f"<:trubotBeingLookedInto:1099642414303559720> __Patrol__ Point Request - {interaction.user.display_name}")
        embed.add_field(name="", value="")
        embed.add_field(name="", value=f"**{interaction.user.display_name}** has requested **{amount} points** for patrolling **{length} minutes**.\n\n→ **[Log Message]({log})**", inline=False)
        await interaction.response.send_message(embed = embed, view=PatrolrequestButtons(amount))

    @app_commands.command(name="operation", description="Request points for your operations using this command.")
    @app_commands.describe(operation="Example: `ECHO HH`", ringleader="The host of the operation, normally that would be you.", co_hosts="If anyone co-hosted your operation they would go here.", supervisors="If anyone soupervised your operation, they would go here.", attendees="Your attendance list goes here. Make sure to seperate the mentions using a comma.")
    async def request_op(self, interaction:discord.Interaction, operation:str, ringleader:discord.Member, supervisors:str=None, co_hosts:str=None, attendees:str=None):
        if not TRURL(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotDeny:1073668785262833735> Missing permissions!", description=f"This command is limited to TRU Sergeant+."), ephemeral=True)
        if not db_register_get_data(interaction.user.id):
            return await interaction.response.send_message(embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Interaction failed!", description="You were not found in registry database.\n*Use `/db register` to register.*", color=ErrorCOL), ephemeral=True)   
        embed = discord.Embed(color=TRUCommandCOL, title=f"<:trubotBeingLookedInto:1099642414303559720> __Operation__ Points Request - Operation {operation}")
        points_dict = {}
        
        if co_hosts:
            cohost_list = []
            cohosts = co_hosts.split(",")
            for co_host in cohosts:
                error_msg = None
                co_host = co_host.replace(" ", "")
                if not co_host.startswith("<@") or not co_host.endswith(">"):
                    error_msg = "Co-Host: Invalid format for co-hosts. Format `<@USERID>, <@USERID>`"
                    break
                co_host_id = int(co_host.replace("<", "").replace("@", "").replace(">", "").replace(" ", ""))
                if str(co_host_id).__len__() > 20:
                    error_msg = f"`Co-Hosts:` Please separate user mentions with commas."
                    break
                co_host_member = discord.utils.get(interaction.guild.members, id=co_host_id)
                if co_host_member is None:
                    error_msg = f"`Co-Hosts:` Could not a find member."
                    break
                if not db_register_get_data(co_host_member.id):
                    error_msg = f"`Co-Hosts:` {co_host_member.mention} was not found in the database."
                    break
                if co_host_points(co_host_member) == None:
                    error_msg = f"`Co-Hosts:` {co_host_member.mention} is not TRU MR or above."
                    break
                if co_host_member.id in points_dict:
                    error_msg = f"`Co-Hosts:` {co_host_member.mention} was mentioned twice."
                    break
                cohost_list.append(co_host_member)
                points_dict[co_host_member.id] = co_host_points(co_host_member)
            if error_msg:
                return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Invalid Input! || Error", description=error_msg), ephemeral=True)
            cohtxt = ", ".join([f"{cohost.display_name}[{points_dict[cohost.id]}]" for cohost in cohost_list])
        soup_list = []
        if supervisors:
            supervisorss = supervisors.split(",")
            for supervisor in supervisorss:
                error_msg = None
                supervisor_id = int(supervisor.replace("<", "").replace("@", "").replace(">", "").replace(" ", ""))
                if str(supervisor_id).__len__() > 20:
                    error_msg = f"`Supervisors:` Please separate user mentions with commas."
                    break
                if supervisor == f"<@{ringleader.id}>":
                    error_msg = "`Supervisors:` You cannot mention the ringleader as a supervisor."
                    break
                supervisor_member = discord.utils.get(interaction.guild.members, id=supervisor_id)
                if not supervisor_member:
                    error_msg = "`Supervisors:` Could not find a member."
                    break
                if not db_register_get_data(supervisor_member.id):
                    error_msg = f"`Supervisors:` {supervisor_member.mention} was not found in the database."
                    break
                if supervisor_id in points_dict:
                    error_msg = f"`Supervisors:` {supervisor_member.mention} was mentioned twice."
                    break
                if supervisor_points(supervisor_member) == None:
                    error_msg = f"`Supervisors:` {supervisor_member.mention} is not Sergeant+."
                    break
                soup_list.append(supervisor_member)
                points_dict[supervisor_member.id] = supervisor_points(supervisor_member)
            if error_msg:
                return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Invalid Input! || Error", description=error_msg), ephemeral=True)
            souptxt = ", ".join([f"{supervisor.display_name}[{supervisor_points(supervisor)}]" for supervisor in soup_list])
        attendees_list = []
        if attendees:
            attendeess = attendees.split(",")
            for attendee in attendeess:
                error_msg = None
                attendee = attendee.replace(" ", "")
                if attendee == f"<@{ringleader.id}>":
                    error_msg = "Attendees: You cannot mention the ringleader as an attendee."
                    break
                attendee_id = int(attendee.replace("<", "").replace("@", "").replace(">", "").replace(" ", ""))
                if str(attendee_id).__len__() > 20:
                    error_msg = f"`Attendees:` Please separate user mentions with commas."
                    break
                attendee_member = discord.utils.get(interaction.guild.members, id=attendee_id)
                if not attendee_member:
                    error_msg = f"`Attendees:` Could not find a member with ID {attendee_id}."
                    break
                if TRULEAD(attendee_member):
                    error_msg = f"`Attendees:` {attendee_member.mention} is a member of TRUPC or above. You cannot put TRUPC members and above as attendee. 😉"
                    break
                if not db_register_get_data(attendee_id):
                    error_msg = f"`Attendees:` {attendee_member.mention} was not found in the database."
                    break
                if attendance_points(attendee_member) == None:
                    error_msg = f"`Attendees:` {attendee_member.mention} is not a valid attendee. No point value found for this rank/person."
                    break
                attendees_list.append(attendee_member)
                points_dict[attendee_member.id] = attendance_points(attendee_member)
            if error_msg:
                return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Invalid Input! || Error", description=error_msg), ephemeral=True)
            atttxt = ", ".join([f"{attendee.display_name}[{attendance_points(attendee)}]" for attendee in attendees_list])
        else:
            if not cohosts:
                cohtxt = "Something went wrong..."
            if not supervisors:
                souptxt = "Something went wrong..."
            if not attendees:
                atttxt = "Something went wrong..."
        
        if ringleader:
            if TRURL(ringleader):
                points_dict[ringleader.id] = ringleader_points(ringleader)
                embed.add_field(name="", value=f"`Ringleader:` {ringleader.display_name}[{ringleader_points(ringleader)}]")
            else:
                return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotDeny:1073668785262833735> Invalid Input", description=f"{ringleader.mention} is not TRU MR or above."))
        if co_hosts:
            embed.add_field(name="", value=f"`Co-Host:` {cohtxt}" if cohost_list.__len__() == 1 else f"`Co-Hosts:` {cohtxt}",inline=False)
        if supervisors:
            embed.add_field(name="", value=f"`Supervisor:` {souptxt}" if soup_list.__len__() == 1 else f"`Supervisors:` {souptxt}",inline=False)
        if attendees_list:
            embed.add_field(name="", value=f"`Attendee:` {atttxt}"if attendees_list.__len__() == 1 else f"`Attendees:` {atttxt}", inline=False)
        await interaction.response.send_message(embed = embed, view=OperationrequestButtons(points_dict))
        
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
