import discord
from discord.ext import commands
from discord import app_commands
from discord import ui
from discord.ui import View
import discord

import time
import asyncio

from Functions.mainVariables import *
from Functions.permFunctions import *
from Functions.randFunctions import *
from Functions.trelloFunctions import *
from Database_Functions.ResponsedbFunctions import *
from Database_Functions.UserdbFunction import *
import Database_Functions.PrismaFunctions as dbFuncs
from Database_Functions.PrismaFunctions import *
from Functions.formattingFunctions import embedBuilder


## Groundwork is compete ##
# A lot of polishing, compacting and error handling still needed but functionally everything works

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
        await interaction.response.edit_message(embed=discord.Embed(description="<:trubotBeingLookedInto:1099642414303559720> Creating the trello card, updating the database and sending the announement...", color=TRUCommandCOL), view=None)
        trello_card_link = create_response_card(self.res_type, False, self.start_time, interaction.user.id) #Trello
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        trurole:discord.Role = interaction.guild.get_role(int(serverConfig.announceRole))
        msg:discord.Message = await self.channel.send(f"{trurole.mention}", embed=self.embed, allowed_mentions=discord.AllowedMentions.all())
        new_response, success = await createResponse(interaction, str(self.res_type), str(self.start_time), False, False, msg.id, trello_card_link.id) #Database
        if success == True:
            await self.fist_int.edit_original_response(view=None, embed=discord.Embed(title="<:trubotAccepted:1096225940578766968> Response successfully announced!", description=f"→ [Announcement]({msg.jump_url})\n→ [Trello Card]({trello_card_link.short_url})", color=SuccessCOL))
            await msg.add_reaction("<:trubotTRU:1096226111458918470>")
        else:
            await self.fist_int.edit_original_response(view=None, embed=discord.Embed(title="<:trubotDenied:1099642433588965447> An error occured!", description=f"{new_response}", color=ErrorCOL))
            

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
        self.selected_rep_id = selected_response
    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def ConfirmButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        channel = interaction.guild.get_channel(int(serverConfig.announceChannel))
        repmsg:discord.Message = await channel.fetch_message(int(self.selected_rep_id.responseID))
        rep_ann = repmsg.embeds[0]
        rep_ann.title = f"<:trubotTRU:1096226111458918470> {self.selected_rep_id.responseType} Response | Ongoing"
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
                resposne_leader, success = await fetch_operative(interaction)
                test_ann.add_field(name="Details", value=f"➥**Join link:** {resposne_leader.profileLink}\n➥**Voice Channel:** <#{self.vc_id}>\n➥**Status:** {self.status}", inline=False)
                await interaction.response.edit_message(embed=test_ann, view=CommenceAnnouncemenetButtons(test_ann, self.channel, interaction, selected_response))
            except Exception as e:
                print(e)
        elif self.action_type == "cancel":
            try:
                await interaction.response.defer()
                serverConfig = await dbFuncs.fetch_config(interaction=interaction)
                selected_response = await getResponseInfo(interaction, int(self.values[0]))
                channel = interaction.guild.get_channel(int(serverConfig.announceChannel))
                repmsg:discord.Message = await channel.fetch_message(int(selected_response.responseID))
                add_cancelled_label(selected_response.trellocardID)
                rep_ann = repmsg.embeds[0]
                if selected_response.spontaneous == True:
                    rep_ann.title = f"<:trubotTRU:1096226111458918470> Spontaneus {selected_response.responseType} Response | Cancelled"
                else:
                    rep_ann.title = f"<:trubotTRU:1096226111458918470> {selected_response.responseType} Response | Cancelled"
                can_ann = discord.Embed(description=f"{interaction.user.mention}**'s {selected_response.responseType} response has cancelled!**\n\n**Reason:** {self.reason}", color=TRUCommandCOL)
                await cancelResponse(interaction, str(selected_response.responseID))
                await interaction.edit_original_response(embed=discord.Embed(title="<:trubotAccepted:1096225940578766968> Response cancelled!", description=f"→ [Trello Card]({get_trello_card(selected_response.trellocardID).short_url})", color=SuccessCOL), view=None)
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
    
    start_time = ui.TextInput(label='Time', placeholder="ONLY Unix timestamp of start time. [ONLY NUMBERS]",style=discord.TextStyle.short, required=True)
    notes = ui.TextInput(label='Notes', placeholder="Purpose, goals, etc.", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            start_time_int = int(self.start_time.value)
        except ValueError:
            return await interaction.response.send_message(embed=embedBuilder("Error", embedTitle=f"<:trubotDenied:1099642433588965447> Start time error!", embedDesc=f"ValueError: `start_time` can only be numbers. `{self.start_time}` is not a valid integer!"), ephemeral=True)

        response_1 = await checkresponseTimes(self.start_time.value)
        if response_1 is not None:
            return await interaction.response.send_message(embed=embedBuilder("Warning", embedTitle=f"<:trubotDenied:1099642433588965447> Response Time Collision!", embedDesc=f"There is already a {response_1.responseType} response planned for <t:{self.start_time}> by {response_1.operativeName}."), ephemeral=True)
        else:
            serverConfig = await dbFuncs.fetch_config(interaction=interaction)
            self.channel = interaction.guild.get_channel(int(serverConfig.announceChannel))
            repann = discord.Embed(title=f"<:trubotTRU:1096226111458918470> {self.type} Response | Scheduled", color=TRUCommandCOL)
            repann.add_field(name="Time", value=f"<t:{self.start_time}>", inline=False)
            repann.add_field(name="Response Leader", value=f"{interaction.user.mention}", inline=False)
            repann.add_field(name="Notes", value=f"{self.notes}", inline=False)
            await interaction.response.send_message(embed=repann, ephemeral=True, view=ResponseAnnouncementButtons(repann, channel=self.channel, res_type=self.type, start_time=int(self.start_time.value), fist_int=interaction))


class responseCmds(commands.GroupCog, group_name='response'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="create", description=f"Used to manually add responses to the database. [Dev Only]")
    @app_commands.choices(response_type=[
        app_commands.Choice(name="Immediate Response", value="Immediate"),
        app_commands.Choice(name="Wartime Response", value="Wartime"),
        app_commands.Choice(name="Routine Response", value="Routine"),
        app_commands.Choice(name="Training Response", value="Training"),
        app_commands.Choice(name="Special Response", value="Special"),])
    async def r_create(self, interaction: discord.Interaction, response_type:app_commands.Choice[str], time_started:str, started:bool, spontaneous:bool, ann_msg_id:str, trellocard_id:str, time_ended:str, cancelled:bool, response_host:discord.Member):
        if DEVACCESS(interaction.user) is False:
            await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, description=f"<:trubotDenied:1099642433588965447> You do not have permission run this command."), ephemeral=True)
        
        new_response, success = await createResponse(interaction, response_type.value, time_started, started, spontaneous, ann_msg_id, trellocard_id, time_ended, cancelled, response_host)
        if success is True:
            response_embed = discord.Embed(title = "<:trubotAccepted:1096225940578766968> Successfully created the following response:", color=SuccessCOL)
            if type(new_response) is not str:
                    if new_response.cancelled:
                        status = "Cancelled"
                    elif str(new_response.timeEnded) != "Null":
                        status = "Concluded"
                    elif new_response.started:
                        status = "Ongoing"
                    else:
                        status = "Scheduled"
                    trellocard = get_trello_card(new_response.trellocardID)
                    response_embed.add_field(
                        name=f"{new_response.responseType} || {status}",
                        value=f"""
                            >>> Response Leader: {interaction.guild.get_member(int(new_response.operativeDiscordID)).mention}
                            Time Started: <t:{new_response.timeStarted}>
                            Time ended: {'N/A' if str(new_response.timeEnded) == 'Null' else f'<t:{new_response.timeEnded}>'}
                            Spontaneous: {new_response.spontaneous}
                            Trello Card: {trellocard.short_url if trellocard else "Error fetching the trello card."}
                        """,
                        inline=False
                    )

            else:
                response_embed.add_field(name="", value="No responses found in the database.")
        else:
            response_embed = discord.Embed(title="<:trubotDenied:1099642433588965447> Something went wrong while creating the response!", description=f"{new_response}" ,color=SuccessCOL)
            return await interaction.response.send_message(embed=response_embed, ephemeral=True)
        
        return await interaction.response.send_message(embed=response_embed)
            
        
    
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
        if await viewOperative(interaction.user.id) == None:
            await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, description=f"<:trubotDenied:1099642433588965447> You need to be registered to use this command."), ephemeral=True)
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
        if await viewOperative(interaction.user.id) == None:
            await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, description=f"<:trubotDenied:1099642433588965447> You need to be registered to use this command."), ephemeral=True)
        if await getUSERongoingResponses(interaction, interaction.user.id): #CHECK THAT USER DOES NOT HAVE AN ONGOING RESPONSE 
            return await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, title=f"You still have an on-going response!", description=f"You cannot host one responses at a time, please conclude your previous response first. If you believe this is an error, please ping <@!776226471575683082>."), ephemeral=True)
        
        await interaction.response.send_message(embed = discord.Embed(color=YellowCOL, title=f"Creating Trello card and updating the database..."), ephemeral=True)
        start_time = int(time.time())
        trello_card_link = create_response_card(rep_type.value, True, start_time, interaction.user.id)
        resposne_leader, success = await fetch_operative(interaction)
        repann = discord.Embed(title=f"<:trubotTRU:1096226111458918470> Spontaneous {rep_type.value} Response | Ongoing", color=TRUCommandCOL)
        repann.add_field(name="Response Leader", value=f"{interaction.user.mention}", inline=False)
        repann.add_field(name="Details:", value=f"➥**Join link:** {resposne_leader.profileLink}\n➥**Voice Channel:** <#{vc.value}>\n➥**Status:** {status}", inline=False)
        trurole:discord.Role = interaction.guild.get_role(int(serverConfig.announceRole))
        channel = self.bot.get_channel(int(serverConfig.announceChannel))
        ann:discord.Message = await channel.send(trurole.mention, embed=repann, allowed_mentions=discord.AllowedMentions.all())
        new_response, success = await createResponse(interaction, str(rep_type.value), start_time, True , True, ann.id, trello_card_link.id)
        await interaction.edit_original_response(embed=discord.Embed(title="<:trubotAccepted:1096225940578766968> Response announced!", description=f"→ [Announcement]({ann.jump_url})\n→ [Trello Card]({trello_card_link.short_url})", color=SuccessCOL))

    
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
        if await viewOperative(interaction.user.id) == None:
            await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, description=f"<:trubotDenied:1099642433588965447> You need to be registered to use this command."), ephemeral=True)
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
        if await viewOperative(interaction.user.id) == None:
            await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, description=f"<:trubotDenied:1099642433588965447> You need to be registered to use this command."), ephemeral=True)
        response_data = await getUSERongoingResponses(interaction, interaction.user.id)
        if response_data:
            await interaction.response.defer(ephemeral=True)
            channel = interaction.guild.get_channel(int(serverConfig.announceChannel))
            repmsg:discord.Message = await channel.fetch_message(int(response_data.responseID))
            rep_ann = repmsg.embeds[0]
            if response_data.spontaneous == True:
                rep_ann.title = f"<:trubotTRU:1096226111458918470> Spontaneous {response_data.responseType} Response | Concluded"
            else:
                rep_ann.title = f"<:trubotTRU:1096226111458918470> {response_data.responseType} Response | Concluded"
            con_ann = discord.Embed(description=f"{interaction.user.mention}'s {response_data.responseType} response has concluded!", color=TRUCommandCOL)
            await repmsg.edit(embed=rep_ann)
            await repmsg.reply(embed=con_ann)
            await interaction.edit_original_response(embed=discord.Embed(title="<:trubotAccepted:1096225940578766968> Response Concluded!", description=f"→ [Trello Card]({get_trello_card(response_data.trellocardID).short_url})", color=SuccessCOL))
            await concludeResponse(interaction, str(response_data.responseID))
        else:
            await interaction.response.send_message(embed=discord.Embed(description=f"<:trubotDenied:1099642433588965447> You do not have an on-going response to conclude!", color=ErrorCOL), ephemeral=True)

    @app_commands.command(name="cancel", description="Used to cancel an existing operation.")
    async def cancel(self, interaction:discord.Interaction, reason:str):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if not checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.announcePermissionRole))):
            await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, description=f"<:trubotDenied:1099642433588965447> You do not have permission run this command."), ephemeral=True)
        if await viewOperative(interaction.user.id) == None:
            await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, description=f"<:trubotDenied:1099642433588965447> You need to be registered to use this command."), ephemeral=True)
        planned_responses = await getUSERplannedResponses(interaction, str(interaction.user.id))
        if planned_responses:
            channel = self.bot.get_channel(int(serverConfig.announceChannel))
            view = View().add_item(ResponseSelect(responses=planned_responses, status=None, vc_id=None, channel=channel,action_type="cancel", reason=reason))
            await interaction.response.send_message(view=view, ephemeral=True)
        else:
            await interaction.response.send_message(embed=discord.Embed(description=f"<:trubotDenied:1099642433588965447> You do not have an on-going or scheduled response to cancel!", color=ErrorCOL), ephemeral=True)
    
    @app_commands.command(name="view", description="Used to view response chains.")
    async def view_response(self, interaction: discord.Interaction, response_leader:discord.Member = None):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        await interaction.response.defer()
        # Fetch the response chains from the database
        if response_leader:
            response_chains = await getUSERResponses(response_leader.id)
            response_embed = discord.Embed(color=TRUCommandCOL, title=f"Response Overview - {response_leader.nick}")
        else:
            response_chains = await getAllResponses()
            response_embed = discord.Embed(color=TRUCommandCOL, title="General Response Overview")
            
        #print(response_chains)
        # Limit of 15 responses at a time (Maybe add buttons again at one point)
        response_chains = response_chains[:15]

        # Sort the response chains by start time
        response_chains.sort(key=lambda r: r.timeStarted, reverse=True)
        
        
        # Format the response chains as a string
        if response_chains:
            for i, response in enumerate(response_chains):
                if response.cancelled:
                    status = "Cancelled"
                elif str(response.timeEnded) != "Null":
                    status = "Concluded"
                elif response.started:
                    status = "Ongoing"
                else:
                    status = "Scheduled"
                trellocard = get_trello_card(response.trellocardID)
                response_embed.add_field(
                    name=f"{response.responseType} || {status}",
                    value=f"""
                        >>> Response Leader: {interaction.guild.get_member(int(response.operativeDiscordID)).mention}
                        Time Started: <t:{response.timeStarted}>
                        Time ended: {'N/A' if str(response.timeEnded) == 'Null' else f'<t:{response.timeEnded}>'}
                        Spontaneous: {response.spontaneous}
                        Trello Card: {trellocard.short_url if trellocard else "Error fetching the trello card."}
                    """,
                    inline=False
                )

        else:
            response_embed.add_field(name="", value="No responses found in the database.")


        await interaction.edit_original_response(embed=response_embed)
    
    # Temporary       
    @app_commands.command(name="delete", description="ONLY FOR DEVELOPMENT")
    async def delete_response(self, interaction:discord.Interaction, response_id:str):
        if DEVACCESS(interaction.user):
            if await deleteResponse(responseID=response_id) is True:
                return await interaction.response.send_message(embed=embedBuilder("Success", embedTitle="Successfully deleted!", embedDesc=f"Successfully deleted response `{response_id}`"))
            else:
                return await interaction.response.send_message(embed=embedBuilder("Error", embedTitle="Response not foud!", embedDesc=f"Response `{response_id}` was not found in the DB..."))
        else:
            return
                    
        