import discord
import os
import sys
import datetime
import time
import asyncio
from Functions.mainVariables import *
from Functions.permFunctions import *
from Database_Functions.PrismaFunctions import *
from discord.ext import commands
from discord import app_commands

# (COMPLTE)
class BotCmds(commands.Cog):
    def __init__(self, bot: commands.Bot, start_time):
        self.bot = bot
        self.start_time = start_time

    ## DEV COMMANDS ##
    #MAYBE EDIT MESSAGE AFTER RELOAD
    @app_commands.command(name="reload",description="Restarts the TRU Helper. [TRUPC+]")
    async def restart(self, interaction:discord.Interaction, commands:str=None):
        if not TRULEAD(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotDeny:1073668785262833735> Missing permissions!", description="You must be a member of TRUPC or above to use the restart command.", color=ErrorCOL))
        if commands != None:
            await interaction.response.send_message(embed=discord.Embed(color=YellowCOL, title="<:trubotWarning:1099642918974783519> Syncing Commands..."))
            try:
                await self.bot.tree.fetch_commands()
                synced = await self.bot.tree.sync()
                return await interaction.edit_original_response(embed=discord.Embed(color=DarkGreenCOL, title=f"<:trubotAccepted:1096225940578766968> Synced {len(synced)} commands!"))
            except Exception as e:
                print(f"Error syncing commands: {e}")
                return await interaction.edit_original_response(embed=discord.Embed(color=DarkRedCOL, title=f"<:dsbbotFailed:953641818057216050> Syncing failed!", description=f"**Error:** {e}"))
        else:
            await interaction.response.send_message(embed=discord.Embed(color=YellowCOL, title="<:trubotWarning:1099642918974783519> Restarting..."))
            print(f"=========\nBot restarted by {interaction.user}\n=========")
            os.execv(sys.executable, ['python'] + sys.argv)
    #COMPLETE        
    @app_commands.command(name="shutdown", description="Shuts down TRU Helper. [DEVACCESS]")
    async def shutdown(self, interaction:discord.Interaction):
        if not DEVACCESS(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotDeny:1073668785262833735> Missing permissions!", description="You must be member of TRUCOMM or above to use the shutdown command.", color=ErrorCOL))
        else:
            embed = discord.Embed(color=ErrorCOL, title="<:trubotWarning:1099642918974783519> Shutting down...")
            await interaction.response.send_message(embed=embed)
            print(f"=========\nBot closed by {interaction.user}\n=========")
            return await self.bot.close()
    #COMPLETE
    @app_commands.command(name="activity", description="Sets TRU Helper's activity. [DEVACCESS]")
    @app_commands.choices(type=[
        app_commands.Choice(name="clear activity", value="clear"),
        app_commands.Choice(name="Watch command", value="w_enable"),
        app_commands.Choice(name="'lmfao' event", value="lmfao_event"),
        app_commands.Choice(name="'Playing...'", value="Playing"),
        app_commands.Choice(name="'Streaming...'", value="Streaming"),
        app_commands.Choice(name="'Listening...'", value="Listening"),
        app_commands.Choice(name="'Watching...'", value="Watching")])
    async def change_status(self, interaction: discord.Interaction, type:app_commands.Choice[str], name:str=None):
        if not DEVACCESS(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotDeny:1073668785262833735> Missing permissions!", description="You must be listed under DEVACCESS to use this command.", color=ErrorCOL), ephemeral=True)
            
        activity_types = {
            "Playing": discord.ActivityType.playing,
            "Streaming": discord.ActivityType.streaming,
            "Listening": discord.ActivityType.listening,
            "Watching": discord.ActivityType.watching,
        }

        global watching_command
        if type.value in activity_types:
            activity = discord.Activity(type=activity_types[type.value], name=name)
            await self.bot.change_presence(activity=activity)
            return await interaction.response.send_message(f"Status updated: `{type.value}`**`{name}`**", ephemeral=True)
        elif type.value == "w_enable":
            if watching_command == False:
                watching_command = True
                return await interaction.response.send_message(f"The </watching:1070173169937289276> command is now enabled.", ephemeral=True)
            elif watching_command == True:
                watching_command = False
                return await interaction.response.send_message(f"The </watching:1070173169937289276> command is now disabled.", ephemeral=True)
        elif type.value == "clear":
            await self.bot.change_presence(activity=None)
            return await interaction.response.send_message("TRU Helper's activity has been cleared.", ephemeral=True)
        elif type.value == "lmfao_event":
            global lmfao_event
            if lmfao_event == True:
                lmfao_event = False
                return await interaction.response.send_message(f"The `lmfao_event` is now disabled.", ephemeral=True)
            elif lmfao_event == False:
                lmfao_event = True
                return await interaction.response.send_message(f"The `lmfao_event` is now enabled.", ephemeral=True)
        else:
            return await interaction.response.send_message("Something went wrong...", ephemeral=True)
    #COMPLTE
    @app_commands.command(name="uptime", description="Shows how long the bot has been online for.")
    async def uptime(self, interation:discord.Interaction):
        current_time = datetime.now()
        uptime = current_time - self.start_time
        unix_time = int(time.mktime(self.start_time.timetuple()))
        await interation.response.send_message(embed=discord.Embed(color=TRUCommandCOL,title="TRU Helper Uptime", description=f"➥ TRU Helper started <t:{unix_time}:R> (<t:{unix_time}>)"))
        
## Needs a rework cause I'd like this to be a thing ##
'''     
class DatabaseCmds(commands.GroupCog, group_name='db'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    @app_commands.command(name="edit", description="Able to change any value of the database.")
    @app_commands.choices(database=[
        app_commands.Choice(name="Operative Database", value="operative"),
        app_commands.Choice(name="Response Database", value="response"),
        app_commands.Choice(name="Rank Database", value="ranks"),
        app_commands.Choice(name="Log Database", value="logs"),
        app_commands.Choice(name="Server Database", value="server")])
    @app_commands.choices(action=[
        app_commands.Choice(name="Clear database [CAUTION]", value="clear"),
        app_commands.Choice(name="Change value", value="change")])
    async def edit_db(self, interaction:discord.Interaction, database:app_commands.Choice[str], action:app_commands.Choice[str], where:str=None, old_data:str=None, new_data:str=None):
        if not DEVACCESS(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(title="<:trubotDenied:1099642433588965447> Permission Denied!", description="You must be listed under DEVACCESS to use this command.", color=ErrorCOL))
        else:
            if action.value == "clear":
                try:
                    await interaction.response.send_message(embed=discord.Embed(description="<:trubotBeingLookedInto:1099642414303559720> Checking database..."))
                    msg = await interaction.edit_original_response(embed = discord.Embed(color=HRCommandsCOL, description=f"<:trubotWarning:1099642918974783519> **Are you sure you want to clear {table}?**\nReact with <:trubotApproved:1099642447526637670> to confirm.", colour=ErrorCOL))
                    await msg.add_reaction("<:trubotApproved:1099642447526637670>")
                    
                    def check(reaction, user):
                        return user == interaction.user and str(reaction.emoji) == '<:trubotApproved:1099642447526637670>'
                    try:
                        reaction, user_r = await self.bot.wait_for('reaction_add', check=check, timeout=10)
                    except asyncio.TimeoutError:
                        embed = discord.Embed(color=ErrorCOL, description=f"<:trubotDenied:1099642433588965447> Timed out waiting for reaction.")
                        tasks = [    msg.clear_reactions(),    interaction.edit_original_response(embed=embed)]
                        await asyncio.gather(*tasks)

                    else:
                        if DEVACCESS(user_r):
                            clear_table(database.value, table)
                            print(f"Cleared {table} by {interaction.user}!")
                            embed = discord.Embed(title="<:trubotAccepted:1096225940578766968> Point reset successful!", color=discord.Color.green())
                            return await interaction.edit_original_response(embed = discord.Embed(title=f"<:trubotWarning:1099642918974783519> Database table `{database.value}` successfully cleared!", color=DarkGreenCOL))
                except Exception as e:
                    return await interaction.edit_original_response(embed=discord.Embed(title="<:dsbbotFailed:953641818057216050> Error!", description=f"{e}", color=ErrorCOL))  
            else:
                try:
                    data = edit_database_value(database.value, where, old_data, new_data)
                    if data:
                        return await interaction.response.send_message(embed=discord.Embed(title="<:trubotDenied:1099642433588965447> Error!", description=f"{data}", color=ErrorCOL), ephemeral=True)
                    return await interaction.response.send_message(embed=discord.Embed(title="<:trubotAccepted:1096225940578766968> Successfully updated!", description=f"**Database:** `{database.value}` || **Column:** `{where}`\n\nChanged: `{old_data}` -> `{new_data}`", color=SuccessCOL))
                except Exception as e:
                    return await interaction.response.send_message(embed=discord.Embed(title="<:trubotDenied:1099642433588965447> Error!", description=f"{e}", color=ErrorCOL), ephemeral=True)
'''