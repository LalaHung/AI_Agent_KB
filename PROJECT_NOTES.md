# 專案筆記 (Project Notes) - 成績登錄系統

本文件記錄「學生成績管理系統」的開發進度、踩坑紀錄與後續計畫。

---

## 📌 完成事項 (Completed Tasks)
*   **環境建置**：在 Windows 環境下安裝與配置 Node.js 與 clasp (Google Apps Script CLI)。
*   **資料庫建置**：建立 Google Sheet 資料表，規畫欄位：`id`, `student_id`, `name`, `subject`, `score`, `exam_date`, `remarks`, `created_at`。
*   **後端 API 開發**：
    *   撰寫 `Code.js` 提供 `doGet` (讀取成績) 與 `doPost` (新增、修改、刪除成績) 的 API 功能。
    *   設定 `appsscript.json` 開放匿名網頁應用程式存取 (ANYONE_ANONYMOUS)。
*   **前端開發**：
    *   設計現代化玻璃擬態 (Glassmorphism) 的極簡 RWD 儀表板頁面。
    *   整合統計圖表卡片（總人數、及格率、平均分、最高/最低分）。
    *   實作完整的學籍搜尋、學科篩選、及格篩選與成績新增/編輯/刪除之 CRUD 功能。
*   **雲端部署**：將前端靜態頁面部署至 Netlify，連線測試完全成功。
*   **工具與環境配置**：
    *   成功安裝並設定 `voxcpm2-voice-cloner` 聲音複製工具。
    *   全域安裝並設定 `Claude Code CLI` (v2.1.218) 以及選用同步工具 `Chezmoi` (v2.71.1)。
    *   建置與配置 `~/.gemini/GEMINI.md` 的全域「語音輸入文字正規化、語音回覆設定 (Edge-TTS) 與開工/收工工作流程」規則，並依使用者指示清理刪除未使用的 `~/.claude/skills` 目錄。

---

## 💡 下一步計畫 (Next Steps)
1.  **安全性加固**：目前 API 與前端網頁為全公開狀態，未來可加上密碼驗證或限制來源的安全性機制。
2.  **視覺化分析**：在儀表板增加歷次考試分數變動趨勢圖（如使用 Chart.js）。
3.  **批次導入功能**：支援 CSV / Excel 批次匯入學生成績。
4.  **聲音複製體驗**：啟動 `webui_record.py` 錄製聲音，並以 `clone.py` 生成複製語音。
5.  **Google 行事曆與信箱串接**：待申請 Google Cloud OAuth Client ID & Secret 後，於 `mcp_config.json` 中配置 Google Calendar 與 Gmail MCP 伺服器並完成網頁授權。

---

## ⚠️ 踩坑與心得 (Learnings & Pitfalls)
1.  **PowerShell 執行權限限制**：
    *   *問題*：執行 `npm` 或 `clasp` 時，PowerShell 因執行原則限制阻擋載入 `.ps1` 檔案。
    *   *解法*：在 PowerShell 命令中改為直接呼叫 `.cmd` 尾碼（如 `npm.cmd`、`clasp.cmd`），繞過腳本執行限制。
2.  **Google Apps Script 首次執行授權 (HTTP 403)**：
    *   *問題*：以 clasp 部署的 Web App，首次呼叫會直接回傳 HTTP 403 錯誤。
    *   *解法*：必須先手動登入 Apps Script 線上編輯器，並隨便點選一個函數執行 (Run) 來完成權限核准，網頁應用程式 API 才會被啟動。
3.  **桌面程式之環境變數重啟生效與 winget ID**：
    *   *問題*：`winget` 安裝 Node.js 與 `chezmoi` 後，AntiGravity 與 Netlify MCP 抓不到 `npx` / `chezmoi` 的路徑，且 `chezmoi` 的 winget ID 與預想不同。
    *   *解法*：確認 `chezmoi` 在 winget 上的正確 ID 為 `twpayne.chezmoi`；安裝完成後，必須完全重啟 AntiGravity 桌面軟體，新註冊的 Path 才會繼承至工作階段中。
4.  **PowerShell 腳本非 ASCII 字元解析錯誤**：
    *   *問題*：Windows PowerShell 預設系統語系為繁體中文 (ANSI/950)，解析包含中文註解與字串的 UTF-8 `install.ps1` 時會出錯（錯誤碼：TerminatorExpectedAtEndOfString）。
    *   *解法*：將 `install.ps1` 的控制輸出字串改為純英文 (ASCII-only)，即可在各種 Windows環境正常解析執行。

