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


async def createBinding(discordRole: discord.role, robloxID: int, interaction: discord.Interaction):
    db = Prisma()
    await db.connect()

    try:

        await db.ranks.upsert(where={
            'discordRoleID': str(discordRole.id)
        }, data={
            'create': {
                'discordRoleID': str(discordRole.id),
                'RobloxRankID': str(robloxID),
                'rankName': discordRole.name
            }, 'update': {
                'RobloxRankID': str(robloxID),
                'rankName': discordRole.name
            }

        })

        await db.disconnect()
        return True

    except Exception as e:
        return e


async def fetch_config(interaction: discord.Interaction):
    db = Prisma()
    await db.connect()
    try:
        serverObj = await db.server.find_unique(where={'serverID': str(interaction.guild_id)})
        return serverObj

    except Exception as e:
        return e


async def findRole(discordRole: discord.role):
    db = Prisma()
    await db.connect()

    try:
        return

    except Exception as e:
        return e
