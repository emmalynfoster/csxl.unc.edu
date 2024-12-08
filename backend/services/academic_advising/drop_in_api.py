import base64
from datetime import datetime, timezone
import json
import re
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from backend.env import getenv
from backend.services.academic_advising.establish_credentials import getcredentials


#  python3 -m pip install python-dateutil <-- required dependency
from dateutil.relativedelta import relativedelta
import urllib

# grabbing the events from today -> 6 months from now every time the webhook notifies of our reocurring script
# drop table first

SERVICE_ACCOUNT = getcredentials()

# Create the credentials object from the dictionary
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
creds = Credentials.from_service_account_info(SERVICE_ACCOUNT, scopes=SCOPES)

def get_events(calendar_id, creds):  # type: ignore
    """Calls events().list to retrieve all events within a 6 month range from today to populate database

    Args:
        calendar_id: the id of the calendar, to be stored as a credential
        creds: required credentials to make the API call

    Returns:
        events_result: API response
    """
    service = build("calendar", "v3", credentials=creds)

    now = datetime.now(timezone.utc).isoformat()
    six_months_later = (
        datetime.now(timezone.utc) + relativedelta(months=6)
    ).isoformat()

    # Call the Calendar API
    print("Getting the upcoming events from today to six months later")
    events_result = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=now,
            timeMax=six_months_later,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    # print(f'{events_result}')
    return events_result


def upcoming_events(events_result):  # type: ignore
    """Parses events_result API response into a dictionary for processing and inserting into database

    Args:
        event_result: Returned response from get_events()

    Returns:
        events_dict: dictionary with each event
    """
    events = events_result.get("items", [])

    if not events:
        print("No upcoming events found.")
        return {}

    # Dictionary to store event details
    events_dict = {}

    for event in events:
        event_id = event["id"]

        original_summary = event.get("summary", "")
        link = event.get("htmlLink")

        # Clean and normalize the event title
        original_summary = re.sub(
            r"[-–—]+", " ", original_summary
        )  # Replace multiple dashes with a space
        cleaned_summary = re.sub(
            r"[^\w\s-]", "", original_summary
        ).strip()  # Remove special characters
        cleaned_summary = re.sub(r"\s+", " ", cleaned_summary)  # Remove extra spaces

        # Parse start and end times
        start = event["start"].get("dateTime", event["start"].get("date"))
        end = event["end"].get("dateTime", event["end"].get("date"))

        # Convert to datetime objects for better handling
        start_datetime = datetime.fromisoformat(start).replace(tzinfo=None)
        end_datetime = datetime.fromisoformat(end).replace(tzinfo=None)

        # Populate the dictionary
        events_dict[event_id] = {
            "summary": cleaned_summary,
            "start": start_datetime,
            "end": end_datetime,
            "link": link,
        }

    # print(f'{events_dict}')
    return events_dict
