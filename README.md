# Comic_download




## 📖 项目概述

一个基于 Python 的漫画下载工具，用于抓取指定漫画网站的章节列表与原始图片资源。

项目通过解析网页结构获取漫画标题、章节信息与图片直链，支持 Cookie 登录状态（如 VIP 账号），可完整下载包含付费章节在内的全部内容。整体架构保持模块化设计，便于后续站点适配与维护。



### 🛠 技术栈
- Python 3
- requests
- BeautifulSoup4



## 🚀 快速开始

### 环境要求

- Python 3.8+


### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行方式
参数说明：

站点简称 - 漫画 ID - 章节范围 - 登录 Cookie（可选，用于 VIP 章节）

示例：
```bash
 python main.py  zero  21143  --chapter 13-70   --cookie cookie.json
```


### 🗂 项目结构
```bash
comic_download/
├── sites/                  # 站点解析模块
│   ├── manhuazhan.py       # 漫画站
│   ├── zaimanhua.py        # 再漫画
│   └── zero.py             # Zero 漫画
├── download.py             # 图片下载逻辑
├── requirements.txt        # 项目依赖
└── main.py                 # 主程序入口
```

### ⚠️ 免责声明
本项目仅用于 学习与技术研究，请勿用于任何商业用途。
请在使用前确认并遵守目标网站的用户协议及相关法律法规，因使用本项目产生的任何后果由使用者自行承担。





