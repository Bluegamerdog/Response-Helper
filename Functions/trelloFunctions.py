
from trello import TrelloClient
from datetime import datetime

TRELLO_API_KEY = "611905fd240d63a804e36a4fe7c9654e"
TOKEN = "ATTA69143a1d63dd6eebe2b03a5715125045652f744b225c8f2fe7fe140e728a08c24D72615E"

trello = TrelloClient(api_key=TRELLO_API_KEY, token=TOKEN)
boardid = "6437e2978421d13cd9394a5d"
response_trello = trello.get_board(boardid)

def get_trello_id(discord_id):
    data = {
        '776226471575683082': '615a267981e91589231eac1c', # Blue
        '530249755264155649': '6363f1ca2bad7b022333d37f', # DrWolf
        '505679486994612246': '630c4e722badc40052a30c37', # Ellusive
        '1096140994556215407': '641e0c7656e96ac475f5ae9a', # TRU Helper
        '367338968661884928': '6379f8a4f73b000156033a2c', # tommie
        '1053377038490292264':'624ee34ad745880bd6047956' # Shush
    }
    return data.get(str(discord_id), None)

trello_day_dict = {
    "Monday": "6437e49e10e8a03fa3dac765",
    "Tuesday": "6437e4a0c604da6927e42570",
    "Wednesday": "6437e4a282479e4e3039c33c",
    "Thursday": "6437e4a686c318850c172c2c",
    "Friday": "6437e4a76bfd790d5bdc6738",
    "Saturday": "6437e4aa35c94b574d3c8c47",
    "Sunday": "64386095c6f440093121fdd1",

}

def create_response_card(type:str, spontaneus:bool, due_date, ringleader_id):
    
    due_date_datetime = datetime.utcfromtimestamp(due_date)
    weekday = due_date_datetime.strftime("%A")
    if weekday in trello_day_dict:
        listID = trello_day_dict[weekday]
    else:
        listID = "6437e2b7f6426e174d655d06"
        
    trellolist = trello.get_list(listID)
        
    due_date_str = due_date_datetime.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    newCard = trellolist.add_card(name=f"{type} Response", due=due_date_str)
    ringleader = trello.get_member(get_trello_id(ringleader_id))
    newCard.add_member(ringleader)
    
    if spontaneus: 
        label_id = "6437e2974720c87ca4fe3e98" # SPON LABEL 6437e2974720c87ca4fe3e98
    else:
        label_id = "6437eb47965e94c2c8cb2eb3" # SCHED LABEL
    
    label = trello.get_label(label_id, boardid)
    newCard.add_label(label)
        
    return newCard.short_url

def set_card_completed(card_url:str):
    card_id = card_url.split('/')[-1]
    trello_card = trello.get_card(card_id)
    trello_card.set_due_complete()

def get_members():
    return response_trello.all_members()

def get_member(id):
    member = trello.get_member(id)
    return member.username, member.full_name

