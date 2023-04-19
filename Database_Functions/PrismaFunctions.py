from prisma import Prisma
from discord.utils import get
import discord
import asyncio
import urllib3




"""
Prisma Template 

async def prismaFunc():
    db = Prisma()
    await db.connect()

    await db.disconnect()


"""

async def registerUser(discordID: int, profileLink: str, name: str):
    try:
        db = Prisma()
        await db.connect()

        User = await db.operative.create({
            'discordID': discordID,
            'profileLink': profileLink,
            'userName': name,
            'rank': "Placeholder"
        })

        await db.disconnect()
        return User
    except Exception as e:
        return e 


async def removeUser(discordID: int, interaction: discord.Interaction):
    
    try:
        db = Prisma()
        await db.connect()
        object = await db.operative.delete(where={'discordID': discordID})
        return object
    
    except Exception as e:
        return e
    
async def createBinding(discordRole: discord.Role, robloxID: int,interaction: discord.Interaction):
    db = Prisma()
    await db.connect()

    try: 
        #Sanity check to make sure the role exists
        role = interaction.guild.get_role(discordRole.id)
        await db.ranks.create({
            'discordRoleID': discordRole.id,
            'RobloxRankID': robloxID,
            'rankName': discordRole.name
        })

    except Exception as e:
        return e

    
    

