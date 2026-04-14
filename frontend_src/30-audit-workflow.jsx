function NonConformanceTab({ nonConformances: items, setNonConformances: setItems, highlightNcId, onHighlightDone, expandNcId, onExpandDone, documents, documentsSourceInfo, draftSeed, onDraftSeedConsumed, onAuditPlansSync, onOpenDocument }) {
  const emptyDraft = { id:"", date:"", dept:"", type:"製程異常", description:"", severity:"輕微", rootCause:"", correctiveAction:"", responsible:"", dueDate:"", status:"待處理", closeDate:"", effectiveness:"", relatedDocument:"", sourceAuditPlanId:"", sourceAuditScope:"" };
  const [modal, setModal] = useState(null);
  const [showAdd, setShowAdd] = useState(false);
  const [draft, setDraft] = useState(emptyDraft);
  const [editingId, setEditingId] = useState("");
  const [showMissingOnly, setShowMissingOnly] = useState(false);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState("");
  const [importDraft, setImportDraft] = useState(null);
  const [importMissing, setImportMissing] = useState([]);
  const rowRefs = useRef({});
  const ncFieldDefs = [
    ["編號", "id", "text"],
    ["發生日", "date", "date"],
    ["部門", "dept", "text"],
    ["問題描述", "description", "text"],
    ["原因分析", "rootCause", "text"],
    ["改善措施", "correctiveAction", "text"],
    ["責任人", "responsible", "text"],
    ["到期日", "dueDate", "date"],
    ["結案日期", "closeDate", "date"],
    ["有效性確認", "effectiveness", "text"],
  ];

  useEffect(() => {
    if (!highlightNcId) return;
    const el = rowRefs.current[highlightNcId];
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "center" });
      el.style.outline = "2px solid #f59e0b";
      el.style.outlineOffset = "3px";
      el.style.transition = "outline 0.2s";
      const t = setTimeout(() => {
        el.style.outline = "";
        el.style.outlineOffset = "";
        onHighlightDone?.();
      }, 2500);
      return () => clearTimeout(t);
    }
  }, [highlightNcId]);

  useEffect(() => {
    if (!expandNcId) return;
    const nc = items.find(item => String(item.id) === String(expandNcId));
    if (nc) {
      setModal(nc);
      onExpandDone?.();
    }
  }, [expandNcId]);

  useEffect(() => {
    if (!draftSeed?.seedKey) return;
    setShowAdd(true);
    setEditingId("");
    setModal(null);
    setImportDraft(null);
    setImportMissing([]);
    setDraft({ ...emptyDraft, ...draftSeed });
    setMessage("已由稽核計畫帶入不符合草稿，請補上問題描述後存入。");
    onDraftSeedConsumed?.();
  }, [draftSeed?.seedKey]);

  const normalizeStatus = s => (s === "進行中" ? "處理中" : (s || "未分類"));
  const statusColor = s => {
    const normalized = normalizeStatus(s);
    return normalized==="已關閉"?"#22c55e":normalized==="處理中"?"#f97316":normalized==="待處理"?"#ef4444":"#eab308";
  };
  const sevColor = s => s==="重大"?"#ef4444":s==="中度"?"#eab308":"#60a5fa";
  const enriched = items.map(item => {
    const normalizedStatus = normalizeStatus(item.status);
    const missingFields = [];
    if (!String(item.date || "").trim()) missingFields.push("發生日");
    if (!String(item.responsible || "").trim()) missingFields.push("責任人");
    if (!String(item.rootCause || "").trim()) missingFields.push("原因分析");
    if (!String(item.correctiveAction || "").trim()) missingFields.push("改善措施");
    if (!String(item.dueDate || "").trim()) missingFields.push("到期日");
    return {
      ...item,
      normalizedStatus,
      missingFields,
      hasMissingFields: missingFields.length > 0,
      overdue: normalizedStatus !== "已關閉" && daysUntil(item.dueDate) < 0,
    };
  });
  const missingItemCount = enriched.filter(item => item.hasMissingFields).length;
  const visibleItems = showMissingOnly ? enriched.filter(item => item.hasMissingFields) : enriched;
  const sortedEnriched = [...visibleItems].sort((a, b) => {
    const aTime = Date.parse(a.date || "") || 0;
    const bTime = Date.parse(b.date || "") || 0;
    return bTime - aTime || String(a.id || "").localeCompare(String(b.id || ""), "zh-Hant");
  });
  const yearGroups = sortedEnriched.reduce((acc, item) => {
    const year = String(item.date || "").slice(0, 4) || "未填日期";
    if (!acc[year]) acc[year] = [];
    acc[year].push(item);
    return acc;
  }, {});
  const yearGroupEntries = Object.entries(yearGroups).sort((a, b) => {
    if (a[0] === "未填日期") return 1;
    if (b[0] === "未填日期") return -1;
    return Number(b[0]) - Number(a[0]);
  });
  const statusCounts = enriched.reduce((acc, item) => {
    const key = item.normalizedStatus;
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});
  const officialDocuments = (documents || []).filter(doc => /^(MM|MP)-/i.test(doc.id || ""));
  const linkedDocumentCount = enriched.filter(item => resolveRelatedDocument(item.relatedDocument, officialDocuments).doc).length;
  const pendingLinkedCount = enriched.filter(item => {
    const matched = resolveRelatedDocument(item.relatedDocument, officialDocuments).doc;
    return matched && matched.reviewStatus && matched.reviewStatus !== "主清單一致";
  }).length;

  function resetDraftForm() {
    setShowAdd(false);
    setEditingId("");
    setDraft(emptyDraft);
  }

  function startAddRecord() {
    setEditingId("");
    setImportDraft(null);
    setImportMissing([]);
    setDraft(emptyDraft);
    setShowAdd(true);
  }

  function startEditRecord(item) {
    setEditingId(item.id || "");
    setImportDraft(null);
    setImportMissing([]);
    setModal(null);
    setDraft({
      ...emptyDraft,
      ...item,
      status: item.normalizedStatus || item.status || "待處理",
    });
    setShowAdd(true);
  }

  async function persistRecord(record, doneMessage) {
    setBusy("save");
    setMessage("");
    try {
      const payload = await apiJson("/api/nonconformances", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ record }),
      });
      setItems(payload.items || []);
      onAuditPlansSync?.(payload.audit_plans || []);
      setMessage(doneMessage);
      return true;
    } catch (err) {
      setMessage("存檔失敗：" + err.message);
      return false;
    } finally {
      setBusy("");
    }
  }

  async function saveDraftRecord() {
    const ok = await persistRecord(draft, editingId ? "已修正不符合報告。" : "已新增不符合報告。");
    if (!ok) return;
    resetDraftForm();
  }

  async function closeRecord(item) {
    const ok = await persistRecord({ ...item, status: "已關閉", closeDate: new Date().toISOString().split("T")[0], effectiveness: item.effectiveness || "有效" }, "已更新為結案。");
    if (ok) setModal(null);
  }

  async function deleteRecord(id) {
    if (!window.confirm("確定要刪除這筆不符合報告嗎？")) return;
    setBusy("delete");
    setMessage("");
    try {
      const payload = await apiJson("/api/nonconformances/" + encodeURIComponent(id), { method: "DELETE" });
      setItems(payload.items || []);
      onAuditPlansSync?.(payload.audit_plans || []);
      setModal(null);
      setMessage("已刪除不符合報告。");
    } catch (err) {
      setMessage("刪除失敗：" + err.message);
    } finally {
      setBusy("");
    }
  }

  async function importFile(file) {
    if (!file) return;
    setBusy("import");
    setMessage("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const payload = await apiJson("/api/nonconformances/import", { method: "POST", body: formData });
      setImportDraft(payload.draft || null);
      setImportMissing(payload.missing_fields || []);
      setMessage("已讀取檔案，請確認資料後再存入。");
    } catch (err) {
      setMessage("匯入失敗：" + err.message);
    } finally {
      setBusy("");
    }
  }

  async function confirmImport() {
    if (!importDraft) return;
    const ok = await persistRecord(importDraft, "已匯入不符合報告。");
    if (!ok) return;
    setImportDraft(null);
    setImportMissing([]);
  }

  function openRelatedDocument(docId, targetTab = "documents") {
    if (!docId) return;
    onOpenDocument?.(docId, targetTab);
  }

  return (
    <div>
      <SectionHeader title="不符合管理（MP-20）" count={items.length} color="#f87171" />
      <div style={{ marginBottom: 18 }}>
        <DocumentsSourceBanner info={documentsSourceInfo} />
      </div>
      <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
        <StatCard label="待處理" value={statusCounts["待處理"] || 0} color="#ef4444" sub="尚未開始" />
        <StatCard label="處理中" value={statusCounts["處理中"] || 0} color="#f97316" sub="追蹤中" />
        <StatCard label="已關閉" value={statusCounts["已關閉"] || 0} color="#22c55e" sub="已完成" />
        <StatCard label="已逾期" value={enriched.filter(item=>item.overdue).length} color="#ef4444" sub="需優先處理" />
        <StatCard label="已連結程序" value={linkedDocumentCount} color="#38bdf8" sub="已對應柏連正式文件" />
        <StatCard label="待確認程序" value={pendingLinkedCount} color="#f59e0b" sub="主清單仍需人工確認" />
        <StatCard label="待補資料" value={missingItemCount} color="#a78bfa" sub="缺日期或處理資訊" />
      </div>
      <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit,minmax(280px,1fr))", gap:12, marginBottom:18 }}>
        <div style={{ background:"rgba(255,255,255,0.03)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:12, padding:"14px 16px" }}>
          <div style={{ color:"#e2e8f0", fontWeight:700, fontSize:14, marginBottom:10 }}>依年份整理</div>
          <div style={{ display:"flex", flexWrap:"wrap", gap:8 }}>
            {yearGroupEntries.map(([year, records]) => (
              <span key={year} style={{ background:"rgba(96,165,250,0.12)", border:"1px solid rgba(96,165,250,0.24)", borderRadius:999, color:"#bfdbfe", fontSize:12, fontWeight:700, padding:"6px 10px" }}>
                {year}：{records.length} 份
              </span>
            ))}
          </div>
        </div>
        <div style={{ background:"rgba(255,255,255,0.03)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:12, padding:"14px 16px" }}>
          <div style={{ color:"#e2e8f0", fontWeight:700, fontSize:14, marginBottom:10 }}>依狀態整理</div>
          <div style={{ display:"flex", flexWrap:"wrap", gap:8 }}>
            {[
              ["待處理", "#ef4444"],
              ["處理中", "#f97316"],
              ["已關閉", "#22c55e"],
            ].map(([label, color]) => (
              <span key={label} style={{ background:"rgba(255,255,255,0.04)", border:`1px solid ${color}55`, borderRadius:999, color, fontSize:12, fontWeight:700, padding:"6px 10px" }}>
                {label}：{statusCounts[label] || 0} 份
              </span>
            ))}
          </div>
        </div>
      </div>
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", gap:12, marginBottom:14, flexWrap:"wrap" }}>
        <div style={{ color:"#fca5a5", fontSize:12 }}>{message || "可刪除錯誤資料，也可上傳報告檔先解析再確認；如知道對應程序，也能直接連到柏連正式文件主清單。"}</div>
        <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
          <button onClick={() => setShowMissingOnly(v => !v)} style={{ background: showMissingOnly ? "rgba(167,139,250,0.18)" : "rgba(255,255,255,0.06)", border: `1px solid ${showMissingOnly ? "rgba(167,139,250,0.38)" : "rgba(255,255,255,0.12)"}`, borderRadius:10, color: showMissingOnly ? "#ddd6fe" : "#e2e8f0", cursor:"pointer", padding:"9px 18px", fontSize:13, fontWeight:700 }}>
            {showMissingOnly ? "顯示全部報告" : "只看待補資料"}
          </button>
          <label style={{ background:"rgba(255,255,255,0.06)", border:"1px solid rgba(255,255,255,0.12)", borderRadius:10, color:"#e2e8f0", cursor:"pointer", padding:"9px 18px", fontSize:13, fontWeight:700 }}>
            {busy==="import" ? "讀取中..." : "上傳報告檔"}
            <input type="file" accept=".docx,.xlsx,.pdf" onChange={e => importFile(e.target.files && e.target.files[0])} style={{ display:"none" }} />
          </label>
          <button onClick={startAddRecord} style={{ background: "linear-gradient(135deg, #dc2626, #ef4444)", border: "none", borderRadius: 10, color: "#fff", cursor: "pointer", padding: "9px 18px", fontSize: 13, fontWeight: 700 }}>新增報告</button>
        </div>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {showMissingOnly && (
          <div style={{ background:"rgba(167,139,250,0.1)", border:"1px solid rgba(167,139,250,0.22)", borderRadius:12, padding:"12px 14px", color:"#ddd6fe", fontSize:12 }}>
            目前只顯示仍需補資料的報告。你可以直接按每筆右側的「修正」，補上日期、責任人、原因分析、改善措施或到期日。
          </div>
        )}
        {yearGroupEntries.map(([year, records]) => (
          <div key={year} style={{ display:"flex", flexDirection:"column", gap:10 }}>
            <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", gap:12, marginTop:8 }}>
              <div style={{ color:"#e2e8f0", fontWeight:800, fontSize:16 }}>{year === "未填日期" ? "未填日期" : `${year} 年不符合報告`}</div>
              <div style={{ color:"#94a3b8", fontSize:12 }}>{records.length} 份</div>
            </div>
            {records.map(item => {
          const related = resolveRelatedDocument(item.relatedDocument, officialDocuments);
          return (
          <div key={item.id} ref={el => { rowRefs.current[item.id] = el; }} style={{ background: item.overdue?"rgba(239,68,68,0.12)":"rgba(255,255,255,0.03)", border: `1px solid ${item.overdue?"rgba(239,68,68,0.3)":"rgba(255,255,255,0.08)"}`, borderRadius: 12, padding: "14px 18px" }}>
            <div style={{ display: "flex", alignItems: "flex-start", gap: 12, flexWrap: "wrap" }}>
              <div style={{ flex: 1, minWidth: 260 }}>
                <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 6, flexWrap: "wrap" }}>
                  <span style={{ fontWeight: 700, color: "#60a5fa", fontFamily: "monospace", fontSize: 13 }}>{item.id}</span>
                  <Badge color={sevColor(item.severity)}>{item.severity}</Badge>
                  <Badge color={statusColor(item.status)}>{item.normalizedStatus}</Badge>
                  {item.overdue && <Badge color="#ef4444">已逾期</Badge>}
                  {item.hasMissingFields && <Badge color="#a78bfa">待補 {item.missingFields.length} 項</Badge>}
                  {related.code && <Badge color={related.doc ? "#38bdf8" : "#f59e0b"}>{related.doc ? `關聯 ${related.code}` : `待確認 ${related.code}`}</Badge>}
                </div>
                <div style={{ color: "#e2e8f0", fontWeight: 600, fontSize: 14, marginBottom: 4 }}>{item.description}</div>
                <div style={{ fontSize: 12, color: "#64748b" }}>{item.dept} · {item.type} · 發生日 {formatDate(item.date)} · 責任人 {item.responsible || "未填"}</div>
                {item.hasMissingFields && (
                  <div style={{ fontSize: 12, color: "#ddd6fe", marginTop: 6 }}>
                    待補欄位：{item.missingFields.join("、")}
                  </div>
                )}
                {item.sourceAuditPlanId && (
                  <div style={{ fontSize: 12, color: "#c4b5fd", marginTop: 6 }}>
                    來源稽核：{item.sourceAuditPlanId}
                  </div>
                )}
                {related.code && (
                  <div style={{ fontSize: 12, color: related.doc ? "#93c5fd" : "#fcd34d", marginTop: 6 }}>
                    對應程序：
                    {related.doc ? (
                      <>
                        {" "}
                        <button onClick={() => openRelatedDocument(related.doc.id, "documents")} style={{ background:"transparent", border:"none", color:"#93c5fd", cursor:"pointer", padding:0, fontSize:12, fontWeight:700, textDecoration:"underline" }}>
                          {related.doc.id} {related.doc.name}
                        </button>
                      </>
                    ) : `${related.code}（尚未在柏連正式文件主清單找到）`}
                  </div>
                )}
              </div>
              <div style={{ textAlign: "right", minWidth: 120 }}>
                <div style={{ fontSize: 12, color: "#64748b" }}>到期日</div>
                <div style={{ fontWeight: 700, color: item.overdue?"#ef4444":"#e2e8f0", fontSize: 13 }}>{formatDate(item.dueDate)}</div>
                {item.status==="已關閉" && <div style={{ fontSize: 11, color: "#4ade80", marginTop: 4 }}>結案 {formatDate(item.closeDate)}</div>}
              </div>
              <div style={{ display:"flex", gap:8 }}>
                <button onClick={() => setModal(item)} style={{ background: "rgba(255,255,255,0.08)", border: "1px solid rgba(255,255,255,0.15)", borderRadius: 8, color: "#94a3b8", cursor: "pointer", padding: "6px 14px", fontSize: 12 }}>詳情</button>
                <button onClick={() => startEditRecord(item)} style={{ background:"rgba(59,130,246,0.12)", border:"1px solid rgba(59,130,246,0.25)", borderRadius:8, color:"#93c5fd", cursor:"pointer", padding:"6px 14px", fontSize:12 }}>修正</button>
                <button onClick={() => deleteRecord(item.id)} style={{ background:"rgba(239,68,68,0.14)", border:"1px solid rgba(239,68,68,0.28)", borderRadius:8, color:"#fca5a5", cursor:"pointer", padding:"6px 14px", fontSize:12 }}>刪除</button>
              </div>
            </div>
          </div>
        )})}
          </div>
        ))}
      </div>
      {modal && (() => {
        const related = resolveRelatedDocument(modal.relatedDocument, officialDocuments);
        const relatedUrl = related.doc ? (related.doc.pdfPath || related.doc.docxPath || "") : "";
        return (
          <Modal title={`不符合報告：${modal.id}`} onClose={() => setModal(null)}>
            <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              {[["發生日",formatDate(modal.date)],["部門",modal.dept],["類型",modal.type],["嚴重度",modal.severity],["問題描述",modal.description],["原因分析",modal.rootCause],["改善措施",modal.correctiveAction],["責任人",modal.responsible],["到期日",formatDate(modal.dueDate)],["狀態",modal.status],["來源稽核",modal.sourceAuditPlanId || "未連結"],["結案日",formatDate(modal.closeDate)],["有效性",modal.effectiveness||"未填"]].map(([k,v]) => (<div key={k} style={{ display:"flex", gap:12 }}><div style={{ fontSize:12, color:"#64748b", minWidth:90 }}>{k}</div><div style={{ color:"#e2e8f0", fontWeight:600, fontSize:13 }}>{v}</div></div>))}
              <div style={{ background:"rgba(56,189,248,0.08)", border:"1px solid rgba(56,189,248,0.2)", borderRadius:10, padding:12 }}>
                <div style={{ fontSize:12, color:"#7dd3fc", marginBottom:8 }}>對應柏連正式文件</div>
                {!related.code ? (
                  <div style={{ fontSize:12, color:"#94a3b8" }}>這筆不符合目前還沒有指定對應程序。</div>
                ) : related.doc ? (
                  <div style={{ display:"grid", gap:6 }}>
                    <div style={{ color:"#e2e8f0", fontWeight:700, fontSize:13 }}>{related.doc.id} {related.doc.name}</div>
                    <div style={{ color:"#94a3b8", fontSize:12 }}>目前狀態：{related.doc.reviewStatus || "未標示"}</div>
                    {related.doc.reviewReason && <div style={{ color:"#cbd5f5", fontSize:12 }}>{related.doc.reviewReason}</div>}
                    <div style={{ display:"flex", gap:8, flexWrap:"wrap", marginTop:4 }}>
                      <button onClick={() => openRelatedDocument(related.doc.id, "documents")} style={{ background:"rgba(56,189,248,0.12)", border:"1px solid rgba(56,189,248,0.24)", borderRadius:8, color:"#bae6fd", cursor:"pointer", padding:"7px 12px", fontSize:12, fontWeight:700 }}>
                        到文件管理定位
                      </button>
                      <button onClick={() => openRelatedDocument(related.doc.id, "library")} style={{ background:"rgba(249,115,22,0.12)", border:"1px solid rgba(249,115,22,0.22)", borderRadius:8, color:"#fdba74", cursor:"pointer", padding:"7px 12px", fontSize:12, fontWeight:700 }}>
                        到文件庫定位
                      </button>
                      {relatedUrl && <a href={relatedUrl} target="_blank" rel="noreferrer" style={{ color:"#93c5fd", fontSize:12, textDecoration:"none", display:"inline-flex", alignItems:"center" }}>開啟關聯文件</a>}
                    </div>
                  </div>
                ) : (
                  <div style={{ fontSize:12, color:"#fcd34d" }}>已填寫 {related.code}，但目前還沒有在柏連正式文件主清單找到完全對應的文件。</div>
                )}
              </div>
              <div style={{ display:"flex", gap:10, flexWrap:"wrap", marginTop:8 }}>
                <button onClick={() => startEditRecord(modal)} style={{ background:"rgba(59,130,246,0.14)", border:"1px solid rgba(59,130,246,0.26)", borderRadius:10, color:"#bfdbfe", cursor:"pointer", padding:"12px 24px", fontSize:14, fontWeight:700 }}>修正資料</button>
                {modal.status!=="已關閉" && (<button onClick={() => closeRecord(modal)} style={{ background:"linear-gradient(135deg,#059669,#10b981)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"12px 24px", fontSize:14, fontWeight:700 }}>標記結案</button>)}
                <button onClick={() => deleteRecord(modal.id)} style={{ background:"rgba(239,68,68,0.14)", border:"1px solid rgba(239,68,68,0.28)", borderRadius:10, color:"#fca5a5", cursor:"pointer", padding:"12px 24px", fontSize:14, fontWeight:700 }}>刪除這筆資料</button>
              </div>
            </div>
          </Modal>
        );
      })()}
      {showAdd && (
        <Modal title={editingId ? `修正不符合報告：${editingId}` : "新增不符合報告"} onClose={resetDraftForm}>
          <div style={{ display:"flex", flexDirection:"column", gap:12 }}>
            {draft.sourceAuditPlanId && (
              <div style={{ background:"rgba(124,58,237,0.12)", border:"1px solid rgba(124,58,237,0.24)", borderRadius:10, padding:12, color:"#ddd6fe", fontSize:12 }}>
                這份草稿是由稽核計畫 <b>{draft.sourceAuditPlanId}</b> 帶入的，你只要補上具體問題描述與改善內容即可。
              </div>
            )}
            {ncFieldDefs.map(([label, field, type]) => (
              <div key={field}>
                <div style={{ fontSize:12, color:"#64748b", marginBottom:5 }}>{label}</div>
                <input type={type} value={draft[field] || ""} onChange={e=>setDraft({...draft,[field]:e.target.value})} style={inputStyle} />
              </div>
            ))}
            <div>
              <div style={{ fontSize:12, color:"#64748b", marginBottom:5 }}>來源稽核計畫</div>
              <input type="text" value={draft.sourceAuditPlanId || ""} readOnly style={{ ...inputStyle, opacity:0.85, cursor:"default" }} />
            </div>
            <div>
              <div style={{ fontSize:12, color:"#64748b", marginBottom:5 }}>對應程序文件</div>
              <select value={draft.relatedDocument} onChange={e=>setDraft({...draft,relatedDocument:e.target.value})} style={inputStyle}>
                <option value="">未指定</option>
                {officialDocuments.map(doc => <option key={doc.id} value={doc.id}>{getDocumentDisplayLabel(doc)}</option>)}
              </select>
              <div style={{ fontSize:11, color:"#94a3b8", marginTop:6 }}>如果這筆不符合是因為某份程序沒有落實，可以在這裡直接連到那份正式文件。</div>
            </div>
            <div>
              <div style={{ fontSize:12, color:"#64748b", marginBottom:5 }}>類型</div>
              <select value={draft.type} onChange={e=>setDraft({...draft,type:e.target.value})} style={inputStyle}>
                <option>製程異常</option><option>文件不符</option><option>人員作業</option><option>客戶投訴</option><option>量測異常</option><option>來料不合格</option>
              </select>
            </div>
            <div>
              <div style={{ fontSize:12, color:"#64748b", marginBottom:5 }}>嚴重度</div>
              <select value={draft.severity} onChange={e=>setDraft({...draft,severity:e.target.value})} style={inputStyle}>
                <option>輕微</option><option>中度</option><option>重大</option>
              </select>
            </div>
            <div>
              <div style={{ fontSize:12, color:"#64748b", marginBottom:5 }}>狀態</div>
              <select value={draft.status} onChange={e=>setDraft({...draft,status:e.target.value})} style={inputStyle}>
                <option>待處理</option><option>進行中</option><option>已關閉</option>
              </select>
            </div>
            <button onClick={saveDraftRecord} disabled={busy==="save"} style={{ background:"linear-gradient(135deg,#dc2626,#ef4444)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"12px 24px", fontSize:15, fontWeight:700, marginTop:8, opacity:busy==="save"?0.6:1 }}>{busy==="save"?"存檔中...":editingId?"確認修正":"確認新增"}</button>
          </div>
        </Modal>
      )}
      {importDraft && (
        <Modal title="匯入預覽" onClose={() => { setImportDraft(null); setImportMissing([]); }}>
          <div style={{ display:"flex", flexDirection:"column", gap:12 }}>
            {importMissing.length>0 && <div style={{ background:"rgba(250,204,21,0.1)", border:"1px solid rgba(250,204,21,0.24)", borderRadius:8, padding:10, color:"#fde68a", fontSize:12 }}>以下欄位未完整讀取：{importMissing.join("、")}，請先補齊。</div>}
            {ncFieldDefs.map(([label, field, type]) => (
              <div key={field}>
                <div style={{ fontSize:12, color:"#64748b", marginBottom:5 }}>{label}</div>
                <input type={type} value={importDraft[field]||""} onChange={e=>setImportDraft({...importDraft,[field]:e.target.value})} style={inputStyle} />
              </div>
            ))}
            <div>
              <div style={{ fontSize:12, color:"#64748b", marginBottom:5 }}>對應程序文件</div>
              <select value={importDraft.relatedDocument||""} onChange={e=>setImportDraft({...importDraft,relatedDocument:e.target.value})} style={inputStyle}>
                <option value="">未指定</option>
                {officialDocuments.map(doc => <option key={doc.id} value={doc.id}>{getDocumentDisplayLabel(doc)}</option>)}
              </select>
            </div>
            <div>
              <div style={{ fontSize:12, color:"#64748b", marginBottom:5 }}>類型</div>
              <select value={importDraft.type||"製程異常"} onChange={e=>setImportDraft({...importDraft,type:e.target.value})} style={inputStyle}>
                <option>製程異常</option><option>文件不符</option><option>人員作業</option><option>客戶投訴</option><option>量測異常</option><option>來料不合格</option>
              </select>
            </div>
            <div>
              <div style={{ fontSize:12, color:"#64748b", marginBottom:5 }}>嚴重度</div>
              <select value={importDraft.severity||"輕微"} onChange={e=>setImportDraft({...importDraft,severity:e.target.value})} style={inputStyle}>
                <option>輕微</option><option>中度</option><option>重大</option>
              </select>
            </div>
            <div>
              <div style={{ fontSize:12, color:"#64748b", marginBottom:5 }}>狀態</div>
              <select value={importDraft.status||"待處理"} onChange={e=>setImportDraft({...importDraft,status:e.target.value})} style={inputStyle}>
                <option>待處理</option><option>進行中</option><option>已關閉</option>
              </select>
            </div>
            {importDraft.source_file && (
              <div style={{ background:"rgba(255,255,255,0.03)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:8, padding:10, color:"#94a3b8", fontSize:12, wordBreak:"break-all" }}>
                匯入來源：{importDraft.source_file}
              </div>
            )}
            <button onClick={confirmImport} disabled={busy==="save"} style={{ background:"linear-gradient(135deg,#dc2626,#ef4444)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"12px 24px", fontSize:15, fontWeight:700, marginTop:8, opacity:busy==="save"?0.6:1 }}>{busy==="save"?"存檔中...":"確認存入"}</button>
          </div>
        </Modal>
      )}
    </div>
  );
}

function AuditPlanTab({ auditPlans, setAuditPlans, documents, documentsSourceInfo, onCreateNonConformance, nonConformances, setActiveTab, setHighlightNcId, setExpandNcId, onOpenDocument }) {
  const [modal, setModal] = useState(null);
  const [filter, setFilter] = useState("all");
  const [sourceYearFilter, setSourceYearFilter] = useState("all");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState("");
  const [attachments, setAttachments] = useState([]);
  const [attachmentBusy, setAttachmentBusy] = useState(false);
  const [importRecords, setImportRecords] = useState([]);
  const statusColor = s => s==="已完成"?"#22c55e":s==="執行中"?"#60a5fa":s==="計畫中"?"#f97316":"#ef4444";
  const safeNonConformances = objectRows(nonConformances);
  const getAuditPlanSourceYear = (plan) => {
    const sourceFile = String(plan?.source_file || "").trim();
    if (!sourceFile) return "";
    const parts = sourceFile.split("\\").filter(Boolean);
    return parts.find(part => /年度$/.test(part)) || "";
  };

  const filtered = auditPlans.filter(item => {
    const statusMatch = filter === "all" || item.status === filter;
    const yearMatch = sourceYearFilter === "all" || getAuditPlanSourceYear(item) === sourceYearFilter;
    return statusMatch && yearMatch;
  });
  const upcoming = auditPlans.filter(item=>item.status==="計畫中" && daysUntil(item.scheduledDate)<=30 && daysUntil(item.scheduledDate)>=0);
  const officialDocuments = (documents || []).filter(doc => /^(MM|MP)-/i.test(doc.id || ""));
  const documentLookup = buildDocumentLookup(officialDocuments);
  const coveredCodes = Array.from(new Set(auditPlans.flatMap(item => resolveScopeDocuments(item.scope, officialDocuments).codes)));
  const coveredMatchedCount = coveredCodes.filter(code => documentLookup.has(code)).length;
  const coveredPendingCount = coveredCodes.filter(code => {
    const doc = documentLookup.get(code);
    return doc && doc.reviewStatus && doc.reviewStatus !== "主清單一致";
  }).length;
  const uncoveredCodeCount = coveredCodes.length - coveredMatchedCount;
  const linkedNcSummaries = auditPlans.map(plan => buildAuditPlanNcSummary(plan, safeNonConformances));
  const totalLinkedNc = linkedNcSummaries.reduce((sum, item) => sum + item.total, 0);
  const totalOpenLinkedNc = linkedNcSummaries.reduce((sum, item) => sum + item.open, 0);
  const totalClosedLinkedNc = linkedNcSummaries.reduce((sum, item) => sum + item.closed, 0);
  const totalOverdueLinkedNc = linkedNcSummaries.reduce((sum, item) => sum + item.overdue, 0);
  const sourceYearOptions = Array.from(new Set(auditPlans.map(item => getAuditPlanSourceYear(item)).filter(Boolean))).sort((a, b) => b.localeCompare(a, "zh-Hant"));

  const getAuditPlanSourceLabel = (plan) => {
    const sourceFile = String(plan?.source_file || "").trim();
    if (!sourceFile) return "";
    const parts = sourceFile.split("\\").filter(Boolean);
    const fileName = parts[parts.length - 1] || sourceFile;
    const yearFolder = getAuditPlanSourceYear(plan);
    return yearFolder ? `${yearFolder} / ${fileName}` : fileName;
  };

  useEffect(() => {
    let cancelled = false;
    async function loadAttachments() {
      if (!modal) {
        setAttachments([]);
        return;
      }
      setAttachmentBusy(true);
      try {
        const payload = await apiJson("/api/audit-plans/" + encodeURIComponent(modal.id) + "/attachments");
        if (!cancelled) setAttachments(payload.attachments || []);
      } catch (err) {
        if (!cancelled) {
          setAttachments([]);
          setMessage("附件讀取失敗：" + err.message);
        }
      } finally {
        if (!cancelled) setAttachmentBusy(false);
      }
    }
    loadAttachments();
    return () => { cancelled = true; };
  }, [modal && modal.id]);

  async function persistRecords(records, doneMessage) {
    setBusy("save");
    setMessage("");
    try {
      const payload = await apiJson("/api/audit-plans", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ records }),
      });
      setAuditPlans(payload.items || []);
      setMessage(doneMessage);
      return true;
    } catch (err) {
      setMessage("存檔失敗：" + err.message);
      return false;
    } finally {
      setBusy("");
    }
  }

  async function markComplete(plan) {
    const ok = await persistRecords([{ ...plan, status:"已完成", actualDate:new Date().toISOString().split("T")[0] }], "已更新稽核計畫。");
    if (ok) setModal(null);
  }

  async function deletePlan(id) {
    if (!window.confirm("確定要刪除這筆稽核計畫嗎？")) return;
    setBusy("delete");
    try {
      const payload = await apiJson("/api/audit-plans/" + encodeURIComponent(id), { method:"DELETE" });
      setAuditPlans(payload.items || []);
      setModal(null);
      setMessage("已刪除稽核計畫。");
    } catch (err) {
      setMessage("刪除失敗：" + err.message);
    } finally {
      setBusy("");
    }
  }

  async function importPlanFile(file) {
    if (!file) return;
    setBusy("import");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const payload = await apiJson("/api/audit-plans/import", { method:"POST", body:formData });
      setImportRecords(payload.records || []);
      setMessage((payload.records || []).length ? "已讀取稽核計畫檔，請確認後再存入。" : "檔案已上傳，但目前沒有辨識到可匯入的稽核計畫資料。請確認檔案內容是否已填寫。");
    } catch (err) {
      setMessage("匯入失敗：" + err.message);
    } finally {
      setBusy("");
    }
  }

  async function confirmImportPlans() {
    if (!importRecords.length) return;
    const records = importRecords.map(({ missing_fields, ...record }) => record);
    const ok = await persistRecords(records, "已匯入稽核計畫。");
    if (ok) setImportRecords([]);
  }

  function updateImportRecord(field, value) {
    if (importRecords.length !== 1) return;
    setImportRecords([{ ...importRecords[0], [field]: value }]);
  }

  function createNonConformanceDraft(plan) {
    const draft = buildNonConformanceDraftFromAuditPlan(plan, officialDocuments);
    onCreateNonConformance?.(draft);
  }

  function openLinkedNonConformance(item) {
    if (!item?.id) return;
    setHighlightNcId?.(item.id);
    setExpandNcId?.(item.id);
    setModal(null);
    setActiveTab?.("nonconformance");
  }

  function openScopeDocument(docId, targetTab = "documents") {
    if (!docId) return;
    setModal(null);
    onOpenDocument?.(docId, targetTab);
  }

  async function downloadYearBundle() {
    if (sourceYearFilter === "all") {
      setMessage("請先選擇一個年度，再下載該年的附件包。");
      return;
    }
    setBusy("bundle");
    setMessage("");
    try {
      const response = await fetch("/api/audit-plans/year-bundle?year=" + encodeURIComponent(sourceYearFilter));
      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(payload.error || ("HTTP " + response.status));
      }
      downloadBlob(await response.blob(), `柏連內部稽核附件包_${sourceYearFilter}.zip`);
      setMessage(`已下載 ${sourceYearFilter} 稽核附件包。`);
    } catch (err) {
      setMessage("下載附件包失敗：" + err.message);
    } finally {
      setBusy("");
    }
  }

  return (
    <div>
      <SectionHeader title="稽核計畫（MP-17）" count={auditPlans.length} color="#8b5cf6" />
      <div style={{ marginBottom: 18 }}>
        <DocumentsSourceBanner info={documentsSourceInfo} />
      </div>
      <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
        <StatCard label="全部計畫" value={auditPlans.length} color="#8b5cf6" />
        <StatCard label="已完成" value={auditPlans.filter(item=>item.status==="已完成").length} color="#22c55e" />
        <StatCard label="執行中" value={auditPlans.filter(item=>item.status==="執行中").length} color="#60a5fa" />
        <StatCard label="30 天內到期" value={upcoming.length} color="#f97316" sub="需排程確認" />
        <StatCard label="關聯不符合" value={totalLinkedNc} color="#f97316" sub={totalOpenLinkedNc > 0 ? `待結案 ${totalOpenLinkedNc} 筆` : "目前都已結案"} />
        <StatCard label="已結案不符合" value={totalClosedLinkedNc} color="#22c55e" sub={totalOverdueLinkedNc > 0 ? `逾期 ${totalOverdueLinkedNc} 筆` : "追蹤正常"} />
        <StatCard label="涵蓋程序" value={coveredMatchedCount} color="#38bdf8" sub="已對應柏連正式文件" />
        <StatCard label="待確認程序" value={coveredPendingCount + uncoveredCodeCount} color="#f59e0b" sub="主清單待確認或未對應" />
      </div>
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", gap:12, marginBottom:16, flexWrap:"wrap" }}>
        <div style={{ color:"#c4b5fd", fontSize:12 }}>{message || "可上傳稽核計畫表先解析，再確認存入；範圍欄位會自動對照柏連正式文件主清單。"}</div>
        <label style={{ background:"rgba(255,255,255,0.06)", border:"1px solid rgba(255,255,255,0.12)", borderRadius:10, color:"#e2e8f0", cursor:"pointer", padding:"9px 18px", fontSize:13, fontWeight:700 }}>
          {busy==="import" ? "讀取中..." : "上傳稽核計畫檔"}
          <input type="file" accept=".docx,.xlsx,.pdf" onChange={e => importPlanFile(e.target.files && e.target.files[0])} style={{ display:"none" }} />
        </label>
      </div>
      {upcoming.length>0 && (
        <div style={{ background: "rgba(249,115,22,0.08)", border: "1px solid rgba(249,115,22,0.2)", borderRadius: 12, padding: 16, marginBottom: 20 }}>
          <div style={{ fontSize: 13, color: "#fb923c", fontWeight: 700, marginBottom: 10 }}>30 天內即將執行</div>
          {upcoming.map(item => (<div key={item.id} style={{ display:"flex", gap:12, alignItems:"center", marginBottom:6 }}><span style={{ color:"#60a5fa", fontFamily:"monospace", fontSize:12 }}>{item.id}</span><span style={{ color:"#e2e8f0", fontSize:13 }}>{item.dept} · {formatDate(item.scheduledDate)}</span><Badge color="#f97316">剩 {daysUntil(item.scheduledDate)} 天</Badge></div>))}
        </div>
      )}
      <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
        {["all","計畫中","執行中","已完成"].map(key => (<button key={key} onClick={()=>setFilter(key)} style={{ background:filter===key?"rgba(139,92,246,0.2)":"rgba(255,255,255,0.04)", border:`1px solid ${filter===key?"rgba(139,92,246,0.5)":"rgba(255,255,255,0.1)"}`, borderRadius:8, color:filter===key?"#c4b5fd":"#64748b", cursor:"pointer", padding:"6px 14px", fontSize:12, fontWeight:600 }}>{key==="all"?"全部":key}</button>))}
      </div>
      {sourceYearOptions.length > 0 && (
        <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
          {["all", ...sourceYearOptions].map(key => (
            <button
              key={key}
              onClick={() => setSourceYearFilter(key)}
              style={{
                background: sourceYearFilter===key ? "rgba(56,189,248,0.18)" : "rgba(255,255,255,0.04)",
                border:`1px solid ${sourceYearFilter===key ? "rgba(56,189,248,0.4)" : "rgba(255,255,255,0.1)"}`,
                borderRadius:8,
                color:sourceYearFilter===key ? "#bae6fd" : "#64748b",
                cursor:"pointer",
                padding:"6px 14px",
                fontSize:12,
                fontWeight:600
              }}
            >
              {key==="all" ? "全部年度" : key}
            </button>
          ))}
          <button
            onClick={downloadYearBundle}
            style={{
              background:"rgba(34,197,94,0.14)",
              border:"1px solid rgba(34,197,94,0.3)",
              borderRadius:8,
              color:"#bbf7d0",
              cursor:"pointer",
              padding:"6px 14px",
              fontSize:12,
              fontWeight:700,
              opacity: busy==="bundle" ? 0.7 : 1
            }}
            disabled={busy==="bundle"}
          >
            {busy==="bundle" ? "打包中..." : "下載年度附件包"}
          </button>
        </div>
      )}
      <div style={{ overflowX: "auto" }}>
        <table style={{ width:"100%", borderCollapse:"collapse", fontSize:13 }}>
          <thead><tr>{["編號","年度","期別","預定日期","部門","受稽人","稽核員","範圍","狀態","發現數","NC 數",""].map(h => (<th key={h} style={{ textAlign:"left", padding:"10px 12px", color:"#64748b", fontWeight:600, borderBottom:"1px solid rgba(255,255,255,0.06)", whiteSpace:"nowrap" }}>{h}</th>))}</tr></thead>
          <tbody>
            {filtered.map((item,i) => {
              const scopeInfo = resolveScopeDocuments(item.scope, officialDocuments);
              const ncSummary = buildAuditPlanNcSummary(item, safeNonConformances);
              const displayNcCount = ncSummary.total || item.ncCount || 0;
              return (
              <tr key={item.id} style={{ background:i%2===0?"rgba(255,255,255,0.02)":"transparent" }}>
                <td style={{ padding:"10px 12px", color:"#8b5cf6", fontWeight:700, fontFamily:"monospace", whiteSpace:"nowrap" }}>{item.id}</td>
                <td style={{ padding:"10px 12px", color:"#94a3b8" }}>{item.year}</td>
                <td style={{ padding:"10px 12px" }}><Badge color={item.period==="上半年"?"#60a5fa":"#f97316"}>{item.period}</Badge></td>
                <td style={{ padding:"10px 12px", color:"#94a3b8", whiteSpace:"nowrap" }}>{formatDate(item.scheduledDate)}</td>
                <td style={{ padding:"10px 12px", color:"#e2e8f0", fontWeight:600 }}>{item.dept}</td>
                <td style={{ padding:"10px 12px", color:"#94a3b8" }}>{item.auditee}</td>
                <td style={{ padding:"10px 12px", color:"#94a3b8" }}>{item.auditor}</td>
                <td style={{ padding:"10px 12px", color:"#64748b", fontSize:11 }}>
                  <div>{item.scope || "未填"}</div>
                  {getAuditPlanSourceLabel(item) && (
                    <div style={{ color:"#94a3b8", marginTop:4 }}>
                      來源：{getAuditPlanSourceLabel(item)}
                    </div>
                  )}
                  {scopeInfo.matchedDocuments.length > 0 && (
                    <div style={{ color:"#cbd5f5", marginTop:4, display:"flex", flexWrap:"wrap", gap:6 }}>
                      {scopeInfo.matchedDocuments.slice(0, 2).map(doc => (
                        <button key={doc.id} onClick={() => openScopeDocument(doc.id, "documents")} style={{ background:"transparent", border:"none", color:"#cbd5f5", cursor:"pointer", padding:0, fontSize:11, textDecoration:"underline" }}>
                          {doc.id}
                        </button>
                      ))}
                      {scopeInfo.matchedDocuments.length > 2 ? <span>{`等 ${scopeInfo.matchedDocuments.length} 份`}</span> : null}
                    </div>
                  )}
                  {scopeInfo.unmatchedCodes.length > 0 && (
                    <div style={{ color:"#fcd34d", marginTop:4 }}>
                      待確認：{scopeInfo.unmatchedCodes.join("、")}
                    </div>
                  )}
                </td>
                <td style={{ padding:"10px 12px" }}><Badge color={statusColor(item.status)}>{item.status}</Badge></td>
                <td style={{ padding:"10px 12px", textAlign:"center", color:item.findings>0?"#f97316":"#94a3b8", fontWeight:700 }}>{item.findings}</td>
                <td style={{ padding:"10px 12px", textAlign:"center", color:displayNcCount>0?"#ef4444":"#94a3b8", fontWeight:700 }}>
                  <div>{displayNcCount}</div>
                  {ncSummary.total > 0 ? (
                    <div style={{ fontSize:10, color:ncSummary.open > 0 ? "#fca5a5" : "#86efac", fontWeight:600, marginTop:4 }}>
                      未結 {ncSummary.open} / 已結 {ncSummary.closed}
                    </div>
                  ) : item.ncCount > 0 ? (
                    <div style={{ fontSize:10, color:"#94a3b8", fontWeight:600, marginTop:4 }}>
                      已登錄筆數
                    </div>
                  ) : null}
                </td>
                <td style={{ padding:"10px 12px" }}><div style={{ display:"flex", gap:8, flexWrap:"wrap" }}><button onClick={()=>setModal(item)} style={{ background:"rgba(255,255,255,0.06)", border:"1px solid rgba(255,255,255,0.1)", borderRadius:6, color:"#94a3b8", cursor:"pointer", padding:"4px 10px", fontSize:11 }}>詳情</button><button onClick={() => createNonConformanceDraft(item)} style={{ background:"rgba(239,68,68,0.14)", border:"1px solid rgba(239,68,68,0.28)", borderRadius:6, color:"#fca5a5", cursor:"pointer", padding:"4px 10px", fontSize:11 }}>轉不符合</button><button onClick={() => deletePlan(item.id)} style={{ background:"rgba(148,163,184,0.12)", border:"1px solid rgba(148,163,184,0.22)", borderRadius:6, color:"#cbd5e1", cursor:"pointer", padding:"4px 10px", fontSize:11 }}>刪除</button></div></td>
              </tr>
            )})}
          </tbody>
        </table>
      </div>
      {modal && (() => {
        const scopeInfo = resolveScopeDocuments(modal.scope, officialDocuments);
        const ncSummary = buildAuditPlanNcSummary(modal, safeNonConformances);
        const displayNcCount = ncSummary.total || modal.ncCount || 0;
        return (
          <Modal title={`稽核計畫：${modal.id}`} onClose={() => setModal(null)}>
            <div style={{ display:"flex", flexDirection:"column", gap:14 }}>
              {[["計畫編號",modal.id],["受稽部門",modal.dept],["預定日期",formatDate(modal.scheduledDate)],["實際日期",formatDate(modal.actualDate)],["稽核員",modal.auditor],["受稽人",modal.auditee],["稽核範圍",modal.scope],["狀態",modal.status],["發現數",String(modal.findings)],["NC 數",String(displayNcCount)]].map(([k,v]) => (<div key={k} style={{ display:"flex", gap:12 }}><div style={{ fontSize:12, color:"#64748b", minWidth:90 }}>{k}</div><div style={{ color:"#e2e8f0", fontWeight:600, fontSize:13 }}>{v}</div></div>))}
              {getAuditPlanSourceLabel(modal) && (
                <div style={{ background:"rgba(255,255,255,0.03)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:10, padding:12 }}>
                  <div style={{ fontSize:12, color:"#c4b5fd", marginBottom:6 }}>來源年度檔案</div>
                  <div style={{ color:"#e2e8f0", fontSize:13, fontWeight:700 }}>{getAuditPlanSourceLabel(modal)}</div>
                  <div style={{ color:"#94a3b8", fontSize:12, marginTop:6, wordBreak:"break-all" }}>{modal.source_file}</div>
                </div>
              )}
              <div style={{ background:"rgba(56,189,248,0.08)", border:"1px solid rgba(56,189,248,0.2)", borderRadius:10, padding:12 }}>
                <div style={{ fontSize:12, color:"#7dd3fc", marginBottom:8 }}>對應柏連正式文件主清單</div>
                {scopeInfo.matchedDocuments.length === 0 ? (
                  <div style={{ color:"#94a3b8", fontSize:12 }}>這筆稽核計畫的範圍目前還沒有對應到柏連正式文件主清單。</div>
                ) : (
                  <div style={{ display:"grid", gap:10 }}>
                    {scopeInfo.matchedDocuments.map(doc => {
                      const docUrl = doc.pdfPath || doc.docxPath || "";
                      return (
                        <div key={doc.id} style={{ border:"1px solid rgba(255,255,255,0.08)", borderRadius:8, padding:10 }}>
                          <div style={{ color:"#e2e8f0", fontSize:13, fontWeight:700 }}>{doc.id} {doc.name}</div>
                          <div style={{ color:"#94a3b8", fontSize:12, marginTop:4 }}>目前狀態：{doc.reviewStatus || "未標示"}</div>
                          {doc.reviewReason && <div style={{ color:"#cbd5f5", fontSize:12, marginTop:4 }}>{doc.reviewReason}</div>}
                          <div style={{ display:"flex", gap:8, flexWrap:"wrap", marginTop:6 }}>
                            <button onClick={() => openScopeDocument(doc.id, "documents")} style={{ background:"rgba(56,189,248,0.12)", border:"1px solid rgba(56,189,248,0.24)", borderRadius:8, color:"#bae6fd", cursor:"pointer", padding:"7px 12px", fontSize:12, fontWeight:700 }}>
                              到文件管理定位
                            </button>
                            <button onClick={() => openScopeDocument(doc.id, "library")} style={{ background:"rgba(249,115,22,0.12)", border:"1px solid rgba(249,115,22,0.22)", borderRadius:8, color:"#fdba74", cursor:"pointer", padding:"7px 12px", fontSize:12, fontWeight:700 }}>
                              到文件庫定位
                            </button>
                            {docUrl && <a href={docUrl} target="_blank" rel="noreferrer" style={{ color:"#93c5fd", fontSize:12, textDecoration:"none", display:"inline-flex", alignItems:"center" }}>開啟程序文件</a>}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
                {scopeInfo.unmatchedCodes.length > 0 && (
                  <div style={{ color:"#fcd34d", fontSize:12, marginTop:10 }}>
                    以下代碼還沒有在柏連正式文件主清單對到：{scopeInfo.unmatchedCodes.join("、")}
                  </div>
                )}
              </div>
              <div style={{ background:"rgba(239,68,68,0.08)", border:"1px solid rgba(239,68,68,0.2)", borderRadius:10, padding:12 }}>
                <div style={{ fontSize:12, color:"#fca5a5", marginBottom:8 }}>關聯不符合追蹤</div>
                <div style={{ display:"flex", gap:12, flexWrap:"wrap", marginBottom:10 }}>
                  <Badge color="#f97316">未結案 {ncSummary.open}</Badge>
                  <Badge color="#22c55e">已結案 {ncSummary.closed}</Badge>
                  {ncSummary.overdue > 0 && <Badge color="#ef4444">逾期 {ncSummary.overdue}</Badge>}
                  {ncSummary.latestCloseDate && <Badge color="#38bdf8">最近結案 {formatDate(ncSummary.latestCloseDate)}</Badge>}
                </div>
                {ncSummary.items.length === 0 ? (
                  <div style={{ color:"#94a3b8", fontSize:12 }}>這筆稽核計畫目前還沒有連到不符合明細。你可以直接按下方「帶出不符合草稿」新增第一筆。</div>
                ) : (
                  <div style={{ display:"flex", flexDirection:"column", gap:8 }}>
                    {ncSummary.items.map(item => (
                      <div key={item.id} style={{ border:"1px solid rgba(255,255,255,0.08)", borderRadius:8, padding:10, display:"flex", justifyContent:"space-between", gap:12, alignItems:"center", flexWrap:"wrap" }}>
                        <div style={{ flex:1, minWidth:220 }}>
                          <div style={{ display:"flex", alignItems:"center", gap:8, flexWrap:"wrap" }}>
                            <span style={{ color:"#fca5a5", fontFamily:"monospace", fontSize:12, fontWeight:700 }}>{item.id}</span>
                            <Badge color={isClosedNonConformanceStatus(item.status) ? "#22c55e" : "#f97316"}>{item.status || "待處理"}</Badge>
                          </div>
                          <div style={{ color:"#e2e8f0", fontSize:13, fontWeight:600, marginTop:6 }}>{item.description || "未填寫描述"}</div>
                          <div style={{ color:"#94a3b8", fontSize:12, marginTop:4 }}>
                            責任人 {item.responsible || "未填"} · 到期日 {formatDate(item.dueDate)}
                          </div>
                        </div>
                        <button onClick={() => openLinkedNonConformance(item)} style={{ background:"rgba(255,255,255,0.06)", border:"1px solid rgba(255,255,255,0.12)", borderRadius:8, color:"#e2e8f0", cursor:"pointer", padding:"8px 14px", fontSize:12, fontWeight:700 }}>
                          開啟這筆不符合
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <div style={{ background:"rgba(255,255,255,0.03)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:10, padding:12 }}>
                <div style={{ fontSize:12, color:"#c4b5fd", marginBottom:8 }}>關聯附件</div>
{attachmentBusy ? <div style={{ color:"#94a3b8", fontSize:12 }}>讀取中...</div> : attachments.length===0 ? <div style={{ color:"#94a3b8", fontSize:12 }}>找不到關聯文件。</div> : <div style={{ display:"flex", flexDirection:"column", gap:10 }}>{attachments.map(item => (<div key={item.path} style={{ border:"1px solid rgba(255,255,255,0.08)", borderRadius:8, padding:10 }}><div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", gap:12, flexWrap:"wrap" }}><div><div style={{ color:"#e2e8f0", fontSize:13, fontWeight:600 }}>{item.name}</div><div style={{ color:item.exists?"#64748b":"#fca5a5", fontSize:11 }}>{item.exists ? (item.previewable ? "可直接預覽 PDF" : item.text_previewable ? "可直接預覽文字內容" : "可開啟或下載") : "找不到文件"}</div></div>{item.exists && <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}><a href={toAbsoluteAppUrl(item.download_url)} style={{ color:"#93c5fd", fontSize:12, textDecoration:"none" }}>下載</a>{item.previewable && <a href={toAbsoluteAppUrl(item.view_url)} target="_blank" rel="noreferrer" style={{ color:"#c4b5fd", fontSize:12, textDecoration:"none" }}>新頁預覽</a>}{item.text_previewable && <a href={toAbsoluteAppUrl(item.preview_text_url)} target="_blank" rel="noreferrer" style={{ color:"#c4b5fd", fontSize:12, textDecoration:"none" }}>文字預覽</a>}</div>}</div>{item.previewable && item.exists && <iframe src={toAbsoluteAppUrl(item.view_url)} title={item.name} style={{ width:"100%", height:260, marginTop:10, border:"1px solid rgba(255,255,255,0.08)", borderRadius:8, background:"#fff" }} />}{item.text_previewable && item.exists && <iframe src={toAbsoluteAppUrl(item.preview_text_url)} title={item.name + "-text"} style={{ width:"100%", height:260, marginTop:10, border:"1px solid rgba(255,255,255,0.08)", borderRadius:8, background:"#fff" }} />}</div>))}</div>}
              </div>
              <div style={{ display:"flex", gap:10, flexWrap:"wrap", marginTop:8 }}>
                <button onClick={() => createNonConformanceDraft(modal)} style={{ background:"linear-gradient(135deg,#dc2626,#ef4444)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"12px 24px", fontSize:14, fontWeight:700 }}>帶出不符合草稿</button>
                {modal.status!=="已完成" && (<button onClick={()=>markComplete(modal)} style={{ background:"linear-gradient(135deg,#7c3aed,#8b5cf6)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"12px 24px", fontSize:14, fontWeight:700 }}>標記完成</button>)}
                <button onClick={()=>deletePlan(modal.id)} style={{ background:"rgba(239,68,68,0.14)", border:"1px solid rgba(239,68,68,0.28)", borderRadius:10, color:"#fca5a5", cursor:"pointer", padding:"12px 24px", fontSize:14, fontWeight:700 }}>刪除這筆資料</button>
              </div>
            </div>
          </Modal>
        );
      })()}
      {importRecords.length>0 && (<Modal title="匯入預覽" onClose={() => setImportRecords([])}><div style={{ display:"flex", flexDirection:"column", gap:12 }}>{importRecords.length===1 ? <div style={{ display:"flex", flexDirection:"column", gap:12 }}>{importRecords[0].missing_fields?.length>0 && <div style={{ background:"rgba(250,204,21,0.1)", border:"1px solid rgba(250,204,21,0.24)", borderRadius:8, padding:10, color:"#fde68a", fontSize:12 }}>以下欄位未完整讀取：{importRecords[0].missing_fields.join("、")}</div>}{[["預定日期","scheduledDate","date"],["受稽部門","dept","text"],["稽核員","auditor","text"],["受稽人","auditee","text"],["稽核範圍","scope","text"]].map(([label,field,type]) => (<div key={field}><div style={{ fontSize:12, color:"#64748b", marginBottom:5 }}>{label}</div><input type={type} value={importRecords[0][field]||""} onChange={e=>updateImportRecord(field, e.target.value)} style={inputStyle} /></div>))}</div> : <div style={{ background:"rgba(255,255,255,0.03)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:10, padding:12 }}><div style={{ color:"#e2e8f0", fontWeight:700, marginBottom:8 }}>本次共讀到 {importRecords.length} 筆資料</div>{importRecords.slice(0,8).map(item => (<div key={item.id} style={{ display:"flex", justifyContent:"space-between", gap:12, borderBottom:"1px solid rgba(255,255,255,0.05)", padding:"8px 0" }}><span style={{ color:"#c4b5fd", fontFamily:"monospace", fontSize:12 }}>{item.id}</span><span style={{ color:"#94a3b8", fontSize:12 }}>{item.dept || "未讀到部門"}</span><span style={{ color:"#94a3b8", fontSize:12 }}>{formatDate(item.scheduledDate)}</span></div>))}</div>}<button onClick={confirmImportPlans} disabled={busy==="save"} style={{ background:"linear-gradient(135deg,#7c3aed,#8b5cf6)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"12px 24px", fontSize:15, fontWeight:700, marginTop:8, opacity:busy==="save"?0.6:1 }}>{busy==="save"?"存檔中...":"確認存入"}</button></div></Modal>)}
    </div>
  );
}

