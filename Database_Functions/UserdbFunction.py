import os
import sqlite3


## Also still refernce for now but no purpose


def userget_conn():
    db_path = os.path.join('Databases', 'user_database.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    return conn, cur


## POINTS ##

def add_points(discord_id, points):
    conn, cur = userget_conn()
    result = db_register_get_data(discord_id)
    if result:
        cur.execute("UPDATE registry SET points = points + ? WHERE discord_id = ?", (points, result[1], ))
        conn.commit()
        return True
    return False

def remove_points(discord_id, points):
    conn, cur = userget_conn()
    result = db_register_get_data(discord_id)
    rows_updated = 0
    if result:
        cur.execute("UPDATE registry SET points = CASE WHEN points - ? < 0 THEN 0 ELSE points - ? END WHERE discord_id = ?", (points, points, discord_id))
        rows_updated = cur.rowcount
        conn.commit()
    return rows_updated > 0

def get_points(discord_id):
    conn, cur = userget_conn()
    result = db_register_get_data(discord_id)
    if result:
        cur.execute("SELECT points FROM registry WHERE discord_id = ?", (discord_id, ))
        data = cur.fetchall()
        return int(data) if data else 0 # If None, user has no points
    return False # If false, no data in registry

def get_users_amount(page = 1):
    page_offset = (page - 1) * 10
    conn, cur = userget_conn()
    cur.execute("SELECT * FROM registry ORDER BY points DESC LIMIT "+ str(page_offset) +",10")
    rows = cur.fetchall()
    return rows

def get_total_points():
    conn, cur = userget_conn()
    cur.execute("SELECT SUM(points) FROM registry")
    total_points = cur.fetchone()[0]
    return total_points

async def reset_points():
    conn, cur = userget_conn()
    try:
        cur.execute("UPDATE registry SET points = 0, days_excused = NULL")
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return False


## REGISTRY ##

def db_register_new(username, user_id, profile_link):
    conn, cur = userget_conn()
    t = (user_id, )
    result = cur.execute("SELECT * FROM users WHERE user_id=?", t)
    if result.fetchone() is not None:
        return False
    else:
        t = (username, user_id, profile_link, 0, )
        result = cur.execute("INSERT INTO users(username, user_id, roblox_profile, points) VALUES(?,?,?,?)", t)
        conn.commit()
        return True
    
def db_register_update_username(user_id, new_username):
    conn, cur = userget_conn()
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    if row and row[0] != new_username:
        cur.execute("UPDATE users SET username=? WHERE user_id=?", (new_username, user_id))
        conn.commit()
        return True
    else:
        return False
   
def db_register_update_profile_link(user_id, new_profile_link):
    conn, cur = userget_conn()
    cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    if row and row[2] != new_profile_link:
        cur.execute("UPDATE users SET roblox_profile=? WHERE user_id=?", (new_profile_link, user_id))
        conn.commit()
        return True
    else:
        return False

def db_register_remove_user(user_id):
    conn, cur = userget_conn()
    t = (user_id, )
    result = cur.execute("SELECT * FROM users WHERE user_id=?", t)
    if result.fetchone() is None:
        return False
    else:
        cur.execute("DELETE FROM users WHERE user_id = ?", t)
        conn.commit()
        return True

def db_get_all_data():
    conn, cur = userget_conn()
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    return rows

def db_register_get_data(user_id):
    conn, cur = userget_conn()
    t = (user_id,)
    cur.execute("SELECT * FROM users WHERE user_id=?", t)
    user_data = cur.fetchone()
    if user_data == None:
        return False
    else:
        return user_data

def db_register_purge():
    conn, cur = userget_conn()
    result = cur.execute("DELETE FROM users")
    conn.commit()
    if result.rowcount > 0:
        return True, result
    else:
        return False, result
  
  
## DEV ACCESS ##
    
def add_devaccess_member(user_id, user_name):
    conn, cur = userget_conn()
    cur.execute("SELECT * FROM devaccess WHERE user_ids=?", (user_id,))
    if cur.fetchone() is not None:
        return False
    else:
        cur.execute("INSERT INTO devaccess (user_ids, user_names) VALUES (?, ?)", (user_id, user_name))
        conn.commit()
        return True

def remove_devaccess_member(user_id):
    conn, cur = userget_conn()
    cur.execute("SELECT * FROM devaccess WHERE user_ids=?", (user_id,))
    if cur.fetchone() is None:
        return False
    else:
        cur.execute("DELETE FROM devaccess WHERE user_ids=?", (user_id,))
        conn.commit()
        return True

def get_devaccess_members():
    conn, cur = userget_conn()
    cur.execute("SELECT user_ids FROM devaccess")
    return cur.fetchall()


## OTHER ##

def set_days_userOnLoA(discord_id, length):
    conn, cur = userget_conn()
    result = db_register_get_data(discord_id)
    if result:
        if length == 0:
            cur.execute("UPDATE registry SET days_excused = NULL WHERE discord_id = ?", (result[1],))
        elif length is not None:
            cur.execute("UPDATE registry SET days_excused = ? WHERE discord_id = ?", (length, result[1]))
        conn.commit()
        return True
    return False

def get_roblox_link(discord_id):
    conn, cur = userget_conn()
    cur.execute("SELECT * FROM registry WHERE discord_id=?", (discord_id,))
    result = cur.fetchone()
    if result:
        return result[4]
    return None