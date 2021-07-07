##
from contextlib import redirect_stderr
logfile = '/Users/bdd/cloud/code/calendar-management/log.txt'

with open(logfile, 'a') as stderr, redirect_stderr(stderr):

    import json
    import logging
    from util import *
    from auth import get_calendar_service

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    logging.info('\nStarting run.')

    update_msg = '\nAuto-updated ' + datetime.now().strftime("%Y-%m-%d %H:%M") 

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
                body = append_desc(body, update_msg)
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
                body = append_desc(body, update_msg)
                #body['colorId'] = 10

                place_event(service, dest_id, eid, body)
                placed.append(eid)

        elif src[2] in name:
            for event in events:
                base = src[2]
                for s in strip:
                    base = base.strip(s)
                eid = create_id(base, event['id'])
                body = copy_event(event)
                body['id'] = eid
                body = append_desc(body, update_msg)
                title = body['summary']
                if title.startswith('PM:') or 'AN' in title or 'SP' in title:
                    place_event(service, dest_id, eid, body)
                    placed.append(eid)

        else:
            pass

    # delete the ones not added/updated
    deleted = 0
    for ev in dest_events:
        eid = ev['id']
        if eid not in placed:
            logging.info(f'Deleting event {ev}')
            service.events().delete(calendarId=dest_id, eventId=eid).execute()
            deleted += 1

    logging.info(f'Updated {len(placed)} events (deleted {deleted}).\n')
##
