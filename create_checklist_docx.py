import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def create_document():
    doc = Document()

    # Set page margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Color Palette
    PRIMARY_COLOR = RGBColor(27, 85, 155)    # #1B579B Dark Blue
    SECONDARY_COLOR = RGBColor(53, 126, 199) # #357EC7 Blue
    DARK_TEXT = RGBColor(40, 40, 40)        # Dark Gray text
    CODE_BG = "F4F6F9"
    HEADER_BG = "1B579B"
    ALT_ROW_BG = "F8FAFC"

    # Set default style font
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Microsoft JhengHei'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = DARK_TEXT

    # Document Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run("AntiGravity 新手完整導引與帳號設定 CheckList")
    run_title.font.name = 'Microsoft JhengHei'
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    run_title.font.color.rgb = PRIMARY_COLOR
    p_title.paragraph_format.space_after = Pt(4)

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = p_sub.add_run("AI Agent 環境建置、帳號申請、對外授權與工作流程導引手冊")
    run_sub.font.name = 'Microsoft JhengHei'
    run_sub.font.size = Pt(13)
    run_sub.font.color.rgb = SECONDARY_COLOR
    p_sub.paragraph_format.space_after = Pt(24)

    # Helper function for headings
    def add_heading_1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Microsoft JhengHei'
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = PRIMARY_COLOR
        return p

    def add_heading_2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = 'Microsoft JhengHei'
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = SECONDARY_COLOR
        return p

    def add_code_block(code_text):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        set_cell_background(cell, CODE_BG)
        set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(code_text)
        run.font.name = 'Consolas'
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(30, 30, 30)
        
        # Add space after table
        p_after = doc.add_paragraph()
        p_after.paragraph_format.space_before = Pt(0)
        p_after.paragraph_format.space_after = Pt(6)

    # 1. 簡介
    add_heading_1("📌 1. 說明與適用情境")
    p_intro = doc.add_paragraph(
        "本手冊專為 AntiGravity 使用者設計，用於快速將現有的 AI Agent 工作流程、自動化腳本與工具集復用給新夥伴。"
        "本清單完整收錄了「帳號申請 ➔ 基礎工具安裝 ➔ 腳本建置 ➔ 瀏覽器 OAuth 授權 ➔ AntiGravity 開工」全流程。"
    )
    p_intro.paragraph_format.space_after = Pt(12)

    # 2. 階段一：帳號申請
    add_heading_1("📌 階段一：帳號申請與點選（手動點選註冊）")
    doc.add_paragraph("請在開始建置環境前，先確認完成以下免費服務的帳號註冊：")
    
    checklist_1 = [
        ("Google 帳號", "用於 NotebookLM 知識庫檢索、Firebase 資料庫與 Google Apps Script 存取。"),
        ("GitHub 帳號", "前往 https://github.com 註冊，用於版本控制、CLI 存取與 GitHub Pages 部署。"),
        ("Netlify 帳號 (選用)", "前往 https://netlify.com 用 GitHub 免費登入，用於前端網頁一鍵部署。")
    ]
    for item, desc in checklist_1:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(4)
        run_b = p.add_run(f"☐  {item}：")
        run_b.bold = True
        p.add_run(desc)

    # 3. 階段二：必備軟體安裝
    add_heading_1("📌 階段二：必備基礎軟體安裝（點選安裝檔）")
    doc.add_paragraph("請下載並安裝以下基礎開發工具（均為免費軟體）：")

    checklist_2 = [
        ("Git 版本控制工具", "下載位置：https://git-scm.com （一路點擊 Next 安裝即可）"),
        ("GitHub CLI (gh)", "下載位置：https://cli.github.com （或開 PowerShell 執行 winget install GitHub.cli）"),
        ("Node.js (LTS 版)", "下載位置：https://nodejs.org （用於執行 npx.cmd 及前端套件管理）"),
        ("Obsidian 第二大腦筆記 (選用)", "下載位置：https://obsidian.md （用於同步個人專案駕駛艙筆記）")
    ]
    for item, desc in checklist_2:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(4)
        run_b = p.add_run(f"☐  {item}：")
        run_b.bold = True
        p.add_run(desc)

    # 4. 階段三：一鍵環境建置腳本
    add_heading_1("📌 階段三：一鍵環境建置腳本")
    doc.add_paragraph("請以系統管理員身分開啟 PowerShell，進入專案目錄後執行以下腳本：")
    add_code_block("powershell -ExecutionPolicy Bypass -File .\\install_windows.ps1")
    
    p_script_note = doc.add_paragraph()
    p_script_note.paragraph_format.space_after = Pt(12)
    p_script_note.add_run("💡 腳本執行說明：\n").bold = True
    p_script_note.add_run(
        "• 自動檢查並安裝 Python 高速套件管理工具 uv\n"
        "• 自動建立 Python 3.12 虛擬環境 (.venv)\n"
        "• 自動安裝 requirements-core.txt 核心套件\n"
        "• 自動執行 verify_core.py 驗證環境建置是否完整成功"
    )

    # 5. 階段四：服務登入與瀏覽器 OAuth 授權
    add_heading_1("📌 階段四：服務登入與瀏覽器 OAuth 授權")
    doc.add_paragraph(
        "由於 API Key 與帳號 Token 具備個人隱私性，以下三個步驟需由使用者親自在 PowerShell 執行指令，"
        "並在自動跳出的瀏覽器視窗中完成點選授權："
    )

    add_heading_2("1. 登入 GitHub CLI")
    add_code_block("gh auth login --web --git-protocol https")
    p_gh = doc.add_paragraph("👉 說明：在 PowerShell 依提示按 Enter，於跳出的瀏覽器視窗中點擊「Authorize GitHub」完成授權。")
    p_gh.paragraph_format.space_after = Pt(8)

    add_heading_2("2. 登入 NotebookLM (透過 uv 與 nlm CLI)")
    add_code_block("uv tool install notebooklm-mcp-cli\nnlm login")
    p_nlm = doc.add_paragraph("👉 說明：瀏覽器會跳出 Google 登入頁面，請選擇欲連結 NotebookLM 的 Google 帳號授權。")
    p_nlm.paragraph_format.space_after = Pt(8)

    add_heading_2("3. 登入 Firebase")
    add_code_block("npx.cmd -y firebase-tools@latest login")
    p_fb = doc.add_paragraph("👉 說明：瀏覽器跳出授權頁面後，點擊「允許」提供 Firebase CLI 專案存取權限。")
    p_fb.paragraph_format.space_after = Pt(12)

    # 6. 階段五：AntiGravity 技能匯入與專案開工
    add_heading_1("📌 階段五：AntiGravity 技能匯入與專案開工")
    
    steps_5 = [
        ("匯入 Agent 技能包 (Skills)", "將提供之 skills 資料夾內容解開，複製至 C:\\Users\\<你的帳號>\\.gemini\\config\\skills\\。"),
        ("設定全域規則 (User Rules)", "將專案提供之 SENSEBAR_SYNC_WORKFLOW_V1 及 Edge-TTS 語音規則貼入 AntiGravity 設定檔。"),
        ("開啟專案資料夾", "在 AntiGravity 中點選 File -> Open Folder，選取本專案目錄。"),
        ("執行開工驗證", "對 AntiGravity 對話框輸入「開工」。AntiGravity 將自動讀取 ANTIGRAVITY.md，完成專案檢查並回報狀態！")
    ]
    for i, (title, desc) in enumerate(steps_5, 1):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(6)
        r_num = p.add_run(f"Step {i}. {title}\n")
        r_num.bold = True
        r_num.font.color.rgb = SECONDARY_COLOR
        p.add_run(desc)

    # 7. 附錄：常見問題與排錯對照表
    add_heading_1("📌 附錄：常見問題與排錯對照表 (Troubleshooting)")
    
    table_data = [
        ("遇到的問題", "原因分析", "建議解法"),
        ("PowerShell 阻擋執行 .ps1 腳本", "Windows 預設 ExecutionPolicy 限制腳本執行", "執行指令時加入 -ExecutionPolicy Bypass 参数，或改用 .cmd 尾碼"),
        ("gh 或 nlm 指令提示 command not found", "環境變數 (Path) 未重新載入", "關閉並重新開啟 PowerShell 視窗，或重啟 AntiGravity 即可抓到 Path"),
        ("NotebookLM 登入到錯誤的 Google 帳號", "瀏覽器快取了先前的 Google 帳號權限", "執行 nlm logout 登出後，重新執行 nlm login 並在瀏覽器選擇正確帳號"),
        ("Firebase login 畫面卡住", "AI 對話介面無法回應互動式瀏覽器跳轉", "不要在 AI 對話中執行，請直接開啟獨立 PowerShell 視窗手動執行登入"),
        ("Windows 中文字元顯示亂碼", "控制台編碼頁與 UTF-8 不一致", "在 PowerShell 事先執行 $env:PYTHONIOENCODING = \"utf-8\" 再執行指令")
    ]

    table = doc.add_table(rows=len(table_data), cols=3)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    for row_idx, row in enumerate(table.rows):
        # Prevent row split across pages
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        
        for col_idx, cell in enumerate(row.cells):
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            
            cell_text = table_data[row_idx][col_idx]
            run = p.add_run(cell_text)
            
            if row_idx == 0:
                set_cell_background(cell, HEADER_BG)
                run.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
            else:
                if row_idx % 2 == 1:
                    set_cell_background(cell, ALT_ROW_BG)
                run.font.size = Pt(10)

    # Set column widths
    col_widths = [Inches(2.2), Inches(2.2), Inches(2.4)]
    for row in table.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = width

    # Save document
    output_path = "D:\\AI\\AI_Agent\\AntiGravity_新手完整導引與帳號設定_CheckList.docx"
    doc.save(output_path)
    print(f"Successfully generated Word document at: {output_path}")

if __name__ == "__main__":
    create_document()
