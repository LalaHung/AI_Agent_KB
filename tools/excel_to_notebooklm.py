#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel/CSV 轉 Markdown 並自動上傳至 NotebookLM 腳本
功能：
1. 讀取本地 Excel (.xlsx) 或 CSV 檔案。
2. 自動將其轉換為適合 AI 閱讀的 Markdown 表格格式。
3. 透過 nlm CLI 呼叫 NotebookLM API 將其直接上傳至指定的筆記本中。
"""

import os
import sys
import subprocess
import tempfile
import csv

# Ensure UTF-8 output
if sys.version_info >= (3, 7):
    sys.stdout.reconfigure(encoding='utf-8')

def csv_to_markdown(csv_path):
    """將 CSV 轉換為 Markdown 表格"""
    markdown_content = []
    filename = os.path.basename(csv_path)
    markdown_content.append(f"# 數據資料表: {filename}\n")
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        rows = list(reader)
        
    if not rows:
        return ""
        
    # 產生表頭
    headers = rows[0]
    markdown_content.append("| " + " | ".join(headers) + " |")
    markdown_content.append("| " + " | ".join(["---"] * len(headers)) + " |")
    
    # 產生內容
    for row in rows[1:]:
        # 處理空欄位或換行
        cleaned_row = [col.replace('\n', '<br>').replace('|', '\\|') for col in row]
        markdown_content.append("| " + " | ".join(cleaned_row) + " |")
        
    return "\n".join(markdown_content)

def excel_to_markdown(excel_path):
    """將 Excel 的所有工作表轉換為 Markdown 表格"""
    try:
        import openpyxl
    except ImportError:
        print("[錯誤] 請先安裝 openpyxl: pip install openpyxl")
        return None
        
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    markdown_content = []
    filename = os.path.basename(excel_path)
    markdown_content.append(f"# 數據資料表: {filename}\n")
    
    for sheet_name in wb.sheetnames:
        sheet = wb[sheet_name]
        markdown_content.append(f"## 工作表: {sheet_name}\n")
        
        rows = list(sheet.iter_rows(values_only=True))
        if not rows or all(all(val is None for val in row) for row in rows):
            markdown_content.append("*此工作表為空*\n")
            continue
            
        # 尋找非空的表頭與資料列
        valid_rows = [row for row in rows if any(val is not None for val in row)]
        if not valid_rows:
            continue
            
        # 表頭處理
        headers = [str(val) if val is not None else "" for val in valid_rows[0]]
        markdown_content.append("| " + " | ".join(headers) + " |")
        markdown_content.append("| " + " | ".join(["---"] * len(headers)) + " |")
        
        # 資料列處理
        for row in valid_rows[1:]:
            cleaned_row = [str(val).replace('\n', '<br>').replace('|', '\\|') if val is not None else "" for val in row]
            markdown_content.append("| " + " | ".join(cleaned_row) + " |")
            
        markdown_content.append("\n")
        
    return "\n".join(markdown_content)

def upload_to_notebooklm(notebook_id, file_path, title):
    """使用 nlm CLI 上傳檔案"""
    cmd = [
        "nlm", "source", "add", notebook_id,
        "--file", file_path,
        "--title", title,
        "--wait"
    ]
    print(f"[系統] 執行上傳指令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True)
        print("[成功] 上傳完成！")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("[錯誤] 上傳失敗！")
        print(e.stderr)
        return False

def main():
    if len(sys.argv) < 3:
        print("使用方法: python excel_to_notebooklm.py <檔案路徑> <Notebook_ID> [自訂標題]")
        sys.exit(1)
        
    file_path = sys.argv[1]
    notebook_id = sys.argv[2]
    
    if len(sys.argv) >= 4:
        title = sys.argv[3]
    else:
        title = os.path.splitext(os.path.basename(file_path))[0]
        
    if not os.path.exists(file_path):
        print(f"[錯誤] 檔案不存在: {file_path}")
        sys.exit(1)
        
    ext = os.path.splitext(file_path)[1].lower()
    print(f"[系統] 正在解析檔案: {file_path} ...")
    
    if ext == '.csv':
        md_text = csv_to_markdown(file_path)
    elif ext in ['.xlsx', '.xls']:
        md_text = excel_to_markdown(file_path)
    else:
        print("[錯誤] 不支援的檔案格式，僅限 .xlsx, .xls 或 .csv")
        sys.exit(1)
        
    if not md_text:
        print("[錯誤] 轉換失敗或檔案內容為空")
        sys.exit(1)
        
    # 建立臨時 Markdown 檔案並上傳
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file_path = os.path.join(temp_dir, f"{title}_data.md")
        with open(temp_file_path, "w", encoding="utf-8") as f:
            f.write(md_text)
            
        print(f"[系統] 已將試算表轉換為臨時 Markdown 檔案，大小: {len(md_text.encode('utf-8'))} bytes")
        success = upload_to_notebooklm(notebook_id, temp_file_path, title)
        
    if success:
        print("[完成] 轉換與自動上傳作業已順利結束！")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
