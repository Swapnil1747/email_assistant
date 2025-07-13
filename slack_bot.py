import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()  # Load env variables

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

client = WebClient(token=SLACK_BOT_TOKEN)

def send_slack_message(message: str, channel: str = SLACK_CHANNEL_ID):
    try:
        response = client.chat_postMessage(channel=channel, text=message)
        print(f"✅ Slack message sent.")
        return response
    except SlackApiError as e:
        print(f"❌ Slack API Error: {e.response['error']}")
        return None
