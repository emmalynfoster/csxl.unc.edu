import datetime
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

SERVICE_ACCOUNT_FILE = 'csxl-academic-advising-feature.json'
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def upcoming_events(calendar_id, creds):
    service = build("calendar", "v3", credentials=creds)

    # Call the Calendar API
    # now = datetime.datetime.now()  # 'Z' indicates UTC time
    print("Getting the upcoming 10 events")
    events_result = (
        service.events()
        .list(
            calendarId=calendar_id,
            # timeMin=now,
            maxResults=10,
            # singleEvents=True,
            # orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      print("No upcoming events found.")
      return

    # Prints the start and name of the next 10 events
    for event in events:
      start = event["start"].get("dateTime", event["start"].get("date"))
      end = event["end"].get("dateTime", event["start"].get("date"))
      print(f' Start time: {start}, End time: {end} {event["summary"]} - {event["description"]}')


if __name__ == '__main__':
   
   creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

   upcoming_events('79cf1dc8d6030991225a497903d6698cfd411a5317f16d78431f65f851124498@group.calendar.google.com', creds)