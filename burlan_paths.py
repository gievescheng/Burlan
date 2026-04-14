from __future__ import annotations

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def pick_burlan_master_list(base_dir: Path | None = None) -> Path:
    root = base_dir or BASE_DIR
    candidates = [
        root.parent / "burlan_master_latest_confirmed.xlsx",
        root.parent / "柏連正式文件主清單_已確認最新版.xlsx",
        root.parent / "柏連正式文件主清單.xlsx",
    ]
    for path in candidates:
        if path.exists():
            return path
    return candidates[-1]


BURLAN_MASTER_LIST_PATH = pick_burlan_master_list(BASE_DIR)
BURLAN_OBJECTIVE_DIR = BASE_DIR.parent / "3 目標管理程序" / "記錄"
BURLAN_AUDIT_DIR = BASE_DIR.parent / "17內部稽核管理程序" / "記錄"
BURLAN_CALIBRATION_DIR = BASE_DIR.parent / "9量測資源管理程序"
BURLAN_EQUIPMENT_DIR = BASE_DIR.parent / "8設施設備管理程序"
BURLAN_SUPPLIER_DIR = BASE_DIR.parent / "12採購及供應商管理程序"
BURLAN_THIRD_LEVEL_DIR = BASE_DIR.parent / "三階文件"
