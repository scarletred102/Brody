from fastapi import APIRouter, Request, Response, status
from fastapi.responses import RedirectResponse, JSONResponse
from services.google_oauth_service import get_authorization_url, fetch_token_from_code
import os

router = APIRouter(prefix="/auth/google", tags=["auth", "google"])

@router.get("/login")
def google_login():
    url = get_authorization_url()
    return RedirectResponse(url)

@router.get("/callback")
def google_callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    if not code:
        return JSONResponse({"error": "Missing code"}, status_code=400)
    try:
        creds = fetch_token_from_code(code, state)
        # For MVP, just return the tokens (DO NOT do this in production)
        return JSONResponse({
            "access_token": creds.token,
            "refresh_token": getattr(creds, "refresh_token", None),
            "token_expiry": str(getattr(creds, "expiry", None)),
            "scopes": creds.scopes,
            "id_token": getattr(creds, "id_token", None)
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
