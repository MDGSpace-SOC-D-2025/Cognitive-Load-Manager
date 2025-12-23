from google_auth_oauthlib.flow import Flow
import requests

CLIENT_SECRETS_FILE = "client_secret.json"

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/calendar.readonly"
]


REDIRECT_URI = "http://localhost:5000/auth/callback"


def create_flow():
    flow=Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES
    )
    flow.redirect_uri=REDIRECT_URI
    return flow

def get_user_info(credentials):
    response=requests.get(
          "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={
            "Authorization": f"Bearer {credentials.token}"
        }
    )
    return response.json()

