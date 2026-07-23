# Obsidian 第二大腦三層結構設定工作流程 (AntiGravity / Claude Code 適用)

> 版本：v1.0
> 更新日期：2026-07-23
> 語系：繁體中文 (Taiwan)

本工作流程文件旨在引導使用者透過 AI Agent (AntiGravity 或 Claude Code) 自動化安裝並設定 **Obsidian 第二大腦三層結構**。此設定源自 AI 大神 Andrej Karpathy 的筆記工作流理念，旨在建立「輸入 ➔ 消化 ➔ 輸出」的無縫知識管理系統。

---

## 🌟 核心架構：三層筆記結構

安裝完成後，您的 Obsidian Vault 將會被建立以下目錄結構：

```text
vault/
├── Clippings/           ← 【輸入】：網路上剪藏的原始好文、影片筆記、參考資料 (AI 不修改)
├── 知識庫/              ← 【消化】：AI 整理消化後的結構化百科全書，含有 index.md 和 log.md
├── 創作庫/              ← 【輸出】：您個人的原創內容 (教案、教材、教學報告)
├── 每日筆記/            ← 【時間管理】：每日反思、週計畫、每週知識重整週報
├── Templates/           ← 【模板】：存放日記、週計畫與知識庫頁面模板
└── CLAUDE.md            ← 【工作規則】：AI 讀取的「班規」，定義您的教學科目、年級與語系
```

---

## 🛠️ 安裝與設定步驟

### 步驟一：先備條件確認
在執行自動化安裝前，請確認：
- [ ] 電腦已安裝 [Git](https://git-scm.com/) 與 [Node.js](https://nodejs.org/)。
- [ ] 您的 AI Agent (AntiGravity / Claude Code) 運作正常。
- [ ] 已安裝並串接好 Obsidian MCP (如 [MCPVault](https://github.com/bitbonsai/mcpvault))，讓 Agent 可以存取您的筆記資料夾。

---

### 步驟二：透過 AI Agent 安裝 `cc-second-brain` 技能

請在您的 AI Agent 終端機中執行以下命令：

#### 🔹 Windows 系統 (PowerShell 適用)
若遇到 Execution Policy 權限阻擋，請使用 `npx.cmd` 來呼叫：
```powershell
npx.cmd skills add mathruffian-dot/claude-code-lazy-packs --skill cc-second-brain -g -y --full-depth
```

#### 🔹 Mac / Linux 系統
```bash
npx skills add mathruffian-dot/claude-code-lazy-packs --skill cc-second-brain -g -y --full-depth
```

> 💡 **參數說明**：
> - `--skill cc-second-brain`：指定安裝 Obsidian 第二大腦設定技能。
> - `-g`：安裝至全域技能庫。
> - `-y`：自動確認所有提示。
> - `--full-depth`：啟用深度搜索以正確在子目錄中尋找技能設定。

---

### 步驟三：啟動自動化設定工作流
完成安裝後，請在與 AI Agent 的對話中輸入以下指令啟動：

💬 **對話輸入**：
> **「建立第二大腦」** 或 **「啟動第二大腦初始化」**

AI Agent 載入此技能後，將引導您執行以下工作：
1. **收集您的教學資訊**：詢問您的教學科目 (如：國中數學)、教學年級、回答語言與個人偏好。
2. **自動建立結構**：在您的 Obsidian Vault 中建立 `Clippings/`、`知識庫/`、`創作庫/`、`每日筆記/`、`Templates/` 資料夾。
3. **客製化 CLAUDE.md**：自動於 Vault 根目錄產生記錄您個人教學背景與 AI 回應偏好的工作規則。
4. **安裝筆記模板**：於 `Templates/` 下建立：
   - `每日筆記.md` (含備課進度與今日反思)
   - `週計畫.md` (本週重要事項與每日日記連結)
   - `知識庫頁面.md` (核心概念、教學連結與內容缺口)
5. **初始化索引**：在 `知識庫/` 中建立目錄 `index.md` 與歷史記錄 `log.md`。

---

### 步驟四：手動設定瀏覽器 Web Clipper (僅需一次)
1. 打開您的瀏覽器，點擊 **Obsidian Web Clipper** 擴充功能圖示。
2. 進入設定 (齒輪 ⚙ 符號)。
3. 確認選定的 **Vault** 為您目前使用的筆記庫。
4. 將預設存放路徑 (Folder / Location) 改為：`Clippings`。
5. 儲存設定。

---

### 步驟五：設定每週自動知識重整排程 (Optional)
AI Agent 會在系統中註冊一個每週自動執行的排程任務：
- **任務名稱**：`weekly-knowledge-review`
- **重整排程**：每週日早上 9:17 執行
- **重整內容**：AI 會自動讀取您本週剪藏在 `Clippings/` 的文章，將其消化、提煉並更新至 `知識庫/` 中，同時為您產出一份知識重整週報。

您也可以隨時對 AI Agent 說：**「跑一次知識重整」** 或 **「消化 Clippings」** 來手動進行整理。

---

## ✅ 安裝成功驗證
您可以對著 AI Agent 說：
> **「幫我檢查第二大腦狀態」**

正確安裝後，AI 將回報以下狀態：
1. `Clippings/` 等 5 大資料夾已存在。
2. `CLAUDE.md` 已建立且包含您的基本教學資訊。
3. 筆記模板已成功建立至 `Templates/`。
4. `index.md` 與 `log.md` 已順利初始化。
5. 週整理排程 `weekly-knowledge-review` 已設定完成。
