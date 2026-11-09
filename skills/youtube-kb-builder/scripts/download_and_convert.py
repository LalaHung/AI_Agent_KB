import os
import re
import subprocess
import glob
import sys
import argparse

sys.stdout.reconfigure(encoding='utf-8')

def clean_tags(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    return text.strip()

def parse_vtt(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='cp950', errors='ignore') as f:
            lines = f.readlines()

    cues = []
    current_cue = []
    in_header = True
    timestamp_pattern = re.compile(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}')

    for line in lines:
        line = line.strip()
        if in_header:
            if timestamp_pattern.match(line):
                in_header = False
            else:
                continue

        if timestamp_pattern.match(line):
            if current_cue:
                text = " ".join(current_cue).strip()
                cleaned = clean_tags(text)
                if cleaned:
                    cues.append(cleaned)
                current_cue = []
        else:
            if line:
                current_cue.append(line)

    if current_cue:
        text = " ".join(current_cue).strip()
        cleaned = clean_tags(text)
        if cleaned:
            cues.append(cleaned)

    cleaned_cues = []
    for cue in cues:
        cue = cue.strip()
        if not cue:
            continue
        if not cleaned_cues:
            cleaned_cues.append(cue)
            continue
        
        last_cue = cleaned_cues[-1]
        if cue.startswith(last_cue):
            cleaned_cues[-1] = cue
        elif last_cue.endswith(cue):
            continue
        else:
            overlap_found = False
            for i in range(len(last_cue) // 2, len(last_cue)):
                suffix = last_cue[i:]
                if cue.startswith(suffix):
                    combined = last_cue[:i] + cue
                    cleaned_cues[-1] = combined
                    overlap_found = True
                    break
            if not overlap_found:
                cleaned_cues.append(cue)

    return "\n\n".join(cleaned_cues)

def main():
    parser = argparse.ArgumentParser(description="Download and clean YouTube subtitles into Markdown")
    parser.add_argument("--input", default="video_list.md", help="Input URL list file")
    parser.add_argument("--output-dir", default="subtitles", help="Output directory for Markdown files")
    args = parser.parse_args()

    list_file = args.input
    sub_dir = args.output_dir

    if not os.path.exists(list_file):
        print(f"Error: {list_file} not found.")
        return

    with open(list_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f.readlines() if line.strip()]

    print(f"Found {len(urls)} URLs in {list_file}")
    os.makedirs(sub_dir, exist_ok=True)

    print("Downloading subtitles via yt-dlp...")
    cmd = [
        "yt-dlp",
        "--skip-download",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs", "zh-Hant,zh-TW,zh-HK,zh",
        "--sub-format", "vtt",
        "-o", f"{sub_dir}/%(title)s.%(ext)s",
        "-a", list_file
    ]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Subtitles download encountered some warnings/errors, proceeding with conversion: {e}")

    vtt_files = glob.glob(os.path.join(sub_dir, "*.vtt"))
    print(f"Found {len(vtt_files)} VTT subtitle files to process.")

    for filepath in vtt_files:
        filename = os.path.basename(filepath)
        parts = filename.split('.')
        if len(parts) >= 3:
            title = ".".join(parts[:-2])
        else:
            title = parts[0]
            
        cleaned_text = parse_vtt(filepath)
        safe_title = re.sub(r'[\\/*?:"<>|]', '', title)
        md_filepath = os.path.join(sub_dir, f"{safe_title}.md")
        
        md_content = f"# {title}\n\n"
        md_content += f"> 原始字幕檔案：`{filename}`\n\n"
        md_content += "---\n\n"
        md_content += cleaned_text
        
        with open(md_filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        try:
            os.remove(filepath)
        except Exception:
            pass

    print(f"All subtitles processed and saved to {sub_dir}/ successfully!")

if __name__ == "__main__":
    main()
