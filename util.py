from datetime import datetime, timedelta

def get_calendars(service):
    calendars_result = service.calendarList().list().execute()
    calendars = calendars_result.get('items', [])
    return calendars

def get_events(service, calendar_id):
    start = datetime.utcnow() - timedelta(days=1)
    stop = start + timedelta(days=365)
    start, stop = start.isoformat()+'Z', stop.isoformat()+'Z'

    events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=start,
            timeMax=stop,
            maxResults=2500,
            singleEvents=True,
            orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events

def copy_event(e0):
    e = e0.copy()

    e = {k:v for k,v in e.items() if k in ['id', 'summary', 'description', 'start','end','location']}

    return e

def add_reminder(body):
    body['reminders'] = {'useDefault': False,
                         'overrides': [{'method': 'popup',
                                        'minutes': 8}],
                        }

    return body

def append_desc(body, content):
    body['description'] = body.get('description', '') + '\n' + content

    return body

def create_id(base, id):
    return base + id.replace('_', '')

def place_event(service, dest_id, eid, body):
    try:
        service.events().update(calendarId=dest_id, eventId=eid, body=body).execute()
    except:
        service.events().insert(calendarId=dest_id, body=body).execute()

