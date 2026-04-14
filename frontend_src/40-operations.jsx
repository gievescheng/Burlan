function CalibrationTab({ instruments, setInstruments, calibrationSourceInfo, setCalibrationSourceInfo }) {
  const [modal, setModal] = useState(null);
  const [form, setForm] = useState({});
  const [message, setMessage] = useState("");
  const [saving, setSaving] = useState(false);
  const enriched = instruments.map(i => {
    const nextDate = getInstrumentNextCalibrationDate(i);
    const days = nextDate ? daysUntil(nextDate) : 9999;
    return { ...i, nextDate, days };
  }).sort((a, b) => a.days - b.days);
  async function handleUpdate() {
    if (!modal?.id) return;
    if (!form.date) {
      setMessage("隢?憛怠神?祆活?⊥迤?交???);
      return;
    }
    try {
      setSaving(true);
      setMessage("");
      const payload = await apiJson("/api/calibration-records", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          record: {
            instrumentId: modal.id,
            instrumentName: modal.name,
            calibrationDate: form.date,
            nextCalibration: modal.intervalDays ? addDays(form.date, modal.intervalDays) : "",
            calibMethod: modal.calibMethod,
            status: modal.calibMethod === "?" ? "?甇? : "?",
            operator: form.operator || modal.keeper || "",
            keeper: modal.keeper || "",
            location: modal.location || "",
            frequencyLabel: modal.frequencyLabel || "",
            note: form.note || "",
            sourceRecordPath: modal.rawRecordPath || "",
            sourceInventoryPath: modal.rawInventoryPath || "",
            sourceReportPath: modal.rawLatestReportPath || "",
          },
        }),
      });
      const items = (payload.items || []).map(mapCalibrationInstrument);
      setInstruments(items);
      setCalibrationSourceInfo?.({
        mode: payload.mode || "records",
        source_path: payload.source_path || "",
        count: payload.count || items.length,
        latest_plan_path: payload.latest_plan_path || "",
        inventory_path: payload.inventory_path || "",
        manual_update_count: payload.manual_update_count || 0,
        message: payload.message || "",
      });
      setMessage(`撌脖?摮?${modal.id} ?甇??啜?敺??圈??頂蝯梧?銋?靽??活蝯??);
      setModal(null);
    } catch (err) {
      setMessage("?⊥迤?湔憭望?嚗? + err.message);
    } finally {
      setSaving(false);
    }
  }
  const usingRecords = calibrationSourceInfo?.mode === "records";
  return (
    <div>
      <SectionHeader title="????冽甇?蕭頩? count={enriched.length} color="#60a5fa" />
      <ModuleStatusBanner
      title={usingRecords ? "?桀??嚗???祕???? : "?桀??嚗?????渲???}
        tone={usingRecords ? "mixed" : "demo"}
        message={usingRecords
          ? `???歇?湔霈??9?葫鞈?蝞∠?蝔? ??閬??其?閬質”???典悼甇瑁”??函??啁???函楊?甇?撘??∪摰??⊥迤???嚗?臬???祕??隞嗆?靘???{calibrationSourceInfo?.message ? ` ${calibrationSourceInfo.message}` : ""}`
        : "??????臭誑甇?虜??嚗???蝡舀?瘜?????憿舐內????游??冽??殷??踹?頝喳??航炊撠?鞈???}
      />
      {usingRecords && calibrationSourceInfo?.source_path && (
        <div style={{ marginBottom: 18, fontSize: 12, color: "#94a3b8", wordBreak: "break-all" }}>
          撅交風銵其?皞?{calibrationSourceInfo.source_path}
          {calibrationSourceInfo.inventory_path ? ` 嚚?銝閬質”靘?嚗?{calibrationSourceInfo.inventory_path}` : ""}
          {calibrationSourceInfo.latest_plan_path ? ` 嚚???啣僑摨行撽??”嚗?{calibrationSourceInfo.latest_plan_path}` : ""}
          {calibrationSourceInfo.manual_update_count ? ` 嚚?蝟餌絞撌脖?摮?${calibrationSourceInfo.manual_update_count} 蝑甇??躬 : ""}
        </div>
      )}
      {message && (
        <div style={{ marginBottom: 16, background: "rgba(59,130,246,0.12)", border: "1px solid rgba(59,130,246,0.24)", color: "#bfdbfe", borderRadius: 12, padding: "12px 14px", fontSize: 13 }}>
          {message}
        </div>
      )}
      <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
        <StatCard label="?暹?" value={enriched.filter(i => i.days < 0).length} color="#ef4444" />
        <StatCard label="14憭拙?唳?" value={enriched.filter(i => i.days >= 0 && i.days <= 14).length} color="#f97316" />
        <StatCard label="甇?虜" value={enriched.filter(i => i.days > 30).length} color="#22c55e" />
        <StatCard label="?甇? value={enriched.filter(i => i.status === "?甇?).length} color="#6366f1" />
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {enriched.map(inst => inst.status === "?甇? ? (
          <div key={inst.id} style={{ background: "rgba(99,102,241,0.08)", border: "1px solid rgba(99,102,241,0.2)", borderRadius: 12, padding: "14px 18px", display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
            <div style={{ flex: 1, minWidth: 200 }}>
              <div style={{ fontWeight: 700, color: "#c7d2fe", fontSize: 14 }}>{inst.name}</div>
              <div style={{ fontSize: 12, color: "#64748b", marginTop: 2 }}>
                {inst.id} 繚 {inst.location || "?芸‵?圈?"}
                {inst.calibMethod ? ` 繚 ${inst.calibMethod}` : ""}
                繚 靽恣鈭?{inst.keeper || "?芸‵"}
              </div>
              {inst.manualUpdatedAt && <div style={{ fontSize: 12, color: "#818cf8", marginTop: 6 }}>蝟餌絞?湔?交?嚗formatDate(inst.manualUpdatedAt)}{inst.manualOperator ? ` 繚 ${inst.manualOperator}` : ""}</div>}
            </div>
            <Badge color="#6366f1">?甇?/Badge>
            <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
              {inst.inventoryPath && <a href={inst.inventoryPath} target="_blank" rel="noreferrer" style={{ color:"#93c5fd", fontSize:12, textDecoration:"none" }}>??其?閬質”</a>}
              {inst.recordPath && <a href={inst.recordPath} target="_blank" rel="noreferrer" style={{ color:"#c4b5fd", fontSize:12, textDecoration:"none" }}>撅交風銵?/a>}
            </div>
          </div>
        ) : (
          <div key={inst.id} style={{ background: urgencyBg(inst.days), border: `1px solid ${urgencyColor(inst.days)}33`, borderRadius: 12, padding: "14px 18px", display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
            <div style={{ flex: 1, minWidth: 200 }}>
              <div style={{ fontWeight: 700, color: "#e2e8f0", fontSize: 14 }}>{inst.name}</div>
              <div style={{ fontSize: 12, color: "#64748b", marginTop: 2 }}>
                {inst.id} 繚 {inst.location} 繚 {inst.type}
                {inst.frequencyLabel ? ` 繚 ?望? ${inst.frequencyLabel}` : ""}
                {inst.calibMethod ? ` 繚 ${inst.calibMethod}` : ""}
                {inst.keeper ? ` 繚 靽恣鈭?${inst.keeper}` : ""}
                {inst.needsMSA && <span style={{ marginLeft: 8, color: "#818cf8", fontWeight: 700 }}>? MSA</span>}
              </div>
              <div style={{ fontSize: 12, color: "#cbd5e1", marginTop: 6 }}>?敺甇???{formatDate(inst.calibratedDate)}</div>
              {inst.manualUpdatedAt && <div style={{ fontSize: 12, color: "#818cf8", marginTop: 6 }}>蝟餌絞?湔?交?嚗formatDate(inst.manualUpdatedAt)}{inst.manualOperator ? ` 繚 ${inst.manualOperator}` : ""}</div>}
              {inst.manualNote && <div style={{ fontSize: 12, color: "#cbd5e1", marginTop: 6 }}>?酉嚗inst.manualNote}</div>}
            </div>
            <div style={{ textAlign: "right", minWidth: 120 }}>
              <div style={{ fontSize: 12, color: "#64748b" }}>銝活?⊥迤</div>
              <div style={{ fontWeight: 700, color: "#e2e8f0", fontSize: 14 }}>{formatDate(inst.nextDate)}</div>
            </div>
            <Badge color={urgencyColor(inst.days)}>{urgencyLabel(inst.days)}</Badge>
            <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
              {inst.inventoryPath && <a href={inst.inventoryPath} target="_blank" rel="noreferrer" style={{ color:"#93c5fd", fontSize:12, textDecoration:"none" }}>??其?閬質”</a>}
              {inst.recordPath && <a href={inst.recordPath} target="_blank" rel="noreferrer" style={{ color:"#93c5fd", fontSize:12, textDecoration:"none" }}>撅交風銵?/a>}
              {inst.latestReportPath && <a href={inst.latestReportPath} target="_blank" rel="noreferrer" style={{ color:"#fca5a5", fontSize:12, textDecoration:"none" }}>??唳甇???/a>}
              {inst.latestPlanPath && <a href={inst.latestPlanPath} target="_blank" rel="noreferrer" style={{ color:"#c4b5fd", fontSize:12, textDecoration:"none" }}>撟游漲?⊿?閮?</a>}
            </div>
            <button onClick={() => { setModal(inst); setForm({ date: new Date().toISOString().split("T")[0], operator: inst.manualOperator || inst.keeper || "", note: inst.manualNote || "" }); setMessage(""); }} style={{ background: "rgba(255,255,255,0.08)", border: "1px solid rgba(255,255,255,0.15)", borderRadius: 8, color: "#94a3b8", cursor: "pointer", padding: "6px 14px", fontSize: 12, fontWeight: 600 }}>?湔?⊥迤</button>
          </div>
        ))}
      </div>
      {modal && (
        <Modal title={`?湔?⊥迤閮?嚗?{modal.name}`} onClose={() => setModal(null)}>
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div><div style={{ fontSize: 12, color: "#64748b", marginBottom: 6 }}>??函楊??/div><div style={{ color: "#e2e8f0", fontWeight: 600 }}>{modal.id}</div></div>
            <div><div style={{ fontSize: 12, color: "#64748b", marginBottom: 6 }}>?祆活?⊥迤?交?</div><input type="date" value={form.date} onChange={e => setForm({ ...form, date: e.target.value })} style={inputStyle} /></div>
            <div><div style={{ fontSize: 12, color: "#64748b", marginBottom: 6 }}>?瑁?鈭箏</div><input value={form.operator || ""} onChange={e => setForm({ ...form, operator: e.target.value })} style={inputStyle} placeholder="靘?嚗?曌" /></div>
            <div><div style={{ fontSize: 12, color: "#64748b", marginBottom: 6 }}>?酉</div><textarea value={form.note || ""} onChange={e => setForm({ ...form, note: e.target.value })} style={{ ...inputStyle, minHeight: 96, resize: "vertical" }} placeholder="靘?嚗歇摰??扳嚗??扳蝯??湔" /></div>
            <div style={{ background: "rgba(34,197,94,0.1)", border: "1px solid rgba(34,197,94,0.2)", borderRadius: 8, padding: 12 }}>
              <div style={{ fontSize: 12, color: "#4ade80", fontWeight: 600 }}>?湔敺?銝活?⊥迤?交?撠嚗?/div>
              <div style={{ color: "#86efac", fontWeight: 700, fontSize: 16, marginTop: 4 }}>{formatDate(addDays(form.date || modal.calibratedDate, modal.intervalDays))}</div>
            </div>
            <button onClick={handleUpdate} disabled={saving} style={{ background: "linear-gradient(135deg, #3b82f6, #6366f1)", border: "none", borderRadius: 10, color: "#fff", cursor: saving ? "wait" : "pointer", padding: "12px 24px", fontSize: 15, fontWeight: 700, opacity: saving ? 0.75 : 1 }}>{saving ? "靽?銝?.." : "蝣箄??湔?⊥迤閮?"}</button>
          </div>
        </Modal>
      )}
    </div>
  );
}

// ??? DOCUMENTS TAB ???????????????????????????????????????????????????????????
function DocumentsTab({ documents, setDocuments }) {
  const [modal, setModal]       = useState(null);
  const [mode, setMode]         = useState(null);   // null | "single" | "bulk"
  const [err, setErr]           = useState("");
  const [dragOver, setDragOver] = useState(false);

  // ?? Single-add state ??????????????????????????????????????????????????????
  const emptyDoc = { id:"", name:"", type:"蝞∠?蝔?", version:"1.0", department:"", createdDate:"", author:"", retentionYears:16, fileName:"", fileSize:"", fileType:"", fileData:"" };
  const [newDoc, setNewDoc] = useState({ ...emptyDoc });

  // ?? Bulk-upload state ?????????????????????????????????????????????????????
  const [bulkItems, setBulkItems] = useState([]);   // array of draft doc objects
  const [bulkDone,  setBulkDone]  = useState(false);

  // ?? Helpers ???????????????????????????????????????????????????????????????
  const enriched = documents.map(d => {
    const expiryDate = new Date(d.createdDate);
    expiryDate.setFullYear(expiryDate.getFullYear() + (d.retentionYears || 16));
    const expiryStr = expiryDate.toISOString().split("T")[0];
    return { ...d, expiryStr, daysToExpiry: daysUntil(expiryStr) };
  });

  function parseDocxMeta(ab) {
    try {
      const raw = new TextDecoder("utf-8", { fatal: false }).decode(new Uint8Array(ab));
      const g = re => (raw.match(re)||[])[1]||"";
      return {
        title:    g(/<dc:title[^>]*>([^<]*)<\/dc:title>/),
        creator:  g(/<dc:creator[^>]*>([^<]*)<\/dc:creator>/) || g(/<cp:lastModifiedBy[^>]*>([^<]*)<\/cp:lastModifiedBy>/),
        revision: g(/<cp:revision[^>]*>([^<]*)<\/cp:revision>/),
        created:  g(/<dcterms:created[^>]*>([^<]*)<\/dcterms:created>/),
        modified: g(/<dcterms:modified[^>]*>([^<]*)<\/dcterms:modified>/),
      };
    } catch(e) { return {}; }
  }
  function parsePdfMeta(ab) {
    try {
      const raw = new TextDecoder("latin1", { fatal: false }).decode(new Uint8Array(ab));
      const g = re => (raw.match(re)||[])[1]||"";
      const d = g(/\/CreationDate\s*\(D:(\d{8})/);
      return { title: g(/\/Title\s*\(([^)]+)\)/), author: g(/\/Author\s*\(([^)]+)\)/),
               date: d.length===8 ? `${d.slice(0,4)}-${d.slice(4,6)}-${d.slice(6,8)}` : "" };
    } catch(e) { return {}; }
  }

  // Process one File object ??return a draft doc object (with fileData)
  function processFile(file) {
    return new Promise(resolve => {
      const ext     = file.name.split(".").pop().toLowerCase();
      const sizeStr = file.size > 1048576 ? (file.size/1048576).toFixed(1)+" MB" : (file.size/1024).toFixed(0)+" KB";
      const baseName = file.name.replace(/\.[^.]+$/, "");
      const draft = {
        id: "", name: baseName, type: "蝞∠?蝔?", version: "1.0",
        department: "", createdDate: "", author: "",
        retentionYears: 16, fileName: file.name, fileSize: sizeStr,
        fileType: ext.toUpperCase(), fileData: "", _status: "pending"
      };
      // Read as ArrayBuffer for metadata, then as DataURL for storage
      const arrReader = new FileReader();
      arrReader.onload = ev => {
        const ab = ev.target.result;
        // Extract metadata
        if (["docx","xlsx","pptx"].includes(ext)) {
          const m = parseDocxMeta(ab);
          if (m.title)    draft.name        = m.title;
          if (m.creator)  draft.author      = m.creator;
          if (m.revision) draft.version     = parseInt(m.revision)>0 ? `1.${parseInt(m.revision)-1}` : "1.0";
          if (m.created||m.modified) draft.createdDate = (m.created||m.modified).substring(0,10);
        } else if (ext === "pdf") {
          const m = parsePdfMeta(ab);
          if (m.title)  draft.name        = m.title  || draft.name;
          if (m.author) draft.author      = m.author;
          if (m.date)   draft.createdDate = m.date;
        }
        // Now read as DataURL
        const b64r = new FileReader();
        b64r.onload = e2 => { draft.fileData = e2.target.result; resolve(draft); };
        b64r.readAsDataURL(file);
      };
      arrReader.readAsArrayBuffer(file);
    });
  }

  // ?? Single upload handler ?????????????????????????????????????????????????
  async function handleSingleFileUpload(e) {
    const file = e.target.files[0]; if (!file) return;
    const draft = await processFile(file);
    setNewDoc(prev => ({ ...prev, ...draft }));
  }
  function handleSingleAdd() {
    if (!newDoc.id.trim()||!newDoc.name.trim()||!newDoc.department.trim()||!newDoc.createdDate) {
      setErr("隢‵撖急???憛急?雿??辣蝺刻???蝔晞摰??摰??); return;
    }
    setErr("");
    setDocuments(prev => [...prev, { ...newDoc, retentionYears: parseInt(newDoc.retentionYears)||16 }]);
    setMode(null); setNewDoc({ ...emptyDoc });
  }

  // ?? Bulk upload handlers ??????????????????????????????????????????????????
  async function handleBulkFiles(files) {
    if (!files || files.length === 0) return;
    setBulkDone(false);
    const drafts = await Promise.all(Array.from(files).map(processFile));
    setBulkItems(prev => [...prev, ...drafts]);
  }
  function updateBulkItem(idx, field, value) {
    setBulkItems(prev => prev.map((item, i) => i === idx ? { ...item, [field]: value } : item));
  }
  function removeBulkItem(idx) {
    setBulkItems(prev => prev.filter((_, i) => i !== idx));
  }
  function confirmBulkUpload() {
    const valid = bulkItems.filter(d => d.id.trim() && d.name.trim() && d.department.trim() && d.createdDate);
    const invalid = bulkItems.length - valid.length;
    if (invalid > 0) { setErr(`撠? ${invalid} 蝑??憛怠??湛??嚗楊??蝔晞????`); return; }
    setErr("");
    setDocuments(prev => [...prev, ...valid.map(d => ({ ...d, retentionYears: parseInt(d.retentionYears)||16, _status: undefined }))]);
    setBulkItems([]); setBulkDone(true);
    setTimeout(() => { setMode(null); setBulkDone(false); }, 1500);
  }
  function closeModal() { setMode(null); setNewDoc({ ...emptyDoc }); setBulkItems([]); setErr(""); setBulkDone(false); }

  // ?? Shared styles ?????????????????????????????????????????????????????????
  const dropZoneStyle = over => ({
    display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center",
    gap:10, background: over?"rgba(124,58,237,0.12)":"rgba(255,255,255,0.03)",
    border:`2px dashed ${over?"rgba(124,58,237,0.9)":"rgba(124,58,237,0.4)"}`,
    borderRadius:14, padding:"28px 20px", cursor:"pointer", transition:"all 0.2s", textAlign:"center"
  });

  return (
    <div>
      <SectionHeader title="?辣?蝞⊥" count={documents.length} color="#a78bfa" />
      <div style={{ display:"flex", gap:12, marginBottom:20, flexWrap:"wrap" }}>
        <StatCard label="蝞∠???"  value={documents.filter(d=>d.type==="蝞∠???").length}  color="#a78bfa" />
        <StatCard label="蝞∠?蝔?"  value={documents.filter(d=>d.type==="蝞∠?蝔?").length}  color="#60a5fa" />
        <StatCard label="雿平???? value={documents.filter(d=>d.type==="雿平????).length} color="#34d399" />
        <StatCard label="蝮賣?隞嗆"  value={documents.length} color="#f97316" />
      </div>

      {/* Action buttons */}
      <div style={{ display:"flex", gap:10, justifyContent:"flex-end", marginBottom:14 }}>
        <button onClick={() => { setMode("bulk"); setErr(""); }} style={{ background:"linear-gradient(135deg,#0891b2,#06b6d4)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"9px 18px", fontSize:13, fontWeight:700 }}>
          &#128229; ?寥?銝
        </button>
        <button onClick={() => { setMode("single"); setErr(""); }} style={{ background:"linear-gradient(135deg,#7c3aed,#4f46e5)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"9px 18px", fontSize:13, fontWeight:700 }}>
          嚗??啣??辣
        </button>
      </div>

      {/* Document table */}
      <div style={{ overflowX:"auto" }}>
        <table style={{ width:"100%", borderCollapse:"collapse", fontSize:13 }}>
          <thead><tr>{["?辣蝺刻?","?辣?迂","憿","?","?嗅??券?","?嗅??交?","?嗅???,"靽???,"瑼?",""].map(h=>(
            <th key={h} style={{ textAlign:"left", padding:"10px 12px", color:"#64748b", fontWeight:600, borderBottom:"1px solid rgba(255,255,255,0.06)", whiteSpace:"nowrap" }}>{h}</th>
          ))}</tr></thead>
          <tbody>
            {enriched.map((doc, i) => (
              <tr key={doc.id} style={{ background: i%2===0?"rgba(255,255,255,0.02)":"transparent" }}>
                <td style={{ padding:"10px 12px", color:"#60a5fa", fontWeight:700, fontFamily:"monospace" }}>{doc.id}</td>
                <td style={{ padding:"10px 12px", color:"#e2e8f0", fontWeight:600 }}>{doc.name}</td>
                <td style={{ padding:"10px 12px" }}><Badge color={doc.type==="蝞∠???"?"#a78bfa":"#60a5fa"}>{doc.type}</Badge></td>
                <td style={{ padding:"10px 12px" }}><span style={{ background:"rgba(34,197,94,0.1)", color:"#4ade80", borderRadius:6, padding:"2px 8px", fontWeight:700, fontFamily:"monospace" }}>v{doc.version}</span></td>
                <td style={{ padding:"10px 12px", color:"#94a3b8" }}>{doc.department}</td>
                <td style={{ padding:"10px 12px", color:"#94a3b8", whiteSpace:"nowrap" }}>{formatDate(doc.createdDate)}</td>
                <td style={{ padding:"10px 12px", color:"#94a3b8" }}>{doc.author}</td>
                <td style={{ padding:"10px 12px", whiteSpace:"nowrap" }}><span style={{ color:doc.daysToExpiry<365?"#f97316":"#64748b", fontFamily:"monospace", fontSize:12 }}>{formatDate(doc.expiryStr)}</span></td>
                <td style={{ padding:"10px 12px" }}>
{doc.pdfPath ? (<a href={toAbsoluteAppUrl(doc.pdfPath)} target="_blank" rel="noopener noreferrer" style={{ color:"#fca5a5", fontSize:11, textDecoration:"none", background:"rgba(239,68,68,0.1)", borderRadius:6, padding:"3px 8px", border:"1px solid rgba(239,68,68,0.3)", marginRight:4 }}>&#128196; PDF</a>) : null}
                  {doc.fileData ? (<a href={doc.fileData} download={doc.fileName||doc.id} style={{ color:"#60a5fa", fontSize:11, textDecoration:"none", background:"rgba(96,165,250,0.1)", borderRadius:6, padding:"3px 8px", border:"1px solid rgba(96,165,250,0.3)" }}>&#8595; {doc.fileType||"銝?"}</a>) : null}
                  {!doc.pdfPath && !doc.fileData && <span style={{ color:"#374151", fontSize:11 }}>?⊥?獢?/span>}
                </td>
                <td style={{ padding:"10px 12px" }}><button onClick={() => setModal(doc)} style={{ background:"rgba(255,255,255,0.06)", border:"1px solid rgba(255,255,255,0.1)", borderRadius:6, color:"#94a3b8", cursor:"pointer", padding:"4px 10px", fontSize:11 }}>閰單?</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Detail modal */}
      {modal && (
        <Modal title={`?辣閰單?嚗?{modal.id}`} onClose={() => setModal(null)}>
          <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:16, marginBottom:16 }}>
            {[["?辣蝺刻?",modal.id],["?辣?迂",modal.name],["憿",modal.type],["?",`v${modal.version}`],["?嗅??券?",modal.department],["?嗅??交?",formatDate(modal.createdDate)],["?嗅???,modal.author],["靽?撟湧?",`${modal.retentionYears} 撟循],["靽??唳???,formatDate(modal.expiryStr)],["頝??,`${modal.daysToExpiry} 憭奈]].map(([k,v]) => (
              <div key={k}><div style={{ fontSize:11, color:"#64748b", marginBottom:4 }}>{k}</div><div style={{ color:"#e2e8f0", fontWeight:600, fontSize:14 }}>{v}</div></div>
            ))}
          </div>
          {(modal.pdfPath || modal.docxPath) && (
            <div style={{ display:"flex", flexDirection:"column", gap:10, marginBottom:10 }}>
              {modal.pdfPath && (
                <div style={{ background:"rgba(239,68,68,0.07)", border:"1px solid rgba(239,68,68,0.25)", borderRadius:10, padding:14 }}>
                  <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", gap:12, flexWrap:"wrap" }}>
                    <div>
                      <div style={{ fontSize:12, color:"#fca5a5", fontWeight:700, marginBottom:3 }}>&#128196; PDF 甇??瑼?</div>
                      <div style={{ fontSize:11, color:"#94a3b8", wordBreak:"break-all" }}>{modal.rawPdfPath || modal.pdfPath}</div>
                    </div>
                    <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
<a href={toAbsoluteAppUrl(modal.pdfPath)} target="_blank" rel="noopener noreferrer" style={{ background:"linear-gradient(135deg,#dc2626,#ef4444)", color:"#fff", padding:"8px 18px", borderRadius:8, fontSize:13, fontWeight:700, textDecoration:"none", whiteSpace:"nowrap" }}>&#128065; ?? PDF</a>
                    </div>
                  </div>
<iframe src={toAbsoluteAppUrl(modal.pdfPath)} title={`${modal.id}-pdf-preview`} style={{ width:"100%", height:320, marginTop:12, border:"1px solid rgba(239,68,68,0.16)", borderRadius:8, background:"#fff" }} />
                </div>
              )}
              {modal.docxPath && (
                <div style={{ background:"rgba(96,165,250,0.07)", border:"1px solid rgba(96,165,250,0.2)", borderRadius:10, padding:14 }}>
                  <div style={{ fontSize:12, color:"#93c5fd", fontWeight:700, marginBottom:3 }}>?舐楊頛舀?獢?/div>
                  <div style={{ fontSize:11, color:"#94a3b8", wordBreak:"break-all" }}>{modal.rawDocxPath || modal.docxPath}</div>
<a href={toAbsoluteAppUrl(modal.docxPath)} target="_blank" rel="noopener noreferrer" style={{ display:"inline-block", marginTop:10, background:"linear-gradient(135deg,#2563eb,#3b82f6)", color:"#fff", padding:"8px 18px", borderRadius:8, fontSize:13, fontWeight:700, textDecoration:"none", whiteSpace:"nowrap" }}>???舐楊頛舀?</a>
                </div>
              )}
              {(modal.selectedFile || modal.folderPath) && (
                <div style={{ background:"rgba(255,255,255,0.03)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:10, padding:12 }}>
                  <div style={{ fontSize:12, color:"#cbd5e1", fontWeight:700, marginBottom:6 }}>銝餅??桀???閮?/div>
                  {modal.selectedFile ? <div style={{ fontSize:11, color:"#94a3b8", wordBreak:"break-all" }}>?怠?甇??瑼?嚗modal.selectedFile}</div> : null}
                  {modal.folderPath ? <div style={{ fontSize:11, color:"#94a3b8", wordBreak:"break-all", marginTop:4 }}>鞈?憭曆?蝵殷?{modal.folderPath}</div> : null}
                </div>
              )}
            </div>
          )}
          {modal.fileName && (
            <div style={{ background:"rgba(96,165,250,0.07)", border:"1px solid rgba(96,165,250,0.2)", borderRadius:10, padding:14, display:"flex", alignItems:"center", justifyContent:"space-between" }}>
              <div>
                <div style={{ fontSize:13, color:"#93c5fd", fontWeight:700 }}>{modal.fileName}</div>
                <div style={{ fontSize:11, color:"#64748b", marginTop:4 }}>{modal.fileType} ??{modal.fileSize}</div>
              </div>
              {modal.fileData && <a href={modal.fileData} download={modal.fileName} style={{ background:"linear-gradient(135deg,#7c3aed,#4f46e5)", color:"#fff", padding:"8px 18px", borderRadius:8, fontSize:13, fontWeight:700, textDecoration:"none" }}>&#8595; 銝?瑼?</a>}
            </div>
          )}
        </Modal>
      )}

      {/* ?? SINGLE ADD MODAL ??????????????????????????????????????????????????? */}
      {mode === "single" && (
        <Modal title="?啣??辣" onClose={closeModal}>
          <div style={{ display:"flex", flexDirection:"column", gap:14 }}>
            <div>
              <div style={{ fontSize:12, color:"#64748b", marginBottom:6, fontWeight:600 }}>銝?辣嚗?芸?霈??Word / PDF Metadata嚗?/div>
              <label style={{ display:"flex", alignItems:"center", gap:12, background:"rgba(255,255,255,0.03)", border:"2px dashed rgba(124,58,237,0.4)", borderRadius:12, padding:"14px 18px", cursor:"pointer" }}
                onMouseEnter={e=>e.currentTarget.style.borderColor="rgba(124,58,237,0.8)"}
                onMouseLeave={e=>e.currentTarget.style.borderColor="rgba(124,58,237,0.4)"}>
                <input type="file" accept=".pdf,.docx,.xlsx,.pptx,.doc,.txt" onChange={handleSingleFileUpload} style={{ display:"none" }} />
                <span style={{ fontSize:28 }}>&#128196;</span>
                <div>
                  {newDoc.fileName
                    ? <><div style={{ color:"#a78bfa", fontWeight:700 }}>{newDoc.fileName}</div><div style={{ color:"#64748b", fontSize:12 }}>{newDoc.fileType} ??{newDoc.fileSize}</div></>
                    : <><div style={{ color:"#94a3b8", fontWeight:600 }}>暺??豢??桐?瑼?</div><div style={{ color:"#475569", fontSize:12, marginTop:3 }}>PDF?OCX?LSX??/div></>
                  }
                </div>
              </label>
            </div>
            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:12 }}>
              {[["?辣蝺刻? *","id","text"],["? *","version","text"],["?嗅??券? *","department","text"],["?嗅???,"author","text"]].map(([label,field,type]) => (
                <div key={field}>
                  <div style={{ fontSize:12, color:"#64748b", marginBottom:5 }}>{label}</div>
                  <input type={type} value={newDoc[field]} onChange={e=>setNewDoc({...newDoc,[field]:e.target.value})} style={inputStyle} placeholder={field==="id"?"MP-XX":""} />
                </div>
              ))}
            </div>
            <div>
              <div style={{ fontSize:12, color:"#64748b", marginBottom:5 }}>?辣?迂 *</div>
              <input type="text" value={newDoc.name} onChange={e=>setNewDoc({...newDoc,name:e.target.value})} style={inputStyle} />
            </div>
            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:12 }}>
              <div>
                <div style={{ fontSize:12, color:"#64748b", marginBottom:5 }}>?嗅??交? *</div>
                <input type="date" value={newDoc.createdDate} onChange={e=>setNewDoc({...newDoc,createdDate:e.target.value})} style={inputStyle} />
              </div>
              <div>
                <div style={{ fontSize:12, color:"#64748b", marginBottom:5 }}>靽?撟湧?嚗僑嚗?/div>
                <input type="number" value={newDoc.retentionYears} onChange={e=>setNewDoc({...newDoc,retentionYears:e.target.value})} style={inputStyle} min="1" max="99" />
              </div>
              <div>
                <div style={{ fontSize:12, color:"#64748b", marginBottom:5 }}>憿</div>
                <select value={newDoc.type} onChange={e=>setNewDoc({...newDoc,type:e.target.value})} style={inputStyle}>
                  <option>蝞∠???</option><option>蝞∠?蝔?</option><option>雿平????/option><option>銵典</option>
                </select>
              </div>
            </div>
            {err && <div style={{ background:"rgba(239,68,68,0.1)", border:"1px solid rgba(239,68,68,0.3)", borderRadius:8, padding:"10px 14px", color:"#fca5a5", fontSize:13 }}>{err}</div>}
            <button onClick={handleSingleAdd} style={{ background:"linear-gradient(135deg,#7c3aed,#4f46e5)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"13px 24px", fontSize:15, fontWeight:700 }}>嚗?蝣箄??啣??辣</button>
          </div>
        </Modal>
      )}

      {/* ?? BULK UPLOAD MODAL ?????????????????????????????????????????????????? */}
      {mode === "bulk" && (
        <Modal title={`?寥?銝?辣嚗歇??${bulkItems.length} 蝑?`} onClose={closeModal}>
          <div style={{ display:"flex", flexDirection:"column", gap:16 }}>

            {/* Drop zone */}
            <div
              style={dropZoneStyle(dragOver)}
              onDragOver={e=>{ e.preventDefault(); setDragOver(true); }}
              onDragLeave={()=>setDragOver(false)}
              onDrop={e=>{ e.preventDefault(); setDragOver(false); handleBulkFiles(e.dataTransfer.files); }}
            >
              <span style={{ fontSize:40 }}>&#128229;</span>
              <div style={{ color:"#a78bfa", fontWeight:700, fontSize:15 }}>?憭?獢甇方?</div>
              <div style={{ color:"#64748b", fontSize:12 }}>?舀 PDF?OCX?LSX?PTX?XT嚗?圾??Metadata</div>
              <label style={{ marginTop:6, background:"rgba(124,58,237,0.15)", border:"1px solid rgba(124,58,237,0.5)", borderRadius:8, color:"#a78bfa", cursor:"pointer", padding:"8px 20px", fontSize:13, fontWeight:700 }}>
                <input type="file" multiple accept=".pdf,.docx,.xlsx,.pptx,.doc,.txt" onChange={e=>handleBulkFiles(e.target.files)} style={{ display:"none" }} />
                ?????獢?
              </label>
            </div>

            {/* Item list */}
            {bulkItems.length > 0 && (
              <div style={{ display:"flex", flexDirection:"column", gap:10, maxHeight:420, overflowY:"auto", paddingRight:4 }}>
                {/* Header row */}
                <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 0.8fr 0.7fr 0.7fr 28px", gap:6, fontSize:11, color:"#64748b", fontWeight:600, padding:"0 2px" }}>
                  <span>?辣蝺刻? *</span><span>?迂 *</span><span>?券? *</span><span>?交? *</span><span>? / 憿</span><span></span>
                </div>
                {bulkItems.map((item, idx) => (
                  <div key={idx} style={{ background:"rgba(255,255,255,0.03)", border:"1px solid rgba(255,255,255,0.07)", borderRadius:10, padding:"10px 12px" }}>
                    {/* File info row */}
                    <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:8 }}>
                      <div style={{ display:"flex", alignItems:"center", gap:8 }}>
                        <span style={{ fontSize:16 }}>&#128196;</span>
                        <span style={{ fontSize:12, color:"#a78bfa", fontWeight:600 }}>{item.fileName}</span>
                        <span style={{ fontSize:11, color:"#475569" }}>{item.fileSize} ??{item.fileType}</span>
                      </div>
                      <button onClick={()=>removeBulkItem(idx)} style={{ background:"rgba(239,68,68,0.15)", border:"1px solid rgba(239,68,68,0.3)", borderRadius:6, color:"#fca5a5", cursor:"pointer", padding:"2px 8px", fontSize:12 }}>??/button>
                    </div>
                    {/* Editable fields */}
                    <div style={{ display:"grid", gridTemplateColumns:"0.8fr 1.5fr 0.9fr 0.85fr 0.6fr 0.6fr", gap:6 }}>
                      <input value={item.id} onChange={e=>updateBulkItem(idx,"id",e.target.value)} placeholder="蝺刻? *" style={{ ...inputStyle, fontSize:12, padding:"6px 8px" }} />
                      <input value={item.name} onChange={e=>updateBulkItem(idx,"name",e.target.value)} placeholder="?迂 *" style={{ ...inputStyle, fontSize:12, padding:"6px 8px" }} />
                      <input value={item.department} onChange={e=>updateBulkItem(idx,"department",e.target.value)} placeholder="?券? *" style={{ ...inputStyle, fontSize:12, padding:"6px 8px" }} />
                      <input type="date" value={item.createdDate} onChange={e=>updateBulkItem(idx,"createdDate",e.target.value)} style={{ ...inputStyle, fontSize:12, padding:"6px 8px" }} />
                      <input value={item.version} onChange={e=>updateBulkItem(idx,"version",e.target.value)} placeholder="?" style={{ ...inputStyle, fontSize:12, padding:"6px 8px" }} />
                      <select value={item.type} onChange={e=>updateBulkItem(idx,"type",e.target.value)} style={{ ...inputStyle, fontSize:11, padding:"6px 4px" }}>
                        <option>蝞∠???</option><option>蝞∠?蝔?</option><option>雿平????/option><option>銵典</option>
                      </select>
                    </div>
                    {/* Author & retention (collapsed row) */}
                    <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:6, marginTop:6 }}>
                      <input value={item.author} onChange={e=>updateBulkItem(idx,"author",e.target.value)} placeholder="?嗅??? style={{ ...inputStyle, fontSize:12, padding:"6px 8px" }} />
                      <input type="number" value={item.retentionYears} onChange={e=>updateBulkItem(idx,"retentionYears",e.target.value)} placeholder="靽?撟湧?" style={{ ...inputStyle, fontSize:12, padding:"6px 8px" }} min="1" max="99" />
                    </div>
                  </div>
                ))}
              </div>
            )}

            {bulkItems.length === 0 && (
              <div style={{ textAlign:"center", color:"#475569", fontSize:13, padding:"10px 0" }}>撠?豢?隞颱?瑼?</div>
            )}

            {err && <div style={{ background:"rgba(239,68,68,0.1)", border:"1px solid rgba(239,68,68,0.3)", borderRadius:8, padding:"10px 14px", color:"#fca5a5", fontSize:13 }}>{err}</div>}
            {bulkDone && <div style={{ background:"rgba(34,197,94,0.1)", border:"1px solid rgba(34,197,94,0.3)", borderRadius:8, padding:"10px 14px", color:"#86efac", fontSize:13 }}>??撌脫????{bulkItems.length} 蝑?隞塚?</div>}

            <div style={{ display:"flex", gap:10 }}>
              <button onClick={closeModal} style={{ flex:1, background:"rgba(255,255,255,0.06)", border:"1px solid rgba(255,255,255,0.15)", borderRadius:10, color:"#94a3b8", cursor:"pointer", padding:"12px 0", fontSize:14, fontWeight:600 }}>??</button>
              <button onClick={confirmBulkUpload} disabled={bulkItems.length===0} style={{ flex:2, background: bulkItems.length===0?"rgba(124,58,237,0.3)":"linear-gradient(135deg,#0891b2,#06b6d4)", border:"none", borderRadius:10, color:"#fff", cursor: bulkItems.length===0?"not-allowed":"pointer", padding:"12px 0", fontSize:15, fontWeight:700 }}>
                &#128229; 蝣箄??臬?券 {bulkItems.length} 蝑?隞?
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}

// ??? TRAINING TAB ?????????????????????????????????????????????????????????????
