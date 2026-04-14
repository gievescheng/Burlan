function SvgBarChart({ data, width = 420, height = 150, color = "#3b82f6" }) {
  if (!data || data.length === 0) return <div style={{ color:"#475569", fontSize:12, textAlign:"center", padding:16 }}>撠鞈?</div>;
  const max = Math.max(...data.map(d => d.value), 1);
  const padL = 8, padR = 8, padB = 22, padT = 16;
  const innerW = width - padL - padR;
  const innerH = height - padT - padB;
  const slotW = innerW / data.length;
  const barW = Math.max(Math.min(slotW - 6, 36), 6);
  return (
    <svg width="100%" viewBox={`0 0 ${width} ${height}`} style={{ overflow:"visible", display:"block" }}>
      {[0, 0.5, 1].map(pct => {
        const y = padT + innerH - pct * innerH;
        return <line key={pct} x1={padL} y1={y} x2={padL + innerW} y2={y} stroke="rgba(255,255,255,0.05)" />;
      })}
      {data.map((d, i) => {
        const barH = Math.max(Math.round((d.value / max) * innerH), d.value > 0 ? 2 : 0);
        const x = padL + i * slotW + (slotW - barW) / 2;
        const y = padT + innerH - barH;
        return (
          <g key={i}>
            <rect x={x} y={y} width={barW} height={barH} rx={3} fill={color} opacity={0.85} />
            <text x={x + barW / 2} y={height - 4} textAnchor="middle" fill="#475569" fontSize={9}>{d.label}</text>
            {d.value > 0 && <text x={x + barW / 2} y={y - 3} textAnchor="middle" fill="#cbd5e1" fontSize={9}>{d.value}</text>}
          </g>
        );
      })}
    </svg>
  );
}

function SvgLineChart({ data, width = 420, height = 140, color = "#22c55e", domainMin, domainMax }) {
  if (!data || data.length < 2) return <div style={{ color:"#475569", fontSize:12, textAlign:"center", padding:16 }}>? 2 蝑誑銝???/div>;
  const vals = data.map(d => d.value);
  const rawMin = domainMin !== undefined ? domainMin : Math.min(...vals);
  const rawMax = domainMax !== undefined ? domainMax : Math.max(...vals);
  const range = rawMax - rawMin || 1;
  const padL = 36, padR = 12, padT = 16, padB = 24;
  const w = width - padL - padR;
  const h = height - padT - padB;
  const xStep = w / (data.length - 1);
  const pts = data.map((d, i) => ({
    x: padL + i * xStep,
    y: padT + h - ((d.value - rawMin) / range) * h,
    label: d.label,
    value: d.value,
  }));
  const linePath = pts.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(" ");
  const areaPath = linePath + ` L ${pts[pts.length - 1].x.toFixed(1)} ${(padT + h).toFixed(1)} L ${pts[0].x.toFixed(1)} ${(padT + h).toFixed(1)} Z`;
  return (
    <svg width="100%" viewBox={`0 0 ${width} ${height}`} style={{ overflow:"visible", display:"block" }}>
      {[0, 0.5, 1].map(pct => {
        const y = padT + h - pct * h;
        const val = rawMin + pct * range;
        return (
          <g key={pct}>
            <line x1={padL} y1={y} x2={padL + w} y2={y} stroke="rgba(255,255,255,0.05)" />
            <text x={padL - 4} y={y + 4} textAnchor="end" fill="#475569" fontSize={8}>{val.toFixed(1)}</text>
          </g>
        );
      })}
      <path d={areaPath} fill={color} opacity={0.08} />
      <path d={linePath} fill="none" stroke={color} strokeWidth={2} strokeLinejoin="round" />
      {pts.map((p, i) => (
        <g key={i}>
          <circle cx={p.x} cy={p.y} r={3} fill={color} />
          <text x={p.x} y={height - 4} textAnchor="middle" fill="#475569" fontSize={8}>{p.label}</text>
          <text x={p.x} y={p.y - 6} textAnchor="middle" fill="#cbd5e1" fontSize={8}>{p.value.toFixed(1)}</text>
        </g>
      ))}
    </svg>
  );
}

function SvgDonut({ slices, size = 110 }) {
  const total = slices.reduce((s, x) => s + x.value, 0) || 1;
  const cx = size / 2, cy = size / 2, r = size * 0.4, ir = size * 0.27;
  let angle = -Math.PI / 2;
  const paths = slices.map(sl => {
    const sweep = (sl.value / total) * 2 * Math.PI;
    const x1 = cx + r * Math.cos(angle),  y1 = cy + r * Math.sin(angle);
    angle += sweep;
    const x2 = cx + r * Math.cos(angle),  y2 = cy + r * Math.sin(angle);
    const ix1 = cx + ir * Math.cos(angle), iy1 = cy + ir * Math.sin(angle);
    const ix2 = cx + ir * Math.cos(angle - sweep), iy2 = cy + ir * Math.sin(angle - sweep);
    const lg = sweep > Math.PI ? 1 : 0;
    return (
      <path key={sl.label}
        d={`M ${x1.toFixed(2)} ${y1.toFixed(2)} A ${r} ${r} 0 ${lg} 1 ${x2.toFixed(2)} ${y2.toFixed(2)} L ${ix1.toFixed(2)} ${iy1.toFixed(2)} A ${ir} ${ir} 0 ${lg} 0 ${ix2.toFixed(2)} ${iy2.toFixed(2)} Z`}
        fill={sl.color} opacity={0.9} />
    );
  });
  return <svg width={size} height={size} style={{ display:"block" }}>{paths}</svg>;
}

// ??? KPI DASHBOARD ???????????????????????????????????????????????????????????

function KpiDashboard({ instruments, training, equipment, suppliers, nonConformances, auditPlans, envRecords, prodRecords, qualityRecords, qualityObjectives, qualityObjectiveSourceInfo }) {
  const safeArr = v => (Array.isArray(v) ? v : []);
  const prods    = safeArr(prodRecords);
  const ncs      = safeArr(nonConformances);
  const envs     = safeArr(envRecords);
  const supps    = safeArr(suppliers);
  const audits   = safeArr(auditPlans);
  const qrs      = safeArr(qualityRecords);
  const objectiveItems = safeArr(qualityObjectives);

  const objectiveAchieved = objectiveItems.filter(item => item.status === "achieved").length;
  const objectivePending = objectiveItems.filter(item => item.status === "pending").length;
  const objectiveManualReview = objectiveItems.filter(item => item.status !== "achieved" && item.status !== "pending").length;
  const objectiveRate = objectiveItems.length > 0 ? Math.round(objectiveAchieved / objectiveItems.length * 100) : null;

  const qcByMonth = {};
  qrs.forEach(record => {
    const month = String(record.date || record.inspectDate || "").substring(0, 7) || "?芰";
    if (!qcByMonth[month]) qcByMonth[month] = { total: 0, pass: 0 };
    qcByMonth[month].total += 1;
    if ((record.result || "").toUpperCase() === "PASS") qcByMonth[month].pass += 1;
  });
  const qcMonthRateData = Object.entries(qcByMonth).sort().slice(-6).map(([month, summary]) => ({
    label: month === "?芰" ? month : month.substring(5) + "??,
    value: summary.total > 0 ? Math.round(summary.pass / summary.total * 100) : 0,
  }));

  // ?? NC ?漲?梁? ?????????????????????????????????????????????
  const ncByMonth = {};
  ncs.forEach(nc => {
    const m = (nc.date || "").substring(0, 7) || "?芰";
    ncByMonth[m] = (ncByMonth[m] || 0) + 1;
  });
  const ncMonthData = Object.entries(ncByMonth).sort().slice(-6)
    .map(([k, v]) => ({ label: k.substring(5) + "??, value: v }));
  const openNc = ncs.filter(n => n.status !== "撌脤???).length;

  // ?? ?啣??????????????????????????????????????????????????
  const envTotal = envs.length;
  const envPass  = envs.filter(r => r.result === "?").length;
  const envPassRate = envTotal > 0 ? Math.round(envPass / envTotal * 100) : null;
  const envByLoc = {};
  envs.forEach(r => {
    const loc = r.location || r.point || "?芰";
    if (!envByLoc[loc]) envByLoc[loc] = { pass: 0, total: 0 };
    envByLoc[loc].total++;
    if (r.result === "?") envByLoc[loc].pass++;
  });
  const envLocData = Object.entries(envByLoc)
    .map(([loc, d]) => ({ label: loc.length > 5 ? loc.substring(0, 5) + "?? : loc, value: d.total > 0 ? Math.round(d.pass / d.total * 100) : 0 }));

  // ?? 靘?????????????????????????????????????????????????????
  const avgSupplierScore = supps.length > 0
    ? (supps.reduce((s, x) => s + getSupplierScore(x), 0) / supps.length).toFixed(0) : null;

  // ?? 蝔賣摰?????????????????????????????????????????????????
  const auditTotal = audits.length;
  const auditDone  = audits.filter(a => a.status === "撌脣???).length;
  const auditRate  = auditTotal > 0 ? Math.round(auditDone / auditTotal * 100) : null;
  const auditSlices = [
    { label: "撌脣???, value: auditDone,                                               color: "#22c55e" },
    { label: "?脰?銝?, value: audits.filter(a => a.status === "?脰?銝?).length,         color: "#3b82f6" },
    { label: "閮銝?, value: audits.filter(a => a.status === "閮銝?).length,         color: "#6366f1" },
    { label: "?暹?",   value: audits.filter(a => a.status === "?暹?").length,           color: "#ef4444" },
  ].filter(s => s.value > 0);

  // ?? 銝??蝯梯? ?????????????????????????????????????????
  const defectCount = {};
  prods.forEach(r => (r.defectReasons || []).forEach(reason => { defectCount[reason] = (defectCount[reason] || 0) + 1; }));
  const defectReasonData = Object.entries(defectCount).sort((a, b) => b[1] - a[1]).slice(0, 6)
    .map(([k, v]) => ({ label: k.length > 8 ? k.substring(0, 8) + "?? : k, value: v }));

  // ?? ?脫??????????????????????????????????????????????????
  const qcTotal = qrs.length;
  const qcPass  = qrs.filter(r => (r.result || "").toUpperCase() === "PASS").length;
  const qcRate  = qcTotal > 0 ? Math.round(qcPass / qcTotal * 100) : null;
  const supplierOverdue = supps.filter(item => daysUntil(addDays(item.lastEvalDate, item.evalIntervalDays)) < 0).length;

  // ?? KPI hero cards ??????????????????????????????????????????
  const heroCards = [
    {
      label: "?釭?格?????,
      value: objectiveRate !== null ? objectiveRate + "%" : "??,
      color: objectiveRate === null ? "#475569" : objectiveRate >= 90 ? "#22c55e" : objectiveRate >= 70 ? "#f59e0b" : "#ef4444",
      desc:  `${objectiveAchieved}/${objectiveItems.length} ???,
    },
    {
      label: "?芷???蝚血?",
      value: openNc,
      color: openNc === 0 ? "#22c55e" : openNc <= 3 ? "#f59e0b" : "#ef4444",
      desc:  `?? ${ncs.length} ?,
    },
    ENABLE_ENVIRONMENT_MODULE ? {
      label: "?啣????,
      value: envPassRate !== null ? envPassRate + "%" : "??,
      color: envPassRate === null ? "#475569" : envPassRate >= 90 ? "#22c55e" : envPassRate >= 80 ? "#f59e0b" : "#ef4444",
      desc:  `${envTotal} 蝑??,
    } : null,
    {
      label: "靘??像??",
      value: avgSupplierScore !== null ? avgSupplierScore : "??,
      color: avgSupplierScore === null ? "#475569" : parseFloat(avgSupplierScore) >= 85 ? "#22c55e" : parseFloat(avgSupplierScore) >= 70 ? "#f59e0b" : "#ef4444",
      desc:  `${supps.length} 摰跆,
    },
    {
      label: "蝔賣摰???,
      value: auditRate !== null ? auditRate + "%" : "??,
      color: auditRate === null ? "#475569" : auditRate >= 80 ? "#22c55e" : auditRate >= 50 ? "#f59e0b" : "#ef4444",
      desc:  `${auditDone}/${auditTotal} ?循,
    },
    {
      label: "?釭瑼ａ????,
      value: qcRate !== null ? qcRate + "%" : "??,
      color: qcRate === null ? "#475569" : qcRate >= 95 ? "#22c55e" : qcRate >= 80 ? "#f59e0b" : "#ef4444",
      desc:  `${qcTotal} ?鉑,
    },
  ].filter(Boolean);

  const panel = (children, style = {}) => (
    <div style={{ background:"rgba(255,255,255,0.03)", border:"1px solid rgba(255,255,255,0.08)", borderRadius:14, padding:20, ...style }}>
      {children}
    </div>
  );
  const sectionTitle = t => <div style={{ fontSize:13, fontWeight:700, color:"#e2e8f0", marginBottom:14 }}>{t}</div>;

  return (
    <div>
      {/* ?? 璅? ?? */}
      <div style={{ marginBottom:24 }}>
        <div style={{ fontSize:20, fontWeight:800, color:"#e2e8f0" }}>?蝮暹??銵冽</div>
        <div style={{ fontSize:13, color:"#64748b", marginTop:4 }}>
          擃?銝餌恣閬? ??{new Date().toLocaleString("zh-TW", { year:"numeric", month:"long", day:"numeric", hour:"2-digit", minute:"2-digit" })}
        </div>
      </div>
      <ModuleStatusBanner
        title="?桀??嚗?鞈芰璅蜓瑼?+ 蝟餌絞頛鞈?"
        tone="mixed"
        message="????冽??誑??.1?釭?格?蝞∪銵具銝餉? KPI ?????鞈芣炎撽?蝚血??里?詻甇??蝺氬身????蝑頂蝯梯????抵蕭頩扎?撠望??蝔?閬??璅???蝟餌絞?桀??祕????
      />

      <div style={{ background:"rgba(14,165,233,0.08)", border:"1px solid rgba(14,165,233,0.24)", borderRadius:14, padding:"14px 16px", marginBottom:20 }}>
        <div style={{ fontSize:12, color:"#7dd3fc", fontWeight:800 }}>?釭?格?銝餃???/div>
        <div style={{ fontSize:13, color:"#dbeafe", marginTop:6 }}>
          {qualityObjectiveSourceInfo?.message || "撠霈?啣?鞈芰璅恣?嗉”"}
        </div>
        <div style={{ fontSize:12, color:"#94a3b8", marginTop:6 }}>
          靘?瑼?嚗qualityObjectiveSourceInfo?.source_path || "撠???"}?|?敺犖撌亙霈嚗objectiveManualReview} ?|?撠憛怠神嚗objectivePending} ??
        </div>
      </div>

      <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(180px, 1fr))", gap:12, marginBottom:20 }}>
        <div style={{ background:"rgba(16,185,129,0.08)", border:"1px solid rgba(16,185,129,0.22)", borderRadius:14, padding:"14px 16px" }}>
          <div style={{ fontSize:12, color:"#86efac", fontWeight:700 }}>閮毀蝞∠?</div>
          <div style={{ fontSize:13, color:"#d1fae5", marginTop:6 }}>撌脖?摮?{training.length} 雿犖?～training.reduce((sum, employee) => sum + (employee.trainings || []).length, 0)} 蝑?蝺?/div>
        </div>
        <div style={{ background:"rgba(16,185,129,0.08)", border:"1px solid rgba(16,185,129,0.22)", borderRadius:14, padding:"14px 16px" }}>
          <div style={{ fontSize:12, color:"#86efac", fontWeight:700 }}>閮剖?靽?</div>
          <div style={{ fontSize:13, color:"#d1fae5", marginTop:6 }}>撌脖?摮?{equipment.length} ?啗身???暹? {equipment.filter(item => daysUntil(getEquipmentNextMaintenanceDate(item)) < 0).length} ??/div>
        </div>
        <div style={{ background:"rgba(16,185,129,0.08)", border:"1px solid rgba(16,185,129,0.22)", borderRadius:14, padding:"14px 16px" }}>
          <div style={{ fontSize:12, color:"#86efac", fontWeight:700 }}>靘?????/div>
          <div style={{ fontSize:13, color:"#d1fae5", marginTop:6 }}>撌脖?摮?{supps.length} 摰嗡???嚗??暹? {supplierOverdue} 摰?/div>
        </div>
      </div>

      {/* ?? Hero KPI ?∠? ?? */}
      <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill, minmax(150px, 1fr))", gap:12, marginBottom:20 }}>
        {heroCards.map(k => (
          <div key={k.label} style={{ background:"rgba(255,255,255,0.03)", border:`1px solid ${k.color}30`, borderRadius:14, padding:"18px 16px" }}>
            <div style={{ fontSize:28, fontWeight:800, color:k.color, lineHeight:1 }}>{k.value}</div>
            <div style={{ fontSize:12, color:"#94a3b8", marginTop:6 }}>{k.label}</div>
            <div style={{ fontSize:11, color:"#475569", marginTop:3 }}>{k.desc}</div>
          </div>
        ))}
      </div>

      {/* ?? 蝚砌????釭瑼ａ? + NC ?漲 ?? */}
      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:16, marginBottom:16 }}>
        {panel(<>
          {sectionTitle("?釭?格?蝮質汗")}
          {objectiveItems.length === 0 ? (
            <div style={{ color:"#475569", fontSize:12 }}>撠霈?啣?鞈芰璅恣?嗉”</div>
          ) : (
            <div style={{ display:"flex", flexDirection:"column", gap:10 }}>
              {objectiveItems.map(item => {
                const statusMeta = item.status === "achieved"
                  ? { label: "撌脤???, color: "#22c55e", bg: "rgba(34,197,94,0.12)" }
                  : item.status === "pending"
                    ? { label: "撠憛怠神", color: "#f59e0b", bg: "rgba(245,158,11,0.12)" }
                    : item.status === "missed"
                      ? { label: "?芷???, color: "#ef4444", bg: "rgba(239,68,68,0.12)" }
                      : { label: "敺犖撌亙霈", color: "#38bdf8", bg: "rgba(56,189,248,0.12)" };
                return (
                  <div key={item.id} style={{ border:"1px solid rgba(255,255,255,0.08)", borderRadius:12, padding:"12px 14px", background:"rgba(255,255,255,0.02)" }}>
                    <div style={{ display:"flex", justifyContent:"space-between", gap:12, alignItems:"center", marginBottom:8 }}>
                      <div>
                        <div style={{ fontSize:13, fontWeight:800, color:"#e2e8f0" }}>{item.item_no}. {item.objective}</div>
                        <div style={{ fontSize:12, color:"#94a3b8", marginTop:4 }}>{item.department} 嚚?{item.measurement}</div>
                      </div>
                      <div style={{ padding:"4px 10px", borderRadius:999, background:statusMeta.bg, color:statusMeta.color, fontSize:12, fontWeight:800, whiteSpace:"nowrap" }}>{statusMeta.label}</div>
                    </div>
                    <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(180px, 1fr))", gap:8, fontSize:12 }}>
                      <div style={{ color:"#cbd5e1" }}>?餈?隞踝?<span style={{ color:"#e2e8f0", fontWeight:700 }}>{item.latest_month || "?芸‵"}</span></div>
                      <div style={{ color:"#cbd5e1" }}>?格?嚗?span style={{ color:"#e2e8f0", fontWeight:700 }}>{item.latest_target || "?芸‵"}</span></div>
                      <div style={{ color:"#cbd5e1" }}>撖衣蜀嚗?span style={{ color:"#e2e8f0", fontWeight:700 }}>{item.latest_actual || "?芸‵"}</span></div>
                      <div style={{ color:"#cbd5e1" }}>?文?嚗?span style={{ color:"#e2e8f0", fontWeight:700 }}>{item.latest_judgement || "?芸‵"}</span></div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>)}
        {panel(<>
          {sectionTitle("?釭瑼ａ??漲???%嚗?)}
          {qcMonthRateData.length === 0
            ? <div style={{ color:"#475569", fontSize:12 }}>撠?釭瑼ａ?閮?</div>
            : <SvgLineChart data={qcMonthRateData} color="#22c55e" domainMin={0} domainMax={100} />
          }
        </>)}
      </div>

      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:16, marginBottom:16 }}>
        {panel(<>
          {sectionTitle("銝泵???漲隞嗆")}
          {ncMonthData.length === 0
            ? <div style={{ color:"#475569", fontSize:12 }}>撠銝泵????/div>
            : <SvgBarChart data={ncMonthData} color="#f59e0b" />
          }
        </>)}
        {ENABLE_ENVIRONMENT_MODULE && panel(<>
          {sectionTitle("?皜祇??啣????%嚗?)}
          {envLocData.length === 0
            ? <div style={{ color:"#475569", fontSize:12 }}>撠?啣?閮?</div>
            : <SvgBarChart data={envLocData} color="#38bdf8" />
          }
        </>)}
        {panel(<>
          {sectionTitle("銝??嚗辣嚗?)}
          {defectReasonData.length === 0
            ? <div style={{ color:"#475569", fontSize:12 }}>撠銝??閮?</div>
            : <SvgBarChart data={defectReasonData} color="#ef4444" />
          }
        </>)}
      </div>

      {/* ?? 蝚砌???靘??帖璇?+ 蝔賣? ?? */}
      <div style={{ display:"grid", gridTemplateColumns:"2fr 1fr", gap:16 }}>
        {panel(<>
          {sectionTitle("靘?????閬?)}
          <div style={{ display:"flex", flexDirection:"column", gap:9 }}>
            {supps.length === 0 && <div style={{ color:"#475569", fontSize:12 }}>撠靘?????/div>}
            {supps.slice(0, 8).map(s => {
              const score = getSupplierScore(s);
              const barColor = score >= 85 ? "#22c55e" : score >= 70 ? "#f59e0b" : "#ef4444";
              return (
                <div key={s.id || s.name} style={{ display:"flex", alignItems:"center", gap:10 }}>
                  <div style={{ fontSize:12, color:"#94a3b8", width:72, flexShrink:0, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{s.name || "??}</div>
                  <div style={{ flex:1, background:"rgba(255,255,255,0.05)", borderRadius:4, height:10, overflow:"hidden" }}>
                    <div style={{ width:score + "%", height:"100%", background:barColor, borderRadius:4, transition:"width 0.6s ease" }} />
                  </div>
                  <div style={{ fontSize:12, fontWeight:700, color:barColor, width:28, textAlign:"right", flexShrink:0 }}>{score}</div>
                </div>
              );
            })}
          </div>
        </>)}
        {panel(<>
          {sectionTitle("蝔賣閮摰???)}
          {auditSlices.length === 0
            ? <div style={{ color:"#475569", fontSize:12 }}>撠蝔賣閮</div>
            : (
              <div style={{ display:"flex", alignItems:"center", gap:20 }}>
                <SvgDonut slices={auditSlices} size={110} />
                <div style={{ display:"flex", flexDirection:"column", gap:8 }}>
                  {[
                    { label:"撌脣???, color:"#22c55e", count: auditDone },
                    { label:"?脰?銝?, color:"#3b82f6", count: audits.filter(a => a.status === "?脰?銝?).length },
                    { label:"閮銝?, color:"#6366f1", count: audits.filter(a => a.status === "閮銝?).length },
                    { label:"?暹?",   color:"#ef4444", count: audits.filter(a => a.status === "?暹?").length },
                  ].map(item => (
                    <div key={item.label} style={{ display:"flex", alignItems:"center", gap:6 }}>
                      <div style={{ width:8, height:8, borderRadius:"50%", background:item.color, flexShrink:0 }} />
                      <div style={{ fontSize:11, color:"#94a3b8" }}>{item.label}</div>
                      <div style={{ fontSize:12, fontWeight:700, color:item.color, marginLeft:"auto", paddingLeft:8 }}>{item.count}</div>
                    </div>
                  ))}
                  <div style={{ fontSize:13, fontWeight:800, color: auditRate !== null ? (auditRate >= 80 ? "#22c55e" : auditRate >= 50 ? "#f59e0b" : "#ef4444") : "#475569", marginTop:4, borderTop:"1px solid rgba(255,255,255,0.07)", paddingTop:6 }}>
                    摰???{auditRate !== null ? auditRate + "%" : "??}
                  </div>
                </div>
              </div>
            )
          }
        </>)}
      </div>
    </div>
  );
}

// ??? DASHBOARD HOME ???????????????????????????????????????????????????????????
function DashboardHome({ instruments, documents, training, equipment, suppliers, nonConformances, auditPlans, envRecords, setActiveTab, calibrationSourceInfo }) {
  const now = new Date(); now.setHours(0,0,0,0);
  const overdueInst = instruments.filter(i => {
    const nextDate = getInstrumentNextCalibrationDate(i);
    return nextDate && daysUntil(nextDate) < 0;
  }).length;
  const upcomingInst = instruments.filter(i => {
    const nextDate = getInstrumentNextCalibrationDate(i);
    const d = nextDate ? daysUntil(nextDate) : 9999;
    return d >= 0 && d <= 30;
  }).length;
  const overdueDoc = documents.filter(d => daysUntil(d.nextReview) < 0).length;
  const expiredTrain = training.filter(t => {
    const expiry = getEmployeeTrainingExpiry(t);
    return expiry && daysUntil(expiry) < 0;
  }).length;
  const overdueEquip = equipment.filter(e => daysUntil(getEquipmentNextMaintenanceDate(e)) < 0).length;
  const openNc = nonConformances.filter(n => n.status !== "撌脤???).length;
  const overdueNc = nonConformances.filter(n => n.status !== "撌脤??? && daysUntil(n.dueDate) < 0).length;
  const upcomingAudit = auditPlans.filter(a => a.status === "閮銝? && daysUntil(a.scheduledDate) >= 0 && daysUntil(a.scheduledDate) <= 30).length;
  const envPassRate = envRecords.length > 0 ? Math.round(envRecords.filter(r => r.result === "?").length / envRecords.length * 100) : 0;
  const poorSupplier = suppliers.filter(s => getSupplierScore(s) < 70).length;
  const alerts = [];
  if (overdueInst > 0) alerts.push({ type: "error", msg: `??${overdueInst} ?啣??冽甇?歇?暹?嚗??芸?摰?` });
  if (upcomingInst > 0) alerts.push({ type: "warn", msg: `??${upcomingInst} ?啣??典???30 憭拙?唳??⊥迤` });
  if (overdueDoc > 0) alerts.push({ type: "error", msg: `??${overdueDoc} 隞賣?隞嗅歇頞?銴祟??` });
  if (expiredTrain > 0) alerts.push({ type: "error", msg: `??${expiredTrain} 雿犖?∠?閮毀???歇? });
  if (overdueEquip > 0) alerts.push({ type: "error", msg: `??${overdueEquip} ?啗身??擗歇?暹?` });
  if (overdueNc > 0) alerts.push({ type: "error", msg: `??${overdueNc} 蝑?蝚血?撌脤暹??芰?獢 });
  if (upcomingAudit > 0) alerts.push({ type: "warn", msg: `${upcomingAudit} ?游?函里?詨???30 憭拙?瑁?` });
  if (poorSupplier > 0) alerts.push({ type: "warn", msg: `??${poorSupplier} 摰嗡???閰?銝雲 70 ? });
  if (ENABLE_ENVIRONMENT_MODULE && envRecords.length > 0 && envPassRate < 90) alerts.push({ type: "warn", msg: `瞏楊摰斤憓??潛???${envPassRate}%` });
  const kpis = [
    { label: "?⊥迤???, value: instruments.length, sub: overdueInst > 0 ? `${overdueInst} ?圈暹?` : "?券甇?虜", color: overdueInst > 0 ? "#ef4444" : "#60a5fa", tab: "calibration" },
    { label: "蝔??辣", value: documents.length, sub: overdueDoc > 0 ? `${overdueDoc} 隞賡暹?` : "?券??", color: overdueDoc > 0 ? "#ef4444" : "#22c55e", tab: "documents" },
    { label: "閮毀閮?", value: training.length, sub: expiredTrain > 0 ? `${expiredTrain}鈭粹?? : "?券??", color: expiredTrain > 0 ? "#ef4444" : "#22c55e", tab: "training" },
    { label: "閮剖?靽?", value: equipment.length, sub: overdueEquip > 0 ? `${overdueEquip} ?圈暹?` : "?券甇?虜", color: overdueEquip > 0 ? "#ef4444" : "#22c55e", tab: "equipment" },
    { label: "靘???, value: suppliers.length, sub: poorSupplier > 0 ? `${poorSupplier}摰嗉???頞訢 : "?券?", color: poorSupplier > 0 ? "#eab308" : "#22c55e", tab: "supplier" },
    { label: "銝泵??", value: nonConformances.length, sub: openNc > 0 ? `${openNc}???` : "?券撌脤???, color: openNc > 0 ? "#ef4444" : "#22c55e", tab: "nonconformance" },
    { label: "蝔賣閮", value: auditPlans.length, sub: upcomingAudit > 0 ? `${upcomingAudit} ??30 憭拙?瑁?` : "憒??脰?", color: upcomingAudit > 0 ? "#f97316" : "#8b5cf6", tab: "auditplan" },
    ENABLE_ENVIRONMENT_MODULE ? { label: "?啣???葫", value: envRecords.length, sub: `???${envPassRate}%`, color: envPassRate >= 90 ? "#14b8a6" : envPassRate >= 80 ? "#eab308" : "#ef4444", tab: "environment" } : null,
  ].filter(Boolean);
  return (
    <div>
      <div style={{ marginBottom: 28 }}>
        <div style={{ fontSize: 22, fontWeight: 800, color: "#e2e8f0", letterSpacing: 1 }}>???璆剛隞賣????ISO 9001:2015</div>
        <div style={{ fontSize: 14, color: "#64748b", marginTop: 4 }}>?釭蝞∠?蝟餌絞?芸?蝔賣銝餅????{new Date().toLocaleDateString("zh-TW", { year:"numeric", month:"long", day:"numeric" })}</div>
      </div>
      <ModuleStatusBanner
        title="?桀?蝟餌絞?脣漲"
        tone="mixed"
        message={`撌脣?????迤撘???????辣蝞∠???隞嗅澈?I 撌乩??啜?蝚血?蝞∠??里?貉???{calibrationSourceInfo?.mode === "records" ? "?甇?恣?? : ""}?身??擗???蝞∠???蝺渡恣????舀???頂蝯梯????批捆?舀?蝥?摮?KPI ?毽?＊蝷箸迤撘???蝟餌絞鞈?嚗???蕭頩方?撽??}
      />
      {alerts.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <div style={{ fontSize: 13, color: "#94a3b8", fontWeight: 700, marginBottom: 10 }}>??蝟餌絞霅衣內 ({alerts.length})</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {alerts.map((a, i) => (
              <div key={i} style={{ background: a.type==="error"?"rgba(239,68,68,0.08)":"rgba(234,179,8,0.08)", border: `1px solid ${a.type==="error"?"rgba(239,68,68,0.3)":"rgba(234,179,8,0.3)"}`, borderRadius: 10, padding: "10px 16px", fontSize: 13, color: a.type==="error"?"#fca5a5":"#fde68a", display:"flex", alignItems:"center", gap:8 }}>
                <span>{a.type==="error"?"??:"??"}</span><span>{a.msg}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 14, marginBottom: 28 }}>
        {kpis.map(k => (
          <div key={k.tab} onClick={() => setActiveTab(k.tab)} style={{ background: "rgba(255,255,255,0.04)", border: `1px solid ${k.color}40`, borderRadius: 14, padding: "18px 20px", cursor: "pointer", transition: "all 0.2s" }}
            onMouseEnter={e => e.currentTarget.style.background="rgba(255,255,255,0.08)"}
            onMouseLeave={e => e.currentTarget.style.background="rgba(255,255,255,0.04)"} >
            <div style={{ fontSize: 28, fontWeight: 800, color: k.color, lineHeight: 1 }}>{k.value}</div>
            <div style={{ fontSize: 13, color: "#94a3b8", marginTop: 6 }}>{k.label}</div>
            <div style={{ fontSize: 11, color: k.color, marginTop: 4, fontWeight: 600 }}>{k.sub}</div>
          </div>
        ))}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 14, padding: 20 }}>
          <div style={{ fontSize: 14, fontWeight: 700, color: "#e2e8f0", marginBottom: 14 }}>?餈甇?????/div>
          {[...instruments]
            .map(inst => ({ ...inst, dashboardNextCalibration: getInstrumentNextCalibrationDate(inst) }))
            .sort((a,b) => daysUntil(a.dashboardNextCalibration) - daysUntil(b.dashboardNextCalibration))
            .slice(0,5)
            .map(inst => (
            <div key={inst.id} style={{ display:"flex", justifyContent:"space-between", alignItems:"center", padding:"8px 0", borderBottom:"1px solid rgba(255,255,255,0.05)" }}>
              <div>
                <div style={{ fontSize:13, color:"#e2e8f0" }}>{inst.name}</div>
                <div style={{ fontSize:11, color:"#64748b" }}>{inst.id} 嚚??敺甇?{formatDate(inst.calibratedDate)}</div>
              </div>
              <Badge color={urgencyColor(daysUntil(inst.dashboardNextCalibration))}>{urgencyLabel(daysUntil(inst.dashboardNextCalibration))}</Badge>
            </div>
          ))}
        </div>
        <div style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 14, padding: 20 }}>
          <div style={{ fontSize: 14, fontWeight: 700, color: "#e2e8f0", marginBottom: 14 }}>?芷???蝚血??</div>
          {nonConformances.filter(n => n.status !== "撌脤???).slice(0,5).map(nc => (
            <div key={nc.id} style={{ display:"flex", justifyContent:"space-between", alignItems:"center", padding:"8px 0", borderBottom:"1px solid rgba(255,255,255,0.05)" }}>
              <div>
                <div style={{ fontSize:12, color:"#e2e8f0" }}>{nc.description.slice(0,20)}{nc.description.length>20?"...":""}</div>
                <div style={{ fontSize:11, color:"#64748b" }}>{nc.id} ??{nc.dept}</div>
              </div>
              <Badge color={daysUntil(nc.dueDate)===9999?"#64748b":daysUntil(nc.dueDate)<0?"#ef4444":daysUntil(nc.dueDate)<=7?"#eab308":"#60a5fa"}>{daysUntil(nc.dueDate)===9999?"?∪?":daysUntil(nc.dueDate)<0?"?暹?":"??+daysUntil(nc.dueDate)+"憭?}</Badge>
            </div>
          ))}
          {nonConformances.filter(n=>n.status!=="撌脤???).length===0 && <div style={{color:"#22c55e",fontSize:13,marginTop:8}}>???桀?瘝??芷???蝚血???/div>}
        </div>
      </div>
    </div>
  );
}

// ??? MAIN APP ????????????????????????????????????????????????????????????????
export default function App() {
  const [activeTab, setActiveTab] = useState(() => {
    if (typeof window === "undefined") return "home";
    const params = new URLSearchParams(window.location.search);
    return params.get("google") ? "notification" : (params.get("tab") || "home");
  });
  const [instruments, setInstruments] = useState(initialInstruments);
  const [calibrationSourceInfo, setCalibrationSourceInfo] = useState({
    mode: "fallback",
    source_path: "",
    count: initialInstruments.length,
    latest_plan_path: "",
    inventory_path: "",
    manual_update_count: 0,
    message: "",
  });
  const [documents, setDocuments] = useState(initialDocuments);
  const [focusDocumentId, setFocusDocumentId] = useState("");
  const [documentsSourceInfo, setDocumentsSourceInfo] = useState({
    mode: "fallback",
    source_path: "",
    count: initialDocuments.length,
    pending_review_count: 0,
    message: "",
  });
  const [qualityObjectives, setQualityObjectives] = useState([]);
  const [qualityObjectiveSourceInfo, setQualityObjectiveSourceInfo] = useState({
    mode: "unloaded",
    source_path: "",
    count: 0,
    achieved_count: 0,
    pending_count: 0,
    manual_review_count: 0,
    achievement_rate: null,
    message: "",
  });
  const [training, setTraining] = useState(initialTraining);
  const [equipment, setEquipment] = useState(initialEquipment);
  const [suppliers, setSuppliers] = useState(initialSuppliers);
  const [nonConformances, setNonConformances] = useState(initialNonConformances);
  const [highlightNcId, setHighlightNcId] = useState(null);
  const [expandNcId, setExpandNcId] = useState(null);
  const [pendingNcDraft, setPendingNcDraft] = useState(null);
  const [auditPlans, setAuditPlans] = useState(initialAuditPlans);
  const [envRecords, setEnvRecords] = useState(initialEnvRecords);
  const [prodRecords, setProdRecords] = useState(() => loadStoredState("audit_prodrecords", initialProdRecords));
  const [qualityRecords, setQualityRecords] = useState(() => loadStoredState("audit_qualityrecords", initialQualityRecords));
  const [manuals] = useState(initialManuals);
  const runningFromFile = typeof window !== "undefined" && window.location.protocol === "file:";

  useEffect(() => saveStoredState("audit_prodrecords", prodRecords), [prodRecords]);
  useEffect(() => saveStoredState("audit_qualityrecords", qualityRecords), [qualityRecords]);

  useEffect(() => {
    let cancelled = false;
    async function loadOpsData() {
      try {
        const requests = [
          apiJson("/api/training-records"),
          apiJson("/api/equipment-records"),
          apiJson("/api/supplier-records"),
          apiJson("/api/nonconformances"),
          apiJson("/api/audit-plans"),
        ];
        if (ENABLE_ENVIRONMENT_MODULE) requests.push(apiJson("/api/environment-records"));
        const [trainingPayload, equipmentPayload, supplierPayload, ncPayload, auditPayload, envPayload] = await Promise.all(requests);
        if (cancelled) return;
        setTraining(trainingPayload.items || []);
        setEquipment(equipmentPayload.items || []);
        setSuppliers(supplierPayload.items || []);
        setNonConformances(ncPayload.items || []);
        setAuditPlans(auditPayload.items || []);
        setEnvRecords(ENABLE_ENVIRONMENT_MODULE ? (envPayload?.items || []) : []);
      } catch (err) {
        console.warn("Failed to load operation data", err);
      }
    }
    loadOpsData();
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function loadCalibrationRecords() {
      try {
        const payload = await apiJson("/api/burlan/calibration-instruments");
        if (cancelled) return;
        const items = (payload.items || []).map(mapCalibrationInstrument);
        if (items.length > 0) {
          setInstruments(items);
          setCalibrationSourceInfo({
            mode: payload.mode || "records",
            source_path: payload.source_path || "",
            count: payload.count || items.length,
            latest_plan_path: payload.latest_plan_path || "",
            inventory_path: payload.inventory_path || "",
            manual_update_count: payload.manual_update_count || 0,
            message: payload.message || "",
          });
          return;
        }
        setCalibrationSourceInfo({
          mode: "fallback",
          source_path: payload.source_path || "",
          count: initialInstruments.length,
          latest_plan_path: payload.latest_plan_path || "",
          inventory_path: payload.inventory_path || "",
          manual_update_count: payload.manual_update_count || 0,
          message: "9?葫鞈?蝞∠?蝔? 瘝?霈?啣?典??其?閬質”?悼甇瑁”嚗?＊蝷箸?????渲???,
        });
      } catch (err) {
        if (cancelled) return;
        setCalibrationSourceInfo({
          mode: "fallback",
          source_path: "",
          count: initialInstruments.length,
          latest_plan_path: "",
          inventory_path: "",
          manual_update_count: 0,
          message: "9?葫鞈?蝞∠?蝔? 頛憭望?嚗?＊蝷箸?????渲???" + err.message,
        });
      }
    }
    loadCalibrationRecords();
    return () => { cancelled = true; };
  }, []);

  function handleCreateNonConformanceDraft(draft) {
    setPendingNcDraft(draft);
    setActiveTab("nonconformance");
  }

  function handleOpenDocumentFromFlow(docId, tab = "documents") {
    if (!docId) return;
    setFocusDocumentId(docId);
    setActiveTab(tab);
  }

  useEffect(() => {
    let cancelled = false;
    async function loadBurlanDocuments() {
      try {
        const payload = await apiJson("/api/burlan/master-documents");
        if (cancelled) return;
        const items = (payload.items || []).filter(item => item.path).map(mapBurlanMasterToDocument);
        if (items.length > 0) {
          setDocuments(items);
          setDocumentsSourceInfo({
            mode: "master",
            source_path: payload.source_path || "",
            count: payload.count || items.length,
            pending_review_count: payload.pending_review_count || 0,
            message: payload.message || "",
          });
          return;
        }
        setDocumentsSourceInfo({
          mode: "fallback",
          source_path: payload.source_path || "",
          count: initialDocuments.length,
          pending_review_count: payload.pending_review_count || 0,
          message: "??蜓皜瘝??舐?辣嚗?＊蝷箏撱箏??渲???,
        });
      } catch (err) {
        if (cancelled) return;
        setDocumentsSourceInfo({
          mode: "fallback",
          source_path: "",
          count: initialDocuments.length,
          pending_review_count: 0,
          message: "??蜓皜頛憭望?嚗?＊蝷箏撱箏??渲???" + err.message,
        });
      }
    }
    loadBurlanDocuments();
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function loadQualityObjectives() {
      try {
        const payload = await apiJson("/api/burlan/quality-objectives");
        if (cancelled) return;
        setQualityObjectives(payload.items || []);
        setQualityObjectiveSourceInfo({
          mode: "objective_master",
          source_path: payload.source_path || "",
          count: payload.count || 0,
          achieved_count: payload.achieved_count || 0,
          pending_count: payload.pending_count || 0,
          manual_review_count: payload.manual_review_count || 0,
          achievement_rate: payload.achievement_rate,
          message: payload.message || "",
        });
      } catch (err) {
        if (cancelled) return;
        setQualityObjectives([]);
        setQualityObjectiveSourceInfo({
          mode: "error",
          source_path: "",
          count: 0,
          achieved_count: 0,
          pending_count: 0,
          manual_review_count: 0,
          achievement_rate: null,
          message: "?釭?格?蝞∪銵刻??亙仃??" + err.message,
        });
      }
    }
    loadQualityObjectives();
    return () => { cancelled = true; };
  }, []);

  const tabs = [
    { id: "home",           label: "銝餅??,   icon: "?? },
    { id: "kpi",            label: "蝮暹??銵冽", icon: "?? },
    { id: "calibration",    label: "?⊥迤蝞∠?", icon: "?? },
    { id: "documents",      label: "?辣蝞∠?", icon: "?? },
    { id: "library",        label: "?辣摨?,   icon: "??" },
    { id: "training",       label: "閮毀蝞∠?", icon: "?? },
    { id: "equipment",      label: "閮剖?靽?", icon: "?? },
    { id: "supplier",       label: "靘??恣??, icon: "?? },
    { id: "nonconformance", label: "銝泵?恣??, icon: "?? },
    { id: "auditplan",      label: "蝔賣閮", icon: "?? },
    ENABLE_ENVIRONMENT_MODULE ? { id: "environment", label: "?啣???葫", icon: "?? } : null,
    { id: "production",     label: "閮??臬", icon: "R" },
    { id: "notification",   label: "???", icon: "?? },
    { id: "aiworkbench",    label: "AI 撌乩???, icon: "AI" },
    { id: "report",         label: "蝔賣?勗?", icon: "?? },
  ].filter(Boolean);

  function renderTab() {
    switch(activeTab) {
      case "home":           return <DashboardHome instruments={instruments} documents={documents} training={training} equipment={equipment} suppliers={suppliers} nonConformances={nonConformances} auditPlans={auditPlans} envRecords={envRecords} setActiveTab={setActiveTab} calibrationSourceInfo={calibrationSourceInfo} />;
      case "kpi":            return <KpiDashboard instruments={instruments} training={training} equipment={equipment} suppliers={suppliers} nonConformances={nonConformances} auditPlans={auditPlans} envRecords={envRecords} prodRecords={prodRecords} qualityRecords={qualityRecords} qualityObjectives={qualityObjectives} qualityObjectiveSourceInfo={qualityObjectiveSourceInfo} />;
      case "calibration":    return <CalibrationTab instruments={instruments} setInstruments={setInstruments} calibrationSourceInfo={calibrationSourceInfo} setCalibrationSourceInfo={setCalibrationSourceInfo} />;
      case "documents":      return <DocumentsManagerTab documents={documents} setDocuments={setDocuments} manuals={manuals} documentsSourceInfo={documentsSourceInfo} focusDocumentId={focusDocumentId} onFocusDocumentDone={() => setFocusDocumentId("")} />;
      case "library":        return <LibraryHierarchyTab documents={documents} manuals={manuals} documentsSourceInfo={documentsSourceInfo} focusDocumentId={focusDocumentId} onFocusDocumentDone={() => setFocusDocumentId("")} />;
      case "training":       return <TrainingTab training={training} setTraining={setTraining} />;
      case "equipment":      return <EquipmentTab equipment={equipment} setEquipment={setEquipment} />;
      case "supplier":       return <SupplierTab suppliers={suppliers} setSuppliers={setSuppliers} />;
      case "nonconformance": return <NonConformanceTab nonConformances={nonConformances} setNonConformances={setNonConformances} highlightNcId={highlightNcId} onHighlightDone={() => setHighlightNcId(null)} expandNcId={expandNcId} onExpandDone={() => setExpandNcId(null)} documents={documents} documentsSourceInfo={documentsSourceInfo} draftSeed={pendingNcDraft} onDraftSeedConsumed={() => setPendingNcDraft(null)} onAuditPlansSync={setAuditPlans} onOpenDocument={handleOpenDocumentFromFlow} />;
      case "auditplan":      return <AuditPlanTab auditPlans={auditPlans} setAuditPlans={setAuditPlans} documents={documents} documentsSourceInfo={documentsSourceInfo} onCreateNonConformance={handleCreateNonConformanceDraft} nonConformances={nonConformances} setActiveTab={setActiveTab} setHighlightNcId={setHighlightNcId} setExpandNcId={setExpandNcId} onOpenDocument={handleOpenDocumentFromFlow} />;
      case "environment":    return ENABLE_ENVIRONMENT_MODULE ? <EnvironmentTab envRecords={envRecords} setEnvRecords={setEnvRecords} /> : <div style={{ padding:24, color:"#94a3b8" }}>????雿輻?啣???葫璅∠?嚗歇敺蜓瘚??梯???/div>;
    case "production":     return <PageErrorBoundary pageName="????" storageKeys={["audit_prodrecords", "audit_qualityrecords"]}><ProductionTab envRecords={envRecords} prodRecords={prodRecords} setProdRecords={setProdRecords} qualityRecords={qualityRecords} setQualityRecords={setQualityRecords} nonConformances={nonConformances} auditPlans={auditPlans} setActiveTab={setActiveTab} setHighlightNcId={setHighlightNcId} setExpandNcId={setExpandNcId} /></PageErrorBoundary>;
      case "notification":   return <NotificationTab instruments={instruments} documents={documents} equipment={equipment} suppliers={suppliers} nonConformances={nonConformances} auditPlans={auditPlans} />;
      case "aiworkbench":    return <AIWorkbenchTab documents={documents} manuals={manuals} nonConformances={nonConformances} />;
      case "report":         return <ReportTab instruments={instruments} documents={documents} training={training} equipment={equipment} suppliers={suppliers} nonConformances={nonConformances} auditPlans={auditPlans} envRecords={envRecords} />;
      default:               return <DashboardHome instruments={instruments} documents={documents} training={training} equipment={equipment} suppliers={suppliers} nonConformances={nonConformances} auditPlans={auditPlans} envRecords={envRecords} setActiveTab={setActiveTab} calibrationSourceInfo={calibrationSourceInfo} />;
    }
  }

  return (
    <div style={{ minHeight: "100vh", background: "radial-gradient(circle at top left, rgba(14,165,233,0.08), transparent 26%), linear-gradient(135deg, #08101f 0%, #0b1220 45%, #080d18 100%)", color: "#e2e8f0", fontFamily: "'Noto Sans TC', sans-serif" }}>
      <div style={{ position: "sticky", top: 0, zIndex: 20, background: "rgba(8,15,30,0.88)", borderBottom: "1px solid rgba(148,163,184,0.12)", backdropFilter: "blur(16px)", padding: "0 24px", boxShadow: "0 10px 30px rgba(2,6,23,0.18)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 18, overflowX: "auto" }}>
          <div style={{ padding: "14px 0", minWidth: 170 }}>
            <div style={{ fontSize: 11, letterSpacing: 1.4, textTransform: "uppercase", color: "#7dd3fc", fontWeight: 800 }}>??QMS</div>
            <div style={{ fontSize: 15, color: "#e2e8f0", fontWeight: 800, marginTop: 4 }}>?釭蝔賣撌乩???/div>
          </div>
          {tabs.map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)} style={{
              background: activeTab === t.id ? "rgba(56,189,248,0.14)" : "transparent",
              border: activeTab === t.id ? "1px solid rgba(56,189,248,0.28)" : "1px solid transparent",
              cursor: "pointer",
              padding: "10px 14px",
              fontSize: 12,
              fontWeight: 700,
              color: activeTab === t.id ? "#dbeafe" : "#94a3b8",
              borderRadius: 12,
              whiteSpace: "nowrap",
              display: "flex",
              alignItems: "center",
              gap: 8,
              transition: "all 0.2s ease",
              margin: "10px 0",
            }}>
              <span style={{ fontSize: 12, minWidth: 24, height: 24, display: "inline-flex", alignItems: "center", justifyContent: "center", borderRadius: 999, background: activeTab === t.id ? "rgba(59,130,246,0.18)" : "rgba(255,255,255,0.06)" }}>{t.icon}</span>
              <span>{t.label}</span>
            </button>
          ))}
        </div>
      </div>
      <div style={{ maxWidth: 1460, margin: "0 auto", padding: "28px 24px 40px" }}>
        {runningFromFile && (
          <div style={{ marginBottom: 18, background: "rgba(245,158,11,0.08)", border: "1px solid rgba(245,158,11,0.24)", borderRadius: 16, padding: 16, boxShadow: uiTheme.shadow }}>
            <div style={{ fontSize: 14, fontWeight: 800, color: "#fcd34d", marginBottom: 6 }}>雿??湔?? index.html</div>
            <div style={{ fontSize: 13, color: uiTheme.textMuted, lineHeight: 1.8 }}>
              ?見?臭誑??恍嚗?????蜓皜?I 蝔賣?PI 霈??摰??航銝?甇?虜?遣霅唳??
              <span style={{ color: "#e2e8f0", fontWeight: 700 }}> ????里?貊頂蝯?bat </span>
              嚗??湔??
              <span style={{ color: "#e2e8f0", fontWeight: 700 }}> http://127.0.0.1:8888/ </span>
              ?脣蝟餌絞??
            </div>
          </div>
        )}
        {renderTab()}
      </div>
    </div>
  );
}

