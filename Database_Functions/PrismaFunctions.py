from prisma import Prisma
from discord.utils import get
import discord
import asyncio
import urllib3
import uuid

"""
Prisma Template 

async def prismaFunc():
    db = Prisma()
    await db.connect()

    await db.disconnect()


"""


async def registerUser(discordID: int, profileLink: str, name: str, rankName: str):
    try:
        db = Prisma()
        await db.connect()

        User = await db.operative.create({
            'discordID': str(discordID),
            'profileLink': profileLink,
            'userName': name,
            'rank': rankName,
            'activeLog': False
        })

        await db.disconnect()
        return User
    except Exception as e:
        return e


"""
await prisma.logs.create({
                data: {
                    logID: id.toString(),
                    timeStarted: logStart.toString(),
                    timeEnded: "NULL",
                    timeElapsed: "NULL",
                    operativeName: splitUser(nickname)
                }
            })
await prisma.operative.update({
    where: {
        discordID: interaction.user.id
    },
    data: {
        logs: {
            connect: {
                logID: id.toString()
            }
        },
        activeLog: true
    }
})
"""
async def fetchOperative(interaction: discord.Interaction):
    try:
        db = Prisma()
        await db.connect()
        operative = await db.operative.find_unique(where={'discordID': str(interaction.user.id)})
        if operative:
            return operative, True
        else:
            return "no operator registration matching you was found. Please make sure you are registered.", False
    except Exception as e:
        return e, False
async def prismaCreatelog(interaction: discord.Interaction, unixTime: str, ):
    try:
        log_id = str(uuid.uuid4())[:8]
        db = Prisma()
        await db.connect()
        log = await db.logs.create({
            'logID': log_id,
            'timeStarted': unixTime,
            'timeEnded': "Null",
            'timeElapsed': "Null",
        })
        await db.operative.update(where={
            'discordID': str(interaction.user.id)
        }, data={
            'activeLog': True,
            'logs': {
                'connect': {
                    'logID': log_id
                }
            }
        })
        return "Success", True
    except Exception as e:
        return e, False

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
