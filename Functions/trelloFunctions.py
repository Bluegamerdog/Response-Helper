from trello import TrelloClient
from datetime import datetime

TRELLO_API_KEY = "611905fd240d63a804e36a4fe7c9654e"
TOKEN = "ATTA69143a1d63dd6eebe2b03a5715125045652f744b225c8f2fe7fe140e728a08c24D72615E"

trello = TrelloClient(api_key=TRELLO_API_KEY, token=TOKEN)
responseBoardID = "6437e2978421d13cd9394a5d"
memberactivityBoardID = "643c638f797233341d30294f"
membermanagmanetBoardID = "643707e584f45acbd7dd7c94"

response_trello = trello.get_board(responseBoardID)
memberactivityBoard = trello.get_board(memberactivityBoardID)
membermanagmanetBoard = trello.get_board(membermanagmanetBoardID)


def get_trello_id(discord_id):
    data = {
        "776226471575683082": "615a267981e91589231eac1c",  # Blue
        "505679486994612246": "630c4e722badc40052a30c37",  # Ellusive
        "367338968661884928": "6379f8a4f73b000156033a2c",  # tommie
        "1096140994556215407": "641e0c7656e96ac475f5ae9a",  # TRU Helper
        "201525891271098368": "6242339da8b6bf73b65173b0",  # Seal
        "530249755264155649": "6363f1ca2bad7b022333d37f",  # DrWolf
        "313005277857185803": "5cb00cf689005359f8417948",  # Coco
        "1053377038490292264": "624ee34ad745880bd6047956",  # Shush
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


def create_response_card(type: str, spontaneus: bool, due_date, ringleader_id):
    due_date_datetime = datetime.utcfromtimestamp(due_date)
    weekday = due_date_datetime.strftime("%A")
    if weekday in trello_day_dict:
        listID = trello_day_dict[weekday]
    else:
        listID = "6437e2b7f6426e174d655d06"

    trellolist = trello.get_list(listID)
    host = get_trello_id(ringleader_id)

    due_date_str = due_date_datetime.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
<<<<<<< HEAD
    newCard = trellolist.add_card(name=f"[InDev Bot] {type} Response", due=due_date_str)
=======
    if host:
        ringleader = trello.get_member(get_trello_id(ringleader_id))
        newCard.add_member(ringleader)

    if spontaneus:
        label_id = "6437e2974720c87ca4fe3e98"  # SPON LABEL 6437e2974720c87ca4fe3e98
    else:
        label_id = "6437eb47965e94c2c8cb2eb3"  # SCHED LABEL

    label = trello.get_label(label_id, responseBoardID)
    newCard.add_label(label)

    return newCard


def set_card_completed(card_url: str):
    card_id = card_url.split("/")[-1]
    trello_card = trello.get_card(card_id)
    trello_card.set_due_complete()


def get_card_by_id(card_id):
    try:
        card = trello.get_card(card_id)
        return card
    except Exception as e:
        print(e)
        return None


def add_loa_to_card(card_id, loa_text):
    try:
        trello_card = trello.get_card(card_id)
        trello_card.comment(loa_text)
        return True
    except Exception as e:
        print(e)
        return False


def get_card_by_name_managmanetBoard(card_name):
    lists = membermanagmanetBoard.list_lists()
    if card_name == "Blue":
        card_name = "Bluegamerdog"
    if card_name == "Ellusive":
        card_name = "EllusiveTM"
    # Iterate over lists
    for trello_list in lists:
        cards = trello_list.list_cards()

        # Iterate over cards
        for card in cards:
            similarity_ratio = fuzz.ratio(card_name, card.name)
            if similarity_ratio >= 50:
                # Get all comments on the card
                return card

    return None


def get_card_by_name_activityBoard(card_name):
    lists = memberactivityBoard.list_lists()
    if card_name == "Blue":
        card_name = "Bluegamerdog"
    if card_name == "Ellusive":
        card_name = "EllusiveTM"
    # Iterate over lists
    for trello_list in lists:
        cards = trello_list.list_cards()

        # Iterate over cards
        for card in cards:
            similarity_ratio = fuzz.ratio(card_name, card.name)
            if similarity_ratio >= 50:
                # Get all comments on the card
                return card

    return None

def add_loa_label(card_id):
    try:
        trello_card = trello.get_card(card_id)
        loa_label = trello.get_label(
            "64373d1469dab5113422dd55", membermanagmanetBoardID
        )
        active_label = trello.get_label(
            "64373cae14c66fb33ccb6d12", membermanagmanetBoardID
        )
        trello_card.add_label(loa_label)
        trello_card.remove_label(active_label)
        return True
    except Exception as e:
        print(e)
        return False


def remove_loa_label(card_id):
    try:
        trello_card = trello.get_card(card_id)
        loa_label = trello.get_label(
            "64373d1469dab5113422dd55", membermanagmanetBoardID
        )
        active_label = trello.get_label(
            "64373cae14c66fb33ccb6d12", membermanagmanetBoardID
        )
        trello_card.add_label(active_label)
        trello_card.remove_label(loa_label)
        return True
    except Exception as e:
        print(e)
        return False


def add_cancelled_label(card_id):
    try:
        trello_card = trello.get_card(card_id)
        cancelled_label = trello.get_label("6437e432cdf097cffdc2fda1", responseBoardID)
        trello_card.add_label(cancelled_label)
        return True
    except Exception as e:
        print(e)
        return False

def add_log_comment(username: str, co_host: bool, host: str, response_type: str, spontaneous:bool):
    time_attended = time.strftime("%m/%d/%Y", time.localtime())  # Format timestamp as MM/DD/YYYY
    operator_card = get_card_by_name_activityBoard(username)
    
    if operator_card:
        print(time_attended, operator_card.name, co_host, host, response_type, spontaneous)
        comment_text = f"{time_attended} - {'Co-hosted' if co_host is True else 'Attended'}{' a spontaneous ' if spontaneous is True else ' a '}{response_type} Response (Host: {host})"
        print(username, comment_text)
        
        try:
            operator_card.comment(comment_text=comment_text)
            print("Comment added successfully.")
            return True
        except Exception as e:
            print(f"Error adding comment: {e}")
            return e
    else:
        print(f"Card not found for user: {username}")
        return False
    
    
    

def get_card_comments(card_name):
    lists = memberactivityBoard.list_lists()

    # Iterate over lists
    for trello_list in lists:
        # Get all cards in the list
        cards = trello_list.list_cards()

        # Iterate over cards
        for card in cards:
            similarity_ratio = fuzz.ratio(card_name, card.name)
            if similarity_ratio >= 50:
                print(str(similarity_ratio) +' | '+ card.name + ' ' + card_name)
                # Get all comments on the card
                comments = card.fetch_comments()
                return comments

    return False


def get_comments_timeframe(comments, unix_starttime, unix_endtime=None):
    start_time = datetime.utcfromtimestamp(int(unix_starttime))

    # If endtime is provided, convert it to a datetime object
    if unix_endtime is not None:
        end_time = datetime.utcfromtimestamp(int(unix_endtime))

    num_comments = 0

    for comment in comments:
        comment_time = datetime.strptime(comment["date"], "%Y-%m-%dT%H:%M:%S.%fZ")

        # Check if comment is within the specified time frame
        if unix_endtime is not None:
            if start_time <= comment_time <= end_time:
                num_comments += 1
        else:
            if comment_time >= start_time:
                num_comments += 1

    return num_comments
