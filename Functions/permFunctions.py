from Database_Functions.MaindbFunctions import *
import discord

def TRULEAD(user): # TRU Captain and above
    roles = user.roles
    for role in roles:
        if role.name in ["TRU Captain", "TRU Commander", "QSO P.C.", "Field Captain", "Field Commander", "Director of Defense"] or role.permissions.administrator:
            return True
    return False

def TRURL(user): # Elite Vanguard and above
    roles = user.roles
    for role in roles:
        if role.name in ["Elite Vanguard","TRU Captain", "TRU Commander", "QSO P.C.", "Field Captain", "Field Commander", "Director of Defense"] or role.permissions.administrator:
            return True
    return False

def TRUECO(user): # Vanguard and above
    roles = user.roles
    for role in roles:
        if role.name in ["Vanguard", "Elite Vanguard", "TRU Captain", "TRU Commander", "QSO P.C.", "Field Captain", "Field Commander", "Director of Defense"] or role.permissions.administrator:
            return True
    return False

def TRUMEMBER(user): # Operator and above
    roles = user.roles
    for role in roles:
        if role.name in ["Server Access"] or role.permissions.administrator:
            return True
    return False

def TRUROLE(user): # Entrant and above
    roles = user.roles
    for role in roles:
        if role.name in ["TRU"]:
            return True
    return False

def onLoA(user): # On Leave of Absence
    roles = user.roles
    for role in roles:
        if role.name in ["TRU Excused"]:
            return True
    return False

def DEVACCESS(user: discord.Member):
    if user.guild_permissions.administrator or str(user.id) == "776226471575683082":
        return True
    else:
        conn, cur = userget_conn()
        cur.execute(f"SELECT user_ids FROM devaccess WHERE user_ids LIKE '%{user.id}%'")
        result = cur.fetchone()
        if result:
            return True
    return False
