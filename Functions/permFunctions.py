from Database_Functions.MaindbFunctions import *
import discord


def checkPermission(userRole: discord.role, targetRole: discord.role):
    #print("User role: " + str(userRole.position))
    #print("Target role: " + str(targetRole.position))
    return userRole.position >= targetRole.position


# Consolidate into a single function rather than do this every time :steamangry:
def TRULEAD(user):  # TRU Captain and above
    roles = user.roles
    for role in roles:
        if role.name in ["TRU Captain", "TRU Commander", "QSO P.C.", "Field Captain", "Field Commander",
                         "Director of Defense"] or role.permissions.administrator:
            return True
    return False


def TRURL(user):  # Elite Vanguard and above
    roles = user.roles
    for role in roles:
        if role.name in ["Elite Vanguard", "TRU Captain", "TRU Commander", "QSO P.C.", "Field Captain",
                         "Field Commander", "Director of Defense"] or role.permissions.administrator:
            return True
    return False


def TRUECO(user):  # Vanguard and above
    roles = user.roles
    for role in roles:
        if role.name in ["Vanguard", "Elite Vanguard", "TRU Captain", "TRU Commander", "QSO P.C.", "Field Captain",
                         "Field Commander", "Director of Defense"] or role.permissions.administrator:
            return True
    return False


def TRUMEMBER(user):  # Operator and above
    roles = user.roles
    for role in roles:
        if role.name in ["Server Access"] or role.permissions.administrator:
            return True
    return False


def TRUROLE(user):  # Entrant and above
    roles = user.roles
    for role in roles:
        if role.name in ["TRU"]:
            return True
    return False


def onLoA(user):  # On Leave of Absence
    roles = user.roles
    for role in roles:
        if role.name in ["TRU Excused"]:
            return True
    return False


def DEVACCESS(user: discord.Member):
    roles = user.roles
    for role in roles:
        if role.name in ["TRU Helper Developer"]:
            return True
    return False
