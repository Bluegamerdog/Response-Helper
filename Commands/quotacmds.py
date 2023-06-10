import asyncio
import datetime
import time

import discord
from discord import app_commands
from discord.ext import commands

import Database_Functions.PrismaFunctions as dbFuncs
from Database_Functions.PrismaFunctions import *
from Database_Functions.UserdbFunction import (add_points, get_points,
                                               remove_points, reset_points)
from Functions.formattingFunctions import embedBuilder
from Functions.mainVariables import *
from Functions.permFunctions import *
from prisma import Prisma

# Embed types: Success, Warning, Error

class patrolCmds(commands.GroupCog, group_name="patrol"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="start", description="Start a log.")
    async def startlog(self, interaction: discord.Interaction):
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        if checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.logPermissionRole))):
            operativeResponse, operativeResponseBool = await dbFuncs.fetch_operative(interaction)
            if operativeResponseBool:
                date_time = datetime.datetime.now()
                unixTime = int(time.mktime(date_time.timetuple()))
                dbResponse, dbResponseBool = await dbFuncs.prismaCreatelog(interaction, str(unixTime))
                if dbResponseBool == True:
                    successEmbed = embedBuilder("Success", embedTitle="Log successful started! ", embedDesc=("Log started at: <t:" + str(unixTime) + ":f>"))
                    print(successEmbed)
                    await interaction.response.send_message(embed=successEmbed)
                else:
                    errorEmbed = embedBuilder("Error", embedTitle="An error occurred.", embedDesc="Error details: " + str(dbResponse))
                    await interaction.response.send_message(embed=errorEmbed)
            else:
                errorEmbed = embedBuilder("Error", embedTitle="An error occurred.",
                                          embedDesc="Error details: " + str(operativeResponse))
                await interaction.response.send_message(embed=errorEmbed)


        else:
            errEmbed = embedBuilder("Error", embedTitle="Permission error:",
                                    embedDesc="You are not: <@&" + str(serverConfig.logPermissionRole) + ">")
            await interaction.response.send_message(embed=errEmbed)



    @app_commands.command(name="end", description="End your current log.")
    async def endlog(self, interaction: discord.Interaction):
        serverConfig = await fetch_config(interaction)
        op, opResponse = await fetch_operative(interaction)
        if not checkPermission(interaction.user.top_role, serverConfig.logPermissionRole):
            errEmbed = embedBuilder("Error", embedTitle="Permission error:",
                                    embedDesc="You are not: <@&" + str(serverConfig.logPermissionRole) + ">")
            await interaction.response.send_message(embed=errEmbed)
            return
        print(op)
        print(opResponse)
        if not opResponse:
            errEmbed = embedBuilder("Error", embedTitle="Operative not found!",
                                    embedDesc="Please make sure you are regsitered with the TRU bot before running commands!")
            await interaction.response.send_message(embed=errEmbed)
            return
        if checkPermission(interaction.user.top_role, interaction.guild.get_role(int(serverConfig.logPermissionRole))):
            date_time = datetime.datetime.now()
            unixTime = int(time.mktime(date_time.timetuple()))
            dbMessage, dbSuccess = await prismaEndLog(interaction, str(unixTime))
            if dbSuccess:
                successEmbed = embedBuilder("Success", embedTitle="Log ended successfully!", embedDesc="A log with the following details below was ended.")
                successEmbed.add_field(name="Time ended: ", value= "<t:" + str(unixTime) + ":f>")
                successEmbed.add_field(name="Log Time: ", value= str(dbMessage) + " minutes")
                await interaction.response.send_message(embed=successEmbed)
            else:
                errorEmbed = embedBuilder("Error", embedTitle="Unable to end log:", embedDesc="**Reason:** " + str(dbMessage))
                await interaction.response.send_message(embed=errorEmbed)
        else:
            errEmbed = embedBuilder("Error", embedTitle="Permission error:",
                                    embedDesc="You are not: <@&" + str(serverConfig.logPermissionRole) + ">")
            await interaction.response.send_message(embed=errEmbed)

        
    @app_commands.command(name="cancel", description="Cancel current log.")
    async def cancellog(self, interaction: discord.Interaction):
        serverConfig = await fetch_config(interaction)
        if not checkPermission(interaction.user.top_role, serverConfig.logPermissionRole):
            errEmbed = embedBuilder("Error", embedTitle="Permission error:",
                                    embedDesc="You are not: <@&" + str(serverConfig.logPermissionRole) + ">")
            await interaction.response.send_message(embed=errEmbed)
            return
        op, opResponse = await fetch_operative(interaction)
        log, logResponse = await checkLog(interaction)
        if not opResponse:
            errEmbed = embedBuilder("Error", embedTitle="Operative not found!",
                                    embedDesc="Please make sure you are regsitered with the TRU bot before running commands!")
            await interaction.response.send_message(embed=errEmbed)
        if not logResponse:
            errEmbed = embedBuilder("Error", embedTitle="Log not found!",
                                    embedDesc="No active log was found under your operative id.")
            await interaction.response.send_message(embed=errEmbed)
        if logResponse:
            print("Found a log")
            await prismaCancelLog(interaction)
            successEmbed = embedBuilder("Error", embedTitle="Log cancelled.",
                                        embedDesc="A log with the following details below was cancelled.")
            successEmbed.add_field(name="Log ID: ", value=str(log.logID))
            successEmbed.add_field(name="Log start time: ", value="<t:" + str(log.timeStarted) + ":f>")
            await interaction.response.send_message(embed=successEmbed)

   
### REWORK ###
class pointCmds(commands.GroupCog, group_name='attendace'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    

    @app_commands.command(name="add", description="Increases the attendance counter of a user.")
    async def add(self, interaction:discord.Interaction, member:discord.Member, amount:int):
        user = interaction.user
        if(not TRULEAD(user)): # check if user has permission
            embed = discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Failed to add points to user!", description=f"You must be a member of TRUPC or above to add points.")
            await interaction.response.send_message(embed=embed)
            return
        if(type(amount)==int and int(amount) >= 1):
            if add_points(member.id, amount) == True: # add points to the user
                    embed = discord.Embed(color=TRUCommandCOL, title=f"<:trubotAccepted:1096225940578766968> Successfully added {amount} point to **{member.display_name}**!" if amount == 1 else f"<:trubotAccepted:1096225940578766968> Successfully added {amount} points to **{member.display_name}**!", description=f"**{member.display_name}** now has **{get_points(member.id)}** point." if int(get_points(member.id)) == 1 else f"**{member.display_name}** now has **{get_points(member.id)}** points." )
            else:
                embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Failed to add points to `{member}`!", description="User not found in registry database.", color=ErrorCOL)
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Failed to add points to **{member.display_name}**!", description="Invalid point number.", color=ErrorCOL)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="remove", description="Decreases the attendance counter of a user. [TRUPC+]")
    async def remove(self, interaction:discord.Interaction, member:discord.Member, amount:int):
        if not TRULEAD(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Failed to remove points from user!", description=f"You must be a member of TRUPC or above to remove points."))
        if(type(amount)==int and int(amount)>=1):
            if remove_points(member.id, amount) == True: #removes points from user
                embed = discord.Embed(color=TRUCommandCOL, title=f"<:trubotAccepted:1096225940578766968> Successfully removed {amount} point from **{member.display_name}**!" if amount == 1 else f"<:trubotAccepted:1096225940578766968> Successfully removed {amount} points from {member.display_name}!", description=f"**{member.display_name}** now has **{get_points(member.id)}** point." if int(get_points(member.id)) == 1 else f"**{member.display_name}** now has **{get_points(member.id)}** points." )
            else:
                embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Failed to remove points from `{member}`!", description="User not found in registry database.", color=ErrorCOL)
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Failed to remove points from **{member.display_name}**!", description="Invalid point number.", color=ErrorCOL)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    '''        
    @app_commands.command(name="view",description="View someone else's current point count.")
    async def view(self, interaction: discord.Interaction, user:discord.Member=None):
        if not TRUMEMBER(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Missing permissions!", description=f"Only TRU Private First Class or above may interact with TRU Helper."), ephemeral=True)
        else:
            embed = discord.Embed(color=TRUCommandCOL, title=f"<:trubotAccepted:1096225940578766968> Point data found for {user.display_name}!" if user and user != interaction.user else f"<:trubotAccepted:1096225940578766968> Point data found!")
            if user == None:
                user = interaction.user
            points = get_points(user.id)
            if points is False:
                return await interaction.response.send_message(embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> No point data found for `{user}`!", description="User not found in registry database.", color=ErrorCOL))
            username = str(user.display_name)
            embed = discord.Embed(color=TRUCommandCOL, title=f"<:trubotAccepted:1096225940578766968> Point data for {username}!")
            data = db_register_get_data(user.id)
            quota, rank = get_point_quota(user, data)
            if quota:
                onloa = onLoA(user)
                percent = float(points / quota * 100)
                qm = quota_prog_display(percent, onloa)
                if onloa == True:
                    quota = 0
                embed.add_field(name=f"{qm} {percent:.1f}% || {points}/{quota}", value="")
                if not data[4]:
                    embed.add_field(name="", value=f"Rank: **{rank}**\nPoints: **{points}**", inline=False)
                else:
                    embed.add_field(name="", value=f"Rank: **{rank}**\nPoints: **{points}**\nDays excused: **{data[4]}**", inline=False)
            else:
                embed.add_field(name="", value=f"Rank: {rank}\nPoints: **{points}**", inline=False)
            
            await interaction.response.send_message(embed=embed)
    '''
    @app_commands.command(name="reset",description="Resets the points of all users to zero. [TRUPC+]")
    async def reset(self, interaction:discord.Interaction):
        if not TRULEAD(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Failed to reset points!", description="You must be a member of TRUCOMM or above to purge the registry database.", color=ErrorCOL))
        else:
            await interaction.response.send_message(embed=discord.Embed(description="<:dsbbotUnderReview:1067970676041982053> Waiting for response..."))
            embed = discord.Embed(color=HRCommandsCOL, description=f"<:dsbbotUnderReview:1067970676041982053> **Are you sure you want to reset the points?**\nReact with <:trubotApproved:1099642447526637670> to confirm.", colour=ErrorCOL)
            msg = await interaction.edit_original_response(embed=embed)
            await msg.add_reaction("<:trubotApproved:1099642447526637670>")
            
            
            # Wait for the user's reaction
            def check(reaction, user):
                return user == interaction.user and str(reaction.emoji) == '<:trubotApproved:1099642447526637670>'
            try:
                reaction, user_r = await self.bot.wait_for('reaction_add', check=check, timeout=10)
            except asyncio.TimeoutError:
                embed = discord.Embed(color=ErrorCOL, description=f"<:dsbbotFailed:953641818057216050> Timed out waiting for reaction.")
                tasks = [    msg.clear_reactions(),    interaction.edit_original_response(embed=embed)]
                await asyncio.gather(*tasks)

            else:
                if TRULEAD(user_r):
                    success = await reset_points()
                    print("Points successfully reset!")
                    if success:
                        embed = discord.Embed(title="<:trubotAccepted:1096225940578766968> Point reset successful!", color=discord.Color.green())
                        await interaction.edit_original_response(embed=embed)
                    else:
                        embed = discord.Embed(title="<:dsbbotFailed:953641818057216050> Point reset failed!", description=f"Something went wrong...", color=ErrorCOL)
                        tasks = [    msg.clear_reactions(),    interaction.edit_original_response(embed=embed)]
                        await asyncio.gather(*tasks)

class mypointsCmd(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.client = bot
    
    @app_commands.command(name="viewdata",description="View someone elses current quota status.")
    async def mypoints(self, interaction: discord.Interaction, member:discord.Member=None):
        try:
            if member==None:
                member = interaction.user
            
            db = Prisma()
            await db.connect()
            data = await db.operative.find_unique(where={"discordID": f"{member.id}"})
            log_amount = await db.logs.find_many(where={"operativeDiscordID": f"{member.id}"})
            await db.disconnect()
            
            if data == None:
                return await interaction.response.send_message(embed=embedBuilder("Error", embedDesc=f"Unable to find userdata on {member.mention}. Maybe they aren't registered?", embedTitle="No data found!"))
            else:
                embed = embedBuilder("Success", embedTitle=f"<:trubotAccepted:1096225940578766968> User data found!", embedDesc=f"Displaying {interaction.user.mention}'s data for block `TBA`.")
                embed.add_field(name="TRU Rank", value=f"> {data.rank}", inline=True)
                embed.add_field(name="Activity Status", value=f"> On Leave of Absence" if onLoA(member) else f"> Active Duty", inline=True)
                embed.add_field(name="", value="", inline=False) # Filler for 2x2 field config because discord
                embed.add_field(name="Responses Attended", value=f"> `TBA`", inline=True) # Need to add response attendance count
                embed.add_field(name="Patrols Logged", value=f"> {len(log_amount)}/Quota", inline=True) #(need to add something and be able to change quota at will)
                await interaction.response.send_message(embed=embed)
        except Exception as e:
            errEmbed = embedBuilder("Error", embedDesc=str(e), embedTitle="An error occurred.")
            await interaction.response.send_message(embed=errEmbed, ephemeral=True)
                



