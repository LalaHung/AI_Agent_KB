---
name: youtube-kb-builder
description: YouTube 頻道教學影片字幕自動化抓取、去重清洗轉 Markdown，以及影片說明欄 GitHub 開源專案雙向索引建構技能。當使用者要求「抓取頻道影片字幕」、「製作 YouTube 知識庫」、「比對缺漏教學影片」、「整理影片中的 GitHub 連結」、「抓取 YouTube 影片說明」時自動載入。
---

# 📺 YouTube 知識庫建構與 GitHub 資源索引技能 (`youtube-kb-builder`)

本技能封裝了 YouTube 頻道教學影片的完整知識庫萃取生命週期，具備四大核心能力：
1. **頻道掃描與關鍵字過濾**：依關鍵字精準抓取指定 YouTube 頻道的影片清單。
2. **批次下載與自研字幕清洗**：下載繁中/中文 VTT 字幕，自動去除時間標籤、去除 HTML tag，並利用滑動窗口算法消除累積式滾動重複語句。
3. **影片說明欄 GitHub 資源萃取**：自動解析所有影片之資訊欄，抓取作者釋出之開源 GitHub Repository，產出雙向對照索引。
4. **頻道差集比對**：比對頻道最新影片/直播與現有清單，精準抓出未收錄之教學集數。

---

## 🛠️ 內部封裝工具與執行指令

本技能所有工具均位於技能目錄的 `scripts/` 下，執行時請優先使用專案或全域之 Python 環境（如 `python` 或 `.\.venv\Scripts\python.exe`）。

### 1. 頻道掃描與關鍵字過濾 (`fetch_and_filter.py`)
依頻道網址與指定關鍵字，產出目標影片 URL 清單檔案（如 `video_list.md`）。

```powershell
python "<SKILL_DIR>/scripts/fetch_and_filter.py" --channel "https://www.youtube.com/@channel_name" --keywords "agent,python,ai" --output "video_list.md"
```

### 2. 字幕批次下載與清洗轉檔 (`download_and_convert.py`)
讀取 URL 清單檔，批次下載繁體/中文 VTT 字幕並自動清洗輸出成 Markdown。

```powershell
python "<SKILL_DIR>/scripts/download_and_convert.py" --input "video_list.md" --output-dir "subtitles"
```

#### 字幕清洗核心算法規則：
- **HTML/格式標記剔除**：移除 `<c>`、`</c>`、`<00:00:00.000>` 等時間標籤與 HTML Entities。
- **滑動重疊字句去重**：針對 YouTube 自動字幕連續 cue 區塊的前綴/後綴重疊進行滾動消除，徹底杜絕 RAG 與向量資料庫的重複垃圾字句。

### 3. GitHub 資源萃取與雙向索引生成 (`extract_github_links.py`)
解析清單中所有影片之說明欄與字幕內文，提取作者提供的 GitHub 倉庫，生成 `GITHUB_RESOURCES.md`。

```powershell
python "<SKILL_DIR>/scripts/extract_github_links.py" --input "video_list.md" --output "GITHUB_RESOURCES.md"
```

### 4. 頻道最新影片差集比對 (`find_missing_videos.py`)
比對頻道所有影片及直播（Streams），精準抓出尚未列入現有清單的集數。

```powershell
python "<SKILL_DIR>/scripts/find_missing_videos.py" --channel "https://www.youtube.com/@channel_name" --input "video_list.md" --keywords "關鍵字"
```

---

## 📋 Agent 實務調用守則

1. **優先讀取清單**：執行前先檢查專案根目錄是否已有 `video_list.md`。
2. **編碼安全**：Windows 環境下一律強制啟用 UTF-8 輸出，避免繁體中文字元在命令列管道中出現亂碼。
3. **無字幕處理原則**：若影片為直播回放（Streams）且無語音字幕軌（僅有 `live_chat`），主動提示使用者並優先使用正式剪輯版。
