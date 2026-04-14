// ?????? HELPERS ????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
const today = new Date();
today.setHours(0, 0, 0, 0);

function loadStoredState(key, fallback) {
  try {
    if (typeof window === "undefined") return fallback;
    const raw = window.localStorage.getItem(key);
    if (!raw) return fallback;
    const parsed = JSON.parse(raw);
    return parsed ?? fallback;
  } catch (err) {
    console.warn("Failed to load " + key, err);
    return fallback;
  }
}

function saveStoredState(key, value) {
  try {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch (err) {
    console.warn("Failed to save " + key, err);
  }
}

async function apiJson(url, options = {}) {
  const response = await fetch(url, options);
  let payload = {};
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    payload = await response.json();
  } else {
    const bodyText = await response.text();
    payload = bodyText ? { message: bodyText } : {};
  }
  if (!response.ok) {
    throw new Error(payload.error || payload.message || `Request failed (${response.status})`);
  }
  return payload;
}

async function apiDeleteWithFallback(url, fallbackUrl) {
  const response = await fetch(url, { method: "DELETE" });
  let payload = {};
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    payload = await response.json();
  } else {
    const bodyText = await response.text();
    payload = bodyText ? { message: bodyText } : {};
  }
  if (response.ok) return payload;
  if (response.status === 405 && fallbackUrl) {
    return apiJson(fallbackUrl, { method: "POST" });
  }
  throw new Error(payload.error || payload.message || `Request failed (${response.status})`);
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function buildManagedFileUrl(path) {
  return path ? toAbsoluteAppUrl(`/api/files/view?path=${encodeURIComponent(path)}`) : "";
}

function toAbsoluteAppUrl(url) {
  const text = String(url || "").trim();
  if (!text) return "";
  if (/^https?:\/\//i.test(text)) return text;
  if (typeof window === "undefined") return text;
  if (text.startsWith("/")) return `${window.location.origin}${text}`;
  return text;
}

function normalizeDisplayDate(value) {
  const text = String(value || "").trim();
  if (!text) return "";
  if (/^\d{4}\.\d{2}\.\d{2}$/.test(text)) {
    return text.replaceAll(".", "-");
  }
  return text;
}

function mapBurlanMasterToDocument(item) {
  const sourcePath = String(item.path || "").trim();
  const pdfSourcePath = String(item.pdf_path || "").trim();
  const wordSourcePath = String(item.word_path || "").trim();
  const fileType = String(item.file_type || "").trim().toLowerCase();
  const managedUrl = buildManagedFileUrl(sourcePath);
  return {
    id: item.id || "",
    name: item.name || "",
    type: /^MM-/i.test(item.id || "") ? "??????" : "??????",
    version: item.version || "",
    department: item.department || "",
    createdDate: normalizeDisplayDate(item.issue_date || ""),
    author: "",
    retentionYears: 16,
    pdfPath: pdfSourcePath ? buildManagedFileUrl(pdfSourcePath) : (fileType === "pdf" ? managedUrl : ""),
    docxPath: wordSourcePath ? buildManagedFileUrl(wordSourcePath) : ((fileType === "docx" || fileType === "doc") ? managedUrl : ""),
    rawPath: sourcePath,
    rawPdfPath: pdfSourcePath,
    rawDocxPath: wordSourcePath,
    selectedFile: item.selected_file || "",
    folderPath: item.folder_path || "",
    nextReview: normalizeDisplayDate(item.issue_date || ""),
    reviewStatus: item.review_status || "",
    reviewReason: item.review_reason || "",
    sourceSystem: item.source_system || "burlan_official_master",
  };
}

function getInstrumentNextCalibrationDate(item) {
  if (item?.status === "?????) return "";
  const calibratedDate = normalizeDisplayDate(item?.calibratedDate || "");
  const intervalDays = Number(item?.intervalDays || 0);
  if (calibratedDate && intervalDays > 0) {
    return normalizeDisplayDate(addDays(calibratedDate, intervalDays));
  }
  return normalizeDisplayDate(item?.nextCalibration || "");
}

function mapCalibrationInstrument(item) {
  const intervalDays = Number(item.intervalDays || 0);
  const calibratedDate = normalizeDisplayDate(item.calibratedDate || "");
  const nextCalibration = getInstrumentNextCalibrationDate({ ...item, calibratedDate, intervalDays });
  return {
    id: item.id || "",
    name: item.name || "",
    type: item.type || "",
    location: item.location || "",
    keeper: item.keeper || "",
    brand: item.brand || "",
    model: item.model || "",
    serialNo: item.serialNo || "",
    calibMethod: item.calibMethod || "",
    calibratedDate,
    intervalDays,
    status: item.status || "?綽?⊿?,
    nextCalibration,
    needsMSA: Boolean(item.needsMSA),
    frequencyLabel: item.frequencyLabel || "",
    registeredDate: normalizeDisplayDate(item.registeredDate || ""),
    manualRecordId: item.manualRecordId || "",
    manualUpdatedAt: normalizeDisplayDate(String(item.manualUpdatedAt || "").slice(0, 10)),
    manualNote: item.manualNote || "",
    manualOperator: item.manualOperator || "",
    rawInventoryPath: item.inventoryPath || "",
    rawRecordPath: item.recordPath || "",
    rawLatestReportPath: item.latestReportPath || "",
    rawLatestPlanPath: item.latestPlanPath || "",
    inventoryPath: item.inventoryPath ? buildManagedFileUrl(item.inventoryPath) : "",
    recordPath: item.recordPath ? buildManagedFileUrl(item.recordPath) : "",
    latestReportPath: item.latestReportPath ? buildManagedFileUrl(item.latestReportPath) : "",
    latestPlanPath: item.latestPlanPath ? buildManagedFileUrl(item.latestPlanPath) : "",
    sourceSystem: item.sourceSystem || "burlan_calibration_records",
  };
}

function normalizeDocumentCode(value) {
  return String(value || "").trim().toUpperCase().replace(/\s+/g, "");
}

function splitDocumentCodes(value) {
  const matches = String(value || "").toUpperCase().match(/\b(?:MM|MP|FR|RC)-\d{2}\b/g);
  return Array.from(new Set(matches || []));
}

function objectRows(value) {
  return Array.isArray(value) ? value.filter(item => item && typeof item === "object") : [];
}

function buildDocumentLookup(documents) {
  const lookup = new Map();
  (Array.isArray(documents) ? documents : []).forEach(doc => {
    const code = normalizeDocumentCode(doc?.id);
    if (code && !lookup.has(code)) lookup.set(code, doc);
  });
  return lookup;
}

function getDocumentDisplayLabel(doc) {
  if (!doc) return "";
  const statusText = doc.reviewStatus ? `??{doc.reviewStatus}?? : "";
  return `${doc.id} ${doc.name}${statusText}`;
}

function resolveRelatedDocument(value, documents) {
  const raw = String(value || "").trim();
  if (!raw) return { raw: "", code: "", doc: null };
  const lookup = buildDocumentLookup(documents);
  const normalized = normalizeDocumentCode(raw);
  if (lookup.has(normalized)) {
    return { raw, code: normalized, doc: lookup.get(normalized) };
  }
  const firstCode = splitDocumentCodes(raw)[0] || normalized;
  return { raw, code: firstCode, doc: lookup.get(firstCode) || null };
}

function resolveScopeDocuments(scope, documents) {
  const lookup = buildDocumentLookup(documents);
  const codes = splitDocumentCodes(scope);
  const matchedDocuments = [];
  const unmatchedCodes = [];
  codes.forEach(code => {
    const matched = lookup.get(code);
    if (matched) matchedDocuments.push(matched);
    else unmatchedCodes.push(code);
  });
  return { codes, matchedDocuments, unmatchedCodes };
}

function isClosedNonConformanceStatus(status) {
  return ["????, "????, "Closed"].includes(String(status || "").trim());
}

function buildAuditPlanNcSummary(plan, nonConformances) {
  const auditId = String(plan?.id || "").trim();
  const relatedItems = objectRows(nonConformances).filter(item => String(item?.sourceAuditPlanId || "").trim() === auditId);
  const openItems = relatedItems.filter(item => !isClosedNonConformanceStatus(item?.status));
  const closedItems = relatedItems.filter(item => isClosedNonConformanceStatus(item?.status));
  const overdueItems = openItems.filter(item => daysUntil(item?.dueDate) < 0);
  const closedDates = closedItems.map(item => item?.closeDate).filter(Boolean).sort();
  return {
    items: relatedItems,
    total: relatedItems.length,
    open: openItems.length,
    closed: closedItems.length,
    overdue: overdueItems.length,
    latestCloseDate: closedDates.length ? closedDates[closedDates.length - 1] : "",
  };
}

function buildNonConformanceDraftFromAuditPlan(plan, documents) {
  const scopeInfo = resolveScopeDocuments(plan?.scope, documents || []);
  const baseDate = plan?.actualDate || plan?.scheduledDate || new Date().toISOString().split("T")[0];
  const relatedDocument = scopeInfo.matchedDocuments[0]?.id || scopeInfo.codes[0] || "";
  const severity = Number(plan?.ncCount || 0) > 0 || Number(plan?.findings || 0) >= 3 ? "??瞍? : "????;
  const deptText = String(plan?.dept || "").trim();
  const auditId = String(plan?.id || "").trim();
  const scopeText = String(plan?.scope || "").trim();

  return {
    seedKey: `${auditId || "audit"}-${Date.now()}`,
    date: baseDate,
    dept: deptText,
    type: "??刻麾??瘜?,
    description: auditId
      ? `?璇??鞎???${auditId} ????臬????骨??蟡暑??瘜???????????渲?蹐?
      : "?璇??鞎?????隡??ｇ????謓梁???????哨???????擗???,
    severity,
    rootCause: "",
    correctiveAction: "",
    responsible: String(plan?.auditee || "").trim(),
    dueDate: addDays(baseDate, 14),
    status: "?綽???,
    closeDate: "",
    effectiveness: "",
    relatedDocument,
    sourceAuditPlanId: auditId,
    sourceAuditScope: scopeText,
  };
}

function daysUntil(dateStr) {
  if (!dateStr) return 9999;
  const d = new Date(dateStr);
  d.setHours(0, 0, 0, 0);
  return Math.round((d - today) / 86400000);
}

function addDays(dateStr, days) {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return "";
  d.setDate(d.getDate() + days);
  return d.toISOString().split("T")[0];
}

function formatDate(dateStr) {
  if (!dateStr) return "?";
  const d = new Date(dateStr);
  return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, "0")}/${String(d.getDate()).padStart(2, "0")}`;
}

const opsFieldLabels = {
  scheduledDate: "????鈭?",
  dept: "???",
  scope: "?都赯梯??",
  auditor: "?都赯??,
  auditee: "?謅???,
  date: "?瞏???,
  description: "?????渲",
  responsible: "????,
  location: "???",
};

function formatMissingFields(fields) {
  return (fields || []).map(field => opsFieldLabels[field] || field).join("??);
}

function urgencyColor(days) {
  if (days < 0) return "#ef4444";
  if (days <= 14) return "#f97316";
  if (days <= 30) return "#eab308";
  return "#22c55e";
}

function urgencyLabel(days) {
  if (days === 9999) return "??迎??賹?";
  if (days < 0) return `??? ${Math.abs(days)} ?剖?;
  if (days === 0) return "??謑???";
  return `??${days} ?剖?;
}

function urgencyBg(days) {
  if (days < 0) return "rgba(239,68,68,0.12)";
  if (days <= 14) return "rgba(249,115,22,0.12)";
  if (days <= 30) return "rgba(234,179,8,0.12)";
  return "rgba(34,197,94,0.08)";
}

function getEmployeeTrainingExpiry(employee) {
  const topLevel = String(employee?.validUntil || "").trim();
  const entryDates = (employee?.trainings || []).map(item => String(item?.validUntil || "").trim()).filter(Boolean);
  const candidates = [topLevel, ...entryDates].filter(Boolean).sort();
  return candidates[0] || "";
}

function getEquipmentNextMaintenanceDate(equipment) {
  const lastMaintenance = normalizeDisplayDate(equipment?.lastMaintenance || "");
  const intervalDays = Number(equipment?.intervalDays || 0);
  if (lastMaintenance && intervalDays > 0) {
    return addDays(lastMaintenance, intervalDays);
  }
  return normalizeDisplayDate(equipment?.nextMaintenance || "");
}

function getSupplierScore(supplier) {
  const raw = supplier?.evalScore ?? supplier?.score ?? 0;
  const value = parseFloat(raw);
  return Number.isFinite(value) ? value : 0;
}

function buildCalendarLink(item) {
  const start = String(item.date || "").replaceAll("-", "");
  const end = String(addDays(item.date, 1) || "").replaceAll("-", "");
  const details = [
    item.module ? "???: " + item.module : "",
    item.summary ? "?謢?: " + item.summary : "",
    item.owner ? "?滿?? " + item.owner : "",
  ].filter(Boolean).join("\n");
  const params = new URLSearchParams({
    action: "TEMPLATE",
    text: item.title || "?都赯???",
    dates: start + "/" + end,
    details,
  });
  return "https://calendar.google.com/calendar/render?" + params.toString();
}

function collectNotificationItems({ instruments, documents, equipment, suppliers, nonConformances, auditPlans }) {
  const items = [];

  instruments.forEach(inst => {
    const date = addDays(inst.calibratedDate, inst.intervalDays);
    const days = daysUntil(date);
    if (!date || days > 30) return;
    items.push({
      key: "instrument-" + inst.id,
      sourceType: "instrument",
      priority: days < 0 ? "high" : days <= 14 ? "medium" : "low",
      title: "????踐???????" + inst.name,
      module: "MP-09 ??脰?????",
      date,
      summary: `${inst.id} ??瘣??亥縣??${formatDate(date)}??{urgencyLabel(days)}`,
      owner: inst.keeper || inst.location || "",
      days,
      statusText: urgencyLabel(days),
    });
  });

  documents.forEach(doc => {
    const date = addDays(doc.createdDate, 365);
    const days = daysUntil(date);
    if (!date || days > 45) return;
    items.push({
      key: "document-" + doc.id,
      sourceType: "document",
      priority: days < 0 ? "high" : "low",
      title: "??刻麾?虜瞍脫????? + doc.name,
      module: "MP-01 ??刻麾?謘??殷????,
      date,
      summary: `${doc.id} ?梁???皜豢撞??貔??${formatDate(date)}????蹌剜蝞??鈭??蹎??儐,
      owner: doc.author || doc.department || "",
      days,
      statusText: urgencyLabel(days),
    });
  });

  equipment.forEach(eq => {
    const date = getEquipmentNextMaintenanceDate(eq);
    const days = daysUntil(date);
    if (!date || days > 30) return;
    items.push({
      key: "equipment-" + eq.id,
      sourceType: "equipment",
      priority: days < 0 ? "high" : days <= 14 ? "medium" : "low",
      title: "?桀???踐??????? + eq.name,
      module: "MP-08 ?桀?謘?????",
      date,
      summary: `${eq.id} ??瘣駁豲???${formatDate(date)}??{urgencyLabel(days)}`,
      owner: eq.location || "",
      days,
      statusText: urgencyLabel(days),
    });
  });

  suppliers.forEach(supplier => {
    const date = addDays(supplier.lastEvalDate, supplier.evalIntervalDays);
    const days = daysUntil(date);
    if (!date || days > 30) return;
    items.push({
      key: "supplier-" + supplier.id,
      sourceType: "supplier",
      priority: days < 0 ? "high" : "low",
      title: "????????????" + supplier.name,
      module: "MP-12 ????????????",
      date,
      summary: `${supplier.id} ??瘣駁????${formatDate(date)}?謆?????${supplier.evalResult}`,
      owner: supplier.contact || supplier.category || "",
      days,
      statusText: urgencyLabel(days),
    });
  });

  nonConformances.forEach(nc => {
    const days = daysUntil(nc.dueDate);
    if (!nc.dueDate || nc.status === "???? || days > 30) return;
    items.push({
      key: "nc-" + nc.id,
      sourceType: "nc",
      priority: days < 0 ? "high" : "medium",
      title: "??餈????擗釭擐勗?? + nc.id,
      module: "MP-20 ??瘜?????餈????",
      date: nc.dueDate,
      summary: `${nc.dept}??{nc.description}`,
      owner: nc.responsible || "",
      days,
      statusText: urgencyLabel(days),
    });
  });

  auditPlans.forEach(plan => {
    const days = daysUntil(plan.scheduledDate);
    if (!plan.scheduledDate || plan.status === "???? || days > 30) return;
    items.push({
      key: "audit-" + plan.id,
      sourceType: "audit",
      priority: days < 0 ? "high" : "medium",
      title: "??貉?鞈?僚????? + plan.dept,
      module: "MP-17 ??貉?鞈?僚???",
      date: plan.scheduledDate,
      summary: `${plan.id} ?都赯望??? ${plan.auditee}???閰制 ${plan.auditor}`,
      owner: plan.auditor || "",
      days,
      statusText: urgencyLabel(days),
    });
  });

  return items.sort((a, b) => {
    const left = new Date(a.date).getTime();
    const right = new Date(b.date).getTime();
    return left - right;
  });
}

// ?????? SHARED COMPONENTS ????????????????????????????????????????????????????????????????????????????????????????????????????????????????
const uiTheme = {
  panel: "linear-gradient(180deg, rgba(15,23,42,0.94) 0%, rgba(15,23,42,0.78) 100%)",
  panelSoft: "rgba(255,255,255,0.035)",
  panelBorder: "rgba(148,163,184,0.16)",
  text: "#e2e8f0",
  textMuted: "#94a3b8",
  textSoft: "#64748b",
  shadow: "0 24px 60px rgba(2, 6, 23, 0.28)",
};

function buttonStyle(variant = "secondary", disabled = false) {
  const map = {
    primary: {
      background: "linear-gradient(135deg, #0284c7, #38bdf8)",
      color: "#fff",
      border: "none",
      boxShadow: "0 10px 24px rgba(14,165,233,0.22)",
    },
    secondary: {
      background: "rgba(255,255,255,0.045)",
      color: "#dbeafe",
      border: "1px solid rgba(148,163,184,0.18)",
      boxShadow: "none",
    },
    success: {
      background: "linear-gradient(135deg, #15803d, #22c55e)",
      color: "#fff",
      border: "none",
      boxShadow: "0 10px 24px rgba(34,197,94,0.18)",
    },
    warning: {
      background: "linear-gradient(135deg, #c2410c, #f97316)",
      color: "#fff",
      border: "none",
      boxShadow: "0 10px 24px rgba(249,115,22,0.18)",
    },
    danger: {
      background: "rgba(239,68,68,0.12)",
      color: "#fecaca",
      border: "1px solid rgba(239,68,68,0.24)",
      boxShadow: "none",
    },
  };
  return {
    ...map[variant],
    borderRadius: 12,
    cursor: disabled ? "not-allowed" : "pointer",
    padding: "10px 16px",
    fontSize: 13,
    fontWeight: 700,
    opacity: disabled ? 0.6 : 1,
    transition: "all 0.2s ease",
  };
}

const tableShellStyle = {
  overflowX: "auto",
  background: "rgba(2, 6, 23, 0.16)",
  border: "1px solid rgba(148,163,184,0.12)",
  borderRadius: 16,
};

const tableHeadCellStyle = {
  padding: "12px 10px",
  borderBottom: "1px solid rgba(148,163,184,0.14)",
  color: "#94a3b8",
  fontSize: 12,
  fontWeight: 700,
  textAlign: "left",
  letterSpacing: 0.2,
};

const tableRowCellStyle = {
  padding: "9px 10px",
  borderBottom: "1px solid rgba(148,163,184,0.08)",
};

function PageIntro({ eyebrow, title, description, actions, children }) {
  return (
    <div style={{
      background: "linear-gradient(180deg, rgba(15,23,42,0.92) 0%, rgba(15,23,42,0.72) 100%)",
      border: "1px solid rgba(148,163,184,0.16)",
      borderRadius: 20,
      padding: 24,
      marginBottom: 20,
      boxShadow: uiTheme.shadow,
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 20, alignItems: "flex-start", flexWrap: "wrap" }}>
        <div style={{ minWidth: 280, flex: 1 }}>
          {eyebrow && <div style={{ fontSize: 11, letterSpacing: 1.4, textTransform: "uppercase", color: "#7dd3fc", fontWeight: 800, marginBottom: 10 }}>{eyebrow}</div>}
          <div style={{ fontSize: 28, lineHeight: 1.1, fontWeight: 800, color: uiTheme.text }}>{title}</div>
          {description && <div style={{ marginTop: 10, fontSize: 13, lineHeight: 1.8, color: uiTheme.textMuted, maxWidth: 760 }}>{description}</div>}
        </div>
        {actions && <div style={{ display: "flex", gap: 10, flexWrap: "wrap", justifyContent: "flex-end" }}>{actions}</div>}
      </div>
      {children && <div style={{ marginTop: 18 }}>{children}</div>}
    </div>
  );
}

function DocumentsSourceBanner({ info }) {
  if (!info) return null;

  const usingMaster = info.mode === "master";
  const background = usingMaster ? "rgba(34,197,94,0.08)" : "rgba(245,158,11,0.08)";
  const border = usingMaster ? "1px solid rgba(34,197,94,0.25)" : "1px solid rgba(245,158,11,0.25)";
  const titleColor = usingMaster ? "#86efac" : "#fcd34d";

  return (
    <div style={{ marginTop: 14, background, border, borderRadius: 14, padding: 14, display: "grid", gap: 6 }}>
      <div style={{ fontSize: 13, fontWeight: 700, color: titleColor }}>
            ?獢???????爸usingMaster ? "??肅?餈斗???????荒?" : "??寥?謕???"}
      </div>
      <div style={{ fontSize: 13, color: uiTheme.textMuted }}>
        ?獢??????刻麾 {info.count || 0} ????綽??鈭色??{info.pending_review_count || 0} ?閉??
      </div>
      {info.source_path && (
        <div style={{ fontSize: 12, color: "#cbd5f5", wordBreak: "break-all" }}>
          ????獢??菜捕?{info.source_path}
        </div>
      )}
      {info.message && <div style={{ fontSize: 12, color: "#cbd5f5" }}>{info.message}</div>}
    </div>
  );
}

function ModuleStatusBanner({ title, message, tone = "demo" }) {
  const palette = tone === "mixed"
    ? { background:"rgba(59,130,246,0.08)", border:"1px solid rgba(59,130,246,0.22)", title:"#93c5fd", text:"#cbd5f5" }
    : tone === "system"
    ? { background:"rgba(16,185,129,0.08)", border:"1px solid rgba(16,185,129,0.22)", title:"#86efac", text:"#d1fae5" }
    : { background:"rgba(245,158,11,0.08)", border:"1px solid rgba(245,158,11,0.22)", title:"#fcd34d", text:"#fde68a" };

  return (
    <div style={{ marginBottom: 18, background: palette.background, border: palette.border, borderRadius: 14, padding: 14 }}>
      <div style={{ fontSize: 13, fontWeight: 700, color: palette.title, marginBottom: 6 }}>{title}</div>
      <div style={{ fontSize: 12, lineHeight: 1.8, color: palette.text }}>{message}</div>
    </div>
  );
}

function Panel({ title, description, actions, accent = "#60a5fa", children, style = {} }) {
  return (
    <div style={{
      background: uiTheme.panel,
      border: `1px solid ${accent}28`,
      borderRadius: 18,
      padding: 20,
      boxShadow: uiTheme.shadow,
      ...style,
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "flex-start", flexWrap: "wrap", marginBottom: 14 }}>
        <div style={{ minWidth: 220, flex: 1 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
            <div style={{ width: 10, height: 10, borderRadius: 999, background: accent, boxShadow: `0 0 0 6px ${accent}18` }} />
            <div style={{ fontSize: 16, fontWeight: 800, color: uiTheme.text }}>{title}</div>
          </div>
          {description && <div style={{ fontSize: 12, color: uiTheme.textMuted, lineHeight: 1.7 }}>{description}</div>}
        </div>
        {actions && <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>{actions}</div>}
      </div>
      {children}
    </div>
  );
}

function Badge({ color, children }) {
  return (
    <span style={{
      display: "inline-block",
      padding: "4px 10px",
      borderRadius: 99,
      background: color + "18",
      color,
      fontSize: 12,
      fontWeight: 700,
      border: `1px solid ${color}38`,
      letterSpacing: 0.3,
    }}>{children}</span>
  );
}

function getParserBadge(parserName) {
  if (parserName === "opendataloader_pdf") {
    return { color: "#14b8a6", label: "????OpenDataLoader" };
  }
  if (parserName === "legacy_pypdf") {
    return { color: "#f59e0b", label: "????pypdf" };
  }
  return null;
}

function getLayoutBadge(item) {
  const pageCount = Number(item?.layout_page_count || 0);
  const elementCount = Number(item?.layout_element_count || 0);
  if (!item?.layout_available && !pageCount && !elementCount) return null;
  return {
    color: "#38bdf8",
    label: `????堊垢? ${pageCount} ??/ ${elementCount} ????,
  };
}

class PageErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error("PageErrorBoundary", this.props.pageName || "page", error, info);
  }

  resetPageState = () => {
    try {
      const keys = Array.isArray(this.props.storageKeys) ? this.props.storageKeys : [];
      keys.forEach((key) => window.localStorage.removeItem(key));
    } catch (err) {
      console.warn("Failed to clear page storage", err);
    }
    if (typeof window !== "undefined") {
      window.location.reload();
    }
  };

  render() {
    if (!this.state.error) return this.props.children;
    return (
      <div style={{ background:"rgba(127,29,29,0.18)", border:"1px solid rgba(248,113,113,0.35)", borderRadius:18, padding:24, color:"#fee2e2" }}>
        <div style={{ fontSize:24, fontWeight:800, marginBottom:10 }}>???????????</div>
        <div style={{ fontSize:14, lineHeight:1.8, color:"#fecaca", marginBottom:14 }}>
          {this.props.pageName || "????"} ???????????????????????????????????
        </div>
        <div style={{ fontSize:13, color:"#fde68a", marginBottom:16 }}>
          ?????{String(this.state.error && this.state.error.message || this.state.error || "????")}
        </div>
        <div style={{ display:"flex", gap:10, flexWrap:"wrap" }}>
          <button onClick={this.resetPageState} style={{ background:"linear-gradient(135deg,#dc2626,#ef4444)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"10px 16px", fontSize:13, fontWeight:700 }}>
            ???????????
          </button>
          <button onClick={() => window.location.href='/?tab=home'} style={{ background:"rgba(255,255,255,0.08)", border:"1px solid rgba(255,255,255,0.15)", borderRadius:10, color:"#fff", cursor:"pointer", padding:"10px 16px", fontSize:13, fontWeight:700 }}>
            ?????
          </button>
        </div>
      </div>
    );
  }
}

function StatCard({ label, value, color, sub }) {
  return (
    <div style={{
      background: uiTheme.panel,
      border: "1px solid " + uiTheme.panelBorder,
      borderRadius: 18,
      padding: "22px 24px",
      flex: 1,
      minWidth: 150,
      borderTop: `3px solid ${color}`,
      boxShadow: uiTheme.shadow,
    }}>
      <div style={{ fontSize: 32, fontWeight: 800, color, fontFamily: "'DM Mono', monospace", lineHeight: 1 }}>{value}</div>
      <div style={{ fontSize: 13, color: uiTheme.textMuted, marginTop: 8, fontWeight: 700 }}>{label}</div>
      {sub && <div style={{ fontSize: 11, color: uiTheme.textSoft, marginTop: 6, lineHeight: 1.6 }}>{sub}</div>}
    </div>
  );
}

function SectionHeader({ title, count, color = "#60a5fa" }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
      <div style={{ width: 5, height: 22, background: color, borderRadius: 3 }} />
      <h2 style={{ margin: 0, fontSize: 17, fontWeight: 800, color: uiTheme.text }}>{title}</h2>
      {count !== undefined && (
        <span style={{ background: color + "18", color, borderRadius: 99, padding: "3px 10px", fontSize: 12, fontWeight: 700, border: `1px solid ${color}33` }}>{count}</span>
      )}
    </div>
  );
}

function Modal({ title, onClose, children }) {
  return (
    <div style={{
      position: "fixed", inset: 0, background: "rgba(0,0,0,0.7)", zIndex: 1000,
      display: "flex", alignItems: "center", justifyContent: "center", padding: 20,
    }} onClick={onClose}>
      <div style={{
        background: "#162033", borderRadius: 20, padding: 32, maxWidth: 700, width: "100%",
        maxHeight: "85vh", overflow: "auto", border: "1px solid rgba(148,163,184,0.18)",
        boxShadow: "0 32px 80px rgba(0,0,0,0.6)",
      }} onClick={e => e.stopPropagation()}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
          <h3 style={{ margin: 0, fontSize: 18, color: uiTheme.text, fontWeight: 800 }}>{title}</h3>
          <button onClick={onClose} style={{
            background: "rgba(255,255,255,0.08)", border: "1px solid rgba(148,163,184,0.14)", borderRadius: 10,
            color: uiTheme.textMuted, cursor: "pointer", padding: "8px 14px", fontSize: 13, fontWeight: 700,
          }}>???謚?</button>
        </div>
        {children}
      </div>
    </div>
  );
}

const inputStyle = {
  background: "rgba(255,255,255,0.05)",
  border: "1px solid rgba(148,163,184,0.18)",
  borderRadius: 12,
  padding: "10px 12px",
  color: "#e2e8f0",
  fontSize: 14,
  width: "100%",
  boxSizing: "border-box",
  outline: "none",
};

// ?????? CALIBRATION TAB ??????????????????????????????????????????????????????????????????????????????????????????????????????????????????
