function NotificationTab({ instruments, documents, equipment, suppliers, nonConformances, auditPlans }) {
  const items = collectNotificationItems({ instruments, documents, equipment, suppliers, nonConformances, auditPlans });
  const [googleStatus, setGoogleStatus] = useState({ configured: false, connected: false, email: "", redirect_uri: "" });
  const [googleForm, setGoogleForm] = useState({ client_id: "", client_secret: "" });
  const [googleBusy, setGoogleBusy] = useState("");
  const [googleMessage, setGoogleMessage] = useState("");
  const [notionForm, setNotionForm] = useState({ token: "", db_id: "" });
  const [notionBusyKey, setNotionBusyKey] = useState("");
  const [notionMessage, setNotionMessage] = useState("");

  useEffect(() => {
    let cancelled = false;
    async function loadStatus() {
      try {
        const response = await fetch("/api/google-calendar/status");
        const payload = await response.json();
        if (!response.ok) throw new Error(payload.error || ("HTTP " + response.status));
        if (!cancelled) setGoogleStatus(payload);
      } catch (err) {
        if (!cancelled) setGoogleMessage("???Google ?蛛????????? " + err.message);
      }
    }
    loadStatus();
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const params = new URLSearchParams(window.location.search);
    const googleState = params.get("google");
    if (!googleState) return;
    const reason = params.get("reason");
    setGoogleMessage(googleState === "connected" ? "Google ?蛛?????堆?????? : "Google ????剜??: " + (reason || "unknown"));
    params.delete("google");
    params.delete("reason");
    params.set("tab", "notification");
    const next = window.location.pathname + "?" + params.toString();
    window.history.replaceState({}, "", next);
  }, []);

  async function refreshGoogleStatus() {
    const response = await fetch("/api/google-calendar/status");
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || ("HTTP " + response.status));
    setGoogleStatus(payload);
  }

  async function saveGoogleConfig() {
    setGoogleBusy("config");
    setGoogleMessage("");
    try {
      const response = await fetch("/api/google-calendar/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(googleForm),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || ("HTTP " + response.status));
      setGoogleStatus(payload);
      setGoogleMessage("Google Calendar ?桀????謢朝?);
      setGoogleForm(prev => ({ ...prev, client_secret: "" }));
    } catch (err) {
      setGoogleMessage("Google Calendar ?桀???剜??: " + err.message);
    } finally {
      setGoogleBusy("");
    }
  }

  async function startGoogleAuth() {
    setGoogleBusy("auth");
    setGoogleMessage("");
    try {
      const response = await fetch("/api/google-calendar/auth/start");
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || ("HTTP " + response.status));
      window.location.href = payload.auth_url;
    } catch (err) {
      setGoogleMessage("?賹? Google ????剜??: " + err.message);
      setGoogleBusy("");
    }
  }

  async function logoutGoogle() {
    setGoogleBusy("logout");
    setGoogleMessage("");
    try {
      const response = await fetch("/api/google-calendar/logout", { method: "POST" });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || ("HTTP " + response.status));
      setGoogleStatus(payload);
      setGoogleMessage("Google ?蛛??????謘?????);
    } catch (err) {
      setGoogleMessage("??謘?Google ?蛛?????? " + err.message);
    } finally {
      setGoogleBusy("");
    }
  }

  async function createGoogleEvents(batchItems, mode) {
    if (!batchItems.length) {
      setGoogleMessage("?獢??????祇?∴???????梱???);
      return;
    }
    setGoogleBusy(mode);
    setGoogleMessage("");
    try {
      const response = await fetch("/api/google-calendar/events", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ items: batchItems }),
      });
      const payload = await response.json();
      if (!response.ok && response.status !== 207) throw new Error(payload.error || ("HTTP " + response.status));
      const detail = (payload.results || []).filter(result => !result.success).map(result => result.title + ": " + result.error).join("??);
      setGoogleMessage(`Google ?蛛????∴???????? ${payload.success_count || 0} ????剜?? ${payload.failed_count || 0} ????{detail ? " ?剜?????? + detail : ""}`);
      await refreshGoogleStatus();
    } catch (err) {
      setGoogleMessage("?梁?? Google ?蛛??????隞?? " + err.message);
    } finally {
      setGoogleBusy("");
    }
  }

  async function sendToNotion(item) {
    if (!notionForm.token || !notionForm.db_id) {
      setNotionMessage("?ｇ???岳??Notion Token ??Database ID??);
      return;
    }
    setNotionBusyKey(item.key);
    setNotionMessage("");
    try {
      const response = await fetch("/api/notion", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          token: notionForm.token,
          db_id: notionForm.db_id,
          properties: {
            Name: { title: [{ text: { content: item.title } }] },
            Module: { rich_text: [{ text: { content: item.module } }] },
            Date: { date: { start: item.date } },
            Owner: { rich_text: [{ text: { content: item.owner || "" } }] },
            Summary: { rich_text: [{ text: { content: item.summary || "" } }] },
          },
        }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || payload.message || JSON.stringify(payload));
      setNotionMessage("??蹓鳴??Notion: " + item.title);
    } catch (err) {
      setNotionMessage("Notion ?梁???剜??: " + err.message);
    } finally {
      setNotionBusyKey("");
    }
  }

  function openMailDraft(item) {
    const subject = encodeURIComponent(item.title);
    const body = encodeURIComponent([
      "?鈭?: " + formatDate(item.date),
      "???: " + item.module,
      "?謢?: " + item.summary,
      "?滿?? " + (item.owner || "?????),
    ].join("\n"));
    window.location.href = `mailto:?subject=${subject}&body=${body}`;
  }

  const overdueCount = items.filter(item => item.days < 0).length;
  const thisWeekCount = items.filter(item => item.days >= 0 && item.days <= 7).length;
  const moduleCounts = items.reduce((acc, item) => {
    acc[item.module] = (acc[item.module] || 0) + 1;
    return acc;
  }, {});

  return (
    <div>
      <SectionHeader title="?謍船????" count={items.length} color="#f59e0b" />
      <div style={{ display:"flex", gap:12, marginBottom:20, flexWrap:"wrap" }}>
        <StatCard label="????株都?? value={items.length} color="#f59e0b" sub="30 ?剜???????" />
        <StatCard label="????" value={overdueCount} color="#ef4444" sub="??????" />
        <StatCard label="7 ?剜??? value={thisWeekCount} color="#f97316" sub="擗????" />
        <StatCard label="Google ???? value={googleStatus.connected ? "????" : googleStatus.configured ? "?綽??? : "??曇澈??} color={googleStatus.connected ? "#22c55e" : googleStatus.configured ? "#eab308" : "#64748b"} sub={googleStatus.email || "primary calendar"} />
      </div>

      <div style={{ display:"grid", gridTemplateColumns:"minmax(320px, 1.1fr) minmax(320px, 0.9fr)", gap:16, marginBottom:20 }}>
        <div style={{ background:"rgba(245,158,11,0.08)", border:"1px solid rgba(245,158,11,0.2)", borderRadius:14, padding:18 }}>
          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", gap:12, flexWrap:"wrap", marginBottom:12 }}>
            <div>
              <div style={{ fontSize:15, fontWeight:700, color:"#fef3c7" }}>Google ?蛛???/div>
              <div style={{ fontSize:12, color:"#fcd34d", marginTop:4 }}>????獢??謘踝?蟡??primary calendar??/div>
            </div>
            <Badge color={googleStatus.connected ? "#22c55e" : googleStatus.configured ? "#eab308" : "#94a3b8"}>{googleStatus.connected ? "???? : googleStatus.configured ? "?綽??? : "??曇澈??}</Badge>
          </div>

          <div style={{ display:"grid", gridTemplateColumns:"1fr", gap:12 }}>
            <div>
              <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>Google Client ID</div>
              <input value={googleForm.client_id} onChange={e => setGoogleForm(prev => ({ ...prev, client_id: e.target.value }))} placeholder="??? Google OAuth Client ID" style={inputStyle} />
            </div>
            <div>
              <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>Google Client Secret</div>
              <input type="password" value={googleForm.client_secret} onChange={e => setGoogleForm(prev => ({ ...prev, client_secret: e.target.value }))} placeholder="??? Google OAuth Client Secret" style={inputStyle} />
            </div>
            <div style={{ fontSize:11, color:"#94a3b8", lineHeight:1.6 }}>
              Redirect URI: <span style={{ color:"#e2e8f0", fontFamily:"monospace" }}>{googleStatus.redirect_uri || "??謘餉?"}</span>
            </div>
          </div>

          <div style={{ display:"flex", gap:10, flexWrap:"wrap", marginTop:14 }}>
            <button onClick={saveGoogleConfig} disabled={googleBusy !== ""} style={{ background:"linear-gradient(135deg,#b45309,#f59e0b)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"10px 16px", fontSize:13, fontWeight:700, opacity: googleBusy ? 0.6 : 1 }}>{googleBusy === "config" ? "?????.." : "????桀??"}</button>
            <button onClick={startGoogleAuth} disabled={googleBusy !== "" || !googleStatus.configured} style={{ background:"linear-gradient(135deg,#1d4ed8,#3b82f6)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"10px 16px", fontSize:13, fontWeight:700, opacity: (googleBusy || !googleStatus.configured) ? 0.6 : 1 }}>{googleBusy === "auth" ? "?????.." : "??? Google"}</button>
            <button onClick={() => createGoogleEvents(items, "batch")} disabled={googleBusy !== "" || !items.length} style={{ background:"linear-gradient(135deg,#0369a1,#0ea5e9)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"10px 16px", fontSize:13, fontWeight:700, opacity: (googleBusy || !items.length) ? 0.6 : 1 }}>{googleBusy === "batch" ? "?梁????.." : "??賂豢蝞? Google ?哨?颲?}</button>
            <button onClick={logoutGoogle} disabled={googleBusy !== "" || !googleStatus.connected} style={{ background:"rgba(239,68,68,0.14)", border:"1px solid rgba(239,68,68,0.3)", borderRadius:10, color:"#fca5a5", cursor:"pointer", padding:"10px 16px", fontSize:13, fontWeight:700, opacity: (googleBusy || !googleStatus.connected) ? 0.6 : 1 }}>{googleBusy === "logout" ? "?????.." : "??謘???"}</button>
          </div>
          {googleMessage && <div style={{ marginTop:12, fontSize:12, color:"#fde68a", lineHeight:1.6 }}>{googleMessage}</div>}
        </div>

        <div style={{ background:"rgba(99,102,241,0.08)", border:"1px solid rgba(99,102,241,0.2)", borderRadius:14, padding:18 }}>
          <div style={{ marginBottom:12 }}>
            <div style={{ fontSize:15, fontWeight:700, color:"#e0e7ff" }}>Notion ??抬??■??????/div>
            <div style={{ fontSize:12, color:"#c7d2fe", marginTop:4 }}>??威???蹓鳴? Notion?????豯佇? Email / Google ?梁???蹓嗽?/div>
          </div>

          <div style={{ display:"grid", gap:12 }}>
            <div>
              <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>Notion Token</div>
              <input type="password" value={notionForm.token} onChange={e => setNotionForm(prev => ({ ...prev, token: e.target.value }))} placeholder="secret_xxx" style={inputStyle} />
            </div>
            <div>
              <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>Notion Database ID</div>
              <input value={notionForm.db_id} onChange={e => setNotionForm(prev => ({ ...prev, db_id: e.target.value }))} placeholder="??? Notion Database ID" style={inputStyle} />
            </div>
          </div>
          <div style={{ marginTop:14, fontSize:12, color:"#a5b4fc", lineHeight:1.7 }}>
            ??澈??萇???`Name / Module / Date / Owner / Summary` ?叟?????選??蹇??遴?????冽??選???????Notion ??畸??鈭???莎??斗食??????對??瑞???迎????純?
          </div>
          {notionMessage && <div style={{ marginTop:12, fontSize:12, color:"#c7d2fe", lineHeight:1.6 }}>{notionMessage}</div>}
          <div style={{ marginTop:16 }}>
            <div style={{ fontSize:13, color:"#e2e8f0", fontWeight:700, marginBottom:8 }}>??????</div>
            <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
              {Object.entries(moduleCounts).map(([module, count]) => (
                <Badge key={module} color="#818cf8">{module} x {count}</Badge>
              ))}
              {items.length === 0 && <span style={{ fontSize:12, color:"#94a3b8" }}>?獢???????秋撚?謍船?????謕?/span>}
            </div>
          </div>
        </div>
      </div>

      <div style={{ display:"flex", flexDirection:"column", gap:12 }}>
        {items.map(item => (
          <div key={item.key} style={{ background: urgencyBg(item.days), border:"1px solid rgba(255,255,255,0.08)", borderRadius:14, padding:16 }}>
            <div style={{ display:"flex", justifyContent:"space-between", gap:12, flexWrap:"wrap", alignItems:"flex-start" }}>
              <div style={{ display:"flex", flexDirection:"column", gap:8 }}>
                <div style={{ display:"flex", gap:8, flexWrap:"wrap", alignItems:"center" }}>
                  <div style={{ fontSize:15, fontWeight:700, color:"#e2e8f0" }}>{item.title}</div>
                  <Badge color={urgencyColor(item.days)}>{item.statusText}</Badge>
                  <Badge color="#60a5fa">{item.module}</Badge>
                </div>
                <div style={{ fontSize:13, color:"#cbd5e1", lineHeight:1.6 }}>{item.summary}</div>
                <div style={{ fontSize:12, color:"#94a3b8" }}>
                  ?鈭? {formatDate(item.date)} {item.owner ? " / ?滿??" + item.owner : ""}
                </div>
              </div>
              <div style={{ display:"flex", gap:8, flexWrap:"wrap", justifyContent:"flex-end" }}>
                <button onClick={() => createGoogleEvents([item], "single:" + item.key)} disabled={googleBusy !== ""} style={{ background:"linear-gradient(135deg,#0369a1,#0ea5e9)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"9px 14px", fontSize:12, fontWeight:700, opacity: googleBusy ? 0.6 : 1 }}>{googleBusy === "single:" + item.key ? "?梁????.." : "?梁?? Google ?哨?颲?}</button>
                <button onClick={() => window.open(buildCalendarLink(item), "_blank", "noopener,noreferrer")} style={{ background:"rgba(255,255,255,0.06)", border:"1px solid rgba(255,255,255,0.16)", borderRadius:10, color:"#e2e8f0", cursor:"pointer", padding:"9px 14px", fontSize:12, fontWeight:700 }}>????梁????/button>
                <button onClick={() => sendToNotion(item)} disabled={notionBusyKey !== ""} style={{ background:"rgba(99,102,241,0.16)", border:"1px solid rgba(99,102,241,0.32)", borderRadius:10, color:"#c7d2fe", cursor:"pointer", padding:"9px 14px", fontSize:12, fontWeight:700, opacity: notionBusyKey ? 0.6 : 1 }}>{notionBusyKey === item.key ? "?蹓鳴??.." : "?蹓鳴? Notion"}</button>
                <button onClick={() => openMailDraft(item)} style={{ background:"rgba(245,158,11,0.14)", border:"1px solid rgba(245,158,11,0.3)", borderRadius:10, color:"#fde68a", cursor:"pointer", padding:"9px 14px", fontSize:12, fontWeight:700 }}>Email ??仿</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function AIWorkbenchTab({ documents, manuals, nonConformances }) {
  const fallbackSources = [...documents, ...manuals]
    .map(item => ({
      id: item.id,
      name: item.name,
      department: item.department || "",
      version: item.version || "",
      path: item.docxPath || item.pdfPath || "",
    }))
    .filter(item => item.path)
    .sort((a, b) => a.id.localeCompare(b.id));
  const [masterSources, setMasterSources] = useState([]);
  const [masterSourceInfo, setMasterSourceInfo] = useState({
    mode: "fallback",
    source_path: "",
    count: 0,
    pending_review_count: 0,
    message: "",
  });
  const sources = masterSources.length > 0 ? masterSources : fallbackSources;
  const sourceMetadata = sources.reduce((acc, item) => {
    acc[item.path] = {
      title: item.name,
      document_code: item.id,
      owner_dept: item.department,
      version: item.version,
      source_system: item.source_system || (masterSources.length > 0 ? "burlan_official_master" : "iso_local_library"),
    };
    return acc;
  }, {});

  const [apiBase, setApiBase] = useState(() => loadStoredState("audit_v2_api_base", "http://127.0.0.1:8890/api/v2"));
  const [serviceInfo, setServiceInfo] = useState({ service: "auto-audit-v2", database_mode: "unknown", openrouter_enabled: false });
  const [serviceMessage, setServiceMessage] = useState("");
  const [cacheBusy, setCacheBusy] = useState(false);
  const [cacheStatus, setCacheStatus] = useState({ compare_cache_count: 0, audit_cache_count: 0 });
  const [ingestBusy, setIngestBusy] = useState(false);
  const [ingestMessage, setIngestMessage] = useState("");
  const [ingestResult, setIngestResult] = useState(null);
  const [selectedPath, setSelectedPath] = useState(sources[0]?.path || "");
  const [compareMode, setCompareMode] = useState("generic");
  const [compareUseLlm, setCompareUseLlm] = useState(false);
  const [compareLeftPath, setCompareLeftPath] = useState(sources[0]?.path || "");
  const [compareRightPath, setCompareRightPath] = useState(sources[1]?.path || sources[0]?.path || "");
  const [compareBusy, setCompareBusy] = useState(false);
  const [compareExportBusy, setCompareExportBusy] = useState(false);
  const [compareDocxExportBusy, setCompareDocxExportBusy] = useState(false);
  const [compareResult, setCompareResult] = useState(null);
  const [compareMessage, setCompareMessage] = useState("");
  const [versionCandidatesBusy, setVersionCandidatesBusy] = useState(false);
  const [versionCandidates, setVersionCandidates] = useState([]);
  const [auditBusy, setAuditBusy] = useState(false);
  const [auditExportBusy, setAuditExportBusy] = useState(false);
  const [auditResult, setAuditResult] = useState(null);
  const [auditMessage, setAuditMessage] = useState("");
  const [historyBusy, setHistoryBusy] = useState(false);
  const [historyMode, setHistoryMode] = useState("all");
  const [historyQuery, setHistoryQuery] = useState("");
  const [historyItems, setHistoryItems] = useState([]);
  const [historyMessage, setHistoryMessage] = useState("");
  const [searchQuery, setSearchQuery] = useState("?閰? ??暑 ?踐??");
  const [searchBusy, setSearchBusy] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [qaQuestion, setQaQuestion] = useState("??刻麾?謘??殷??????制??踐????軋僚?????餅螂??縈?");
  const [qaScope, setQaScope] = useState("selected");
  const [qaBusy, setQaBusy] = useState(false);
  const [qaResult, setQaResult] = useState(null);
  const [qaMessage, setQaMessage] = useState("");
  const [spcBusy, setSpcBusy] = useState(false);
  const [spcResult, setSpcResult] = useState(null);
  const [spcMessage, setSpcMessage] = useState("");
  const [spcForm, setSpcForm] = useState({
    parameter_name: "Thickness",
    csv_text: "10.1,10.0,9.9,10.2,10.1",
    lsl: "9.5",
    usl: "10.5",
    target: "10.0",
  });
  const [deviationBusy, setDeviationBusy] = useState(false);
  const [deviationResult, setDeviationResult] = useState(null);
  const [deviationMessage, setDeviationMessage] = useState("");
  const [deviationForm, setDeviationForm] = useState(() => ({
    issue_description: nonConformances[0]?.description || "",
    process_step: "AOI ?潘??",
    lot_no: "LOT-20260301-A",
    severity: "medium",
  }));

  useEffect(() => {
    saveStoredState("audit_v2_api_base", apiBase);
  }, [apiBase]);

  useEffect(() => {
    let cancelled = false;
    async function loadBurlanMasterSources() {
      try {
        const payload = await apiJson("/api/burlan/master-documents");
        if (cancelled) return;
        const items = (payload.items || []).filter(item => item.path);
        setMasterSources(items);
        setMasterSourceInfo({
          mode: items.length > 0 ? "master" : "fallback",
          source_path: payload.source_path || "",
          count: payload.count || items.length,
          pending_review_count: payload.pending_review_count || 0,
          message: payload.message || "",
        });
      } catch (err) {
        if (cancelled) return;
        setMasterSources([]);
        setMasterSourceInfo({
          mode: "fallback",
          source_path: "",
          count: fallbackSources.length,
          pending_review_count: 0,
          message: "?獢??????賂?梁???皝?????畾??賹??? + err.message,
        });
      }
    }
    loadBurlanMasterSources();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!sources.length) return;
    if (!sources.some(item => item.path === selectedPath)) {
      setSelectedPath(sources[0]?.path || "");
    }
  }, [sources, selectedPath]);

  useEffect(() => {
    if (!sources.length) return;
    if (!sources.some(item => item.path === compareLeftPath)) {
      setCompareLeftPath(sources[0]?.path || "");
    }
    if (!sources.some(item => item.path === compareRightPath)) {
      setCompareRightPath(sources[1]?.path || sources[0]?.path || "");
    }
  }, [sources, compareLeftPath, compareRightPath]);

  useEffect(() => {
    setVersionCandidates([]);
    if (compareMode === "version") {
      setCompareRightPath("");
    }
  }, [compareLeftPath, compareMode]);

  useEffect(() => {
    let cancelled = false;
    async function loadHealth() {
      try {
        const payload = await callV2("/health");
        if (!cancelled) {
          setServiceInfo(payload.data || {});
          setServiceMessage("");
        }
        const cachePayload = await callV2("/cache/status");
        if (!cancelled) {
          setCacheStatus(cachePayload.data || {});
        }
        const historyPayload = await callV2("/history/runs?mode=all&limit=12");
        if (!cancelled) {
          setHistoryItems(historyPayload.data?.items || []);
          setHistoryMessage("");
        }
      } catch (err) {
        if (!cancelled) setServiceMessage("V2 ????垮謓舀?璇?: " + err.message);
      }
    }
    loadHealth();
    return () => {
      cancelled = true;
    };
  }, [apiBase]);

  async function callV2(path, options = {}) {
    const response = await fetch(apiBase + path, options);
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.message || payload.error || ("HTTP " + response.status));
    if (!payload.success) throw new Error(payload.message || payload.error_code || "V2 request failed");
    return payload;
  }

  async function runDocumentAudit() {
    if (!selectedPath) {
      setAuditMessage("?ｇ???鞊???刻麾??);
      return;
    }
    setAuditBusy(true);
    setAuditMessage("");
    try {
      const payload = await callV2("/documents/audit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: selectedPath }),
      });
      setAuditResult(payload.data);
      setAuditMessage("??刻麾?都赯望????);
      loadHistory(historyMode, historyQuery);
    } catch (err) {
      setAuditMessage("??刻麾?都赯望??: " + err.message);
    } finally {
      setAuditBusy(false);
    }
  }

  async function exportDocumentAuditWordReport() {
    if (!selectedPath) {
      setAuditMessage("?ｇ???鞊???刻麾??);
      return;
    }
    setAuditExportBusy(true);
    setAuditMessage("");
    try {
      const response = await fetch(apiBase + "/documents/audit/export/docx", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: selectedPath }),
      });
      if (!response.ok) {
        let payload = null;
        try {
          payload = await response.json();
        } catch (err) {
          payload = null;
        }
        throw new Error(payload?.message || ("HTTP " + response.status));
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "document_audit_report.docx";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      setAuditMessage("AI ??刻麾?都赯?Word ?????????);
      loadHistory(historyMode, historyQuery);
    } catch (err) {
      setAuditMessage("AI ??刻麾?都赯?Word ???????剜??: " + err.message);
    } finally {
      setAuditExportBusy(false);
    }
  }

  async function runDocumentCompare() {
    if (!compareLeftPath || !compareRightPath) {
      setCompareMessage("?ｇ???鞊????????刻麾??);
      return;
    }
    setCompareBusy(true);
    setCompareMessage("");
    try {
      const payload = await callV2("/documents/compare", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ left_path: compareLeftPath, right_path: compareRightPath, use_llm: compareUseLlm }),
      });
      setCompareResult(payload.data);
      setCompareMessage("??刻麾???芰???堆???);
      loadHistory(historyMode, historyQuery);
    } catch (err) {
      setCompareMessage("??刻麾???芰???剜??: " + err.message);
    } finally {
      setCompareBusy(false);
    }
  }

  async function loadVersionCandidates() {
    if (!compareLeftPath) {
      setCompareMessage("?ｇ???鞊??蝞???刻麾??);
      return;
    }
    setVersionCandidatesBusy(true);
    setCompareMessage("");
    try {
      const payload = await callV2("/documents/version-candidates", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: compareLeftPath, limit: 12 }),
      });
      const candidates = payload.data?.candidates || [];
      setVersionCandidates(candidates);
      if (candidates[0]?.path) {
        setCompareRightPath(candidates[0].path);
      }
      setCompareMessage(candidates.length ? "???鈭???刻麾??暑?謕??? : "???????輯?????????謕???);
    } catch (err) {
      setCompareMessage("??暑?謕??謚??剜??: " + err.message);
    } finally {
      setVersionCandidatesBusy(false);
    }
  }

  async function exportDocumentCompareReport() {
    if (!compareLeftPath || !compareRightPath) {
      setCompareMessage("?ｇ???鞊????????刻麾??);
      return;
    }
    setCompareExportBusy(true);
    setCompareMessage("");
    try {
      const response = await fetch(apiBase + "/documents/compare/export", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ left_path: compareLeftPath, right_path: compareRightPath, use_llm: compareUseLlm }),
      });
      if (!response.ok) {
        let payload = null;
        try {
          payload = await response.json();
        } catch (err) {
          payload = null;
        }
        throw new Error(payload?.message || ("HTTP " + response.status));
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "document_compare_report.xlsx";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      setCompareMessage("?餌捂??伍???????????);
      loadHistory(historyMode, historyQuery);
    } catch (err) {
      setCompareMessage("?餌捂??伍?????????剜??: " + err.message);
    } finally {
      setCompareExportBusy(false);
    }
  }

  async function exportDocumentCompareWordReport() {
    if (!compareLeftPath || !compareRightPath) {
      setCompareMessage("?ｇ???鞊????????刻麾??);
      return;
    }
    setCompareDocxExportBusy(true);
    setCompareMessage("");
    try {
      const response = await fetch(apiBase + "/documents/compare/export/docx", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ left_path: compareLeftPath, right_path: compareRightPath, use_llm: compareUseLlm }),
      });
      if (!response.ok) {
        let payload = null;
        try {
          payload = await response.json();
        } catch (err) {
          payload = null;
        }
        throw new Error(payload?.message || ("HTTP " + response.status));
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "document_compare_report.docx";
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      setCompareMessage("Word ?伍???????????);
      loadHistory(historyMode, historyQuery);
    } catch (err) {
      setCompareMessage("Word ?伍?????????剜??: " + err.message);
    } finally {
      setCompareDocxExportBusy(false);
    }
  }

  async function ingestPaths(paths) {
    if (!paths.length) {
      setIngestMessage("?獢??????穿??鈭???刻麾??);
      return;
    }
    setIngestBusy(true);
    setIngestMessage("");
    try {
      const payload = await callV2("/documents/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          paths,
          metadata: paths.reduce((acc, path) => {
            acc[path] = sourceMetadata[path] || {};
            return acc;
          }, {}),
        }),
      });
      setIngestResult(payload.data);
      setIngestMessage(`????${payload.data.ingested_count} ?都?????隡??剜?? ${payload.data.failed_count || 0} ?閉?蹐?;
      const healthPayload = await callV2("/health");
      setServiceInfo(healthPayload.data || {});
      const cachePayload = await callV2("/cache/status");
      setCacheStatus(cachePayload.data || {});
    } catch (err) {
      setIngestMessage("?撖暑??穿?剜??: " + err.message);
    } finally {
      setIngestBusy(false);
    }
  }

  async function clearRuntimeCache(target) {
    setCacheBusy(true);
    setServiceMessage("");
    try {
      const payload = await callV2("/cache/clear?target=" + encodeURIComponent(target), { method: "POST" });
      const cachePayload = await callV2("/cache/status");
      setCacheStatus(cachePayload.data || {});
      setCompareResult(prev => prev ? { ...prev, cache_hit: false } : prev);
      setAuditResult(prev => prev ? { ...prev, cache_hit: false } : prev);
      setServiceMessage(`????${payload.data.deleted_compare_cache || 0} ????????蝧?謘甄?{payload.data.deleted_audit_cache || 0} ??????閰函膩?謘甄蹐?;
    } catch (err) {
      setServiceMessage("?寞????剜??: " + err.message);
    } finally {
      setCacheBusy(false);
    }
  }

  async function loadHistory(mode = historyMode, query = historyQuery) {
    setHistoryBusy(true);
    setHistoryMessage("");
    try {
      const payload = await callV2("/history/runs?mode=" + encodeURIComponent(mode) + "&q=" + encodeURIComponent(query.trim()) + "&limit=20");
      setHistoryItems(payload.data?.items || []);
      setHistoryMessage((payload.data?.items || []).length ? "???鈭??謚恍◢??純? : "?獢??鈭佗??????颲??◢??????);
    } catch (err) {
      setHistoryMessage("?荒?????暸???謘潔??? " + err.message);
    } finally {
      setHistoryBusy(false);
    }
  }

  async function runSearch() {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }
    setSearchBusy(true);
    setServiceMessage("");
    try {
      const payload = await callV2("/documents/search?q=" + encodeURIComponent(searchQuery.trim()) + "&limit=8");
      setSearchResults(payload.data?.hits || []);
    } catch (err) {
      setServiceMessage("??刻麾?謚??剜??: " + err.message);
    } finally {
      setSearchBusy(false);
    }
  }

  async function runKnowledgeQA() {
    if (!qaQuestion.trim()) {
      setQaMessage("?ｇ???岳??????);
      return;
    }
    setQaBusy(true);
    setQaMessage("");
    try {
      const qaPayload = { question: qaQuestion.trim(), limit: 5 };
      if (qaScope === "selected" && selectedPath) {
        qaPayload.path = selectedPath;
      }
      const payload = await callV2("/knowledge/qa", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(qaPayload),
      });
      setQaResult(payload.data);
      setQaMessage("??刻麾?鈭?????堆???);
    } catch (err) {
      setQaMessage("??刻麾?鈭?????剜??: " + err.message);
    } finally {
      setQaBusy(false);
    }
  }

  async function runSpcAnalyze() {
    setSpcBusy(true);
    setSpcMessage("");
    try {
      const payload = await callV2("/spc/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          parameter_name: spcForm.parameter_name,
          csv_text: spcForm.csv_text,
          lsl: spcForm.lsl === "" ? null : Number(spcForm.lsl),
          usl: spcForm.usl === "" ? null : Number(spcForm.usl),
          target: spcForm.target === "" ? null : Number(spcForm.target),
        }),
      });
      setSpcResult(payload.data);
      setSpcMessage("SPC ?謢??堆???);
    } catch (err) {
      setSpcMessage("SPC ?謢??剜??: " + err.message);
    } finally {
      setSpcBusy(false);
    }
  }

  async function runDeviationDraft() {
    setDeviationBusy(true);
    setDeviationMessage("");
    try {
      const payload = await callV2("/deviations/draft", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(deviationForm),
      });
      setDeviationResult(payload.data);
      setDeviationMessage("??????仿?堆???);
    } catch (err) {
      setDeviationMessage("??????仿?剜??: " + err.message);
    } finally {
      setDeviationBusy(false);
    }
  }

  return (
    <div>
      <PageIntro
        eyebrow="??肅?AI ??刻麾???"
        title="AI ?鼎??????肅?V2??
        description="?謕??蹓??????餈斗????? AI ????垮????閰鄞蹓???????蹓踐??朱????蹍C ?謢???恃?????葩?蹇??舀??????輯撒??????餈斗???????荒?.xlsx???遴鬥???????
      >
        <div style={{ display:"flex", gap:12, flexWrap:"wrap" }}>
          <StatCard label="??刻麾???" value={sources.length} color="#38bdf8" sub={masterSourceInfo.mode === "master" ? "???????餈斗???????荒?" : "????輯撒???寥?謕??謘?} />
          <StatCard label="???冽亥??? value={serviceInfo.database_mode || "unknown"} color={serviceInfo.database_mode === "postgresql" ? "#22c55e" : "#f59e0b"} sub={(serviceInfo.database_status && serviceInfo.database_status.using_fallback) ? "?????SQLite" : "??????冽??鈭?"} />
          <StatCard label="LLM ???? value={serviceInfo.openrouter_enabled ? "???? : "?????} color={serviceInfo.openrouter_enabled ? "#22c55e" : "#64748b"} sub="?秋?????????????" />
        </div>
        <div style={{ marginTop:14, fontSize:12, color:"#cbd5e1", lineHeight:1.8 }}>
          {masterSourceInfo.mode === "master"
            ? `????獢????${masterSourceInfo.source_path || "?????}??謆????${masterSourceInfo.count || sources.length} ?都?????綽??鈭色??${masterSourceInfo.pending_review_count || 0} ?閉?蹐?
            : (masterSourceInfo.message || "?垮謓舫?????肅?餈斗???????荒???)}
        </div>
      </PageIntro>

      <Panel
        title="???????????□?"
        description="????V2 ????蹓??謕???拍膩?謘???蹇??秋撮?????????鈭?????謘???膩?謘???????
        accent="#38bdf8"
        style={{ marginBottom: 18 }}
      >
        <div style={{ display:"grid", gridTemplateColumns:"1.2fr 0.8fr", gap:12, alignItems:"end" }}>
          <div>
            <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>V2 API Base URL</div>
            <input value={apiBase} onChange={e => setApiBase(e.target.value.trim())} style={inputStyle} />
          </div>
          <button onClick={runSearch} disabled={searchBusy} style={buttonStyle("primary", searchBusy)}>{searchBusy ? "?謚???.." : "??撗??刻麾?謚?"}</button>
        </div>
        <div style={{ marginTop:10, fontSize:12, color: serviceMessage ? "#fca5a5" : "#7dd3fc" }}>
          {serviceMessage || "V2 ????鈭??潘撓貔??恃??綜姿???澈?輯撒??http://127.0.0.1:8890/api/v2??}
        </div>
        {serviceInfo.database_status && (
          <div style={{ marginTop:8, fontSize:12, color:"#cbd5e1", lineHeight:1.7 }}>
            ?獢????冽?{serviceInfo.database_status.active_database_url || "unknown"}
            {serviceInfo.database_status.using_fallback && serviceInfo.database_status.fallback_reason ? "??ostgreSQL ?賹??剜?????蹎?" + serviceInfo.database_status.fallback_reason : ""}
          </div>
        )}
        <div style={{ marginTop:10, display:"flex", gap:8, flexWrap:"wrap" }}>
          <Badge color="#14b8a6">?伍???寞? {cacheStatus.compare_cache_count || 0}</Badge>
          <Badge color="#38bdf8">?都赯望?? {cacheStatus.audit_cache_count || 0}</Badge>
          {cacheStatus.latest_compare_cache_at && <Badge color="#64748b">?伍???寞??皝? {cacheStatus.latest_compare_cache_at.slice(0, 19).replace("T", " ")}</Badge>}
          {cacheStatus.latest_audit_cache_at && <Badge color="#64748b">?都赯望???皝? {cacheStatus.latest_audit_cache_at.slice(0, 19).replace("T", " ")}</Badge>}
        </div>
        <div style={{ display:"flex", gap:10, flexWrap:"wrap", marginTop:12 }}>
          <button onClick={() => ingestPaths(sources.map(item => item.path))} disabled={ingestBusy || sources.length === 0} style={buttonStyle("success", ingestBusy || sources.length === 0)}>{ingestBusy ? "??穿??.." : (masterSourceInfo.mode === "master" ? "??穿??肅????荒???賂??刻麾" : "??穿??賂?ISO ??刻麾")}</button>
          <button onClick={() => ingestPaths(selectedPath ? [selectedPath] : [])} disabled={ingestBusy || !selectedPath} style={buttonStyle("secondary", ingestBusy || !selectedPath)}>??賂??鈭佇?????????/button>
          <button onClick={() => clearRuntimeCache("all")} disabled={cacheBusy} style={buttonStyle("danger", cacheBusy)}>{cacheBusy ? "????.." : "?謒??賂豢??"}</button>
          <button onClick={() => clearRuntimeCache("compare")} disabled={cacheBusy} style={buttonStyle("warning", cacheBusy)}>????伍???寞?</button>
          <button onClick={() => clearRuntimeCache("audit")} disabled={cacheBusy} style={buttonStyle("secondary", cacheBusy)}>????都赯望??</button>
          {ingestMessage && <div style={{ fontSize:12, color:"#99f6e4", alignSelf:"center" }}>{ingestMessage}</div>}
        </div>
        {ingestResult && (
          <div style={{ marginTop:12, display:"flex", flexDirection:"column", gap:10 }}>
            <div style={{ fontSize:12, color:"#cbd5e1", lineHeight:1.7 }}>
              ?????皝? {ingestResult.ingested_count} ?都?????剜?? {ingestResult.failed_count || 0} ?????擗????隞???蹌?{ingestResult.documents?.[0]?.title || "n/a"}??
            </div>
            {(ingestResult.documents || []).slice(0, 5).map(item => {
              const parserBadge = getParserBadge(item.parser_name);
              const layoutBadge = getLayoutBadge(item);
              return (
                <div key={item.document_id || item.source_path} style={{ background:"rgba(255,255,255,0.03)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:10, padding:"10px 12px" }}>
                  <div style={{ display:"flex", justifyContent:"space-between", gap:10, flexWrap:"wrap", alignItems:"center" }}>
                    <div>
                      <div style={{ fontSize:12, color:"#e2e8f0", fontWeight:700 }}>{item.title}</div>
                      <div style={{ fontSize:11, color:"#94a3b8", marginTop:4 }}>{item.source_path}</div>
                    </div>
                    <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
                      {parserBadge && <Badge color={parserBadge.color}>{parserBadge.label}</Badge>}
                      {layoutBadge && <Badge color={layoutBadge.color}>{layoutBadge.label}</Badge>}
                    </div>
                  </div>
                  {item.parser_note && <div style={{ marginTop:8, fontSize:11, color:"#cbd5e1", lineHeight:1.6 }}>{item.parser_note}</div>}
                </div>
              );
            })}
            {(ingestResult.documents || []).length > 5 && (
              <div style={{ fontSize:11, color:"#94a3b8" }}>??? {(ingestResult.documents || []).length - 5} ?都???甇??穿???嚗??輯????5 ?閉??/div>
            )}
          </div>
        )}
      </Panel>

      <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(320px, 1fr))", gap:16 }}>
        <div style={{ background:"rgba(255,255,255,0.04)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:14, padding:18 }}>
          <div style={{ fontSize:15, fontWeight:700, color:"#e2e8f0", marginBottom:12 }}>AI ??刻麾?都赯?/div>
          <div style={{ fontSize:12, color:"#94a3b8", marginBottom:10 }}>????輯????肅?餈斗???????荒??????刻麾???皝??蹓鳴 V2 ?秋??都赯??/div>
          <select value={selectedPath} onChange={e => setSelectedPath(e.target.value)} style={inputStyle}>
            {sources.map(item => (
              <option key={item.id + item.path} value={item.path}>{item.id}?砭item.name}{item.review_status ? `??{item.review_status}` : ""}</option>
            ))}
          </select>
          <div style={{ display:"flex", gap:10, marginTop:12, flexWrap:"wrap" }}>
            <button onClick={runDocumentAudit} disabled={auditBusy || !selectedPath} style={{ background:"linear-gradient(135deg,#2563eb,#38bdf8)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"10px 16px", fontSize:13, fontWeight:700, opacity:(auditBusy || !selectedPath) ? 0.6 : 1 }}>{auditBusy ? "?都赯梢??.." : "?????刻麾?都赯?}</button>
            <button onClick={exportDocumentAuditWordReport} disabled={auditExportBusy || !selectedPath} style={{ background:"rgba(255,255,255,0.06)", border:"1px solid rgba(255,255,255,0.14)", borderRadius:10, color:"#e2e8f0", cursor:"pointer", padding:"10px 16px", fontSize:13, fontWeight:700, opacity:(auditExportBusy || !selectedPath) ? 0.6 : 1 }}>{auditExportBusy ? "??穿??.." : "????都赯?Word ???"}</button>
          </div>
          {auditMessage && <div style={{ marginTop:10, fontSize:12, color:"#bae6fd" }}>{auditMessage}</div>}
          {auditResult && (
            <div style={{ marginTop:14, display:"flex", flexDirection:"column", gap:10 }}>
              <div style={{ fontSize:13, color:"#e2e8f0", lineHeight:1.7 }}>{auditResult.summary}</div>
              <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
                <Badge color="#60a5fa">prompt {auditResult.prompt_version}</Badge>
                <Badge color={auditResult.needs_human_review ? "#f59e0b" : "#22c55e"}>{auditResult.needs_human_review ? "???剔?璆菟?僚" : "????鈭止???}</Badge>
                {typeof auditResult.cache_hit === "boolean" && <Badge color={auditResult.cache_hit ? "#14b8a6" : "#64748b"}>{auditResult.cache_hit ? "?鞈剛??寞?" : "????殷??"}</Badge>}
                {getParserBadge(auditResult.parser_name) && <Badge color={getParserBadge(auditResult.parser_name).color}>{getParserBadge(auditResult.parser_name).label}</Badge>}
                {getLayoutBadge(auditResult) && <Badge color={getLayoutBadge(auditResult).color}>{getLayoutBadge(auditResult).label}</Badge>}
              </div>
              {auditResult.parser_note && (
                <div style={{ fontSize:12, color:"#cbd5e1", lineHeight:1.7, background:"rgba(255,255,255,0.03)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:10, padding:"10px 12px" }}>
                  ????方??爸auditResult.parser_note}
                </div>
              )}
              <div>
                <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>????謘?/div>
                <div style={{ display:"flex", flexDirection:"column", gap:8 }}>
                  {(auditResult.issues || []).map(item => (
                    <div key={item.code} style={{ background:"rgba(239,68,68,0.08)", border:"1px solid rgba(239,68,68,0.18)", borderRadius:10, padding:"10px 12px" }}>
                      <div style={{ display:"flex", gap:8, flexWrap:"wrap", marginBottom:4 }}>
                        <Badge color={item.severity === "high" ? "#ef4444" : "#f59e0b"}>{item.severity}</Badge>
                        <span style={{ fontSize:13, color:"#fecaca", fontWeight:700 }}>{item.title}</span>
                      </div>
                      <div style={{ fontSize:12, color:"#fca5a5" }}>{item.description}</div>
                    </div>
                  ))}
                  {(!auditResult.issues || auditResult.issues.length === 0) && <div style={{ fontSize:12, color:"#4ade80" }}>?獢??秋??潘撓貔??堊赤????秋播??倦?餌捂???/div>}
                </div>
              </div>
              <div>
                <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>????芣</div>
                <div style={{ display:"flex", flexDirection:"column", gap:8 }}>
                  {(auditResult.citations || []).map((item, idx) => (
                    <div key={idx} style={{ background:"rgba(255,255,255,0.03)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:10, padding:"10px 12px" }}>
                      <div style={{ fontSize:12, color:"#7dd3fc", marginBottom:4 }}>{item.title}</div>
                      <div style={{ fontSize:11, color:"#94a3b8", marginBottom:4 }}>{item.source_path}</div>
                      {(item.page_no || item.section_name) && (
                        <div style={{ fontSize:11, color:"#cbd5e1", marginBottom:4 }}>
                          {item.page_no ? `?蹓賤??{item.page_no}` : "?蹓賤?垮謓舐?謕"}
                          {item.section_name ? ` ???????${item.section_name}` : ""}
                        </div>
                      )}
                      <div style={{ fontSize:12, color:"#cbd5e1", lineHeight:1.6 }}>{item.preview}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        <div style={{ background:"rgba(255,255,255,0.04)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:14, padding:18 }}>
          <div style={{ fontSize:15, fontWeight:700, color:"#e2e8f0", marginBottom:12 }}>??刻麾???芰??</div>
          <div style={{ fontSize:12, color:"#94a3b8", marginBottom:10 }}>?伍????????謘踱?獢???秧????蹓賣?????????等???/div>
          <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:10, padding:"10px 12px", background:"rgba(255,255,255,0.03)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:10 }}>
            <input id="compare-llm-toggle" type="checkbox" checked={compareUseLlm} onChange={e => setCompareUseLlm(e.target.checked)} />
            <label htmlFor="compare-llm-toggle" style={{ fontSize:12, color:"#cbd5e1", cursor:"pointer" }}>?賹? LLM ?謢?</label>
            <span style={{ fontSize:11, color:"#94a3b8" }}>??澈?謚??蹇????????秋?????殉?璁????伍???寞?/span>
          </div>
          <div style={{ display:"flex", gap:8, flexWrap:"wrap", marginBottom:10 }}>
            <button onClick={() => setCompareMode("generic")} style={{ background:compareMode === "generic" ? "rgba(29,78,216,0.22)" : "rgba(255,255,255,0.04)", border:"1px solid " + (compareMode === "generic" ? "rgba(29,78,216,0.45)" : "rgba(255,255,255,0.1)"), borderRadius:999, color:compareMode === "generic" ? "#bfdbfe" : "#94a3b8", cursor:"pointer", padding:"6px 12px", fontSize:12, fontWeight:700 }}>??蟡???/button>
            <button onClick={() => setCompareMode("version")} style={{ background:compareMode === "version" ? "rgba(124,58,237,0.22)" : "rgba(255,255,255,0.04)", border:"1px solid " + (compareMode === "version" ? "rgba(124,58,237,0.45)" : "rgba(255,255,255,0.1)"), borderRadius:999, color:compareMode === "version" ? "#ddd6fe" : "#94a3b8", cursor:"pointer", padding:"6px 12px", fontSize:12, fontWeight:700 }}>??????????/button>
          </div>
          {compareMode === "generic" ? (
            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:10 }}>
              <div>
                <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>??蹓??刻麾</div>
                <select value={compareLeftPath} onChange={e => setCompareLeftPath(e.target.value)} style={inputStyle}>
                  {sources.map(item => (
                    <option key={"left-" + item.id + item.path} value={item.path}>{item.id}?砭item.name}{item.review_status ? "?? + item.review_status : ""}</option>
                  ))}
                </select>
              </div>
              <div>
                <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>??啾???刻麾</div>
                <select value={compareRightPath} onChange={e => setCompareRightPath(e.target.value)} style={inputStyle}>
                  {sources.map(item => (
                    <option key={"right-" + item.id + item.path} value={item.path}>{item.id}?砭item.name}{item.review_status ? "?? + item.review_status : ""}</option>
                  ))}
                </select>
              </div>
            </div>
          ) : (
            <div style={{ display:"grid", gap:10 }}>
              <div>
                <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>?蝞???刻麾</div>
                <select value={compareLeftPath} onChange={e => setCompareLeftPath(e.target.value)} style={inputStyle}>
                  {sources.map(item => (
                    <option key={"base-" + item.id + item.path} value={item.path}>{item.id}?砭item.name}{item.review_status ? "?? + item.review_status : ""}</option>
                  ))}
                </select>
              </div>
              <div style={{ display:"flex", gap:10, flexWrap:"wrap" }}>
                <button onClick={loadVersionCandidates} disabled={versionCandidatesBusy || !compareLeftPath} style={{ background:"rgba(255,255,255,0.06)", border:"1px solid rgba(255,255,255,0.14)", borderRadius:10, color:"#e2e8f0", cursor:"pointer", padding:"10px 16px", fontSize:13, fontWeight:700, opacity:(versionCandidatesBusy || !compareLeftPath) ? 0.6 : 1 }}>{versionCandidatesBusy ? "?謚???.." : "??????????}</button>
                {versionCandidates.length > 0 && <div style={{ fontSize:12, color:"#cbd5e1", alignSelf:"center" }}>????{versionCandidates.length} ??謕???秧</div>}
              </div>
              <div>
                <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>?謕???暑</div>
                <select value={compareRightPath} onChange={e => setCompareRightPath(e.target.value)} style={inputStyle}>
                  <option value="">?ｇ蹓??怏謕???秧</option>
                  {versionCandidates.map(item => (
                    <option key={"candidate-" + item.path} value={item.path}>{item.title}{item.version_label ? "?鬲???" + item.version_label : ""}{item.extension ? "?? + item.extension : ""}</option>
                  ))}
                </select>
              </div>
            </div>
          )}
          <div style={{ display:"flex", gap:10, flexWrap:"wrap", marginTop:12 }}>
            <button onClick={runDocumentCompare} disabled={compareBusy || !compareLeftPath || !compareRightPath} style={{ background:"linear-gradient(135deg,#1d4ed8,#7c3aed)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"10px 16px", fontSize:13, fontWeight:700, opacity:(compareBusy || !compareLeftPath || !compareRightPath) ? 0.6 : 1 }}>{compareBusy ? "?伍????.." : "?????刻麾?伍??"}</button>
            <button onClick={exportDocumentCompareReport} disabled={compareExportBusy || !compareLeftPath || !compareRightPath} style={{ background:"rgba(255,255,255,0.06)", border:"1px solid rgba(255,255,255,0.14)", borderRadius:10, color:"#e2e8f0", cursor:"pointer", padding:"10px 16px", fontSize:13, fontWeight:700, opacity:(compareExportBusy || !compareLeftPath || !compareRightPath) ? 0.6 : 1 }}>{compareExportBusy ? "??穿??.." : "????餌捂??伍?????"}</button>
            <button onClick={exportDocumentCompareWordReport} disabled={compareDocxExportBusy || !compareLeftPath || !compareRightPath} style={{ background:"rgba(255,255,255,0.06)", border:"1px solid rgba(255,255,255,0.14)", borderRadius:10, color:"#e2e8f0", cursor:"pointer", padding:"10px 16px", fontSize:13, fontWeight:700, opacity:(compareDocxExportBusy || !compareLeftPath || !compareRightPath) ? 0.6 : 1 }}>{compareDocxExportBusy ? "??穿??.." : "??? Word ?伍?????"}</button>
          </div>
          {compareMessage && <div style={{ marginTop:10, fontSize:12, color:"#c4b5fd" }}>{compareMessage}</div>}
          {compareResult && (
            <div style={{ marginTop:14, display:"grid", gap:10 }}>
              {compareResult.version_change_conclusion && (
                <div style={{ background:"rgba(59,130,246,0.08)", border:"1px solid rgba(59,130,246,0.18)", borderRadius:10, padding:"10px 12px" }}>
                  <div style={{ fontSize:12, color:"#93c5fd", fontWeight:700, marginBottom:6 }}>??暑?荒??</div>
                  <div style={{ fontSize:12, color:"#dbeafe", lineHeight:1.7 }}>{compareResult.version_change_conclusion}</div>
                  {compareResult.version_change_recommendation && <div style={{ marginTop:6, fontSize:12, color:"#bfdbfe" }}>{compareResult.version_change_recommendation}</div>}
                </div>
              )}
              <div style={{ fontSize:12, color:"#e9d5ff", lineHeight:1.8, whiteSpace:"pre-wrap" }}>{compareResult.summary}</div>
              <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
                <Badge color="#7c3aed">?閮暹??{compareResult.similarity}</Badge>
                <Badge color="#60a5fa">prompt {compareResult.prompt_version}</Badge>
                {typeof compareResult.same_document_family === "boolean" && <Badge color={compareResult.same_document_family ? "#22c55e" : "#f59e0b"}>{compareResult.same_document_family ? "??????? : "??芣?????刻麾"}</Badge>}
                {typeof compareResult.cache_hit === "boolean" && <Badge color={compareResult.cache_hit ? "#14b8a6" : "#64748b"}>{compareResult.cache_hit ? "?鞈剛??寞?" : "????殷??"}</Badge>}
              </div>
              <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:10 }}>
                <div style={{ background:"rgba(245,158,11,0.08)", border:"1px solid rgba(245,158,11,0.18)", borderRadius:10, padding:"10px 12px" }}>
                  <div style={{ fontSize:12, color:"#fcd34d", fontWeight:700, marginBottom:6 }}>??啾??????寞?</div>
                  {(compareResult.added_lines || []).slice(0, 6).map((item, idx) => (
                    <div key={idx} style={{ fontSize:12, color:"#fde68a", lineHeight:1.6 }}>+ {item}</div>
                  ))}
                  {(!compareResult.added_lines || compareResult.added_lines.length === 0) && <div style={{ fontSize:12, color:"#94a3b8" }}>??賃????????????寞???/div>}
                </div>
                <div style={{ background:"rgba(239,68,68,0.08)", border:"1px solid rgba(239,68,68,0.18)", borderRadius:10, padding:"10px 12px" }}>
                  <div style={{ fontSize:12, color:"#fca5a5", fontWeight:700, marginBottom:6 }}>??蹓?擏???寞?</div>
                  {(compareResult.removed_lines || []).slice(0, 6).map((item, idx) => (
                    <div key={idx} style={{ fontSize:12, color:"#fecaca", lineHeight:1.6 }}>- {item}</div>
                  ))}
                  {(!compareResult.removed_lines || compareResult.removed_lines.length === 0) && <div style={{ fontSize:12, color:"#94a3b8" }}>??賃?????????謒??寞???/div>}
                </div>
              </div>
              <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:10 }}>
                <div style={{ background:"rgba(255,255,255,0.03)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:10, padding:"10px 12px" }}>
                  <div style={{ fontSize:12, color:"#e2e8f0", fontWeight:700, marginBottom:6 }}>??舀什?皜?????秋??餌???/div>
                  {(compareResult.left_only_issues || []).map(item => (
                    <div key={item.code} style={{ fontSize:12, color:"#cbd5e1", lineHeight:1.6 }}>- {item.title}</div>
                  ))}
                  {(!compareResult.left_only_issues || compareResult.left_only_issues.length === 0) && <div style={{ fontSize:12, color:"#94a3b8" }}>?嚚?/div>}
                </div>
                <div style={{ background:"rgba(255,255,255,0.03)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:10, padding:"10px 12px" }}>
                  <div style={{ fontSize:12, color:"#e2e8f0", fontWeight:700, marginBottom:6 }}>??荒?皜?????秋??餌???/div>
                  {(compareResult.right_only_issues || []).map(item => (
                    <div key={item.code} style={{ fontSize:12, color:"#cbd5e1", lineHeight:1.6 }}>- {item.title}</div>
                  ))}
                  {(!compareResult.right_only_issues || compareResult.right_only_issues.length === 0) && <div style={{ fontSize:12, color:"#94a3b8" }}>?嚚?/div>}
                </div>
              </div>
            </div>
          )}
        </div>

        <div style={{ background:"rgba(255,255,255,0.04)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:14, padding:18 }}>
          <div style={{ fontSize:15, fontWeight:700, color:"#e2e8f0", marginBottom:12 }}>?荒???????軋???/div>
          <div style={{ fontSize:12, color:"#94a3b8", marginBottom:10 }}>?鈭亙眺擗???刻麾?都赯?蹓????????????穿????荒???謘?頛??鞎?擗釭擐??/div>
          <div style={{ display:"grid", gridTemplateColumns:"0.7fr 1.3fr auto", gap:10, alignItems:"end" }}>
            <div>
              <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>?遴竣?</div>
              <select value={historyMode} onChange={e => setHistoryMode(e.target.value)} style={inputStyle}>
                <option value="all">??賂?/option>
                <option value="audit">??刻麾?都赯?/option>
                <option value="compare">??刻麾?伍??</option>
                <option value="export">?????穿</option>
              </select>
            </div>
            <div>
              <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>?謚殷??/div>
              <input value={historyQuery} onChange={e => setHistoryQuery(e.target.value)} placeholder="?????task type?蹍禿ompt version?蹍河quest ?謢?" style={inputStyle} />
            </div>
            <button onClick={() => loadHistory()} disabled={historyBusy} style={{ background:"linear-gradient(135deg,#475569,#0f172a)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"10px 16px", fontSize:13, fontWeight:700, opacity: historyBusy ? 0.6 : 1 }}>{historyBusy ? "??舫??.." : "?鈭亙眺????}</button>
          </div>
          {historyMessage && <div style={{ marginTop:10, fontSize:12, color:"#cbd5e1" }}>{historyMessage}</div>}
          <div style={{ marginTop:12, display:"flex", flexDirection:"column", gap:8 }}>
            {historyItems.map(item => (
              <div key={item.id} style={{ background:"rgba(255,255,255,0.03)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:10, padding:"10px 12px" }}>
                <div style={{ display:"flex", justifyContent:"space-between", gap:12, flexWrap:"wrap", marginBottom:6 }}>
                  <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
                    <Badge color="#38bdf8">{item.task_type}</Badge>
                    <Badge color={item.result_status === "success" ? "#22c55e" : "#ef4444"}>{item.result_status}</Badge>
                    {item.prompt_version && <Badge color="#a78bfa">{item.prompt_version}</Badge>}
                  </div>
                  <div style={{ fontSize:11, color:"#94a3b8" }}>{item.created_at ? item.created_at.slice(0, 19).replace("T", " ") : ""}</div>
                </div>
                <div style={{ fontSize:12, color:"#cbd5e1", lineHeight:1.6, whiteSpace:"pre-wrap" }}>{item.request_summary || "??request ?謢?"}</div>
              </div>
            ))}
            {historyItems.length === 0 && <div style={{ fontSize:12, color:"#64748b" }}>?獢??垓???恬??瑞?????曇?????/div>}
          </div>
        </div>

        <div style={{ background:"rgba(255,255,255,0.04)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:14, padding:18 }}>
          <div style={{ fontSize:15, fontWeight:700, color:"#e2e8f0", marginBottom:12 }}>SPC ?謢?</div>
          <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:10 }}>
            <div style={{ gridColumn:"1 / -1" }}>
              <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>??塗???</div>
              <input value={spcForm.parameter_name} onChange={e => setSpcForm(prev => ({ ...prev, parameter_name: e.target.value }))} style={inputStyle} />
            </div>
            <div style={{ gridColumn:"1 / -1" }}>
              <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>?閰阬瞏???/div>
              <textarea value={spcForm.csv_text} onChange={e => setSpcForm(prev => ({ ...prev, csv_text: e.target.value }))} style={{ ...inputStyle, minHeight:84, resize:"vertical" }} />
            </div>
            <div>
              <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>LSL</div>
              <input value={spcForm.lsl} onChange={e => setSpcForm(prev => ({ ...prev, lsl: e.target.value }))} style={inputStyle} />
            </div>
            <div>
              <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>USL</div>
              <input value={spcForm.usl} onChange={e => setSpcForm(prev => ({ ...prev, usl: e.target.value }))} style={inputStyle} />
            </div>
            <div>
              <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>Target</div>
              <input value={spcForm.target} onChange={e => setSpcForm(prev => ({ ...prev, target: e.target.value }))} style={inputStyle} />
            </div>
          </div>
          <button onClick={runSpcAnalyze} disabled={spcBusy} style={{ marginTop:12, background:"linear-gradient(135deg,#0f766e,#14b8a6)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"10px 16px", fontSize:13, fontWeight:700, opacity: spcBusy ? 0.6 : 1 }}>{spcBusy ? "?????.." : "?嚗? SPC ?謢?"}</button>
          {spcMessage && <div style={{ marginTop:10, fontSize:12, color:"#99f6e4" }}>{spcMessage}</div>}
          {spcResult && (
            <div style={{ marginTop:14, display:"flex", flexDirection:"column", gap:10 }}>
              <div style={{ display:"grid", gridTemplateColumns:"repeat(3, minmax(0, 1fr))", gap:8 }}>
                {[
                  ["????, spcResult.metrics.mean],
                  ["?????, spcResult.metrics.stdev],
                  ["Cpk", spcResult.metrics.cpk ?? "n/a"],
                  ["Cp", spcResult.metrics.cp ?? "n/a"],
                  ["??????, spcResult.metrics.out_of_spec_count],
                  ["???, spcResult.metrics.trend],
                ].map(([label, value]) => (
                  <div key={label} style={{ background:"rgba(20,184,166,0.08)", border:"1px solid rgba(20,184,166,0.16)", borderRadius:10, padding:"10px 12px" }}>
                    <div style={{ fontSize:11, color:"#99f6e4" }}>{label}</div>
                    <div style={{ fontSize:14, color:"#e2e8f0", fontWeight:700, marginTop:4 }}>{value}</div>
                  </div>
                ))}
              </div>
              <div style={{ fontSize:12, color:"#cbd5e1", lineHeight:1.7 }}>{spcResult.engineering_summary}</div>
              <div style={{ fontSize:12, color:"#fef3c7", lineHeight:1.7 }}>{spcResult.management_summary}</div>
            </div>
          )}
        </div>

        <div style={{ background:"rgba(255,255,255,0.04)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:14, padding:18 }}>
          <div style={{ fontSize:15, fontWeight:700, color:"#e2e8f0", marginBottom:12 }}>??刻麾?鈭????</div>
          <div style={{ fontSize:12, color:"#94a3b8", marginBottom:10 }}>???僕?謍唳???穿??????曇????????謕????????/div>
          <div style={{ display:"flex", gap:8, flexWrap:"wrap", marginBottom:10 }}>
            <button onClick={() => setQaScope("selected")} style={{ background:qaScope === "selected" ? "rgba(124,58,237,0.22)" : "rgba(255,255,255,0.04)", border:"1px solid " + (qaScope === "selected" ? "rgba(124,58,237,0.45)" : "rgba(255,255,255,0.1)"), borderRadius:999, color:qaScope === "selected" ? "#ddd6fe" : "#94a3b8", cursor:"pointer", padding:"6px 12px", fontSize:12, fontWeight:700 }}>????獢???刻麾</button>
            <button onClick={() => setQaScope("all")} style={{ background:qaScope === "all" ? "rgba(124,58,237,0.22)" : "rgba(255,255,255,0.04)", border:"1px solid " + (qaScope === "all" ? "rgba(124,58,237,0.45)" : "rgba(255,255,255,0.1)"), borderRadius:999, color:qaScope === "all" ? "#ddd6fe" : "#94a3b8", cursor:"pointer", padding:"6px 12px", fontSize:12, fontWeight:700 }}>?謚???賂??刻麾</button>
          </div>
          {qaScope === "selected" && (
            <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:10 }}>
              ?獢??????刻麾??span style={{ color:"#e9d5ff" }}>{sources.find(item => item.path === selectedPath)?.name || "??畸???}</span>
            </div>
          )}
          <textarea value={qaQuestion} onChange={e => setQaQuestion(e.target.value)} style={{ ...inputStyle, minHeight:92, resize:"vertical" }} />
          <button onClick={runKnowledgeQA} disabled={qaBusy} style={{ marginTop:12, background:"linear-gradient(135deg,#7c3aed,#a855f7)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"10px 16px", fontSize:13, fontWeight:700, opacity: qaBusy ? 0.6 : 1 }}>{qaBusy ? "?豯???.." : "?????刻麾???"}</button>
          {qaMessage && <div style={{ marginTop:10, fontSize:12, color:"#ddd6fe" }}>{qaMessage}</div>}
          {qaResult && (
            <div style={{ marginTop:14, display:"grid", gap:10 }}>
              <div style={{ fontSize:11, color:"#94a3b8" }}>?豯??哨???爸qaResult.scope || "??賂豢?????鈭???}</div>
              <div style={{ fontSize:12, color:"#e9d5ff", lineHeight:1.8, whiteSpace:"pre-wrap" }}>{qaResult.answer}</div>
              <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
                <Badge color="#a855f7">prompt {qaResult.prompt_version}</Badge>
                <Badge color={qaResult.needs_human_review ? "#f59e0b" : "#22c55e"}>{qaResult.needs_human_review ? "???剔?璆菟?僚" : "????鈭止???}</Badge>
              </div>
              {(qaResult.insufficient_evidence || []).length > 0 && (
                <div style={{ background:"rgba(245,158,11,0.08)", border:"1px solid rgba(245,158,11,0.18)", borderRadius:10, padding:"10px 12px" }}>
                  <div style={{ fontSize:12, color:"#fcd34d", fontWeight:700, marginBottom:6 }}>??????/div>
                  {(qaResult.insufficient_evidence || []).map((item, idx) => (
                    <div key={idx} style={{ fontSize:12, color:"#fde68a", lineHeight:1.6 }}>- {item}</div>
                  ))}
                </div>
              )}
              <div>
                <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>????芣</div>
                <div style={{ display:"flex", flexDirection:"column", gap:8 }}>
                  {(qaResult.citations || []).map((item, idx) => (
                    <div key={idx} style={{ background:"rgba(255,255,255,0.03)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:10, padding:"10px 12px" }}>
                      <div style={{ fontSize:12, color:"#c4b5fd", marginBottom:4 }}>{item.title}</div>
                      <div style={{ fontSize:11, color:"#94a3b8", marginBottom:4 }}>{item.source_path}</div>
                      <div style={{ fontSize:12, color:"#cbd5e1", lineHeight:1.6 }}>{item.preview}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        <div style={{ background:"rgba(255,255,255,0.04)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:14, padding:18 }}>
          <div style={{ fontSize:15, fontWeight:700, color:"#e2e8f0", marginBottom:12 }}>??????仿</div>
          <div style={{ display:"grid", gap:10 }}>
            <div>
              <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>?????渲</div>
              <textarea value={deviationForm.issue_description} onChange={e => setDeviationForm(prev => ({ ...prev, issue_description: e.target.value }))} style={{ ...inputStyle, minHeight:88, resize:"vertical" }} />
            </div>
            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:10 }}>
              <div>
                <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>????遛?</div>
                <input value={deviationForm.process_step} onChange={e => setDeviationForm(prev => ({ ...prev, process_step: e.target.value }))} style={inputStyle} />
              </div>
              <div>
                <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>?撖?</div>
                <input value={deviationForm.lot_no} onChange={e => setDeviationForm(prev => ({ ...prev, lot_no: e.target.value }))} style={inputStyle} />
              </div>
              <div>
                <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>?皝???/div>
                <select value={deviationForm.severity} onChange={e => setDeviationForm(prev => ({ ...prev, severity: e.target.value }))} style={inputStyle}>
                  <option value="low">low</option>
                  <option value="medium">medium</option>
                  <option value="high">high</option>
                </select>
              </div>
            </div>
          </div>
          <button onClick={runDeviationDraft} disabled={deviationBusy} style={{ marginTop:12, background:"linear-gradient(135deg,#dc2626,#f97316)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"10px 16px", fontSize:13, fontWeight:700, opacity: deviationBusy ? 0.6 : 1 }}>{deviationBusy ? "?嚗???.." : "?嚗???????仿"}</button>
          {deviationMessage && <div style={{ marginTop:10, fontSize:12, color:"#fdba74" }}>{deviationMessage}</div>}
          {deviationResult && (
            <div style={{ marginTop:14, display:"grid", gap:10 }}>
              <div style={{ fontSize:12, color:"#fde68a", lineHeight:1.7 }}>{deviationResult.draft_summary}</div>
              {[
                ["?貔??", deviationResult.known_facts],
                ["??迎??賹?", deviationResult.possible_causes],
                ["?????僥????", deviationResult.containment_actions],
                ["?防?????摮?", deviationResult.permanent_actions],
                ["?踐???殷???, deviationResult.verification_plan],
              ].map(([label, items]) => (
                <div key={label} style={{ background:"rgba(255,255,255,0.03)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:10, padding:"10px 12px" }}>
                  <div style={{ fontSize:12, color:"#e2e8f0", fontWeight:700, marginBottom:6 }}>{label}</div>
                  <div style={{ display:"flex", flexDirection:"column", gap:4 }}>
                    {(items || []).map((item, idx) => (
                      <div key={idx} style={{ fontSize:12, color:"#cbd5e1", lineHeight:1.6 }}>- {item}</div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div style={{ marginTop:18, background:"rgba(255,255,255,0.03)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:14, padding:18 }}>
        <div style={{ display:"flex", justifyContent:"space-between", gap:12, flexWrap:"wrap", alignItems:"center", marginBottom:10 }}>
          <div style={{ fontSize:14, fontWeight:700, color:"#e2e8f0" }}>??刻麾?謚??荒??</div>
          <div style={{ display:"flex", gap:10, flexWrap:"wrap" }}>
            <input value={searchQuery} onChange={e => setSearchQuery(e.target.value)} style={{ ...inputStyle, width:260 }} />
            <button onClick={runSearch} disabled={searchBusy} style={{ background:"rgba(56,189,248,0.16)", border:"1px solid rgba(56,189,248,0.3)", borderRadius:10, color:"#bae6fd", cursor:"pointer", padding:"10px 16px", fontSize:13, fontWeight:700, opacity: searchBusy ? 0.6 : 1 }}>{searchBusy ? "?謚???.." : "????謚?"}</button>
          </div>
        </div>
        <div style={{ display:"flex", flexDirection:"column", gap:8 }}>
          {searchResults.map((item, idx) => (
            <div key={idx} style={{ background:"rgba(255,255,255,0.02)", border:"1px solid rgba(255,255,255,0.06)", borderRadius:10, padding:"10px 12px" }}>
              <div style={{ fontSize:12, color:"#7dd3fc", marginBottom:4 }}>{item.title}</div>
              <div style={{ fontSize:11, color:"#94a3b8", marginBottom:4 }}>{item.source_path}</div>
              <div style={{ fontSize:12, color:"#cbd5e1", lineHeight:1.6 }}>{item.preview}</div>
            </div>
          ))}
          {searchResults.length === 0 && <div style={{ fontSize:12, color:"#64748b" }}>?垮謓?鈭??荒???????????????撗?謚??????岑?/div>}
        </div>
      </div>
    </div>
  );
}

// ?????? REPORT TAB ??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
function ReportTab({ instruments, documents, training, equipment, suppliers, nonConformances: ncs, auditPlans, envRecords }) {
  const [generated, setGenerated] = useState(false);
  const calibEnriched = instruments
    .filter(i => i.status !== "?????)
    .map(i => {
    const nextDate = getInstrumentNextCalibrationDate(i);
      return { ...i, nextDate, days: daysUntil(nextDate) };
    });
  const eqEnriched = equipment.map(eq => ({ ...eq, nextDate:addDays(eq.lastMaintenance,eq.intervalDays), days:daysUntil(addDays(eq.lastMaintenance,eq.intervalDays)) }));
  const supEnriched = suppliers.map(s => ({ ...s, nextEvalDate:addDays(s.lastEvalDate,s.evalIntervalDays), days:daysUntil(addDays(s.lastEvalDate,s.evalIntervalDays)) }));
  const overdue = calibEnriched.filter(i=>i.days<0).length;
  const soonCalib = calibEnriched.filter(i=>i.days>=0&&i.days<=14).length;
  const overdueEq = eqEnriched.filter(e=>e.days<0).length;
  const openNcs = ncs.filter(n=>n.status!=="????).length;
  const totalTraining = training.reduce((s,e)=>s+e.trainings.length,0);
  const auditCompleted = auditPlans.filter(a=>a.status==="????).length;
  const auditTotal = auditPlans.length;
  const envPassRate = envRecords.length>0?Math.round(envRecords.filter(r=>r.result==="??僱").length/envRecords.length*100):0;
  const tdStyle = { padding:"7px 12px", border:"1px solid #e2e8f0" };
  const thStyle = { padding:"8px 12px", textAlign:"left", border:"1px solid #e2e8f0", background:"#f1f5f9" };
  const secStyle = { fontSize:15, fontWeight:800, color:"#0f172a", paddingLeft:12, marginBottom:14 };
  const conStyle = { marginTop:10, padding:12, background:"#f8fafc", borderRadius:8, fontSize:13, color:"#374151" };
  return (
    <div>
      <SectionHeader title="?都赯????嚗??? color="#f472b6" />
      <div style={{ background:"rgba(244,114,182,0.06)", border:"1px solid rgba(244,114,182,0.2)", borderRadius:14, padding:24, marginBottom:20 }}>
        <div style={{ fontSize:15, color:"#f9a8d4", fontWeight:600, marginBottom:8 }}>[ISO 9001] ????嚗? ISO 9001:2015 ?都赯?謢????</div>
        <div style={{ fontSize:13, color:"#64748b", lineHeight:1.7 }}>??蝯??軋僕?謍船?????謕?????殉死???????皝??????蹓曇澈?謕???蹓??箸葡???蹓?????蹓?????堊??蹓?????殉死???抬??賡??閰???????/div>
        <div style={{ display:"flex", gap:12, marginTop:16 }}>
          <button onClick={() => setGenerated(true)} style={{ background:"linear-gradient(135deg, #be185d, #ec4899)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"12px 24px", fontSize:14, fontWeight:700 }}>[+] ?嚗??都赯???</button>
          {generated && (<button onClick={() => window.print()} style={{ background:"rgba(244,114,182,0.15)", border:"1px solid rgba(244,114,182,0.3)", borderRadius:10, color:"#f9a8d4", cursor:"pointer", padding:"12px 24px", fontSize:14, fontWeight:700 }}>[P] ?謅 / ?殉次蹌?PDF</button>)}
        </div>
      </div>
      {generated && (
        <div id="report-content" style={{ background:"#fff", color:"#1e293b", borderRadius:14, padding:32, fontFamily:"'Microsoft JhengHei', 'PingFang TC', 'Noto Sans TC', sans-serif" }}>
          <div style={{ textAlign:"center", borderBottom:"2px solid #e2e8f0", paddingBottom:20, marginBottom:24 }}>
            <div style={{ fontSize:22, fontWeight:800, color:"#0f172a" }}>??肅????蹌?鞈?????/div>
            <div style={{ fontSize:16, fontWeight:600, color:"#374151", marginTop:4 }}>ISO 9001:2015 ?蹓暸??蝯?鞈?僚?謢????</div>
            <div style={{ fontSize:13, color:"#6b7280", marginTop:8 }}>????嚗??鈭??爸formatDate(new Date().toISOString().split("T")[0])} / ?????秧?奕???∵??/div>
          </div>
{/* ??蹓??????MP-09 */}
          <div style={{ marginBottom:24 }}>
            <div style={{ ...secStyle, borderLeft:"4px solid #3b82f6" }}>??蹓??????????MP-09???鞊???/div>
            <table style={{ width:"100%", borderCollapse:"collapse", fontSize:13 }}><thead><tr style={{ background:"#f1f5f9" }}>{["????賣???,"???","?遴竣?","???綽赯??,"??瘣??亥縣","????].map(h=>(<th key={h} style={thStyle}>{h}</th>))}</tr></thead><tbody>{calibEnriched.map(i=>(<tr key={i.id}><td style={tdStyle}>{i.id}</td><td style={tdStyle}>{i.name}</td><td style={tdStyle}>{i.type}</td><td style={tdStyle}>{formatDate(i.calibratedDate)}</td><td style={tdStyle}>{formatDate(i.nextDate)}</td><td style={{...tdStyle,color:i.days<0?"#ef4444":i.days<=14?"#f97316":"#16a34a",fontWeight:700}}>{urgencyLabel(i.days)}</td></tr>))}</tbody></table>
            <div style={conStyle}>?都赯梯???城??{instruments.length} ????秋??????? <b style={{color:"#ef4444"}}>{overdue}</b> ???14?剜????? <b style={{color:"#f97316"}}>{soonCalib}</b> ??蹌verdue>0&&" [???] ?ｇ?????????????踐?????}</div>
          </div>
          {/* ?哨?蹓曇澈?鞈芾澈??MP-04 */}
          <div style={{ marginBottom:24 }}>
            <div style={{ ...secStyle, borderLeft:"4px solid #f97316" }}>?哨?蹓曇澈?鞈芾澈?謕???MP-04???鞊???/div>
            <table style={{ width:"100%", borderCollapse:"collapse", fontSize:13 }}><thead><tr style={{ background:"#f1f5f9" }}>{["?桀???箏?","???","?選???,"???綽???,"??瘣駁豲?","????].map(h=>(<th key={h} style={thStyle}>{h}</th>))}</tr></thead><tbody>{eqEnriched.map(eq=>(<tr key={eq.id}><td style={tdStyle}>{eq.id}</td><td style={tdStyle}>{eq.name}</td><td style={tdStyle}>{eq.location}</td><td style={tdStyle}>{formatDate(eq.lastMaintenance)}</td><td style={tdStyle}>{formatDate(eq.nextDate)}</td><td style={{...tdStyle,color:eq.days<0?"#ef4444":eq.days<=30?"#f97316":"#16a34a",fontWeight:700}}>{urgencyLabel(eq.days)}</td></tr>))}</tbody></table>
            <div style={conStyle}>?都赯梯???城??{equipment.length} ??澈?謕?????踐?? <b style={{color:"#ef4444"}}>{overdueEq}</b> ???/div>
          </div>
          {/* ??蹓箇??謜???MP-03 */}
          <div style={{ marginBottom:24 }}>
            <div style={{ ...secStyle, borderLeft:"4px solid #8b5cf6" }}>??蹓箇??謜?????殉瘥??P-03???鞊???/div>
            <table style={{ width:"100%", borderCollapse:"collapse", fontSize:13 }}><thead><tr style={{ background:"#f1f5f9" }}>{["??芣扔?箏?","?軋?","???","???","?????,"?殉瘥????,"?叟▼?????,"?????].map(h=>(<th key={h} style={thStyle}>{h}</th>))}</tr></thead><tbody>{training.map(emp=>(<tr key={emp.id}><td style={tdStyle}>{emp.id}</td><td style={{...tdStyle,fontWeight:600}}>{emp.name}</td><td style={tdStyle}>{emp.dept}</td><td style={tdStyle}>{emp.role}</td><td style={tdStyle}>{formatDate(emp.hireDate)}</td><td style={{...tdStyle,fontWeight:700}}>{emp.trainings.length}</td><td style={tdStyle}>{emp.trainings.filter(t=>t.type==="?叟▼?").length}</td><td style={tdStyle}>{emp.trainings.filter(t=>t.cert==="??).length}</td></tr>))}</tbody></table>
            <div style={conStyle}>?都赯梯???城??{training.length} ??????殉瘥?殉死???? <b>{totalTraining}</b> ????/div>
          </div>
          {/* ?謜蹓???? MP-10 */}
          <div style={{ marginBottom:24 }}>
          <div style={{ ...secStyle, borderLeft:"4px solid #06b6d4" }}>?謜蹓澗????????????MP-12???鞊???/div>
            <table style={{ width:"100%", borderCollapse:"collapse", fontSize:13 }}><thead><tr style={{ background:"#f1f5f9" }}>{["????????,"???","?遴竣??,"?堊???","?堊???荒??","???綽???,"??瘣駁??"].map(h=>(<th key={h} style={thStyle}>{h}</th>))}</tr></thead><tbody>{supEnriched.map(s=>(<tr key={s.id}><td style={tdStyle}>{s.id}</td><td style={{...tdStyle,fontWeight:600}}>{s.name}</td><td style={tdStyle}>{s.category}</td><td style={{...tdStyle,fontWeight:700,color:s.evalScore>=90?"#16a34a":s.evalScore>=70?"#d97706":"#ef4444"}}>{s.evalScore}</td><td style={tdStyle}>{s.evalResult}</td><td style={tdStyle}>{formatDate(s.lastEvalDate)}</td><td style={{...tdStyle,color:s.days<0?"#ef4444":"#374151"}}>{formatDate(s.nextEvalDate)}</td></tr>))}</tbody></table>
            <div style={conStyle}>?都赯梯???城??{suppliers.length} ?啣????????純?? <b style={{color:"#ef4444"}}>{supEnriched.filter(s=>s.days<0).length}</b> ?啣????颲??僱 <b style={{color:"#eab308"}}>{suppliers.filter(s=>s.evalResult==="??颲??僱").length}</b> ?啣???/div>
          </div>
          {/* ?叟??蹓???? MP-15 */}
          <div style={{ marginBottom:24 }}>
          <div style={{ ...secStyle, borderLeft:"4px solid #ef4444" }}>?叟??蹓???????????頦?MP-20???鞊???/div>
            <table style={{ width:"100%", borderCollapse:"collapse", fontSize:13 }}><thead><tr style={{ background:"#f1f5f9" }}>{["?箏?","?鈭?","???","?遴竣?","?皝???,"?芬???,"???,"?????,"????].map(h=>(<th key={h} style={thStyle}>{h}</th>))}</tr></thead><tbody>{ncs.map(nc=>(<tr key={nc.id}><td style={{...tdStyle,fontFamily:"monospace",fontSize:11}}>{nc.id}</td><td style={tdStyle}>{formatDate(nc.date)}</td><td style={tdStyle}>{nc.dept}</td><td style={tdStyle}>{nc.type}</td><td style={{...tdStyle,color:nc.severity==="???"?"#ef4444":"#d97706",fontWeight:700}}>{nc.severity}</td><td style={tdStyle}>{nc.description.substring(0,20)}{nc.description.length>20?"...":""}</td><td style={tdStyle}>{nc.responsible}</td><td style={tdStyle}>{formatDate(nc.dueDate)}</td><td style={{...tdStyle,color:nc.status==="?????"#16a34a":nc.status==="??????"#d97706":"#ef4444",fontWeight:700}}>{nc.status}</td></tr>))}</tbody></table>
            <div style={conStyle}>?都赯梯???城??{ncs.length} ????????????????<b style={{color:"#ef4444"}}>{openNcs}</b> ???蹌penNcs>0&&" [???] ?ｇ?謆??啾秤?謚???梱???貔????鞈ｆ??蛛???撞??}</div>
          </div>
          {/* ??蹓鳴??賡???MP-09 */}
          <div style={{ marginBottom:24 }}>
          <div style={{ ...secStyle, borderLeft:"4px solid #8b5cf6" }}>??蹓鳴??賡??鞎???MP-17?貔????/div>
            <div style={conStyle}>??貉?鞈?僚????<b>{auditCompleted}</b> ??/ ?殷???<b>{auditTotal}</b> ???堆???<b>{auditTotal>0?Math.round(auditCompleted/auditTotal*100):0}%</b>?蹇??殷?謒??{auditPlans.reduce((s,a)=>s+a.findings,0)} ?????瘜??{auditPlans.reduce((s,a)=>s+a.ncCount,0)} ??倦?/div>
          </div>
          {ENABLE_ENVIRONMENT_MODULE && (
            <div style={{ marginBottom:24 }}>
              <div style={{ ...secStyle, borderLeft:"4px solid #14b8a6" }}>??蹓餅扔?遴鬲???畸????MP-07???鞊???/div>
              <div style={conStyle}>??璆?止??謆?? {envRecords.length} ????皝???僱??<b style={{color:envPassRate>=90?"#16a34a":envPassRate>=80?"#d97706":"#ef4444"}}>{envPassRate}%</b>????僱 <b style={{color:"#ef4444"}}>{envRecords.filter(r=>r.result==="?????).length}</b> ?????? <b style={{color:"#d97706"}}>{envRecords.filter(r=>r.result==="???").length}</b> ????/div>
            </div>
          )}
          <div style={{ borderTop:"1px solid #e2e8f0", paddingTop:16, marginTop:24, display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:16 }}>
            {["?都赯??,"??赯??,"?閰???].map(role => (<div key={role} style={{ textAlign:"center" }}><div style={{ height:40, borderBottom:"1px solid #374151" }} /><div style={{ fontSize:12, color:"#6b7280", marginTop:6 }}>{role}??????</div></div>))}
          </div>
        </div>
      )}
    </div>
  );
}


