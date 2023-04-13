import os
import sqlite3

def rankget_conn():
    db_path = os.path.join('Databases', 'rank_database.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    return conn, cur

def rankbind_add(rank_name, roblox_group_id, roblox_role_id, discord_role_id, discord_role_id2, discord_role_id3):
    conn, cur = rankget_conn()
    t = (rank_name, roblox_group_id, roblox_role_id, discord_role_id, discord_role_id2, discord_role_id3)
    cur.execute("INSERT INTO rankbinds (rank_name, roblox_group_id, roblox_role_id, discord_role_id, discord_role_id2, discord_role_id3) VALUES (?,?,?,?,?,?)", t)
    conn.commit()
    
def rankbind_edit(op_type, op_pal, op_start, op_trello, op_message_id):
    conn, cur = rankget_conn()
    t = (op_type, op_pal, op_start, op_trello, 0, 0, op_message_id, )
    cur.execute("INSERT INTO rankbinds (OP_TYPE, OP_PAL, OP_START, OP_TRELLO, OP_SPON, OP_CONCLU, OP_MESSAGE_ID) VALUES (?,?,?,?,?,?,?)", t)
    conn.commit()
    
def rankbind_remove(op_type, op_pal, op_start, op_trello, op_message_id):
    conn, cur = rankget_conn()
    t = (op_type, op_pal, op_start, op_trello, 0, 0, op_message_id, )
    cur.execute("INSERT INTO rankbinds (OP_TYPE, OP_PAL, OP_START, OP_TRELLO, OP_SPON, OP_CONCLU, OP_MESSAGE_ID) VALUES (?,?,?,?,?,?,?)", t)
    conn.commit()