import re
from Database_Functions.MaindbFunctions import *
from Functions.mainVariables import *
from Functions.permFunctions import (TRULEAD, onLoA)
from discord.ext import commands






def get_point_quota(user, data=None):
    role_quota = {
        "Private First Class": (16, "Private First Class"),
        "Corporal": (16, "**Corporal**"),
        "Sergeant": (20, "**Sergeant**"),
        "Junior Staff Sergeant": (26, "**Junior Staff Sergeant**"),
        "Staff Sergeant": (32, "**Staff Sergeant**"),
        "Sergeant Major": (36, "**Sergeant Major**"),
        "Chief Sergeant": (36, "**Chief Sergeant**"),
        "Colonel": (None, "**Colonel**"),
        "Lieutenant": (None, "**Lieutenant**"),
        "TRU Captain": (None, "**TRU Captain**"),
        "TRU Commander": (None, "**TRU Commander**"),
        "Major": (None, "**Major** *[QSO Pre-Command]*"),
        "QSO Pre-Command": (None, "**QSO Pre-Command**"),
        "QSO Command": (None, "**QSO Command**")
    }
    
    for role in user.roles:
        if role.name in role_quota:
            quota, rank = role_quota[role.name]
            if data and data[4] and TRULEAD(user)==False:
                quota = int(quota - ((quota/14)*data[4]))
            return quota, rank
    
    return None, None   

def attendance_points(user):
    roles_ = {
        "Private First Class": 4,
        "Corporal": 4,
        "Sergeant": 4,
        "Junior Staff Sergeant": 2,
        "Staff Sergeant": 2,
        "Sergeant Major": 2,
        "Chief Sergeant": 2,
    }
    
    for role in user.roles:
        if role.name in roles_:
            return roles_[role.name]
    
    return None

def co_host_points(user):
    roles_ = {
        "Junior Staff Sergeant": 5,
        "Staff Sergeant": 4,
        "Sergeant Major": 6,
        "Chief Sergeant": 6,
        "TRU Pre-Command": 1,
        "TRU Command": 1,
    }
    
    for role in user.roles:
        if role.name in roles_:
            return roles_[role.name]
    
    return None

def supervisor_points(user):
    roles_ = {
        "Sergeant Major": 5,
        "Chief Sergeant": 6,
        "TRU Pre-Command": 1,
        "TRU Command": 1,
    }
    
    for role in user.roles:
        if role.name in roles_:
            return roles_[role.name]
    
    return None

def ringleader_points(user):
    roles_ = {
        "Junior Staff Sergeant": 7,
        "Staff Sergeant": 8,
        "Sergeant Major": 8,
        "Chief Sergeant": 7,
        "TRU Pre-Command": 1,
        "TRU Command": 1,
    }
    
    for role in user.roles:
        if role.name in roles_:
            return roles_[role.name]
    
    return None


def quota_prog_display(percent, LOA:bool):
    if percent > 200:
        qm = "🌟🌟🌟🌟🌟🌟🌟🌟🌟🌟"
    elif percent >= 200:
        qm = "⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐"
    elif percent >= 190:
        qm = "⭐⭐⭐⭐⭐⭐⭐⭐⭐🟦"
    elif percent >= 180:
        qm = "⭐⭐⭐⭐⭐⭐⭐⭐🟦🟦"
    elif percent >= 170:
        qm = "⭐⭐⭐⭐⭐⭐⭐🟦🟦🟦"
    elif percent >= 160:
        qm = "⭐⭐⭐⭐⭐⭐🟦🟦🟦🟦"
    elif percent >= 150:
        qm = "⭐⭐⭐⭐⭐🟦🟦🟦🟦🟦"
    elif percent >= 140:
        qm = "⭐⭐⭐⭐🟦🟦🟦🟦🟦🟦"
    elif percent >= 130:
        qm = "⭐⭐⭐🟦🟦🟦🟦🟦🟦🟦"
    elif percent >= 120:
        qm = "⭐⭐🟦🟦🟦🟦🟦🟦🟦🟦"
    elif percent >= 110:
        qm = "⭐🟦🟦🟦🟦🟦🟦🟦🟦🟦"
    elif percent >= 100:
        qm = "🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦"
    elif percent >= 90:
        qm = "🟦🟦🟦🟦🟦🟦🟦🟦🟦⬛"
    elif percent >= 80:
        qm = "🟦🟦🟦🟦🟦🟦🟦🟦⬛⬛"
    elif percent >= 70:
        qm = "🟦🟦🟦🟦🟦🟦🟦⬛⬛⬛"
    elif percent >= 60:
        qm = "🟦🟦🟦🟦🟦🟦⬛⬛⬛⬛"
    elif percent >= 50:
        qm = "🟦🟦🟦🟦🟦⬛⬛⬛⬛⬛"
    elif percent >= 40:
        qm = "🟦🟦🟦🟦⬛⬛⬛⬛⬛⬛"
    elif percent >= 30:
        qm = "🟦🟦🟦⬛⬛⬛⬛⬛⬛⬛"
    elif percent >= 20:
        qm = "🟦🟦⬛⬛⬛⬛⬛⬛⬛⬛"
    elif percent >= 10:
        qm = "🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛"
    else:
        qm = "⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛"
        
    if LOA == True:
        qm = ":regional_indicator_l::regional_indicator_o::regional_indicator_a:" + qm[3:]
        return qm
    else:
        return qm

def getrank(user):
    roles_ = {
        "TRU Private": ("TRU Private", 1),
        "Private First Class": ("Private First Class", 4),
        "Corporal": ("Corporal", 6),
        "Sergeant": ("Sergeant", 16),
        "Junior Staff Sergeant": ("Junior Staff Sergeant", 18),
        "Staff Sergeant": ("Staff Sergeant", 18),
        "Sergeant Major": ("Sergeant Major", 20),
        "Chief Sergeant": ("Chief Sergeant", 25),
        "Major":("Major [QSO Pre-Command]", 252),
        "Colonel":("Colonel", 252),
        "Lieutenant":("Lieutenant", 252),
        "TRU Captain": ("TRU Captain", 253),
        "TRU Commander": ("TRU Commander", 253),
        }
    
    for role in user.roles:
        if role.name in roles_:
            return roles_[role.name]
    return None

def changerank(rank):
    ranks_ = {
        "Pvt": ("TRU Private", 1),
        "PFC": ("Private First Class", 4),
        "Crp": ("Corporal", 6),
        "Sgt": ("Sergeant", 10),
        "J.SSgt": ("Junior Staff Sergeant", 18),
        "SSgt": ("Staff Sergeant", 18),
        "SMaj": ("Sergeant Major", 20),
        "CSgt": ("Chief Sergeant", 25),
        "Major":("Major [QSO Pre-Command]", 252),
        "Colonel":("Colonel", 252),
        "Lieutenant":("Lieutenant", 252),
        "TRU Captain": ("TRU Captain", 253),
        "TRU Commander": ("TRU Commander", 253),}
    
    return ranks_.get(rank, None)

def change_nickname(rank_name, prev_nickname):
    rank_abbreviations = {
        "TRU Private": "Pvt",
        "Private First Class": "PFC",
        "Corporal": "Crp",
        "Sergeant": "Sgt",
        "Junior Staff Sergeant":"J.SSgt",
        "Staff Sergeant": "SSgt",
        "Sergeant Major": "SMaj",
        "Chief Sergeant": "CSgt",
        "Major":"TRUMAJ/",
        "Colonel":"Col",
        "Lieutenant": "Ltn",
        "TRU Captain": "Capt",
        "TRU Commander": "Cmdr",
    }
    username = prev_nickname.split()[-1]
    new_nick = f"TRU {rank_abbreviations.get(rank_name, 'Unknown')} {username}"
    return new_nick


def get_user_id_from_link(link):
    user_id = None
    match = re.search(r'/users/(\d+)', link)
    if match:
        user_id = match.group(1)
    return user_id