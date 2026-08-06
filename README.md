# YouTube Subtitle Knowledge Base Builder for AI Agents

This repository contains automated workflows and scripts designed for AI agents (e.g., Google Antigravity, Claude Code, GPT-CodeX) to build a clean Markdown-based subtitle knowledge base from any YouTube channel. The output is optimized for ingestion into Large Language Models (LLMs) or retrieval systems like **NotebookLM**, **Obsidian**, or vector databases.

> 🤖 **FOR AI AGENTS**: Please read [AGENTS.md](AGENTS.md) for full execution protocols, environment setup, multi-source ingestion pipelines, and daily lifecycle rules.

---

## 🤖 Instructions for AI Agents (System Prompt / Goal)

If you are an AI agent tasked with recreating or updating this knowledge base, refer to [AGENTS.md](AGENTS.md) or follow these core instructions:

1. **Prerequisites Verification**:
   - Ensure **Python 3.x** is installed on the host system.
   - Ensure **yt-dlp** is installed. If not, install it using:
     ```sh
     pip install yt-dlp
     ```
2. **Execute Fetching & Filtering**:
   - Run the Python script `tools/fetch_and_filter.py` with the target YouTube channel URL and desired keywords. This will output a list of target URLs to `video_list.md`.
3. **Execute Subtitle Downloading & Cleaning**:
   - Run `tools/download_and_convert.py`. This script will:
     - Read URLs from `video_list.md`.
     - Download VTT subtitle files using `yt-dlp` (skipping video downloads for speed).
     - Clean VTT formatting (remove timestamps, style tags, and deduplicate scrolling captions).
     - Write the final cleaned text to individual Markdown (`.md`) files in the `subtitles/` directory.

---

## 📁 Repository Structure

* `README.md` - This instruction file.
* `video_list.md` - The generated list of raw YouTube video URLs.
* `subtitles/` - Directory containing the generated clean Markdown subtitle files.
* `tools/`
  * `fetch_and_filter.py` - Fetches all video URLs from a channel and filters them by keywords.
  * `download_and_convert.py` - Downloads subtitles in batch and cleans them into Markdown.

---

## 🛠️ Tool Scripts Detail

### 1. `tools/fetch_and_filter.py`
This script uses `yt-dlp` to fetch all videos from a channel and filters titles based on a set of keywords (case-insensitive).

### 2. `tools/download_and_convert.py`
This script runs a batch download of subtitles for the URLs in `video_list.md`, parses the VTT cues, cleans them up, and saves them as `.md` files.

#### Subtitle Cleaning Algorithm
The script automatically cleans the VTT files by:
1. Stripping all HTML/XML tags (e.g., `<c>`, `</c>`).
2. Deduplicating scroll-accumulation lines (common in YouTube auto-generated subtitles) by checking if consecutive cues are prefixes or suffixes of each other and merging them.

---

## 🚀 How to Run (Quickstart)

```bash
# Step 1: Install dependencies
pip install yt-dlp

# Step 2: Fetch and filter video list
python tools/fetch_and_filter.py --channel "https://www.youtube.com/@sensebar" --keywords "claude,codex,antigravity,opencode,agent"

# Step 3: Download subtitles and convert to clean Markdown
python tools/download_and_convert.py
```

Now, the `subtitles/` folder will be populated with clean Markdown documents, ready for NotebookLM!
