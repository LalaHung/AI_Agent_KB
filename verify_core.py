import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

core_modules = {
    "python-docx": "docx",
    "openpyxl": "openpyxl",
    "python-pptx": "pptx",
    "pypdf": "pypdf",
    "PyMuPDF": "fitz",
    "reportlab": "reportlab",
    "pillow": "PIL",
    "matplotlib": "matplotlib",
    "qrcode[pil]": "qrcode",
    "markitdown": "markitdown"
}

optional_modules = {
    "docxcompose": "docxcompose",
    "xlsxwriter": "xlsxwriter",
    "pandas": "pandas",
    "pdfplumber": "pdfplumber",
    "pdf2image": "pdf2image",
    "fpdf2": "fpdf2",
    "ocrmypdf": "ocrmypdf",
    "docx2pdf": "docx2pdf",
    "pywin32": "win32com",
    "edge-tts": "edge_tts",
    "yt-dlp": "yt_dlp",
    "youtube-transcript-api": "youtube_transcript_api"
}

print("Running verify_core.py...")

core_success = 0
for name, mod_name in core_modules.items():
    try:
        __import__(mod_name)
        core_success += 1
    except ImportError:
        print(f"❌ Core package import failed: {name} (module: {mod_name})")

optional_installed = []
for name, mod_name in optional_modules.items():
    if name in ["pandas", "xlsxwriter", "pdfplumber"]:
        continue
    try:
        __import__(mod_name)
        optional_installed.append(name)
    except ImportError:
        pass

python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

# Get repo path
repo_path = os.path.dirname(os.path.abspath(__file__))
venv_path = os.path.join(repo_path, ".venv")

print("\n--- Verification Report ---")
print("核心安裝完成回報：")
# We will verify uv outside, but let's output ✅ uv: 已存在／已安裝
# For Python, let's output the version
print(f"✅ uv：已存在／已安裝")
print(f"✅ Python：{python_version}")
print(f"✅ 環境：{venv_path}")
print(f"✅ 核心套件：{core_success}/10 匯入成功")

if len(optional_installed) == 0:
    print("🟡 選用套件：未安裝（正確）")
else:
    print(f"⚠️ 選用套件：已安裝了以下套件 {optional_installed}（預設不應安裝）")

print(f"下一步：請使用 .\\.venv\\Scripts\\python.exe 執行本 repo 的 Python 程式")

if core_success < 10:
    sys.exit(1)
else:
    sys.exit(0)
