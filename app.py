import os
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

from flask import Flask, redirect, url_for, session, request, render_template
from functools import wraps

# OAuth helper functions (you will create this file)
from auth.google_oauth import create_flow, get_user_info

app = Flask(__name__)
app.secret_key = "dev-secret-key"  # replace later with env variable


# -------------------------
# Login required decorator
# -------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated_function


# -------------------------
# Basic routes
# -------------------------
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

    # Store logged-in user info
    session["user"] = {
        "google_id": user_info["id"],
        "email": user_info["email"],
        "name": user_info["name"]
    }

    # Store OAuth credentials (needed for Calendar)
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
    # Later: fetch data from DB, ML predictions, etc.
    return render_template("dashboard.html", user=session["user"])


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


# -------------------------
# App entry point
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)