import sqlite3

DB_NAME="cognitive_load.db"

def get_connection():
    return sqlite3.connect(DB_NAME)