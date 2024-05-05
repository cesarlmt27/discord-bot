import sqlite3
import subprocess

con = sqlite3.connect("private/database.db")
cur = con.cursor()

server = subprocess.Popen("ls", stdout=subprocess.DEVNULL)
started_in = None
started_by = None
streaming = False
