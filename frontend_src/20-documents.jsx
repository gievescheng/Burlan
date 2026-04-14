function sortByDocumentId(items) {
  return [...items].sort((a, b) => String(a.id || "").localeCompare(String(b.id || ""), "zh-Hant", { numeric: true, sensitivity: "base" }));
}

function buildIsoDocumentMap(documents, manuals) {
  const firstLevel = [];
  const procedures = [];
  const thirdLevelMap = new Map();
  const procedureMap = new Map();
  const orphanForms = [];
  const orphanRecords = [];

  const getProcedureKey = id => {
    const match = String(id || "").match(/^MP-(\d+)/i);
    return match ? String(parseInt(match[1], 10)).padStart(2, "0") : "";
  };

  const addThirdLevel = doc => {
    if (!doc || !doc.id) return;
    if (!thirdLevelMap.has(doc.id)) thirdLevelMap.set(doc.id, doc);
  };

  documents.forEach(doc => {
    if (/^MM-/i.test(doc.id) || doc.type === "管理手冊") {
      firstLevel.push(doc);
      return;
    }
    if (/^MP-/i.test(doc.id)) {
      procedures.push(doc);
      procedureMap.set(getProcedureKey(doc.id), { procedure: doc, forms: [], records: [] });
      return;
    }
    if (/^RW-/i.test(doc.id) || doc.type === "作業指導書") {
      addThirdLevel(doc);
    }
  });

  manuals.forEach(addThirdLevel);

  documents.forEach(doc => {
    const match = String(doc.id || "").match(/^(FR|RC)-(\d+)/i);
    if (!match) return;
    const bucket = procedureMap.get(String(parseInt(match[2], 10)).padStart(2, "0"));
    if (!bucket) {
      if (match[1].toUpperCase() === "FR") orphanForms.push(doc);
      else orphanRecords.push(doc);
      return;
    }
    if (match[1].toUpperCase() === "FR") bucket.forms.push(doc);
    else bucket.records.push(doc);
  });

  const bundles = procedures
    .map(proc => {
      const key = getProcedureKey(proc.id);
      const bucket = procedureMap.get(key) || { procedure: proc, forms: [], records: [] };
      return {
        procedure: proc,
        forms: sortByDocumentId(bucket.forms),
        records: sortByDocumentId(bucket.records),
      };
    })
    .sort((a, b) => String(a.procedure.id).localeCompare(String(b.procedure.id), "zh-Hant", { numeric: true, sensitivity: "base" }));

  return {
    firstLevel: sortByDocumentId(firstLevel),
    secondLevel: sortByDocumentId(procedures),
    thirdLevel: sortByDocumentId(Array.from(thirdLevelMap.values())),
    bundles,
    orphanForms: sortByDocumentId(orphanForms),
    orphanRecords: sortByDocumentId(orphanRecords),
  };
}

function IsoDocumentCard({ doc, accent = "#60a5fa", showPaths = false, containerRef = null, highlighted = false }) {
  const path = doc.pdfPath || doc.docxPath || doc.fileName || "";
  return (
    <div ref={containerRef} style={{ background:highlighted ? "rgba(59,130,246,0.14)" : "rgba(255,255,255,0.03)", border:highlighted ? "1px solid rgba(59,130,246,0.45)" : `1px solid ${accent}33`, borderRadius:14, padding:16, boxShadow: highlighted ? "0 0 0 2px rgba(147,197,253,0.18)" : "none" }}>
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", gap:12 }}>
        <div>
          <div style={{ fontSize:11, fontFamily:"monospace", color:accent, fontWeight:700 }}>{doc.id}</div>
          <div style={{ fontSize:14, fontWeight:700, color:"#e2e8f0", marginTop:6 }}>{doc.name}</div>
        </div>
        <Badge color={accent}>{doc.type}</Badge>
      </div>
      <div style={{ display:"flex", gap:12, flexWrap:"wrap", marginTop:10, fontSize:12, color:"#94a3b8" }}>
        <span>部門: {doc.department || "未填寫"}</span>
        <span>版本: v{doc.version || "?"}</span>
        {doc.author && <span>作者: {doc.author}</span>}
      </div>
      {showPaths && path && <div style={{ marginTop:10, fontSize:11, color:"#64748b", wordBreak:"break-all" }}>{path}</div>}
    </div>
  );
}

function IsoProcedureBundle({ bundle, showPaths = false, containerRef = null, highlighted = false }) {
  const sections = [
    { title: "表單", items: bundle.forms, color: "#22c55e" },
    { title: "記錄", items: bundle.records, color: "#f59e0b" },
  ];

  return (
    <div ref={containerRef} style={{ background:highlighted ? "rgba(59,130,246,0.12)" : "rgba(255,255,255,0.025)", border:highlighted ? "1px solid rgba(59,130,246,0.42)" : "1px solid rgba(255,255,255,0.08)", borderRadius:16, padding:18, boxShadow: highlighted ? "0 0 0 2px rgba(147,197,253,0.16)" : "none" }}>
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", gap:12, flexWrap:"wrap" }}>
        <div>
          <div style={{ fontSize:11, fontFamily:"monospace", color:"#60a5fa", fontWeight:700 }}>{bundle.procedure.id}</div>
          <div style={{ fontSize:16, fontWeight:800, color:"#e2e8f0", marginTop:6 }}>{bundle.procedure.name}</div>
          <div style={{ display:"flex", gap:12, flexWrap:"wrap", marginTop:8, fontSize:12, color:"#94a3b8" }}>
            <span>部門: {bundle.procedure.department || "未填寫"}</span>
            <span>版本: v{bundle.procedure.version || "?"}</span>
            <span>表單: {bundle.forms.length}</span>
            <span>記錄: {bundle.records.length}</span>
          </div>
        </div>
        <Badge color="#60a5fa">二階文件</Badge>
      </div>
      <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(280px, 1fr))", gap:14, marginTop:18 }}>
        {sections.map(section => (
          <div key={section.title} style={{ background:"rgba(15,23,42,0.35)", border:`1px solid ${section.color}22`, borderRadius:12, padding:14 }}>
            <div style={{ fontSize:13, fontWeight:700, color:section.color, marginBottom:10 }}>{section.title} ({section.items.length})</div>
            {section.items.length === 0 ? (
              <div style={{ fontSize:12, color:"#64748b" }}>目前沒有歸屬到此程序的{section.title}</div>
            ) : (
              <div style={{ display:"flex", flexDirection:"column", gap:10 }}>
                {section.items.map(item => <IsoDocumentCard key={item.id} doc={item} accent={section.color} showPaths={showPaths} />)}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function DocumentsManagerTab({ documents, setDocuments, manuals, documentsSourceInfo, focusDocumentId, onFocusDocumentDone }) {
  const iso = buildIsoDocumentMap(documents, manuals);
  const itemRefs = useRef({});

  useEffect(() => {
    if (!focusDocumentId) return;
    const el = itemRefs.current[focusDocumentId];
    if (!el) return;
    el.scrollIntoView({ behavior:"smooth", block:"center" });
    const t = setTimeout(() => onFocusDocumentDone?.(), 1200);
    return () => clearTimeout(t);
  }, [focusDocumentId, onFocusDocumentDone, iso.firstLevel.length, iso.bundles.length, iso.thirdLevel.length]);

  return (
    <div>
      <PageIntro
        eyebrow="柏連文件中心"
        title="文件管理（柏連正式文件主清單）"
        description="這裡是柏連 QMS 文件中心。系統會先以柏連正式文件主清單為基準，再依 ISO 邏輯把一階、二階、三階文件，以及表單與記錄整理到對應程序底下。"
      >
        <div style={{ display:"flex", gap:12, flexWrap:"wrap" }}>
          <StatCard label="一階文件" value={iso.firstLevel.length} color="#a78bfa" sub="品質手冊 / 管理手冊" />
          <StatCard label="二階文件" value={iso.secondLevel.length} color="#60a5fa" sub="管理程序" />
          <StatCard label="三階文件" value={iso.thirdLevel.length} color="#14b8a6" sub="作業指導書" />
          <StatCard label="表單" value={documents.filter(doc => /^FR-/i.test(doc.id)).length} color="#22c55e" />
          <StatCard label="記錄" value={documents.filter(doc => /^RC-/i.test(doc.id)).length} color="#f59e0b" />
        </div>
        <DocumentsSourceBanner info={documentsSourceInfo} />
      </PageIntro>

      <div style={{ display:"flex", flexDirection:"column", gap:18 }}>
        <Panel title="第一層：品質手冊與管理手冊" description="這一層放制度總綱與管理原則，是整套 QMS 的最高層文件。" accent="#a78bfa">
          <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(280px, 1fr))", gap:12 }}>
            {iso.firstLevel.map(doc => <IsoDocumentCard key={doc.id} doc={doc} accent="#a78bfa" showPaths containerRef={el => { itemRefs.current[doc.id] = el; }} highlighted={focusDocumentId === doc.id} />)}
          </div>
        </Panel>

        <Panel title="第二層：管理程序與其表單 / 記錄" description="每一份程序文件下面都會帶出對應表單與記錄，方便你從程序一路追到實際執行紀錄。" accent="#60a5fa">
          <div style={{ display:"flex", flexDirection:"column", gap:14 }}>
            {iso.bundles.map(bundle => <IsoProcedureBundle key={bundle.procedure.id} bundle={bundle} showPaths containerRef={el => { itemRefs.current[bundle.procedure.id] = el; }} highlighted={focusDocumentId === bundle.procedure.id} />)}
          </div>
          {(iso.orphanForms.length > 0 || iso.orphanRecords.length > 0) && (
            <div style={{ marginTop:14, background:"rgba(245,158,11,0.08)", border:"1px solid rgba(245,158,11,0.2)", borderRadius:12, padding:14 }}>
              <div style={{ fontSize:13, fontWeight:700, color:"#fcd34d", marginBottom:10 }}>未歸屬程序的文件</div>
              <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(260px, 1fr))", gap:10 }}>
                {iso.orphanForms.map(doc => <IsoDocumentCard key={doc.id} doc={doc} accent="#22c55e" showPaths containerRef={el => { itemRefs.current[doc.id] = el; }} highlighted={focusDocumentId === doc.id} />)}
                {iso.orphanRecords.map(doc => <IsoDocumentCard key={doc.id} doc={doc} accent="#f59e0b" showPaths containerRef={el => { itemRefs.current[doc.id] = el; }} highlighted={focusDocumentId === doc.id} />)}
              </div>
            </div>
          )}
        </Panel>

        <Panel title="第三層：作業指導書" description="這一層是現場操作、設備使用與細部作業規則，通常最貼近實際執行。" accent="#14b8a6">
          <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(280px, 1fr))", gap:12 }}>
            {iso.thirdLevel.map(doc => <IsoDocumentCard key={doc.id} doc={doc} accent="#14b8a6" showPaths containerRef={el => { itemRefs.current[doc.id] = el; }} highlighted={focusDocumentId === doc.id} />)}
          </div>
        </Panel>

        <details style={{ background:uiTheme.panel, border:"1px solid " + uiTheme.panelBorder, borderRadius:18, padding:18, boxShadow: uiTheme.shadow }}>
          <summary style={{ cursor:"pointer", fontSize:14, fontWeight:700, color:"#e2e8f0" }}>進階管理：原始文件清單、上傳與編修</summary>
          <div style={{ marginTop:18 }}>
            <DocumentsTab documents={documents} setDocuments={setDocuments} />
          </div>
        </details>
      </div>
    </div>
  );
}

function LibraryHierarchyTab({ documents, manuals, documentsSourceInfo, focusDocumentId, onFocusDocumentDone }) {
  const [search, setSearch] = useState("");
  const [levelFilter, setLevelFilter] = useState("全部");
  const iso = buildIsoDocumentMap(documents, manuals);
  const itemRefs = useRef({});

  const matchesSearch = doc => {
    const q = search.trim().toLowerCase();
    if (!q) return true;
    return [doc.id, doc.name, doc.department, doc.docxPath, doc.pdfPath].filter(Boolean).some(value => String(value).toLowerCase().includes(q));
  };

  const filterByLevel = section => levelFilter === "全部" || levelFilter === section;
  const filteredBundles = iso.bundles.map(bundle => ({
    ...bundle,
    forms: bundle.forms.filter(matchesSearch),
    records: bundle.records.filter(matchesSearch),
    visible: matchesSearch(bundle.procedure) || bundle.forms.some(matchesSearch) || bundle.records.some(matchesSearch),
  })).filter(bundle => bundle.visible);
  const filteredFirst = iso.firstLevel.filter(matchesSearch);
  const filteredThird = iso.thirdLevel.filter(matchesSearch);

  useEffect(() => {
    if (!focusDocumentId) return;
    const targetDoc = [...iso.firstLevel, ...iso.secondLevel, ...iso.thirdLevel, ...iso.orphanForms, ...iso.orphanRecords].find(doc => doc.id === focusDocumentId);
    if (targetDoc) {
      if (iso.firstLevel.some(doc => doc.id === focusDocumentId)) setLevelFilter("一階文件");
      else if (iso.thirdLevel.some(doc => doc.id === focusDocumentId)) setLevelFilter("三階文件");
      else setLevelFilter("二階文件");
      const q = `${targetDoc.id} ${targetDoc.name || ""}`.trim();
      setSearch(q);
    }
    const timer = setTimeout(() => {
      const el = itemRefs.current[focusDocumentId];
      if (el) {
        el.scrollIntoView({ behavior:"smooth", block:"center" });
      }
      onFocusDocumentDone?.();
    }, 80);
    return () => clearTimeout(timer);
  }, [focusDocumentId, onFocusDocumentDone, iso.firstLevel.length, iso.secondLevel.length, iso.thirdLevel.length, iso.orphanForms.length, iso.orphanRecords.length]);

  return (
    <div>
      <PageIntro
        eyebrow="柏連文件庫"
        title="文件庫（柏連正式文件主清單）"
        description="這裡偏向查詢與閱讀。你可以先依 ISO 層級切換，再用搜尋快速縮小範圍，同時確認目前是不是讀到柏連正式文件主清單。"
      >
        <div style={{ display:"flex", gap:10, flexWrap:"wrap" }}>
          <input type="text" value={search} onChange={e => setSearch(e.target.value)} placeholder="搜尋文件名稱、編號、部門或路徑…" style={{ ...inputStyle, flex:1, minWidth:240 }} />
          {["全部", "一階文件", "二階文件", "三階文件"].map(item => (
            <button key={item} onClick={() => setLevelFilter(item)} style={levelFilter===item ? buttonStyle("warning") : buttonStyle("secondary")}>{item}</button>
          ))}
        </div>
        <DocumentsSourceBanner info={documentsSourceInfo} />
      </PageIntro>

      <div style={{ display:"flex", flexDirection:"column", gap:18 }}>
        {filterByLevel("一階文件") && (
          <Panel title="第一層文件" description="以制度與手冊為主，適合快速看總則與管理原則。" accent="#a78bfa">
            <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(280px, 1fr))", gap:12 }}>
              {filteredFirst.map(doc => <IsoDocumentCard key={doc.id} doc={doc} accent="#a78bfa" showPaths containerRef={el => { itemRefs.current[doc.id] = el; }} highlighted={focusDocumentId === doc.id} />)}
            </div>
          </Panel>
        )}

        {filterByLevel("二階文件") && (
          <Panel title="第二層文件與其表單 / 記錄" description="從程序直接展開其表單和記錄，最適合做稽核追查與缺漏檢查。" accent="#60a5fa">
            <div style={{ display:"flex", flexDirection:"column", gap:14 }}>
              {filteredBundles.map(bundle => <IsoProcedureBundle key={bundle.procedure.id} bundle={bundle} showPaths containerRef={el => { itemRefs.current[bundle.procedure.id] = el; }} highlighted={focusDocumentId === bundle.procedure.id} />)}
            </div>
          </Panel>
        )}

        {filterByLevel("三階文件") && (
          <Panel title="第三層文件" description="主要用來查看作業指導書與現場執行依據。" accent="#14b8a6">
            <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(280px, 1fr))", gap:12 }}>
              {filteredThird.map(doc => <IsoDocumentCard key={doc.id} doc={doc} accent="#14b8a6" showPaths containerRef={el => { itemRefs.current[doc.id] = el; }} highlighted={focusDocumentId === doc.id} />)}
            </div>
          </Panel>
        )}

        {filteredFirst.length === 0 && filteredBundles.length === 0 && filteredThird.length === 0 && (
          <div style={{ textAlign:"center", padding:"36px 20px", color:"#64748b", fontSize:14 }}>沒有符合篩選條件的文件。</div>
        )}

        <details style={{ background:uiTheme.panel, border:"1px solid " + uiTheme.panelBorder, borderRadius:18, padding:18, boxShadow: uiTheme.shadow }}>
          <summary style={{ cursor:"pointer", fontSize:14, fontWeight:700, color:"#e2e8f0" }}>原始文件庫視圖</summary>
          <div style={{ marginTop:18 }}>
            <LibraryTab documents={documents} manuals={manuals} />
          </div>
        </details>
      </div>
    </div>
  );
}

// ─── LIBRARY TAB ──────────────────────────────────────────────────────────────────────────────
function LibraryTab({ documents, manuals }) {
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("全部");
  const [preview, setPreview] = useState(null);

  // Merge all docs with pdfs + manuals
  const allItems = [
    ...documents.filter(d => d.pdfPath),
    ...manuals,
  ];
  const types = ["全部", "管理手冊", "管理程序", "作業指導書"];
  const filtered = allItems.filter(d => {
    const matchType = typeFilter === "全部" || d.type === typeFilter;
    const q = search.toLowerCase();
    const matchSearch = !q || d.name.toLowerCase().includes(q) || d.id.toLowerCase().includes(q) || (d.department||"").toLowerCase().includes(q);
    return matchType && matchSearch;
  });

  const typeColor = t => t==="管理手冊"?"#a78bfa":t==="管理程序"?"#60a5fa":"#34d399";

  return (
    <div>
      <SectionHeader title="文件庫（PDF 檔案）" count={allItems.length} color="#f97316" />
      <div style={{ display:"flex", gap:12, marginBottom:20, flexWrap:"wrap" }}>
        <StatCard label="管理手冊" value={allItems.filter(d=>d.type==="管理手冊").length} color="#a78bfa" />
        <StatCard label="管理程序" value={allItems.filter(d=>d.type==="管理程序").length} color="#60a5fa" />
        <StatCard label="作業指導書" value={allItems.filter(d=>d.type==="作業指導書").length} color="#34d399" />
        <StatCard label="總計" value={allItems.length} color="#f97316" />
      </div>

      {/* Search & Filter bar */}
      <div style={{ display:"flex", gap:10, marginBottom:18, flexWrap:"wrap" }}>
        <input
          type="text" value={search} onChange={e=>setSearch(e.target.value)}
          placeholder="搜尋文件名稱、編號、部門…"
          style={{ ...inputStyle, flex:1, minWidth:200, padding:"10px 14px" }}
        />
        <div style={{ display:"flex", gap:6 }}>
          {types.map(t => (
            <button key={t} onClick={()=>setTypeFilter(t)} style={{
              background: typeFilter===t ? "linear-gradient(135deg,#ea580c,#f97316)" : "rgba(255,255,255,0.05)",
              border: "1px solid " + (typeFilter===t ? "#f97316" : "rgba(255,255,255,0.1)"),
              borderRadius:8, color: typeFilter===t?"#fff":"#94a3b8",
              cursor:"pointer", padding:"8px 14px", fontSize:12, fontWeight:600
            }}>{t}</button>
          ))}
        </div>
      </div>

      {/* Document Cards Grid */}
      <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill, minmax(300px, 1fr))", gap:14 }}>
        {filtered.map(doc => (
          <div key={doc.id} style={{ background:"rgba(255,255,255,0.03)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:14, padding:18, display:"flex", flexDirection:"column", gap:10 }}>
            {/* Header */}
            <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start" }}>
              <div style={{ fontSize:11, fontFamily:"monospace", color:"#60a5fa", fontWeight:700 }}>{doc.id}</div>
              <Badge color={typeColor(doc.type)}>{doc.type}</Badge>
            </div>
            {/* Name */}
            <div style={{ fontSize:14, fontWeight:700, color:"#e2e8f0", lineHeight:1.4 }}>{doc.name}</div>
            {/* Description (for manuals) */}
            {doc.desc && <div style={{ fontSize:12, color:"#64748b", lineHeight:1.5 }}>{doc.desc}</div>}
            {/* Meta */}
            <div style={{ display:"flex", gap:12, fontSize:11, color:"#64748b", flexWrap:"wrap" }}>
              <span>版本: <b style={{color:"#4ade80"}}>v{doc.version}</b></span>
              <span>部門: {doc.department}</span>
              {doc.author && <span>作者: {doc.author}</span>}
            </div>
            {/* PDF button */}
            <div style={{ display:"flex", gap:8, marginTop:4 }}>
              <a
href={toAbsoluteAppUrl(doc.pdfPath)} target="_blank" rel="noopener noreferrer"
                style={{ flex:1, background:"linear-gradient(135deg,#dc2626,#ef4444)", color:"#fff",
                  padding:"10px 0", borderRadius:8, fontSize:13, fontWeight:700,
                  textDecoration:"none", textAlign:"center" }}
              >
                &#128196; 開啟 PDF
              </a>
              <button onClick={()=>setPreview(doc.pdfPath)} style={{
                background:"rgba(255,255,255,0.06)", border:"1px solid rgba(255,255,255,0.15)",
                borderRadius:8, color:"#94a3b8", cursor:"pointer",
                padding:"10px 14px", fontSize:12, fontWeight:600
              }}>預覽</button>
            </div>
          </div>
        ))}
      </div>
      {filtered.length === 0 && (
        <div style={{ textAlign:"center", padding:"40px 0", color:"#475569", fontSize:14 }}>未找到符合條件的文件</div>
      )}

      {/* PDF Preview Modal (iframe) */}
      {preview && (
        <div style={{ position:"fixed", inset:0, background:"rgba(0,0,0,0.85)", zIndex:1000, display:"flex", flexDirection:"column" }}>
          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", padding:"12px 20px", background:"rgba(15,23,42,0.95)", borderBottom:"1px solid rgba(255,255,255,0.1)" }}>
            <div style={{ fontSize:13, color:"#94a3b8", fontFamily:"monospace" }}>{preview.split("/").pop()}</div>
            <div style={{ display:"flex", gap:10 }}>
<a href={toAbsoluteAppUrl(preview)} target="_blank" rel="noopener noreferrer" style={{ background:"linear-gradient(135deg,#dc2626,#ef4444)", color:"#fff", padding:"6px 14px", borderRadius:7, fontSize:12, fontWeight:700, textDecoration:"none" }}>在新標籤開啟</a>
              <button onClick={()=>setPreview(null)} style={{ background:"rgba(255,255,255,0.1)", border:"1px solid rgba(255,255,255,0.2)", borderRadius:7, color:"#e2e8f0", cursor:"pointer", padding:"6px 14px", fontSize:13, fontWeight:700 }}>✕ 關閉</button>
            </div>
          </div>
          <iframe
src={toAbsoluteAppUrl(preview)}
            style={{ flex:1, border:"none", background:"#fff" }}
            title="PDF Preview"
          />
        </div>
      )}
    </div>
  );
}

// ─── DASHBOARD HOME ──────────────────────────────────────────────────────────
// ─── SVG CHART PRIMITIVES ────────────────────────────────────────────────────

