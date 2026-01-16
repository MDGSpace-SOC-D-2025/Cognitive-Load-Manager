<<<<<<< HEAD
import sqlite3

DB_NAME="cognitive_load.db"

def get_connection():
    conn=sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys=ON")
=======
import sqlite3

DB_NAME="cognitive_load.db"

def get_connection():
    conn=sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys=ON")
>>>>>>> 9c15bd2489283ce4463ab9d773e86d0d0f88124b
    return conn