import re
from Functions.mainVariables import *
from Functions.rolecheckFunctions import *
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


async def getHighestRole(discordUser: discord.Member):
    roles = discordUser.roles
    roles.sort(reverse=True, key=lambda r: r.position)  # Sort roles in descending order of position

    for role in roles:
        if role.name != "TRU Excused":
            return role.name

    return ""  # Return an empty string if no valid role is found

def get_promotion_message(rank_name):
    unlocks = {
        "Operator": "Congratulations on your promotion to Operator (OPR)! As an Operator, you perform the most basic TRU duties in the field. You have shown progress and gained valuable experience. Enjoy free use of the Desert Eagle, a symbol of your proficiency. Your journey as an operator has just begun, and there is much to learn and accomplish. Continue to grow and develop your skills.",
        "Senior Operator": "Congratulations on your promotion to Senior Operator (SOPR)! As a Senior Operator, your experience and skills make you an invaluable asset to TRU. You are granted free use of the TRU Tactical Uniform and G-18s, which enhance your effectiveness in the field. Your continued dedication and expertise will contribute to the success of TRU operations.",
        "Elite Operator": "Congratulations on your promotion to Elite Operator (EOPR)! As an Elite Operator, you are a veteran with exceptional combat capabilities. Your authority within the operator class is significant, and your contributions are vital to TRU. You are granted free use of the Vector-45 and have the option for an M60 loadout [1:1 QSO to Raider ratio, or as a counter for RPD], along with a Riot Shield [1:1.5 QSO to Raider ratio]. Lead by example and continue to excel in your role.",
        "Vanguard":"Congratulations on your promotion to Vanguard (VGD)! As a Vanguard, you are entrusted with specific tasks assigned by the Response Leader. Demonstrate your leadership potential and actively showcase your skills to become a future Response Leader yourself. Embrace the challenge and continue to exhibit your expertise on the field. Enjoy free use of the M60, a truly formidable weapon if used right.",
        "Vanguard Officer": "Congratulations on your promotion to Vanguard Officer (VGO)! As a VGO, you have proven your exceptional skills as an operator and now take on the role of a leader. Your new responsibilities include leading TRU into conflict, making informed tactical decisions, and mentoring those below you. You are also granted free use of a Riot Shield [1:1 QSO to Raider ratio] and have the option for a HK416 and RPG loadout [1:1.5 QSO:Raider ratio or to counter RPG/MIN-134], along with the Juggernaut Suit. Lead with valor and inspire others to excel."
    }
    message = f"{unlocks.get(rank_name, 'Unknown')}"
    return message

def is_valid_profile_link(profilelink: str) -> bool:
    # Regular expression pattern for matching Roblox profile links
    pattern = r"^https?://www\.roblox\.com/users/\d+/profile$"
    return bool(re.match(pattern, profilelink))

