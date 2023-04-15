import sqlite3
import time
import string
import random
import os



def opget_conn():
    db_path = os.path.join('Databases', 'response_database.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    return conn, cur


# Operation

def db_response_schedule(res_type, res_trello_link, res_start_time, ann_msg_link, ringleader_id): # Add a scheduled response to the db
    conn, cur = opget_conn()
    t = (res_type, res_trello_link, res_start_time, 0, 0, 0, 0, ann_msg_link, None, None, ringleader_id)
    cur.execute("INSERT INTO response_data (res_type, res_trello_link, res_start_time, concluded, started, spontaneous, cancelled, ann_msg_link, start_msg_link, end_msg_link, ringleader_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", t)
    conn.commit()

def db_response_spontaneous(res_type, res_trello_link, res_start_time, ann_msg_link, ringleader_id): # Add a spontaneus response to the db
    conn, cur = opget_conn()
    op_start_time = int(time.time())
    t = (res_type, res_trello_link, res_start_time, 0, 1, 1, 0, ann_msg_link, ann_msg_link, None, ringleader_id)
    cur.execute("INSERT INTO response_data (res_type, res_trello_link, res_start_time, concluded, started, spontaneous, cancelled, ann_msg_link, start_msg_link, end_msg_link, ringleader_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", t)
    conn.commit()

def db_response_ongoing(user_id): # Check if user has an already on-going response.
    conn, cur = opget_conn()
    t = (user_id,)
    cur.execute("SELECT * FROM response_data WHERE ringleader_id=? AND started=1 AND concluded=0", t)
    result = cur.fetchone()
    if result is None:
        return None
    return result

def db_response_time_check(start_time): # Check if there's already an op for that time.
    conn, cur = opget_conn()
    cur.execute("SELECT res_ID FROM response_data WHERE res_start_time = ?", (start_time,))
    result = cur.fetchone()
    if result is None:
        return False
    return result

def db_getall_responses_user(user_id): # Get all responses from a user.
    conn, cur = opget_conn()
    t = (user_id,)
    cur.execute("SELECT * FROM response_data WHERE ringleader_id=?", t)
    result = cur.fetchone()
    if result is None:
        return
    return result

def get_getall_planned_responses_user(user_id): # Get all non-started planned operations from a user
    conn, cur = opget_conn()
    t = (user_id,)
    cur.execute("SELECT * FROM response_data WHERE ringleader_id=? AND started=0 AND concluded=0 AND cancelled=0", t)
    results = cur.fetchall()
    if not results:
        return None
    return results

def resp_commence(primary_key, start_msg_link):
    conn, cur = opget_conn()
    t = (start_msg_link, primary_key,)
    cur.execute("UPDATE response_data SET start_msg_link=?, started=1 WHERE res_ID=?", t)
    conn.commit()
    return True

def op_cancel(primary_key, ): # Update an operation to cancelled
    conn, cur = opget_conn()
    t = (primary_key,)
    cur.execute("UPDATE response_data SET cancelled=1, WHERE res_ID=?", t)
    conn.commit()
    return True

def op_conclude(end_time, op_end_msg_link, ringleader_id): # Concludes an operation database wise.
    conn, cur = opget_conn()
    t = (end_time, op_end_msg_link, ringleader_id)
    cur.execute("UPDATE response_data SET concluded=1, res_end_time=?, end_msg_link=? WHERE ringleader_id=? AND started=1 AND concluded=0", t)
    rows_affected = cur.rowcount
    conn.commit()
    if rows_affected == 0:
        return False
    else:
        return True


    