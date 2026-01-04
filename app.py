import os
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

import joblib
predicting_model=joblib.load("cognitive_load_model.pkl")



from db import get_connection

from flask import Flask, redirect, url_for, session, request, render_template
from functools import wraps
from auth.google_oauth import create_flow, get_user_info

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime, timezone, date

app = Flask(__name__)
app.secret_key = "dev-secret-key"  



def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated_function



@app.route("/")
def login_page():
    return render_template("login.html")


@app.route("/login")
def login():
    flow = create_flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true"
    )

    session["state"] = state
    return redirect(authorization_url)


@app.route("/auth/callback")
def auth_callback():
    flow = create_flow()
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    user_info = get_user_info(credentials)


    conn=get_connection()
    cur=conn.cursor()

    cur.execute("""
INSERT OR IGNORE INTO users (google_id, email, name)
                VALUES(?,?,?)
                """,(
                    user_info["id"],
                    user_info["email"],
                    user_info["name"],
                    )
                )
    
    conn.commit()

    cur.execute("""
SELECT id FROM users WHERE google_id=?
                """, (user_info["id"],))
    
    user_id=cur.fetchone()[0]
    conn.close()

    session["user_id"]=user_id #yaha pe user_id session me store hui as session.user_id=user_id, basically smthlike yaha session bana
    session["user"]={
        "name": user_info["name"],
        "email":user_info["email"]
    }

    session["credentials"]={
    "token": credentials.token,
    "refresh_token": credentials.refresh_token,
    "token_uri": credentials.token_uri,
    "client_id": credentials.client_id,
    "client_secret":credentials.client_secret,
    "scopes": credentials.scopes

    }

    return redirect(url_for("dashboard")) 
# this"dashboard" is the name of the function defined ahead, url_for looks at the the place where this function is defined and redirects there. in this case, /dashboard


@app.route("/dashboard")
@login_required
def dashboard():
    user_id=session["user_id"] #yaha pehle ye input dena pada ki user_id is the same session ka user id. thus user_id=session[user_id]

    conn=get_connection()
    cur=conn.cursor()


    cur.execute("""
        SELECT title, deadline
        FROM assignments
        WHERE user_id=?
        ORDER BY deadline
              """, (user_id,))
    assignments=cur.fetchall()


    cur.execute(""" 
        SELECT IFNULL(SUM(duration_hours),0)
        FROM study_sessions
        WHERE user_id=?
        """,(user_id,))
    total_study_hours=cur.fetchone()[0]



    cur.execute("""
        SELECT load_score, load_label
        FROM cognitive_load
        WHERE user_id=?
        ORDER BY date DESC
        LIMIT 1                                 
    """, (user_id,))

    # cognitive_load=cur.fetchone()


    cur.execute("""
        SELECT date, sleep_hours, fatigue_level
                FROM user_state
                WHERE user_id=?
                ORDER BY date DESC
                LIMIT 1
                """, (user_id,))
    latest_state=cur.fetchone()

    conn.close()

     # Get cognitive load from session



     
    user_id=session["user_id"]
    conn=get_connection()
    cur=conn.cursor()

    cur.execute(
        """SELECT sleep_hours, fatigue_level
          FROM user_state
          WHERE user_id=?
          LIMIT 1
    """,(user_id,)
    )
    sleep_hours, fatigue_level=cur.fetchone()


    cur.execute(
        """SELECT duration_hours
        FROM study_sessions
        WHERE user_id=?
        """,(user_id,)
    )
    study_hours=cur.fetchone()[0] or 0

    cur.execute(
        """SELECT COUNT(*), AVG(julianday(deadline)-julianday('now'))
        FROM assignments
        WHERE user_id=?
    """,(user_id,)
    )
    assignments_due, avg_deadline_days=cur.fetchone()
    avg_deadline_days=avg_deadline_days or 30


    conn.close()

    


    X=[[
    sleep_hours,
    fatigue_level,
    assignments_due,
    avg_deadline_days,
    study_hours
    ]]


    cognitive_load=float(predicting_model.predict(X)[0])
    print("the load is :",cognitive_load)

    conn=get_connection()
    cur=conn.cursor()

    cur.execute("""
        INSERT INTO cognitive_load(user_id, load_score)
        VALUES(?,?)""",
        (user_id, cognitive_load))
    
    conn.commit()
    conn.close()




    return render_template(
        "dashboard.html",
        user=session["user"],
        assignments=assignments,
        cognitive_load=cognitive_load,
        latest_state=latest_state,
        total_study_hours=total_study_hours
    )


@app.route("/log_state", methods=["POST"])
@login_required
def log_state():
    sleep_hours=float(request.form["sleep_hours"])
    fatigue_level=int(request.form["fatigue_level"])
    user_id= session["user_id"]

    conn=get_connection()
    cur=conn.cursor()

    cur.execute("""
    INSERT INTO user_state(user_id, date, sleep_hours, fatigue_level)
    VALUES (?, DATE('now'), ?, ?)
""", (user_id, sleep_hours, fatigue_level)
    )

    conn.commit()
    conn.close()


    return redirect(url_for("dashboard"))



@app.route("/start_session", methods=["POST"])
@login_required
def start_session():
    user_id=session["user_id"]

    conn=get_connection()
    cur=conn.cursor()

    cur.execute("""
        INSERT INTO study_sessions (user_id, start_time)
        VALUES (?, DATETIME('now'))
    """, (user_id,))

    conn.commit()
    conn.close()

    return "", 204




@app.route("/stop_session", methods=["POST"])
@login_required
def stop_session():
    user_id=session["user_id"]

    conn=get_connection()
    cur=conn.cursor()

    cur.execute("""
        SELECT id, start_time
        FROM study_sessions
        WHERE user_id=? AND end_time IS NULL
        ORDER BY start_time DESC
        LIMIT 1
    """,(user_id,))
    session_row=cur.fetchone()

    if session_row:    
        session_id, start_time=session_row
        # THIS IS TO CHECK IF AN ACTIVE SESSION EXISTS

        cur.execute("""
            UPDATE study_sessions
            SET end_time=DATETIME('now'), 
                    duration_hours=
                        (JULIANDAY(DATETIME('now')) - JULIANDAY(start_time)) * 24
            WHERE id = ?
        """, (session_id,))

        
    conn.commit()
    conn.close()


    return "", 204



@app.route("/sync_calendar", methods=["POST"])
@login_required
def sync_calendar():
    user_id=session["user_id"]

    creds_data=session["credentials"]
    credentials=Credentials(
        token=creds_data["token"],
        refresh_token=creds_data["refresh_token"],
        token_uri=creds_data["token_uri"],
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=creds_data["scopes"]
    )

    service=build("calendar", "v3", credentials=credentials)
    
    now=datetime.utcnow().isoformat()+"Z"


    events_result=service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=20,
        singleEvents=True,
        orderBy='startTime'

    ).execute()

    events=events_result.get("items", [])


    user_id= session["user_id"]
    conn=get_connection()
    cur=conn.cursor()

    # events is a list; event is a dictionary 
    for event in events: 
        title=event.get('summary')

        first=event.get('start')
        start_time=first.get('dateTime')
        start_date=first.get('date')
        deadline=start_time or start_date
        event_id=event["id"]

        cur.execute("""
        INSERT OR IGNORE INTO assignments(user_id, google_event_id, title, deadline)
        VALUES (?,?,?,?)""", (user_id,event_id, title, deadline))
    
    conn.commit()
    conn.close()


    return redirect(url_for("dashboard"))







    
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))



def init_db():
    print("Initializing database...")
    conn = get_connection()
    with open("schema.sql", "r") as f:
        conn.executescript(f.read())
    conn.close()
    print("Database initialized.")





if __name__ == "__main__":
    init_db()
    app.run(debug=True)





