import discord
from colorama import Back, Fore, Style
from discord.ext import commands
from discord import app_commands
from discord import ui
from discord.ui import View
import discord

import time
import asyncio
from Database_Functions.MaindbFunctions import *
from Functions.mainVariables import *
from Functions.permFunctions import *
from Functions.randFunctions import *
from Functions.trelloFunctions import *
from Database_Functions.ResponsedbFunctions import *
from Database_Functions.UserdbFunction import *
import Database_Functions.PrismaFunctions as dbFuncs
from Database_Functions.PrismaFunctions import *
from Functions.formattingFunctions import embedBuilder


class ResponseAnnouncementButtons(discord.ui.View):
    def __init__(self, embed:discord.Embed, channel:discord.TextChannel, res_type, start_time, fist_int:discord.Interaction):
        super().__init__()
        self.embed = embed
        self.channel = channel
        self.res_type = res_type
        self.start_time = start_time
        self.fist_int = fist_int
        discord.ui.View.timeout = None
    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def ConfirmButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        await interaction.response.defer()
        trello_card_link = create_response_card(self.res_type, False, self.start_time, interaction.user.id) #Trello
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        trurole:discord.Role = interaction.guild.get_role(int(serverConfig.announceRole))
        msg:discord.Message = await self.channel.send(f"{trurole.mention}", embed=self.embed, allowed_mentions=discord.AllowedMentions.all())
        await createResponse(interaction, str(self.res_type), str(self.start_time), False, False, msg.id, trello_card_link.id) #Database
        await self.fist_int.edit_original_response(view=None, embed=discord.Embed(title="<:trubotAccepted:1096225940578766968> Response successfully announnced!", description=f"→ [Announcement]({msg.jump_url})\n→ [Trello Card]({trello_card_link.short_url})", color=SuccessCOL))
        await msg.add_reaction("<:trubotTRU:1096226111458918470>")

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def CancelButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        return await interaction.response.edit_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Announcement Cancelled!", color=ErrorCOL), view=None)

class CommenceAnnouncemenetButtons(discord.ui.View):
    def __init__(self, embed:discord.Embed, channel:discord.TextChannel, fist_int:discord.Interaction, selected_response):
        super().__init__()
        self.embed = embed
        self.channel = channel
        self.fist_int = fist_int
        discord.ui.View.timeout = None
        print(selected_response)
        self.selected_rep_id = selected_response
    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def ConfirmButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        channel = interaction.guild.get_channel(int(serverConfig.announceChannel))
        repmsg:discord.Message = await channel.fetch_message(int(self.selected_rep_id.responseID))
        rep_ann = repmsg.embeds[0]
        rep_ann.title = f"<:trubotTRU:1096226111458918470> {self.selected_rep_id.responseType} Response | On-Going"
        trurole:discord.Role = interaction.guild.get_role(int(serverConfig.announceRole))
        await repmsg.edit(embed=rep_ann)
        msg = await repmsg.reply(f"{trurole.mention}", embed=self.embed, allowed_mentions=discord.AllowedMentions.all())
        await commenceResponse(interaction, responseID=self.selected_rep_id.responseID)
        await self.fist_int.edit_original_response(view=None, embed=discord.Embed(title="<:trubotAccepted:1096225940578766968> Response successfully started!", description=f"→ [Announcement]({msg.jump_url})", color=SuccessCOL))
        #database start op
        return

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def CancelButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        return await interaction.response.edit_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Announcement Cancelled!", color=ErrorCOL), view=None)

class ResponseSelect(discord.ui.Select):
    def __init__(self, responses, status, vc_id, channel, action_type, reason):
        super().__init__(
            placeholder="Select a response from the dropdown.",
            options=[])
        self.responses = responses
        self.refresh_options()
        self.status = status
        self.vc_id = vc_id
        self.channel:discord.TextChannel = channel
        self.action_type = action_type
        self.reason = reason

    def refresh_options(self):
        self.options = [
            discord.SelectOption(
                label=f"{response.responseType} Response",
                description=f"{datetime.utcfromtimestamp(int(response.timeStarted)).strftime('%m/%d/%y || %H:%M ZULU')}",
                value=str(response.responseID)
            ) for response in self.responses
        ]

    async def callback(self, interaction: discord.Interaction):
        if self.action_type == "commence":
            try:
                selected_response = await getResponseInfo(interaction, int(self.values[0]))
                test_ann = discord.Embed(title=f"<:trubotTRU:1096226111458918470> {selected_response.responseType} Response is now commencing!", color=TRUCommandCOL)
                test_ann.add_field(name="Response Leader", value=f"{interaction.user.mention}", inline=False)
                test_ann.add_field(name="Details", value=f"➥**Join link:** <profilelink>\n➥**Voice Channel:** <#{self.vc_id}>\n➥**Status:** {self.status}", inline=False)
                await interaction.response.edit_message(embed=test_ann, view=CommenceAnnouncemenetButtons(test_ann, self.channel, interaction, selected_response))
            except Exception as e:
                print(e)
        elif self.action_type == "cancel":
            try:
                serverConfig = await dbFuncs.fetch_config(interaction=interaction)
                selected_response = await getResponseInfo(interaction, int(self.values[0]))
                channel = interaction.guild.get_channel(int(serverConfig.announceChannel))
                repmsg:discord.Message = await channel.fetch_message(int(selected_response.responseID))
                rep_ann = repmsg.embeds[0]
                rep_ann.title = rep_ann.title + " | Cancelled"
                can_ann = discord.Embed(title=f"{interaction.user.nick}'s {selected_response.responseType} Response has been cancelled!", description=f"**Reason:** {self.reason}", color=TRUCommandCOL)
                await cancelResponse(interaction, str(selected_response.responseID))
                await interaction.response.edit_message(embed=discord.Embed(title="<:trubotAccepted:1096225940578766968> Response cancelled!", description=f"→ [Trello Card]({get_trello_card(selected_response.trellocardID).short_url})", color=SuccessCOL), view=None)
                await repmsg.edit(embed=rep_ann)
                await repmsg.reply(embed=can_ann)
            except Exception as e:
                print(e)
        else:
            await interaction.response.send_message(embed=discord.Embed(description=f"<:trubotDenied:1099642433588965447> No valid action_type found!", color=ErrorCOL), ephemeral=True)
            

class ScheduleModal(ui.Modal, title="Scheduled Response Announcement"):
    def __init__(self, type:str):
        super().__init__(timeout=None)
        self.type = type
    
    start_time = ui.TextInput(label='Time', placeholder="Provide the start time using ONLY an Unix timestamp.",style=discord.TextStyle.short, required=True)
    notes = ui.TextInput(label='Notes', placeholder="Purpose, goals, etc.", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        if await checkForPlannedOperation(self.start_time) is True:
            return await interaction.response.send_message(embed=embedBuilder("Warning", embedTitle=f"<:trubotWarning:1099642918974783519> There is already a response planned for around <t:{self.start_time}>!", embedDesc=None), ephemeral=True)
        else:
            serverConfig = await dbFuncs.fetch_config(interaction=interaction)
            self.channel = interaction.guild.get_channel(int(serverConfig.announceChannel))
            repann = discord.Embed(title=f"<:trubotTRU:1096226111458918470> {self.type} Response | Scheduled", color=TRUCommandCOL)
            repann.add_field(name="Time", value=f"<t:{self.start_time}>", inline=False)
            repann.add_field(name="Response Leader", value=f"{interaction.user.mention}", inline=False)
            repann.add_field(name="Notes", value=f"{self.notes}", inline=False)
            await interaction.response.send_message(embed=repann, ephemeral=True, view=ResponseAnnouncementButtons(repann, channel=self.channel, res_type=self.type, start_time=int(self.start_time.value), fist_int=interaction))


class OperationCmds(commands.GroupCog, group_name='response'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @app_commands.command(name="schedule", description="Used to schedule up-coming responses.")
    @app_commands.describe(type="Select your response type.")
    @app_commands.choices(type=[
        app_commands.Choice(name="Immediate Response", value="Immediate"),
        app_commands.Choice(name="Wartime Response", value="Wartime"),
        app_commands.Choice(name="Routine Response", value="Routine"),
        app_commands.Choice(name="Training Response", value="Training"),
        app_commands.Choice(name="Special Response", value="Special"),])
    async def schedule(self, interaction: discord.Interaction, type:app_commands.Choice[str]):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.announcePermissionRole))):
            await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, description=f"<:trubotDenied:1099642433588965447> You do not have permission run this command."), ephemeral=True)
        else:
            return await interaction.response.send_modal(ScheduleModal(type=type.value))
    
    @app_commands.command(name="spontaneous", description="Used to start scheduled & spontaneous responses.")
    @app_commands.choices(vc=[
        app_commands.Choice(name="[QSO] On Duty 1", value="937473342884179980"),
        app_commands.Choice(name="[QSO] On Duty 2", value="937473342884179981"),
        app_commands.Choice(name="[QSO] On Duty 3", value="937473342884179982"),
        app_commands.Choice(name="[QSO] On Duty 4", value="937473342884179983"),
        app_commands.Choice(name="[QSO] On Duty 5", value="937473342884179984"),
        app_commands.Choice(name="[QSO] VIP Raid", value="937473342884179985"),
        app_commands.Choice(name="[QSO] Events", value="992865433059340309"),
        app_commands.Choice(name="[TRU] On Duty 1", value="1095847944047054878"),
        app_commands.Choice(name="[TRU] On Duty 2", value="1096215752345915452"),
        app_commands.Choice(name="[TRU] Stage", value="950145200087511130"),])
    @app_commands.choices(rep_type=[
        app_commands.Choice(name="Immediate Response", value="Immediate"),
        app_commands.Choice(name="Wartime Response", value="Wartime"),
        app_commands.Choice(name="Routine Response", value="Routine"),
        app_commands.Choice(name="Training Response", value="Training"),
        app_commands.Choice(name="Special Response", value="Special"),])
    async def spontaneous(self, interaction:discord.Interaction,rep_type:app_commands.Choice[str], vc:app_commands.Choice[str], status:str,):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.announcePermissionRole))):
            return await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, description=f"You do not have permission run this command."), ephemeral=True)
        if await getUSERongoingResponses(interaction, interaction.user.id): #CHECK THAT USER DOES NOT HAVE AN ONGOING RESPONSE 
            return await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, title=f"You still have an on-going response!", description=f"You cannot host one responses at a time, please conclude your previous response first. If you believe this is an error, please ping <@!776226471575683082>."), ephemeral=True)
        
        await interaction.response.send_message(embed = discord.Embed(color=YellowCOL, title=f"Creating Trello card and updating the database..."), ephemeral=True)
        start_time = int(time.time())
        trello_card_link = create_response_card(rep_type.value, True, start_time, interaction.user.id)
        repann = discord.Embed(title=f"<:trubotTRU:1096226111458918470> Spontaneous {rep_type.value} Response", color=TRUCommandCOL)
        repann.add_field(name="Response Leader", value=f"{interaction.user.mention}", inline=False)
        repann.add_field(name="Details:", value=f"➥**Join link:** <profilelink>\n➥**Voice Channel:** <#{vc.value}>\n➥**Status:** {status}", inline=False)
        trurole:discord.Role = interaction.guild.get_role(int(serverConfig.announceRole))
        channel = self.bot.get_channel(int(serverConfig.announceChannel))
        ann:discord.Message = await channel.send(trurole.mention, embed=repann, allowed_mentions=discord.AllowedMentions.all())
        await createResponse(interaction, str(rep_type.value), start_time, True , True, ann.id, trello_card_link.id)
        await interaction.edit_original_response(embed=discord.Embed(title="<:trubotAccepted:1096225940578766968> Response announnced!", description=f"→ [Announcement]({ann.jump_url})\n→ [Trello Card]({trello_card_link.short_url})", color=SuccessCOL))

    
    @app_commands.command(name="commence", description="Used to start scheduled responses.")
    @app_commands.choices(vc=[
        app_commands.Choice(name="[QSO] On Duty 1", value="937473342884179980"),
        app_commands.Choice(name="[QSO] On Duty 2", value="937473342884179981"),
        app_commands.Choice(name="[QSO] On Duty 3", value="937473342884179982"),
        app_commands.Choice(name="[QSO] On Duty 4", value="937473342884179983"),
        app_commands.Choice(name="[QSO] On Duty 5", value="937473342884179984"),
        app_commands.Choice(name="[QSO] VIP Raid", value="937473342884179985"),
        app_commands.Choice(name="[QSO] Events", value="992865433059340309"),
        app_commands.Choice(name="[TRU] On Duty 1", value="1095847944047054878"),
        app_commands.Choice(name="[TRU] On Duty 2", value="1096215752345915452"),
        app_commands.Choice(name="[TRU] Stage", value="950145200087511130"),])
    async def commence(self, interaction:discord.Interaction, vc:app_commands.Choice[str], status:str,): # resp_type:app_commands.Choice[str]
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.announcePermissionRole))):
            await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, description=f"You do not have permission run this command."), ephemeral=True)
        if await getUSERongoingResponses(interaction, interaction.user.id): #CHECK THAT USER DOES NOT HAVE AN ONGOING RESPONSE 
            return await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, title=f"You still have an on-going response!", description=f"You cannot host one responses at a time, please conclude your previous response first. If you believe this is an error, please ping <@!776226471575683082>."), ephemeral=True)
        
        scheduled_responses = await getUSERplannedResponses(interaction, interaction.user.id)
        channel = self.bot.get_channel(int(serverConfig.announceChannel))
        if scheduled_responses:
            view = View().add_item(ResponseSelect(responses=scheduled_responses, status=status, vc_id=vc.value, channel=channel, action_type="commence", reason=None))
            await interaction.response.send_message(view=view, ephemeral=True)
        else:
            return await interaction.response.send_message(embed=discord.Embed(description=f"<:trubotDenied:1099642433588965447> You do not have a scheduled response to start!", color=ErrorCOL), ephemeral=True)
            
    
    @app_commands.command(name="conclude", description="Used to conclude an operations.")
    async def conclude(self, interaction:discord.Interaction, picture:discord.Attachment):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.announcePermissionRole))):
            await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, description=f"<:trubotDenied:1099642433588965447> You do not have permission run this command."), ephemeral=True)
        response_data = await getUSERongoingResponses(interaction, interaction.user.id)
        print(response_data)
        if response_data:
            channel = interaction.guild.get_channel(int(serverConfig.announceChannel))
            repmsg:discord.Message = await channel.fetch_message(int(response_data.responseID))
            rep_ann = repmsg.embeds[0]
            rep_ann.title = rep_ann.title + " | Concluded"
            con_ann = discord.Embed(description=f"{interaction.user.mention}'s {response_data.responseType} response has concluded!", color=TRUCommandCOL)
            await repmsg.edit(embed=rep_ann)
            await repmsg.reply(embed=con_ann)
            await interaction.response.send_message(embed=discord.Embed(title="<:trubotAccepted:1096225940578766968> Response Concluded!", description=f"→ [Trello Card]({get_trello_card(response_data.trellocardID).short_url})", color=SuccessCOL), ephemeral=True)
            await concludeResponse(interaction, str(response_data.responseID))
        else:
            await interaction.response.send_message(embed=discord.Embed(description=f"<:trubotDenied:1099642433588965447> You do not have an on-going response to conclude!", color=ErrorCOL), ephemeral=True)

    @app_commands.command(name="cancel", description="Used to cancel an existing operation.")
    async def cancel(self, interaction:discord.Interaction, reason:str):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.announcePermissionRole))):
            await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, description=f"<:trubotDenied:1099642433588965447> You do not have permission run this command."), ephemeral=True)
        planned_responses = await getUSERplannedResponses(interaction, str(interaction.user.id))
        if planned_responses:
            channel = self.bot.get_channel(int(serverConfig.announceChannel))
            view = View().add_item(ResponseSelect(responses=planned_responses, status=None, vc_id=None, channel=channel,action_type="cancel", reason=reason))
            await interaction.response.send_message(view=view, ephemeral=True)
        else:
            await interaction.response.send_message(embed=discord.Embed(description=f"<:trubotDenied:1099642433588965447> You do not have an on-going or scheduled response to cancel!", color=ErrorCOL), ephemeral=True)
            
    @app_commands.command(name="deleteresponse", description="ONLY FOR DEVELOPMENT")
    async def delete_response(self, interaction:discord.Interaction, response_id:str):
        if DEVACCESS(interaction.user):
            if await deleteResponse(responseID=response_id) is True:
                return await interaction.response.send_message(embed=embedBuilder("Success", embedTitle="Successfully deleted!", embedDesc=f"Successfully deleted response `{response_id}`"))
            else:
                return await interaction.response.send_message(embed=embedBuilder("Error", embedTitle="Response not foud!", embedDesc=f"Response `{response_id}` was not found in the DB..."))
        else:
            return
                    
        