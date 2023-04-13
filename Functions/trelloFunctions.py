from trello import TrelloClient
from trello.card import Card
import datetime

TRELLO_API_KEY = "7728134341a69e810f630856c7871231"
TOKEN = "ATTAe37a6d6d54f7fde47ce9465d473b6f8d29e71628dd72833714767652b2f29e19CE4EA758"

trello = TrelloClient(api_key=TRELLO_API_KEY, token=TOKEN)
opsched = trello.get_board("631e1f2aee06a600708e6a2b")

def unix_to_datetime(unix_time):
    return datetime.datetime.fromtimestamp(int(unix_time))

async def create_op_card(operation:str, ringleader:str, length:str, purpstat:str, spontaneus:bool, co_host:str=None, supervisor:str=None):
    
    listID = "631e1f3edd797f00a8b58102" 
    tempID = "oCs1pSm1"

    if co_host==None:
        co_host = "TBD"
    if supervisor == None:
        carddesc=f"- **Ringleader**: {ringleader}\n- **Co-host(s)**: {co_host}\n- **Supervisor**: {supervisor}\n- **Length**: {length}\n- **Purpose**: {purpstat}."
    else:
        carddesc=f"- **Ringleader**: {ringleader}\n- **Co-host(s)**: {co_host}\n- **Length**: {length}\n- **Purpose**: {purpstat}."
    
    template = trello.get_card(tempID)
    #print(template)
    newCard = Card(f"{operation}", listID, source=template)
    
    if spontaneus:
        label_id = "631e2ef29a42d20209a3a45a"
        spon_label = trello.get_label(label_id)
        newCard.add_label(spon_label)
    
    return newCard.short_url
