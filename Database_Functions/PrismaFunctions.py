from prisma import Prisma
from discord.utils import get
import discord
import asyncio
import urllib3
import uuid
import time
import random
from Functions.randFunctions import getHighestRole
import math

"""
Prisma Template 

async def prismaFunc():
    db = Prisma()
    await db.connect()

    await db.disconnect()


"""

## Quota Blocks

# Function to get all quota block data
async def get_all_quota_data():
    db = Prisma()
    await db.connect()
    quotadata = await db.quota_blocks.find_many()
    await db.disconnect()
    return quotadata

# Function to get quota block data by block number
async def get_quotablock(block_num=None):
    db = Prisma()
    await db.connect()
    if block_num is not None:
        quotaBlock =  await db.quota_blocks.find_unique(where={"blockNum": block_num})
    else:
        quotaBlock = await db.quota_blocks.find_first(where={"blockActive": True})
    await db.disconnect()
    return quotaBlock

# Function to set the active quota block by block number
async def set_active_block(block_num):
    db = Prisma()
    await db.connect()
    await db.quota_blocks.update_many(
        where={"blockActive": True},
        data={"blockActive": False}
    )
    await db.quota_blocks.update(
        where={"blockNum": block_num},
        data={"blockActive": True}
    )
    await db.disconnect()
    return

# Function to insert quota block data
async def insert_quota_data(block_num, unix_starttime, unix_endtime, block_active):
    return await Prisma().quota_blocks.create({
        "blockNum": block_num,
        "unix_starttime": unix_starttime,
        "unix_endtime": unix_endtime,
        "blockActive": block_active
    })








 

async def registerOperator(discordUser:discord.Member, profileLink: str, name: str):
    try:
        db = Prisma()
        await db.connect()

        highest_role = await getHighestRole(discordUser)
        
        operative = await db.operative.create({
            'discordID': str(discordUser.id),
            'userName': name,
            'rank': str(highest_role),
            'profileLink': profileLink,
            'activeLog': False,
            'activeLogID': f"NULL{random.randint(1000, 9999)}"

        })
        if operative is not None:
            await db.disconnect()
            return operative
        else:
            await db.disconnect()
            return False
    except Exception as e:
        return str(e)
        
async def updateOperator(discordUser: discord.Member, profileLink: str, name: str):
    try:
        db = Prisma()
        await db.connect()

        highest_role = await getHighestRole(discordUser)

        operative = await db.operative.find_unique(where={'discordID' :str(discordUser.id)})
        if operative:
            updated_operative = await db.operative.update(
                where={"discordID": str(discordUser.id)},
                data={
                    "userName": name,
                    "rank": str(highest_role),
                    "profileLink": profileLink,
                },
            )
            await db.disconnect()
            return updated_operative
        else:
            await db.disconnect()
            return operative
    except Exception as e:
        return str(e)

async def updateOperator_rank(discordUser: discord.Member, new_rank:str):
    try:
        db = Prisma()
        await db.connect()
        updated_operative = await db.operative.update(where={'discordID': str(discordUser.id)}, data={'rank': str(new_rank)})
        await db.disconnect()
        return updated_operative
    except Exception as e:
        return str(e)

async def removeOperator(operativeID: int):
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

async def getOperator(operativeID:int):
    try:
        db = Prisma()
        await db.connect()
        operative = await db.operative.find_unique(where={'discordID': str(operativeID)})
        await db.disconnect()
        return operative   
    except Exception as e:
        return str(e)

## LOGS

async def checkLog(interaction: discord.Interaction):
    db = Prisma()
    await db.connect()
    operative = await db.operative.find_unique(where={'discordID': str(interaction.user.id)})
    log = await db.logs.find_unique(where={'logID': str(operative.activeLogID)})
    logID = operative.activeLogID
    if operative.activeLog == False:
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
        if operative.activeLog == False:
            return "No log is currently started!", False
        print("Found a valid logID")
        await db.logs.delete(where={'logID': logID})
        await db.operative.update(where={'discordID': str(interaction.user.id)},
                                  data={
                                      'activeLog': False,
                                      'activeLogID': f"NULL{random.randint(1000, 9999)}",
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
        if operative.activeLog == False:
            return "No log is currently started!", False
        elapsed = round(((int(unixTime) - int(log.timeStarted))/60), 2)
        if elapsed > 5:
            await db.operative.update(where={'discordID': str(interaction.user.id)},
                                      data={
                                          'activeLog': False,
                                          'activeLogID': f"NULL{random.randint(1000, 9999)}",
                                      })
            await db.logs.update(where={'logID': str(logID)},
                                      data={
                                          'timeEnded': unixTime,
                                          'timeElapsed': str(elapsed),
                                      })
            return str(elapsed), True
        else:
            timeRemaining = int(log.timeStarted) + 300 #1500 = 25 minutes
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

async def getallLogs(member:discord.Member):
    db = Prisma()
    await db.connect()
    logdata = await db.logs.find_many(where={"operativeDiscordID": f"{member.id}"})
    await db.disconnect()
    return logdata
    

## ROLEBINDS

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


# SERVERCONFIG

async def fetch_config(interaction: discord.Interaction):
    db = Prisma()
    try:
        await db.connect()
        serverObj = await db.server.find_unique(where={'serverID': str(interaction.guild_id)})
        await db.disconnect()
        return serverObj
        

    except Exception as e:
        return e

  
# ---

async def clear_table(table_name):
    db = Prisma()
    await db.connect()
    try:
        # Delete all records in the specified table
        await db.execute_raw(f'DELETE FROM "{table_name}";')
        await db.disconnect()
        return True
    except Exception as e:
        return e

