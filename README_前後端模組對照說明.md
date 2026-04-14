# 柏連前後端模組對照說明

## 這份文件的用途
- 幫你快速知道每個功能在哪個檔案。
- 之後如果要修功能、查問題、交接給別人，先看這份最快。

## 前端模組

### 基礎與共用
- [00-seed-and-state.jsx](C:\Users\USER\Documents\Codex\ISO 9001 SOP-柏連正式版\_柏連稽核系統\frontend_src\00-seed-and-state.jsx)
  - 共用狀態
  - 共用工具函式
  - 資料格式整理與轉換

### 文件相關
- [20-documents.jsx](C:\Users\USER\Documents\Codex\ISO 9001 SOP-柏連正式版\_柏連稽核系統\frontend_src\20-documents.jsx)
  - 文件管理
  - 文件庫
  - ISO 文件階層整理

### 稽核流程相關
- [30-audit-workflow.jsx](C:\Users\USER\Documents\Codex\ISO 9001 SOP-柏連正式版\_柏連稽核系統\frontend_src\30-audit-workflow.jsx)
  - 不符合管理
  - 稽核計畫
  - 稽核附件
  - 年度附件包
  - 稽核與不符合串接

### 日常作業相關
- [40-operations.jsx](C:\Users\USER\Documents\Codex\ISO 9001 SOP-柏連正式版\_柏連稽核系統\frontend_src\40-operations.jsx)
  - 校正管理

- [41-equipment-supplier.jsx](C:\Users\USER\Documents\Codex\ISO 9001 SOP-柏連正式版\_柏連稽核系統\frontend_src\41-equipment-supplier.jsx)
  - 設備保養
  - 供應商管理

### 主控台與 KPI
- [50-dashboard-kpi.jsx](C:\Users\USER\Documents\Codex\ISO 9001 SOP-柏連正式版\_柏連稽核系統\frontend_src\50-dashboard-kpi.jsx)
  - 主控台
  - KPI 儀表板
  - 圖表元件

### 訓練與生產品質
- [60-training-production.jsx](C:\Users\USER\Documents\Codex\ISO 9001 SOP-柏連正式版\_柏連稽核系統\frontend_src\60-training-production.jsx)
  - 訓練管理
  - 環境監測
  - 生產記錄
  - 品質記錄

### AI 與報表
- [70-ai-report.jsx](C:\Users\USER\Documents\Codex\ISO 9001 SOP-柏連正式版\_柏連稽核系統\frontend_src\70-ai-report.jsx)
  - 通知提醒
  - AI 工作台
  - 記錄匯出

### 主整合入口
- [10-app.jsx](C:\Users\USER\Documents\Codex\ISO 9001 SOP-柏連正式版\_柏連稽核系統\frontend_src\10-app.jsx)
  - App 主架構
  - 分頁切換
  - 全域整合
  - 尚未拆出的零星邏輯

## 後端模組

### 主伺服器入口
- [server.py](C:\Users\USER\Documents\Codex\ISO 9001 SOP-柏連正式版\_柏連稽核系統\server.py)
  - Flask 路由入口
  - 各模組對外 API 掛載點

### 文件處理
- [server_handlers_documents.py](C:\Users\USER\Documents\Codex\ISO 9001 SOP-柏連正式版\_柏連稽核系統\server_handlers_documents.py)
  - 文件檢視
  - 文件下載
  - 文字預覽
  - 柏連正式文件主清單 API

### 作業與紀錄
- [server_handlers_operations.py](C:\Users\USER\Documents\Codex\ISO 9001 SOP-柏連正式版\_柏連稽核系統\server_handlers_operations.py)
  - 校正
  - 訓練
  - 設備
  - 供應商
  - 不符合
  - 稽核計畫
  - 記錄匯入與匯出

### 外部整合
- [server_handlers_integrations.py](C:\Users\USER\Documents\Codex\ISO 9001 SOP-柏連正式版\_柏連稽核系統\server_handlers_integrations.py)
  - Notion
  - Google 行事曆

### 柏連正式來源路徑
- [burlan_paths.py](C:\Users\USER\Documents\Codex\ISO 9001 SOP-柏連正式版\_柏連稽核系統\burlan_paths.py)
  - 柏連主要來源資料夾位置

- [burlan_document_sources.py](C:\Users\USER\Documents\Codex\ISO 9001 SOP-柏連正式版\_柏連稽核系統\burlan_document_sources.py)
  - 正式文件主清單讀取
  - 文件名稱正規化
  - PDF / Word 對應

## 資料層
- [ops_data.py](C:\Users\USER\Documents\Codex\ISO 9001 SOP-柏連正式版\_柏連稽核系統\ops_data.py)
  - 系統補充紀錄讀寫
  - 匯入解析
  - 附件查找
  - 路徑對應

- [ops_seed_defaults.py](C:\Users\USER\Documents\Codex\ISO 9001 SOP-柏連正式版\_柏連稽核系統\ops_seed_defaults.py)
  - 系統預設資料
  - 目前盡量保持為空，避免歷史假資料干擾

## 報表與產生器
- [record_engine.py](C:\Users\USER\Documents\Codex\ISO 9001 SOP-柏連正式版\_柏連稽核系統\record_engine.py)
  - 記錄模板產生

- [record_engine_catalog.py](C:\Users\USER\Documents\Codex\ISO 9001 SOP-柏連正式版\_柏連稽核系統\record_engine_catalog.py)
  - 模板目錄與對照

- [generate_record.py](C:\Users\USER\Documents\Codex\ISO 9001 SOP-柏連正式版\_柏連稽核系統\generate_record.py)
  - Excel 記錄產生

## 如果你之後要找功能，建議這樣找
- 找文件問題：
  先看 `20-documents.jsx` 和 `server_handlers_documents.py`
- 找稽核或不符合：
  先看 `30-audit-workflow.jsx` 和 `server_handlers_operations.py`
- 找校正：
  先看 `40-operations.jsx`
- 找設備與供應商：
  先看 `41-equipment-supplier.jsx`
- 找 KPI 或主控台：
  先看 `50-dashboard-kpi.jsx`
- 找訓練、生產、品質記錄：
  先看 `60-training-production.jsx`
- 找通知、AI 工作台、記錄匯出：
  先看 `70-ai-report.jsx`
- 找正式來源規則：
  先看 `README_資料邊界與來源規則.md`
