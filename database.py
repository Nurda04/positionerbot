import sqlite3 as sq


def db_start():
    global db, cur
    db = sq.connect("Desktop/Python/positioner_bot/bot.db")
    cur = db.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(
                'id' INTEGER PRIMARY KEY AUTOINCREMENT,
                'user_id' INTEGER,
                'name' TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS position(
                'users_name' TEXT,
                'operation' TEXT,
                'pos' TEXT,
                'time' DATETIME DEFAULT(STRFTIME('%H:%M', 'now', 'localtime', '+6 hours')),
                'day' DATETIME)""")
    db.commit()


def cmd_start_db(user_id):
    user = cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
    if not user:
        cur.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        db.commit()


def db_name(user_id, name):
    cur.execute("UPDATE users SET name = ? WHERE user_id = ?", (name, user_id))
    db.commit()


def db_get_name(user_id):
    result = cur.execute("SELECT name FROM users WHERE user_id = ?", (user_id,))
    return result.fetchone()[0]


def db_get_day():
    return cur.execute("SELECT strftime('%j', 'now', 'localtime', '+6 hours')").fetchone()[0]


def db_set_position(user_id, operation, pos):
    check = cur.execute("Select pos FROM position WHERE operation = ? AND users_name = ?", (operation, db_get_name(user_id))).fetchall()
    if not check:
        cur.execute("INSERT INTO position (users_name, operation, pos) VALUES (?, ?, ?)", (db_get_name(user_id), operation, pos))
        db.commit()
    else: 
        cur.execute("DELETE FROM position WHERE users_name = ? AND operation = ?", (db_get_name(user_id), operation))
        cur.execute("INSERT INTO position (users_name, operation, pos, day) VALUES (?, ?, ?, ?)", (db_get_name(user_id), operation, pos, db_get_day()))
        db.commit()
    

def db_check_registr(user_id):
    result = cur.execute("SELECT name FROM users WHERE user_id = ?", (user_id,))
    return result.fetchone()


def db_check_name(pos_name):
    result = cur.execute("SELECT name FROM users WHERE name = ?", (pos_name,))
    return result.fetchall()


def db_check_oper(oper, pos_name):
    result = cur.execute("SELECT pos FROM position WHERE operation = ? AND users_name = ? AND day = ?", (oper, pos_name, db_get_day()))
    return result.fetchall()


def db_get_position(oper, pos_name):
    result = cur.execute("SELECT pos, time FROM position WHERE operation = ? AND users_name = ? AND day = ?", (oper, pos_name, db_get_day()))
    return result.fetchone()
    