import json
import requests
import datetime
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, Response

TIMEZONE = 9

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
        # start_at = datetime.datetime.fromtimestamp(event['start_at'] / 1000).strftime("%Y%m%dT%H%M%S")
        # end_at = datetime.datetime.fromtimestamp(event['end_at'] / 1000).strftime("%Y%m%dT%H%M%S")
        # actually, it is UTC+0 so we need to convert it to Asia/Seoul
        start_at = datetime.datetime.strptime(start_at, "%Y%m%dT%H%M%S").astimezone(datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=TIMEZONE))).strftime("%Y%m%dT%H%M%S")
        end_at = datetime.datetime.strptime(end_at, "%Y%m%dT%H%M%S").astimezone(datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=TIMEZONE))).strftime("%Y%m%dT%H%M%S")
        if title != "":
            ics_data += f"BEGIN:VEVENT\nDTSTART;TZID=Asia/Seoul:{start_at}\nDTEND;TZID=Asia/Seoul:{end_at}\nSUMMARY:{title}\nEND:VEVENT\n"
    ics_data += "END:VCALENDAR"
    return ics_data

session_id = signup()
app = FastAPI()

@app.get("/")
def read_root():
    return "Hello, World!"

@app.get("/list")
def read_list():
    # return calender_list
    calender_list = get_calender_list(session_id)
    # remove id from calender_list
    for key in calender_list:
        calender_list[key] = calender_list[key][1]
    return calender_list

@app.get("/{ALIAS_CODE}.ics")
def read_ics(ALIAS_CODE: str):
    calender_list = get_calender_list(session_id)
    if ALIAS_CODE in calender_list:
        calendar = get_calendar(calender_list[ALIAS_CODE][0], session_id)
        ics_data = convert_to_ics(calendar, calender_list[ALIAS_CODE][1])
        return StreamingResponse(content=ics_data, media_type="text/calendar")
    else:
        return Response(content="No such calendar", media_type="text/plain", status_code=404)