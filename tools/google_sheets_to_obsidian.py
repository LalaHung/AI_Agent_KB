#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Sheets 調研問卷自動同步至 Obsidian 腳本範本
功能：
1. 讀取 Google 試算表上的調研問卷資料。
2. 根據「客戶/專案名稱」自動在 Obsidian 中建立對應的專案目錄結構。
3. 將問卷數據格式化為 Markdown 調研報告並存入該專案的 01_Research 資料夾中。
"""

import os
import sys
import json
import csv
from datetime import datetime

# ==================== 設定區 ====================
# 請在此設定您的 Obsidian Vault 實體路徑
OBSIDIAN_VAULT_PATH = r"d:\AI\SecondBrain"

# 暫時的本地測試問卷 CSV 檔案路徑（可用於模擬 Google Sheets 匯出的資料）
TEST_CSV_PATH = "survey_responses.csv"
# ===============================================

def initialize_project_info(vault_path, client_name):
    """
    建立專案基本資訊的 Metadata 檔案，並儲存至 200_專案交付區/00_專案基本資訊/
    """
    info_dir = os.path.join(vault_path, "200_專案交付區", "00_專案基本資訊")
    os.makedirs(info_dir, exist_ok=True)
    
    info_file = os.path.join(info_dir, f"{client_name}_基本資訊.md")
    print(f"[系統] 正在為「{client_name}」建立基本資訊檔...")
    
    if not os.path.exists(info_file):
        with open(info_file, "w", encoding="utf-8") as f:
            f.write(f"""# {client_name} 專案基本資訊

- **專案名稱**: {client_name}
- **建立時間**: {datetime.now().strftime('%Y-%m-%d')}
- **專案階段**: #stage/research
- **負責顧問**: 

---
## 專案簡介
請在此輸入專案的簡要背景與目標。
""")
        print(f"[成功] 基本資訊已建立: {info_file}")
    return info_file

def generate_research_report(vault_path, client_name, row_data):
    """
    將問卷的單列資料轉換為 Markdown 格式的調研報告，並儲存至 200_專案交付區/01_調研階段/
    """
    research_dir = os.path.join(vault_path, "200_專案交付區", "01_調研階段")
    os.makedirs(research_dir, exist_ok=True)
    
    report_path = os.path.join(research_dir, f"{client_name}_01調研問卷報告.md")
    
    # 解析問卷資料（這裡假設了問卷欄位，實際使用時需對照 Google 試算表的欄位名稱）
    timestamp = row_data.get("時間戳記", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    consultant = row_data.get("負責顧問", "未填寫")
    pain_points = row_data.get("目前面臨的最大痛點", "無描述")
    aps_req = row_data.get("APS系統期望達成的目標", "無描述")
    existing_systems = row_data.get("現有ERP/MES系統種類", "無")
    
    report_content = f"""# {client_name} - 01 調研問卷報告

- **調研時間**: {timestamp}
- **負責顧問**: [[{consultant}]]
- **專案連結**: [[{client_name}_基本資訊]]
- **標籤**: #stage/research #report/survey #client/{client_name}

---

## 📌 調研背景與系統現況
- **現有 ERP/MES 系統**: {existing_systems}

## 🔍 客戶核心痛點分析
{pain_points}

## 🎯 APS 系統上線期望目標
{aps_req}

---
> [!NOTE]
> 本文件由自動化腳本自 Google 試算表調研問卷產生。後續可搭配 NotebookLM 進行深度的 RAG 分析，並將分析結果貼回 [[{client_name}_基本資訊]]。
"""
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"[成功] 調研報告已生成至: {report_path}")
    return report_path

def load_survey_data(file_path):
    """
    從 CSV 或 Excel 讀取問卷資料
    """
    if not os.path.exists(file_path):
        # 建立一個測試用的 CSV 檔
        print(f"[提示] 未找到 {file_path}，自動產生測試問卷數據...")
        with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["時間戳記", "客戶名稱", "負責顧問", "目前面臨的最大痛點", "APS系統期望達成的目標", "現有ERP/MES系統種類"])
            writer.writerow([
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "客戶A製造廠",
                "王大明",
                "1. 排程效率低下，手工排產需耗時4小時。\n2. 物料與訂單無法即時鎖定，常因缺料停工。",
                "1. 實現自動化排程，排產時間縮短至30分鐘內。\n2. 精準預測缺料風險。",
                "SAP ECC 6.0"
            ])
            
    ext = os.path.splitext(file_path)[1].lower()
    data = []
    
    if ext == '.csv':
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(dict(row))
    elif ext in ['.xlsx', '.xls']:
        try:
            import openpyxl
            wb = openpyxl.load_workbook(file_path, data_only=True)
            sheet = wb.active
            rows = list(sheet.iter_rows(values_only=True))
            if not rows:
                return []
            headers = [str(h).strip() if h is not None else "" for h in rows[0]]
            for row in rows[1:]:
                if not any(val is not None for val in row):
                    continue
                row_dict = {}
                for idx, h in enumerate(headers):
                    if h:
                        row_dict[h] = row[idx] if idx < len(row) else ""
                data.append(row_dict)
        except Exception as e:
            print(f"[錯誤] 無法讀取 Excel 檔案: {e}")
            
    return data

def main():
    print("=== 專案調研問卷自動分類歸檔啟動 ===")
    
    # 支援命令列傳入檔案路徑
    if len(sys.argv) < 2:
        survey_path = TEST_CSV_PATH
        print(f"[提示] 未提供輸入路徑，預設使用: {survey_path}")
    else:
        survey_path = sys.argv[1]
        
    # 1. 檢查 Obsidian Vault 是否存在
    if not os.path.exists(OBSIDIAN_VAULT_PATH):
        print(f"[警告] 找不到設定的 Obsidian Vault 路徑: {OBSIDIAN_VAULT_PATH}")
        print("將在當前目錄下建立一個臨時的 'SecondBrain_Local' 測試資料夾。")
        vault_path = os.path.abspath("SecondBrain_Local")
    else:
        vault_path = OBSIDIAN_VAULT_PATH
        
    # 2. 獲取資料
    survey_rows = load_survey_data(survey_path)
    if not survey_rows:
        print("[錯誤] 未能載入任何問卷數據！")
        sys.exit(1)
        
    # 3. 處理每一筆調研問卷
    for row in survey_rows:
        client_name = row.get("客戶名稱", "").strip()
        if not client_name:
            # 嘗試搜尋「客戶」或「專案」相關的 key
            for k, v in row.items():
                if "客戶" in k or "專案" in k:
                    client_name = str(v).strip()
                    break
                    
        if not client_name or client_name.upper() == 'NONE':
            continue
            
        # 3.1 建立該客戶的專案基本資訊檔
        initialize_project_info(vault_path, client_name)
        
        # 3.2 產生調研報告 Markdown 檔案並歸檔
        generate_research_report(vault_path, client_name, row)
        
    print("\n=== 自動化處理完成 ===")
    print(f"請打開 Obsidian Vault 並查看: {vault_path}")

if __name__ == "__main__":
    main()
