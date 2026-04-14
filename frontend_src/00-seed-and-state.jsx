import { useState, useEffect, useRef } from "react";

// ─── INITIAL DATA ─────────────────────────────────────────────────────────────
// 儀器資料來源：9量測資源管理程序/記錄/9.1量規儀器一覽表、9.2量規儀器履歷表
// 初始畫面只作備援顯示，實際仍以 API 載入柏連來源資料為主
const initialInstruments = [
  { id: "BRA-01", name: "傅立葉轉換紅外線譜儀系統", type: "FTIR",
    location: "品管課", keeper: "程鼎智", brand: "",
    model: "", serialNo: "", calibMethod: "免校",
    calibratedDate: "", intervalDays: 0,
    status: "免校正", needsMSA: false },
  { id: "BRA-02", name: "多功能測量儀器", type: "量測儀器",
    location: "品管課", keeper: "程鼎智", brand: "",
    model: "", serialNo: "", calibMethod: "內校",
    calibratedDate: "2024-08-01", intervalDays: 183,
    status: "合格", needsMSA: false },
  { id: "BRA-06", name: "攜帶型數位屈折度計", type: "屈折度計",
    location: "品管課", keeper: "程鼎智", brand: "",
    model: "", serialNo: "", calibMethod: "內校",
    calibratedDate: "2024-09-02", intervalDays: 183,
    status: "合格", needsMSA: false },
];

const initialDocuments = [];

const initialManuals = [];

const initialTraining = [
  { id: "EMP-001", name: "劉哲驊", dept: "管理部", role: "協理", hireDate: "2021-07-01", trainings: [
    { course: "ISO9001品質管理標準教育訓練班", date: "", type: "外訓", result: "合格", cert: "無" },
    { course: "ISO9001內部稽核員訓練", date: "", type: "外訓", result: "合格", cert: "無" },
    { course: "品質管理程序文件訓練", date: "", type: "內訓", result: "合格", cert: "無" },
  ]},
  { id: "EMP-002", name: "蔡有為", dept: "管理部", role: "部長", hireDate: "2021-07-01", trainings: [
    { course: "ISO9001品質管理標準教育訓練班", date: "", type: "外訓", result: "合格", cert: "無" },
    { course: "ISO9001內部稽核員訓練", date: "", type: "外訓", result: "合格", cert: "無" },
    { course: "品質管理程序文件訓練", date: "", type: "內訓", result: "合格", cert: "無" },
  ]},
  { id: "EMP-003", name: "林佑翰", dept: "業務部", role: "組長", hireDate: "2022-09-01", trainings: [
    { course: "ISO9001品質管理標準教育訓練班", date: "", type: "外訓", result: "合格", cert: "無" },
    { course: "ISO9001內部稽核員訓練", date: "", type: "外訓", result: "合格", cert: "無" },
    { course: "品質管理程序文件訓練", date: "", type: "內訓", result: "合格", cert: "無" },
  ]},
  { id: "EMP-004", name: "詹博智", dept: "生產課", role: "組長", hireDate: "2024-03-01", trainings: [
    { course: "ISO9001品質管理標準教育訓練班", date: "", type: "外訓", result: "合格", cert: "無" },
    { course: "ISO9001內部稽核員訓練", date: "", type: "外訓", result: "合格", cert: "無" },
    { course: "品質管理程序文件訓練", date: "", type: "內訓", result: "合格", cert: "無" },
    { course: "量測儀器校正與管理訓練", date: "", type: "外訓", result: "合格", cert: "無" },
  ]},
  { id: "EMP-005", name: "程鼎智", dept: "品管課", role: "課長", hireDate: "2021-07-01", trainings: [
    { course: "ISO9001品質管理標準教育訓練班", date: "", type: "外訓", result: "合格", cert: "無" },
    { course: "ISO9001內部稽核員訓練", date: "", type: "外訓", result: "合格", cert: "無" },
    { course: "品質管理程序文件訓練", date: "", type: "內訓", result: "合格", cert: "無" },
  ]},
  { id: "EMP-006", name: "吳澤仁", dept: "業務部", role: "部長", hireDate: "2021-07-01", trainings: [
    { course: "ISO9001品質管理標準教育訓練班", date: "", type: "外訓", result: "合格", cert: "無" },
    { course: "ISO9001內部稽核員訓練", date: "", type: "外訓", result: "合格", cert: "無" },
    { course: "品質管理程序文件訓練", date: "", type: "內訓", result: "合格", cert: "無" },
  ]},
  { id: "EMP-007", name: "林育陞", dept: "", role: "", hireDate: "", trainings: [
    { course: "產品相關作業操作及檢驗標準訓練", date: "", type: "內訓", result: "合格", cert: "無" },
    { course: "消防常識與火災預防", date: "", type: "內訓", result: "合格", cert: "無" },
  ]},
  { id: "EMP-008", name: "楊麗璇", dept: "", role: "", hireDate: "", trainings: [
    { course: "產品相關作業操作及檢驗標準訓練", date: "", type: "內訓", result: "合格", cert: "無" },
    { course: "消防常識與火災預防", date: "", type: "內訓", result: "合格", cert: "無" },
  ]},
  { id: "EMP-009", name: "朱姿霖", dept: "", role: "", hireDate: "", trainings: [
    { course: "產品相關作業操作及檢驗標準訓練", date: "", type: "內訓", result: "合格", cert: "無" },
  ]},
  { id: "EMP-010", name: "陳宥穎", dept: "", role: "", hireDate: "", trainings: [
    { course: "產品相關作業操作及檢驗標準訓練", date: "", type: "內訓", result: "合格", cert: "無" },
  ]},
];

// 設備資料來源：8 設施設備管理程序/記錄/8.1機器設備一覽表.xlsx
// 初始畫面只作暫存顯示，實際仍以 API 載入柏連來源資料為主
const initialEquipment = [
  { id: "BRM-001", name: "攪拌槽", location: "管理部", lastMaintenance: "", intervalDays: 30, nextItems: ["外觀清潔", "檢查電線完整無破損", "檢查配件無缺少", "運作正常無異音", "洩水閥功能確認"], sourceSystem: "burlan_equipment_records" },
  { id: "BRM-002", name: "過濾機", location: "管理部", lastMaintenance: "", intervalDays: 30, nextItems: ["外觀清潔", "檢查電線完整無破損", "檢查配件無缺少", "運作正常無異音"], sourceSystem: "burlan_equipment_records" },
  { id: "BRM-003", name: "純水系統", location: "管理部", lastMaintenance: "", intervalDays: 30, nextItems: ["外觀清潔", "檢查電線完整無破損", "檢查配件無缺少", "運作正常無異音"], sourceSystem: "burlan_equipment_records" },
  { id: "BRM-004", name: "PLC進料機", location: "管理部", lastMaintenance: "", intervalDays: 30, nextItems: ["外觀清潔", "檢查電線完整無破損", "檢查配件無缺少", "運作正常無異音"], sourceSystem: "burlan_equipment_records" },
  { id: "BRM-005", name: "PLC裝填機", location: "管理部", lastMaintenance: "", intervalDays: 30, nextItems: ["外觀清潔", "檢查電線完整無破損", "檢查配件無缺少", "運作正常無異音"], sourceSystem: "burlan_equipment_records" },
  { id: "BRM-006", name: "自動壓蓋機", location: "管理部", lastMaintenance: "", intervalDays: 30, nextItems: ["外觀清潔", "檢查電線完整無破損", "檢查配件無缺少", "運作正常無異音"], sourceSystem: "burlan_equipment_records" },
  { id: "BRM-007", name: "二合一排煙機", location: "管理部", lastMaintenance: "", intervalDays: 30, nextItems: ["外觀清潔", "檢查電線完整無破損", "檢查配件無缺少", "運作正常無異音"], sourceSystem: "burlan_equipment_records" },
  { id: "BRM-008", name: "電動堆高機", location: "管理部", lastMaintenance: "", intervalDays: 30, nextItems: ["外觀清潔", "檢查電線完整無破損", "檢查配件無缺少", "運作正常無異音"], sourceSystem: "burlan_equipment_records" },
];

// 供應商資料來源：12 採購及供應商管理程序/記錄/12.2供應商評鑑表(*).docx
// 初始畫面只作暫存顯示，實際仍以 API 載入柏連來源資料為主
const initialSuppliers = [
  { id: "SUP-BR-001", name: "良器", category: "採購供應商", contact: "", lastEvalDate: "2025-12-31", evalScore: 95, evalResult: "滿意", evalIntervalDays: 183, issues: [], sourceSystem: "burlan_supplier_records" },
  { id: "SUP-BR-002", name: "合億", category: "採購供應商", contact: "", lastEvalDate: "2025-12-31", evalScore: 93, evalResult: "滿意", evalIntervalDays: 183, issues: [], sourceSystem: "burlan_supplier_records" },
  { id: "SUP-BR-003", name: "于正瓶罐", category: "採購供應商", contact: "", lastEvalDate: "2025-12-31", evalScore: 85, evalResult: "普通", evalIntervalDays: 183, issues: ["服務態度：普通", "交期配合：普通"], sourceSystem: "burlan_supplier_records" },
];

const ENABLE_ENVIRONMENT_MODULE = false;

// 不符合資料來源：15 不符合及矯正措施管理程序/記錄/15.1.1~15.1.2 不符合及矯正措施報告表.docx
// 共2筆有文件記錄；原假造的5筆（NC-2025-001~005）已移除
const initialNonConformances = [
  { id: "NC-2025-001", date: "2025-11-12",
    dept: "品管課", type: "人員作業",
    description: "在品檢室進行作業時，不慎撞到已洗完待檢測的玻璃，導致掉落地板破裂。",
    severity: "輕微",
    rootCause: "品管作業員在作業時不慎撞到 FOSB 盒，導致盒子掉落並摔破玻璃片。",
    correctiveAction: "作業員立即清理現場並確認無玻璃碎片殘留，另行包裝破碎玻璃片至包裝袋並隔離儲存；主管提醒作業員注意各物品擺放。",
    responsible: "林佑翰", dueDate: "", status: "已關閉", closeDate: "2025-11-12", effectiveness: "有效" },
  { id: "NC-2026-001", date: "2026-01-28",
    dept: "品檢課", type: "人員作業",
    description: "品檢人員於 AOI 檢驗後取出 NG 品放置 FOSB，中途玻璃脫落導致破片。",
    severity: "輕微",
    rootCause: "AOI 測試判定 NG 後，取出放置 NG FOSB 時操作不慎，玻璃脫落破片。",
    correctiveAction: "加強作業員操作訓練，明確規範 FOSB 取放動作要領，並更新作業 SOP。",
    responsible: "朱姿霖", dueDate: "", status: "處理中", closeDate: "", effectiveness: "" },
];

// 稽核計畫資料來源：9 內部稽核管理程序/記錄/內部稽核114年度/
// 9.5 品質稽核報告書（114/09/04~05 全廠，稽核員蔡有為，20 OK 4 NG）
// 9.4 內部稽核矯正通知單（114/06/23 品管課，稽核員蔡有為，發出矯正通知）
// 原假造的9筆（IA-2025-01~06, IA-2026-01~03）已移除
const initialAuditPlans = [
  { id: "IA-2025-01", year: 2025, period: "下半年", scheduledDate: "2025-09-04",
    dept: "全廠", scope: "MM-01,MP-01,MP-02,MP-04,MP-17,MP-18",
    auditor: "蔡有為", auditee: "程鼎智",
    status: "已完成", actualDate: "2025-09-05", findings: 4, ncCount: 1 },
  { id: "IA-2025-02", year: 2025, period: "上半年", scheduledDate: "2025-06-23",
    dept: "品管課", scope: "MP-16,MP-19,MP-20",
    auditor: "蔡有為", auditee: "程鼎智",
    status: "已完成", actualDate: "2025-06-23", findings: 1, ncCount: 1 },
];

// 環境監測：查無 6 工作環境管理程序/記錄/ 下的實際環境監測紀錄
// 原假造的9筆（ENV-001~009）已移除，待實際量測後再填入
const initialEnvRecords = [];

const initialProdRecords = [
  { lot:"LOT-20260301-A", customer:"TSMC", product:"Wafer Clean", input:1200, good:1180, defect:20, yieldRate:98.3, defectReasons:["particle","scratch"], operator:"Operator A", note:"first article checked" },
  { lot:"LOT-20260302-B", customer:"VIS", product:"Final Clean", input:860, good:822, defect:38, yieldRate:95.6, defectReasons:["AOI NG","edge crack"], operator:"Operator B", note:"codes classified" },
];

const initialQualityRecords = [
  { materialName:"IPA Cleaner", batchNo:"MAT-202603-01", quantity:"20L", spec:"PH 6.5-7.5 / density 0.78-0.80", inspQty:"3 bottles", ph:"7.0", density:"0.79", ri:"1.37", rotation:"0.0", result:"PASS", note:"within spec" },
  { materialName:"Developer", batchNo:"MAT-202603-02", quantity:"10L", spec:"PH 10.5-11.0 / density 1.01-1.05", inspQty:"2 bottles", ph:"10.8", density:"1.03", ri:"1.42", rotation:"0.0", result:"PASS", note:"sample checked" },
];


