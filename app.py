import os
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

from db import get_connection

from flask import Flask, redirect, url_for, session, request, render_template
from functools import wraps
from auth.google_oauth import create_flow, get_user_info

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

    session["user_id"]=user_id
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


@app.route("/dashboard")
@login_required
def dashboard():
    user_id=session["user_id"]

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
        SELECT load_score, load_label
        FROM cognitive_load
        WHERE user_id=?
        ORDER BY date DESC
        LIMIT 1                                 
    """, (user_id,))

    load=cur.fetchone()


    cur.execute("""
        SELECT date, sleep_hours, fatigue_level
                FROM user_state
                WHERE user_id=?
                ORDER BY date
                """, (user_id,))
    state_history=cur.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        user=session["user"],
        assignments=assignments,
        load=load,
        state_history=state_history
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





