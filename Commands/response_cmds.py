import discord
from discord.ext import commands
from discord import app_commands
from discord import ui
from discord.ui import View
import discord

import time
import asyncio

from Functions.mainVariables import *
from Functions.rolecheckFunctions import *
from Functions.randFunctions import *
from Functions.trelloFunctions import *
from Database_Functions.ResponsedbFunctions import *
import Database_Functions.PrismaFunctions as dbFuncs
from Database_Functions.PrismaFunctions import *
from Functions.formattingFunctions import embedBuilder


# Will mostly not use embedBuilder()


class ResponseAnnouncementButtons(discord.ui.View):
    def __init__(
        self,
        embed: discord.Embed,
        channel: discord.TextChannel,
        res_type,
        start_time,
        fist_int: discord.Interaction,
    ):
        super().__init__()
        self.embed = embed
        self.channel = channel
        self.res_type = res_type
        self.start_time = start_time
        self.fist_int = fist_int
        discord.ui.View.timeout = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def ConfirmButton(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            embed=discord.Embed(
                description="<:trubotBeingLookedInto:1099642414303559720> Creating the trello card, updating the database and sending the announcement...",
                color=TRUCommandCOL,
            ),
            view=None,
        )
        trello_card_link = create_response_card(
            self.res_type, False, self.start_time, interaction.user.id
        )  # Trello
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        trurole: discord.Role = interaction.guild.get_role(
            int(serverConfig.announceRole)
        )
        msg: discord.Message = await self.channel.send(
            f"{trurole.mention}",
            embed=self.embed,
            allowed_mentions=discord.AllowedMentions.all(),
        )
        new_response, success = await createResponse(
            interaction,
            str(self.res_type),
            str(self.start_time),
            False,
            False,
            msg.id,
            trello_card_link.id,
        )  # Database
        if success == True:
            await self.fist_int.edit_original_response(
                view=None,
                embed=embedBuilder(
                    responseType="succ",
                    embedTitle="Response announced!",
                    embedDesc=f"→ [Announcement]({msg.jump_url})\n→ [Trello Card]({trello_card_link.short_url})",
                ),
            )
            await msg.add_reaction("<:trubotTRU:1096226111458918470>")
        else:
            await self.fist_int.edit_original_response(
                view=None,
                embed=embedBuilder(responseType="err", embedDesc=f"{new_response}"),
            )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def CancelButton(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        return await interaction.response.edit_message(
            embed=embedBuilder(
                responseType="warn", embedTitle="Announcement cancelled!"
            ),
            view=None,
        )


class CommenceAnnouncemenetButtons(discord.ui.View):
    def __init__(
        self,
        embed: discord.Embed,
        channel: discord.TextChannel,
        fist_int: discord.Interaction,
        selected_response,
    ):
        super().__init__()
        self.embed = embed
        self.channel = channel
        self.fist_int = fist_int
        discord.ui.View.timeout = None
        self.selected_rep_id = selected_response

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def ConfirmButton(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        channel = interaction.guild.get_channel(int(serverConfig.announceChannel))
        repmsg: discord.Message = await channel.fetch_message(
            int(self.selected_rep_id.responseID)
        )
        rep_ann = repmsg.embeds[0]
        rep_ann.description = f"### <:trubotTRU:1096226111458918470> {self.selected_rep_id.responseType} Response | Ongoing"
        trurole: discord.Role = interaction.guild.get_role(
            int(serverConfig.announceRole)
        )
        await repmsg.edit(embed=rep_ann)
        msg = await repmsg.reply(
            f"{trurole.mention}",
            embed=self.embed,
            allowed_mentions=discord.AllowedMentions.all(),
        )
        await commenceResponse(interaction, responseID=self.selected_rep_id.responseID)
        await self.fist_int.edit_original_response(
            view=None,
            embed=embedBuilder(
                responseType="succ",
                embedTitle="Response started!",
                embedDesc=f"→ [Announcement]({msg.jump_url})",
            ),
        )
        # database start op
        return

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def CancelButton(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        return await interaction.response.edit_message(
            embed=embedBuilder(
                responseType="warn", embedTitle="Announcement cancelled!"
            ),
            view=None,
        )


class ResponseSelect(discord.ui.Select):
    def __init__(self, responses, status, vc_id, channel, action_type, reason):
        super().__init__(placeholder="Select a response from the dropdown.", options=[])
        self.responses = responses
        self.refresh_options()
        self.status = status
        self.vc_id = vc_id
        self.channel: discord.TextChannel = channel
        self.action_type = action_type
        self.reason = reason

    def refresh_options(self):
        self.options = [
            discord.SelectOption(
                label=f"{response.responseType} Response",
                description=f"{datetime.utcfromtimestamp(int(response.timeStarted)).strftime('%m/%d/%y || %H:%M ZULU')}",
                value=str(response.responseID),
            )
            for response in self.responses
        ]

    async def callback(self, interaction: discord.Interaction):
        if self.action_type == "commence":
            try:
                selected_response = await getResponseInfo(
                    interaction, int(self.values[0])
                )
                test_ann = discord.Embed(
                    description=f"### <:trubotTRU:1096226111458918470> {selected_response.responseType} Response is now commencing!",
                    color=TRUCommandCOL,
                )
                test_ann.add_field(
                    name="Response Leader:",
                    value=f"{interaction.user.mention}",
                    inline=False,
                )
                resposne_leader = await getOperator(interaction.user.id)
                test_ann.add_field(
                    name="Response Details",
                    value=f"> __Join link__: {resposne_leader.profileLink}\n> __Voice Channel__: <#{self.vc_id}>\n> __Status__: {self.status}",
                    inline=False,
                )
                await interaction.response.edit_message(
                    embed=test_ann,
                    view=CommenceAnnouncemenetButtons(
                        test_ann, self.channel, interaction, selected_response
                    ),
                )
            except Exception as e:
                print(e)
        elif self.action_type == "cancel":
            try:
                await interaction.response.defer()
                serverConfig = await dbFuncs.fetch_config(interaction=interaction)
                selected_response = await getResponseInfo(
                    interaction, int(self.values[0])
                )
                channel = interaction.guild.get_channel(
                    int(serverConfig.announceChannel)
                )
                repmsg: discord.Message = await channel.fetch_message(
                    int(selected_response.responseID)
                )
                if not add_cancelled_label(selected_response.trellocardID):
                    trellofailed = True
                else:
                    trellofailed = False
                rep_ann = repmsg.embeds[0]
                if selected_response.spontaneous == True:
                    rep_ann.description = f"### <:trubotTRU:1096226111458918470> Spontaneus {selected_response.responseType} Response | Cancelled"
                else:
                    rep_ann.description = f"### <:trubotTRU:1096226111458918470> {selected_response.responseType} Response | Cancelled"
                can_ann = discord.Embed(
                    description=f"### {interaction.user.mention}'s {selected_response.responseType} response has been cancelled!",
                    color=TRUCommandCOL,
                )
                if self.reason:
                    can_ann.add_field(name="Reason:", value=f"{self.reason}")
                await cancelResponse(interaction, str(selected_response.responseID))
                await interaction.edit_original_response(
                    embed=embedBuilder(
                        responseType="succ",
                        embedTitle="Response cancelled!",
                        embedDesc=f"→ [Trello Card]({get_card_by_id(selected_response.trellocardID).short_url})"
                        if trellofailed is False
                        else "The Trello card associated with the response could not be found, and therefore not updated.",
                    ),
                    view=None,
                )
                await repmsg.edit(embed=rep_ann)
                await repmsg.reply(embed=can_ann)
            except Exception as e:
                print(e)
        else:
            await interaction.response.send_message(
                embed=embedBuilder(
                    responseType="err",
                    embedTitle="No valid 'action_type' found!",
                    embedDesc=f"`{self.action_type}` is not a valid 'action_type'.",
                ),
                ephemeral=True,
            )


class ScheduleModal(ui.Modal, title="Scheduled Response Announcement"):
    def __init__(self, type: str):
        super().__init__(timeout=None)
        self.type = type

    start_time = ui.TextInput(
        label="Time",
        placeholder="Must be a valid Unix timestamp, numbers only.",
        style=discord.TextStyle.short,
        required=True,
    )
    notes = ui.TextInput(
        label="Notes",
        placeholder="Purpose, goals, etc.",
        style=discord.TextStyle.paragraph,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            start_time_int = int(self.start_time.value)
        except ValueError:
            return await interaction.response.send_message(
                embed=embedBuilder(
                    "err",
                    embedTitle=f"Start time error!",
                    embedDesc=f"ValueError: `start_time` can only be numbers. `{self.start_time}` is not a valid integer!",
                ),
                ephemeral=True,
            )
        try:
            due_date_datetime = datetime.utcfromtimestamp(start_time_int)
        except OSError:
            return await interaction.response.send_message(
                embed=embedBuilder(
                    "err",
                    embedTitle="Start time error!",
                    embedDesc="OSError: `start_time` is not a valid Unix timestamp!",
                ),
                ephemeral=True,
            )

        response_1 = await checkresponseTimes(start_time_int)
        if response_1 is not None:
            return await interaction.response.send_message(
                embed=embedBuilder(
                    "warn",
                    embedTitle=f"Response Time Collision!",
                    embedDesc=f"There is already a {response_1.responseType} response planned for <t:{self.start_time}> by {response_1.operativeName}.",
                ),
                ephemeral=True,
            )
        else:
            serverConfig = await dbFuncs.fetch_config(interaction=interaction)
            self.channel = interaction.guild.get_channel(
                int(serverConfig.announceChannel)
            )
            repann = discord.Embed(
                description=f"### <:trubotTRU:1096226111458918470> {self.type} Response | Scheduled",
                color=TRUCommandCOL,
            )
            repann.add_field(name="Time & Date:", value=f"<t:{self.start_time}>", inline=False)
            repann.add_field(
                name="Response Leader:",
                value=f"{interaction.user.mention}",
                inline=False,
            )
            repann.add_field(name="Notes:", value=f"{self.notes}", inline=False)
            await interaction.response.send_message(
                embed=repann,
                ephemeral=True,
                view=ResponseAnnouncementButtons(
                    repann,
                    channel=self.channel,
                    res_type=self.type,
                    start_time=start_time_int,
                    fist_int=interaction,
                ),
            )


class responseCmds(commands.GroupCog, group_name="response"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="create",
        description=f"Used to manually add responses to the database. [Dev Only]",
    )
    @app_commands.choices(
        response_type=[
            app_commands.Choice(name="Immediate Response", value="Immediate"),
            app_commands.Choice(name="Wartime Response", value="Wartime"),
            app_commands.Choice(name="Routine Response", value="Routine"),
            app_commands.Choice(name="Training Response", value="Training"),
            app_commands.Choice(name="Special Response", value="Special"),
        ]
    )
    async def r_create(
        self,
        interaction: discord.Interaction,
        response_type: app_commands.Choice[str],
        time_started: str,
        started: bool,
        spontaneous: bool,
        ann_msg_id: str,
        trellocard_id: str,
        time_ended: str,
        cancelled: bool,
        response_host: discord.Member,
    ):
        if DEVACCESS(interaction.user) is False:
            return await interaction.response.send_message(
                embed=embedBuilder(
                    responseType="perms",
                    embedDesc="This command is limited to Bot Developers.",
                ),
                ephemeral=True,
            )

        new_response, success = await createResponse(
            interaction,
            response_type.value,
            time_started,
            started,
            spontaneous,
            ann_msg_id,
            trellocard_id,
            time_ended,
            cancelled,
            response_host,
        )
        if success is True:
            response_embed = embedBuilder(
                responseType="succ", embedTitle="Created the following response:"
            )
            if type(new_response) is not str:
                if new_response.cancelled:
                    status = "Cancelled"
                elif str(new_response.timeEnded) != "Null":
                    status = "Concluded"
                elif new_response.started:
                    status = "Ongoing"
                else:
                    status = "Scheduled"
                trellocard = get_card_by_id(new_response.trellocardID)
                response_embed.add_field(
                    name=f"{new_response.responseType} || {status}",
                    value=f"""
                            >>> Response Leader: {interaction.guild.get_member(int(new_response.operativeDiscordID)).mention}
                            Time Started: <t:{new_response.timeStarted}>
                            Time ended: {'N/A' if str(new_response.timeEnded) == 'Null' else f'<t:{new_response.timeEnded}>'}
                            Spontaneous: {new_response.spontaneous}
                            Trello Card: {trellocard.short_url if trellocard else "Error fetching the trello card."}
                        """,
                    inline=False,
                )

            else:
                response_embed.add_field(
                    name="", value="No responses found in the database."
                )
        else:
            response_embed = embedBuilder(
                responseType="err",
                embedTitle="While creating the response...",
                embedDesc=f"{new_response}",
            )
            return await interaction.response.send_message(
                embed=response_embed, ephemeral=True
            )

        return await interaction.response.send_message(embed=response_embed)

    @app_commands.command(
        name="schedule", description="Used to schedule up-coming responses."
    )
    @app_commands.describe(type="Select your response type.")
    @app_commands.choices(
        type=[
            app_commands.Choice(name="Immediate Response", value="Immediate"),
            app_commands.Choice(name="Wartime Response", value="Wartime"),
            app_commands.Choice(name="Routine Response", value="Routine"),
            app_commands.Choice(name="Training Response", value="Training"),
            app_commands.Choice(name="Special Response", value="Special"),
        ]
    )
    async def schedule(
        self, interaction: discord.Interaction, type: app_commands.Choice[str]
    ):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if not checkPermission(
            interaction.user.top_role,
            interaction.guild.get_role(int(serverConfig.announcePermissionRole)),
        ):
            return await interaction.response.send_message(
                embed=embedBuilder(
                    responseType="perms",
                    embedDesc="This command is limited to Response Leaders and TRU Leadership.",
                ),
                ephemeral=True,
            )
        if await getOperator(interaction.user.id) == None:
            return await interaction.response.send_message(
                embed=embedBuilder(
                    responseType="err",
                    embedTitle="User not found!",
                    embedDesc=f"You need to be registered to use this command.",
                ),
                ephemeral=True,
            )
        return await interaction.response.send_modal(ScheduleModal(type=type.value))

    @app_commands.command(
        name="spontaneous",
        description="Used to start scheduled & spontaneous responses.",
    )
    @app_commands.choices(
        vc=[
            app_commands.Choice(name="[QSO] On Duty 1", value="937473342884179980"),
            app_commands.Choice(name="[QSO] On Duty 2", value="937473342884179981"),
            app_commands.Choice(name="[QSO] On Duty 3", value="937473342884179982"),
            app_commands.Choice(name="[QSO] On Duty 4", value="937473342884179983"),
            app_commands.Choice(name="[QSO] On Duty 5", value="937473342884179984"),
            app_commands.Choice(name="[QSO] VIP Raid", value="937473342884179985"),
            app_commands.Choice(name="[QSO] Events", value="992865433059340309"),
            app_commands.Choice(name="[TRU] On Duty 1", value="1095847944047054878"),
            app_commands.Choice(name="[TRU] On Duty 2", value="1096215752345915452"),
            app_commands.Choice(name="[TRU] Stage", value="950145200087511130"),
        ]
    )
    @app_commands.choices(
        rep_type=[
            app_commands.Choice(name="Immediate Response", value="Immediate"),
            app_commands.Choice(name="Wartime Response", value="Wartime"),
            app_commands.Choice(name="Routine Response", value="Routine"),
            app_commands.Choice(name="Training Response", value="Training"),
            app_commands.Choice(name="Special Response", value="Special"),
        ]
    )
    async def spontaneous(
        self,
        interaction: discord.Interaction,
        rep_type: app_commands.Choice[str],
        vc: app_commands.Choice[str],
        status: str,
    ):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if not checkPermission(
            interaction.user.top_role,
            interaction.guild.get_role(int(serverConfig.announcePermissionRole)),
        ):
            return await interaction.response.send_message(
                embed=embedBuilder(
                    responseType="perms",
                    embedDesc="This command is limited to Response Leaders and TRU Leadership.",
                ),
                ephemeral=True,
            )
        if await getOperator(interaction.user.id) == None:
            await interaction.response.send_message(
                embed=embedBuilder(
                    responseType="err",
                    embedTitle="User not found!",
                    embedDesc=f"You need to be registered to use this command.",
                ),
                ephemeral=True,
            )
        if await getUSERongoingResponses(
            interaction, interaction.user.id
        ):  # CHECK THAT USER DOES NOT HAVE AN ONGOING RESPONSE
            return await interaction.response.send_message(
                embed=embedBuilder(
                    responseType="err",
                    embedTitle=f"You still have an on-going response!",
                    embedDesc=f"You cannot host more than one responses at a time, please conclude your previous response first. If you believe this is an error, please ping <@!776226471575683082>.",
                ),
                ephemeral=True,
            )

        await interaction.response.send_message(
            embed=discord.Embed(
                color=YellowCOL,
                title=f"Creating Trello card and updating the database...",
            ),
            ephemeral=True,
        )
        start_time = int(time.time())
        trello_card_link = create_response_card(
            rep_type.value, True, start_time, interaction.user.id
        )
        response_leader = await getOperator(interaction.user.id)
        repann = discord.Embed(
            description=f"### <:trubotTRU:1096226111458918470> Spontaneous {rep_type.value} Response | Ongoing",
            color=TRUCommandCOL,
        )
        repann.add_field(
            name="Response Leader:", value=f"{interaction.user.mention}", inline=False
        )
        repann.add_field(
            name="Response Details:",
            value=f"> __Join link__: {response_leader.profileLink}\n> __Voice Channel__: <#{vc.value}>\n> __Status__: {status}",
            inline=False,
        )
        trurole: discord.Role = interaction.guild.get_role(
            int(serverConfig.announceRole)
        )
        channel = self.bot.get_channel(int(serverConfig.announceChannel))
        ann: discord.Message = await channel.send(
            trurole.mention,
            embed=repann,
            allowed_mentions=discord.AllowedMentions.all(),
        )
        new_response, success = await createResponse(
            interaction,
            str(rep_type.value),
            start_time,
            True,
            True,
            ann.id,
            trello_card_link.id,
        )
        await interaction.edit_original_response(
            embed=embedBuilder(
                responseType="succ",
                embedTitle="Response announced!",
                embedDesc=f"→ [Announcement]({ann.jump_url})\n→ [Trello Card]({trello_card_link.short_url})",
            )
        )

    @app_commands.command(
        name="commence", description="Used to start scheduled responses."
    )
    @app_commands.choices(
        vc=[
            app_commands.Choice(name="[QSO] On Duty 1", value="937473342884179980"),
            app_commands.Choice(name="[QSO] On Duty 2", value="937473342884179981"),
            app_commands.Choice(name="[QSO] On Duty 3", value="937473342884179982"),
            app_commands.Choice(name="[QSO] On Duty 4", value="937473342884179983"),
            app_commands.Choice(name="[QSO] On Duty 5", value="937473342884179984"),
            app_commands.Choice(name="[QSO] VIP Raid", value="937473342884179985"),
            app_commands.Choice(name="[QSO] Events", value="992865433059340309"),
            app_commands.Choice(name="[TRU] On Duty 1", value="1095847944047054878"),
            app_commands.Choice(name="[TRU] On Duty 2", value="1096215752345915452"),
            app_commands.Choice(name="[TRU] Stage", value="950145200087511130"),
        ]
    )
    async def commence(
        self,
        interaction: discord.Interaction,
        vc: app_commands.Choice[str],
        status: str,
    ):  # resp_type:app_commands.Choice[str]
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if not checkPermission(
            interaction.user.top_role,
            interaction.guild.get_role(int(serverConfig.announcePermissionRole)),
        ):
            await interaction.response.send_message(
                embed=embedBuilder(
                    responseType="perms",
                    embedDesc="This command is limited to Response Leaders and TRU Leadership.",
                ),
                ephemeral=True,
            )
        if await getOperator(interaction.user.id) == None:
            await interaction.response.send_message(
                embed=embedBuilder(
                    responseType="err",
                    embedTitle="User not found!",
                    embedDesc=f"You need to be registered to use this command.",
                ),
                ephemeral=True,
            )
        if await getUSERongoingResponses(
            interaction, interaction.user.id
        ):  # CHECK THAT USER DOES NOT HAVE AN ONGOING RESPONSE
            return await interaction.response.send_message(
                embed=embedBuilder(
                    responseType="err",
                    embedTitle=f"You still have an on-going response!",
                    embedDesc=f"You cannot host more than one responses at a time, please conclude your previous response first. If you believe this is an error, please ping <@!776226471575683082>.",
                ),
                ephemeral=True,
            )

        scheduled_responses = await getUSERplannedResponses(
            interaction, interaction.user.id
        )
        channel = self.bot.get_channel(int(serverConfig.announceChannel))
        if scheduled_responses:
            view = View().add_item(
                ResponseSelect(
                    responses=scheduled_responses,
                    status=status,
                    vc_id=vc.value,
                    channel=channel,
                    action_type="commence",
                    reason=None,
                )
            )
            return await interaction.response.send_message(view=view, ephemeral=True)
        else:
            return await interaction.response.send_message(
                embed=embedBuilder(
                    responseType="err",
                    embedTitle="No response found!",
                    embedDesc=f"You do not have a scheduled response to start!",
                ),
                ephemeral=True,
            )

    @app_commands.command(
        name="conclude", description="Used to conclude an operations."
    )
    @app_commands.describe(attendees='If somehow you had no attendees, just type "none" or "null".')
    async def conclude(
        self, interaction: discord.Interaction, attendees:str, co_hosts:str=None, picture: discord.Attachment = None
    ):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if not checkPermission(
            interaction.user.top_role,
            interaction.guild.get_role(int(serverConfig.announcePermissionRole)),
        ):
            await interaction.response.send_message(
                embed=embedBuilder(
                    responseType="perms",
                    embedDesc="This command is limited to Response Leaders and TRU Leadership.",
                ),
                ephemeral=True,
            )
        if await getOperator(interaction.user.id) == None:
            await interaction.response.send_message(
                embed=embedBuilder(
                    responseType="err",
                    embedTitle="User not found!",
                    embedDesc=f"You need to be registered to use this command.",
                ),
                ephemeral=True,
            )
        response_data = await getUSERongoingResponses(interaction, interaction.user.id)
        if response_data:
            await interaction.response.defer(ephemeral=True)
            channel = interaction.guild.get_channel(int(serverConfig.announceChannel))
            repmsg: discord.Message = await channel.fetch_message(
                int(response_data.responseID)
            )
            if repmsg:
                con_ann = discord.Embed(description=f"### {interaction.user.mention}'s {response_data.responseType} Response has concluded!",
                color=TRUCommandCOL,)
                
                rep_ann = repmsg.embeds[0]
                if rep_ann:
                    if response_data.spontaneous == True:
                        rep_ann.description = f"### <:trubotTRU:1096226111458918470> Spontaneous {response_data.responseType} Response | Concluded"
                    else:
                        rep_ann.description = f"### <:trubotTRU:1096226111458918470> {response_data.responseType} Response | Concluded"

            if picture:
                con_ann.set_image(url=picture.url)
            if rep_ann and repmsg and repmsg.author == self.bot: #1096140994556215407
                await repmsg.edit(embed=rep_ann)
            if repmsg:
                await repmsg.reply(embed=con_ann)
            await concludeResponse(interaction, str(response_data.responseID))
            
            if get_card_by_id(response_data.trellocardID):
                trellocardlink = get_card_by_id(response_data.trellocardID).short_url
                trellolink_found = True
            else:
                trellocardlink = "Error fetching the Trello card."
                trellolink_found = False
            
            await interaction.edit_original_response(
                embed=embedBuilder(
                    responseType="succ",
                    embedTitle="Response concluded!",
                    embedDesc=f"{'→ [Trello Card](' + trellocardlink + ')' if trellolink_found else ''}\nLogging all attendees, please wait...",
                )
            )
            
            ## Logging
            
            if str(attendees) != "none" or str(attendees) != "null" or co_hosts:
                attendee_mentions = []  # List to store mentioned attendees
                co_host_mentions = []   # List to store mentioned co-hosts
                failed_users = [] 

                if attendees and attendees != "none" and attendees != "null":
                    attendee_mentions = extract_user_ids(attendees)
                    attendee_mentions = list(filter(None, attendee_mentions))

                if co_hosts:
                    co_host_mentions = extract_user_ids(co_hosts)
                    co_host_mentions = list(filter(None, co_host_mentions))

 
                # Now you can use attendee_mentions and co_host_mentions lists to perform actions
                # For example, you can iterate through them using a loop
                
                for attendee_id in attendee_mentions:
                    attendee = interaction.guild.get_member(int(attendee_id))
                    if attendee:
                        operator = await getOperator(attendee.id)
                        if not add_log_comment(
                            username=str(operator.userName),
                            co_host=False,
                            host=str(interaction.user.nick),
                            response_type=str(response_data.responseType),
                            spontaneous=response_data.spontaneous,
                        ):
                            failed_users.append(attendee.display_name)

                for co_host_id in co_host_mentions:
                    co_host = interaction.guild.get_member(int(co_host_id))
                    if co_host:
                        operator = await getOperator(co_host.id)
                        
                        if not add_log_comment(
                            username=str(operator.userName),
                            co_host=True,
                            host=str(interaction.user.nick),
                            response_type=str(response_data.responseType),
                            spontaneous=response_data.spontaneous,
                        ):
                            failed_users.append(co_host.display_name)
            
                if failed_users:
                    failed_users_text = ", ".join(failed_users)
                    failed_users_response = f"Failed to add comments for: {failed_users_text}"
                else:
                    failed_users_response = "All comments added successfully."
                
                await interaction.followup.send(
                    embed=embedBuilder(
                        responseType="cust",
                        embedTitle="Logging Information!",
                        embedDesc=f"{failed_users_response}",
                        embedColor=SuccessCOL
                    ), ephemeral=True
                )
            
        else:
            await interaction.response.send_message(
                embed=embedBuilder(
                    responseType="err",
                    embedTitle="No response found",
                    embedDesc="You do not have an on-going response to conclude!",
                ),
                ephemeral=True,
            )
            

    @app_commands.command(
        name="cancel", description="Used to cancel an existing operation."
    )
    async def cancel(self, interaction: discord.Interaction, reason: str):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if not checkPermission(
            interaction.user.top_role,
            interaction.guild.get_role(int(serverConfig.announcePermissionRole)),
        ):
            await interaction.response.send_message(
                embed=embedBuilder(
                    responseType="perms",
                    embedDesc="This command is limited to Response Leaders and TRU Leadership.",
                ),
                ephemeral=True,
            )
        if await getOperator(interaction.user.id) == None:
            await interaction.response.send_message(
                embed=embedBuilder(
                    responseType="err",
                    embedTitle="User not found!",
                    embedDesc=f"You need to be registered to use this command.",
                ),
                ephemeral=True,
            )
        planned_responses = await getUSERplannedResponses(
            interaction, str(interaction.user.id)
        )
        if planned_responses:
            channel = self.bot.get_channel(int(serverConfig.announceChannel))
            view = View().add_item(
                ResponseSelect(
                    responses=planned_responses,
                    status=None,
                    vc_id=None,
                    channel=channel,
                    action_type="cancel",
                    reason=reason,
                )
            )
            await interaction.response.send_message(view=view, ephemeral=True)
        else:
            await interaction.response.send_message(
                embed=embedBuilder(
                    responseType="err",
                    embedTitle="No response found!",
                    embedDesc="You do not have an on-going response to cancel!",
                ),
                ephemeral=True,
            )

    @app_commands.command(name="view", description="Used to view response chains.")
    async def view_response(
        self,
        interaction: discord.Interaction,
        response_leader: discord.Member = None,
        response_id: str = None,
    ):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        await interaction.response.defer()
        # Fetch the response chains from the database
        if response_id:
            response_chains = await getResponseByID(response_id)
            response_chains = [response_chains] if response_chains else []
            response_embed = embedBuilder("succ", embedTitle="Response found!")

        elif response_leader:
            response_chains = await getUSERResponses(response_leader.id)
            response_embed = discord.Embed(
                color=TRUCommandCOL, title=f"Response Overview - {response_leader.nick}"
            )
        else:
            response_chains = await getAllResponses()
            response_embed = discord.Embed(
                color=TRUCommandCOL, title="General Response Overview"
            )

        if isinstance(response_chains, list):
            # print(response_chains)
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
                    trellocard = get_card_by_id(response.trellocardID)
                    response_embed.add_field(
                        name=f"{response.responseType} || {status}",
                        value=f"""
                            >>> Response Leader: {interaction.guild.get_member(int(response.operativeDiscordID)).mention}
                            Time Started: <t:{response.timeStarted}>
                            Time ended: {'N/A' if str(response.timeEnded) == 'Null' else f'<t:{response.timeEnded}>'}
                            Spontaneous: {response.spontaneous}
                            Trello Card: {trellocard.short_url if trellocard else "Error fetching the trello card."}
                            Response ID: `{response.responseID}`
                        """,
                        inline=False,
                    )

            else:
                response_embed.add_field(
                    name="", value="No responses found in the database."
                )
        else:
            response_embed.add_field(
                name="", value=f"Error retrieving response chains.\n{response_chains}"
            )

        await interaction.edit_original_response(embed=response_embed)

    @app_commands.command(name="delete", description="ONLY FOR DEVELOPMENT")
    async def delete_response(self, interaction: discord.Interaction, response_id: str):
        if DEVACCESS(interaction.user):
            if await deleteResponse(responseID=response_id) is True:
                return await interaction.response.send_message(
                    embed=embedBuilder(
                        "succ",
                        embedTitle="Response deleted!",
                        embedDesc=f"Successfully deleted response `{response_id}`",
                    )
                )
            else:
                return await interaction.response.send_message(
                    embed=embedBuilder(
                        "err",
                        embedTitle="Response not found!",
                        embedDesc=f"Response `{response_id}` was not found in the DB...",
                    )
                )
        else:
            return await interaction.response.send_message(
                embed=embedBuilder(
                    responseType="perms",
                    embedDesc="This command is limited to Bot Developers.",
                )
            )
