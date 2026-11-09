# AI Agent 知識庫建構專案指引 (Project Guide)

> **重要說明**：
> 本專案已全面升級為標準化 AI Agent 自主執行架構。
> 完整的機器可讀作業規範、4 階段知識庫建構管線（YouTube 字幕清洗、GitHub 資源抽取、NotebookLM/Obsidian 整合）以及開工/收工 Lifecycle 規範，請統一參閱：
> 
> 👉 **[AGENTS.md](file:///d:/AI/AI_Agent/AGENTS.md)**

---

## 📌 專案核心使命
本專案為一個由 AI Agent 全自動維護的多來源智慧知識庫（AI Agent Knowledge Base），涵蓋：
1. **YouTube 教學精華知識庫**：自動抓取三師爸（@sensebar）頻道 65+ 部 AI Agent、AntiGravity、Claude Code、Codex 的教學字幕，透過自研滑動窗口演算法進行時間戳剔除與連續字句去重，產出結構化 Markdown 於 `subtitles/`。
2. **開源專案資源索引**：自動萃取影片說明欄中提及的所有 GitHub 開源專案（如 `antigravity-lazy-pack`, `voxcpm2-voice-cloner`, `soil-motion-deck` 等），建立雙向對照索引於 `GITHUB_RESOURCES.md`。
3. **全域技能封裝**：本專案之 YouTube 萃取管線已封裝為獨立全域技能 `youtube-kb-builder`（存放於 `D:\.gemini\config\skills\youtube-kb-builder\`），供本機所有專案調用。

詳細執行指令與架構請見 [AGENTS.md](file:///d:/AI/AI_Agent/AGENTS.md) 與 [README.md](file:///d:/AI/AI_Agent/README.md)。
