import sqlite3

DB_NAME="cognitive_load.db"

def get_connection():
    conn=sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys=ON")
    return conn