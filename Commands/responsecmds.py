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

### REDO ####

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
        trurole:discord.Role = discord.utils.get(interaction.guild.roles, name="TRU")
        msg:discord.Message = await self.channel.send(f"`{trurole.mention}`", embed=self.embed, allowed_mentions=discord.AllowedMentions.all())
        await self.fist_int.edit_original_response(view=None, embed=discord.Embed(title="<:dsbbotSuccess:953641647802056756> Response successfully announnced!", description=f"→ [Announcement]({msg.jump_url})\n→ [Trello Card]({trello_card_link})", color=SuccessCOL))
        await msg.add_reaction("<:trubotTRU:1096226111458918470>")
        db_response_schedule(self.res_type, trello_card_link, self.start_time, msg.id, interaction.user.id) #Database
        return

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def CancelButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        return await interaction.response.edit_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Announcement Cancelled!", color=ErrorCOL), view=None)

class CommenceAnnouncemenetButtons(discord.ui.View):
    def __init__(self, embed:discord.Embed, channel:discord.TextChannel, fist_int:discord.Interaction):
        super().__init__()
        self.embed = embed
        self.channel = channel
        self.fist_int = fist_int
        discord.ui.View.timeout = None
    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def ConfirmButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        trurole:discord.Role = discord.utils.get(interaction.guild.roles, name="TRU")
        msg:discord.Message = await self.channel.send(f"`{trurole.mention}`", embed=self.embed, allowed_mentions=discord.AllowedMentions.all())
        await self.fist_int.edit_original_response(view=None, embed=discord.Embed(title="<:dsbbotSuccess:953641647802056756> Response successfully started!", description=f"→ [Announcement]({msg.jump_url})", color=SuccessCOL))
        #database start op
        return

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def CancelButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        return await interaction.response.edit_message(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Announcement Cancelled!", color=ErrorCOL), view=None)

class ResponseSelect(discord.ui.Select):
    def __init__(self, responses, status, vc_id, channel):
        super().__init__(
            placeholder="Select a response from the dropdown.",
            options=[])
        self.responses = responses
        self.refresh_options()
        self.status = status
        self.vc_id = vc_id
        self.channel = channel

    def refresh_options(self):
        self.options = [
            discord.SelectOption(
                label=f"{response[1]} Response",
                description=f"{datetime.utcfromtimestamp(response[3]).strftime('%m/%d/%y || %H:%M ZULU')}",
                value=str(response[0])
            ) for response in self.responses
        ]

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_response = next((response for response in self.responses if response[0] == int(self.values[0])), None)
        test_ann = discord.Embed(title=f"<:trubotTRU:1096226111458918470> {self.view.selected_response[1]} Response | Commencing", color=TRUCommandCOL)
        test_ann.add_field(name="Response Leader", value=f"{interaction.user.mention}", inline=False)
        test_ann.add_field(name="Details", value=f"➥**Join link:** <profilelink>\n➥**Voice Channel:** <#{self.vc_id}>\n➥**Status:** {self.status}", inline=False)
        await interaction.response.edit_message(embed=test_ann, view=CommenceAnnouncemenetButtons(test_ann, self.channel, interaction))

class ScheduleModal(ui.Modal, title="Scheduled Response Announcement"):
    def __init__(self, type:str, channel:discord.TextChannel):
        super().__init__(timeout=None)
        self.type = type
        self.channel = channel
    
    start_time = ui.TextInput(label='Time', placeholder="Provide the start time using ONLY an Unix timestamp.",style=discord.TextStyle.short, required=True)
    notes = ui.TextInput(label='Notes', placeholder="Purpose, goals, etc.", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        if db_response_time_check(self.start_time.value):
            return await interaction.response.send_message(embed=discord.Embed(title=f"<:dsbbotFailed:953641818057216050> There is already a response planned for <t:{self.start_time}>!",color=ErrorCOL), ephemeral=True)
        repann = discord.Embed(title=f"<:trubotTRU:1096226111458918470> {self.type} Response | Scheduled", color=TRUCommandCOL)
        repann.add_field(name="Time", value=f"<t:{self.start_time}>", inline=False)
        repann.add_field(name="Response Leader", value=f"{interaction.user.mention}", inline=False)
        repann.add_field(name="Notes", value=f"{self.notes}", inline=False)
        await interaction.response.send_message(embed=repann, ephemeral=True, view=ResponseAnnouncementButtons(repann, channel=self.channel, res_type=self.type, start_time=int(self.start_time.value), fist_int=interaction))


class OperationCmds(commands.GroupCog, group_name='response'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @app_commands.command(name="schedule", description="Used to schedule up-coming responses.")
    @app_commands.describe(type="Which response type?")
    @app_commands.choices(type=[
        app_commands.Choice(name="ALPHA - Immediate Response", value="ALPHA"),
        app_commands.Choice(name="BRAVO - Wartime Response", value="BRAVO"),
        app_commands.Choice(name="CHARLIE - Routine Response", value="CHARLIE"),
        app_commands.Choice(name="DELTA - Training Response", value="DELTA"),
        app_commands.Choice(name="ECHO - Special Response", value="ECHO"),])
    async def schedule(self, interaction: discord.Interaction, type:app_commands.Choice[str]):
        if not TRURL(interaction.user):
            await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, description=f"You do not have permission run this command."), ephemeral=True)
        else:
            channel = self.bot.get_channel(1095865885304045609)
            return await interaction.response.send_modal(ScheduleModal(type=type.value, channel=channel))
    
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
        app_commands.Choice(name="ALPHA - Immediate Response", value="ALPHA"),
        app_commands.Choice(name="BRAVO - Wartime Response", value="BRAVO"),
        app_commands.Choice(name="CHARLIE - Routine Response", value="CHARLIE"),
        app_commands.Choice(name="DELTA - Training Response", value="DELTA"),
        app_commands.Choice(name="ECHO - Special Response", value="ECHO"),])
    async def spontaneous(self, interaction:discord.Interaction,rep_type:app_commands.Choice[str], vc:app_commands.Choice[str], status:str,):
        if not TRURL(interaction.user):
            await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, description=f"You do not have permission run this command."), ephemeral=True)
        
        if db_response_ongoing(interaction.user.id) is not None: #CHECK THAT USER DOES NOT HAVE AN ONGOING RESPONSE 
            return await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, title=f"You still have an on-going response!",description=f"You cannot host two responses at once, please conclude your previous response first. If you believe this is an error, please ping <@!776226471575683082>."), ephemeral=True)
        await interaction.response.send_message(embed = discord.Embed(color=YellowCOL, title=f"Creating Trello card and updating the database..."), ephemeral=True)
        start_time = int(time.time())
        trello_card_link = create_response_card(rep_type.value, True, start_time, interaction.user.id)
        repann = discord.Embed(title=f"<:trubotTRU:1096226111458918470> {rep_type.value} Response | Spontaneous", color=TRUCommandCOL)
        repann.add_field(name="Response Leader", value=f"{interaction.user.mention}", inline=False)
        repann.add_field(name="Details", value=f"➥**Join link:** <profilelink>\n➥**Voice Channel:** <#{vc.value}>\n➥**Status:** {status}", inline=False)
        trurole:discord.Role = discord.utils.get(interaction.guild.roles, name="TRU")
        channel = self.bot.get_channel(1095865885304045609)
        ann:discord.Message = await channel.send(trurole, embed=repann, allowed_mentions=discord.AllowedMentions.all())
        db_response_spontaneous(rep_type.value, trello_card_link, start_time, ann.id, interaction.user.id)
        await interaction.edit_original_response(embed=discord.Embed(title="<:dsbbotSuccess:953641647802056756> Response announnced!", description=f"→ [Announcement]({ann.jump_url})\n→ [Trello Card]({trello_card_link})", color=SuccessCOL))

    
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
        if not TRURL(interaction.user):
            await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, description=f"You do not have permission run this command."), ephemeral=True)
        if db_response_ongoing(interaction.user.id) is not None: #CHECK THAT USER DOES NOT HAVE AN ONGOING RESPONSE 
            return await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, title=f"You still have an on-going response!",description=f"You cannot host two responses at once, please conclude your previous response first. If you believe this is an error, please ping <@!776226471575683082>."), ephemeral=True)
        
        responses = get_getall_planned_responses_user(interaction.user.id)
        channel = self.bot.get_channel(1095865885304045609)
        if len(responses) == 1:
            repann = discord.Embed(title=f"<:trubotTRU:1096226111458918470> {responses[1]} Response | Spontaneous", color=TRUCommandCOL)
            repann.add_field(name="Response Leader", value=f"{interaction.user.mention}", inline=False)
            repann.add_field(name="Details", value=f"➥**Join link:** <profilelink>\n➥**Voice Channel:** <#{vc.value}>\n➥**Status:** {status}", inline=False)
            trurole:discord.Role = discord.utils.get(interaction.guild.roles, name="TRU")
            ann:discord.Message = await channel.send(trurole, embed=repann, allowed_mentions=discord.AllowedMentions.all())
            await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotSuccess:953641647802056756> Response announnced!", description=f"→ [Announcement]({ann.jump_url})", color=SuccessCOL), ephemeral=True)
        elif len(responses) > 1:
            view = View().add_item(ResponseSelect(responses, status, vc.value, channel))
            await interaction.response.send_message(view=view, ephemeral=True)
        else:
            return await interaction.response.send_message(embed=discord.Embed(description=f"You do not have any scheduled response to start!", color=ErrorCOL), ephemeral=True)
            
    
    @app_commands.command(name="conclude", description="Used to conclude an operations.")
    async def conclude(self, interaction:discord.Interaction, picture:discord.Attachment):
        if not TRURL(interaction.user):
            await interaction.response.send_message(embed = discord.Embed(color=ErrorCOL, description=f"You do not have permission run this command."), ephemeral=True)
            response_data = True
            if response_data:
                rep_ann:discord.Message = await interaction.channel.fetch_message(response_data)
                rep_ann = rep_ann.embeds[0]
                rep_ann.title = "<:TRU:1060271947725930496> Concluded Operation!"
                con_ann = discord.Embed(description=f"[User.Mentions]'s [type] response has concluded!", color=TRUCommandCOL)
                #op_conclude(pal)
                await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotSuccess:953641647802056756> Response Concluded!", description=f"→ [Trello Card]()", color=SuccessCOL), ephemeral=True)
                await rep_ann.edit(embed=con_ann)
                await rep_ann.reply(embed=con_ann)
            else:
                await interaction.response.send_message(embed=discord.Embed(description=f"You do not have an on-going response to conclude!", color=ErrorCOL), ephemeral=True)

    @app_commands.command(name="cancel", description="Used to cancel an existing operation.")
    async def cancel(self, interaction:discord.Interaction, reason:str):
        if TRUMEMBER(interaction.user):
            if TRURL(interaction.user):
                result = True
                if result:
                    
                    #IF MORE THAN ONE RESULT
                    
                    op_ann = await interaction.channel.fetch_message(result[6])
                    op_ann.clear_reactions()
                    op_emb = op_ann.embeds[0]
                    op_emb.title = "<:TRU:1060271947725930496> Cancelled Operation!"
                    can_ann = discord.Embed(description=f"[User.Mentions]'s [type] response has been cancelled!\n\nReason: {reason}", color=TRUCommandCOL)
                    op_cancel(result)
                    await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotSuccess:953641647802056756> Response cancelled!", description=f"→ [Trello Card]()", color=SuccessCOL), ephemeral=True)
                    await op_ann.edit(embed=op_emb)
                    await op_ann.reply(embed=can_ann)
                else:
                    await interaction.response.send_message(embed=discord.Embed(description=f"You do not have an on-going or scheduled response to cancel!", color=ErrorCOL), ephemeral=True)
                    
        