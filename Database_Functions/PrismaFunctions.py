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


async def updateUser(interaction: discord.Interaction, discordID: int, profileLink: str, name: str):
    try:
        db = Prisma()
        await db.connect()

        User = await db.operative.update(where={'discordID': str(interaction.user.id)},
                                         data={
            'discordID': str(discordID),
            'profileLink': profileLink,
            'userName': name,
            'rank': str(interaction.user.top_role.name),
            'activeLog': False
        })

        await db.disconnect()
        return True
    except Exception as e:
        return e


async def registerUser(interaction: discord.Interaction, discordID: int, profileLink: str, name: str):
    try:
        db = Prisma()
        await db.connect()

        User = await db.operative.create({
            'discordID': str(discordID),
            'profileLink': profileLink,
            'userName': name,
            'rank': str(interaction.user.top_role.name),
            'activeLog': False
        })

        await db.disconnect()
        return True
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


async def prismaCreatelog(interaction: discord.Interaction, unixTime: str, ):
    try:
        db = Prisma()
        await db.connect()
        log = await db.logs.create({
            'timeStarted': unixTime,
            'timeEnded': "Null",
            'timeElapsed': "Null",
        })
        await db.operative.update(where={
            'discordID': str(interaction.user.id)
        }, data={
            'logs': {
                'connect': {
                    'logID': str(log.logID)
                }
            },
            'activeLog': True
        })

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

async def get_all_role_bindings():
    db = Prisma()
    await db.connect()
    roles = await db.ranks.find_many()
    await db.disconnect()
    return roles


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
