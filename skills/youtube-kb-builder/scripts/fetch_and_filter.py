import os
import re
import subprocess
import argparse
import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description="Fetch and filter YouTube videos by keywords")
    parser.add_argument("--channel", required=True, help="YouTube channel URL")
    parser.add_argument("--keywords", default="", help="Comma-separated keywords to filter titles (empty for all)")
    parser.add_argument("--output", default="video_list.md", help="Output file path")
    args = parser.parse_args()

    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    print(f"Target Channel: {args.channel}")
    print(f"Keywords: {keywords if keywords else 'ALL'}")

    temp_file = "temp_all_videos.txt"

    print("Fetching channel videos list via yt-dlp...")
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--print", "%(title)s | %(webpage_url)s",
        f"{args.channel.rstrip('/')}/videos"
    ]

    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running yt-dlp: {e}")
        return

    matches = []
    if os.path.exists(temp_file):
        with open(temp_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line or "|" not in line:
                continue
            parts = line.split("|")
            title = parts[0].strip()
            url = parts[1].strip()

            if not keywords:
                matches.append(url)
            else:
                matched_kws = [kw for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', title, re.IGNORECASE) or kw.lower() in title.lower()]
                if matched_kws:
                    matches.append(url)

        os.remove(temp_file)

    if matches:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("\n".join(matches) + "\n")
        print(f"Successfully wrote {len(matches)} filtered video URLs to {args.output}")
    else:
        print("No videos matched the specified criteria.")

if __name__ == "__main__":
    main()
