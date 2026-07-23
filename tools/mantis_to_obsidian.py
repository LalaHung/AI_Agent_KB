#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MantisBT 模擬登入與案件資料自動同步至 Obsidian 腳本
功能：
1. 模擬登入 MantisBT (支援 2.x 兩階段登入)。
2. 給定案件編號 (Bug ID)，下載案件詳情（包含主旨、描述、處理歷程與附加檔案連結）。
3. 自動解析「專案/客戶名稱」，並在 Obsidian 知識庫中對應的客戶目錄下，建立或更新該案件的 Markdown 文件。
"""

import os
import sys
import re
import getpass
import urllib.request
import urllib.parse
import http.cookiejar
from datetime import datetime

# ==================== 預設設定區 ====================
MANTIS_BASE_URL = "http://122.146.130.11:81/mantis/"
OBSIDIAN_VAULT_PATH = r"d:\AI\SecondBrain"

# 帳密可在此處設定，若為空則執行時會提示輸入
MANTIS_USERNAME = "dci_lavender"
MANTIS_PASSWORD = "DGW04137"
# ===================================================

# Ensure UTF-8 output
if sys.version_info >= (3, 7):
    sys.stdout.reconfigure(encoding='utf-8')

class MantisScraper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/') + '/'
        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))
        # 模擬瀏覽器 User-Agent
        self.opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')]
        
    def login(self, username, password):
        """模擬登入 MantisBT (兩階段)"""
        print("[系統] 正在連接 MantisBT 登入頁面...")
        
        # 1. 取得登入頁面
        url_login_page = self.base_url + "login_page.php"
        try:
            resp1 = self.opener.open(url_login_page)
            html1 = resp1.read().decode('utf-8')
        except Exception as e:
            print(f"[錯誤] 無法連線至登入頁面: {e}")
            return False
            
        # 2. 第一階段：提交帳號
        url_password_page = self.base_url + "login_password_page.php"
        post_data1 = {
            'return': 'index.php',
            'username': username
        }
        
        # 檢查是否有 CSRF token
        token_match = re.search(r'name="mantis_login_token" value="([^"]*)"', html1)
        if token_match:
            post_data1['mantis_login_token'] = token_match.group(1)
            
        try:
            data1 = urllib.parse.urlencode(post_data1).encode('utf-8')
            resp2 = self.opener.open(url_password_page, data=data1)
            html2 = resp2.read().decode('utf-8')
        except Exception as e:
            print(f"[錯誤] 第一階段登入失敗: {e}")
            return False
            
        # 3. 第二階段：提交密碼
        url_login = self.base_url + "login.php"
        post_data2 = {
            'return': 'index.php',
            'username': username,
            'password': password,
            'secure_session': 'on'
        }
        
        # 檢查第二階段的 token
        token_match2 = re.search(r'name="mantis_login_token" value="([^"]*)"', html2)
        if token_match2:
            post_data2['mantis_login_token'] = token_match2.group(1)
            
        try:
            data2 = urllib.parse.urlencode(post_data2).encode('utf-8')
            resp3 = self.opener.open(url_login, data=data2)
            final_html = resp3.read().decode('utf-8')
            
            # 檢查是否登入成功 (若仍在 login_page 或 login_password_page 代表失敗)
            if "login_page.php" in resp3.geturl() or "login_password_page.php" in resp3.geturl():
                print("[錯誤] 登入失敗，請檢查帳號或密碼是否正確。")
                return False
                
            print("[成功] MantisBT 登入成功！")
            return True
        except Exception as e:
            print(f"[錯誤] 第二階段登入連線失敗: {e}")
            return False

    def fetch_issue(self, issue_id):
        """下載特定單號的網頁內容"""
        url = f"{self.base_url}view.php?id={issue_id}"
        print(f"[系統] 正在讀取案件編號 #{issue_id} ...")
        try:
            resp = self.opener.open(url)
            html = resp.read().decode('utf-8')
            return html
        except Exception as e:
            print(f"[錯誤] 無法讀取案件 #{issue_id}: {e}")
            return None

    def clean_html_tags(self, text):
        """清除 HTML 標籤並還原特殊字元"""
        if not text:
            return ""
        # 替換常見標籤
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = re.sub(r'<p[^>]*>', '\n', text)
        text = re.sub(r'</p>', '\n', text)
        # 清除刪除按鈕/表單
        text = re.sub(r'<form[^>]*>.*?</form>', '', text, flags=re.DOTALL)
        # 清除所有其他 HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # 還原 HTML Entities
        text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&').replace('&quot;', '"').replace('&#32;', ' ')
        # 清除多餘換行
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def convert_html_links_to_markdown(self, text):
        """將 HTML 連結轉換為 Markdown 格式，如果是相對路徑就補上完整網址"""
        if not text:
            return ""
        def replace_link(match):
            href = match.group(1).strip()
            link_text = match.group(2)
            if not href:
                return ""
            # 排除垃圾連結 (如刪除按鈕圖示等)
            if "bug_file_delete.php" in href or "bugnote_delete.php" in href:
                return ""
            if not href.startswith('http'):
                href = self.base_url + href.lstrip('/')
            cleaned_text = self.clean_html_tags(link_text)
            if not cleaned_text:
                return ""
            return f"[{cleaned_text}]({href})"
        
        # 匹配 <a ... href="url">text</a>
        text = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>', replace_link, text, flags=re.DOTALL)
        return text

    def parse_issue_html(self, html, issue_id):
        """解析 MantisBT 案件頁面的資訊"""
        data = {
            'id': issue_id,
            'project': '未分類專案',
            'category': '未分類',
            'summary': '未命名案件',
            'status': '未知',
            'description': '無描述',
            'steps_to_reproduce': '',
            'additional_info': '',
            'client_name': '',  # 客戶名稱自訂欄位
            'custom_fields': {}, # 其他自訂欄位
            'bugnotes': [],
            'attachments': [],
            'relationships': []
        }
        
        # 1. 解析專案名稱 (優先使用 class="bug-project")
        project_match = re.search(r'<td class="bug-project"[^>]*>(.*?)</td>', html, re.DOTALL)
        if project_match:
            data['project'] = self.clean_html_tags(project_match.group(1))
        else:
            # 備用方案：尋找麵包屑
            project_match2 = re.search(r'<ul class="breadcrumb">.*?<li><a[^>]*>(.*?)</a></li>.*?</ul>', html, re.DOTALL)
            if project_match2:
                data['project'] = self.clean_html_tags(project_match2.group(1))

        # 2. 解析案件主旨/摘要 (Summary)
        summary_match = re.search(r'<td class="bug-summary"[^>]*>(.*?)</td>', html, re.DOTALL)
        if summary_match:
            raw_summary = self.clean_html_tags(summary_match.group(1))
            if ":" in raw_summary:
                data['summary'] = raw_summary.split(":", 1)[1].strip()
            else:
                data['summary'] = raw_summary
        
        # 3. 解析類別與狀態 (Category & Status)
        category_match = re.search(r'<td class="bug-category"[^>]*>(.*?)</td>', html, re.DOTALL)
        if category_match:
            data['category'] = self.clean_html_tags(category_match.group(1))
            
        status_match = re.search(r'<td class="bug-status"[^>]*>(.*?)</td>', html, re.DOTALL)
        if status_match:
            data['status'] = self.clean_html_tags(status_match.group(1))

        # 4. 解析描述、重現步驟與附加資訊
        desc_match = re.search(r'<td class="bug-description"[^>]*>(.*?)</td>', html, re.DOTALL)
        if desc_match:
            data['description'] = self.clean_html_tags(desc_match.group(1))
            
        steps_match = re.search(r'<td class="bug-steps-to-reproduce"[^>]*>(.*?)</td>', html, re.DOTALL)
        if steps_match:
            data['steps_to_reproduce'] = self.clean_html_tags(steps_match.group(1))
        else:
            # 備用中文標籤匹配
            steps_match2 = re.search(r'如何重現[^<]*</td>\s*<td[^>]*>(.*?)</td>', html, re.DOTALL)
            if steps_match2:
                data['steps_to_reproduce'] = self.clean_html_tags(steps_match2.group(1))
            
        add_match = re.search(r'<td class="bug-additional-information"[^>]*>(.*?)</td>', html, re.DOTALL)
        if add_match:
            data['additional_info'] = self.clean_html_tags(add_match.group(1))
        else:
            # 備用中文標籤匹配
            add_match2 = re.search(r'附加資訊[^<]*</td>\s*<td[^>]*>(.*?)</td>', html, re.DOTALL)
            if add_match2:
                data['additional_info'] = self.clean_html_tags(add_match2.group(1))

        # 5. 解析自訂欄位 (Custom Fields)
        custom_fields = re.findall(r'<th class="bug-custom-field category"[^>]*>(.*?)</th>\s*<td class="bug-custom-field"[^>]*>(.*?)</td>', html, re.DOTALL)
        for header, val in custom_fields:
            header_clean = self.clean_html_tags(header)
            val_clean = self.clean_html_tags(val)
            if val_clean and val_clean.upper() != 'NONE' and val_clean.upper() != 'STD' and val_clean:
                data['custom_fields'][header_clean] = val_clean
                if "客戶名稱" in header_clean:
                    data['client_name'] = val_clean

        # 6. 解析相關附件
        attachments = re.findall(r'<a[^>]*href="file_download\.php\?file_id=(\d+)&amp;type=bug"[^>]*>(.*?)</a>', html)
        for fid, fname in attachments:
            data['attachments'].append({
                'name': fname.strip(),
                'url': f"{self.base_url}file_download.php?file_id={fid}&type=bug"
            })

        # 7. 解析關聯案件
        rel_matches = re.findall(r'href="view\.php\?id=(\d+)"[^>]*>(\d+)</a>', html)
        seen_rels = set()
        for rid, rnum in rel_matches:
            if rid != issue_id and rid not in seen_rels:
                seen_rels.add(rid)
                data['relationships'].append(rid)

        # 8. 解析處理歷程/留言 (Bugnotes)
        bugnote_rows = re.findall(r'<tr class="bugnote[^"]*"[^>]*>(.*?)</tr>', html, re.DOTALL)
        for row in bugnote_rows:
            author_match = re.search(r'<a class="user"[^>]*>(.*?)</a>', row)
            # 尋找時間戳記，格式如 2026-07-21 14:16
            time_match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})', row)
            note_match = re.search(r'<td class="bugnote-note[^"]*"[^>]*>(.*?)</td>', row, re.DOTALL)
            
            if author_match and note_match:
                author = self.clean_html_tags(author_match.group(1))
                time_str = time_match.group(1).strip() if time_match else "未知時間"
                raw_note = note_match.group(1)
                
                # 將留言中的 <a> 連結轉換為 Markdown 格式
                note_with_markdown_links = self.convert_html_links_to_markdown(raw_note)
                note_cleaned = self.clean_html_tags(note_with_markdown_links)
                
                data['bugnotes'].append({
                    'author': author,
                    'time': time_str,
                    'content': note_cleaned
                })
                    
        return data

    def save_to_obsidian(self, issue_data, vault_path):
        """將案件資料轉換成 Markdown 存入 Obsidian"""
        # 優先使用自訂欄位的「客戶名稱」作為資料夾，其次使用專案名稱
        client_folder = issue_data['client_name'] if issue_data['client_name'] else issue_data['project']
        client_folder = client_folder.replace('/', '_').replace('\\', '_').strip()
        
        # 檔案名稱：Mantis_[ID]_[主旨]
        safe_summary = re.sub(r'[\\/*?:"<>|]', '_', issue_data['summary']).strip()
        filename = f"Mantis_{issue_data['id']}_{safe_summary}.md"
        
        # 格式化 Markdown 內文
        content = []
        content.append(f"# Mantis #{issue_data['id']}: {issue_data['summary']}\n")
        content.append(f"- **專案/系統**: [[{issue_data['project']}_基本資訊]] (專案名稱: {issue_data['project']})")
        if issue_data['client_name']:
            content.append(f"- **客戶名稱**: [[{client_folder}_基本資訊]]")
        content.append(f"- **類別**: {issue_data['category']}")
        content.append(f"- **當前狀態**: {issue_data['status']}")
        content.append(f"- **同步時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 狀態標籤
        safe_status = issue_data['status'].replace(' ', '_').replace('=>', '_to_')
        content.append(f"- **標籤**: #mantis/id/{issue_data['id']} #mantis/status/{safe_status} #client/{client_folder}\n")
        
        # 自訂欄位 (如果有)
        if issue_data['custom_fields']:
            content.append("### 📋 系統欄位")
            for k, v in issue_data['custom_fields'].items():
                content.append(f"- **{k}**: {v}")
            content.append("")

        # 關聯案件
        if issue_data['relationships']:
            rel_links = [f"[[Mantis_{rid}]]" for rid in issue_data['relationships']]
            content.append(f"- **關聯單號**: {', '.join(rel_links)}")
            
        content.append("\n---\n")
        
        content.append("## 📌 案件描述")
        content.append(issue_data['description'] if issue_data['description'] else "（無描述）")
        content.append("")
        
        if issue_data['steps_to_reproduce']:
            content.append("### 🔍 如何重現")
            content.append(issue_data['steps_to_reproduce'])
            content.append("")
            
        if issue_data['additional_info']:
            content.append("### 💡 附加資訊")
            content.append(issue_data['additional_info'])
            content.append("")
            
        # 附件清單
        if issue_data['attachments']:
            content.append("## 📎 相關附件")
            for att in issue_data['attachments']:
                content.append(f"- [{att['name']}]({att['url']})")
            content.append("")
            
        # 歷程留言
        content.append("## 💬 歷程回覆與留言")
        if issue_data['bugnotes']:
            for note in issue_data['bugnotes']:
                content.append(f"### 👤 {note['author']} (於 {note['time']})")
                content.append(note['content'])
                content.append("")
        else:
            content.append("*目前尚無處理歷程回覆*")
            
        content_text = "\n".join(content)
        
        # 寫入目標 1: 客服目錄 300_Customer_Service
        # 寫入目標 1: 客服目錄 300_客戶服務部 (依客戶獨立資料夾存放)
        client_dir = os.path.join(vault_path, "300_客戶服務部", "Clients", client_folder)
        os.makedirs(client_dir, exist_ok=True)
        cs_filename = f"Mantis_{issue_data['id']}_{safe_summary}.md"
        filepath = os.path.join(client_dir, cs_filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content_text)
        print(f"[成功] 案件已歸檔至客服專區: {filepath}")
        
        # 寫入目標 2: 交付專案目錄 200_專案交付區/08_專案交接/ (扁平化存放，以客戶名稱作為檔名前綴)
        project_handover_dir = os.path.join(vault_path, "200_專案交付區", "08_專案交接")
        os.makedirs(project_handover_dir, exist_ok=True)
        proj_filename = f"{client_folder}_Mantis_{issue_data['id']}_{safe_summary}.md"
        proj_filepath = os.path.join(project_handover_dir, proj_filename)
        with open(proj_filepath, "w", encoding="utf-8") as f:
            f.write(content_text)
        print(f"[成功] 案件已同步歸檔至專案交接區: {proj_filepath}")
            
        return filepath

def main():
    print("=== MantisBT to Obsidian 自動同步工具 ===")
    
    # 處理帳號密碼
    username = MANTIS_USERNAME
    password = MANTIS_PASSWORD
    
    if not username:
        username = input("請輸入 MantisBT 帳號: ").strip()
    if not password:
        password = getpass.getpass("請輸入 MantisBT 密碼: ")
        
    if not username or not password:
        print("[錯誤] 帳號或密碼不得為空！")
        sys.exit(1)
        
    # 案件單號
    if len(sys.argv) < 2:
        issue_id = input("請輸入欲同步的 Mantis 案件編號 (例如 12345): ").strip()
    else:
        issue_id = sys.argv[1].strip()
        
    if not issue_id.isdigit():
        print("[錯誤] 案件編號必須為純數字！")
        sys.exit(1)
        
    # 初始化 Scraper
    scraper = MantisScraper(MANTIS_BASE_URL)
    
    # 登入
    if not scraper.login(username, password):
        print("[失敗] 無法登入 Mantis，終止執行。")
        sys.exit(1)
        
    # 下載
    html = scraper.fetch_issue(issue_id)
    if not html:
        print("[失敗] 讀取案件失敗。")
        sys.exit(1)
        
    # 檢查是否讀到正確的案件內容
    if "登入" in html and "username" in html:
        print("[錯誤] 登入 Session 已失效，或頁面仍停留在登入頁。")
        sys.exit(1)
        
    # 解析
    print("[系統] 正在解析網頁內容...")
    issue_data = scraper.parse_issue_html(html, issue_id)
    
    # 檢查是否設定了暫時的 Local Vault
    vault_path = OBSIDIAN_VAULT_PATH
    if not os.path.exists(vault_path):
        print(f"[提示] 找不到設定的 Vault 路徑: {vault_path}")
        print("將在當前目錄建立 'SecondBrain_Local' 資料夾進行測試歸檔。")
        vault_path = os.path.abspath("SecondBrain_Local")
        
    # 存檔
    scraper.save_to_obsidian(issue_data, vault_path)
    print("=== 同步作業順利結束 ===")

if __name__ == "__main__":
    main()
