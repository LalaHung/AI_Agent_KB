import sys
import os
import re
import yt_dlp

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('tools'))
from download_and_convert import parse_vtt

new_videos = [
    "https://www.youtube.com/watch?v=hBEXshEnWRY",
    "https://www.youtube.com/watch?v=5jj4W5XU3nw",
    "https://www.youtube.com/watch?v=pI2nitfc8Tg",
    "https://www.youtube.com/watch?v=QOsWBcs1RAQ",
    "https://www.youtube.com/watch?v=8INcIHIYnMA",
    "https://www.youtube.com/watch?v=NpBfe9LfEUA",
    "https://www.youtube.com/watch?v=wH2tXQY5MOU",
    "https://www.youtube.com/watch?v=agQOf09rXlk",
    "https://www.youtube.com/watch?v=sB5RrZkOUuU",
    "https://www.youtube.com/watch?v=TU_Upg_whtk"
]

# 1. Update video_list.md
existing_lines = []
if os.path.exists("video_list.md"):
    with open("video_list.md", "r", encoding="utf-8") as f:
        existing_lines = [l.strip() for l in f if l.strip()]

existing_set = set(existing_lines)
added_count = 0
for v in new_videos:
    if v not in existing_set:
        existing_lines.append(v)
        existing_set.add(v)
        added_count += 1

with open("video_list.md", "w", encoding="utf-8") as f:
    f.write("\n".join(existing_lines) + "\n")

print(f"Updated video_list.md: added {added_count} new videos, total {len(existing_lines)} videos.")

# 2. Download subtitles and fetch descriptions for GitHub link extraction
sub_dir = "subtitles"
os.makedirs(sub_dir, exist_ok=True)

github_results = {}

ydl_opts = {
    'skip_download': True,
    'writesubtitles': True,
    'writeautomaticsub': True,
    'subtitleslangs': ['zh-Hant', 'zh-TW', 'zh-HK', 'zh'],
    'subtitlesformat': 'vtt',
    'outtmpl': f'{sub_dir}/%(title)s.%(ext)s',
    'quiet': True,
    'no_warnings': True
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    for idx, url in enumerate(new_videos, 1):
        print(f"[{idx}/{len(new_videos)}] Processing: {url}")
        try:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Unknown Title')
            desc = info.get('description', '')
            
            # Find github links in description
            gh_links = re.findall(r'https?://github\.com/[a-zA-Z0-9_.\-]+/[a-zA-Z0-9_.\-]+(?:\b|/)', desc)
            gh_links = list(dict.fromkeys([l.rstrip('/.') for l in gh_links]))
            
            github_results[url] = {
                'title': title,
                'github_links': gh_links,
                'description': desc
            }
        except Exception as e:
            print(f"Error processing {url}: {e}")

# 3. Convert all pending downloaded VTTs to Markdown
import glob
vtts = glob.glob(os.path.join(sub_dir, "*.vtt"))
print(f"Found {len(vtts)} VTT files to convert...")

for filepath in vtts:
    filename = os.path.basename(filepath)
    parts = filename.split('.')
    if len(parts) >= 3:
        title = '.'.join(parts[:-2])
    else:
        title = parts[0]
    
    cleaned = parse_vtt(filepath)
    safe_title = re.sub(r'[\\/*?:"<>|]', '', title)
    out_path = os.path.join(sub_dir, f"{safe_title}.md")
    
    content = f"# {title}\n\n> 原始字幕檔案：`{filename}`\n\n---\n\n{cleaned}\n"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(content)
        
    os.remove(filepath)
    print(f"Converted: {safe_title}.md")

print("All subtitle downloads and conversions finished!")
