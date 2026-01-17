
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
    google_event_id TEXT NOT NULL,


    UNIQUE(user_id, google_event_id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);


CREATE TABLE IF NOT EXISTS user_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date TEXT,
    sleep_hours REAL, 
    fatigue_level INTEGER,
    FOREIGN KEY(user_id) REFERENCES users(id)   
);


CREATE TABLE IF NOT EXISTS cognitive_load(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
date TEXT,
load_score REAL,
load_label TEXT,
FOREIGN KEY(user_id) REFERENCES users(id) 

);


CREATE TABLE IF NOT EXISTS study_sessions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    duration_hours REAL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);


