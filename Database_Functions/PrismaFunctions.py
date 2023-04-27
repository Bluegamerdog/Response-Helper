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

        await db.operative.create({
            'discordID': str(discordID),
            'userName': name,
            'rank': str(interaction.user.top_role.name),
            'profileLink': profileLink,
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


async def fetch_operative(interaction: discord.Interaction):
    try:
        db = Prisma()
        await db.connect()
        operative = await db.operative.find_unique(where={'discordID': str(interaction.user.id)})
        return operative, True

    except Exception as e:
        return e, False

async def findRole(discordRole: discord.role):
    db = Prisma()
    await db.connect()

    try:


        return

    except Exception as e:
        return e
    
    
## Response Functions ##

async def createResponse(interaction:discord.Interaction, responseType:str, timeStarted:int, started:bool, spontaneous:bool, messageID:str, trellocard_ID:str):
    try:
        
        db = Prisma()
        await db.connect()
        
        await db.response.create(data={
            'responseID' : str(messageID),
            'responseType' : responseType,
            'timeStarted' : str(timeStarted),
            'timeEnded' : "Null",
            'started' : started,
            'cancelled' : False,
            'spontaneous' : spontaneous,
            'trellocardID' : str(trellocard_ID),
            'operativeDiscordID' : str(interaction.user.id),
            'operativeName' : interaction.user.nick
        })
        
        await db.disconnect()
        return True
    except Exception as e:
        print(e)
        return e
    
async def cancelResponse(interaction:discord.Interaction, responseID:str):
    try:    
        db = Prisma()
        await db.connect()
        
        await db.response.update(where={'responseID' : responseID},
                                 data={'cancelled' : True})
        
        await db.disconnect()
        return True
    except Exception as e:
        return e
    
async def concludeResponse(interaction:discord.Interaction, responseID:str):
    try:    
        db = Prisma()
        await db.connect()
        time_Ended = str(time.time())
        await db.response.update(where={'responseID' : str(responseID)},
                                 data={'timeEnded' : time_Ended, 'started' : False})
        
        await db.disconnect()
        return True
    except Exception as e:
        return e
    
async def commenceResponse(interaction:discord.Interaction, responseID:str):
    try:    
        db = Prisma()
        await db.connect()
        time_Ended = int(time.time())
        await db.response.update(where={'responseID' : str(responseID)},
                                 data={'started' : True})
        
        await db.disconnect()
        return True
    except Exception as e:
        return e
    
async def getResponseInfo(interaction:discord.Interaction, responseID:str):
    try:
        db = Prisma()
        await db.connect()
        
        responseData = await db.response.find_first(where={'responseID' : str(responseID)})
        await db.disconnect()
        return responseData
    except Exception as e:
        return e
    
async def getALLplannedResponses(interaction:discord.Interaction):
    try:
        db = Prisma()
        await db.connect()
        
        responses = await db.response.find_many(where={'timeEnded': None, 'cancelled': False})
        
        await db.disconnect()
        return responses
    except Exception as e:
        return e
    
async def getUSERplannedResponses(interaction:discord.Interaction, hostDiscordID:str):
    try:
        db = Prisma()
        await db.connect()
        
        responses = await db.response.find_many(where={'operativeDiscordID': str(hostDiscordID), 'timeEnded': "Null", 'cancelled': False})
        
        await db.disconnect()
        return responses
    except Exception as e:
        return e
    
async def getUSERongoingResponses(interaction:discord.Interaction, hostDiscordID:str):
    try:
        db = Prisma()
        await db.connect()
        
        response = await db.response.find_first(where={'operativeDiscordID': str(hostDiscordID), 'started': True, 'timeEnded': "Null", 'cancelled': False})
        
        await db.disconnect()
        return response
    except Exception as e:
        return e

    
async def deleteResponse(responseID):
    try:
        db = Prisma()
        await db.connect()

        result = await db.response.delete(where={'responseID': str(responseID)})

        await db.disconnect()
        if result == None:
            return False
        return True
    except Exception as e:
        return e

    
async def checkresponseTimes(plannedTime):
    try:
        db = Prisma()
        await db.connect()
        planned_response = await db.response.find_first(where={"timeStarted": str(plannedTime), "timeEnded": "Null", 'cancelled': False})

        if planned_response is not None:
            return planned_response
        return None
    except Exception as e:
        return e

