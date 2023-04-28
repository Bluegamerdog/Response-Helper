import time
from prisma import Prisma
import discord

# Mostly done but I def missed something :skull:

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
        time_Ended = int(time.time())
        await db.response.update(where={'responseID' : str(responseID)},
                                 data={'timeEnded' : str(time_Ended), 'started' : False})
        
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
    
async def getUSERResponses(hostDiscordID:str):
    try:
        db = Prisma()
        await db.connect()
        
        user_responses = await db.response.find_many(where={'operativeDiscordID': str(hostDiscordID)})
        
        await db.disconnect()
        return user_responses
    except Exception as e:
        return e
    
async def getAllResponses():
    try:
        db = Prisma()
        await db.connect()
        
        responses = await db.response.find_many()
        
        await db.disconnect()
        return responses
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