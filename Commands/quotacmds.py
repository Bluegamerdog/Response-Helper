import asyncio
import discord
from prisma import Prisma
from discord.ext import commands
from discord import app_commands
from Database_Functions.MaindbFunctions import *
from Functions.mainVariables import *
from Functions.permFunctions import *
from Functions.randFunctions import (get_point_quota, quota_prog_display)
from Database_Functions.UserdbFunction import (get_users_amount, add_points, remove_points, get_points, db_register_get_data, reset_points)
from Database_Functions.MaindbFunctions import (get_quota)
from Functions.formattingFunctions import embedBuilder
import Database_Functions.PrismaFunctions as dbFuncs
import Database_Functions.PrismaFunctions as DBFunc
from Functions import permFunctions

# Embed types: Success, Warning, Error

### REWORK ###


class overviewButtons(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.gray)
    async def PreviousButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        page, last_user_count = get_leaderboard_page(interaction.message.id)
        if page == 1:
            button.disabled = True
            return await interaction.response.defer()
        rows = get_users_amount(page-1)
        if(last_user_count <= page * 10):
            last_user_count -= 10 + (last_user_count-1) % 10
        else:
            last_user_count -= 20
        embed = interaction.message.embeds[0]
        embed.clear_fields()
        for row in rows:
            if(row[1] != None and int(row[3]) >= 1): # added check for points >= 1
                user = self.bot.get_user(int(row[1]))
                if user:
                    member = self.bot.get_guild(SupportServerID).get_member(user.id)
                    if member:
                        nickname = member.nick or user.name
                    else:
                        nickname = user.name
                else:
                    nickname = "User not found"
                user = str(last_user_count) + ". || " + str(nickname)
                embed.add_field(name = "", value = f"**{user}**\nPoints: " + '{:,}'.format(int(row[3])), inline=False)
                last_user_count += 1
        update_leaderboard(page - 1, last_user_count, interaction.message.id)
        page_u, last_user_count_u = get_leaderboard_page(interaction.message.id)
        embed.set_footer(text=f"Page {page_u}")
        await interaction.message.edit(embed=embed, view=overviewButtons())
        await interaction.response.defer()

    @discord.ui.button(emoji="<:dsbbotRefresh:1071533380581208146>", style=discord.ButtonStyle.gray)
    async def RefreshButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        page, last_user_count = get_leaderboard_page(interaction.message.id)
        rows = get_users_amount(page)
        last_user_count = (page - 1) * 10 + 1
        has_points = False
        embed = interaction.message.embeds[0]
        blockdata = get_quota()
        if blockdata:
            embed.title = f"Point Overview - Block {blockdata[0]}"
            embed.description = f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nQuota block {blockdata[0]} ends <t:{blockdata[2]}:R>. \n<t:{blockdata[1]}> - <t:{blockdata[2]}>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        else:
            embed.title = f"Point Overview  -  Block not set!"
            embed.description = f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nQuota block has not yet been set, please ping a member of DBSPC or above.\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        embed.clear_fields()
        for row in rows:
            if(row[1] != None and int(row[3]) >= 1):
                has_points = True
                user = self.bot.get_user(int(row[1]))
                if user:
                    member = self.bot.get_guild(SupportServerID).get_member(user.id)
                    if member:
                        nickname = member.nick or user.name
                    else:
                        nickname = user.name
                else:
                    nickname = "User not found"
                user = str(last_user_count) + ". || " + str(nickname)
                embed.add_field(name = "", value = f"**{user}**\nPoints: " + '{:,}'.format(int(row[3])), inline=False)
                last_user_count += 1
        if not has_points:
            embed.add_field(name="", value="", inline=False)
            embed.add_field(name="", value="*No point data found, it seems no one currently has any points.*", inline=False)
        update_leaderboard(page, last_user_count, interaction.message.id)
        page_u, last_user_count_u = get_leaderboard_page(interaction.message.id)
        embed.set_footer(text=f"Page {page_u}")
        await interaction.message.edit(embed=embed, view=overviewButtons(self.bot))
        await interaction.response.defer()

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.gray)
    async def NextButton(self, interaction:discord.Interaction, button:discord.ui.Button):        
        page, last_user_count = get_leaderboard_page(interaction.message.id)
        if(last_user_count-1 < page * 10):
            button.disabled = True
            return await interaction.response.defer()
        rows = get_users_amount(page+1)
        embed = interaction.message.embeds[0]
        embed.clear_fields()
        for row in rows:
            if(row[1] != None and int(row[3]) >= 1): # added check for points 
                user = self.bot.get_user(int(row[1]))
                if user:
                    member = self.bot.get_guild(SupportServerID).get_member(user.id)
                    if member:
                        nickname = member.nick or user.name
                    else:
                        nickname = user.name
                else:
                    nickname = "User not found"
                user = str(last_user_count) + ". || " + str(nickname)
                embed.add_field(name = "", value = f"**{user}**\nPoints: " + '{:,}'.format(int(row[3])), inline=False)
                last_user_count += 1     
        update_leaderboard(page + 1, last_user_count, interaction.message.id)
        page_u, last_user_count_u = get_leaderboard_page(interaction.message.id)
        embed.set_footer(text=f"Page {page_u}")
        await interaction.message.edit(embed=embed, view=overviewButtons())
        await interaction.response.defer()
        
    @discord.ui.button(label="||", style=discord.ButtonStyle.gray, disabled=True)
    async def EmptyButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        pass

    @discord.ui.button(emoji="ℹ️", style=discord.ButtonStyle.gray)
    async def InfoButton(self, interaction:discord.Interaction, button:discord.ui.Button):
        embed = interaction.message.embeds[0]
        embed.clear_fields()
        embed.remove_footer()
        blockdata = get_quota()
        if blockdata:
            embed.title = f"Point Overview - Block {blockdata[0]}"
            embed.description = f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nQuota block {blockdata[0]} ends <t:{blockdata[2]}:R>. \n<t:{blockdata[1]}> - <t:{blockdata[2]}>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        else:
            embed.title = f"Point Overview  -  Block not set!"
            embed.description = f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nQuota block has not yet been set, please ping a member of DBSPC or above.\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        data = db_register_get_data(interaction.user.id)
        if data:
            if not data[4]:
                quota, rank = get_point_quota(interaction.user)
            else:
                quota, rank = get_point_quota(interaction.user)
                if quota is not None:
                    quota = int(quota - ((quota/14)*data[4]))

        completion_percentage = "Testing"#get_quota_completion_percentage(self.bot)
        qm = quota_prog_display(completion_percentage, False)
        embed.add_field(name=f"Total quota completion:", value=f"{qm} {completion_percentage:.1f}% || 3/3")
        await interaction.message.edit(embed=embed, view=overviewButtons(self.bot))
        await interaction.response.defer()

   

class pointCmds(commands.GroupCog, group_name='points'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    

    @app_commands.command(name="add", description="Adds points to a user. [TRUPC+]")
    async def add(self, interaction:discord.Interaction, member:discord.Member, amount:int):
        user = interaction.user
        if(not TRULEAD(user)): # check if user has permission
            embed = discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Failed to add points to user!", description=f"You must be a member of TRUPC or above to add points.")
            await interaction.response.send_message(embed=embed)
            return
        if(type(amount)==int and int(amount) >= 1):
            if add_points(member.id, amount) == True: # add points to the user
                    embed = discord.Embed(color=TRUCommandCOL, title=f"<:dsbbotSuccess:953641647802056756> Successfully added {amount} point to **{member.display_name}**!" if amount == 1 else f"<:dsbbotSuccess:953641647802056756> Successfully added {amount} points to **{member.display_name}**!", description=f"**{member.display_name}** now has **{get_points(member.id)}** point." if int(get_points(member.id)) == 1 else f"**{member.display_name}** now has **{get_points(member.id)}** points." )
            else:
                embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Failed to add points to `{member}`!", description="User not found in registry database.", color=ErrorCOL)
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Failed to add points to **{member.display_name}**!", description="Invalid point number.", color=ErrorCOL)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="remove", description="Removes points from a user. [TRUPC+]")
    async def remove(self, interaction:discord.Interaction, member:discord.Member, amount:int):
        if not TRULEAD(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Failed to remove points from user!", description=f"You must be a member of TRUPC or above to remove points."))
        if(type(amount)==int and int(amount)>=1):
            if remove_points(member.id, amount) == True: #removes points from user
                embed = discord.Embed(color=TRUCommandCOL, title=f"<:dsbbotSuccess:953641647802056756> Successfully removed {amount} point from **{member.display_name}**!" if amount == 1 else f"<:dsbbotSuccess:953641647802056756> Successfully removed {amount} points from {member.display_name}!", description=f"**{member.display_name}** now has **{get_points(member.id)}** point." if int(get_points(member.id)) == 1 else f"**{member.display_name}** now has **{get_points(member.id)}** points." )
            else:
                embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Failed to remove points from `{member}`!", description="User not found in registry database.", color=ErrorCOL)
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Failed to remove points from **{member.display_name}**!", description="Invalid point number.", color=ErrorCOL)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
    @app_commands.command(name="view",description="View someone else's current point count.")
    async def view(self, interaction: discord.Interaction, user:discord.Member=None):
        if not TRUMEMBER(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Missing permissions!", description=f"Only TRU Private First Class or above may interact with TRU Helper."), ephemeral=True)
        else:
            embed = discord.Embed(color=TRUCommandCOL, title=f"<:dsbbotSuccess:953641647802056756> Point data found for {user.display_name}!" if user and user != interaction.user else f"<:dsbbotSuccess:953641647802056756> Point data found!")
            if user == None:
                user = interaction.user
            points = get_points(user.id)
            if points is False:
                return await interaction.response.send_message(embed = discord.Embed(title=f"<:dsbbotFailed:953641818057216050> No point data found for `{user}`!", description="User not found in registry database.", color=ErrorCOL))
            username = str(user.display_name)
            embed = discord.Embed(color=TRUCommandCOL, title=f"<:dsbbotSuccess:953641647802056756> Point data for {username}!")
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

    @app_commands.command(name="reset",description="Resets the points of all users to zero. [TRUPC+]")
    async def reset(self, interaction:discord.Interaction):
        if not TRULEAD(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(title=f"<:dsbbotFailed:953641818057216050> Failed to reset points!", description="You must be a member of TRUCOMM or above to purge the registry database.", color=ErrorCOL))
        else:
            await interaction.response.send_message(embed=discord.Embed(description="<:dsbbotUnderReview:1067970676041982053> Waiting for response..."))
            embed = discord.Embed(color=HRCommandsCOL, description=f"<:dsbbotUnderReview:1067970676041982053> **Are you sure you want to reset the points?**\nReact with <:dsbbotApproved:953642750039953418> to confirm.", colour=ErrorCOL)
            msg = await interaction.edit_original_response(embed=embed)
            await msg.add_reaction("<:dsbbotApproved:953642750039953418>")
            
            
            # Wait for the user's reaction
            def check(reaction, user):
                return user == interaction.user and str(reaction.emoji) == '<:dsbbotApproved:953642750039953418>'
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
                        embed = discord.Embed(title="<:dsbbotSuccess:953641647802056756> Point reset successful!", color=discord.Color.green())
                        await interaction.edit_original_response(embed=embed)
                    else:
                        embed = discord.Embed(title="<:dsbbotFailed:953641818057216050> Point reset failed!", description=f"Something went wrong...", color=ErrorCOL)
                        tasks = [    msg.clear_reactions(),    interaction.edit_original_response(embed=embed)]
                        await asyncio.gather(*tasks)

    @app_commands.command(name="overview",description="Shows leaderboard for points.")
    async def overview(self, interaction: discord.Interaction):
        if not TRUMEMBER(interaction.user):
            return await interaction.response.send_message(embed=discord.Embed(color=ErrorCOL, title="<:dsbbotFailed:953641818057216050> Missing permissions!", description=f"Only TRU Private First Class or above may interact with TRU Helper."), ephemeral=True)
        else:
            gettingembed = discord.Embed(description="Getting data...")
            await interaction.response.send_message(embed=gettingembed)
            rows = get_users_amount(1)
            blockdata = get_quota()
            if blockdata:
                embed = discord.Embed(title =f"Point Overview  -  Block {blockdata[0]}", description=f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nQuota block {blockdata[0]} ends <t:{blockdata[2]}:R>. \n<t:{blockdata[1]}> - <t:{blockdata[2]}>\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", color=TRUCommandCOL)
            else:
                embed = discord.Embed(title =f"Point Overview  -  Block not set!", description=f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nQuota block has not yet been set, please ping a member of DBSPC or above.\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", color=TRUCommandCOL)
            count = 1
            has_points = False
            embed.set_footer(text=f"Page 1")
            for row in rows:
                if(row[1] != None and int(row[3]) >= 1):
                    has_points = True
                    user = self.bot.get_user(int(row[1]))
                    if user:
                        member = self.bot.get_guild(SupportServerID).get_member(user.id)
                        if member:
                            nickname = member.nick or user.name
                        else:
                            nickname = user.name
                    else:
                        nickname = "User not found"
                    user = str(count) + ". || " + str(nickname)
                    embed.add_field(name = "", value = f"**{user}**\nPoints: " + '{:,}'.format(int(row[3])), inline=False)
                    count += 1
            if not has_points:
                embed.add_field(name="", value="", inline=False)
                embed.add_field(name="", value="*No point data found, it seems no one currently has any points.*", inline=False)
                embed.remove_footer()
            
            msg_sent = await interaction.edit_original_response(embed=embed, view = overviewButtons(self.bot))
            add_leaderboard(interaction.user.id, msg_sent.id, count)

## WORKS ##
class mypointsCmd(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.client = bot

    @app_commands.command(name="mydata",description="View your current quota status.")
    async def mypoints(self, interaction: discord.Interaction):
        try:
            db = Prisma()
            await db.connect()
            data = await db.operative.find_unique(where={"discordID": f"{interaction.user.id}"})
            log_amount = await db.logs.find_many(where={"operativeDiscordID": f"{interaction.user.id}"})
            await db.disconnect()
            if data == None:
                return await interaction.response.send_message(embed=embedBuilder("Error", embedDesc=f"Unable to find userdata on {interaction.user.mention}. Make sure you are registered.", embedTitle="No data found!"))
            else:
                embed = embedBuilder("Success", embedTitle=f"<:dsbbotSuccess:953641647802056756> User data found!", embedDesc=f"Displaying {interaction.user.mention}'s data for block `TBA`.")
                embed.add_field(name="TRU Rank", value=f"> {data.rank}", inline=True)
                embed.add_field(name="Activity Status", value=f"> On Leave of Absence" if onLoA(interaction.user) else f"> Activty Duty", inline=True)
                embed.add_field(name="", value="", inline=False)
                embed.add_field(name="Responses Attended", value=f"> `TBA`", inline=True) # Need to add response attendance count
                embed.add_field(name="Patrols Logged", value=f"> {len(log_amount)}/Quota", inline=True) #(need to add something and be able to change quota at will)
                await interaction.response.send_message(embed=embed)
        except Exception as e:
            errEmbed = embedBuilder("Error", embedDesc=str(e), embedTitle="An error occurred.")
            await interaction.response.send_message(embed=errEmbed, ephemeral=True)
                



