import asyncio
import datetime
import os
import sys
import time

import discord
from discord import app_commands
from discord.ext import commands

import Database_Functions.PrismaFunctions as dbFuncs
from Database_Functions.PrismaFunctions import *
from Functions import permFunctions
from Functions.formattingFunctions import embedBuilder
from Functions.mainVariables import *
from Functions.permFunctions import *


class botCmds(commands.Cog):
    def __init__(self, bot: commands.Bot, start_time):
        self.bot = bot

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
    
    @app_commands.command(name="shutdown", description="Shuts down TRU Helper. [DEVACCESS]")
    async def shutdown(self, interaction:discord.Interaction):
        if not DEVACCESS(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(title="<:dsbbotDeny:1073668785262833735> Missing permissions!", description="You must be member of TRUCOMM or above to use the shutdown command.", color=ErrorCOL))
        else:
            embed = discord.Embed(color=ErrorCOL, title="<:trubotWarning:1099642918974783519> Shutting down...")
            await interaction.response.send_message(embed=embed)
            print(f"=========\nBot closed by {interaction.user}\n=========")
            return await self.bot.close()


class serverconfigCmds(commands.GroupCog, group_name="serverconfigs"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @app_commands.command(name="set", description="Configure bot permission settings")
    async def serverconfig(self, interaction: discord.Interaction, logrole: discord.Role, schedule_role: discord.Role,
                           announce_channel: discord.TextChannel, command_role: discord.Role,
                           developer_role: discord.Role, ping_role: discord.Role):
        requiredRole = interaction.guild.get_role(1095826407894024192)
        if checkPermission(interaction.user.top_role, interaction.guild.get_role(1095826407894024192)):

            db = Prisma()
            await db.connect()
            #await db.operative.f
            await db.server.upsert(where={
                'serverID': str(interaction.guild.id)
            },
                data={
                    'create': {
                        'serverID': str(interaction.guild.id),
                        'announceRole': str(ping_role.id),
                        'announceChannel': str(announce_channel.id),
                        'logPermissionRole': str(logrole.id),
                        'announcePermissionRole': str(schedule_role.id),
                        'commandRole': str(command_role.id),
                        'developerRole': str(developer_role.id)
                    }, 'update': {
                        'announceRole': str(ping_role.id),
                        'announceChannel': str(announce_channel.id),
                        'logPermissionRole': str(logrole.id),
                        'announcePermissionRole': str(schedule_role.id),
                        'commandRole': str(command_role.id),
                        'developerRole': str(developer_role.id)
                    }

                })
            await db.disconnect()

            embed = embedBuilder(embedType="Success", embedTitle="Success!",
                                 embedDesc="A configuration with the following details was made: ")
            embed.add_field(name="Response pings: ", value="<@&" + str(ping_role.id) + ">")
            embed.add_field(name="Member role: ", value="<@&" + str(logrole.id) + ">")
            embed.add_field(name="Response Leaders: ", value="<@&" + str(schedule_role.id) + ">")
            embed.add_field(name="Response announcements channel: ", value="<#" + str(announce_channel.id) + ">")
            embed.add_field(name="TRU Leadership role: ", value="<@&" + str(command_role.id) + ">")
            embed.add_field(name="TRU Helper Dev role: ", value="<@&" + str(developer_role.id) + ">")
            await interaction.response.send_message(embed=embed, ephemeral=False)
        else:
            errEmbed = embedBuilder("Error", embedTitle="Permission error:",
                                    embedDesc="You are not: <@&" + str(requiredRole.id) + ">")
            await interaction.response.send_message(embed=errEmbed)
    
    @app_commands.command(name="edit", description="Edit bot permission settings")
    async def editconfig(self, interaction: discord.Interaction, logrole: discord.Role = None,
                        response_leaders: discord.Role = None, resp_announcement_channel: discord.TextChannel = None,
                        leadership_role: discord.Role = None, developer_role: discord.Role = None,
                        response_pings: discord.Role = None):
        db = Prisma()
        await db.connect()

        server_config = await db.server.find_first(where={'serverID': str(interaction.guild.id)})
        if not server_config:
            await interaction.response.send_message(
                "Configuration not found. Please use the `/serverconfig` command to create a configuration first.",
                ephemeral=True)
            return

        update_data = {}
        if logrole:
            update_data['logPermissionRole'] = str(logrole.id)
        if response_leaders:
            update_data['announcePermissionRole'] = str(response_leaders.id)
        if resp_announcement_channel:
            update_data['announceChannel'] = str(resp_announcement_channel.id)
        if leadership_role:
            update_data['commandRole'] = str(leadership_role.id)
        if developer_role:
            update_data['developerRole'] = str(developer_role.id)
        if response_pings:
            update_data['announceRole'] = str(response_pings.id)

        await db.server.update(where={'serverID': str(interaction.guild.id)}, data=update_data)
        await db.disconnect()
        serverConfig = await dbFuncs.fetch_config(interaction=interaction)
        embed = embedBuilder(embedType="Success", embedTitle="<:trubotAccepted:1096225940578766968> Successfully updated server configs!",
                            embedDesc=f"{interaction.guild.name}'s Server Configuration updated: ")
        if response_pings:
            embed.add_field(name="Response pings: ", value="<@&" + str(serverConfig.announceRole) + ">")
        if logrole:
            embed.add_field(name="Member role: ", value="<@&" + str(serverConfig.logPermissionRole) + ">")
        if response_leaders:
            embed.add_field(name="Response Leaders: ", value="<@&" + str(serverConfig.announcePermissionRole) + ">")
        if resp_announcement_channel:
            embed.add_field(name="Response announcements channel: ", value="<#" + str(serverConfig.announceChannel) + ">")
        if leadership_role:
            embed.add_field(name="TRU Leadership role: ", value="<@&" + str(serverConfig.commandRole) + ">")
        if developer_role:
            embed.add_field(name="TRU Helper Dev role: ", value="<@&" + str(serverConfig.developerRole) + ">")

        await interaction.response.send_message(embed=embed, ephemeral=False)

    @app_commands.command(name="view", description="View the current server configs.")
    async def viewconfig(self, interaction: discord.Interaction):
        db = Prisma()
        await db.connect()
        server_config = await db.server.find_first(where={"serverID": str(interaction.guild.id)})
        await db.disconnect()

        if server_config:
            embed = embedBuilder("Success", embedTitle=f"{interaction.guild.name} || Server Configurations", embedDesc=None)
            embed.add_field(name="Response pings:", value=f"<@&{server_config.announceRole}>")
            embed.add_field(name="Member role:", value=f"<@&{server_config.logPermissionRole}>")
            embed.add_field(name="Response Leaders:", value=f"<@&{server_config.announcePermissionRole}>")
            embed.add_field(name="Response announcement channel:", value=f"<#{server_config.announceChannel}>")
            embed.add_field(name="TRU Leadership role:", value=f"<@&{server_config.commandRole}>")
            embed.add_field(name="TRU Helper Dev role:", value=f"<@&{server_config.developerRole}>")
            await interaction.response.send_message(embed=embed, ephemeral=False)
        else:
            await interaction.response.send_message(content="No server configuration found", ephemeral=True)


class rolebindCmds(commands.GroupCog, group_name="rolebind"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="add", description="Bind a role using ")
    # @app_commands.describe(roles="Roles to bind")
    async def rolebind(self, interaction: discord.Interaction, role: discord.Role,
                       robloxid: int):
        try:
            serverConfig = await dbFuncs.fetch_config(interaction=interaction)
            requiredRole = interaction.guild.get_role(int(serverConfig.commandRole))
            if permFunctions.checkPermission(interaction.user.top_role, requiredRole):
                try:
                    dbresponse = await dbFuncs.createBinding(role, robloxid, interaction)
                    new_bind = await dbFuncs.fetch_rolebind(discordRole=role)
                    if dbresponse == True and new_bind:
                        
                        successEmbed = embedBuilder("Success", embedTitle="<:trubotAccepted:1096225940578766968> Successfully added rolebind!",
                                                    embedDesc=f"**➣ Rank Name: {new_bind.rankName}**\n> +Discord Role: {interaction.guild.get_role(int(new_bind.discordRoleID)).mention}\n> +roblox_client Rank ID: `{new_bind.RobloxRankID}`")
                        await interaction.response.send_message(embed=successEmbed)
                    else:
                        errEmbed = embedBuilder("Error", embedTitle="An error occured:",
                                                embedDesc="Error: " + str(dbresponse))
                        await interaction.response.send_message(embed=errEmbed)
                except Exception as e:
                    errEmbed = embedBuilder("Error", embedTitle="An error occured:",
                                            embedDesc="Error: " + str(e))
                    await interaction.response.send_message(embed=errEmbed, ephemeral=True)
            else:
                errEmbed = embedBuilder("Error", embedTitle="Permission error:",
                                        embedDesc="You are not: <@&" + str(requiredRole.id) + ">")
                await interaction.response.send_message(embed=errEmbed, ephemeral=True)

        except Exception as e:
            errEmbed = embedBuilder("Error", embedDesc=str(e), embedTitle="An error occurred.")
            await interaction.response.send_message(embed=errEmbed, ephemeral=True)

    rolebind._params["role"].required = True
    rolebind._params["robloxid"].required = True

    @app_commands.command(name="remove", description="Remove a role binding.")
    async def role_unbind(self, interaction: discord.Interaction, discord_role: discord.Role):
        try:
            serverConfig = await dbFuncs.fetch_config(interaction=interaction)
            requiredRole = interaction.guild.get_role(int(serverConfig.commandRole))

            if not permFunctions.checkPermission(interaction.user.top_role, requiredRole):
                errEmbed = embedBuilder("Error", embedTitle="Permission error:",
                                        embedDesc="You are not: <@&" + str(requiredRole.id) + ">")
                await interaction.response.send_message(embed=errEmbed, ephemeral=True)
                return

            role = await fetch_rolebind(discordRole = discord_role)
            if not role:
                errEmbed = embedBuilder("Error", embedTitle="<:trubotDenied:1099642433588965447> No rolebind found!",
                                        embedDesc=f"No rolebind was found for {discord_role.mention}.")
                await interaction.response.send_message(embed=errEmbed)
                return

            await dbFuncs.deleteBinding(discord_role)
            successEmbed = embedBuilder("Success", embedTitle="<:trubotAccepted:1096225940578766968> Rolebind successfully removed!",
                                        embedDesc=f"**➣ Rank Name: {role.rankName}**\n> -Discord Role: {interaction.guild.get_role(int(role.discordRoleID)).mention}\n> -roblox_client Rank ID: `{role.RobloxRankID}`")
            await interaction.response.send_message(embed=successEmbed)

        except Exception as e:
            errEmbed = embedBuilder("Error", embedDesc=str(e), embedTitle="An error occurred.")
            await interaction.response.send_message(embed=errEmbed, ephemeral=True)


    @app_commands.command(name="overview", description="View all set binds")
    async def viewbinds(self, interaction: discord.Interaction):
        try:
            roles = await get_all_role_bindings()
            roles.sort(key=lambda r: int(r.RobloxRankID), reverse=True)
            if len(roles) > 0:
                bind_list = discord.Embed(title=f"TRU Helper Rolebinds", color=TRUCommandCOL)
                for role in roles:
                    bind_list.add_field(name=f"➣ Rank Name: {role.rankName}", value=f"> Discord Role: <@&{role.discordRoleID}>\n> roblox_client Rank ID: `{role.RobloxRankID}`", inline=False)
                await interaction.response.send_message(embed=bind_list)
            else:
                await interaction.response.send_message("No role bindings found.")
        except Exception as e:
            errEmbed = embedBuilder("Error", embedDesc=str(e), embedTitle="An error occurred.")
            await interaction.response.send_message(embed=errEmbed, ephemeral=True)