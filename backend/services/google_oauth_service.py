import os
from urllib.parse import urlencode
from google_auth_oauthlib.flow import Flow
from fastapi import Request

GOOGLE_CLIENT_ID = os.getenv("GMAIL_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GMAIL_REDIRECT_URI", "http://localhost:9000/auth/google/callback")
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"
]


def get_google_auth_flow(state=None):
    return Flow(
        client_type="web",
        client_config={
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uris": [GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=GOOGLE_SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI,
        state=state,
    )


def get_authorization_url(state=None):
    flow = get_google_auth_flow(state)
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    return auth_url


def fetch_token_from_code(code: str, state=None):
    flow = get_google_auth_flow(state)
    flow.fetch_token(code=code)
    return flow.credentials
