import sys
import os
import re
import yt_dlp

sys.stdout.reconfigure(encoding='utf-8')

# Read existing video_list.md
existing_urls = set()
existing_ids = set()
if os.path.exists("video_list.md"):
    with open("video_list.md", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                existing_urls.add(line)
                # extract id
                m = re.search(r'(?:v=|youtu\.be/)([\w-]+)', line)
                if m:
                    existing_ids.add(m.group(1))

print(f"Current videos in video_list.md: {len(existing_ids)}")

ydl_opts = {
    'extract_flat': True,
    'quiet': True,
    'skip_download': True
}

targets = [
    "https://www.youtube.com/@sensebar/videos",
    "https://www.youtube.com/@sensebar/streams"
]

all_entries = []
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    for url in targets:
        print(f"Extracting playlist from {url}...")
        try:
            res = ydl.extract_info(url, download=False)
            if 'entries' in res:
                for entry in res['entries']:
                    if entry:
                        all_entries.append(entry)
        except Exception as e:
            print(f"Error extracting {url}: {e}")

print(f"Total entries found: {len(all_entries)}")

# Search for antigravity / agy in title
keywords = ["antigravity", "反重力", "agy"]

matched_missing = []
matched_existing = []

seen_ids = set()
for item in all_entries:
    vid_id = item.get('id')
    if not vid_id or vid_id in seen_ids:
        continue
    seen_ids.add(vid_id)
    
    title = item.get('title', '')
    url = f"https://www.youtube.com/watch?v={vid_id}"
    
    # Check if title matches keywords
    title_lower = title.lower()
    is_antigravity = any(kw in title_lower for kw in keywords)
    
    if is_antigravity:
        if vid_id in existing_ids or url in existing_urls:
            matched_existing.append((title, url))
        else:
            matched_missing.append((title, url))

print("\n=== AntiGravity 影片清單比對結果 ===")
print(f"已在清單中的 AntiGravity 影片數量: {len(matched_existing)}")
for t, u in matched_existing:
    print(f" [已收錄] {t} -> {u}")

print(f"\n未在清單中的 AntiGravity 影片數量: {len(matched_missing)}")
for t, u in matched_missing:
    print(f" [未收錄] {t} -> {u}")
