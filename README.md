# TimeTree ICS Server
이 프로젝트는 TimeTree의 API를 리버스 엔지니어링, 크롤링하여 ICS 형식으로 변환후 사용자에게 배포하는 웹서버를 구축하는 프로젝트입니다.

## TimeTree API에 대한 간단한 정보
- TimeTree API는 공식적으로 제공되지 않습니다.
- 해당 프로젝트의 코드는 웹버전을 기반으로 작성되었습니다.
- 모든 요청은 **X-TimeTreeA** 헤더를 필요로 하며, **web/2.1.0/ko**를 값으로 가집니다.
- https://timetreeapp.com/api/v1/auth/email/signin을 통해 로그인을 할 수 있습니다.
    - **uid**(이메일), **password**, **uuid**(임의의 UUID)를 요청 바디에 담아 요청을 보내야 합니다.
    - 로그인 후 반환되는 **_session_id**를 쿠키에 추가하여 요청을 보내야 합니다.
- https://timetreeapp.com/api/v1/calendar/{calendar_id}/events/sync를 통해 캘린더 이벤트를 가져올 수 있습니다.
- **_session_id**의 유효시간은 명확하지 않습니다.

## 사용법
0. git clone
```bash
git clone https://github.com/dltkddnr04/timetree_ics_server
cd timetree_ics_server
```
1. python 설치
```bash
sudo apt install python3 python3-pip
```
2. 필수 라이브러리 설치
```bash
pip install -r requirements.txt
```
3. `config.json` 파일 수정
4. 실행
```bash
uvicorn main:app --reload --host=0.0.0.0 --port=80
```