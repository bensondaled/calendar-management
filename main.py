##
from contextlib import redirect_stderr
logfile = './log.txt'

with open(logfile, 'a') as stderr, redirect_stderr(stderr):

    import json
    import logging, sys
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

        if src[1] in name: #src[0] is not useful this year 2022, see priv for details
            for event in events:
                base = src[1]
                for s in strip:
                    base = base.replace(s, '')
                eid = create_id(base, event['id'])
                body = copy_event(event)
                body['id'] = eid
                body = append_desc(body, update_msg)
                title_raw = body['summary']
                title = title_raw.lower()

                if 'call' in title or 'dac' in title or '1pm' in title:
                    body = truncate_event(body) # for events that cross days

                    body['summary'] = body['summary'].strip('Call: ')

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

