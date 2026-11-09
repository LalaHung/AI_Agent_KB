import sys
import os
import re
import argparse
import yt_dlp

sys.stdout.reconfigure(encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description="Find missing YouTube videos by comparing channel videos with local list")
    parser.add_argument("--channel", required=True, help="YouTube channel URL")
    parser.add_argument("--input", default="video_list.md", help="Existing video list file")
    parser.add_argument("--keywords", default="", help="Comma-separated keywords to filter")
    args = parser.parse_args()

    existing_ids = set()
    if os.path.exists(args.input):
        with open(args.input, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    m = re.search(r'(?:v=|youtu\.be/)([\w-]+)', line)
                    if m:
                        existing_ids.add(m.group(1))

    print(f"Loaded {len(existing_ids)} existing video IDs from {args.input}")

    keywords = [k.strip().lower() for k in args.keywords.split(",") if k.strip()]

    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
        'skip_download': True
    }

    base_channel = args.channel.rstrip('/')
    targets = [f"{base_channel}/videos", f"{base_channel}/streams"]

    all_entries = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for t in targets:
            print(f"Scanning {t}...")
            try:
                res = ydl.extract_info(t, download=False)
                if 'entries' in res:
                    for e in res['entries']:
                        if e:
                            all_entries.append(e)
            except Exception as ex:
                print(f"Warning scanning {t}: {ex}")

    missing = []
    seen = set()
    for item in all_entries:
        vid_id = item.get('id')
        if not vid_id or vid_id in seen:
            continue
        seen.add(vid_id)

        title = item.get('title', '')
        url = f"https://www.youtube.com/watch?v={vid_id}"

        if keywords:
            title_lower = title.lower()
            if not any(k in title_lower for k in keywords):
                continue

        if vid_id not in existing_ids:
            missing.append((title, url))

    print(f"\nFound {len(missing)} missing videos:")
    for t, u in missing:
        print(f"- {t} -> {u}")

if __name__ == "__main__":
    main()
