#!/usr/bin/env python3
import email
import imaplib
import json
import os
import sys
import urllib.request
from datetime import datetime
from email.header import decode_header


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


IMAP_HOST = os.getenv("NIUERA_IMAP_HOST", "imap.example.com")
IMAP_PORT = int(os.getenv("NIUERA_IMAP_PORT", "993"))
EMAIL_USER = require_env("NIUERA_IMAP_USER")
EMAIL_PASS = require_env("NIUERA_IMAP_PASS")
WEBHOOK_URL = require_env("NIUERA_EMAIL_WEBHOOK_URL")
PROCESSED_FILE = os.getenv("NIUERA_PROCESSED_EMAILS_FILE", "/home/ubuntu/processed_emails.txt")


def decode_str(s):
    if s is None:
        return ""
    parts = decode_header(s)
    result = []
    for part, charset in parts:
        if isinstance(part, bytes):
            result.append(part.decode(charset or "utf-8", errors="ignore"))
        else:
            result.append(part)
    return "".join(result)


def decode_payload(part):
    payload = part.get_payload(decode=True)
    if payload is None:
        return ""
    charset = part.get_content_charset() or "utf-8"
    return payload.decode(charset, errors="ignore")


def get_body(msg):
    text_body = ""
    html_body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain" and not text_body:
                text_body = decode_payload(part)
            elif content_type == "text/html" and not html_body:
                html_body = decode_payload(part)
    else:
        payload = decode_payload(msg)
        if msg.get_content_type() == "text/html":
            html_body = payload
        else:
            text_body = payload

    return {"text": text_body, "html": html_body}


def load_processed():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()


def save_processed(ids):
    processed_path = os.path.dirname(PROCESSED_FILE)
    if processed_path:
        os.makedirs(processed_path, exist_ok=True)

    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        for mid in list(ids)[-500:]:
            f.write(mid + "\n")


def post_to_webhook(payload: dict):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        WEBHOOK_URL,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(req, timeout=30)


def main():
    processed = load_processed()
    mailbox = None

    try:
        mailbox = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mailbox.login(EMAIL_USER, EMAIL_PASS)
        mailbox.select("INBOX")

        status, msgs = mailbox.search(None, "UNSEEN")
        if status != "OK" or not msgs[0]:
            return

        for num in msgs[0].split():
            status, data = mailbox.fetch(num, "(RFC822)")
            if status != "OK":
                continue

            msg = email.message_from_bytes(data[0][1])
            msg_id = msg.get("Message-ID", "").strip()

            if not msg_id:
                msg_id = f"NO_MSG_ID_{num.decode()}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            if msg_id in processed:
                mailbox.store(num, "+FLAGS", "\\Seen")
                continue

            from_addr = decode_str(msg.get("From", ""))
            subject = decode_str(msg.get("Subject", ""))
            body = get_body(msg)

            payload = {
                "from": from_addr,
                "subject": subject,
                "text": body["text"],
                "html": body["html"],
            }

            try:
                post_to_webhook(payload)
                mailbox.store(num, "+FLAGS", "\\Seen")
                processed.add(msg_id)
                print(f"[OK] {subject[:60]}")
            except Exception as exc:
                print(f"[ERROR] {subject[:60]}: {exc}", file=sys.stderr)

        save_processed(processed)

    finally:
        if mailbox is not None:
            try:
                mailbox.logout()
            except Exception:
                pass


if __name__ == "__main__":
    main()
