import base64
from email.mime.text import MIMEText
from email.message import EmailMessage

def create_message(to, subject, body):
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_email(service, to, subject, body):
    message = create_message(to, subject, body)
    sent = service.users().messages().send(userId="me", body=message).execute()
    print(f"📤 Sent Email to {to} | ID: {sent['id']}")