from prisma import Prisma
from discord.utils import get
import discord
import asyncio
import urllib3
import uuid
import time
import random

"""
Prisma Template 

async def prismaFunc():
    db = Prisma()
    await db.connect()

    await db.disconnect()


"""

# Need to start moving these into their own files (pls)

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
 

async def registerUser(discordUser:discord.Member, profileLink: str, name: str):
    try:
        db = Prisma()
        await db.connect()

        operative = await db.operative.create({
            'discordID': str(discordUser.id),
            'userName': name,
            'rank': str(discordUser.top_role.name),
            'profileLink': profileLink,
            'activeLog': False,

        })
        if operative is not None:
            await db.disconnect()
            return operative
        else:
            await db.disconnect()
            return False
    except Exception as e:
        return str(e)
    
    
async def updateOperative(discordUser: discord.Member, profileLink: str = None, name: str = None): # Help :sob:
    try:
        db = Prisma()
        await db.connect()

        operative = await db.operative.find_unique(where={'discordID': str(discordUser.id)})
        if operative is not None:
            update_data = {}
            if profileLink:
                update_data['profileLink'] = profileLink
            if name:
                update_data['userName'] = name
            updated_operative = await db.operative.update(where={'discordID': str(discordUser.id)}, data=update_data)
            await db.disconnect()
            return True
        else:
            await db.disconnect()
            return f"No operative found with Discord ID: {discordUser.id}"
    except Exception as e:
        return str(e)

async def updateOperative_rank(discordUser: discord.Member, new_rank:str):
    try:
        db = Prisma()
        await db.connect()
        updated_operative = await db.operative.update(where={'discordID': str(discordUser.id)}, data={'rank': str(new_rank)})
        await db.disconnect()
        return updated_operative
    except Exception as e:
        return str(e)

async def removeOperative(operativeID: int):
    try:
        db = Prisma()
        await db.connect()

        operative = await db.operative.find_unique(where={'discordID': str(operativeID)})

        if operative:
            await db.operative.delete(where={'discordID': str(operativeID)})
            await db.disconnect()
            return True
        else:
            await db.disconnect()
            return f"Operative with ID `{operativeID}` not found!"
    except Exception as e:
        await db.disconnect()
        return str(e)


async def viewOperative(operativeID:int):
    try:
        db = Prisma()
        await db.connect()
        operative = await db.operative.find_unique(where={'discordID': str(operativeID)})
        await db.disconnect()
        return operative   
    except Exception as e:
        return str(e)



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
async def checkLog(interaction: discord.Interaction):
    db = Prisma()
    await db.connect()
    operative = await db.operative.find_unique(where={'discordID': str(interaction.user.id)})
    log = await db.logs.find_unique(where={'logID': str(operative.activeLogID)})
    logID = operative.activeLogID
    if logID == "NULL":
        return "No log is currently started!", False
    else:
        return log, True
async def prismaCancelLog(interaction: discord.Interaction):
    try:
        db = Prisma()
        await db.connect()
        operative = await db.operative.find_unique(where={'discordID': str(interaction.user.id)})
        log = await db.logs.find_unique(where={'logID': str(operative.activeLogID)})
        logID = operative.activeLogID
        if logID == "NULL":
            return "No log is currently started!", False
        print("Found a valid logID")
        await db.logs.delete(where={'logID': logID})
        await db.operative.update(where={'discordID': str(interaction.user.id)},
                                  data={
                                      'activeLog': False,
                                      'activeLogID': "NULL",
                                  })

        return log, True
    except Exception as e:
        return e, False


async def prismaEndLog(interaction: discord.Interaction, unixTime: str):
    try:
        db = Prisma()
        await db.connect()
        operative = await db.operative.find_unique(where={'discordID': str(interaction.user.id)})
        log = await db.logs.find_unique(where={'logID': str(operative.activeLogID)})
        logID = operative.activeLogID
        if logID == "NULL":
            return "No log is currently started!", False
        elapsed = round(((int(unixTime) - int(log.timeStarted))/60), 2)
        if elapsed > 25:
            await db.operative.update(where={'discordID': str(interaction.user.id)},
                                      data={
                                          'activeLog': False,
                                          'activeLogID': "NULL",
                                      })
            await db.logs.update(where={'logID': str(logID)},
                                      data={
                                          'timeEnded': unixTime,
                                          'timeElapsed': str(elapsed),
                                      })
            return str(elapsed), True
        else:
            timeRemaining = int(log.timeStarted) + 1500
            return str("Log is eligible to end in **<t:" + str(timeRemaining) + ":R>**"), False
    except Exception as e:
        return str(e), False


async def prismaCreatelog(interaction: discord.Interaction, unixTime: str):
    try:
        log_id = str(uuid.uuid4())[:8]
        db = Prisma()
        await db.connect()
        operative = await db.operative.find_unique(where={'discordID': str(interaction.user.id)})
        log = await db.logs.create({
            'logID': log_id,
            'timeStarted': unixTime,
            'timeEnded': "Null",
            'timeElapsed': "Null",
            'operativeName': operative.userName
        })
        await db.operative.update(where={
            'discordID': str(interaction.user.id)
        }, data={
            'activeLog': True,
            'activeLogID': log_id,
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


async def createBinding(discordRole:discord.Role, robloxID:int, interaction: discord.Interaction):
    db = Prisma()
    await db.connect()
    
    try:

        await db.ranks.upsert(where={
            'discordRoleID': str(discordRole.id)}, data={
            'create': {
                'discordRoleID': str(discordRole.id),
                'RobloxRankID': str(robloxID),
                'rankName': discordRole.name}, 
            'update': {
                'RobloxRankID': str(robloxID),
                'rankName': discordRole.name}})

        await db.disconnect()
        return True

    except Exception as e:
        return e
    
async def fetch_rolebind(robloxID:int = None, discordRole:discord.Role = None, rankName:str=None):
    db = Prisma()
    try:
        await db.connect()
        if robloxID is not None:
            role = await db.ranks.find_unique(where={'RobloxRankID': str(robloxID)})
        elif discordRole is not None:
            role = await db.ranks.find_unique(where={'discordRoleID': str(discordRole.id)})
        elif rankName is not None:
            role = await db.ranks.find_unique(where={'rankName': str(rankName)})
        else:
            role = None
        await db.disconnect()
        return role
    except Exception as e:
        return e


async def deleteBinding(discordRole:discord.Role):
    db = Prisma()
    await db.connect()

    try:
        await db.ranks.delete(where={
            'discordRoleID': str(discordRole.id)})

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
    try:
        await db.connect()
        serverObj = await db.server.find_unique(where={'serverID': str(interaction.guild_id)})
        await db.disconnect()
        return serverObj
        

    except Exception as e:
        return e


async def fetch_operative(interaction: discord.Interaction):
    try:
        db = Prisma()
        await db.connect()
        operative = await db.operative.find_unique(where={'discordID': str(interaction.user.id)})
        if operative is not None:
            return operative, True
        else:
            return "No operative found!", False

    except Exception as e:
        return e, False

async def findRole(discordRole: discord.role):
    db = Prisma()
    await db.connect()

    try:


        return

    except Exception as e:
        return e
    
    


