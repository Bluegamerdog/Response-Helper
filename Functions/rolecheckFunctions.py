
import discord


def checkPermission(userRole: discord.role, targetRole: discord.role):
    #print("User role: " + str(userRole.position))
    #print("Target role: " + str(targetRole.position))
    return userRole.position >= targetRole.position

#This needs to stay though
def DEVACCESS(user: discord.Member):
    roles = user.roles
    for role in roles:
        if role.name in ["TRU Helper Developer", "TRU Helper Dev. Access"] or role.permissions.administrator:
            return True
    return False


def serverAccess(user: discord.Member):  # User a TRU OPR or abvoe?
    roles = user.roles
    for role in roles:
        if role.name in ["Server Access"] or role.permissions.administrator:
            return True
    return False


def TRUMember(user: discord.Member):  # User a TRU member?
    roles = user.roles
    for role in roles:
        if role.name in ["TRU"]:
            return True
    return False


def userOnLoA(user: discord.Member):  # User on LoA?
    roles = user.roles
    for role in roles:
        if role.name in ["TRU Excused"]:
            return True
    return False

def userSuspended(user: discord.Member):  # User suspended?
    roles = user.roles
    for role in roles:
        if role.name in ["Suspended"]:
            return True
    return False



