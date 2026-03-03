import requests
import time
import random
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re
cookies={
    "SESSDATA":'78102464%2C1780398789%2Cda594%2Ac1CjDuvonFDjqNqCp3o281aSLDH1a-EyaHGd6lX8A_MslhVs8b-KufoiH5pfqre6C9YgsSVkFvQ194LTQ3VXExWWxjVUE2M3BlOE5nTUZwVnRXZ3NyTUxlbGlmUE8zWkFScWRRTkZYNW1HWVROenRnSy10c2RyVUhDb0I2bzUtWHN6QTByTVp3VVJRIIEC',
    "bili_jct":'a42b8818767a0ad8a49f1fafcf7ec7e9',
    'buvid3':'F63A2E41-8505-02EC-E78C-1B953DF67F9437967infoc',
    'sid':'5wayzwiu',
    "innersign": "1",
    "PVID": "1",
    "bili_ticket": "eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjQ5MTY0MDksImlhdCI6MTc2NDY1NzE0OSwicGx0IjotMX0.OAUeb12cjPPegIbBgbFBczoSW0qziE1Hp-iRtit9APU",
    "bili_ticket_expires": "1764916349",
    'buvid4':'7C550BC9-2969-3091-09F7-5F00AD39198840210-025100413-5j8pNPbWiWkaH9UQkk6k1+zuPbQyQDKF4RT/n0VMYxUSVs+ztnXEGj4MpvApAUXK'
}
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Origin": "https://www.bilibili.com",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
}
RETRY_PARAMS = {
    "total": 5,
    "backoff_factor": 2,
    "status_forcelist": [-352,412, 429, 500, 502, 503, 504],
}
def clean_illegal_chars(s):
    illegal_chars = r'[\x00-\x1F\x7F\x80-\x9F\u2000-\u20FF]'
    if isinstance(s, str):
        illegal_chars = r'[\x00-\x1F\x7F\x80-\x9F\u2000-\u20FF]'
        return re.sub(illegal_chars, '', s)
    elif isinstance(s, list):
        return re.sub(illegal_chars, '', ','.join([str(i) for i in s]))
    return s
def create_session():
    session = requests.Session()
    retry = Retry(
        total=RETRY_PARAMS["total"],
        backoff_factor=RETRY_PARAMS["backoff_factor"],
        status_forcelist=RETRY_PARAMS["status_forcelist"],
        respect_retry_after_header=True
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(HEADERS)
    if cookies:
        session.cookies.update(cookies)
    return session
def get_weekly_series_list(session: requests.Session):
    url = "https://api.bilibili.com/x/web-interface/popular/series/list"
    try:
        response = session.get(url, timeout=15)
        data = response.json()
        if data.get("code") == 0:
            series_list = [item["number"] for item in data["data"]["list"]]
            return series_list
    except requests.exceptions.RequestException as e:
        return [0]
def get_weekly_videos(session: requests.Session, series_number: int):
    url = f"https://api.bilibili.com/x/web-interface/popular/series/one?number={series_number}"
    try:
        time.sleep(random.uniform(4.0,8.0))
        response = session.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        data = response.json()
        if data.get("code") == 0:
            config = data["data"]["config"]
            core_data = data["data"]["list"]
            date = config["name"]
            return core_data, date
        else:
            print(data.get("code"))
    except requests.exceptions.RequestException as e:
        return[]
    return []
def get_video_tags(session: requests.Session, bvid: str, max_retries: int = 10):
    url = f"https://api.bilibili.com/x/tag/archive/tags?bvid={bvid}"
    for attempt in range(max_retries):
        try:
            time.sleep(random.uniform(4.0, 5.0))
            response = session.get(url, timeout=15)
            data = response.json()
            description=[]
            if data.get("code") == 0:
                tag_list = data.get("data",[])
                tag_names = [item["tag_name"] for item in tag_list if "tag_name" in item]
                for tag in tag_list:
                    description.append(tag["content"])
                return tag_names,description
        except requests.exceptions.RequestException as e:
            return data.get("code")
    return []

video_bvid=[]
video_ctime=[]

session=create_session()
series_num=get_weekly_series_list(session)
for i in range(len(series_num)):
    print(f'开始{series_num[i]}')
    videos,date=get_weekly_videos(session,series_num[i])

    for video in videos:
        video_bvid.append(video["bvid"])
        video_ctime.append(video["ctime"])
df = pd.DataFrame({"bvid":video_bvid,"ctime":video_ctime})
df.to_excel('F:\\work_code\\video_date.xlsx')

