import sys
import os
import re
import json
import glob
import yt_dlp

sys.stdout.reconfigure(encoding='utf-8')

# 1. Read all URLs from video_list.md
with open("video_list.md", "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip()]

print(f"Total videos to inspect for GitHub links: {len(urls)}")

# 2. Also check existing subtitle files for any github links
subtitle_gh = {}
for sf in glob.glob("subtitles/*.md"):
    with open(sf, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
        gh_matches = re.findall(r'https?://github\.com/[a-zA-Z0-9_.\-]+/[a-zA-Z0-9_.\-]+(?:\b|/)', text)
        if gh_matches:
            title = os.path.basename(sf).replace(".md", "")
            subtitle_gh[title] = list(dict.fromkeys([m.rstrip('/.') for m in gh_matches]))

# 3. Extract descriptions using yt_dlp
results = []
ydl_opts = {
    'extract_flat': False,
    'quiet': True,
    'skip_download': True,
    'no_warnings': True
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    for idx, url in enumerate(urls, 1):
        try:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', '')
            desc = info.get('description', '')
            
            # find github links in description
            # match github links like https://github.com/user/repo or https://github.com/user/repo/tree/...
            gh_links = re.findall(r'https?://github\.com/[a-zA-Z0-9_.\-]+(?:/[a-zA-Z0-9_.\-]+)*(?:[^\s\)\"\'>]*)?', desc)
            clean_links = []
            for gl in gh_links:
                gl = gl.rstrip('.,;:)!?"\'')
                if gl not in clean_links and gl != "https://github.com":
                    clean_links.append(gl)
            
            if clean_links:
                results.append({
                    'title': title,
                    'url': url,
                    'github_links': clean_links,
                    'desc_snippet': desc[:300]
                })
                print(f"[{idx}/{len(urls)}] Found GH links in: {title} -> {clean_links}")
            else:
                pass
        except Exception as e:
            print(f"[{idx}/{len(urls)}] Error extracting {url}: {e}")

# Generate GITHUB_RESOURCES.md
output_path = "GITHUB_RESOURCES.md"
with open(output_path, "w", encoding="utf-8") as f:
    f.write("# 📦 三師爸影片與專案 GitHub 資源彙整清單\n\n")
    f.write("> 本清單自動從 `video_list.md` 中收錄的影片說明欄與教學內容中檢索，整理所有三師爸釋出的 GitHub Repository 專案與相關程式碼連結。\n\n")
    f.write("---\n\n")
    
    # Unique repositories mapping
    all_repos = {}
    for item in results:
        for gh in item['github_links']:
            # Normalize repo root URL if possible
            m = re.match(r'(https?://github\.com/[^/\s]+/[^/\s]+)', gh)
            repo_base = m.group(1) if m else gh
            if repo_base not in all_repos:
                all_repos[repo_base] = {
                    'links': set(),
                    'videos': []
                }
            all_repos[repo_base]['links'].add(gh)
            all_repos[repo_base]['videos'].append((item['title'], item['url']))

    f.write("## 🌟 核心開源專案與 Repository 彙整\n\n")
    for repo, data in sorted(all_repos.items()):
        f.write(f"### 🔗 [{repo}]({repo})\n\n")
        f.write("**相關教學影片**：\n")
        seen_vid = set()
        for vtitle, vurl in data['videos']:
            if vurl not in seen_vid:
                seen_vid.add(vurl)
                f.write(f"- [{vtitle}]({vurl})\n")
        f.write("\n")

    f.write("---\n\n")
    f.write("## 📑 依影片明細索引\n\n")
    for item in results:
        f.write(f"### [{item['title']}]({item['url']})\n\n")
        f.write("**影片中提供的 GitHub 連結：**\n")
        for gl in item['github_links']:
            f.write(f"- [{gl}]({gl})\n")
        f.write("\n")

print(f"Finished! Written to {output_path}")
