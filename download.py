import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed



def download_single_image(img_url, folder, idx, headers):
    ext = os.path.splitext(img_url.split("?")[0])[1]
    if not ext or len(ext) > 5:
        ext = ".jpg"
    fname = os.path.join(folder, f"{idx:03d}{ext}")

    try:
        resp = requests.get(img_url, headers=headers, timeout=15)
        resp.raise_for_status()
        with open(fname, "wb") as f:
            f.write(resp.content)
        print(f"  ✓ 下载第 {idx} 张图 → {fname}")
    except Exception as e:
        fak_name = os.path.join(folder, f"{idx:03d}.fak")
        print(f"  × 下载失败: 第 {idx} 张图 → {img_url}，错误: {e}")
        with open(fak_name, "wb") as f:
            pass  # 创建空 .fak 文件
        print(f"    → 创建占位文件：{fak_name}")


def download_images(img_urls, folder, headers, max_workers=8):
    os.makedirs(folder, exist_ok=True)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for idx, url in enumerate(img_urls, 1):
            futures.append(executor.submit(download_single_image, url, folder, idx, headers))
        for future in as_completed(futures):
            _ = future.result()  # 捕获异常防止线程池中断
