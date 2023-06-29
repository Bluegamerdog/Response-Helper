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
from Functions import rolecheckFunctions
from Functions.formattingFunctions import embedBuilder
from Functions.mainVariables import *
from Functions.rolecheckFunctions import *


class botCmds(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    #MAYBE EDIT MESSAGE AFTER RELOAD
    @app_commands.command(name="reload",description="Restarts the TRU Helper. [TRUPC+]")
    async def restart(self, interaction:discord.Interaction, commands:str=None):
        if not DEVACCESS(interaction.user):
            return await interaction.response.send_message(embed = embedBuilder(responseType="perms", embedDesc="This command is limited to Bot Developers."))
        if commands != None:
            await interaction.response.send_message(embed = embedBuilder(responseType="cust", embedColor=YellowCOL, embedTitle="<:trubotWarning:1099642918974783519> Syncing Commands..."))
            try:
                await self.bot.tree.fetch_commands()
                synced = await self.bot.tree.sync()
                return await interaction.edit_original_response(embed = embedBuilder(responseType="succ",embedTitle=f"Synced {len(synced)} commands!"))
            except Exception as e:
                print(f"Error syncing commands: {e}")
                return await interaction.edit_original_response(embed = embedBuilder(responseType="err", title=f"Syncing failed!", description=f"**Error:** {e}"))
        else:
            await interaction.response.send_message(embed = embedBuilder(responseType="warn",  embedTitle="Restarting..."))
            print(f"=========\nBot restarted by {interaction.user}\n=========")
            os.execv(sys.executable, ['python'] + sys.argv)
    
    @app_commands.command(name="shutdown", description="Shuts down TRU Helper. [DEVACCESS]")
    async def shutdown(self, interaction:discord.Interaction):
        if not DEVACCESS(interaction.user):
            return await interaction.response.send_message(embed = embedBuilder(responseType="perms", embedDesc="This command is limited to Bot Developers."))
        else:
            embed = embedBuilder(responseType="cust", embedColor=ErrorCOL, embedTitle="<:trubotWarning:1099642918974783519> Shutting down...")
            await interaction.response.send_message(embed=embed)
            print(f"=========\nBot closed by {interaction.user}\n=========")
            return await self.bot.close()
        
    @app_commands.command(name="clear", description="Able to clear any specified database table. [BotDev Only]")
    @app_commands.choices(table=[
        app_commands.Choice(name="operators", value="operative"),
        app_commands.Choice(name="responses", value="response"),
        app_commands.Choice(name="rolebinds", value="ranks"),
        app_commands.Choice(name="logs", value="logs"),
        app_commands.Choice(name="serverconfigs", value="server"),
        ])
    async def edit_db(self, interaction:discord.Interaction, table:app_commands.Choice[str]):
        if not DEVACCESS(interaction.user):
            return await interaction.response.send_message(embed = embedBuilder(responseType="perms", embedDesc="This command is limited to Bot Developers.", color=ErrorCOL))
        try:
            await interaction.response.send_message(embed = embedBuilder(responseType="cust", embedDesc="<:trubotBeingLookedInto:1099642414303559720> Looking for table..."))
            msg = await interaction.edit_original_response(embed = embedBuilder(responseType="warn", embedDesc=f"<:trubotBeingLookedInto:1099642414303559720> **Are you sure you want to clear `{table.name}`?**\nReact with <:trubotApproved:1099642447526637670> to confirm."))
            await msg.add_reaction("<:trubotApproved:1099642447526637670>")
            
            def check(reaction, user):
                return user == interaction.user and str(reaction.emoji) == '<:trubotApproved:1099642447526637670>'
            try:
                reaction, user_r = await self.bot.wait_for('reaction_add', check=check, timeout=10)
            except asyncio.TimeoutError:
                embed = embedBuilder(responseType="err", embedDesc=f"Timed out waiting for reaction.")
                tasks = [    msg.clear_reactions(),    interaction.edit_original_response(embed=embed)]
                await asyncio.gather(*tasks)

            else:
                if DEVACCESS(user_r):
                    results = await clear_table(table.value)
                    print(f"The table '{table.value}' has been cleared by {interaction.user}!")
                    if results == True:
                        return await interaction.edit_original_response(embed = embedBuilder(responseType="succ", embedTitle=f"`{table.name}` was cleared!"))
                    else:
                        return await interaction.edit_original_response(embed= embedBuilder(responseType="err", embedTitle=f"Unable to clear `{table.name}`", embedDesc=f"{results}"))
        except Exception as e:
            return await interaction.edit_original_response(embed=embedBuilder(responseType="err", embedDesc=f"{e}"))


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

            embed = embedBuilder(responseType="succ",
                                 embedDesc="A configuration with the following details was made: ")
            embed.add_field(name="Response pings: ", value="<@&" + str(ping_role.id) + ">")
            embed.add_field(name="Member role: ", value="<@&" + str(logrole.id) + ">")
            embed.add_field(name="Response Leaders: ", value="<@&" + str(schedule_role.id) + ">")
            embed.add_field(name="Response announcements channel: ", value="<#" + str(announce_channel.id) + ">")
            embed.add_field(name="TRU Leadership role: ", value="<@&" + str(command_role.id) + ">")
            embed.add_field(name="TRU Helper Dev role: ", value="<@&" + str(developer_role.id) + ">")
            await interaction.response.send_message(embed=embed, ephemeral=False)
        else:
            errEmbed = embedBuilder(responseType="perms",
                                    embedDesc="This command is limited to Bot Developers.")
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
        embed = embedBuilder(responseType="succ", embedTitle="Updated server configs!",
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
            embed = embedBuilder("cust", embedTitle=f"{interaction.guild.name} || Server Configurations", embedColor=TRUCommandCOL)
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
            if rolecheckFunctions.checkPermission(interaction.user.top_role, requiredRole):
                try:
                    dbresponse = await dbFuncs.createBinding(role, robloxid, interaction)
                    new_bind = await dbFuncs.fetch_rolebind(discordRole=role)
                    if dbresponse == True and new_bind:
                        
                        successEmbed = embedBuilder("succ", embedTitle="Added rolebind!",
                                                    embedDesc=f"**➣ Rank Name: {new_bind.rankName}**\n> +Discord Role: {interaction.guild.get_role(int(new_bind.discordRoleID)).mention}\n> +roblox_client Rank ID: `{new_bind.RobloxRankID}`")
                        await interaction.response.send_message(embed=successEmbed)
                    else:
                        errEmbed = embedBuilder("err",
                                                embedDesc="Error: " + str(dbresponse))
                        await interaction.response.send_message(embed=errEmbed)
                except Exception as e:
                    errEmbed = embedBuilder("err",
                                            embedDesc="Error: " + str(e))
                    await interaction.response.send_message(embed=errEmbed, ephemeral=True)
            else:
                errEmbed = embedBuilder("perms",
                                        embedDesc="This command is limited to Bot Developers.")
                await interaction.response.send_message(embed=errEmbed, ephemeral=True)

        except Exception as e:
            errEmbed = embedBuilder("err", embedDesc=str(e), embedTitle="An error occurred.")
            await interaction.response.send_message(embed=errEmbed, ephemeral=True)

    rolebind._params["role"].required = True
    rolebind._params["robloxid"].required = True

    @app_commands.command(name="remove", description="Remove a role binding.")
    async def role_unbind(self, interaction: discord.Interaction, discord_role: discord.Role):
        try:
            serverConfig = await dbFuncs.fetch_config(interaction=interaction)
            requiredRole = interaction.guild.get_role(int(serverConfig.commandRole))

            if not rolecheckFunctions.checkPermission(interaction.user.top_role, requiredRole):
                errEmbed = embedBuilder("perms",
                                        embedDesc="This command is limited to Bot Developers.")
                await interaction.response.send_message(embed=errEmbed, ephemeral=True)
                return

            role = await fetch_rolebind(discordRole = discord_role)
            if not role:
                errEmbed = embedBuilder("err", embedTitle="No rolebind found!",
                                        embedDesc=f"No rolebind was found for {discord_role.mention}.")
                await interaction.response.send_message(embed=errEmbed)
                return

            await dbFuncs.deleteBinding(discord_role)
            successEmbed = embedBuilder("succ", embedTitle="Rolebind removed!",
                                        embedDesc=f"**➣ Rank Name: {role.rankName}**\n> -Discord Role: {interaction.guild.get_role(int(role.discordRoleID)).mention}\n> -roblox_client Rank ID: `{role.RobloxRankID}`")
            await interaction.response.send_message(embed=successEmbed)

        except Exception as e:
            errEmbed = embedBuilder("err", embedDesc=str(e))
            await interaction.response.send_message(embed=errEmbed, ephemeral=True)


    @app_commands.command(name="overview", description="View all set binds")
    async def viewbinds(self, interaction: discord.Interaction):
        try:
            roles = await get_all_role_bindings()
            roles.sort(key=lambda r: int(r.RobloxRankID), reverse=True)
            if len(roles) > 0:
                bind_list = embedBuilder(responseType="cust", embedTitle=f"TRU Helper Rolebinds", embedColor=TRUCommandCOL)
                for role in roles:
                    bind_list.add_field(name=f"➣ Rank Name: {role.rankName}", value=f"> Discord Role: <@&{role.discordRoleID}>\n> roblox_client Rank ID: `{role.RobloxRankID}`", inline=False)
                await interaction.response.send_message(embed=bind_list)
            else:
                await interaction.response.send_message("No role bindings found.")
        except Exception as e:
            errEmbed = embedBuilder("err", embedDesc=str(e))
            await interaction.response.send_message(embed=errEmbed, ephemeral=True)