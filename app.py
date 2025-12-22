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


    session["user"] = {
        "google_id": user_info["id"],
        "email": user_info["email"],
        "name": user_info["name"]
    }

    
    session["credentials"] = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes
    }

    return redirect(url_for("dashboard"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=session["user"])


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





if __name__ == "__main__":
    app.run(debug=True)
