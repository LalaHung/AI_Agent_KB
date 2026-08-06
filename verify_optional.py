import sys
import os
import subprocess

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

optional_modules = {
    "docxcompose": "docxcompose",
    "xlsxwriter": "xlsxwriter",
    "pandas": "pandas",
    "pdfplumber": "pdfplumber",
    "pdf2image": "pdf2image",
    "fpdf2": "fpdf",
    "ocrmypdf": "ocrmypdf",
    "docx2pdf": "docx2pdf",
    "pywin32": "win32com",
    "edge-tts": "edge_tts",
    "yt-dlp": "yt_dlp",
    "youtube-transcript-api": "youtube_transcript_api"
}

# Helper to dynamically add common directories to PATH on Windows for verification
if sys.platform == 'win32':
    extra_paths = []
    # 1. Tesseract OCR
    tesseract_dir = "C:\\Program Files\\Tesseract-OCR"
    if os.path.exists(os.path.join(tesseract_dir, "tesseract.exe")):
        extra_paths.append(tesseract_dir)
        
    # 2. Ghostscript
    gs_root = "C:\\Program Files\\gs"
    if os.path.exists(gs_root):
        for item in os.listdir(gs_root):
            bin_path = os.path.join(gs_root, item, "bin")
            if os.path.exists(os.path.join(bin_path, "gswin64c.exe")):
                extra_paths.append(bin_path)
                break
                
    # 3. Poppler
    localappdata = os.environ.get("LOCALAPPDATA", "")
    winget_links = os.path.join(localappdata, "Microsoft", "WinGet", "Links")
    if os.path.exists(os.path.join(winget_links, "pdftoppm.exe")):
        extra_paths.append(winget_links)
    else:
        winget_packages = os.path.join(localappdata, "Microsoft", "WinGet", "Packages")
        if os.path.exists(winget_packages):
            for folder in os.listdir(winget_packages):
                if "Poppler" in folder:
                    for root, dirs, files in os.walk(os.path.join(winget_packages, folder)):
                        if "pdftoppm.exe" in files:
                            extra_paths.append(root)
                            break
    
    if extra_paths:
        current_path = os.environ.get("PATH", "")
        os.environ["PATH"] = ";".join(extra_paths) + ";" + current_path
        print(f"Added local paths to PATH environment: {extra_paths}")

print("Running verify_optional.py...")

print("\n--- Python Optional Packages Verification ---")
success_count = 0
for name, mod_name in optional_modules.items():
    try:
        __import__(mod_name)
        print(f"✅ Optional package import success: {name} (module: {mod_name})")
        success_count += 1
    except ImportError as e:
        print(f"❌ Optional package import failed: {name} (module: {mod_name}). Error: {e}")

print(f"\nSummary: {success_count}/{len(optional_modules)} optional packages imported successfully.")

print("\n--- System Tools Verification ---")
system_tools = ["tesseract", "pdftoppm", "gswin64c", "ffmpeg"]
for tool in system_tools:
    try:
        if tool == "tesseract":
            res = subprocess.run([tool, "--version"], capture_output=True, text=True, check=True)
            first_line = res.stdout.split("\n")[0]
            print(f"✅ Tesseract OCR found: {first_line}")
        elif tool == "pdftoppm":
            res = subprocess.run([tool, "-v"], capture_output=True, text=True, check=True)
            first_line = res.stderr.split("\n")[0]  # pdftoppm outputs version to stderr
            print(f"✅ Poppler (pdftoppm) found: {first_line}")
        elif tool == "gswin64c":
            res = subprocess.run([tool, "--version"], capture_output=True, text=True, check=True)
            first_line = res.stdout.strip()
            print(f"✅ Ghostscript (gswin64c) found: Version {first_line}")
        elif tool == "ffmpeg":
            res = subprocess.run([tool, "-version"], capture_output=True, text=True, check=True)
            first_line = res.stdout.split("\n")[0]
            print(f"✅ ffmpeg found: {first_line}")
    except FileNotFoundError:
        print(f"❌ System tool NOT found in PATH: {tool}")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ System tool {tool} executed with error or non-zero exit code: {e}")
    except Exception as e:
        print(f"⚠️ System tool {tool} failed check: {e}")

# Check Word COM
print("\n--- Word COM Integration Check ---")
if sys.platform == 'win32':
    try:
        import win32com.client
        word = win32com.client.Dispatch("Word.Application")
        print("✅ MS Word COM Object successfully dispatched.")
        word.Quit()
    except Exception as e:
        print(f"❌ MS Word COM Object dispatch failed: {e}")
else:
    print("ℹ️ Word COM is only checked on Windows.")

if success_count < len(optional_modules):
    sys.exit(1)
else:
    sys.exit(0)
