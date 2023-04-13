import sqlite3
import time
import os
from datetime import datetime
from Database_Functions.UserdbFunction import (userget_conn)
from Database_Functions.OperationdbFunctions import (opget_conn)
from Database_Functions.RankdbFunctions import (rankget_conn)

def get_conn():
    db_path = os.path.join('Databases', 'main_database.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    return conn, cur

def replace_value(database, table, column, old_value, new_value):
    if str(database) == "main": # Connect to main_database.db
        conn, cur = get_conn()
    elif str(database) == "operations": # Connect to operations_database.db
        conn, cur = opget_conn()
    elif str(database) == "ranks": # Connect to rank_database.db
        conn, cur = rankget_conn()
    elif str(database) == "users": # Connect to user_database.db
        conn, cur = userget_conn()
    cur.execute(f"UPDATE {table} SET {column} = ? WHERE {column} = ?", (new_value, old_value))
    conn.commit()
    
def clear_table(database, table):
    if str(database) == "main":
        conn, cur = get_conn()
    elif str(database) == "operations":
        conn, cur = opget_conn()
    elif str(database) == "ranks":
        conn, cur = rankget_conn()
    elif str(database) == "users":
        conn, cur = userget_conn()
    cur.execute(f"DELETE FROM {table}")
    conn.commit()

## LEADERBOARD ##
def add_leaderboard(username, message_id, count):
    conn, cur = get_conn()
    now=datetime.now()
    timestamp=datetime.timestamp(now)
    t = (username, message_id, timestamp, 1, count, )
    cur.execute("INSERT INTO board_tables(username, message_id, created_time, page_number, last_usernumber) VALUES(?,?,?,?,?)", t)
    conn.commit()
    
def check_leaderboard(message_id, user_id):
    conn, cur = get_conn()
    t = (user_id, message_id, )
    cur.execute("SELECT COUNT(*) FROM board_tables WHERE username = ? AND message_id = ?",t)
    data = cur.fetchall()
    if(data[0][0] == 0):
        return False
    else:
        return True
  
def get_leaderboard_page(message_id):
    conn, cur = get_conn()
    t = (message_id, )
    cur.execute("SELECT * FROM board_tables WHERE message_id = ?",t)
    data = cur.fetchall()
    return data[0][4], data[0][5]
    
def update_leaderboard(page, last_user, message_id):
    conn, cur = get_conn()
    t = (page, last_user, message_id)
    cur.execute("UPDATE board_tables SET page_number = ? , last_usernumber = ? WHERE message_id = ?", t)
    conn.commit()

## QUOTA ##

def set_active_block(block_num):
    conn, cur = get_conn()
    cur.execute("UPDATE quota_blocks SET active = 0") # set all rows to inactive
    cur.execute("UPDATE quota_blocks SET active = 1 WHERE block_num = ?", (block_num,)) # set the specified block to active
    conn.commit()

def get_quota(block_num=None): # Blocks 7 - 26 (End of 2023)
    conn, cur = get_conn()
    if block_num is None:
        cur.execute(f"SELECT * FROM quota_blocks WHERE active = 1") # Get info about active block
        blockdata = cur.fetchone()
        if blockdata is not None:
            return blockdata ## Block_Num, Start, End
        else:
            return None
    else:
        cur.execute(f"SELECT * FROM quota_blocks WHERE block_num = ?", (block_num,)) # Get info about specific block
        blockdata = cur.fetchone()
        if blockdata is not None:
            return blockdata ## Block_Num, Start, End
        else:
            return False
        
def get_all_quota_data():
    conn, cur = get_conn()
    cur.execute("SELECT * FROM quota_blocks")
    data = cur.fetchall()
    count = len(data)
    return data, count

        

    


    



 

