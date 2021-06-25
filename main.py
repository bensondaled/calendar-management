##
from util import *
import json
from auth import get_calendar_service

with open('private.json', 'r') as f:
    priv = json.load(f)
src = priv['src_names']
strip = priv['strip_strs']
save_to = priv['destination_calendar']

service = get_calendar_service()
calendars = get_calendars(service)

try:
    dest_cal = [c for c in calendars if c['summary']==save_to][0]
except:
    dest_cal = None
dest_id = dest_cal['id']
dest_events = get_events(service, dest_cal['id'])

placed = []
for cal in calendars:
    name = cal['summary']
    cid = cal['id']

    events = get_events(service, cid)

    if src[0] in name:
        for event in events:
            base = src[0]
            for s in strip:
                base = base.strip(s)
            eid = create_id(base, event['id'])
            body = copy_event(event)
            body['id'] = eid
            body['colorId'] = 8
            body = add_reminder(body)
            body = append_desc(body, priv['zoom_desc'])
            body['location'] = priv['zoom_link']

            title = body['summary'].lower()
            if 'report' in title or 'grand' in title or 'conference' in title:
                place_event(service, dest_id, eid, body)
                placed.append(eid)

    elif src[1] in name:
        # take everything
        for event in events:
            base = src[1]
            for s in strip:
                base = base.strip(s)
            eid = create_id(base, event['id'])
            body = copy_event(event)
            body['id'] = eid
            #body['colorId'] = 10

            place_event(service, dest_id, eid, body)
            placed.append(eid)

    elif src[2] in name:
        # take all but publish only days where change occurs
        # could do, but skipping for now bc was so easy to do manually
        pass

    else:
        pass

# delete the ones not added/updated
deleted = 0
for ev in dest_events:
    eid = ev['id']
    if eid not in placed:
        service.events().delete(calendarId=dest_id, eventId=eid).execute()
        deleted += 1

print(f'Updated {len(placed)} events (deleted {deleted}).')
##

