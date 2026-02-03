import os
import requests
import hashlib
from urllib.parse import urlparse, parse_qs

BASE_URL = "https://m.zaimanhua.com"
API_URL = "https://manhua.zaimanhua.com/api/v1"
APP_URL = "https://manhua.zaimanhua.com/app/v1"
V4_APP_URL = "https://v4api.zaimanhua.com/app/v1"
ACCOUNT_API = "https://account-api.zaimanhua.com/v1"

# 🔐 写死账号密码（可替换为你自己的）
USERNAME = "123456"
PASSWORD = "123456"

# 创建 session
session = requests.Session()
TOKEN = None

def md5(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def login():
    global TOKEN
    print("🔐 正在登录账号...")
    data = {
        "username": USERNAME,
        "passwd": md5(PASSWORD)
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
    }
    resp = session.post(f"{ACCOUNT_API}/login/passwd", data=data, headers=headers)
    resp.raise_for_status()
    res = resp.json()
    if res["errno"] != 0:
        raise Exception(f"登录失败: {res['errmsg']}")
    TOKEN = res["data"]["user"]["token"]
    print(f"✅ 登录成功，Token: {TOKEN[:10]}...")

    # 设置默认 Authorization
    session.headers.update({
        "Authorization": f"Bearer {TOKEN}",
        "User-Agent": headers["User-Agent"]
    })

def get_comic_name(comic_id):
    if TOKEN is None:
        login()
    url = f"{V4_APP_URL}/comic/detail/{comic_id}"
    resp = session.get(url)
    resp.raise_for_status()
    data = resp.json()["data"]["data"]
    return data["title"]

def get_chapter_links(comic_id):
    if TOKEN is None:
        login()
    url = f"{V4_APP_URL}/comic/detail/{comic_id}"
    resp = session.get(url)
    resp.raise_for_status()
    chapters = resp.json()["data"]["data"]["chapters"]
    chapter_list = chapters[0]["data"]
    result = []
    for idx, item in enumerate(reversed(chapter_list), 1):  # 从 1 开始计数
        chapter_id = item["chapter_id"]
        title = item["chapter_title"]
        chapter_url = f"{BASE_URL}/pages/comic/page?comic_id={comic_id}&chapter_id={chapter_id}"
        result.append((chapter_url, f"{idx:03d}_{title}"))  # 格式化为 001_章节名
    return result

def download_chapter(url, title, save_root):
    from download import download_images

    if TOKEN is None:
        login()

    qs = parse_qs(urlparse(url).query)
    comic_id = qs["comic_id"][0]
    chapter_id = qs["chapter_id"][0]

    api_url = f"{API_URL}/comic1/chapter/detail?channel=pc&app_name=zmh&version=1.0.0&comic_id={comic_id}&chapter_id={chapter_id}"
    resp = session.get(api_url)
    resp.raise_for_status()
    data = resp.json()["data"]["chapterInfo"]
    img_urls = data["page_url"]

    # 调用 download_images，传入 headers
    download_images(img_urls, os.path.join(save_root, title), dict(session.headers))