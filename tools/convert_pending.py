import os
import re
import glob
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('tools'))
from download_and_convert import parse_vtt

sub_dir = "subtitles"
vtts = glob.glob(os.path.join(sub_dir, "*.vtt"))

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
    print(f"Successfully converted: {out_path}")
