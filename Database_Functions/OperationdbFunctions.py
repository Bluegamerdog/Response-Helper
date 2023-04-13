import sqlite3
import time
import string
import random
import os



def opget_conn():
    db_path = os.path.join('Databases', 'operation_database.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    return conn, cur

# PALS

def pal_blacklist_add(pals):
    # Check if each pal already exists
    conn, cur = opget_conn()
    existing_pals = []
    for pal in pals:
        cur.execute("SELECT pals FROM blacklisted_pals WHERE pals=?", (pal,))
        result = cur.fetchone()
        if result:
            existing_pals.append(pal)
        else:
            # Add to database
            cur.execute("INSERT INTO blacklisted_pals(pals) VALUES (?)", (pal,))
    conn.commit()
    if existing_pals:
        return False, existing_pals
    else:
        return True, []

def pal_blacklist_remove(pals):
    conn, cur = opget_conn()
    nonexisting_pals = []
    for pal in pals:
        cur.execute("SELECT pals FROM blacklisted_pals WHERE pals=?", (pal,))
        result = cur.fetchone()
        if not result:
            nonexisting_pals.append(pal)
        else:
            # Remove from database
            cur.execute("DELETE FROM blacklisted_pals WHERE pals=?", (pal,))
    conn.commit()
    if nonexisting_pals:
        return False, nonexisting_pals
    else:
        return True, []

def get_blacklisted_pals():
    conn, cur = opget_conn()
    cur.execute("SELECT pals FROM blacklisted_pals")
    result = cur.fetchall()
    return result

#blacklist = ['SEX', 'FUC', 'FUK', "KYS", "YES", "ASS", "NIG", "GGR", "GER"] ## NOTES
def generate_pals(length):
    letters = string.ascii_uppercase
    while True:
        pals = ''.join(random.choice(letters) for i in range(length))
        blacklisted_pals = get_blacklisted_pals()
        if not any(black in pals for black in blacklisted_pals):  # check if any blacklisted combination exists in the string
            return pals

# Operation

def op_create_scheduled(op_type, op_pal, op_start, op_trello, op_message_id):
    conn, cur = opget_conn()
    t = (op_type, op_pal, op_start, op_trello, 0, 0, op_message_id, )
    cur.execute("INSERT INTO op_table (OP_TYPE, OP_PAL, OP_START, OP_TRELLO, OP_SPON, OP_CONCLU, OP_MESSAGE_ID) VALUES (?,?,?,?,?,?,?)", t)
    conn.commit()

def op_get_info(op_pal):
    conn, cur = opget_conn()
    t = (op_pal,)
    cur.execute("SELECT * FROM op_table WHERE OP_PAL=?", t)
    result = cur.fetchone()
    if result is None:
        return
    return result

def op_create_spontaneous(op_type, op_pal, op_message_id, op_trello=None):
    conn, cur = opget_conn()
    op_start = int(time.time())
    if op_trello==None:
        op_trello = "TBA"
    t = (op_type, op_pal, op_start, op_trello, 1, 0, op_message_id, )
    cur.execute("INSERT INTO op_table (OP_TYPE, OP_PAL, OP_START, OP_TRELLO, OP_SPON, OP_CONCLU, OP_MESSAGE_ID) VALUES (?,?,?,?,?,?,?)", t)
    conn.commit()

def op_cancel(op_pal):
    conn, cur = opget_conn()
    t = (op_pal,)
    cur.execute("DELETE FROM op_table WHERE OP_PAL=?", t)
    conn.commit()
    return True

def op_conclude(op_pal):
    conn, cur = opget_conn()
    t = (op_pal,)
    cur.execute("UPDATE op_table SET OP_CONCLU=1 WHERE OP_PAL=?", t)
    rows_affected = cur.rowcount
    conn.commit()
    if rows_affected == 0:
        return False
    else:
        return True

def op_edit(op_pal, op_type=None, op_start=None, op_trello=None):
    conn, cur = opget_conn()
    updates = []
    if op_type is not None:
        updates.append("OP_TYPE=?")
    if op_start is not None:
        updates.append("OP_START=?")
    if op_trello is not None:
        updates.append("OP_TRELLO=?")

    if updates:
        t = (op_pal,) + tuple(
            value for value in (op_type, op_start, op_trello) if value is not None
        )
        query = f"UPDATE op_table SET {','.join(updates)} WHERE OP_PAL=?"
        cur.execute(query, t)
        conn.commit()
    else:
        print("Cannot find operation")


    