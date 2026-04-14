from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent
JSX_PATH = BASE_DIR / "audit-dashboard.jsx"
HTML_PATH = BASE_DIR / "index.html"
FRONTEND_SRC_DIR = BASE_DIR / "frontend_src"
FRONTEND_MANIFEST = FRONTEND_SRC_DIR / "manifest.txt"
APP_TITLE = "柏連企業股份有限公司 ISO 9001:2015 品質稽核工作台"


def load_jsx_source() -> str:
    if FRONTEND_MANIFEST.exists():
        chunks = []
        for line in FRONTEND_MANIFEST.read_text(encoding="utf-8-sig").splitlines():
            item = line.strip()
            if not item or item.startswith("#"):
                continue
            source_path = (FRONTEND_SRC_DIR / item).resolve()
            source_path.relative_to(FRONTEND_SRC_DIR.resolve())
            chunks.append(source_path.read_text(encoding="utf-8-sig"))
        return "\n\n".join(chunks)
    return JSX_PATH.read_text(encoding="utf-8-sig")


def build_source_bundle(raw_jsx: str) -> str:
    jsx_content = re.sub(r'^import\s+.*?from\s+["\']react["\'];\s*\n', "", raw_jsx, flags=re.MULTILINE)
    return jsx_content.replace("export default function App()", "function App()")


raw_jsx = load_jsx_source()
jsx_bundle = build_source_bundle(raw_jsx)
JSX_PATH.write_text(raw_jsx, encoding="utf-8")

html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{APP_TITLE}</title>
  <script src="./vendor/react.production.min.js"></script>
  <script src="./vendor/react-dom.production.min.js"></script>
  <script src="./vendor/babel.min.js"></script>
  <script src="./vendor/xlsx.full.min.js"></script>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #0a0f1e;
      color: #e2e8f0;
      font-family: 'Microsoft JhengHei', 'PingFang TC', 'Noto Sans TC', sans-serif;
    }}
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: rgba(255,255,255,0.03); }}
    ::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.15); border-radius: 3px; }}
    @media print {{
      body {{ background: #fff; color: #000; }}
      #report-content, #report-content * {{ font-family: 'Microsoft JhengHei', 'PingFang TC', 'Noto Sans TC', sans-serif !important; }}
    }}
  </style>
</head>
<body>
  <div id="root"></div>
  <script type="text/babel" data-presets="react">
    const {{ useState, useEffect, useRef }} = React;
{jsx_bundle}
    const root = ReactDOM.createRoot(document.getElementById("root"));
    root.render(<App />);
  </script>
</body>
</html>
"""

HTML_PATH.write_text(html, encoding="utf-8")
print(f"Built {HTML_PATH}")
print(f"Bundled source: {JSX_PATH}")
print(f"Size: {len(html)} bytes")
