import sqlite3

def get_connection():
    con = sqlite3.connect("private/database.db")
    cur = con.cursor()
    return cur, con