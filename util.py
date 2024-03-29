from datetime import datetime, timedelta
import dateutil.parser

def get_calendars(service):
    calendars_result = service.calendarList().list().execute()
    calendars = calendars_result.get('items', [])
    return calendars

def get_events(service, calendar_id):
    start = datetime.utcnow() - timedelta(days=3)
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
    eid = base + id.replace('_', '')
    for ch in eid:
        eid = eid.replace(ch, ch.lower())
    eid = eid.replace('w', 'avva')
    eid = eid.replace('x', 'avvva')
    eid = eid.replace('y', 'avvvva')
    eid = eid.replace('z', 'avvvvva')
    return eid

def place_event(service, dest_id, eid, body):
    try:
        service.events().update(calendarId=dest_id, eventId=eid, body=body).execute()
    except:
        service.events().insert(calendarId=dest_id, body=body).execute()

def truncate_event(body, n_hrs=1):
    if 'end' not in body or 'start' not in body:
        return body

    start = body['start']['dateTime']
    end = body['end']['dateTime']
    
    if not start.endswith('Z') and end.endswith('Z'):
        print('Not truncating event b/c not UTC so unsafe')
        return body

    start = dateutil.parser.parse(start)
    end = dateutil.parser.parse(end)
    
    newmin = start.minute + 59
    if newmin > 59:
        newmin = start.minute+5
    new_end = end.replace(day=start.day, month=start.month, hour=start.hour, minute=newmin)
    new_end = new_end.strftime('%Y-%m-%dT%H:%M:%S') 

    body['end']['dateTime'] = new_end

    return body

