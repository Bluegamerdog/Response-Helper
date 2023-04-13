from Database_Functions.MaindbFunctions import *
import discord

def DSBCOMM_A(user): # function to check if user is DSBPCOMM+
    roles = user.roles
    for role in roles:
        if role.name in ["QSO Pre-Command", "QSO Command", "DSB Command"] or role.permissions.administrator:
            return True
    return False

def DSBPC_A(user): # function to check if user is DSBPC+ 
    roles = user.roles
    for role in roles:
        if role.name in ["DSB Pre-Command", "QSO Pre-Command", "QSO Command", "DSB Command"] or role.permissions.administrator:
            return True
    return False

def FMR_A(user): # function to check if user is MR+
    roles = user.roles
    for role in roles:
        if role.name in ["Elite Defense Specialist", "Master Sergeant", "[DSB] Squadron Officer", "DSB Pre-Command", "QSO Pre-Command", "QSO Command", "DSB Command"] or role.permissions.administrator:
            return True
    return False

def ITMR_A(user): # MR in-training and above
    roles = user.roles
    for role in roles:
        if role.name in ["DSB MR", "DSB Pre-Command", "QSO Pre-Command", "QSO Command", "DSB Command"] or role.permissions.administrator:
            return True
    return False

def DSBMEMBER(user): # PFC+
    roles = user.roles
    for role in roles:
        if role.name in ["DSB"] and role.name not in ["DSB Private"] or role.permissions.administrator:
            return True
    return False

def DSBROLE(user): # PRV+
    roles = user.roles
    for role in roles:
        if role.name in ["DSB"]:
            return True
    return False

def onLoA(user): # On LoA?
    roles = user.roles
    for role in roles:
        if role.name in ["DSB Leave of Absence"]:
            return True
    return False

def DEVACCESS(user: discord.Member):
    if user.guild_permissions.administrator:
        return True
    else:
        conn, cur = get_conn()
        cur.execute(f"SELECT user_ids FROM devaccess WHERE user_ids LIKE '%{user.id}%'")
        result = cur.fetchone()
        if result:
            return True
    return False
