import sys
import os
import re
import argparse
import yt_dlp

sys.stdout.reconfigure(encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description="Extract GitHub repository links from YouTube video descriptions and subtitles")
    parser.add_argument("--input", default="video_list.md", help="Path to video list file")
    parser.add_argument("--output", default="GITHUB_RESOURCES.md", help="Output Markdown file")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: {args.input} not found.")
        return

    with open(args.input, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    print(f"Inspecting {len(urls)} videos for GitHub repository resources...")

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
                        'github_links': clean_links
                    })
                    print(f"[{idx}/{len(urls)}] Found GH links: {title}")
            except Exception as e:
                print(f"[{idx}/{len(urls)}] Error inspecting {url}: {e}")

    with open(args.output, "w", encoding="utf-8") as f:
        f.write("# 📦 影片與專案 GitHub 資源彙整清單\n\n")
        f.write("> 本清單由 `youtube-kb-builder` 自動檢索影片說明欄與教學內容生成。\n\n---\n\n")
        
        all_repos = {}
        for item in results:
            for gh in item['github_links']:
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

    print(f"Finished! Written to {args.output}")

if __name__ == "__main__":
    main()
