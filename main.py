import json
import requests
import datetime

with open("config.json", "r") as f:
    config = json.load(f)
    ID = config["id"]
    PW = config["pw"]
    CALENDER_ID = config["calendar_id"]

def signup(id=ID, pw=PW):
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
        return req.cookies['_session_id']
    except:
        print(req.text)
        print(req.status_code)
        return None
    
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

def convert_to_ics(calendar):
    ics_data = "BEGIN:VCALENDAR\nVERSION:2.0\nX-WR-CALNAME:포세이돈\nX-WR-TIMEZONE:Asia/Seoul\n"
    for event in calendar['events']:
        title = event['title']
        start_at = datetime.datetime.fromtimestamp(event['start_at'] / 1000).strftime("%Y%m%dT%H%M%S")
        end_at = datetime.datetime.fromtimestamp(event['end_at'] / 1000).strftime("%Y%m%dT%H%M%S")
        if title != "":
            ics_data += f"BEGIN:VEVENT\nDTSTART;TZID=Asia/Seoul:{start_at}\nDTEND;TZID=Asia/Seoul:{end_at}\nSUMMARY:{title}\nEND:VEVENT\n"
    ics_data += "END:VCALENDAR"
    return ics_data

def save_ics(ics_data):
    with open("calendar.ics", "w") as f:
        f.write(ics_data)

def main():
    calendar = get_calendar(CALENDER_ID, signup())
    ics_data = convert_to_ics(calendar)
    save_ics(ics_data)

if __name__ == "__main__":
    main()