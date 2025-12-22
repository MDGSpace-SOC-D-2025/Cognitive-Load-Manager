CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    google_id TEXT UNIQUE,
    email TEXT,
    name TEXT
);

CREATE TABLE IF NOT EXISTS assignments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT,
    deadline TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);


CREATE TABLE IF NOT EXISTS user_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date TEXT,
    sleep_hours REAL, --check this
    fatigue_level INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id)   --check this
);


CREATE TABLE IF NOT EXISTS cognitive_load(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
date TEXT,
load_score REAL,
load_label TEXT,
FOREIGN KEY(user_id) REFERENCES users(id) 

);