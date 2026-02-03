import requests
from bs4 import BeautifulSoup
import os
from download import download_images
# from playwright.sync_api import sync_playwright
# import time
headers = {
    "User-Agent": "Mozilla/5.0"
}
cookies = {}


def set_cookie(cookie_input):
    global cookies
    if isinstance(cookie_input, str):
        # 解析类似 "key1=value1; key2=value2" 的字符串
        cookie_dict = {}
        for part in cookie_input.split(";"):
            if "=" in part:
                k, v = part.strip().split("=", 1)
                cookie_dict[k] = v
        cookies = cookie_dict
    elif isinstance(cookie_input, dict):
        cookies = cookie_input


def get_comic_name(comic_id):
    url = f"https://www.zerobywai.com/pc/manga_pc.php?kuid={comic_id}"
    resp = requests.get(url, headers=headers, cookies=cookies)
    if resp.status_code != 200:
        raise Exception("获取页面失败")

    soup = BeautifulSoup(resp.text, "html.parser")

    # 新标题位置
    name_tag = soup.select_one("h1.text-2xl")
    if not name_tag:
        raise Exception("未找到漫画名")

    # 处理 <br>，并去掉多余说明
    raw_title = name_tag.get_text(separator="\n").strip()
    title_lines = [line.strip() for line in raw_title.split("\n") if line.strip()]

    # 一般第一行就是主标题
    comic_name = title_lines[0]

    return comic_name


def get_chapter_links(comic_id):
    url = f"https://www.zerobywai.com/pc/manga_pc.php?kuid={comic_id}"
    resp = requests.get(url, headers=headers, cookies=cookies)
    if resp.status_code != 200:
        raise Exception(f"章节页面加载失败：{resp.status_code}")

    soup = BeautifulSoup(resp.text, "html.parser")
    chapter_links = []

    for a in soup.select('a[href*="manga_read_pc.php?zjid="]'):
        href = a.get("href")
        title = a.text.strip()

        if not href or not title:
            continue

        # 补全为绝对地址
        full_url = "https://www.zerobywai.com/pc/" + href.lstrip("/")

        chapter_links.append((full_url, f"第{title}话"))

    if not chapter_links:
        raise Exception("未找到任何章节链接，页面结构可能再次变化")

    return chapter_links


def download_chapter(url, title, save_root):
    folder = os.path.join(save_root, title)
    print(f"\n📖 下载章节《{title}》")

    resp = requests.get(url, headers=headers, cookies=cookies)
    if resp.status_code != 200:
        print("❌ 章节页面加载失败")
        return

    soup = BeautifulSoup(resp.text, "html.parser")

    img_urls = []
    for img in soup.select("img.manga-image"):
        src = img.get("src")
        if not src:
            continue

        # 处理 // 开头的协议相对路径
        if src.startswith("//"):
            src = "https:" + src

        img_urls.append(src)

    if not img_urls:
        print("⚠️ 没有找到有效图片")
        return

    download_images(img_urls, folder, headers)