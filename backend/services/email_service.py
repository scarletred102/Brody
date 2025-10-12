import imaplib
import email
from email import policy
from email.header import decode_header
from email.parser import BytesParser
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import re
import html as html_module


def _decode_header_value(value: Optional[str]) -> str:
    if not value:
        return ""
    try:
        parts = decode_header(value)
        decoded = ""
        for text, enc in parts:
            if isinstance(text, bytes):
                decoded += text.decode(enc or "utf-8", errors="ignore")
            else:
                decoded += text
        return decoded
    except Exception:
        return value or ""


def _html_to_text(html: str) -> str:
    # Very light-weight HTML -> text conversion without external deps
    try:
        # Remove script/style
        html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.IGNORECASE)
        html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.IGNORECASE)
        # Replace breaks/paragraphs with newlines
        html = re.sub(r"<(br|/p|/div|/li)>", "\n", html, flags=re.IGNORECASE)
        # Strip tags
        text = re.sub(r"<[^>]+>", " ", html)
        # Unescape entities
        text = html_module.unescape(text)
        # Collapse whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text
    except Exception:
        return html


def _get_body_from_message(msg: email.message.EmailMessage) -> str:
    # Prefer text/plain, then fall back to text/html
    try:
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                disp = str(part.get("Content-Disposition", "")).lower()
                if "attachment" in disp:
                    continue
                if ctype == "text/plain":
                    payload = part.get_payload(decode=True) or b""
                    return payload.decode(part.get_content_charset() or "utf-8", errors="ignore")
            for part in msg.walk():
                ctype = part.get_content_type()
                disp = str(part.get("Content-Disposition", "")).lower()
                if "attachment" in disp:
                    continue
                if ctype == "text/html":
                    payload = part.get_payload(decode=True) or b""
                    html = payload.decode(part.get_content_charset() or "utf-8", errors="ignore")
                    return _html_to_text(html)
        else:
            ctype = msg.get_content_type()
            payload = msg.get_payload(decode=True) or b""
            if ctype == "text/plain":
                return payload.decode(msg.get_content_charset() or "utf-8", errors="ignore")
            if ctype == "text/html":
                html = payload.decode(msg.get_content_charset() or "utf-8", errors="ignore")
                return _html_to_text(html)
    except Exception:
        pass
    return ""


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        # email.utils.parsedate_to_datetime available in py3.3+
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(value)
        # Ensure timezone-aware
        if dt and dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def parse_email_bytes(raw_bytes: bytes) -> Dict[str, Any]:
    msg = BytesParser(policy=policy.default).parsebytes(raw_bytes)
    subject = _decode_header_value(msg.get("Subject"))
    sender = _decode_header_value(msg.get("From"))
    date_hdr = _decode_header_value(msg.get("Date"))
    timestamp = _parse_datetime(date_hdr)
    message_id = _decode_header_value(msg.get("Message-Id")) or _decode_header_value(msg.get("Message-ID"))
    body = _get_body_from_message(msg)
    return {
        "id": message_id or "",
        "subject": subject or "",
        "sender": sender or "",
        "timestamp": timestamp,
        "body": body or "",
    }


class EmailService:
    """Lightweight IMAP client for listing and parsing messages."""

    def connect(self, host: str, username: str, password: str, port: int = 993, use_ssl: bool = True):
        try:
            if use_ssl:
                client = imaplib.IMAP4_SSL(host, port)
            else:
                client = imaplib.IMAP4(host, port)
            client.login(username, password)
            return client
        except Exception as e:
            raise RuntimeError(f"IMAP connection/login failed: {e}")

    def list_messages(self, client, mailbox: str = "INBOX", limit: int = 5) -> List[Dict[str, Any]]:
        try:
            typ, _ = client.select(mailbox, readonly=True)
            if typ != "OK":
                raise RuntimeError(f"Unable to select mailbox {mailbox}")
            typ, data = client.search(None, "ALL")
            if typ != "OK":
                raise RuntimeError("Search failed")
            ids = (data[0] or b"").split()
            if not ids:
                return []
            # Take latest N
            ids = ids[-limit:]
            results: List[Dict[str, Any]] = []
            for msg_id in ids[::-1]:  # newest first
                ftyp, msg_data = client.fetch(msg_id, "(RFC822)")
                if ftyp != "OK" or not msg_data or not msg_data[0]:
                    continue
                raw_bytes = msg_data[0][1]
                parsed = parse_email_bytes(raw_bytes)
                results.append(parsed)
            return results
        except Exception as e:
            raise RuntimeError(f"IMAP list/fetch failed: {e}")
