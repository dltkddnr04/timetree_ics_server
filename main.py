import json
import requests
import datetime
import pytz
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, Response

with open("config.json", "r") as f:
    config = json.load(f)
    ID = config["id"]
    PW = config["pw"]

session_id = None

def signup(id=ID, pw=PW):
    global session_id

    url = "https://timetreeapp.com/api/v1/auth/email/signin"
    headers = {
        "Content-Type": "application/json",
        "X-TimeTreeA": "web/2.1.0/ko",
    }
    data = {
        "uid": id,
        "password": pw,
        "uuid": "0"*32,
    }
    req = requests.put(url, headers=headers, data=json.dumps(data))
    try:
        session_id = req.cookies['_session_id']
        return session_id
    except:
        print(req.text)
        print(req.status_code)
        return None
    
def get_calender_list(session_id):
    url = "https://timetreeapp.com/api/batch"
    data = {
        "ops": [{
            "method": "get",
            "url": "/v1/calendars",
            "params": {
                "since": 0
            }
        }],
        "sequential": True
    }
    headers = {
        "Content-Type": "application/json",
        "X-TimeTreeA": "web/2.1.0/ko",
    }
    cookies = {
        "_session_id": session_id,
    }
    req = requests.post(url, headers=headers, cookies=cookies, data=json.dumps(data))
    if req.status_code == 200:
        calender_list_data = req.json()['results'][0]['body']['calendars']
        calender_list = {}
        for calender in calender_list_data:
            calender_list[calender['alias_code']] = [calender['id'], calender['name']]
        return calender_list
    else:
        get_calender_list(signup())
    
def get_calendar(calendar_id, session_id):
    url = f"https://timetreeapp.com/api/v1/calendar/{calendar_id}/events/sync"
    headers = {
        "X-TimeTreeA": "web/2.1.0/ko",
    }
    cookies = {
        "_session_id": session_id,
    }
    req = requests.get(url, headers=headers, cookies=cookies)
    if req.status_code == 200:
        return json.loads(req.text)
    else:
        get_calendar(calendar_id, signup())

def convert_to_ics(calendar_data, calender_name="TimeTree"):
    ics_data = f"BEGIN:VCALENDAR\nVERSION:2.0\nX-WR-CALNAME:{calender_name}\nX-WR-TIMEZONE:Asia/Seoul\n"
    for event in calendar_data['events']:
        title = event['title']
        note = event['note']
        location = event['location']
        url = event['url']
        start_timezone = event['start_timezone']
        end_timezone = event['end_timezone']
        start_timezone_offset = datetime.datetime.now(pytz.timezone(start_timezone)).utcoffset().total_seconds()
        end_timezone_offset = datetime.datetime.now(pytz.timezone(end_timezone)).utcoffset().total_seconds()
        start_timezone_offset = 9 * 3600
        end_timezone_offset = 9 * 3600
        start_at = datetime.datetime.fromtimestamp(event['start_at'] / 1000).astimezone(datetime.timezone(datetime.timedelta(seconds=int(start_timezone_offset)))).strftime("%Y%m%dT%H%M%S")
        end_at = datetime.datetime.fromtimestamp(event['end_at'] / 1000).astimezone(datetime.timezone(datetime.timedelta(seconds=int(end_timezone_offset)))).strftime("%Y%m%dT%H%M%S")
        if title != "":
            ics_data += f"""BEGIN:VEVENT\n
                            SUMMARY:{title if title != "" else "No Title"}\n
                            DESCRIPTION:{note if note != None else ""}\n
                            DTSTART;TZID={start_timezone}:{start_at}\n
                            DTEND;TZID={end_timezone}:{end_at}\n
                            LOCATION:{location if location != None else ""}\n
                            URL;VALUE=URI:{url if url != None else ""}\n
                            END:VEVENT\n"""
    ics_data += "END:VCALENDAR"
    return ics_data

session_id = signup()
app = FastAPI()

@app.get("/")
def read_root():
    # return calender_list
    calender_list = get_calender_list(session_id)
    list_data = "<ul>"
    for alias_code in calender_list:
        list_data += f"<li><a href=\"{alias_code}.ics\">{calender_list[alias_code][1]}</a></li>"
    list_data += "</ul>"
    return Response(content=list_data, media_type="text/html")

@app.get("/{ALIAS_CODE}.ics")
def read_ics(ALIAS_CODE: str):
    calender_list = get_calender_list(session_id)
    if ALIAS_CODE in calender_list:
        calendar = get_calendar(calender_list[ALIAS_CODE][0], session_id)
        ics_data = convert_to_ics(calendar, calender_list[ALIAS_CODE][1])
        return StreamingResponse(content=ics_data, media_type="text/calendar")
    else:
        return Response(content="No such calendar", media_type="text/plain", status_code=404)