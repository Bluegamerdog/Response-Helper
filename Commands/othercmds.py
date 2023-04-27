import discord
import asyncio
import random
from discord.ext import commands
from discord import app_commands

from Functions.mainVariables import *
from Functions.permFunctions import *
from Functions.randFunctions import *

### COMPLETED ####

class otherCmds(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @app_commands.command(name="whois",description="Displays a user's information.")
    async def whois(self, interaction: discord.Interaction, user:discord.Member=None):
            roles = []
            if user is None:
                user = interaction.user
            for role in user.roles:
                if role.name == '@everyone':
                    continue
                roles.append(str(role.mention))
            roles.reverse()
            ct = user.created_at.strftime("%a, %d %b, %Y | %H:%M")
            jt = user.joined_at.strftime("%a, %d %b %Y | %H:%M")
            if user:
                embed=discord.Embed(description=f"{user.mention}  •  ID: {user.id}",color=BasiccommandCOL)
            embed.set_author(icon_url=user.avatar, name=f"{user}'s User Info")
            embed.set_thumbnail(url=user.avatar)
            #embed.set_footer(text=f'ID: {user.id}')
            embed.add_field(name="Joined Server On:", value=jt,inline=True)
            embed.add_field(name="Created Account On:", value=ct,inline=True)
            if len(str(" | ".join([x.mention for x in user.roles]))) > 1024:
                embed.add_field(name=f"Roles[{len(user.roles)}]:", value="Too many to display.", inline=False)
            else:
                role_count = len([role for role in user.roles if role.name != '@everyone'])
                embed.add_field(name=f"Roles[{role_count}]:", value=" | ".join(roles),inline=False)   
            #embed.add_field(name="Bot:", value=f'{("Yes" if user.bot==True else "No")}',inline=False)
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ping",description="Shows the bot's response time.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"🏓Pong! Took `{round(self.bot.latency * 1000)}`ms")

    @app_commands.command(name="coinflip", description="Flips a coin and returns heads or tails.")
    async def coinflip(self, interaction: discord.Interaction):
        result = random.choice(['Heads', 'Tails'])
        return await interaction.response.send_message(f"The coin landed on **{result}**!")
    
    @app_commands.command(name="8ball", description="Ask the magischen 8-ball a Frage.")
    @app_commands.describe(question="What do you want to ask the magischen 8-ball?")
    async def eight_ball(self, interaction: discord.Interaction, question:str):
        responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes - definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "Outlook not so good.",
            "My sources say no.",
            "Very doubtful.",
            "My reply is no."
        ]
        response = random.choice(responses)
        await interaction.response.send_message(f"> {question}",embed=discord.Embed(description=f":8ball: {response}"))

    @app_commands.command(name="watch", description=":lo:") #<a:dsbbotlo:1093874594231898233>
    async def watching(self, interaction: discord.Interaction, user:discord.Member=None):
        if not watching_command:
            return await interaction.response.send_message("This command is currently disabled. <a:dsbbotlo:1093874594231898233>", ephemeral=True)
        elif user == None:
            members = self.bot.guilds[0].members
            random_member = random.choice(members)
            activity = discord.Activity(type=discord.ActivityType.watching, name=f"{random_member.display_name}")
            await self.bot.change_presence(activity=activity)
            await interaction.response.send_message(f"Status updated: `Watching`**`{random_member.display_name}`** <a:dsbbotlo:1093874594231898233>", ephemeral=True)
        else:
            activity = discord.Activity(type=discord.ActivityType.watching, name=f"{user.display_name}")
            await self.bot.change_presence(activity=activity)
            await interaction.response.send_message(f"Status updated: `Watching`**`{user.display_name}`** <a:dsbbotlo:1093874594231898233>", ephemeral=True)


