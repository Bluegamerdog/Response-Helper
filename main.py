import asyncio
import datetime
import json
import platform
import random
import re
import string
import sys
import time
import discord
import time
from colorama import Back, Fore, Style
from discord import app_commands
from discord.ext import commands


from Functions.mainVariables import *
from Functions.rolecheckFunctions import *
from Commands.bot_cmds import botCmds, serverconfigCmds, rolebindCmds
from Commands.command_testing import testingCmds, oldpatrolCmds
from Commands.misc_cmds import otherCmds
from Commands.quota_cmds import (
    patrolCmds,
    viewdataCommand,
    quotaCmds,
    quotablockCommands,
)
from Commands.operator_cmds import operatorCmds
from Commands.response_cmds import responseCmds
from Functions.formattingFunctions import *
from Functions.trelloFunctions import *

# from Commands.strike_cmds import strikecmds


bot = commands.Bot(command_prefix=">", intents=discord.Intents().all())
tree = app_commands.CommandTree(discord.Client(intents=discord.Intents().all()))
start_time = datetime.now()


async def accept_loa(interaction: discord.Interaction, message: discord.Message):
    # Check if the context menu is used in the designated LoA channel
    loa_channel_id = 1121081165697265684  # bot-testing
    if message.channel.id != loa_channel_id:
        return await interaction.response.send_message(
            embed=embedBuilder(
                "err",
                "This context menu can only be used in the designated LoA channel.",
                "Incorrect channel!",
            ),
            ephemeral=True,
        )

    _emoji = "<:Accepted:1095834084636364900>"
    for reaction in message.reactions:
        if str(reaction.emoji) == _emoji:
            return await interaction.response.send_message(
                embed=embedBuilder(
                    "err", "This LoA has already been accepted.", "While processing..."
                ),
                ephemeral=True,
            )
    await interaction.response.defer(thinking=True, ephemeral=True)
    member = interaction.guild.get_member(message.author.id)
    card = get_card_by_name_managmanetBoard(member.display_name.split()[-1])
    if card:
        add_loa_label(card.id)
    if member:
        loa_role_id = 1096194282840395857  # Replace with the ID of the LoA role
        loa_role = interaction.guild.get_role(loa_role_id)
        if loa_role:
            await member.add_roles(loa_role)
            await message.add_reaction(_emoji)

            await interaction.edit_original_response(
                embed=embedBuilder(
                    "succ",
                    f"{member.mention}'s LoA has been accepted and their trello card has been updated.",
                )
            )
            return await message.reply(f"LoA accepted by {interaction.user.mention}.")
        else:
            await interaction.edit_original_response(
                embed=embedBuilder(
                    "err", f"Could not find the designated LoA role (`{loa_role_id}`)"
                )
            )


async def end_loa(interaction: discord.Interaction, message: discord.Message):
    # Check if the context menu is used in the designated LoA channel
    loa_channel_id = 1121081165697265684  # bot-testing
    if message.channel.id != loa_channel_id:
        return await interaction.response.send_message(
            embed=embedBuilder(
                "err",
                "This context menu can only be used in the designated LoA channel.",
                "Incorrect channel!",
            ),
            ephemeral=True,
        )
    _emoji = "<:ExpiredOver:1102161253515931768>"  # Replace with the ID of the accepted emoji
    for reaction in message.reactions:
        if str(reaction.emoji) == _emoji:
            return await interaction.response.send_message(
                embed=embedBuilder(
                    "err", "This LoA has already been expired.", "While processing..."
                ),
                ephemeral=True,
            )
    await interaction.response.defer(thinking=True, ephemeral=True)
    member = interaction.guild.get_member(message.author.id)
    card = get_card_by_name_managmanetBoard(member.display_name.split()[-1])
    if card:
        remove_loa_label(card.id)
        add_loa_to_card(card.id, message.content)
    if member:
        loa_role_id = 1096194282840395857  # Replace with the ID of the LoA role
        loa_role = interaction.guild.get_role(loa_role_id)
        if loa_role:
            await member.remove_roles(loa_role)
            await message.add_reaction(_emoji)
            await interaction.edit_original_response(
                embed=embedBuilder(
                    "succ",
                    embedDesc=f"{member.mention} has been removed from the LoA role. Please make sure their LoA has been properly archived. [Card Link]({card.shortUrl})."
                    if card
                    else f"{member.mention} has been removed from the LoA role. Please make sure their LoA has been properly archived.",
                )
            )
            return await message.reply(f"LoA expired.")
        else:
            await interaction.edit_original_response(
                embed=embedBuilder(
                    "err", f"Could not find the designated LoA role (`{loa_role_id}`)"
                )
            )


loaaccept_context_menu = app_commands.ContextMenu(
    name="Accept LoA",
    callback=accept_loa,
)

loaend_context_menu = app_commands.ContextMenu(
    name="Expire LoA",
    callback=end_loa,
)


bot.tree.add_command(loaaccept_context_menu)
bot.tree.add_command(loaend_context_menu)


@bot.event
async def on_ready():
    print("Loading imports...")

    # bot_cmds.py
    await bot.add_cog(botCmds(bot))
    await bot.add_cog(serverconfigCmds(bot))
    await bot.add_cog(rolebindCmds(bot))

    # misc_cmds.py
    await bot.add_cog(otherCmds(bot, start_time))

    # quota_cmds.py
    await bot.add_cog(patrolCmds(bot))
    await bot.add_cog(quotaCmds(bot))
    await bot.add_cog(viewdataCommand(bot))
    await bot.add_cog(quotablockCommands(bot))

    # operator_cmds.py
    await bot.add_cog(operatorCmds(bot))

    # TBA_response_cmds.py
    await bot.add_cog(responseCmds(bot))

    # command_testing.py
    await bot.add_cog(testingCmds(bot))
    # await bot.add_cog(oldpatrolCmds(bot))

    # strike_cmds.py
    # await bot.add_cog(strikeCmds(bot))

    # Console output
    prfx = (Back.BLACK + Fore.BLUE) + Back.RESET + Fore.WHITE + Style.BRIGHT
    print(
        prfx
        + "|| Logged in as "
        + Fore.BLUE
        + bot.user.name
        + "  at  "
        + time.strftime("%H:%M:%S UTC", time.gmtime())
    )
    print(prfx + "|| Bot ID: " + Fore.BLUE + str(bot.user.id))
    print(prfx + "|| Discord Version: " + Fore.BLUE + discord.__version__)
    print(prfx + "|| Python Version: " + Fore.BLUE + str(platform.python_version()))
    print(prfx + "Syncing commands...")
    try:
        synced = await bot.tree.sync()
        print(
            "\033[2K"
            + prfx
            + f"|| Slash CMDs Synced: {Fore.BLUE}{len(synced)} Commands"
        )
    except Exception as e:
        print(f"Error syncing commands: {e}")
        synced = []
    # Quota and notes output
    print(prfx + f"|| That is all for now. (Remove quota blocks for now)")

    # Embed message
    embed = discord.Embed(title="Bot Startup Info • InDev", color=discord.Color.green())
    embed.add_field(name="Bot Name", value=bot.user.name, inline=True)
    embed.add_field(name="Bot ID", value=bot.user.id, inline=True)
    embed.add_field(
        name="Runtime Information",
        value=f"Discord Version: {discord.__version__} || Python Version: {platform.python_version()}",
        inline=False,
    )
    embed.add_field(name="Synced Slash Commands", value=len(synced), inline=False)
    embed.add_field(
        name="Notes",
        value="That is all for now. (Remove quota blocks for now).",
        inline=False,
    )

    channel = bot.get_channel(1096146385830690866)  # Startup-channel ID
    await channel.send(embed=embed)


with open("token.json", "r") as f:
    data = json.load(f)
    TOKEN = data["TOKEN"]


bot.run(TOKEN)
