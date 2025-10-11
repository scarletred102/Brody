from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from services.email_service import EmailService, parse_email_bytes
from services.openrouter_service import OpenRouterService


router = APIRouter(prefix="/email", tags=["email"])
email_service = EmailService()
ai = OpenRouterService()


class IMAPCreds(BaseModel):
    host: str
    username: str
    password: str
    port: Optional[int] = 993
    use_ssl: Optional[bool] = True
    mailbox: Optional[str] = "INBOX"
    limit: Optional[int] = 5


class RawEmail(BaseModel):
    raw: str  # base64 or raw RFC822; we will try bytes decode


@router.post("/imap/test")
def imap_test(creds: IMAPCreds) -> Dict[str, Any]:
    try:
        client = email_service.connect(creds.host, creds.username, creds.password, creds.port or 993, creds.use_ssl is not False)
        try:
            messages = email_service.list_messages(client, creds.mailbox or "INBOX", creds.limit or 5)
        finally:
            try:
                client.logout()
            except Exception:
                pass
        return {"ok": True, "count": len(messages), "sample": messages[:1]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/parse")
def parse(raw: RawEmail) -> Dict[str, Any]:
    # Try to interpret the string as raw RFC822; if looks like base64, attempt decode
    data: bytes
    try:
        if "\n" not in raw.raw and "\r" not in raw.raw:
            # probably base64
            import base64
            data = base64.b64decode(raw.raw)
        else:
            data = raw.raw.encode("utf-8", errors="ignore")
    except Exception:
        data = raw.raw.encode("utf-8", errors="ignore")
    parsed = parse_email_bytes(data)
    # Make timestamp JSON serializable
    ts = parsed.get("timestamp")
    if isinstance(ts, datetime):
        parsed["timestamp"] = ts.isoformat()
    return parsed


@router.post("/fetch-and-classify")
def fetch_and_classify(creds: IMAPCreds) -> Dict[str, Any]:
    try:
        client = email_service.connect(creds.host, creds.username, creds.password, creds.port or 993, creds.use_ssl is not False)
        try:
            messages = email_service.list_messages(client, creds.mailbox or "INBOX", creds.limit or 5)
        finally:
            try:
                client.logout()
            except Exception:
                pass

        results: List[Dict[str, Any]] = []
        for m in messages:
            ai_result: Optional[Dict[str, Any]] = None
            if ai and ai.available():
                ai_result = ai.classify_email(m.get("subject", ""), m.get("body", ""), m.get("sender", ""))

            if ai_result:
                results.append({
                    "email": {
                        **m,
                        "timestamp": m.get("timestamp").isoformat() if isinstance(m.get("timestamp"), datetime) else m.get("timestamp")
                    },
                    "classification": ai_result,
                })
            else:
                # fallback simple heuristic
                subj = (m.get("subject") or "").lower()
                urgency = "high" if any(w in subj for w in ["urgent", "asap", "important"]) else ("low" if any(w in subj for w in ["fyi", "optional"]) else "medium")
                results.append({
                    "email": {
                        **m,
                        "timestamp": m.get("timestamp").isoformat() if isinstance(m.get("timestamp"), datetime) else m.get("timestamp")
                    },
                    "classification": {
                        "urgency": urgency,
                        "category": "work",
                        "sentiment": "neutral",
                        "action": "response_needed" if urgency == "high" else "fyi",
                        "summary": (m.get("subject") or "")[:100]
                    }
                })

        return {"ok": True, "count": len(results), "results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
