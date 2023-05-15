import re
from Functions.mainVariables import *
from Functions.permFunctions import *
from discord.ext import commands

# If we have any random function they can go here?

def get_user_id_from_link(link):
    user_id = None
    match = re.search(r'/users/(\d+)', link)
    if match:
        user_id = match.group(1)
    return user_id

def in_roblox_group(members, roblox_user):
    for member in members:
        if member.name == roblox_user.name:
            return True
    return False

def change_nickname(new_rank_name, current_nick):
    rank_abbreviations = {
        "Entrant": "ENT",
        "Operator": "OPR",
        "Senior Operator": "SOPR",
        "Elite Operator": "EOPR",
        "Vanguard":"VGD",
        "Vanguard Officer": "VGO"
    }
    username = current_nick.split()[-1]
    new_nick = f"{rank_abbreviations.get(new_rank_name, 'Unknown')} {username}"
    return new_nick

