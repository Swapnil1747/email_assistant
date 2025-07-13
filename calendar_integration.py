from dateparser import parse
from dateparser.search import search_dates
from datetime import timedelta
from googleapiclient.errors import HttpError
from dateutil.tz import gettz  # ✅ For correct timezone handling

def extract_meeting_datetime(text, email_received_date):
    """
    Extracts a datetime object from natural language text using the context of the email's received date.
    """
    settings = {
        'RELATIVE_BASE': email_received_date,
        'PREFER_DATES_FROM': 'future'
    }

    # Use search_dates to find all possible datetime expressions
    results = search_dates(text, settings=settings)
    if results:
        for _, dt in results:
            if dt:
                return dt

    # Fallback if no expressions matched
    return parse(text, settings=settings)


def create_event(calendar_service, summary, event_start_time_str):
    """
    Creates an event in Google Calendar starting at the parsed time with a default 1-hour duration.
    """
    start_dt = parse(event_start_time_str)
    if not start_dt:
        print("⚠️ Could not parse start time.")
        return None

    # Convert to IST (Asia/Kolkata)
    start_dt = start_dt.replace(tzinfo=gettz("Asia/Kolkata"))
    end_dt = start_dt + timedelta(hours=1)

    event = {
        'summary': summary,
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': 'Asia/Kolkata'  # ✅ Proper IST timezone
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': 'Asia/Kolkata'
        },
    }

    try:
        created_event = calendar_service.events().insert(
            calendarId='primary', body=event
        ).execute()

        print(f"📅 Event created: {created_event.get('htmlLink')}")
        return created_event.get('htmlLink')

    except HttpError as error:
        print(f"❌ Calendar Error: {error}")
        return None
