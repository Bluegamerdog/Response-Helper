import discord
import os
import sys
import datetime
import random
from Functions.mainVariables import *
from Functions.permFunctions import *
from Functions.formattingFunctions import embedBuilder
from Functions.randFunctions import (get_user_id_from_link, in_roblox_group, change_nickname)
#from Database_Functions.UserdbFunction import (db_register_get_data)
from discord.ext import commands
from discord import app_commands
from discord import ui
import Database_Functions.PrismaFunctions as dbFuncs

    


    
'''
@app_commands.command(name="trukick", description="Used to kick TRU members.")
async def trukick_user(self, interaction:discord.Interaction, member:discord.Member, reason:str):
    if not TRULEAD(interaction.user):
        return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotDeny:1073668785262833735> Missing Permission!", description=f"You must be a member of TRUPC or above to use this command."), ephemeral=True)
    try:
        username = str(member.display_name).split()[-1] 
        group = await roblox_client.get_group(15155104) # Currently DSB
        user = await roblox_client.get_user_by_username(username)
        logsch = self.bot.get_channel(1096146385830690866) # Currently #startup || 1008449677210943548 #audit-logs
        kickembed = discord.Embed(title=f"<:TRU:1060271947725930496> Kicked TRU Member", description=f"{member.mention} has been kicked from TRU by {interaction.user.mention}.\n\n**Reason:** {reason}", color=DarkRedCOL)
        kickembed.set_thumbnail(url=member.avatar.url)
        kickembed.set_footer(text=f"ID: {member.id} • {datetime.datetime.now().strftime('%m/%d/%Y %H:%M %p')}")
        logmsg = await logsch.send(embed=kickembed)
        await interaction.response.send_message(embed = discord.Embed(title=f"<:trubotAccepted:1096225940578766968> Member removed", description=f"Successfully removed {member.mention} from TRU.\n\n**Reason:** {reason}\n→ [Audit Log]({logmsg.jump_url})", color=DarkRedCOL))
        await member.send(embed = discord.Embed(title=f"You have been kicked from Defensive Squadron Bravo.",description=f"**Reason:** {reason}", color=DarkRedCOL))
        await group.kick_user(user)
        await member.kick(reason=reason)
    except Exception as e:
        print(e)
        await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Error!", description=f"An error occurred while accepting {username}: {str(e)}"), ephemeral=True)        

@app_commands.command(name="trustrike", description="Give out strikes in TRU.")
async def trustrike_user(self, interaction:discord.Interaction, member:discord.Member, reason:str):
    if not TRULEAD(interaction.user):
        return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotDeny:1073668785262833735> Missing Permission!", description=f"You must be a member of TRUPC or above to use this command."), ephemeral=True)
    else:
        strikeemb = discord.Embed(title=f"<:TRU:1060271947725930496> Striked TRU Member", description=f"{member.mention} has recieved a strike in TRU from {interaction.user.mention}.\n\n**Reason:** {reason}", color=DarkRedCOL)
        #strikeemb.set_thumbnail(url=member.avatar.url)
        strikeemb.set_footer(text=f"ID: {member.id} • {datetime.datetime.now().strftime('%m/%d/%Y %H:%M %p')}")
        logsch = self.bot.get_channel(1054705433971003412) # 1008449677210943548 #audit-logs
        logmsg = await logsch.send(embed=strikeemb)
        await interaction.response.send_message(embed = discord.Embed(title=f"<:trubotAccepted:1096225940578766968> Member striked", description=f"Successfully striked {member.mention}.\n\n**Reason:** {reason}\n→ [Audit Log]({logmsg.jump_url})", color=DarkRedCOL))
        await member.send(embed = discord.Embed(title=f"You have received a strike in Defensive Squadron Bravo.",description=f"**Reason:** {reason}", color=DarkRedCOL))
        pass

@app_commands.command(name="trustrikes", description="See a users moderation history in TRU.")
async def trustrikesview_user(self, interaction:discord.Interaction, member:discord.Member=None):
    if member == None:
        member = interaction.user
    if member != interaction.user and TRULEAD(interaction.user) == False:
        return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotDeny:1073668785262833735> Missing Permission!", description=f"You must be a member of TRUPC or above to view someone else's strikes."), ephemeral=True)
    else:
        # Get the user's warnings from the database
        warnings = None #await self.db.get_warnings(member.id)
        if not warnings:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="<:trubotAbstain:1099642858505515018> No warnings found",
                    description=f"No warnings found for {member.mention}.",
                    color=DarkRedCOL
                )
            )

        # Create the embed to display the warnings
        embed = discord.Embed(title=f"Warnings for {member}", color=TRUCommandCOL)
        for i, warn in enumerate(warnings):
            embed.add_field(name=f"Warning {i+1}",value=f"**Reason:** {warn['reason']}\n**Moderator:** {await self.bot.fetch_user(warn['moderator'])}\n**Date:** {warn['date'].strftime('%m/%d/%Y %I:%M %p')}"
            )

        await interaction.response.send_message(embed=embed)
'''        





