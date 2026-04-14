function TrainingTab({ training, setTraining }) {
  const [selectedId, setSelectedId] = useState("");
  const [showTrainingModal, setShowTrainingModal] = useState(false);
  const [showEmployeeModal, setShowEmployeeModal] = useState(false);
  const [employeeDraft, setEmployeeDraft] = useState({ id: "", name: "", dept: "", role: "", hireDate: "", note: "" });
  const [trainingDraft, setTrainingDraft] = useState({ course: "", date: "", type: "???", result: "??僱", cert: "??, validUntil: "", hours: "", instructor: "", note: "" });
  const [editingEmployeeId, setEditingEmployeeId] = useState("");
  const [busy, setBusy] = useState("");
  const [message, setMessage] = useState("");
  const [search, setSearch] = useState("");
  const [deptFilter, setDeptFilter] = useState("ALL");

  useEffect(() => {
    if (!training.length) {
      setSelectedId("");
      return;
    }
    if (!training.some(item => item.id === selectedId)) {
      setSelectedId(training[0].id);
    }
  }, [training, selectedId]);

  const selected = training.find(item => item.id === selectedId) || null;
  const deptOptions = Array.from(new Set(training.map(item => item.dept).filter(Boolean))).sort((a, b) => a.localeCompare(b, "zh-Hant"));
  const filteredEmployees = training.filter(item => {
    const matchesDept = deptFilter === "ALL" || item.dept === deptFilter;
    const keyword = search.trim().toLowerCase();
    const matchesSearch = !keyword || [item.id, item.name, item.dept, item.role].some(value => String(value || "").toLowerCase().includes(keyword));
    return matchesDept && matchesSearch;
  });
  const totalTraining = training.reduce((sum, employee) => sum + (employee.trainings || []).length, 0);
  const externalTrainingCount = training.reduce((sum, employee) => sum + (employee.trainings || []).filter(item => item.type === "?叟▼?").length, 0);
  const certTrainingCount = training.reduce((sum, employee) => sum + (employee.trainings || []).filter(item => item.cert === "??).length, 0);
  const expiringCount = training.filter(employee => {
    const expiry = getEmployeeTrainingExpiry(employee);
    return expiry && daysUntil(expiry) <= 30;
  }).length;

  function resetEmployeeDraft(record = null) {
    setEmployeeDraft(record ? {
      id: record.id || "",
      name: record.name || "",
      dept: record.dept || "",
      role: record.role || "",
      hireDate: record.hireDate || "",
      note: record.note || "",
    } : { id: "", name: "", dept: "", role: "", hireDate: "", note: "" });
  }

  function resetTrainingDraft() {
    setTrainingDraft({ course: "", date: "", type: "???", result: "??僱", cert: "??, validUntil: "", hours: "", instructor: "", note: "" });
  }

  async function saveEmployeeRecord(record, successText) {
    setBusy("save-employee");
    setMessage("");
    try {
      const payload = await apiJson("/api/training-records", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ record }),
      });
      setTraining(payload.items || []);
      setSelectedId(record.id || payload.saved?.[0]?.id || "");
      setMessage(successText);
    } catch (err) {
      setMessage("?踐???殉瘥???剜???? + err.message);
    } finally {
      setBusy("");
    }
  }

  async function saveEmployeeBasic() {
    if (!employeeDraft.id.trim() || !employeeDraft.name.trim()) {
      setMessage("?ｇ??????芣扔?箏???????);
      return;
    }
    const base = training.find(item => item.id === editingEmployeeId) || { trainings: [] };
    await saveEmployeeRecord(
      {
        ...base,
        ...employeeDraft,
        trainings: Array.isArray(base.trainings) ? base.trainings : [],
      },
      editingEmployeeId ? "?謆??祉???軋??蟡??謕? : "?謘?豯???嚚?
    );
    setShowEmployeeModal(false);
    setEditingEmployeeId("");
    resetEmployeeDraft();
  }

  async function saveTrainingEntry() {
    if (!selected) {
      setMessage("?ｇ???鞊???選??⊥?銋?);
      return;
    }
    if (!trainingDraft.course.trim()) {
      setMessage("?ｇ?????方??????);
      return;
    }
    await saveEmployeeRecord(
      {
        ...selected,
        trainings: [...(selected.trainings || []), { ...trainingDraft, id: `${selected.id}-T${Date.now()}` }],
      },
      "????殉此??箸葡????
    );
    setShowTrainingModal(false);
    resetTrainingDraft();
  }

  async function deleteEmployee(recordId) {
    if (!window.confirm("??畸??謕???芣扔?綽???▽??殉瘥?殉死???????摰?甇??????秋撒??????)) return;
    setBusy("delete-employee");
    setMessage("");
    try {
      const encodedId = encodeURIComponent(recordId);
      const payload = await apiDeleteWithFallback(`/api/training-records/${encodedId}`, `/api/training-records/${encodedId}/delete`);
      setTraining(payload.items || []);
      if (selectedId === recordId) setSelectedId((payload.items || [])[0]?.id || "");
      setMessage("?????漸?????箸葡????);
    } catch (err) {
      setMessage("??畸???芣扔?剜???? + err.message);
    } finally {
      setBusy("");
    }
  }

  async function deleteTrainingEntry(entryId) {
    if (!selected) return;
    if (!window.confirm("?????秋撒???氐謕??殉瘥?殉死????")) return;
    await saveEmployeeRecord(
      {
        ...selected,
        trainings: (selected.trainings || []).filter(item => item.id !== entryId),
      },
      "??????箸葡????
    );
  }
  return (
    <div>
      <SectionHeader title="?剔??⊿?扳??殉死?" count={training.length} color="#34d399" />
    <ModuleStatusBanner
        title="?獢??蹓遴??垮????璇??謕?????伐???
        tone="system"
        message="?謕??蹓踐?????????????????????殉瘥???蹇結?迎??望撖???肅????????????祗????蹓箄?憳蹓鳴??????寞??鞈??踐??????綽????????謕墨?殉瘥?殉死??皝??穿??啾??
      />
      <div style={{ display:"flex", gap:8, flexWrap:"wrap", alignItems:"center", marginBottom: 16 }}>
        <button onClick={() => { setEditingEmployeeId(""); resetEmployeeDraft(); setShowEmployeeModal(true); }} style={{ background:"linear-gradient(135deg,#059669,#10b981)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"9px 16px", fontSize:13, fontWeight:700 }}>????剔???/button>
        {message && <div style={{ fontSize:12, color:"#bbf7d0" }}>{message}</div>}
      </div>
      <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
        <StatCard label="??芣扔?剔捂?? value={training.length} color="#34d399" />
        <StatCard label="?殉瘥?株???? value={totalTraining} color="#60a5fa" />
        <StatCard label="?叟▼????? value={externalTrainingCount} color="#a78bfa" />
        <StatCard label="????鞎??? value={certTrainingCount} color="#f472b6" />
        <StatCard label="30 ?剜?????" value={expiringCount} color="#f97316" />
      </div>
      <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(180px, 1fr))", gap:12, marginBottom: 16 }}>
        <div>
          <div style={{ fontSize:12, color:"#94a3b8", marginBottom:6 }}>???</div>
          <select value={deptFilter} onChange={e => setDeptFilter(e.target.value)} style={inputStyle}>
            <option value="ALL">??賂???</option>
            {deptOptions.map(item => <option key={item} value={item}>{item}</option>)}
          </select>
        </div>
        <div>
          <div style={{ fontSize:12, color:"#94a3b8", marginBottom:6 }}>?謚?</div>
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="??????⊥?鈭行??貔螞蹓???蹓選???蹓橫??? style={inputStyle} />
        </div>
      </div>
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
        <div style={{ flex: "0 0 260px", display: "flex", flexDirection: "column", gap: 8 }}>
          {filteredEmployees.map(emp => {
            const hireMonths = Math.floor((today - new Date(emp.hireDate)) / (30*86400000));
            const isNew = hireMonths < 3;
            const expiry = getEmployeeTrainingExpiry(emp);
            const days = daysUntil(expiry);
            return (<div key={emp.id} onClick={() => setSelectedId(emp.id)} style={{ background: selected?.id===emp.id?"rgba(52,211,153,0.15)":"rgba(255,255,255,0.04)", border: `1px solid ${selected?.id===emp.id?"rgba(52,211,153,0.4)":"rgba(255,255,255,0.08)"}`, borderRadius: 12, padding: "14px 16px", cursor: "pointer" }}><div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap:8 }}><div><div style={{ fontWeight: 700, color: "#e2e8f0", fontSize: 14 }}>{emp.name}</div><div style={{ fontSize: 12, color: "#64748b", marginTop: 2 }}>{emp.dept || "??詹???"} 蝜?{emp.role || "??詹???"}</div></div><div style={{ textAlign: "right" }}>{isNew&&<Badge color="#f97316">???/Badge>}{expiry && <div style={{ marginTop:4 }}><Badge color={urgencyColor(days)}>{urgencyLabel(days)}</Badge></div>}<div style={{ fontSize: 11, color: "#64748b", marginTop: 4 }}>{(emp.trainings || []).length} ?????/div></div></div></div>);
          })}
          {filteredEmployees.length === 0 && <div style={{ textAlign:"center", padding:"24px 18px", color:"#64748b", background:"rgba(255,255,255,0.03)", borderRadius:12 }}>?獢?????????颲????嚚?/div>}
        </div>
        <div style={{ flex: 1, minWidth: 280 }}>
          {selected ? (
            <div>
              <div style={{ background: "rgba(255,255,255,0.04)", borderRadius: 12, padding: 16, border: "1px solid rgba(255,255,255,0.08)", marginBottom: 14 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap:12, flexWrap:"wrap" }}>
                  <div>
                    <div style={{ fontSize: 18, fontWeight: 800, color: "#e2e8f0" }}>{selected.name}</div>
                    <div style={{ color: "#64748b", fontSize: 13, marginTop: 4 }}>{selected.id} 蝜?{selected.dept} 蝜?{selected.role}</div>
                    <div style={{ color: "#64748b", fontSize: 12, marginTop: 2 }}>????隡?{formatDate(selected.hireDate)}</div>
                    {selected.note && <div style={{ color:"#94a3b8", fontSize:12, marginTop:6 }}>?謕??爸selected.note}</div>}
                  </div>
                  <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
                    <button onClick={() => { setEditingEmployeeId(selected.id); resetEmployeeDraft(selected); setShowEmployeeModal(true); }} style={{ background:"rgba(255,255,255,0.08)", border:"1px solid rgba(255,255,255,0.15)", borderRadius:8, color:"#cbd5e1", cursor:"pointer", padding:"7px 14px", fontSize:12, fontWeight:700 }}>?賣?蝞</button>
                    <button onClick={() => { resetTrainingDraft(); setShowTrainingModal(true); }} style={{ background: "linear-gradient(135deg, #059669, #10b981)", border: "none", borderRadius: 8, color: "#fff", cursor: "pointer", padding: "7px 14px", fontSize: 12, fontWeight: 700 }}>??????殉瘥</button>
                    <button onClick={() => deleteEmployee(selected.id)} disabled={busy !== ""} style={{ background:"rgba(239,68,68,0.14)", border:"1px solid rgba(239,68,68,0.28)", borderRadius:8, color:"#fca5a5", cursor:"pointer", padding:"7px 14px", fontSize:12, fontWeight:700, opacity:busy ? 0.7 : 1 }}>??畸??剔???/button>
                  </div>
                </div>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {(selected.trainings || []).map((t) => (
                  <div key={t.id || t.course} style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: 10, padding: "12px 16px", display: "flex", gap: 16, alignItems: "center", flexWrap:"wrap" }}>
                    <div style={{ flex: 1, minWidth:220 }}>
                      <div style={{ fontWeight: 600, color: "#e2e8f0", fontSize: 13 }}>{t.course}</div>
                      <div style={{ fontSize: 11, color: "#64748b", marginTop: 3 }}>{formatDate(t.date)} 蝜?{t.type}{t.instructor ? ` 蝜?????${t.instructor}` : ""}</div>
                      {(t.validUntil || t.note) && <div style={{ fontSize: 11, color: "#94a3b8", marginTop: 4 }}>{t.validUntil ? `?????${formatDate(t.validUntil)}` : ""}{t.validUntil && t.note ? " 蝜?" : ""}{t.note || ""}</div>}
                    </div>
                    <Badge color={t.result==="??僱"?"#22c55e":t.result==="??????"#ef4444":"#f59e0b"}>{t.result}</Badge>
                    {t.cert==="??&&<Badge color="#a78bfa">?????/Badge>}
                    <button onClick={() => deleteTrainingEntry(t.id)} disabled={busy !== ""} style={{ background:"rgba(239,68,68,0.14)", border:"1px solid rgba(239,68,68,0.28)", borderRadius:8, color:"#fca5a5", cursor:"pointer", padding:"6px 12px", fontSize:12, opacity:busy ? 0.7 : 1 }}>??畸?</button>
                  </div>
                ))}
                {(selected.trainings || []).length === 0 && <div style={{ textAlign:"center", padding:"24px 20px", color:"#64748b", background:"rgba(255,255,255,0.03)", borderRadius:10 }}>?謕???芣扔?獢????????箸葡????/div>}
              </div>
            </div>
          ) : (<div style={{ textAlign: "center", padding: "60px 20px", color: "#475569" }}>???綜筐蹓?銵蹓??芣扔?漱貔????箸葡???/div>)}
        </div>
      </div>
      {showEmployeeModal && (
        <Modal title={editingEmployeeId ? "?賣?蝞??" : "????剔???} onClose={() => { setShowEmployeeModal(false); setEditingEmployeeId(""); }}>
          <div style={{ display:"flex", flexDirection:"column", gap:12 }}>
            {[["??芣扔?箏?","id","text"],["?軋?","name","text"],["???","dept","text"],["???","role","text"],["?????,"hireDate","date"]].map(([label, field, type]) => (
              <div key={field}>
                <div style={{ fontSize:12, color:"#64748b", marginBottom:5 }}>{label}</div>
                <input type={type} value={employeeDraft[field]} onChange={e => setEmployeeDraft({ ...employeeDraft, [field]: e.target.value })} style={inputStyle} disabled={editingEmployeeId && field === "id"} />
              </div>
            ))}
            <div>
              <div style={{ fontSize:12, color:"#64748b", marginBottom:5 }}>?謕?</div>
              <textarea value={employeeDraft.note} onChange={e => setEmployeeDraft({ ...employeeDraft, note: e.target.value })} style={{ ...inputStyle, minHeight:72, resize:"vertical" }} />
            </div>
            <button onClick={saveEmployeeBasic} disabled={busy !== ""} style={{ background:"linear-gradient(135deg,#059669,#10b981)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"12px 24px", fontSize:15, fontWeight:700, marginTop:8, opacity:busy ? 0.7 : 1 }}>{busy === "save-employee" ? "?踐????.." : "?????踐??"}</button>
          </div>
        </Modal>
      )}
      {showTrainingModal && selected && (
        <Modal title={`????殉瘥?殉死???{selected.name}`} onClose={() => setShowTrainingModal(false)}>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            {[["?方????","course","text"],["?殉瘥?鈭?","date","date"],["????賹?","validUntil","date"],["?蹇","hours","number"],["????/ ??朣?,"instructor","text"]].map(([label,field,type]) => (
              <div key={field}>
                <div style={{ fontSize: 12, color: "#64748b", marginBottom: 5 }}>{label}</div>
                <input type={type} value={trainingDraft[field]} onChange={e => setTrainingDraft({ ...trainingDraft, [field]: e.target.value })} style={inputStyle} />
              </div>
            ))}
            <div>
              <div style={{ fontSize: 12, color: "#64748b", marginBottom: 5 }}>?殉瘥?遴竣?</div>
              <select value={trainingDraft.type} onChange={e => setTrainingDraft({ ...trainingDraft, type: e.target.value })} style={inputStyle}><option>???</option><option>?叟▼?</option></select>
            </div>
            <div>
              <div style={{ fontSize: 12, color: "#64748b", marginBottom: 5 }}>?堊??航??</div>
              <select value={trainingDraft.result} onChange={e => setTrainingDraft({ ...trainingDraft, result: e.target.value })} style={inputStyle}><option>??僱</option><option>?????/option><option>?綽???/option></select>
            </div>
            <div>
              <div style={{ fontSize: 12, color: "#64748b", marginBottom: 5 }}>??秋?????????/div>
              <select value={trainingDraft.cert} onChange={e => setTrainingDraft({ ...trainingDraft, cert: e.target.value })} style={inputStyle}><option>??/option><option>??/option></select>
            </div>
            <div>
              <div style={{ fontSize: 12, color: "#64748b", marginBottom: 5 }}>?謕?</div>
              <textarea value={trainingDraft.note} onChange={e => setTrainingDraft({ ...trainingDraft, note: e.target.value })} style={{ ...inputStyle, minHeight:72, resize:"vertical" }} />
            </div>
            <button onClick={saveTrainingEntry} disabled={busy !== ""} style={{ background: "linear-gradient(135deg, #059669, #10b981)", border: "none", borderRadius: 10, color: "#fff", cursor: "pointer", padding: "12px 24px", fontSize: 15, fontWeight: 700, marginTop: 8, opacity:busy ? 0.7 : 1 }}>{busy === "save-employee" ? "?踐????.." : "????殉瘥?殉死?"}</button>
          </div>
        </Modal>
      )}
    </div>
  );
}

// ?????? EQUIPMENT TAB ????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
function EnvironmentTab({ envRecords, setEnvRecords }) {
  const emptyDraft = { date:"", measuredAt:"", location:"??璆銋??", point:"", particles03:0, particles05:0, particles5:0, temp:"", humidity:"", pressure:"", operator:"", result:"" };
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState("");
  const [rangeStart, setRangeStart] = useState("");
  const [rangeEnd, setRangeEnd] = useState("");
  const [summary, setSummary] = useState({ total: envRecords.length, passed: envRecords.filter(r=>r.result==="??僱").length, warning: envRecords.filter(r=>r.result==="???").length, failed: envRecords.filter(r=>r.result==="?????).length });
  const [showAdd, setShowAdd] = useState(false);
  const [draft, setDraft] = useState(emptyDraft);
  const [importPreview, setImportPreview] = useState([]);
  const [importSummary, setImportSummary] = useState(null);
  const environmentSortKey = (item) => {
    const measuredAt = String(item?.measuredAt || "").trim();
    if (measuredAt) {
      const measuredValue = Date.parse(measuredAt);
      if (!Number.isNaN(measuredValue)) return measuredValue;
    }
    const datePart = String(item?.date || "").trim();
    const timeMatch = String(item?.location || "").match(/(\d{1,2}:\d{2}:\d{2})/);
    const timePart = timeMatch ? timeMatch[1] : "00:00:00";
    const candidate = `${datePart}T${timePart}`;
    const value = Date.parse(candidate);
    return Number.isNaN(value) ? 0 : value;
  };
  const sorted = [...envRecords].sort((a, b) => environmentSortKey(a) - environmentSortKey(b));
  const resultColor = r => r==="??僱"?"#22c55e":r==="???"?"#eab308":"#ef4444";

  useEffect(() => {
    const nextSummary = {
      total: envRecords.length,
      passed: envRecords.filter(item=>item.result==="??僱").length,
      warning: envRecords.filter(item=>item.result==="???").length,
      failed: envRecords.filter(item=>item.result==="?????).length,
    };
    setSummary(nextSummary);
  }, [envRecords]);

  function buildRecord(record) {
    const point = String(record.point || "").trim();
    const measuredAt = String(record.measuredAt || "").trim();
    const particles03 = parseInt(record.particles03 || 0, 10) || 0;
    const particles05 = parseInt(record.particles05 || 0, 10) || 0;
    const particles5 = parseInt(record.particles5 || 0, 10) || 0;
    const temp = record.temp === "" ? "" : parseFloat(record.temp || 0) || 0;
    const humidity = record.humidity === "" ? "" : parseFloat(record.humidity || 0) || 0;
    const pressure = record.pressure === "" ? "" : parseFloat(record.pressure || 0) || 0;
    let result = record.result;
    if (!result) {
      if (particles05 > 1000 || particles5 > 35 || (temp !== "" && (temp > 23 || temp < 21)) || (humidity !== "" && (humidity > 50 || humidity < 40)) || (pressure !== "" && pressure < 10)) result = "?????;
      else if (particles05 > 800 || particles5 > 20 || (temp !== "" && temp > 22.5) || (humidity !== "" && humidity > 48)) result = "???";
      else result = "??僱";
    }
    return { ...record, point, measuredAt, particles03, particles05, particles1:0, particles5, temp, humidity, pressure, result };
  }

  async function saveRecords(records, doneMessage, replaceSourceFile = "") {
    setBusy("save");
    setMessage("");
    try {
      const payload = await apiJson("/api/environment-records", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ records, replace_source_file: replaceSourceFile }),
      });
      setEnvRecords(payload.items || []);
      setSummary(payload.summary || { total:0, passed:0, warning:0, failed:0 });
      setMessage(doneMessage);
      return true;
    } catch (err) {
      setMessage("?殉朵??剜???? + err.message);
      return false;
    } finally {
      setBusy("");
    }
  }

  async function loadRange(start = rangeStart, end = rangeEnd) {
    setBusy("query");
    setMessage("");
    try {
      const params = new URLSearchParams();
      if (start) params.set("start", start);
      if (end) params.set("end", end);
      const payload = await apiJson("/api/environment-records" + (params.toString() ? "?" + params.toString() : ""));
      setEnvRecords(payload.items || []);
      setSummary(payload.summary || { total:0, passed:0, warning:0, failed:0 });
      setMessage("????蹇???????謘??謕?);
    } catch (err) {
      setMessage("??謘潔??謅?" + err.message);
    } finally {
      setBusy("");
    }
  }

  async function addRecord() {
    const ok = await saveRecords([buildRecord(draft)], "?謘?豯佇??謆????謕?);
    if (!ok) return;
    setShowAdd(false);
    setDraft(emptyDraft);
  }

  async function deleteRecord(id) {
    if (!window.confirm("?????秋撒???氐謕??????????")) return;
    setBusy("delete");
    try {
      const payload = await apiJson("/api/environment-records/" + encodeURIComponent(id), { method:"DELETE" });
      setEnvRecords(payload.items || []);
      setSummary(payload.summary || { total:0, passed:0, warning:0, failed:0 });
      setMessage("????止?????謕?);
    } catch (err) {
      setMessage("??畸??剜???? + err.message);
    } finally {
      setBusy("");
    }
  }

  async function deleteRange() {
    if (!rangeStart && !rangeEnd) {
      setMessage("?ｇ???鞊??秋撒?????鈭???????);
      return;
    }
    if (!window.confirm("?????秋撒???縐?蹇??????????伍?????謕???)) return;
    setBusy("delete-range");
    try {
      const payload = await apiJson("/api/environment-records/delete-range", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ start: rangeStart, end: rangeEnd }),
      });
      setEnvRecords(payload.items || []);
      setSummary(payload.summary || { total:0, passed:0, warning:0, failed:0 });
      setMessage(`????${payload.deleted || 0} ????謕蹐?;
    } catch (err) {
      setMessage("????伐?????謅?" + err.message);
    } finally {
      setBusy("");
    }
  }

  async function importFile(file) {
    if (!file) return;
    setBusy("import");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const payload = await apiJson("/api/environment-records/import", { method:"POST", body:formData });
      setImportPreview(payload.records || []);
      setImportSummary(payload.summary || null);
      setMessage((payload.records || []).length ? "???謘??迎???謕??ｇ??⊿??????銋? : "?澗?????????選?謆?????血??朱???穿??鈭???????????蹇??????賹??澗?赯菜??純?);
    } catch (err) {
      setMessage("??穿?剜???? + err.message);
    } finally {
      setBusy("");
    }
  }

  async function confirmImport() {
    if (!importPreview.length) return;
    const replaceSourceFile = importPreview[0]?.source_file || "";
    const records = importPreview.map(({ missing_fields, id, ...record }) => record);
    const ok = await saveRecords(records, `????${records.length} ?????畸?????謕蹐? replaceSourceFile);
    if (!ok) return;
    setImportPreview([]);
    setImportSummary(null);
  }

  const passRate = summary.total > 0 ? Math.round((summary.passed / summary.total) * 100) : 0;
  const formatMaybeNumber = (value, digits = 1) => {
    if (value === "" || value === null || value === undefined) return "??;
    const numeric = Number(value);
    return Number.isFinite(numeric) ? numeric.toFixed(digits) : "??;
  };
  const formatMaybeInteger = (value) => {
    if (value === "" || value === null || value === undefined) return "??;
    const numeric = Number(value);
    return Number.isFinite(numeric) ? numeric.toLocaleString() : "??;
  };

  return (
    <div>
      <SectionHeader title="?鼎?????????-07?? count={envRecords.length} color="#14b8a6" />
      <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
        <StatCard label="?株???? value={summary.total} color="#14b8a6" />
        <StatCard label="??僱" value={summary.passed} color="#22c55e" />
        <StatCard label="???" value={summary.warning} color="#eab308" />
        <StatCard label="????? value={summary.failed} color="#ef4444" />
        <StatCard label="??僱?? value={`${passRate}%`} color={passRate>=90?"#22c55e":passRate>=80?"#eab308":"#ef4444"} sub="?獢??剜?蹓??" />
      </div>
      <div style={{ background: "rgba(20,184,166,0.06)", border: "1px solid rgba(20,184,166,0.2)", borderRadius: 12, padding: 16, marginBottom: 20 }}>
        <div style={{ fontSize: 13, color: "#2dd4bf", fontWeight: 700, marginBottom: 8 }}>Class 1000 ??蜃????/div>
        <div style={{ display:"flex", gap:24, flexWrap:"wrap", fontSize:12, color:"#64748b" }}>
          <span>0.5撘峻 ??? ??1000</span>
          <span>5撘峻 ??? ??35</span>
          <span>?撞 21??3蝪</span>
          <span>??瞍?40??0% RH</span>
          <span>??? ??10 Pa</span>
        </div>
      </div>
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", gap:12, marginBottom:14, flexWrap:"wrap" }}>
        <div style={{ display:"flex", gap:10, flexWrap:"wrap", alignItems:"center" }}>
          <input type="date" value={rangeStart} onChange={e => setRangeStart(e.target.value)} style={{ ...inputStyle, width:170 }} />
          <span style={{ color:"#64748b", fontSize:12 }}>??/span>
          <input type="date" value={rangeEnd} onChange={e => setRangeEnd(e.target.value)} style={{ ...inputStyle, width:170 }} />
          <button onClick={() => loadRange()} style={{ background:"rgba(20,184,166,0.14)", border:"1px solid rgba(20,184,166,0.28)", borderRadius:10, color:"#99f6e4", cursor:"pointer", padding:"9px 16px", fontSize:13, fontWeight:700 }}>?鈭亙眺????/button>
          <button onClick={() => { setRangeStart(""); setRangeEnd(""); loadRange("", ""); }} style={{ background:"rgba(255,255,255,0.06)", border:"1px solid rgba(255,255,255,0.12)", borderRadius:10, color:"#cbd5e1", cursor:"pointer", padding:"9px 16px", fontSize:13, fontWeight:700 }}>?謒??</button>
        </div>
        <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
          <label style={{ background:"rgba(255,255,255,0.06)", border:"1px solid rgba(255,255,255,0.12)", borderRadius:10, color:"#e2e8f0", cursor:"pointer", padding:"9px 18px", fontSize:13, fontWeight:700 }}>
            {busy==="import" ? "??謘餉?..." : "??蹌?賹???"}
            <input type="file" accept=".xlsx,.csv" onChange={e => importFile(e.target.files && e.target.files[0])} style={{ display:"none" }} />
          </label>
          <button onClick={deleteRange} style={{ background:"rgba(239,68,68,0.14)", border:"1px solid rgba(239,68,68,0.28)", borderRadius:10, color:"#fca5a5", cursor:"pointer", padding:"9px 18px", fontSize:13, fontWeight:700 }}>??畸??????/button>
          <button onClick={() => setShowAdd(true)} style={{ background: "linear-gradient(135deg, #0d9488, #14b8a6)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"9px 18px", fontSize:13, fontWeight:700 }}>?????????</button>
        </div>
      </div>
      <div style={{ color:"#99f6e4", fontSize:12, marginBottom:14 }}>{message || "????鈭?????佇??堆撓???畸????????Excel/CSV ????謘??殉朱???}</div>
      <div style={{ overflowX:"auto" }}>
        <table style={{ width:"100%", borderCollapse:"collapse", fontSize:12 }}>
          <thead><tr>{["?箏?","?鈭?","?綜童?","???","0.3撘峻","0.5撘峻","5.0撘峻","?撞","??瞍?,"???","?殉死???,"?荒??",""].map(h => (<th key={h} style={{ textAlign:"left", padding:"8px 10px", color:"#64748b", fontWeight:600, borderBottom:"1px solid rgba(255,255,255,0.06)", whiteSpace:"nowrap" }}>{h}</th>))}</tr></thead>
          <tbody>
            {sorted.map((item,i) => (
              <tr key={item.id} style={{ background:i%2===0?"rgba(255,255,255,0.02)":"transparent" }}>
                <td style={{ padding:"8px 10px", color:"#14b8a6", fontFamily:"monospace" }}>{item.id}</td>
                <td style={{ padding:"8px 10px", color:"#94a3b8", whiteSpace:"nowrap" }}>{formatDate(item.date)}</td>
                <td style={{ padding:"8px 10px", color:"#94a3b8" }}>{item.point || "??}</td>
                <td style={{ padding:"8px 10px", color:"#e2e8f0" }}>{item.location}</td>
                <td style={{ padding:"8px 10px", color:"#94a3b8" }}>{formatMaybeInteger(item.particles03)}</td>
                <td style={{ padding:"8px 10px", color:item.particles05>1000?"#ef4444":item.particles05>800?"#eab308":"#94a3b8", fontWeight:item.particles05>800?700:400 }}>{formatMaybeInteger(item.particles05)}</td>
                <td style={{ padding:"8px 10px", color:item.particles5>35?"#ef4444":item.particles5>20?"#eab308":"#94a3b8", fontWeight:item.particles5>20?700:400 }}>{formatMaybeInteger(item.particles5)}</td>
                <td style={{ padding:"8px 10px", color:item.temp === "" || item.temp === null || item.temp === undefined ? "#64748b" : item.temp>23||item.temp<21?"#ef4444":"#94a3b8" }}>{formatMaybeNumber(item.temp)}</td>
                <td style={{ padding:"8px 10px", color:item.humidity === "" || item.humidity === null || item.humidity === undefined ? "#64748b" : item.humidity>50||item.humidity<40?"#ef4444":"#94a3b8" }}>{formatMaybeNumber(item.humidity)}</td>
                <td style={{ padding:"8px 10px", color:item.pressure === "" || item.pressure === null || item.pressure === undefined ? "#64748b" : item.pressure<10?"#ef4444":"#94a3b8" }}>{formatMaybeNumber(item.pressure)}</td>
                <td style={{ padding:"8px 10px", color:"#94a3b8" }}>{item.operator || "??}</td>
                <td style={{ padding:"8px 10px" }}><Badge color={resultColor(item.result)}>{item.result}</Badge></td>
                <td style={{ padding:"8px 10px" }}><button onClick={() => deleteRecord(item.id)} style={{ background:"rgba(239,68,68,0.14)", border:"1px solid rgba(239,68,68,0.28)", borderRadius:8, color:"#fca5a5", cursor:"pointer", padding:"6px 12px", fontSize:11 }}>??畸?</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {showAdd && (<Modal title="????????????" onClose={() => setShowAdd(false)}><div style={{ display:"flex", flexDirection:"column", gap:12 }}>{[["?鈭?","date","date"],["??脰?蹇?","measuredAt","datetime-local"],["?綜童?","point","text"],["???","location","text"],["0.3撘峻 ???","particles03","number"],["0.5撘峻 ???","particles05","number"],["5.0撘峻 ???","particles5","number"],["?撞","temp","number"],["??瞍?,"humidity","number"],["???","pressure","number"],["?殉死???,"operator","text"]].map(([label,field,type]) => (<div key={field}><div style={{ fontSize:12, color:"#64748b", marginBottom:5 }}>{label}</div><input type={type} value={draft[field]} onChange={e=>setDraft({...draft,[field]:e.target.value})} style={inputStyle} /></div>))}<button onClick={addRecord} disabled={busy==="save"} style={{ background:"linear-gradient(135deg,#0d9488,#14b8a6)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"12px 24px", fontSize:15, fontWeight:700, marginTop:8, opacity:busy==="save"?0.6:1 }}>{busy==="save"?"?殉朵???..":"???????"}</button></div></Modal>)}
      {importPreview.length>0 && (<Modal title="??穿???" onClose={() => { setImportPreview([]); setImportSummary(null); }}><div style={{ display:"flex", flexDirection:"column", gap:12 }}>{importSummary && <div style={{ background:"rgba(20,184,166,0.08)", border:"1px solid rgba(20,184,166,0.24)", borderRadius:8, padding:10, color:"#99f6e4", fontSize:12 }}>?蟡暑????爸importSummary.total} ?????僱 {importSummary.passed}?蹓暸???{importSummary.warning}?蹓???僱 {importSummary.failed}</div>}<div style={{ background:"rgba(255,255,255,0.03)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:10, padding:12, maxHeight:340, overflowY:"auto" }}>{importPreview.slice(0,20).map(item => (<div key={item.id || item.source_file + item.date} style={{ display:"grid", gridTemplateColumns:"110px 1fr 120px", gap:12, borderBottom:"1px solid rgba(255,255,255,0.05)", padding:"8px 0" }}><span style={{ color:"#5eead4", fontFamily:"monospace", fontSize:12 }}>{formatDate(item.date)}</span><span style={{ color:"#94a3b8", fontSize:12 }}>?綜童? {item.point || "??} 蝜?{item.location} 蝜?0.3撘峻 {formatMaybeInteger(item.particles03)} 蝜?0.5撘峻 {formatMaybeInteger(item.particles05)}</span><span style={{ color:item.missing_fields?.length?"#fde68a":"#cbd5e1", fontSize:12, textAlign:"right" }}>{item.missing_fields?.length ? `????${item.missing_fields.join("/")}` : item.result}</span></div>))}</div><button onClick={confirmImport} disabled={busy==="save"} style={{ background:"linear-gradient(135deg,#0d9488,#14b8a6)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"12px 24px", fontSize:15, fontWeight:700, marginTop:8, opacity:busy==="save"?0.6:1 }}>{busy==="save"?"?殉朵???..":"?????殉朱??}</button></div></Modal>)}
    </div>
  );
}

function ProductionTab({ envRecords, prodRecords, setProdRecords, qualityRecords, setQualityRecords, nonConformances, auditPlans, setActiveTab, setHighlightNcId, setExpandNcId }) {
  const objectRows = (value) => Array.isArray(value) ? value.filter(item => item && typeof item === "object") : [];
  const safeEnvRecords = objectRows(envRecords);
  const safeProdRecords = objectRows(prodRecords);
  const safeQualityRecords = objectRows(qualityRecords);
  const safeNonConformances = objectRows(nonConformances);
  const safeAuditPlans = objectRows(auditPlans);
  const [downloadType, setDownloadType] = useState("");
  const [message, setMessage] = useState("");
  const [shipmentOrders, setShipmentOrders] = useState([]);
  const [shipmentLoading, setShipmentLoading] = useState(true);
  const [shipmentBusy, setShipmentBusy] = useState(false);
  const [shipmentMessage, setShipmentMessage] = useState("");
  const [shipmentOrderNo, setShipmentOrderNo] = useState("");
  const [shipmentForm, setShipmentForm] = useState({ date:"", department:"", requester:"", product_name:"", spec:"", quantity:"", unit:"", remark:"", batch_display:"" });
  const [selectedLots, setSelectedLots] = useState([]);
  const [engineCatalog, setEngineCatalog] = useState([]);
  const [engineTemplateCode, setEngineTemplateCode] = useState("shipping_pack");
  const [enginePrompt, setEnginePrompt] = useState("");
  const [engineSuggestions, setEngineSuggestions] = useState([]);
  const [engineBusy, setEngineBusy] = useState(false);
  const [engineMessage, setEngineMessage] = useState("");
  const [enginePrecheck, setEnginePrecheck] = useState(null);
  const [enginePrecheckBusy, setEnginePrecheckBusy] = useState(false);
  const [selectedNcId, setSelectedNcId] = useState("");
  const [recordReadBusy, setRecordReadBusy] = useState("");
  const [prodStartDate, setProdStartDate] = useState("");
  const [prodEndDate, setProdEndDate] = useState("");
  const [prodSiteFilter, setProdSiteFilter] = useState("ALL");
  const [prodSearch, setProdSearch] = useState("");
  const [expandedProdGroups, setExpandedProdGroups] = useState({});
  const [qualitySearch, setQualitySearch] = useState("");
  const [qualityResultFilter, setQualityResultFilter] = useState("ALL");
  const [expandedQualityGroups, setExpandedQualityGroups] = useState({});
  const prodSectionRef = useRef(null);
  const qualitySectionRef = useRef(null);
  const shipmentSectionRef = useRef(null);
  const shipmentFieldRefs = {
    date: useRef(null),
    department: useRef(null),
    requester: useRef(null),
    product_name: useRef(null),
    quantity: useRef(null),
    spec: useRef(null),
    unit: useRef(null),
    batch_display: useRef(null),
  };

  useEffect(() => {
    let cancelled = false;
    async function loadCatalog() {
      setShipmentLoading(true);
      try {
        const response = await fetch("/api/shipment-draft/catalog");
        const payload = await response.json();
        if (!response.ok) throw new Error(payload.error || ("HTTP " + response.status));
        if (!cancelled) {
          const orders = payload.orders || [];
          setShipmentOrders(orders);
          if (orders.length > 0) setShipmentOrderNo(prev => prev || orders[0].order_no);
        }
      } catch (err) {
        if (!cancelled) setShipmentMessage("??謘潘?謘????剜??: " + err.message);
      } finally {
        if (!cancelled) setShipmentLoading(false);
      }
    }
    loadCatalog();
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function loadRecordEngineCatalog() {
      try {
        const response = await fetch("/api/record-engine/catalog");
        const payload = await response.json();
        if (!response.ok) throw new Error(payload.error || ("HTTP " + response.status));
        if (!cancelled) {
          const templates = payload.templates || [];
          setEngineCatalog(templates);
          if (templates.length > 0 && !templates.some(item => item.code === engineTemplateCode)) {
            setEngineTemplateCode(templates[0].code);
          }
        }
      } catch (err) {
        if (!cancelled) setEngineMessage("??航??????頦嫣??? " + err.message);
      }
    }
    loadRecordEngineCatalog();
    return () => { cancelled = true; };
  }, []);

  const [selectedAuditId, setSelectedAuditId] = useState("");

  useEffect(() => {
    if (!selectedNcId && safeNonConformances.length > 0) {
      setSelectedNcId(safeNonConformances[0].id);
    }
  }, [safeNonConformances, selectedNcId]);

  useEffect(() => {
    if (!selectedAuditId && safeAuditPlans.length > 0) {
      setSelectedAuditId(safeAuditPlans[0].id);
    }
  }, [safeAuditPlans, selectedAuditId]);

  const selectedOrder = shipmentOrders.find(item => item.order_no === shipmentOrderNo) || null;

  useEffect(() => {
    if (!selectedOrder) return;
    setShipmentForm({
      date: selectedOrder.ship_date_suggested || "",
      department: selectedOrder.department_suggested || "",
      requester: selectedOrder.requester_suggested || "",
      product_name: selectedOrder.product_name_suggested || selectedOrder.source_product || "",
      spec: selectedOrder.spec_suggested || "",
      quantity: selectedOrder.quantity_suggested || "",
      unit: selectedOrder.unit_suggested || "",
      remark: selectedOrder.remark_suggested || "",
      batch_display: selectedOrder.batch_display_suggested || selectedOrder.order_no,
    });
    setSelectedLots([]);
    setShipmentMessage("");
  }, [shipmentOrderNo]);

  function updateProdRecord(index, field, value) {
    setProdRecords(prev => prev.map((row, i) => {
      if (i !== index) return row;
      const next = { ...row, [field]: value };
      if (field === "input" || field === "good" || field === "defect") {
        const input = Number(field === "input" ? value : next.input) || 0;
        const good = Number(field === "good" ? value : next.good) || 0;
        next.yieldRate = input ? Number((good / input * 100).toFixed(1)) : "";
      }
      return next;
    }));
  }

  function updateQualityRecord(index, field, value) {
    setQualityRecords(prev => prev.map((row, i) => i === index ? { ...row, [field]: value } : row));
  }

  function addProdRecord() {
    setProdRecords(prev => prev.concat({ lot:"LOT-" + String(prev.length + 1).padStart(3, "0"), customer:"", product:"", input:0, good:0, defect:0, yieldRate:"", defectReasons:[], operator:"", note:"" }));
  }

  function addQualityRecord() {
    setQualityRecords(prev => prev.concat({ materialName:"", batchNo:"", quantity:"", spec:"", inspQty:"", ph:"", density:"", ri:"", rotation:"", result:"PASS", note:"" }));
  }

  async function loadExistingRecordData(kind) {
    const isProduction = kind === "production";
    const label = isProduction ? "?賹?鈭鼓" : "?蹓暸?潘???殉死?";
    if (!window.confirm(label + " ??????????嚗嗉???甽?殉此??謕??????秋撫??謘踐?????????)) return;
    setRecordReadBusy(kind);
    setMessage("");
    try {
      const response = await fetch(isProduction ? "/api/production-records/read-existing" : "/api/quality-records/read-existing");
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || ("HTTP " + response.status));
      const records = payload.records || [];
      if (isProduction) setProdRecords(records);
      else setQualityRecords(records);
      if (records.length === 0) {
        setMessage("?獢??????????穿?? + label + "??);
      } else {
        const shortPath = payload.source_file ? payload.source_file.split("\\").slice(-3).join("\\") : "";
        setMessage("????" + records.length + " ?? + label + (shortPath ? "?????" + shortPath : "??));
      }
    } catch (err) {
      setMessage("??? + label + "?剜???? + err.message);
    } finally {
      setRecordReadBusy("");
    }
  }

  async function importRecordFile(kind) {
    const isProduction = kind === "production";
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".xlsx,.xls";
    input.onchange = async () => {
      const file = input.files && input.files[0];
      if (!file) return;
      setRecordReadBusy(kind);
      setMessage("");
      try {
        const formData = new FormData();
        formData.append("file", file);
        const response = await fetch(
          isProduction ? "/api/production-records/import" : "/api/quality-records/import",
          { method: "POST", body: formData }
        );
        const payload = await response.json();
        if (!response.ok) throw new Error(payload.error || ("HTTP " + response.status));
        const records = payload.records || [];
        const label = isProduction ? "?賹?鈭鼓" : "?蹓暸?殉死?";
        if (!records.length) {
          setMessage("?謕" + label + "?????????穿????謕?);
          return;
        }
        const confirmed = window.confirm(
          "???? + (payload.source_file || file.name) + "???? " + records.length + " ????謕蹐彫??秋???蜃謕???穿???獢??蹓遴???寞???
        );
        if (!confirmed) {
          setMessage("????????選?????????穿???獢??蹓遴?????);
          return;
        }
        if (isProduction) setProdRecords(records);
        else setQualityRecords(records);
        setMessage("????" + records.length + " ?? + label + "???????" + (payload.source_file || file.name));
      } catch (err) {
        setMessage("??穿?剜???? + err.message);
      } finally {
        setRecordReadBusy("");
      }
    };
    input.click();
  }

  function buildEnginePayload(overrides = {}) {
    const selectedNc = safeNonConformances.find(item => item.id === selectedNcId) || safeNonConformances[0] || null;
    return {
      template_code: overrides.template_code || engineTemplateCode,
      prompt: overrides.prompt ?? enginePrompt,
      env_records: safeEnvRecords,
      prod_records: safeProdRecords,
      quality_records: safeQualityRecords,
      shipment_request: {
        order_no: shipmentOrderNo,
        selected_lots: selectedLots,
        ...shipmentForm,
      },
      nonconformance: selectedNc,
      all_nonconformances: safeNonConformances,
      audit_plans: safeAuditPlans,
      selected_audit_id: selectedAuditId,
    };
  }

  function applyEngineTemplatePreset(templateCode, prompt, messageText) {
    setEngineTemplateCode(templateCode);
    if (typeof prompt === "string") setEnginePrompt(prompt);
    setEngineSuggestions([]);
    setEnginePrecheck(null);
    if (messageText) setEngineMessage(messageText);
  }

  async function suggestRecordTemplates() {
    setEngineBusy(true);
    setEngineMessage("");
    setEnginePrecheck(null);
    try {
      const response = await fetch("/api/record-engine/suggest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: enginePrompt,
          context: {
            env_count: envRecords.length,
            prod_count: prodRecords.length,
            quality_count: qualityRecords.length,
            shipment_order_count: shipmentOrders.length,
            nonconformance_count: safeNonConformances.length,
          },
        }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || ("HTTP " + response.status));
      const templates = payload.templates || [];
      setEngineSuggestions(templates.slice(0, 4));
      if (templates.length > 0) {
        setEngineTemplateCode(templates[0].code);
        setEngineMessage("????獢???????謕????蹍????豰??);
      } else {
        setEngineMessage("?獢????????銵??豰??);
      }
    } catch (err) {
      setEngineMessage("????梁????: " + err.message);
    } finally {
      setEngineBusy(false);
    }
  }

  async function precheckRecordTemplate(overrides = null) {
    setEnginePrecheckBusy(true);
    setEngineMessage("");
    try {
      const response = await fetch("/api/record-engine/precheck", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildEnginePayload(overrides || {})),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || ("HTTP " + response.status));
      const result = payload.result || null;
      setEnginePrecheck(result);
      if (result && result.ready) {
        setEngineMessage("????堆??垓謆????謕?漲??賹??葩??);
      } else if (result) {
        setEngineMessage("????堆??奕???????????選???);
      } else {
        setEngineMessage("????堆???????謘??荒????);
      }
    } catch (err) {
      setEngineMessage("????剜??: " + err.message);
    } finally {
      setEnginePrecheckBusy(false);
    }
  }

  async function generateEngineRecord(overrides = null) {
    const effectiveTemplateCode = (overrides && overrides.template_code) || engineTemplateCode;
    if (!overrides && enginePrecheck && enginePrecheck.ready === false) {
      setEngineMessage("?獢?????對?萇??????????ｇ??????潘撕??謚??瞏汕?);
      return;
    }
    setEngineBusy(true);
    setEngineMessage("");
    try {
      const response = await fetch("/api/record-engine/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildEnginePayload(overrides || {})),
      });
      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(payload.error || ("HTTP " + response.status));
      }
      const selectedTemplate = engineCatalog.find(item => item.code === effectiveTemplateCode);
      const fallbackName = selectedTemplate ? (selectedTemplate.title + (selectedTemplate.bundle ? ".zip" : ".xlsx")) : "??????xlsx";
      downloadBlob(await response.blob(), fallbackName);
      setEngineMessage("????" + (selectedTemplate ? selectedTemplate.title : "??????) + "??);
    } catch (err) {
      setEngineMessage("?嚗??????? " + err.message);
    } finally {
      setEngineBusy(false);
    }
  }

  function jumpToMissingDetail(detail) {
    if (!detail || typeof window === "undefined") return;
    const focusField = (refObject) => {
      const el = refObject && refObject.current;
      if (!el) return false;
      el.focus();
      if (typeof el.scrollIntoView === "function") {
        el.scrollIntoView({ behavior: "smooth", block: "center" });
      }
      return true;
    };

    const scrollToRef = (refObject) => {
      const el = refObject && refObject.current;
      if (!el || typeof el.scrollIntoView !== "function") return false;
      el.scrollIntoView({ behavior: "smooth", block: "start" });
      return true;
    };

    if (detail.scope === "production") {
      scrollToRef(prodSectionRef);
      setEngineMessage("???選???賹?撖暑??????ｇ???骨??賹????);
      return;
    }
    if (detail.scope === "quality") {
      scrollToRef(qualitySectionRef);
      setEngineMessage("???選??????潘????????ｇ???骨??蹓暸????);
      return;
    }
    if (detail.scope === "shipment") {
      scrollToRef(shipmentSectionRef);
      const fieldRef = shipmentFieldRefs[detail.field_key];
      if (fieldRef) {
        setTimeout(() => focusField(fieldRef), 120);
      }
      setEngineMessage("???選???蝞?????葭??選?" + (detail.label || detail.field_key));
      return;
    }
    if (detail.scope === "nonconformance") {
      setActiveTab("nonconformance");
      const targetId = detail.item_id || selectedNcId;
      if (targetId) {
        setHighlightNcId(targetId);
        setExpandNcId?.(targetId);
      }
      setEngineMessage("???謜???瘜??????ｇ?????? + (detail.label || detail.field_key || "?對????") + "???);
      return;
    }
    if (detail.scope === "environment") {
      if (ENABLE_ENVIRONMENT_MODULE) {
        setActiveTab("environment");
        setEngineMessage("???謜??鼎?????????????????謆????謕?);
      } else {
        setActiveTab("production");
        setEngineMessage("??肅?謆????輯撒???????怎??????憳???賹?蹓???蹓賡??鞊???瘜????謕冪?０??);
      }
      return;
    }
    if (detail.scope === "audit_plans") {
      setActiveTab("auditplan");
      setEngineMessage("???謜??都赯梢????乾??? + (detail.label || detail.field_key || "?對????") + "???);
      return;
    }
  }

  async function downloadRecords(type, data, fallbackName) {
    setDownloadType(type);
    setMessage("");
    try {
      const response = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ type, data }),
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.error || ("HTTP " + response.status));
      }
      downloadBlob(await response.blob(), fallbackName);
      setMessage("?????" + fallbackName);
    } catch (err) {
      setMessage("????剜??: " + err.message);
    } finally {
      setDownloadType("");
    }
  }

  async function generateShipmentDraft() {
    if (!shipmentOrderNo) {
      setShipmentMessage("?ｇ???鞊??殉?謘??);
      return;
    }
    setShipmentBusy(true);
    setShipmentMessage("");
    try {
      const response = await fetch("/api/shipment-draft/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ order_no: shipmentOrderNo, selected_lots: selectedLots, ...shipmentForm }),
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.error || ("HTTP " + response.status));
      }
      downloadBlob(await response.blob(), shipmentOrderNo + "_?蝞??????xlsx");
      setShipmentMessage("???賹?謘??仿??);
    } catch (err) {
      setShipmentMessage("?蝞?????撒??賹??? " + err.message);
    } finally {
      setShipmentBusy(false);
    }
  }

  const prodIncomplete = safeProdRecords.filter(row => getProdRowIssues(row).length > 0).length;
  const qualityNg = safeQualityRecords.filter(row => ["NG", "FAIL"].includes(String(row?.result || "").toUpperCase())).length;
  const envWarning = safeEnvRecords.filter(row => row.result && row.result !== "??僱").length;

  const normalizeDateText = (value) => {
    const source = String(value || "").trim();
    if (!source) return "";
    const normalized = source.replace(/\//g, "-");
    const match = normalized.match(/(\d{4})-(\d{1,2})-(\d{1,2})/);
    if (match) {
      return `${match[1]}-${match[2].padStart(2, "0")}-${match[3].padStart(2, "0")}`;
    }
    return normalized;
  };

  const extractProdSite = (row) => {
    const note = String(row?.note || "");
    const siteMatch = note.match(/site\s*:\s*([a-z0-9_-]+)/i);
    if (siteMatch) return siteMatch[1].toUpperCase();
    const lot = String(row?.lot || "");
    const lotMatch = lot.match(/([A-Z]{2,5})$/);
    if (lotMatch) return lotMatch[1].toUpperCase();
    return "??詹菔謕?";
  };

  const getProdRowIssues = (row) => {
    const issues = [];
    if (!String(row?.lot || "").trim()) issues.push("?撖?");
    if (!String(row?.customer || "").trim()) issues.push("?堆撓??);
    if (!String(row?.product || "").trim()) issues.push("?嚗?");
    if (!(Number(row?.input) > 0)) issues.push("????);
    if (!String(row?.operator || "").trim()) issues.push("?遴鬥撟??);
    return issues;
  };

  const prodRows = safeProdRecords.map((row, index) => ({
    row,
    index,
    normalizedDate: normalizeDateText(row.date || row.recordDate || row.created_at || ""),
    site: extractProdSite(row),
  }));

  const prodSiteOptions = Array.from(new Set(prodRows.map(item => item.site))).sort((a, b) => a.localeCompare(b, "zh-Hant"));
  const prodDateOptions = Array.from(new Set(prodRows.map(item => item.normalizedDate).filter(Boolean))).sort();
  const prodSearchKeyword = prodSearch.trim().toLowerCase();
  const filteredProdRows = prodRows.filter(({ row, normalizedDate, site }) => {
    if ((prodStartDate || prodEndDate) && !normalizedDate) return false;
    if (prodStartDate && normalizedDate < prodStartDate) return false;
    if (prodEndDate && normalizedDate > prodEndDate) return false;
    if (prodSiteFilter !== "ALL" && site !== prodSiteFilter) return false;
    if (!prodSearchKeyword) return true;
    const haystack = [
      row.lot,
      row.customer,
      row.product,
      row.operator,
      row.note,
      site,
    ].join(" ").toLowerCase();
    return haystack.includes(prodSearchKeyword);
  });

  const prodGroups = filteredProdRows.reduce((acc, item) => {
    const dateLabel = item.normalizedDate || "??詹?鈭?";
    const key = `${dateLabel}__${item.site}`;
    if (!acc[key]) {
      acc[key] = {
        key,
        date: dateLabel,
        site: item.site,
        items: [],
        totalInput: 0,
        totalGood: 0,
        totalDefect: 0,
        issueCount: 0,
      };
    }
    acc[key].items.push(item);
    acc[key].totalInput += Number(item.row.input) || 0;
    acc[key].totalGood += Number(item.row.good) || 0;
    acc[key].totalDefect += Number(item.row.defect) || 0;
    acc[key].issueCount += getProdRowIssues(item.row).length > 0 ? 1 : 0;
    return acc;
  }, {});

  const prodGroupList = Object.values(prodGroups)
    .map(group => ({
      ...group,
      avgYield: group.totalInput ? Number(((group.totalGood / group.totalInput) * 100).toFixed(1)) : 0,
    }))
    .sort((a, b) => `${b.date} ${b.site}`.localeCompare(`${a.date} ${a.site}`));

  const latestProdDate = prodDateOptions.length ? prodDateOptions[prodDateOptions.length - 1] : "";

  const setProdPresetRange = (preset) => {
    if (!prodDateOptions.length) return;
    if (preset === "all") {
      setProdStartDate("");
      setProdEndDate("");
      return;
    }
    if (preset === "latest") {
      setProdStartDate(latestProdDate);
      setProdEndDate(latestProdDate);
      return;
    }
    const days = preset === "7d" ? 7 : 30;
    const latest = new Date(`${latestProdDate}T00:00:00`);
    if (Number.isNaN(latest.getTime())) return;
    const start = new Date(latest);
    start.setDate(start.getDate() - (days - 1));
    const fmt = (value) => {
      const year = value.getFullYear();
      const month = String(value.getMonth() + 1).padStart(2, "0");
      const day = String(value.getDate()).padStart(2, "0");
      return `${year}-${month}-${day}`;
    };
    setProdStartDate(fmt(start));
    setProdEndDate(latestProdDate);
  };

  const toggleProdGroup = (key) => {
    setExpandedProdGroups(prev => ({ ...prev, [key]: !(prev[key] ?? false) }));
  };

  const toggleAllProdGroups = (expanded) => {
    const next = {};
    prodGroupList.forEach(group => {
      next[group.key] = expanded;
    });
    setExpandedProdGroups(next);
  };

  const getQualityRowIssues = (row) => {
    const issues = [];
    if (!String(row?.materialName || "").trim()) issues.push("??????");
    if (!String(row?.batchNo || "").trim()) issues.push("?撖?");
    if (!String(row?.spec || "").trim()) issues.push("?秋赯?);
    if (!String(row?.result || "").trim()) issues.push("?荒??");
    return issues;
  };

  const qualityRows = safeQualityRecords.map((row, index) => ({
    row,
    index,
    materialName: String(row.materialName || "??詹???").trim() || "??詹???",
    resultLabel: String(row.result || "??賂???).trim() || "??賂???,
    normalizedResult: (String(row.result || "").trim() || "??賂???).toUpperCase(),
  }));

  const qualitySearchKeyword = qualitySearch.trim().toLowerCase();
  const normalizedQualityFilter = String(qualityResultFilter || "ALL").toUpperCase();
  const filteredQualityRows = qualityRows.filter(({ row, materialName, resultLabel, normalizedResult }) => {
    if (normalizedQualityFilter !== "ALL" && normalizedResult !== normalizedQualityFilter) return false;
    if (!qualitySearchKeyword) return true;
    const haystack = [
      materialName,
      row.batchNo,
      row.spec,
      row.note,
      resultLabel,
    ].join(" ").toLowerCase();
    return haystack.includes(qualitySearchKeyword);
  });

  const qualityGroups = filteredQualityRows.reduce((acc, item) => {
    if (!acc[item.materialName]) {
      acc[item.materialName] = {
        key: item.materialName,
        materialName: item.materialName,
        items: [],
        ngCount: 0,
        issueCount: 0,
      };
    }
    acc[item.materialName].items.push(item);
    if (["NG", "FAIL"].includes(item.resultLabel.toUpperCase())) acc[item.materialName].ngCount += 1;
    if (getQualityRowIssues(item.row).length > 0) acc[item.materialName].issueCount += 1;
    return acc;
  }, {});

  const qualityGroupList = Object.values(qualityGroups).sort((a, b) => a.materialName.localeCompare(b.materialName, "zh-Hant"));
  const filteredQualityNg = filteredQualityRows.filter(item => ["NG", "FAIL"].includes(item.resultLabel.toUpperCase())).length;

  const toggleQualityGroup = (key) => {
    setExpandedQualityGroups(prev => ({ ...prev, [key]: !(prev[key] ?? false) }));
  };

  const toggleAllQualityGroups = (expanded) => {
    const next = {};
    qualityGroupList.forEach(group => {
      next[group.key] = expanded;
    });
    setExpandedQualityGroups(next);
  };

  const getShipmentFormIssues = () => {
    const issues = [];
    if (!String(shipmentForm.date || "").trim()) issues.push("?鈭?");
    if (!String(shipmentForm.department || "").trim()) issues.push("???");
    if (!String(shipmentForm.requester || "").trim()) issues.push("?????);
    if (!String(shipmentForm.product_name || "").trim()) issues.push("?嚗?");
    if (!String(shipmentForm.quantity || "").trim()) issues.push("?鞈?");
    return issues;
  };

  const shipmentIssues = getShipmentFormIssues();
  const shipmentSuggestions = [];
  if (!String(shipmentForm.spec || "").trim()) shipmentSuggestions.push("?秋赯?);
  if (!String(shipmentForm.unit || "").trim()) shipmentSuggestions.push("?獢?");
  if (!String(shipmentForm.batch_display || "").trim()) shipmentSuggestions.push("?殉?謘?? / ?撖??輯???);
  const shipmentLots = selectedOrder && Array.isArray(selectedOrder.lots) ? selectedOrder.lots : [];
  const selectedLotCount = selectedLots.length;
  const shipmentSummaryCardStyle = {
    background: "rgba(15,23,42,0.72)",
    border: "1px solid rgba(167,139,250,0.18)",
    borderRadius: 14,
    boxShadow: "0 16px 36px rgba(15,23,42,0.16)",
    padding: 14,
  };
  const selectedEngineTemplate = engineCatalog.find(item => item.code === engineTemplateCode) || null;
  const managementReviewPrompt = "?ｇ????肅?謆????賹?蹓???蹓賡??鞎???瘜????謕??嚗? 16 ?????貔?蹓???倦?;
  const completedAuditCount = safeAuditPlans.filter(item => ["????, "?堆?", "Closed"].includes(String(item.status || "").trim())).length;
  const openNonConformanceCount = safeNonConformances.filter(item => !["????, "????, "Closed"].includes(String(item.status || "").trim())).length;
  const latestEnvRecordDate = safeEnvRecords.reduce((latest, item) => {
    const value = String(item.date || "").trim();
    return value && value > latest ? value : latest;
  }, "");
  const latestProdRecordDate = safeProdRecords.reduce((latest, item) => {
    const value = String(item.date || "").trim();
    return value && value > latest ? value : latest;
  }, "");
  const latestQualityRecordDate = safeQualityRecords.reduce((latest, item) => {
    const value = String(item.date || item.inspectDate || item.createdDate || "").trim();
    return value && value > latest ? value : latest;
  }, "");
  const managementReviewSources = [
    { label: "?賹?撖暑", value: safeProdRecords.length, color: "#38bdf8", sub: latestProdRecordDate ? "??擗謑??" + formatDate(latestProdRecordDate) : "?垮謓舫???謘??嚗賃??? },
    { label: "????潘??", value: safeQualityRecords.length, color: "#22c55e", sub: latestQualityRecordDate ? "??擗謑??" + formatDate(latestQualityRecordDate) : "?垮謓舫???謘????? },
    { label: "?都赯梢?", value: safeAuditPlans.length, color: "#a78bfa", sub: completedAuditCount > 0 ? "????" + completedAuditCount + " ?? : "?垓????都赯? },
    { label: "??瘜??, value: safeNonConformances.length, color: "#f97316", sub: openNonConformanceCount > 0 ? "?綽?剝?" + openNonConformanceCount + " ?? : "?獢????擗釭擐? },
  ].filter(Boolean);

  return (
    <div>
      <PageIntro
        eyebrow="QMS Record Workspace"
        title="?殉死???穿"
        description="?謕??蹓????????嚗肅蹓????蝞??鞈??殉死??蹇???剛?????謘踐???方縣???謕?????箸??蹓鳴??蝬??謘餅摹?航﹝??????????蝞?????葩??
        actions={
          <>
            <button onClick={() => downloadRecords("production", prodRecords, "?賹?殉死?.xlsx")} disabled={downloadType !== ""} style={buttonStyle("primary", downloadType !== "" && downloadType !== "production")}>{downloadType === "production" ? "?????.." : "????賹?殉死?"}</button>
            <button onClick={() => downloadRecords("quality", qualityRecords, "?蹓暸?潘???殉死?.xlsx")} disabled={downloadType !== ""} style={buttonStyle("success", downloadType !== "" && downloadType !== "quality")}>{downloadType === "quality" ? "?????.." : "????蹓暸?潘???殉死?"}</button>
          </>
        }
      >
        <div style={{ display:"flex", gap:12, flexWrap:"wrap" }}>
          <StatCard label="?賹?殉死?" value={safeProdRecords.length} color="#38bdf8" sub={prodIncomplete > 0 ? prodIncomplete + " ?摮??鬥??? : "??????} />
          <StatCard label="????潘??" value={safeQualityRecords.length} color="#22c55e" sub={qualityNg > 0 ? qualityNg + " ?撖抆?? : "??賂??僱"} />
        </div>
        {message && <div style={{ marginTop:14, fontSize:12, color:"#bae6fd" }}>{message}</div>}
      </PageIntro>

      <div ref={prodSectionRef}>
      <Panel
        title="?賹?撖暑"
        description="????鈭??蹓??綜筆??謚殷?殉??祆?????????????鈭??嚗賂???蹇???剛???謘踐?????嚗賃???蹓鳴??鈭止??澗?????皝??箏?冽?綽??蝞??嚗????
        accent="#38bdf8"
        actions={
          <>
            <button onClick={() => loadExistingRecordData("production")} disabled={recordReadBusy !== ""} style={buttonStyle("secondary", recordReadBusy !== "" && recordReadBusy !== "production")}>{recordReadBusy === "production" ? "??謘餉?..." : "??謘踐?????嚗賃???}</button>
            <button onClick={() => importRecordFile("production")} disabled={recordReadBusy !== ""} style={buttonStyle("secondary", recordReadBusy !== "" && recordReadBusy !== "production")}>{recordReadBusy === "production" ? "??穿??.." : "??穿?賹?鈭鼓"}</button>
            <button onClick={addProdRecord} style={buttonStyle("primary")}>?????/button>
          </>
        }
        style={{ marginBottom: 20 }}
      >
        <div style={{ display:"grid", gridTemplateColumns:"repeat(4, minmax(180px, 1fr))", gap:12, marginBottom:14 }}>
          <div>
            <div style={{ fontSize:12, color:"#94a3b8", marginBottom:6 }}>????鈭?</div>
            <input type="date" value={prodStartDate} onChange={e => setProdStartDate(e.target.value)} style={inputStyle} />
          </div>
          <div>
            <div style={{ fontSize:12, color:"#94a3b8", marginBottom:6 }}>?荒???鈭?</div>
            <input type="date" value={prodEndDate} onChange={e => setProdEndDate(e.target.value)} style={inputStyle} />
          </div>
          <div>
            <div style={{ fontSize:12, color:"#94a3b8", marginBottom:6 }}>?∵??</div>
            <select value={prodSiteFilter} onChange={e => setProdSiteFilter(e.target.value)} style={inputStyle}>
              <option value="ALL">??賂貉謕?</option>
              {prodSiteOptions.map(site => <option key={site} value={site}>{site}</option>)}
            </select>
          </div>
          <div>
            <div style={{ fontSize:12, color:"#94a3b8", marginBottom:6 }}>?謚殷??/div>
            <input value={prodSearch} onChange={e => setProdSearch(e.target.value)} placeholder="???????貔螞蹓餅??蹓踐?蹓嗽蹓??綜等??遴鬥撟?? style={inputStyle} />
          </div>
        </div>

        <div style={{ display:"flex", gap:8, flexWrap:"wrap", marginBottom:14 }}>
          <button onClick={() => setProdPresetRange("latest")} style={buttonStyle("secondary")}>???????/button>
          <button onClick={() => setProdPresetRange("7d")} style={buttonStyle("secondary")}>??擗?7 ??/button>
          <button onClick={() => setProdPresetRange("30d")} style={buttonStyle("secondary")}>??擗?30 ??/button>
          <button onClick={() => setProdPresetRange("all")} style={buttonStyle("secondary")}>?謒?鈭?</button>
          <button onClick={() => toggleAllProdGroups(true)} style={buttonStyle("secondary")}>??賂豢???</button>
          <button onClick={() => toggleAllProdGroups(false)} style={buttonStyle("secondary")}>??賂???</button>
        </div>

        <div style={{ display:"flex", gap:10, flexWrap:"wrap", marginBottom:16 }}>
          <Badge color="#38bdf8">{filteredProdRows.length} ???駁謘???/Badge>
          <Badge color="#22c55e">{prodGroupList.length} ?????/ ?∵???Ｘ?</Badge>
          <Badge color={filteredProdRows.filter(item => getProdRowIssues(item.row).length > 0).length > 0 ? "#f59e0b" : "#22c55e"}>
            {filteredProdRows.filter(item => getProdRowIssues(item.row).length > 0).length} ????鬥???
          </Badge>
        </div>

        <div style={{ display:"flex", flexDirection:"column", gap:14 }}>
          {prodGroupList.length === 0 && (
            <div style={{ ...tableShellStyle, padding:18, color:"#94a3b8", fontSize:13 }}>
              ?獢????????剜?蹓?豲麾????嚗??謕蹇???剛????皝??貔螞蹓??綜等??謚殷?殉不??謘???謘踐?????嚗賃????
            </div>
          )}

          {prodGroupList.map(group => (
            <div key={group.key} style={{ ...tableShellStyle, overflow:"hidden" }}>
              <div style={{ display:"flex", justifyContent:"space-between", gap:12, flexWrap:"wrap", alignItems:"center", padding:"14px 16px", borderBottom:"1px solid rgba(255,255,255,0.06)" }}>
                <div>
                  <div style={{ fontSize:18, fontWeight:800, color:"#e2e8f0" }}>{group.date} / {group.site}</div>
                  <div style={{ fontSize:12, color:"#94a3b8", marginTop:4 }}>
                    {group.items.length} ????? {group.totalInput}??????皜∵?
                  </div>
                </div>
                <div style={{ display:"flex", gap:8, flexWrap:"wrap", alignItems:"center" }}>
                  {group.issueCount > 0 && <Badge color="#f59e0b">{group.issueCount} ????鬥???/Badge>}
                  <button onClick={() => toggleProdGroup(group.key)} style={buttonStyle("secondary")}>
                    {(expandedProdGroups[group.key] ?? true) ? "?????" : "????"}
                  </button>
                </div>
              </div>

              {(expandedProdGroups[group.key] ?? true) && (
                <div style={{ overflowX:"auto" }}>
                  <table style={{ width:"100%", borderCollapse:"collapse", minWidth:900 }}>
                    <thead><tr>{["?撖?","?堆撓??,"?嚗?","????,"?????,"?????,"????賹?","?遴鬥撟??,"?謕?",""].map(head => <th key={head} style={tableHeadCellStyle}>{head}</th>)}</tr></thead>
                    <tbody>
                      {group.items.map(({ row, index }) => {
                        const issues = getProdRowIssues(row);
                        const issueSet = new Set(issues);
                        const flaggedStyle = (label) => issueSet.has(label)
                          ? { ...inputStyle, borderColor:"rgba(245,158,11,0.55)", background:"rgba(245,158,11,0.08)" }
                          : inputStyle;
                        return (
                          <tr key={(row.lot || "LOT") + "-" + index}>
                            <td style={tableRowCellStyle}><input value={row.lot} onChange={e => updateProdRecord(index, "lot", e.target.value)} style={flaggedStyle("?撖?")} /></td>
                            <td style={tableRowCellStyle}><input value={row.customer} onChange={e => updateProdRecord(index, "customer", e.target.value)} style={flaggedStyle("?堆撓??)} /></td>
                            <td style={tableRowCellStyle}><input value={row.product} onChange={e => updateProdRecord(index, "product", e.target.value)} style={flaggedStyle("?嚗?")} /></td>
                            <td style={tableRowCellStyle}><input type="number" value={row.input} onChange={e => updateProdRecord(index, "input", e.target.value)} style={flaggedStyle("????)} /></td>
                            <td style={tableRowCellStyle}><input type="number" value={row.good} onChange={e => updateProdRecord(index, "good", e.target.value)} style={inputStyle} /></td>
                            <td style={tableRowCellStyle}><input type="number" value={row.defect} onChange={e => updateProdRecord(index, "defect", e.target.value)} style={inputStyle} /></td>
                            <td style={tableRowCellStyle}><input value={Array.isArray(row.defectReasons) ? row.defectReasons.join(", ") : row.defectReasons} onChange={e => updateProdRecord(index, "defectReasons", e.target.value.split(/[;,]/).map(item => item.trim()).filter(Boolean))} style={inputStyle} /></td>
                            <td style={tableRowCellStyle}><input value={row.operator} onChange={e => updateProdRecord(index, "operator", e.target.value)} style={flaggedStyle("?遴鬥撟??)} /></td>
                            <td style={tableRowCellStyle}><input value={row.note} onChange={e => updateProdRecord(index, "note", e.target.value)} style={inputStyle} /></td>
                            <td style={tableRowCellStyle}>
                              <div style={{ display:"flex", flexDirection:"column", gap:6, alignItems:"flex-start" }}>
                                <button onClick={() => setProdRecords(prev => prev.filter((_, i) => i !== index))} style={buttonStyle("danger")}>??畸?</button>
                                {issues.length > 0 && <span style={{ fontSize:11, color:"#fcd34d" }}>?綽??爸issues.join(" / ")}</span>}
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          ))}
        </div>
      </Panel>
      </div>

      <div ref={qualitySectionRef}>
      <Panel
        title="????潘??"
        description="????謚殷?殉???荒???格???哨?????鈭??伍????謕??潘???荒???蹇???剛???謘踐????????蹓鳴??鈭止??澗?????皝??高?瞉???穿??
        accent="#22c55e"
        actions={
          <>
            <button onClick={() => loadExistingRecordData("quality")} disabled={recordReadBusy !== ""} style={buttonStyle("secondary", recordReadBusy !== "" && recordReadBusy !== "quality")}>{recordReadBusy === "quality" ? "??謘餉?..." : "??謘踐????????}</button>
            <button onClick={() => importRecordFile("quality")} disabled={recordReadBusy !== ""} style={buttonStyle("secondary", recordReadBusy !== "" && recordReadBusy !== "quality")}>{recordReadBusy === "quality" ? "??穿??.." : "??穿?蹓暸?殉死?"}</button>
            <button onClick={addQualityRecord} style={buttonStyle("success")}>?????/button>
          </>
        }
        style={{ marginBottom: 20 }}
      >
        <div style={{ display:"grid", gridTemplateColumns:"minmax(240px, 2fr) minmax(180px, 1fr)", gap:12, marginBottom:14 }}>
          <div>
            <div style={{ fontSize:12, color:"#94a3b8", marginBottom:6 }}>?謚殷??/div>
            <input value={qualitySearch} onChange={e => setQualitySearch(e.target.value)} placeholder="???????謕????蹓潘?貔螞蹓??瞏??荒??" style={inputStyle} />
          </div>
          <div>
            <div style={{ fontSize:12, color:"#94a3b8", marginBottom:6 }}>?荒??</div>
            <select value={qualityResultFilter} onChange={e => setQualityResultFilter(e.target.value)} style={inputStyle}>
              <option value="ALL">??賂貉??</option>
              <option value="PASS">PASS</option>
              <option value="NG">NG</option>
              <option value="FAIL">FAIL</option>
            </select>
          </div>
        </div>

        <div style={{ display:"flex", gap:8, flexWrap:"wrap", marginBottom:14 }}>
          <button onClick={() => setQualitySearch("")} style={buttonStyle("secondary")}>?謒?謚殷??/button>
          <button onClick={() => setQualityResultFilter("ALL")} style={buttonStyle("secondary")}>??賂貉??</button>
          <button onClick={() => toggleAllQualityGroups(true)} style={buttonStyle("secondary")}>??賂豢???</button>
          <button onClick={() => toggleAllQualityGroups(false)} style={buttonStyle("secondary")}>??賂???</button>
        </div>

        <div style={{ display:"flex", gap:10, flexWrap:"wrap", marginBottom:16 }}>
          <Badge color="#22c55e">{filteredQualityRows.length} ???謅???/Badge>
          <Badge color="#38bdf8">{qualityGroupList.length} ????謕???/Badge>
          <Badge color={filteredQualityNg > 0 ? "#ef4444" : "#22c55e"}>{filteredQualityNg} ???芣?/Badge>
        </div>

        <div style={{ display:"flex", flexDirection:"column", gap:14 }}>
          {qualityGroupList.length === 0 && (
            <div style={{ ...tableShellStyle, padding:18, color:"#94a3b8", fontSize:13 }}>
              ?獢????????剜?蹓?豲麾?????謅??謕蹇???剛????皝????????謚??謘???謘踐?????????
            </div>
          )}

          {qualityGroupList.map(group => (
            <div key={group.key} style={{ ...tableShellStyle, overflow:"hidden" }}>
              <div style={{ display:"flex", justifyContent:"space-between", gap:12, flexWrap:"wrap", alignItems:"center", padding:"14px 16px", borderBottom:"1px solid rgba(255,255,255,0.06)" }}>
                <div>
                  <div style={{ fontSize:18, fontWeight:800, color:"#e2e8f0" }}>{group.materialName}</div>
                  <div style={{ fontSize:12, color:"#94a3b8", marginTop:4 }}>
                    {group.items.length} ?????∟????? {group.ngCount} ??
                  </div>
                </div>
                <div style={{ display:"flex", gap:8, flexWrap:"wrap", alignItems:"center" }}>
                  {group.issueCount > 0 && <Badge color="#f59e0b">{group.issueCount} ????鬥???/Badge>}
                  <Badge color={group.ngCount > 0 ? "#ef4444" : "#22c55e"}>{group.ngCount > 0 ? "??伍?? : "?獢?????}</Badge>
                  <button onClick={() => toggleQualityGroup(group.key)} style={buttonStyle("secondary")}>
                    {(expandedQualityGroups[group.key] ?? true) ? "?????" : "????"}
                  </button>
                </div>
              </div>

              {(expandedQualityGroups[group.key] ?? true) && (
                <div style={{ overflowX:"auto" }}>
                  <table style={{ width:"100%", borderCollapse:"collapse", minWidth:1080 }}>
                    <thead><tr>{["??????","?撖?","?鞈?","?秋赯?,"?潘???鞈?","PH","?伍??","RI","?????,"?荒??","?謕?",""].map(head => <th key={head} style={tableHeadCellStyle}>{head}</th>)}</tr></thead>
                    <tbody>
                      {group.items.map(({ row, index }) => {
                        const issues = getQualityRowIssues(row);
                        const issueSet = new Set(issues);
                        const flaggedStyle = (label) => issueSet.has(label)
                          ? { ...inputStyle, borderColor:"rgba(245,158,11,0.55)", background:"rgba(245,158,11,0.08)" }
                          : inputStyle;
                        return (
                          <tr key={(row.batchNo || row.materialName || "QUALITY") + "-" + index}>
                            <td style={tableRowCellStyle}><input value={row.materialName} onChange={e => updateQualityRecord(index, "materialName", e.target.value)} style={flaggedStyle("??????")} /></td>
                            <td style={tableRowCellStyle}><input value={row.batchNo} onChange={e => updateQualityRecord(index, "batchNo", e.target.value)} style={flaggedStyle("?撖?")} /></td>
                            <td style={tableRowCellStyle}><input value={row.quantity} onChange={e => updateQualityRecord(index, "quantity", e.target.value)} style={inputStyle} /></td>
                            <td style={tableRowCellStyle}><input value={row.spec} onChange={e => updateQualityRecord(index, "spec", e.target.value)} style={flaggedStyle("?秋赯?)} /></td>
                            <td style={tableRowCellStyle}><input value={row.inspQty} onChange={e => updateQualityRecord(index, "inspQty", e.target.value)} style={inputStyle} /></td>
                            <td style={tableRowCellStyle}><input value={row.ph} onChange={e => updateQualityRecord(index, "ph", e.target.value)} style={inputStyle} /></td>
                            <td style={tableRowCellStyle}><input value={row.density} onChange={e => updateQualityRecord(index, "density", e.target.value)} style={inputStyle} /></td>
                            <td style={tableRowCellStyle}><input value={row.ri} onChange={e => updateQualityRecord(index, "ri", e.target.value)} style={inputStyle} /></td>
                            <td style={tableRowCellStyle}><input value={row.rotation} onChange={e => updateQualityRecord(index, "rotation", e.target.value)} style={inputStyle} /></td>
                            <td style={tableRowCellStyle}><input value={row.result} onChange={e => updateQualityRecord(index, "result", e.target.value)} style={flaggedStyle("?荒??")} /></td>
                            <td style={tableRowCellStyle}><input value={row.note} onChange={e => updateQualityRecord(index, "note", e.target.value)} style={inputStyle} /></td>
                            <td style={tableRowCellStyle}>
                              <div style={{ display:"flex", flexDirection:"column", gap:6, alignItems:"flex-start" }}>
                                <button onClick={() => setQualityRecords(prev => prev.filter((_, i) => i !== index))} style={buttonStyle("danger")}>??畸?</button>
                                {issues.length > 0 && <span style={{ fontSize:11, color:"#fcd34d" }}>?綽??爸issues.join(" / ")}</span>}
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          ))}
        </div>
      </Panel>
      </div>

      <div ref={shipmentSectionRef}>
      <Panel
        title="?蝞?????撒???
        description="????????? LOT ???嚗瘀 14.3 ?蝞?????葩?蹇謕????????????謕???蹓鳴???????
        accent="#a78bfa"
        actions={<Badge color="#a78bfa">{shipmentLoading ? "??舫?? : shipmentOrders.length + " ?????}</Badge>}
      >

        <div style={{ display:"flex", gap:8, flexWrap:"wrap", marginBottom:14 }}>
          <Badge color="#a78bfa">{shipmentOrderNo ? "?蹓蹇?" : "?垮謓?鞎???}</Badge>
          <Badge color="#38bdf8">{shipmentLots.length} ????LOT</Badge>
          <Badge color="#14b8a6">{selectedLotCount} ?????賃? LOT</Badge>
          <Badge color={shipmentIssues.length ? "#f97316" : "#22c55e"}>{shipmentIssues.length ? shipmentIssues.length + " ??????? : "?對?萇????堆??}</Badge>
        </div>

        {selectedOrder && (
          <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(180px, 1fr))", gap:12, marginBottom:14 }}>
            <div style={shipmentSummaryCardStyle}>
              <div style={{ fontSize:11, letterSpacing:1.1, color:"#c4b5fd", marginBottom:6 }}>?獢??殉?謘?/div>
              <div style={{ fontSize:16, fontWeight:700, color:"#f5f3ff" }}>{selectedOrder.order_no}</div>
              <div style={{ fontSize:12, color:"#cbd5e1", marginTop:4 }}>{selectedOrder.product_name_suggested || selectedOrder.source_product || "??賃?????}</div>
            </div>
            <div style={shipmentSummaryCardStyle}>
              <div style={{ fontSize:11, letterSpacing:1.1, color:"#c4b5fd", marginBottom:6 }}>?梁???蝞?</div>
              <div style={{ fontSize:16, fontWeight:700, color:"#f5f3ff" }}>{selectedOrder.ship_date_suggested || "?????}</div>
              <div style={{ fontSize:12, color:"#cbd5e1", marginTop:4 }}>?鞈? {selectedOrder.quantity_suggested || "?????} {selectedOrder.unit_suggested || ""}</div>
            </div>
            <div style={shipmentSummaryCardStyle}>
              <div style={{ fontSize:11, letterSpacing:1.1, color:"#c4b5fd", marginBottom:6 }}>??????</div>
              <div style={{ fontSize:13, color:shipmentIssues.length ? "#fdba74" : "#86efac", fontWeight:600 }}>
                {shipmentIssues.length ? "?綽??? + shipmentIssues.join(" / ") : "?對?萇???????}
              </div>
              {shipmentSuggestions.length > 0 && (
                <div style={{ fontSize:12, color:"#cbd5e1", marginTop:6 }}>?梁???謚??爸shipmentSuggestions.join(" / ")}</div>
              )}
            </div>
          </div>
        )}

        <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(220px, 1fr))", gap:12 }}>
          <div>
            <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>?殉?謘?/div>
            <select value={shipmentOrderNo} onChange={e => setShipmentOrderNo(e.target.value)} style={inputStyle}>
              <option value="">?ｇ蹓?????/option>
              {shipmentOrders.map(item => <option key={item.order_no} value={item.order_no}>{item.order_no} - {item.product_name_suggested || item.source_product || "??賃???}</option>)}
            </select>
          </div>
          <div><div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>?鈭?</div><input ref={shipmentFieldRefs.date} type="date" value={shipmentForm.date} onChange={e => setShipmentForm(prev => ({ ...prev, date:e.target.value }))} style={{ ...inputStyle, borderColor: shipmentIssues.includes("?鈭?") ? "rgba(249,115,22,0.8)" : inputStyle.borderColor }} /></div>
          <div><div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>???</div><input ref={shipmentFieldRefs.department} value={shipmentForm.department} onChange={e => setShipmentForm(prev => ({ ...prev, department:e.target.value }))} style={{ ...inputStyle, borderColor: shipmentIssues.includes("???") ? "rgba(249,115,22,0.8)" : inputStyle.borderColor }} /></div>
          <div><div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>?????/div><input ref={shipmentFieldRefs.requester} value={shipmentForm.requester} onChange={e => setShipmentForm(prev => ({ ...prev, requester:e.target.value }))} style={{ ...inputStyle, borderColor: shipmentIssues.includes("?????) ? "rgba(249,115,22,0.8)" : inputStyle.borderColor }} /></div>
          <div><div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>?嚗?</div><input ref={shipmentFieldRefs.product_name} value={shipmentForm.product_name} onChange={e => setShipmentForm(prev => ({ ...prev, product_name:e.target.value }))} style={{ ...inputStyle, borderColor: shipmentIssues.includes("?嚗?") ? "rgba(249,115,22,0.8)" : inputStyle.borderColor }} /></div>
          <div><div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>?秋赯?/div><input ref={shipmentFieldRefs.spec} value={shipmentForm.spec} onChange={e => setShipmentForm(prev => ({ ...prev, spec:e.target.value }))} style={{ ...inputStyle, borderColor: shipmentSuggestions.includes("?秋赯?) ? "rgba(56,189,248,0.45)" : inputStyle.borderColor }} /></div>
          <div><div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>?鞈?</div><input ref={shipmentFieldRefs.quantity} value={shipmentForm.quantity} onChange={e => setShipmentForm(prev => ({ ...prev, quantity:e.target.value }))} style={{ ...inputStyle, borderColor: shipmentIssues.includes("?鞈?") ? "rgba(249,115,22,0.8)" : inputStyle.borderColor }} /></div>
          <div><div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>?獢?</div><input ref={shipmentFieldRefs.unit} value={shipmentForm.unit} onChange={e => setShipmentForm(prev => ({ ...prev, unit:e.target.value }))} style={{ ...inputStyle, borderColor: shipmentSuggestions.includes("?獢?") ? "rgba(56,189,248,0.45)" : inputStyle.borderColor }} /></div>
        </div>

        <div style={{ marginTop:12 }}>
          <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>?殉?謘?? / ?撖??輯???/div>
          <input ref={shipmentFieldRefs.batch_display} value={shipmentForm.batch_display} onChange={e => setShipmentForm(prev => ({ ...prev, batch_display:e.target.value }))} style={{ ...inputStyle, borderColor: shipmentSuggestions.includes("?殉?謘?? / ?撖??輯???) ? "rgba(56,189,248,0.45)" : inputStyle.borderColor }} />
        </div>

        {selectedOrder && selectedOrder.lots && selectedOrder.lots.length > 0 && (
          <div style={{ marginTop:14 }}>
            <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:8 }}>?撖??謘?/div>
            <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
              {selectedOrder.lots.map(item => {
                const checked = selectedLots.includes(item.lot);
                return (
                  <label key={item.lot} style={{ display:"flex", alignItems:"center", gap:6, background:checked?"rgba(167,139,250,0.18)":"rgba(255,255,255,0.05)", border:"1px solid " + (checked ? "rgba(167,139,250,0.45)" : "rgba(255,255,255,0.12)"), borderRadius:999, padding:"6px 12px", cursor:"pointer", fontSize:12, color:"#e9d5ff" }}>
                    <input type="checkbox" checked={checked} onChange={e => setSelectedLots(prev => e.target.checked ? [...prev, item.lot] : prev.filter(lot => lot !== item.lot))} />
                    <span>{item.lot}</span>
                  </label>
                );
              })}
            </div>
          </div>
        )}

        <div style={{ marginTop:14 }}>
          <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>?謕?</div>
          <textarea value={shipmentForm.remark} onChange={e => setShipmentForm(prev => ({ ...prev, remark:e.target.value }))} style={{ ...inputStyle, minHeight:84, resize:"vertical" }} />
        </div>

        <div style={{ display:"flex", gap:10, alignItems:"center", flexWrap:"wrap", marginTop:16 }}>
          <button onClick={generateShipmentDraft} disabled={shipmentBusy || shipmentLoading || !shipmentOrderNo} style={{ background:"linear-gradient(135deg,#7c3aed,#8b5cf6)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"10px 16px", fontSize:13, fontWeight:700, opacity:(shipmentBusy || shipmentLoading || !shipmentOrderNo) ? 0.6 : 1 }}>{shipmentBusy ? "?嚗???.." : "?嚗??蝞??????}</button>
          {shipmentMessage && <div style={{ fontSize:12, color:"#ddd6fe" }}>{shipmentMessage}</div>}
        </div>
      </Panel>

      <Panel
        title="?????????
        description="????豰∪?????踐????????賹?蹓???蹓鳴????瘜????謕?蝞??葩?蹇謕?????漸???抵??瞏冪?陷???? AI ?叟??????????
        accent="#fb923c"
        actions={<Badge color="#fb923c">{engineCatalog.length} ?????/Badge>}
        style={{ marginTop: 20 }}
      >

        <div style={{ display:"flex", gap:8, flexWrap:"wrap", marginBottom:14 }}>
          <Badge color="#f97316">1. ?岳?????/Badge>
          <Badge color="#fb923c">2. ?鞊Ｚ???/Badge>
          <Badge color="#38bdf8">3. ????鈭行??/Badge>
          <Badge color="#22c55e">4. ?嚗???仿</Badge>
        </div>

        <div style={{ display:"flex", gap:8, flexWrap:"wrap", marginBottom:14 }}>
          <button
            onClick={() => applyEngineTemplatePreset("management_review_pack", managementReviewPrompt, "???謜??????貔?蹓?????梁??????鈭行????)}
            style={{ background:engineTemplateCode === "management_review_pack" ? "rgba(34,197,94,0.22)" : "rgba(255,255,255,0.06)", border:"1px solid rgba(34,197,94,0.24)", borderRadius:999, color:"#dcfce7", cursor:"pointer", padding:"6px 12px", fontSize:12, fontWeight:700 }}
          >
            ?????貔?伐?鈭
          </button>
          <button
            onClick={() => applyEngineTemplatePreset("audit_pack", "?ｇ???獢??都赯梢??嚗???貉?鞈?僚?謍船???軋??潘撕?????謕?, "???謜??都赯梁?蹓???倦?)}
            style={{ background:engineTemplateCode === "audit_pack" ? "rgba(59,130,246,0.22)" : "rgba(255,255,255,0.06)", border:"1px solid rgba(59,130,246,0.24)", borderRadius:999, color:"#dbeafe", cursor:"pointer", padding:"6px 12px", fontSize:12, fontWeight:700 }}
          >
            ?都赯梁?蹓???
          </button>
          <button
            onClick={() => applyEngineTemplatePreset("cip_pack", "?ｇ???獢???瘜????謕??CIP ??????????謢???, "???謜? CIP / ??瘜????????)}
            style={{ background:engineTemplateCode === "cip_pack" ? "rgba(249,115,22,0.22)" : "rgba(255,255,255,0.06)", border:"1px solid rgba(249,115,22,0.24)", borderRadius:999, color:"#ffedd5", cursor:"pointer", padding:"6px 12px", fontSize:12, fontWeight:700 }}
          >
            CIP / ??瘜???
          </button>
        </div>

        <div style={{ display:"grid", gridTemplateColumns:"1.3fr 1fr", gap:12, alignItems:"end" }}>
          <div>
            <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>???????/div>
            <textarea value={enginePrompt} onChange={e => setEnginePrompt(e.target.value)} placeholder="????奕???踐??????謕?賹?????????謘???瘜????謕??? CIP ???? style={{ ...inputStyle, minHeight:80, resize:"vertical" }} />
          </div>
          <div>
            <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>?豰?/div>
            <select value={engineTemplateCode} onChange={e => setEngineTemplateCode(e.target.value)} style={inputStyle}>
              {engineCatalog.map(item => <option key={item.code} value={item.code}>{item.title}</option>)}
            </select>
          </div>
        </div>

        {selectedEngineTemplate && (
          <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(180px, 1fr))", gap:12, marginTop:14 }}>
            <div style={{ ...shipmentSummaryCardStyle, borderColor:"rgba(249,115,22,0.18)" }}>
              <div style={{ fontSize:11, letterSpacing:1.1, color:"#fdba74", marginBottom:6 }}>?獢??豰?/div>
              <div style={{ fontSize:16, fontWeight:700, color:"#fff7ed" }}>{selectedEngineTemplate.title}</div>
              <div style={{ fontSize:12, color:"#cbd5e1", marginTop:4 }}>{selectedEngineTemplate.description}</div>
            </div>
            <div style={{ ...shipmentSummaryCardStyle, borderColor:"rgba(56,189,248,0.18)" }}>
              <div style={{ fontSize:11, letterSpacing:1.1, color:"#7dd3fc", marginBottom:6 }}>?岳????</div>
              <div style={{ fontSize:16, fontWeight:700, color:"#e0f2fe" }}>{selectedEngineTemplate.bundle ? "?播???/ ZIP" : "?獢??萄謘?/ XLSX"}</div>
              <div style={{ fontSize:12, color:"#cbd5e1", marginTop:4 }}>{selectedEngineTemplate.bundle ? "???????蝞??陪?????? : "??堊?賹????????豰?}</div>
            </div>
          </div>
        )}

        {engineTemplateCode === "management_review_pack" && (
          <div style={{ marginTop:14, padding:16, borderRadius:14, background:"linear-gradient(135deg, rgba(15,118,110,0.18), rgba(30,41,59,0.92))", border:"1px solid rgba(45,212,191,0.22)" }}>
            <div style={{ display:"flex", justifyContent:"space-between", gap:12, flexWrap:"wrap", alignItems:"center" }}>
              <div>
                <div style={{ fontSize:15, fontWeight:700, color:"#ccfbf1" }}>??肅??????鈭??謕?</div>
                <div style={{ fontSize:12, color:"#cbd5e1", marginTop:4 }}>?謕????????????貔螞?潭????鈭交??鈭??秋撕?????潭????鈭斗?????????憳??遴??????蹓??鬥餈斗??喳?閰鄞?/div>
              </div>
              <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
                <button onClick={() => precheckRecordTemplate({ template_code: "management_review_pack", prompt: managementReviewPrompt })} disabled={engineBusy || enginePrecheckBusy} style={{ background:"linear-gradient(135deg,#0f766e,#14b8a6)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"10px 14px", fontSize:12, fontWeight:700, opacity:(engineBusy || enginePrecheckBusy) ? 0.6 : 1 }}>????鈭行????鈭???/button>
                <button onClick={() => generateEngineRecord({ template_code: "management_review_pack", prompt: managementReviewPrompt })} disabled={engineBusy} style={{ background:"linear-gradient(135deg,#047857,#22c55e)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"10px 14px", fontSize:12, fontWeight:700, opacity:engineBusy ? 0.6 : 1 }}>?皝??嚗??????貔??/button>
              </div>
            </div>

            <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(180px, 1fr))", gap:12, marginTop:14 }}>
              {managementReviewSources.map(item => (
                <div key={item.label} style={{ ...shipmentSummaryCardStyle, borderColor:"rgba(45,212,191,0.16)", background:"rgba(15,23,42,0.56)" }}>
                  <div style={{ fontSize:11, letterSpacing:1.1, color:item.color, marginBottom:6 }}>{item.label}</div>
                  <div style={{ fontSize:24, fontWeight:800, color:"#f8fafc" }}>{item.value}</div>
                  <div style={{ fontSize:12, color:"#cbd5e1", marginTop:6 }}>{item.sub}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {engineSuggestions.length > 0 && (
          <div style={{ display:"flex", gap:8, flexWrap:"wrap", marginTop:12 }}>
            {engineSuggestions.map(item => (
              <button key={item.code} onClick={() => setEngineTemplateCode(item.code)} style={{ background:item.code === engineTemplateCode ? "rgba(249,115,22,0.22)" : "rgba(255,255,255,0.06)", border:"1px solid rgba(249,115,22,0.24)", borderRadius:999, color:"#ffedd5", cursor:"pointer", padding:"6px 12px", fontSize:12 }}>
                {item.title}
              </button>
            ))}
          </div>
        )}

        {engineTemplateCode === "cip_152" && (
          <div style={{ marginTop:12 }}>
            <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>??瘜?????/div>
            <select value={selectedNcId} onChange={e => setSelectedNcId(e.target.value)} style={inputStyle}>
              {safeNonConformances.map(item => <option key={item.id} value={item.id}>{item.id} - {item.description}</option>)}
            </select>
          </div>
        )}

        {(engineTemplateCode === "audit_notice" || engineTemplateCode === "audit_pack") && (
          <div style={{ marginTop:12 }}>
            <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>?鞊??都赯梢?</div>
            {safeAuditPlans.length === 0
              ? <div style={{ fontSize:12, color:"#ef4444" }}>???垓??鞈?僚?殷??仿?????????潮??鞎??????????/div>
              : <select value={selectedAuditId} onChange={e => setSelectedAuditId(e.target.value)} style={inputStyle}>
                  {safeAuditPlans.map(item => (
                    <option key={item.id} value={item.id}>
                      {item.id}?砭item.year} {item.period}?砭item.dept}?砭item.auditor} ??{item.auditee}
                    </option>
                  ))}
                </select>
            }
          </div>
        )}

        <div style={{ display:"flex", gap:10, alignItems:"center", flexWrap:"wrap", marginTop:16 }}>
          <button onClick={suggestRecordTemplates} disabled={engineBusy} style={{ background:"linear-gradient(135deg,#b45309,#f97316)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"10px 16px", fontSize:13, fontWeight:700, opacity:engineBusy ? 0.6 : 1 }}>{engineBusy ? "?????.." : "????梁????伍瓷"}</button>
          <button onClick={precheckRecordTemplate} disabled={engineBusy || enginePrecheckBusy || !engineTemplateCode} style={{ background:"linear-gradient(135deg,#0369a1,#0ea5e9)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"10px 16px", fontSize:13, fontWeight:700, opacity:(engineBusy || enginePrecheckBusy || !engineTemplateCode) ? 0.6 : 1 }}>{enginePrecheckBusy ? "?潘撓貔??.." : "????鈭行??}</button>
          <button onClick={generateEngineRecord} disabled={engineBusy || !engineTemplateCode} style={{ background:"linear-gradient(135deg,#c2410c,#ea580c)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"10px 16px", fontSize:13, fontWeight:700, opacity:(engineBusy || !engineTemplateCode) ? 0.6 : 1 }}>{engineBusy ? "?嚗???.." : "?嚗???????}</button>
          {engineMessage && <div style={{ fontSize:12, color:"#ffedd5" }}>{engineMessage}</div>}
        </div>

        {enginePrecheck && (
          <div style={{ marginTop:16, padding:16, borderRadius:14, background:"rgba(15,23,42,0.72)", border:"1px solid rgba(249,115,22,0.16)" }}>
            <div style={{ display:"flex", gap:8, flexWrap:"wrap", alignItems:"center", marginBottom:12 }}>
              <Badge color={enginePrecheck.ready ? "#22c55e" : "#f97316"}>{enginePrecheck.ready ? "????鈭佇?? : "???????}</Badge>
              <Badge color="#38bdf8">{(enginePrecheck.missing_items || []).length} ??????/Badge>
              <Badge color="#f59e0b">{(enginePrecheck.warnings || []).length} ?????/Badge>
            </div>

            <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(180px, 1fr))", gap:12 }}>
              <div>
                <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>?????</div>
                <div style={{ fontSize:13, color:"#e2e8f0", lineHeight:1.8 }}>
                  ?賹?爸enginePrecheck.source_counts?.prod_records || 0} ??br />
                  ?蹓暸?爸enginePrecheck.source_counts?.quality_records || 0} ??br />
                  ?蝞??爸enginePrecheck.source_counts?.shipment || 0} ??br />
                  ??瘜???{enginePrecheck.source_counts?.all_nonconformances || enginePrecheck.source_counts?.nonconformance || 0} ??br />
                  ?都赯梢??爸enginePrecheck.source_counts?.audit_plans || 0} ??
                </div>
              </div>
              <div>
                <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>?餌?????</div>
                {(enginePrecheck.missing_details || []).length ? (
                  <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
                    {enginePrecheck.missing_details.map((detail, index) => (
                      <button
                        key={(detail.scope || "scope") + "-" + (detail.field_key || "field") + "-" + index}
                        onClick={() => jumpToMissingDetail(detail)}
                        style={{ background:"rgba(249,115,22,0.12)", border:"1px solid rgba(249,115,22,0.24)", borderRadius:999, color:"#ffedd5", cursor:"pointer", padding:"6px 10px", fontSize:12 }}
                      >
                        {detail.scope_label ? detail.scope_label + "?? : ""}{detail.label || detail.field_key}
                      </button>
                    ))}
                  </div>
                ) : (
                  <div style={{ fontSize:13, color:"#86efac", lineHeight:1.8 }}>?獢?????對?菔蝞</div>
                )}
              </div>
              <div>
                <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>?????伍瓷</div>
                <div style={{ fontSize:13, color:"#e2e8f0", lineHeight:1.8 }}>
                  {enginePrecheck.bundle && (enginePrecheck.included_templates || []).length
                    ? enginePrecheck.included_templates.map(item => item.title).join(" / ")
                    : (enginePrecheck.downstream_templates || []).length
                      ? enginePrecheck.downstream_templates.map(item => item.title).join(" / ")
                      : "????叟◆??悻???}
                </div>
              </div>
            </div>

            {(enginePrecheck.warnings || []).length > 0 && (
              <div style={{ marginTop:12 }}>
                <div style={{ fontSize:12, color:"#cbd5e1", marginBottom:6 }}>???</div>
                <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
                  {enginePrecheck.warnings.map((item, index) => (
                    <span key={index} style={{ fontSize:12, color:"#ffedd5", background:"rgba(249,115,22,0.12)", border:"1px solid rgba(249,115,22,0.18)", borderRadius:999, padding:"6px 10px" }}>
                      {item}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </Panel>
      </div>
    </div>
  );
}

