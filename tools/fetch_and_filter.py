import os
import re
import subprocess
import argparse
import sys

# Reconfigure stdout to support UTF-8 print
sys.stdout.reconfigure(encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description="Fetch and filter YouTube videos by keywords")
    parser.add_argument("--channel", default="https://www.youtube.com/@sensebar", help="YouTube channel URL")
    parser.add_argument("--keywords", default="claude,codex,antigravity,opencode,agent", help="Comma-separated keywords to filter titles")
    parser.add_argument("--output", default="video_list.md", help="Output file path")
    args = parser.parse_args()

    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    print(f"Target Channel: {args.channel}")
    print(f"Keywords: {keywords}")

    temp_file = "temp_all_videos.txt"

    # Step 1: Run yt-dlp to get all video titles and URLs
    print("Fetching channel videos list (this may take a minute)...")
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--print", "%(title)s | %(webpage_url)s",
        f"{args.channel}/videos"
    ]

    try:
        # We write to a temporary file to handle encoding safety
        with open(temp_file, "w", encoding="utf-8") as f:
            subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running yt-dlp: {e}")
        return

    # Step 2: Read and filter
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

            matched_kws = [kw for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', title, re.IGNORECASE) or kw in title.lower()]
            if matched_kws:
                matches.append(url)

        # Remove temp file
        os.remove(temp_file)

    # Step 3: Write raw URLs to output file
    if matches:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("\n".join(matches) + "\n")
        print(f"Successfully wrote {len(matches)} filtered video URLs to {args.output}")
    else:
        print("No videos matched the specified keywords.")

if __name__ == "__main__":
    main()
