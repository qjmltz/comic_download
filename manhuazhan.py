import os
import time
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from download import download_images
BASE_URL = "https://www.manhuazhan.com"
HEADERS = {'User-Agent': 'Mozilla/5.0'}
CUSTOM_COOKIE = None  # 用于存储cookie字符串

def set_cookie(cookie_str):
    """设置全局Cookie，自动添加到请求和Playwright上下文中"""
    global CUSTOM_COOKIE
    CUSTOM_COOKIE = cookie_str
    HEADERS["Cookie"] = cookie_str

def get_chapter_links(comic_id):
    url = f"{BASE_URL}/comic/{comic_id}"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        raise RuntimeError(f"获取章节失败：{url}，状态码：{resp.status_code}")
    soup = BeautifulSoup(resp.text, "lxml")
    a_tags = soup.select("div.d-player-list a")
    chapters = []
    for a in a_tags:
        href = a.get('href')
        title = a.text.strip().replace(":", "：").replace("?", "？")
        if href and title:
            chapters.append((BASE_URL + href, title))
    return chapters

def get_comic_name(comic_id):
    url = f"{BASE_URL}/comic/{comic_id}"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        raise RuntimeError(f"获取漫画主页失败：{url}，状态码：{resp.status_code}")
    soup = BeautifulSoup(resp.text, "lxml")
    # 取 <div class="d-name"> 里的 <h1>文本作为漫画名称
    h1_tag = soup.select_one("div.d-name h1")
    if h1_tag:
        name = h1_tag.text.strip()
        # 防止文件夹名里有非法字符，替换或过滤
        invalid_chars = '<>:"/\\|?*'
        for c in invalid_chars:
            name = name.replace(c, '_')
        return name
    else:
        raise RuntimeError("未能从主页获取漫画名称")

def get_images_by_playwright(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        if CUSTOM_COOKIE:
            cookies = []
            for kv in CUSTOM_COOKIE.split(";"):
                if "=" in kv:
                    name, value = kv.strip().split("=", 1)
                    cookies.append({
                        "name": name,
                        "value": value,
                        "domain": ".manhuazhan.com",
                        "path": "/"
                    })
            context.add_cookies(cookies)

        page = context.new_page()
        page.goto(url)

        max_scrolls = 100
        scrolls = 0
        prev_height = 0
        while scrolls < max_scrolls:
            height = page.evaluate("document.body.scrollHeight")
            if height == prev_height:
                break
            page.evaluate(f"window.scrollTo(0, {height});")
            time.sleep(1)
            prev_height = height
            scrolls += 1

        time.sleep(2)
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "lxml")
    imgs = soup.select("#ChapterContent img.lazy")
    img_urls = []
    for img in imgs:
        url = img.get("data-src") or img.get("src")
        if url and not url.endswith("lazyload.gif"):
            img_urls.append(url)
    return img_urls



def download_chapter(url, title, save_root):
    print(f"\n📖 下载章节《{title}》")
    folder = os.path.join(save_root, title)
    img_urls = get_images_by_playwright(url)
    if not img_urls:
        print("⚠️ 无图片链接")
        return

    download_images(img_urls, folder, HEADERS)

# import os
# import time
# import requests
# from bs4 import BeautifulSoup
# from playwright.sync_api import sync_playwright
#
# BASE_URL = "https://www.manhuazhan.com"
# HEADERS = {'User-Agent': 'Mozilla/5.0'}
#
# def get_chapter_links(comic_id):
#     url = f"{BASE_URL}/comic/{comic_id}"
#     resp = requests.get(url, headers=HEADERS)
#     soup = BeautifulSoup(resp.text, "lxml")
#
#     a_tags = soup.select("div.d-player-list a")
#     chapters = []
#     for a in a_tags:
#         href = a.get('href')
#         title = a.text.strip().replace(":", "：").replace("?", "？")
#         if href and title:
#             chapters.append((BASE_URL + href, title))
#     return chapters
#
# def get_images_by_playwright(url):
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)  # headless=False 可观察浏览器动作
#         page = browser.new_page()
#         page.goto(url)
#
#         max_scrolls =100 # 最大滚动次数，防止死循环
#         scrolls = 0
#         prev_height = 0
#
#         while scrolls < max_scrolls:
#             height = page.evaluate("document.body.scrollHeight")
#             if height == prev_height:
#                 break
#             page.evaluate(f"window.scrollTo(0, {height});")
#             time.sleep(1)
#             prev_height = height
#             scrolls += 1
#
#         # 额外等待图片加载
#         time.sleep(2)
#
#         html = page.content()
#         browser.close()
#
#     soup = BeautifulSoup(html, "lxml")
#     imgs = soup.select("#ChapterContent img.lazy")
#
#     img_urls = []
#     for img in imgs:
#         url = img.get("data-src") or img.get("src")
#         if url and url != "/template/pc/manhuazhan/images/lazyload.gif":
#             img_urls.append(url)
#     return img_urls
#
# def download_images(img_urls, folder):
#     os.makedirs(folder, exist_ok=True)
#     for idx, img_url in enumerate(img_urls, 1):
#         ext = img_url.split('.')[-1].split('?')[0]
#         fname = os.path.join(folder, f"{idx:03d}.{ext}")
#         try:
#             img_data = requests.get(img_url, headers=HEADERS, timeout=15).content
#             with open(fname, 'wb') as f:
#                 f.write(img_data)
#             print(f"  ✓ 下载第 {idx} 张图 → {fname}")
#         except Exception as e:
#             print(f"  × 下载失败: 第 {idx} 张图 → {img_url}，错误: {e}")
#
# def download_chapter(url, title, save_root):
#     print(f"\n开始下载《{title}》")
#     img_urls = get_images_by_playwright(url)
#     if not img_urls:
#         print(f"× 未找到图片链接：{url}")
#         return
#     folder = os.path.join(save_root, title)
#     download_images(img_urls, folder)
# def parse_range(chapter_range, total):
#     if chapter_range == "all":
#         return list(range(total))
#     elif "-" in chapter_range:
#         start, end = map(int, chapter_range.split("-"))
#         return list(range(start - 1, min(end, total)))  # 转为下标
#     else:
#         idx = int(chapter_range) - 1
#         return [idx] if 0 <= idx < total else []
# def crawl(comic_id, save_dir="./downloads", chapter_range="all"):
#     chapters = get_chapter_links(comic_id)
#     total = len(chapters)
#     selected_indexes = parse_range(chapter_range, total)
#
#     print(f"共找到 {total} 章，准备下载索引: {selected_indexes}")
#     for i in selected_indexes:
#         url, title = chapters[i]
#         download_chapter(url, title, os.path.join(save_dir, comic_id))
#
# if __name__ == "__main__":
#     crawl("235514", "manhuazhan", chapter_range="158-220")