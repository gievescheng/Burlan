function EquipmentTab({ equipment, setEquipment }) {
  const [search, setSearch] = useState("");
  const [locationFilter, setLocationFilter] = useState("ALL");
  const [modalType, setModalType] = useState("");
  const [selectedEquipment, setSelectedEquipment] = useState(null);
  const [equipmentDraft, setEquipmentDraft] = useState({ id:"", name:"", location:"", owner:"", intervalDays:"", vendor:"", model:"", nextItems:"", note:"" });
  const [maintenanceDraft, setMaintenanceDraft] = useState({ date:"", operator:"", remark:"", items:"" });
  const [busy, setBusy] = useState("");
  const [message, setMessage] = useState("");

  const enriched = equipment.map(eq => {
    const nextDate = getEquipmentNextMaintenanceDate(eq);
    const days = daysUntil(nextDate);
    return { ...eq, nextDate, days };
  }).sort((a,b) => a.days-b.days);
  const locationOptions = Array.from(new Set(equipment.map(item => item.location).filter(Boolean))).sort((a, b) => a.localeCompare(b, "zh-Hant"));
  const filtered = enriched.filter(item => {
    const matchesLocation = locationFilter === "ALL" || item.location === locationFilter;
    const keyword = search.trim().toLowerCase();
    const matchesSearch = !keyword || [item.id, item.name, item.location, item.owner, item.vendor, item.model].some(value => String(value || "").toLowerCase().includes(keyword));
    return matchesLocation && matchesSearch;
  });
  const historyCount = equipment.reduce((sum, item) => sum + (item.maintenanceHistory || []).length, 0);

  function resetEquipmentDraft(record = null) {
    setEquipmentDraft(record ? {
      id: record.id || "",
      name: record.name || "",
      location: record.location || "",
      owner: record.owner || "",
      intervalDays: String(record.intervalDays || ""),
      vendor: record.vendor || "",
      model: record.model || "",
      nextItems: (record.nextItems || []).join("\n"),
      note: record.note || "",
    } : { id:"", name:"", location:"", owner:"", intervalDays:"", vendor:"", model:"", nextItems:"", note:"" });
  }

  function resetMaintenanceDraft(record) {
    setMaintenanceDraft({
      date: new Date().toISOString().split("T")[0],
      operator: "",
      remark: "",
      items: (record?.nextItems || []).join("\n"),
    });
  }

  async function saveEquipmentRecord(record, successText) {
    setBusy("save-equipment");
    setMessage("");
    try {
      const payload = await apiJson("/api/equipment-records", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ record }),
      });
      setEquipment(payload.items || []);
      setMessage(successText);
    } catch (err) {
      setMessage("靽?閮剖?鞈?憭望?嚗? + err.message);
    } finally {
      setBusy("");
    }
  }

  async function saveEquipmentInfo() {
    if (!equipmentDraft.id.trim() || !equipmentDraft.name.trim()) {
      setMessage("隢?憛怠神閮剖?蝺刻???蝔晞?);
      return;
    }
    const previous = equipment.find(item => item.id === equipmentDraft.id) || { maintenanceHistory: [] };
    await saveEquipmentRecord(
      {
        ...previous,
        ...equipmentDraft,
        intervalDays: Number(equipmentDraft.intervalDays || 0),
        nextMaintenance: previous.lastMaintenance
          ? addDays(previous.lastMaintenance, Number(equipmentDraft.intervalDays || 0))
          : "",
        nextItems: equipmentDraft.nextItems.split(/\r?\n/).map(item => item.trim()).filter(Boolean),
        maintenanceHistory: previous.maintenanceHistory || [],
      },
      previous.id ? "撌脫?啗身???? : "撌脫憓身??
    );
    setModalType("");
    setSelectedEquipment(null);
    resetEquipmentDraft();
  }

  async function saveMaintenanceRecord() {
    if (!selectedEquipment) return;
    if (!maintenanceDraft.date) {
      setMessage("隢?憛怠神靽??交???);
      return;
    }
    const historyEntry = {
      id: `${selectedEquipment.id}-M${Date.now()}`,
      date: maintenanceDraft.date,
      operator: maintenanceDraft.operator,
      remark: maintenanceDraft.remark,
      items: maintenanceDraft.items.split(/\r?\n/).map(item => item.trim()).filter(Boolean),
    };
    await saveEquipmentRecord(
      {
        ...selectedEquipment,
        lastMaintenance: maintenanceDraft.date,
        nextMaintenance: addDays(maintenanceDraft.date, Number(selectedEquipment.intervalDays || 0)),
        status: "甇?虜",
        maintenanceHistory: [historyEntry, ...(selectedEquipment.maintenanceHistory || [])],
      },
      "撌脖?摮身??擗???
    );
    setModalType("");
    setSelectedEquipment(null);
  }

  async function deleteEquipment(recordId) {
    if (!window.confirm("蝣箏?閬?日閮剖???")) return;
    setBusy("delete-equipment");
    setMessage("");
    try {
      const encodedId = encodeURIComponent(recordId);
      const payload = await apiDeleteWithFallback(`/api/equipment-records/${encodedId}`, `/api/equipment-records/${encodedId}/delete`);
      setEquipment(payload.items || []);
      setMessage("撌脣?方身????);
    } catch (err) {
      setMessage("?芷閮剖?憭望?嚗? + err.message);
    } finally {
      setBusy("");
    }
  }
  return (
    <div>
      <SectionHeader title="閮剖?靽?餈質馱" count={equipment.length} color="#fb923c" />
    <ModuleStatusBanner
        title="?桀??嚗???迤撘?皞???
        tone="system"
        message="???歇?湔霈????8 閮剜閮剖?蝞∠?蝔??身??閬質”??擗???雿憭憓?鋆??擗摰嫣???摮蝟餌絞嚗靘踹?蝥蕭頩扎?
      />
      <div style={{ display:"flex", gap:8, flexWrap:"wrap", alignItems:"center", marginBottom: 16 }}>
        <button onClick={() => { resetEquipmentDraft(); setSelectedEquipment(null); setModalType("equipment"); }} style={{ background:"linear-gradient(135deg,#ea580c,#f97316)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"9px 16px", fontSize:13, fontWeight:700 }}>?啣?閮剖?</button>
        {message && <div style={{ fontSize:12, color:"#fed7aa" }}>{message}</div>}
      </div>
      <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
        <StatCard label="?暹?靽?" value={enriched.filter(e=>e.days<0).length} color="#ef4444" />
        <StatCard label="?祆??唳?" value={enriched.filter(e=>e.days>=0&&e.days<=30).length} color="#f97316" />
        <StatCard label="甇?虜" value={enriched.filter(e=>e.days>30).length} color="#22c55e" />
        <StatCard label="靽?蝝???? value={historyCount} color="#60a5fa" />
      </div>
      <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(180px, 1fr))", gap:12, marginBottom: 16 }}>
        <div>
          <div style={{ fontSize:12, color:"#94a3b8", marginBottom:6 }}>雿蔭</div>
          <select value={locationFilter} onChange={e => setLocationFilter(e.target.value)} style={inputStyle}>
            <option value="ALL">?券雿蔭</option>
            {locationOptions.map(item => <option key={item} value={item}>{item}</option>)}
          </select>
        </div>
        <div>
          <div style={{ fontSize:12, color:"#94a3b8", marginBottom:6 }}>??</div>
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="?舀?撠身?楊??蝔晞?蝵柴?鞎砌犖" style={inputStyle} />
        </div>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {filtered.map(eq => (
          <div key={eq.id} style={{ background: urgencyBg(eq.days), border: `1px solid ${urgencyColor(eq.days)}33`, borderRadius: 12, padding: "16px 18px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap", marginBottom: 10 }}>
              <div style={{ flex: 1, minWidth: 200 }}><div style={{ fontWeight: 700, color: "#e2e8f0", fontSize: 14 }}>{eq.name}</div><div style={{ fontSize: 12, color: "#64748b", marginTop: 2 }}>{eq.id} 繚 {eq.location} 繚 瘥?{eq.intervalDays} 憭拐?擗?甈﹃eq.owner ? ` 繚 鞎痊 ${eq.owner}` : ""}</div></div>
              <div style={{ textAlign: "right", minWidth: 120 }}><div style={{ fontSize: 12, color: "#64748b" }}>銝活靽?</div><div style={{ fontWeight: 700, color: "#e2e8f0" }}>{formatDate(eq.nextDate)}</div></div>
              <Badge color={urgencyColor(eq.days)}>{urgencyLabel(eq.days)}</Badge>
              <button onClick={() => { setSelectedEquipment(eq); resetMaintenanceDraft(eq); setModalType("maintenance"); }} style={{ background: "rgba(255,255,255,0.08)", border: "1px solid rgba(255,255,255,0.15)", borderRadius: 8, color: "#94a3b8", cursor: "pointer", padding: "6px 14px", fontSize: 12 }}>閮?靽?</button>
              <button onClick={() => { setSelectedEquipment(eq); resetEquipmentDraft(eq); setModalType("equipment"); }} style={{ background: "rgba(255,255,255,0.08)", border: "1px solid rgba(255,255,255,0.15)", borderRadius: 8, color: "#cbd5e1", cursor: "pointer", padding: "6px 14px", fontSize: 12 }}>靽格閮剖?</button>
              {eq.sourceSystem !== "burlan_equipment_records" && (
                <button onClick={() => deleteEquipment(eq.id)} disabled={busy !== ""} style={{ background:"rgba(239,68,68,0.14)", border:"1px solid rgba(239,68,68,0.28)", borderRadius:8, color:"#fca5a5", cursor:"pointer", padding:"6px 14px", fontSize:12, opacity:busy ? 0.7 : 1 }}>?芷</button>
              )}
            </div>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <span style={{ fontSize: 11, color: "#64748b", fontWeight: 600 }}>靽??嚗?/span>
              {(eq.nextItems || []).map((item,i) => (<span key={i} style={{ fontSize: 11, background: "rgba(251,146,60,0.1)", color: "#fb923c", borderRadius: 6, padding: "2px 8px", border: "1px solid rgba(251,146,60,0.2)" }}>{item}</span>))}
            </div>
            {(eq.maintenanceHistory || []).length > 0 && <div style={{ marginTop:10, fontSize:12, color:"#cbd5e1" }}>?餈?擗?{formatDate(eq.maintenanceHistory[0]?.date)}{eq.maintenanceHistory[0]?.operator ? ` 繚 ${eq.maintenanceHistory[0].operator}` : ""}{eq.maintenanceHistory[0]?.remark ? ` 繚 ${eq.maintenanceHistory[0].remark}` : ""}</div>}
          </div>
        ))}
        {filtered.length === 0 && <div style={{ textAlign:"center", padding:"24px 18px", color:"#64748b", background:"rgba(255,255,255,0.03)", borderRadius:12 }}>?桀?瘝?蝚血?璇辣?身??/div>}
      </div>
      {modalType === "maintenance" && selectedEquipment && (
        <Modal title={`閮?靽?摰?嚗?{selectedEquipment.name}`} onClose={() => { setModalType(""); setSelectedEquipment(null); }}>
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div>
              <div style={{ fontSize: 12, color: "#64748b", marginBottom: 6 }}>靽?摰??交?</div>
              <input type="date" value={maintenanceDraft.date} onChange={e => setMaintenanceDraft({ ...maintenanceDraft, date:e.target.value })} style={inputStyle} />
            </div>
            <div>
              <div style={{ fontSize: 12, color: "#64748b", marginBottom: 6 }}>?瑁?鈭箏</div>
              <input value={maintenanceDraft.operator} onChange={e => setMaintenanceDraft({ ...maintenanceDraft, operator:e.target.value })} style={inputStyle} />
            </div>
            <div>
              <div style={{ fontSize: 12, color: "#64748b", marginBottom: 6 }}>?祆活靽??嚗?銵???</div>
              <textarea value={maintenanceDraft.items} onChange={e => setMaintenanceDraft({ ...maintenanceDraft, items:e.target.value })} style={{ ...inputStyle, minHeight:88, resize:"vertical" }} />
            </div>
            <div>
              <div style={{ fontSize: 12, color: "#64748b", marginBottom: 6 }}>?酉</div>
              <textarea value={maintenanceDraft.remark} onChange={e => setMaintenanceDraft({ ...maintenanceDraft, remark:e.target.value })} style={{ ...inputStyle, minHeight:72, resize:"vertical" }} />
            </div>
            <div style={{ background: "rgba(251,146,60,0.1)", borderRadius: 8, padding: 12 }}>
              <div style={{ fontSize: 12, color: "#fb923c", fontWeight: 600, marginBottom: 8 }}>?湔敺?甈∩?擗</div>
              <div style={{ color: "#fed7aa", fontSize: 16, fontWeight: 700 }}>{formatDate(addDays(maintenanceDraft.date, Number(selectedEquipment.intervalDays || 0)))}</div>
            </div>
            <button onClick={saveMaintenanceRecord} disabled={busy !== ""} style={{ background: "linear-gradient(135deg, #ea580c, #f97316)", border: "none", borderRadius: 10, color: "#fff", cursor: "pointer", padding: "12px 24px", fontSize: 15, fontWeight: 700, opacity:busy ? 0.7 : 1 }}>{busy === "save-equipment" ? "靽?銝?.." : "蝣箄?靽?摰?"}</button>
          </div>
        </Modal>
      )}
      {modalType === "equipment" && (
        <Modal title={selectedEquipment ? `靽格閮剖?嚗?{selectedEquipment.name}` : "?啣?閮剖?"} onClose={() => { setModalType(""); setSelectedEquipment(null); }}>
          <div style={{ display:"flex", flexDirection:"column", gap:12 }}>
            {[["閮剖?蝺刻?","id","text"],["閮剖??迂","name","text"],["雿蔭","location","text"],["鞎痊鈭?,"owner","text"],["靽??望?嚗予嚗?,"intervalDays","number"],["撱?","vendor","text"],["??","model","text"]].map(([label,field,type]) => (
              <div key={field}>
                <div style={{ fontSize:12, color:"#64748b", marginBottom:5 }}>{label}</div>
                <input type={type} value={equipmentDraft[field]} onChange={e => setEquipmentDraft({ ...equipmentDraft, [field]: e.target.value })} style={inputStyle} disabled={selectedEquipment && field === "id"} />
              </div>
            ))}
            <div>
              <div style={{ fontSize:12, color:"#64748b", marginBottom:5 }}>靽??嚗?銵???</div>
              <textarea value={equipmentDraft.nextItems} onChange={e => setEquipmentDraft({ ...equipmentDraft, nextItems:e.target.value })} style={{ ...inputStyle, minHeight:88, resize:"vertical" }} />
            </div>
            <div>
              <div style={{ fontSize:12, color:"#64748b", marginBottom:5 }}>?酉</div>
              <textarea value={equipmentDraft.note} onChange={e => setEquipmentDraft({ ...equipmentDraft, note:e.target.value })} style={{ ...inputStyle, minHeight:72, resize:"vertical" }} />
            </div>
            <button onClick={saveEquipmentInfo} disabled={busy !== ""} style={{ background:"linear-gradient(135deg,#ea580c,#f97316)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"12px 24px", fontSize:15, fontWeight:700, marginTop:8, opacity:busy ? 0.7 : 1 }}>{busy === "save-equipment" ? "靽?銝?.." : "蝣箄?靽?"}</button>
          </div>
        </Modal>
      )}
    </div>
  );
}

// ??? SUPPLIER TAB (MP-10) ????????????????????????????????????????????????????
function SupplierTab({ suppliers, setSuppliers }) {
  const [modalType, setModalType] = useState("");
  const [selectedSupplier, setSelectedSupplier] = useState(null);
  const [supplierDraft, setSupplierDraft] = useState({ id:"", name:"", category:"", contact:"", lastEvalDate:"", evalScore:"90", evalIntervalDays:"365", note:"" });
  const [evalDraft, setEvalDraft] = useState({ date:"", score:"90", operator:"", remark:"", issues:"" });
  const [busy, setBusy] = useState("");
  const [message, setMessage] = useState("");
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("ALL");
  const enriched = suppliers.map(s => {
    const nextEvalDate = addDays(s.lastEvalDate, s.evalIntervalDays);
    const days = daysUntil(nextEvalDate);
    return { ...s, nextEvalDate, days };
  }).sort((a,b) => a.days-b.days);
  const categoryOptions = Array.from(new Set(suppliers.map(item => item.category).filter(Boolean))).sort((a, b) => a.localeCompare(b, "zh-Hant"));
  const filtered = enriched.filter(item => {
    const matchesCategory = categoryFilter === "ALL" || item.category === categoryFilter;
    const keyword = search.trim().toLowerCase();
    const matchesSearch = !keyword || [item.id, item.name, item.category, item.contact].some(value => String(value || "").toLowerCase().includes(keyword));
    return matchesCategory && matchesSearch;
  });
  const historyCount = suppliers.reduce((sum, item) => sum + (item.evalHistory || []).length, 0);

  function evaluationResult(score) {
    const numeric = parseInt(score, 10) || 0;
    return numeric >= 90 ? "?芾" : numeric >= 80 ? "?" : numeric >= 70 ? "璇辣?" : "銝???;
  }

  function resetSupplierDraft(record = null) {
    setSupplierDraft(record ? {
      id: record.id || "",
      name: record.name || "",
      category: record.category || "",
      contact: record.contact || "",
      lastEvalDate: record.lastEvalDate || "",
      evalScore: String(getSupplierScore(record) || 90),
      evalIntervalDays: String(record.evalIntervalDays || 365),
      note: record.note || "",
    } : { id:"", name:"", category:"", contact:"", lastEvalDate:"", evalScore:"90", evalIntervalDays:"365", note:"" });
  }

  function resetEvalDraft(record) {
    setEvalDraft({
      date: new Date().toISOString().split("T")[0],
      score: String(getSupplierScore(record) || 90),
      operator: "",
      remark: "",
      issues: (record?.issues || []).join("\n"),
    });
  }

  async function saveSupplierRecord(record, successText) {
    setBusy("save-supplier");
    setMessage("");
    try {
      const payload = await apiJson("/api/supplier-records", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ record }),
      });
      setSuppliers(payload.items || []);
      setMessage(successText);
    } catch (err) {
      setMessage("靽?靘????仃??" + err.message);
    } finally {
      setBusy("");
    }
  }

  async function saveSupplierInfo() {
    if (!supplierDraft.id.trim() || !supplierDraft.name.trim()) {
      setMessage("隢?憛怠神靘??楊???迂??);
      return;
    }
    const score = parseInt(supplierDraft.evalScore, 10) || 0;
    const previous = suppliers.find(item => item.id === supplierDraft.id) || { evalHistory: [], issues: [] };
    await saveSupplierRecord(
      {
        ...previous,
        ...supplierDraft,
        lastEvalDate: supplierDraft.lastEvalDate || previous.lastEvalDate || "",
        evalScore: score,
        evalResult: evaluationResult(score),
        evalIntervalDays: Number(supplierDraft.evalIntervalDays || 365),
        evalHistory: previous.evalHistory || [],
      },
      previous.id ? "撌脫?唬???鞈??? : "撌脫憓?????
    );
    setModalType("");
    setSelectedSupplier(null);
    resetSupplierDraft();
  }

  async function saveEvaluation() {
    if (!selectedSupplier) return;
    if (!evalDraft.date) {
      setMessage("隢?憛怠神閰??交???);
      return;
    }
    const score = parseInt(evalDraft.score, 10) || 0;
    const issues = evalDraft.issues.split(/\r?\n/).map(item => item.trim()).filter(Boolean);
    const historyEntry = {
      id: `${selectedSupplier.id}-E${Date.now()}`,
      date: evalDraft.date,
      score,
      result: evaluationResult(score),
      operator: evalDraft.operator,
      remark: evalDraft.remark,
      issues,
    };
    await saveSupplierRecord(
      {
        ...selectedSupplier,
        lastEvalDate: evalDraft.date,
        evalScore: score,
        evalResult: evaluationResult(score),
        issues,
        evalHistory: [historyEntry, ...(selectedSupplier.evalHistory || [])],
      },
      "撌脖?摮???閰???
    );
    setModalType("");
    setSelectedSupplier(null);
  }

  async function deleteSupplier(recordId) {
    if (!window.confirm("蝣箏?閬?日振靘???嚗?)) return;
    setBusy("delete-supplier");
    setMessage("");
    try {
      const encodedId = encodeURIComponent(recordId);
      const payload = await apiDeleteWithFallback(`/api/supplier-records/${encodedId}`, `/api/supplier-records/${encodedId}/delete`);
      setSuppliers(payload.items || []);
      setMessage("撌脣?支???鞈???);
    } catch (err) {
      setMessage("?芷靘??仃??" + err.message);
    } finally {
      setBusy("");
    }
  }

  const scoreColor = s => s>=90?"#22c55e":s>=80?"#60a5fa":s>=70?"#eab308":"#ef4444";
  return (
    <div>
      <SectionHeader title="靘????恣??MP-12嚗? count={suppliers.length} color="#06b6d4" />
   <ModuleStatusBanner
        title="?桀??嚗???迤撘?皞???
        tone="system"
        message="???歇?湔霈????僑摨虫???皛踵?摨行??株? 12.2 靘????”嚗??血??啣????餌?閰??批捆銋?靽??啁頂蝯晞?
      />
      <div style={{ display:"flex", gap:8, flexWrap:"wrap", alignItems:"center", marginBottom: 16 }}>
        <button onClick={() => { resetSupplierDraft(); setSelectedSupplier(null); setModalType("supplier"); }} style={{ background:"linear-gradient(135deg,#0891b2,#06b6d4)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"9px 16px", fontSize:13, fontWeight:700 }}>?啣?靘???/button>
        {message && <div style={{ fontSize:12, color:"#bae6fd" }}>{message}</div>}
      </div>
      <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
        <StatCard label="靘??蜇?? value={suppliers.length} color="#06b6d4" />
        <StatCard label="?芾" value={enriched.filter(s=>s.evalResult==="?芾").length} color="#22c55e" />
        <StatCard label="璇辣?" value={enriched.filter(s=>s.evalResult==="璇辣?").length} color="#eab308" />
        <StatCard label="閰??暹?" value={enriched.filter(s=>s.days<0).length} color="#ef4444" />
        <StatCard label="閰?甇瑞?蝑" value={historyCount} color="#60a5fa" />
      </div>
      <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(180px, 1fr))", gap:12, marginBottom: 16 }}>
        <div>
          <div style={{ fontSize:12, color:"#94a3b8", marginBottom:6 }}>憿</div>
          <select value={categoryFilter} onChange={e => setCategoryFilter(e.target.value)} style={inputStyle}>
            <option value="ALL">?券憿</option>
            {categoryOptions.map(item => <option key={item} value={item}>{item}</option>)}
          </select>
        </div>
        <div>
          <div style={{ fontSize:12, color:"#94a3b8", marginBottom:6 }}>??</div>
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="?舀?撠???蝺刻???蝔晞??乓蝯∩犖" style={inputStyle} />
        </div>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {filtered.map(s => (
          <div key={s.id} style={{ background: urgencyBg(s.days), border: `1px solid ${urgencyColor(s.days)}33`, borderRadius: 12, padding: "16px 18px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap", marginBottom: s.issues.length>0?10:0 }}>
              <div style={{ flex: 1, minWidth: 200 }}>
                <div style={{ fontWeight: 700, color: "#e2e8f0", fontSize: 14 }}>{s.name}</div>
                <div style={{ fontSize: 12, color: "#64748b", marginTop: 2 }}>{s.id} 繚 {s.category} 繚 ?舐窗鈭綽?{s.contact || "?芸‵"}</div>
              </div>
              <div style={{ textAlign: "right", minWidth: 90 }}>
                    <div style={{ fontSize: 24, fontWeight: 800, color: scoreColor(getSupplierScore(s)), fontFamily: "monospace" }}>{getSupplierScore(s)}</div>
                <div style={{ fontSize: 11, color: "#64748b" }}>??/div>
              </div>
              <Badge color={s.evalResult==="?芾"?"#22c55e":s.evalResult==="?"?"#60a5fa":s.evalResult==="璇辣?"?"#eab308":"#ef4444"}>{s.evalResult}</Badge>
              <div style={{ textAlign: "right", minWidth: 120 }}>
                <div style={{ fontSize: 12, color: "#64748b" }}>銝活閰?</div>
                <div style={{ fontWeight: 700, color: "#e2e8f0", fontSize: 13 }}>{formatDate(s.nextEvalDate)}</div>
              </div>
              <Badge color={urgencyColor(s.days)}>{urgencyLabel(s.days)}</Badge>
              <button onClick={() => { setSelectedSupplier(s); resetEvalDraft(s); setModalType("evaluation"); }} style={{ background: "rgba(255,255,255,0.08)", border: "1px solid rgba(255,255,255,0.15)", borderRadius: 8, color: "#94a3b8", cursor: "pointer", padding: "6px 14px", fontSize: 12 }}>?湔閰?</button>
              <button onClick={() => { setSelectedSupplier(s); resetSupplierDraft(s); setModalType("supplier"); }} style={{ background: "rgba(255,255,255,0.08)", border: "1px solid rgba(255,255,255,0.15)", borderRadius: 8, color: "#cbd5e1", cursor: "pointer", padding: "6px 14px", fontSize: 12 }}>靽格鞈?</button>
              {s.sourceSystem !== "burlan_supplier_records" && (
                <button onClick={() => deleteSupplier(s.id)} disabled={busy !== ""} style={{ background:"rgba(239,68,68,0.14)", border:"1px solid rgba(239,68,68,0.28)", borderRadius:8, color:"#fca5a5", cursor:"pointer", padding:"6px 14px", fontSize:12, opacity:busy ? 0.7 : 1 }}>?芷</button>
              )}
            </div>
            {s.issues.length>0 && (
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                <span style={{ fontSize: 11, color: "#ef4444", fontWeight: 600 }}>???嚗?/span>
                {s.issues.map((issue,i) => (<span key={i} style={{ fontSize: 11, background: "rgba(239,68,68,0.1)", color: "#f87171", borderRadius: 6, padding: "2px 8px", border: "1px solid rgba(239,68,68,0.2)" }}>{issue}</span>))}
              </div>
            )}
            {(s.evalHistory || []).length > 0 && <div style={{ marginTop:10, fontSize:12, color:"#cbd5e1" }}>?餈???{formatDate(s.evalHistory[0]?.date)}{s.evalHistory[0]?.operator ? ` 繚 ${s.evalHistory[0].operator}` : ""}{s.evalHistory[0]?.remark ? ` 繚 ${s.evalHistory[0].remark}` : ""}</div>}
          </div>
        ))}
        {filtered.length === 0 && <div style={{ textAlign:"center", padding:"24px 18px", color:"#64748b", background:"rgba(255,255,255,0.03)", borderRadius:12 }}>?桀?瘝?蝚血?璇辣??????/div>}
      </div>
      {modalType === "supplier" && (
        <Modal title={selectedSupplier ? `靽格靘???${selectedSupplier.name}` : "?啣?靘???} onClose={() => { setModalType(""); setSelectedSupplier(null); }}>
          <div style={{ display:"flex", flexDirection:"column", gap:16 }}>
            {[["靘??楊??,"id","text"],["靘???蝔?,"name","text"],["憿","category","text"],["?舐窗鈭?,"contact","text"],["?餈????,"lastEvalDate","date"],["閰??","evalScore","number"],["閰??望?嚗予嚗?,"evalIntervalDays","number"]].map(([label, field, type]) => (
              <div key={field}>
                <div style={{ fontSize:12, color:"#64748b", marginBottom:6 }}>{label}</div>
                <input type={type} value={supplierDraft[field]} onChange={e => setSupplierDraft({ ...supplierDraft, [field]: e.target.value })} style={inputStyle} disabled={selectedSupplier && field === "id"} />
              </div>
            ))}
            <div style={{ background: "rgba(6,182,212,0.08)", border: "1px solid rgba(6,182,212,0.2)", borderRadius: 8, padding: 12, color: "#bae6fd", fontSize: 12 }}>
              ?桀?閰?蝯?嚗evaluationResult(supplierDraft.evalScore)}
            </div>
            <div>
              <div style={{ fontSize:12, color:"#64748b", marginBottom:6 }}>?酉</div>
              <textarea value={supplierDraft.note} onChange={e => setSupplierDraft({ ...supplierDraft, note:e.target.value })} style={{ ...inputStyle, minHeight:72, resize:"vertical" }} />
            </div>
            <button onClick={saveSupplierInfo} disabled={busy !== ""} style={{ background:"linear-gradient(135deg,#0891b2,#06b6d4)", border:"none", borderRadius:10, color:"#fff", cursor:"pointer", padding:"12px 24px", fontSize:15, fontWeight:700, opacity:busy ? 0.7 : 1 }}>{busy === "save-supplier" ? "靽?銝?.." : "蝣箄?靽?"}</button>
          </div>
        </Modal>
      )}
      {modalType === "evaluation" && selectedSupplier && (
        <Modal title={`?湔閰?嚗?{selectedSupplier.name}`} onClose={() => { setModalType(""); setSelectedSupplier(null); }}>
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div><div style={{ fontSize: 12, color: "#64748b", marginBottom: 6 }}>閰??交?</div><input type="date" value={evalDraft.date} onChange={e=>setEvalDraft({...evalDraft,date:e.target.value})} style={inputStyle} /></div>
            <div><div style={{ fontSize: 12, color: "#64748b", marginBottom: 6 }}>閰?蝮賢? (0-100)</div><input type="number" min="0" max="100" value={evalDraft.score} onChange={e=>setEvalDraft({...evalDraft,score:e.target.value})} style={inputStyle} /></div>
            <div><div style={{ fontSize: 12, color: "#64748b", marginBottom: 6 }}>閰?鈭箏</div><input value={evalDraft.operator} onChange={e=>setEvalDraft({...evalDraft,operator:e.target.value})} style={inputStyle} /></div>
            <div><div style={{ fontSize: 12, color: "#64748b", marginBottom: 6 }}>???嚗?銵???</div><textarea value={evalDraft.issues} onChange={e=>setEvalDraft({...evalDraft,issues:e.target.value})} style={{ ...inputStyle, minHeight:88, resize:"vertical" }} /></div>
            <div><div style={{ fontSize: 12, color: "#64748b", marginBottom: 6 }}>?酉</div><textarea value={evalDraft.remark} onChange={e=>setEvalDraft({...evalDraft,remark:e.target.value})} style={{ ...inputStyle, minHeight:72, resize:"vertical" }} /></div>
            <div style={{ background: "rgba(6,182,212,0.1)", borderRadius: 8, padding: 12 }}><div style={{ fontSize: 12, color: "#22d3ee", fontWeight: 600 }}>閰?蝑?嚗evaluationResult(evalDraft.score)}</div><div style={{ fontSize: 11, color: "#64748b", marginTop: 4 }}>90+?芾 / 80-89? / 70-79璇辣? / 69隞乩?銝???/div></div>
            <button onClick={saveEvaluation} disabled={busy !== ""} style={{ background: "linear-gradient(135deg, #0891b2, #06b6d4)", border: "none", borderRadius: 10, color: "#fff", cursor: "pointer", padding: "12px 24px", fontSize: 15, fontWeight: 700, opacity:busy ? 0.7 : 1 }}>{busy === "save-supplier" ? "靽?銝?.." : "蝣箄??湔閰?"}</button>
          </div>
        </Modal>
      )}
    </div>
  );
}

// ??? NON-CONFORMANCE TAB (MP-15) ?????????????????????????????????????????????
