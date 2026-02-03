import argparse
import importlib
import os
import json

def parse_chapter_range(chap_input, total_count):
    if chap_input == "all":
        return list(range(total_count))
    elif "-" in chap_input:
        start, end = map(int, chap_input.split("-"))
        return list(range(start - 1, min(end, total_count)))
    else:
        idx = int(chap_input) - 1
        return [idx] if 0 <= idx < total_count else []

def crawl(comic_id, site_module, chapter_range="all", save_dir="./downloads", cookies=None):
    # 如果网站模块支持设置 cookie，则调用
    if cookies and hasattr(site_module, "set_cookie"):
        site_module.set_cookie(cookies)

    # 尝试获取漫画名称，失败就用comic_id
    try:
        comic_name = site_module.get_comic_name(comic_id)
        print(f"🎉 获取漫画名称成功：{comic_name}")
    except Exception as e:
        print(f"⚠️ 获取漫画名称失败，使用漫画ID代替: {comic_id}\n错误: {e}")
        comic_name = comic_id

    chapters = site_module.get_chapter_links(comic_id)
    total = len(chapters)
    indexes = parse_chapter_range(chapter_range, total)

    print(f"📚 共 {total} 章，准备下载 {len(indexes)} 章：{[i+1 for i in indexes]}")

    for i in indexes:
        url, title = chapters[i]
        print(f"📥 下载第 {i+1} 章 - {title}")
        # 用漫画名称作为文件夹名
        site_module.download_chapter(url, title, os.path.join(save_dir, comic_name))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🧲 漫画下载器")
    parser.add_argument("site", help="网站代号，例如 manhuazhan")
    parser.add_argument("comic_id", help="漫画 ID，例如 235514")
    parser.add_argument("--chapter", default="all", help="下载章节编号（例如 all 或 8 或 8-60）")
    parser.add_argument("--cookie", default=None, help="Cookie 字符串或 JSON 文件路径")
    parser.add_argument("--save_dir", default="./downloads", help="保存目录")

    args = parser.parse_args()

    # 动态导入模块
    try:
        site_module = importlib.import_module(f"sites.{args.site}")
    except ModuleNotFoundError:
        print(f"❌ 未找到网站模块：sites.{args.site}")
        exit(1)

    # 解析 Cookie
    cookies = None
    if args.cookie:
        if os.path.exists(args.cookie):
            try:
                with open(args.cookie, "r", encoding="utf-8") as f:
                    parsed = json.load(f)
                    # 支持浏览器导出的 list[dict]
                    if isinstance(parsed, list):
                        cookies = {item["name"]: item["value"] for item in parsed if "name" in item and "value" in item}
                        print(f"✅ 成功读取 cookie 文件（浏览器导出格式），共 {len(cookies)} 条")
                    elif isinstance(parsed, dict):
                        cookies = parsed
                        print(f"✅ 成功读取 cookie 文件（字典格式），共 {len(cookies)} 条")
                    else:
                        print(f"⚠️ 无法识别的 cookie 文件格式：{args.cookie}")
            except Exception as e:
                print(f"❌ 读取 cookie 文件失败：{e}")
        else:
            # 直接传入的是 cookie 字符串
            cookies = args.cookie
            print(f"✅ 使用命令行传入的 cookie 字符串")

    else:
        print("ℹ️ 未提供 cookie，将以游客身份访问")

    crawl(args.comic_id, site_module, args.chapter, args.save_dir, cookies)