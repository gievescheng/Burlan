# 柏連 QMS / ISO 9001 自動稽核系統

這個專案是柏連企業股份有限公司的 ISO 9001 文件管理與稽核工作台。

它的目標不是重做一套大型 ERP，而是直接站在柏連既有的正式程序文件、記錄表單與年度稽核資料上，逐步整理出一套可維護、可追蹤、可試跑的 QMS 系統。

## 專案重點
- 以柏連正式文件為主資料來源，不直接憑系統假資料判定正式版。
- 已整合的主線模組包括：
  - 正式文件主清單
  - 文件管理 / 文件庫
  - 稽核計畫
  - 不符合 / 矯正措施
  - 校正管理
  - 設備保養
  - 供應商管理
  - KPI / 管理審查輔助
  - AI 文件工作台
- 柏連與其他舊專案的執行資料已切開，執行期私有資料固定使用 `burlan_qms`。

## 專案位置
- 柏連原始文件根目錄：
  `C:\Users\USER\Documents\Codex\ISO 9001 SOP-柏連正式版`
- 柏連系統程式目錄：
  `C:\Users\USER\Documents\Codex\ISO 9001 SOP-柏連正式版\_柏連稽核系統`

## 系統啟動方式
最簡單的方式是直接雙擊：

- `C:\Users\USER\Documents\Codex\ISO 9001 SOP-柏連正式版\_柏連稽核系統\啟動柏連稽核系統.bat`

如果瀏覽器沒有自動開啟，再手動打開：

- `http://127.0.0.1:8888/`

## 專案結構
### 前端
前端原本是單一大檔，現在已拆成模組化來源，建置後輸出成 `audit-dashboard.jsx` 與 `index.html`。

- `frontend_src/00-seed-and-state.jsx`
  - 共用初始資料、狀態與基礎工具
- `frontend_src/10-app.jsx`
  - App 主整合層
- `frontend_src/20-documents.jsx`
  - 文件管理、文件庫、ISO 文件階層
- `frontend_src/30-audit-workflow.jsx`
  - 稽核計畫、不符合管理
- `frontend_src/40-operations.jsx`
  - 校正管理
- `frontend_src/41-equipment-supplier.jsx`
  - 設備保養、供應商管理
- `frontend_src/50-dashboard-kpi.jsx`
  - 主控台、KPI、圖表
- `frontend_src/60-training-production.jsx`
  - 訓練管理、生產 / 品質紀錄相關頁面
- `frontend_src/70-ai-report.jsx`
  - AI 工作台、通知提醒、記錄匯出
- `frontend_src/manifest.txt`
  - 前端建置順序
- `build_html.py`
  - 將模組組裝成 `audit-dashboard.jsx` 與 `index.html`

### 後端
後端以 Flask 為主入口，並把處理邏輯拆成多個 handler。

- `server.py`
  - 系統主入口
- `server_handlers_documents.py`
  - 文件、附件、正式文件主清單相關 API
- `server_handlers_operations.py`
  - 稽核、不符合、校正、設備、供應商等作業 API
- `server_handlers_integrations.py`
  - Notion、Google Calendar 等整合
- `burlan_paths.py`
  - 柏連原始文件來源路徑集中管理
- `burlan_document_sources.py`
  - 正式文件主清單、版本選擇、候選檔案對應邏輯
- `ops_data.py`
  - 系統補充紀錄、匯入解析、附件查找
- `ops_seed_defaults.py`
  - 系統預設資料定義

### V2 Backend
`v2_backend/` 是較結構化的後端區塊，包含：

- API / schema / service / repository 分層
- PDF 解析器整合
- Alembic migration
- 單元測試與 smoke test

## 主要資料來源規則
這是專案最重要的維護原則。

- 正式文件：
  以 `柏連正式文件主清單` 為主
- 稽核計畫：
  以 `17 內部稽核管理程序` 年度記錄為主
- 不符合：
  以 `20 不符合及矯正措施報告表` 為主
- 校正：
  以 `9.1 量規儀器一覽表` 與 `9.2 量規儀器履歷表` 為主
- 設備保養：
  以 `8 設施設備管理程序` 記錄為主
- 供應商：
  以 `12 採購及供應商管理程序` 記錄與三階供應商清單為主
- KPI：
  以 `3.1 品質目標管制表` 為主檔，其他記錄作為證據來源

固定優先順序如下：

1. 原始受控文件優先
2. 系統補充紀錄只做補充與追蹤
3. 不直接反寫原始正式 Word / Excel / PDF
4. 遇到版本衝突或缺欄位時，標記待確認，不自動猜測

## 本地執行資料
這個專案的執行期私有資料不放在 Git 內。

目前固定使用：

- `%APPDATA%\AutoAudit\burlan_qms`

這樣可以避免和其他舊專案共用執行資料，降低互相污染風險。

## 開發常用指令
在專案根目錄執行：

```powershell
python build_html.py
python -m unittest discover -s v2_backend/tests -t .
python scripts\check_runtime_boundary.py
python scripts\check_text_encoding.py
python scripts\scan_legacy_terms.py
```

用途說明：

- `build_html.py`
  - 重新組裝前端輸出
- `unittest discover`
  - 跑目前整包測試
- `check_runtime_boundary.py`
  - 檢查執行資料是否仍留在專案內
- `check_text_encoding.py`
  - 檢查文字檔是否為 UTF-8
- `scan_legacy_terms.py`
  - 掃描是否還殘留 `JEPE / 潔沛` 等舊專案字樣

## Git 與版本管理建議
- 只提交 `_柏連稽核系統` 這個系統專案，不要把整包柏連原始正式文件一起當成程式碼提交。
- Office 暫存檔、執行期資料、資料庫檔、快取檔都不應提交。
- 若要新增功能，請先確認：
  - 它的正式資料來源是什麼
  - 它是否會覆蓋原始正式文件
  - 是否需要補測試

## 其他說明文件
如果你要更深入了解專案，建議先看這幾份：

- `README_資料邊界與來源規則.md`
- `README_前後端模組對照說明.md`
- `README_Git工作區使用說明.md`
- `README_剩餘技術債與後續建議.md`

## 目前維護原則
- 不大重寫
- 先保住已可用功能
- 以柏連正式程序文件為主
- 小步整理結構
- 每次改動都盡量可測、可回歸、可追蹤

## 給新開發者的第一個建議
先不要急著新增功能，先做這三件事：

1. 先跑一次測試與檢查腳本
2. 先看清楚資料來源規則
3. 先確認你要改的是「系統補充資料」還是「原始正式來源對應邏輯」

這樣比較不會一改就把柏連正式流程弄亂。
