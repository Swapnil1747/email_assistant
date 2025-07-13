# main.py

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from web_search import search_web_duckduckgo
from calendar_integration import create_event, extract_meeting_datetime
from nlp_utils import extract_questions, is_human_sender
from database import init_db, SessionLocal, Email
from llm_integration import summarize_email, generate_reply, generate_event_title
from email_actions import send_email
from slack_bot import send_slack_message
from email.utils import parsedate_to_datetime
from datetime import datetime
from dateutil.tz import gettz
from bs4 import BeautifulSoup
import os.path
import base64

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar.events'
]

def extract_question_from_email(text):
    questions = extract_questions(text)
    return questions[0] if questions else None

def authenticate_google_services():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    gmail_service = build('gmail', 'v1', credentials=creds)
    calendar_service = build('calendar', 'v3', credentials=creds)
    return gmail_service, calendar_service

def parse_email_body(payload):
    parts = payload.get("parts")
    if parts:
        for part in parts:
            mime_type = part.get("mimeType")
            data = part.get("body", {}).get("data")
            if mime_type == "text/plain" and data:
                return base64.urlsafe_b64decode(data).decode("utf-8")
            elif mime_type == "text/html" and data:
                html = base64.urlsafe_b64decode(data).decode("utf-8")
                return BeautifulSoup(html, "html.parser").get_text()
    else:
        data = payload.get("body", {}).get("data")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8")
    return ""

def fetch_and_store_emails(service):
    session = SessionLocal()
    results = service.users().messages().list(userId='me', maxResults=10, q="is:unread").execute()
    messages = results.get('messages', [])

    for msg in messages:
        full_msg = service.users().messages().get(userId='me', id=msg['id']).execute()
        payload = full_msg.get('payload', {})
        headers = payload.get('headers', [])

        email_data = {
            'id': full_msg['id'],
            'thread_id': full_msg['threadId'],
            'sender': '',
            'recipient': '',
            'subject': '',
            'date': None,
            'body': parse_email_body(payload),
        }
        for header in headers:
            name = header['name']
            value = header['value']
            if name == 'From':
                email_data['sender'] = value
            elif name == 'To':
                email_data['recipient'] = value
            elif name == 'Subject':
                email_data['subject'] = value
            elif name == 'Date':
                email_data['date'] = parsedate_to_datetime(value)

        if not session.query(Email).filter_by(id=email_data['id']).first():
            email = Email(**email_data)
            session.add(email)
            print(f"✅ Stored email: {email.subject}")
            slack_msg = f"📬 *New Email Received!*\n*Subject:* {email.subject}\n*From:* {email.sender}"
            send_slack_message(message=slack_msg)
    session.commit()
    session.close()

def mark_email_as_read(service, msg_id):
    service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()
    print(f"📭 Marked email {msg_id} as read")

def auto_reply_unread_emails(gmail_service, calendar_service):
    session = SessionLocal()
    emails = session.query(Email).all()

    for email in emails:
        if not is_human_sender(email.sender):
            print(f"🤖 Ignored bot/newsletter sender: {email.sender}")
            continue

        reply = generate_reply(email.body)

        if reply and "Draft generation failed" not in reply and "error" not in reply.lower():
            send_email(gmail_service, email.sender, f"Re: {email.subject}", reply)
            print(f"✅ Auto-reply sent to {email.sender} for email {email.id}")
            mark_email_as_read(gmail_service, email.id)
        else:
            print(f"📝 No auto-reply sent for email {email.id}")
    session.close()

def demo_llm_integration(calendar_service):
    session = SessionLocal()
    email = session.query(Email).order_by(Email.date.desc()).first()
    if not email:
        print("⚠️ No email found in database.")
        return

    print(f"\n📬 Email Subject: {email.subject}")
    print(f"\n📝 Email Body:\n{email.body}\n")

    summary = summarize_email(email.body)
    print("🔍 === Summary ===")
    print(summary)

    reply = generate_reply(email.body)
    print("\n✉️ === Draft Reply ===")
    print(reply)

    send_slack_message(f"🧠 *Summary of:* {email.subject}\n{summary}")

    question = extract_question_from_email(email.body)
    if question:
        print(f"\n❓ Question Detected: {question}")
        search_results = search_web_duckduckgo(question)
        print("🌐 === DuckDuckGo Search Results ===")
        print(search_results)
        slack_info = f"🔍 *Answer Found for:* {question}\n{search_results[:500]}..."
        send_slack_message(message=slack_info)

    keywords_for_calendar = ["interview", "meeting", "date", "time", "schedule", "appointment", "call", "event", "calendar", "reminder"]
    if any(keyword in email.body.lower() for keyword in keywords_for_calendar):
        print("\n🗓️ Looking for meeting details in email...")
        email_date = email.date or datetime.now()
        parsed_dt = extract_meeting_datetime(email.body, email_received_date=email_date)

        if parsed_dt:
            event_start_time = parsed_dt.replace(second=0, microsecond=0, tzinfo=gettz("Asia/Kolkata"))
            event_start_str = event_start_time.isoformat()
            meeting_summary = generate_event_title(email.body)
            event_link = create_event(calendar_service, meeting_summary, event_start_str)

            if event_link:
                print("\n📅 === Calendar Event Created ===")
                print(event_link)
                slack_msg = (
                    f"📅 *Event Scheduled!*\n"
                    f"*Title:* {meeting_summary}\n"
                    f"🕒 *Time:* {event_start_str}\n"
                    f"🔗 <{event_link}|View Event>"
                )
                send_slack_message(message=slack_msg)
            else:
                send_slack_message(f"⚠️ Failed to create event for: {email.subject}")
        else:
            print("⚠️ No valid date/time found.")
            send_slack_message(f"⚠️ Couldn't extract datetime for: {email.subject}\n\n{email.body[:300]}...")

    session.close()

if __name__ == '__main__':
    init_db()
    gmail_service, calendar_service = authenticate_google_services()
    fetch_and_store_emails(gmail_service)
    auto_reply_unread_emails(gmail_service)
    demo_llm_integration(calendar_service)
