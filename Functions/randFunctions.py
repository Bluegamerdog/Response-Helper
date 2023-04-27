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