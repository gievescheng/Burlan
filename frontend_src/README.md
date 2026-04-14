# 前端來源說明

這個資料夾是柏連前端的可拆分來源區。

## 使用方式
- `manifest.txt` 決定建置順序
- `build_html.py` 會依序合併來源檔
- 合併後會輸出：
  - `audit-dashboard.jsx`
  - `index.html`

## 目前原則
- 先把前端拆成可維護的來源檔
- 不改變既有畫面與功能行為
- `audit-dashboard.jsx` 視為建置產物，不再當唯一手改來源
