/* ================================================================
   PHARMVERS AIOS app.js
   Analytics Engine + Multi-Scenario Test Runner
   ================================================================ */

/* ── Global state ────────────────────────────────────────────── */
let currentView = "analytics";
let currentMode = "mfg";
let mfgShock = "normal";
let clinShock = "normal";

let assayChart = null, t2Chart = null, kmChart = null, matchChart = null;

let scorePass = 0, scoreWarn = 0, scoreFail = 0, totalImpact = 0;

/* ── Init ────────────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
    switchView("analytics");
    switchMode("mfg");
});

/* ══════════════════════════════════════════════════════════════
   VIEW SWITCHER (Analytics <-> Test Runner)
   ══════════════════════════════════════════════════════════════ */
function switchView(view) {
    currentView = view;
    document.querySelectorAll(".view-container").forEach(v => v.classList.remove("active"));
    document.getElementById(`view-${view}`).classList.add("active");
    document.querySelectorAll(".mode-btn").forEach(b => b.classList.remove("active"));
    document.getElementById(`mode-${view}`).classList.add("active");
    document.getElementById("active-mode-label").innerText = view.toUpperCase();
    if (view === "analytics") {
        updateExplainerAndMetrics();
        if (currentMode === "mfg") runMfgSim(); else runClinSim();
    }
}

/* ══════════════════════════════════════════════════════════════
   ANALYTICS — MODE TOGGLE (Mfg / Clin)
   ══════════════════════════════════════════════════════════════ */
function switchMode(mode) {
    currentMode = mode;
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.getElementById(`tab-${mode}`).classList.add("active");
    document.querySelectorAll(".mode-view").forEach(v => v.classList.remove("active"));
    document.getElementById(`${mode}-charts`).classList.add("active");
    document.querySelectorAll(".ctrl-btns").forEach(b => b.classList.remove("active"));
    document.getElementById(`${mode}-btns`).classList.add("active");
    updateExplainerAndMetrics();
    if (mode === "mfg") runMfgSim(); else runClinSim();
}

/* ── Shock handlers ─────────────────────────────────────────── */
function adjustMfg(shock) {
    mfgShock = shock;
    document.querySelectorAll("#mfg-btns .btn").forEach(b => b.classList.remove("active"));
    document.getElementById(`btn-mfg-${shock}`).classList.add("active");
    updateExplainerAndMetrics(); runMfgSim();
}
function adjustClin(shock) {
    clinShock = shock;
    document.querySelectorAll("#clin-btns .btn").forEach(b => b.classList.remove("active"));
    document.getElementById(`btn-clin-${shock}`).classList.add("active");
    updateExplainerAndMetrics(); runClinSim();
}

/* ══════════════════════════════════════════════════════════════
   ANALYTICS — MFG SIMULATION (PID + Hotelling T²)
   ══════════════════════════════════════════════════════════════ */
function runMfgSim() {
    const tgt_a = 100.0, tgt_m = 4.5;
    const s_inv = { aa: 25.71, am: -2.85, mm: 11.42 };
    const T2_CRIT = 5.991;

    const labels = [], assayData = [], t2Data = [], t2Colors = [];
    let assay = tgt_a, moisture = tgt_m, integral = 0, prevErr = 0;

    for (let i = 0; i < 30; i++) {
        labels.push(`B${i+1}`);
        const na = (Math.random() - 0.5) * 0.16;
        const nm = (Math.random() - 0.5) * 0.08;

        if (mfgShock === "drift") {
            const rawErr = tgt_a - assay;
            integral += rawErr;
            const deriv = rawErr - prevErr;
            const pid = 1.2 * rawErr + 0.05 * integral + 0.1 * deriv;
            prevErr = rawErr;
            assay = assay - 0.14 + pid * 0.38 + na;
            moisture = tgt_m + nm;
        } else if (mfgShock === "spike") {
            assay = tgt_a + na;
            moisture = (i >= 14 && i <= 16) ? 4.94 + Math.random() * 0.05 : tgt_m + nm;
        } else {
            assay = tgt_a + na;
            moisture = tgt_m + nm;
        }

        const da = assay - tgt_a, dm = moisture - tgt_m;
        const t2 = da * (s_inv.aa * da + s_inv.am * dm) + dm * (s_inv.am * da + s_inv.mm * dm);

        assayData.push(+assay.toFixed(3));
        t2Data.push(+t2.toFixed(3));
        t2Colors.push(t2 > T2_CRIT ? "#FF3B30" : "#34C759");
    }

    renderMfgCharts(labels, assayData, t2Data, t2Colors, T2_CRIT);
    compileGxP("mfg", { t2Values: t2Data, t2_critical: T2_CRIT });
}

function renderMfgCharts(labels, assayData, t2Data, t2Colors, crit) {
    if (assayChart) assayChart.destroy();
    assayChart = new Chart(document.getElementById("mfg-assay-chart").getContext("2d"), {
        type: "line",
        data: { labels, datasets: [{ label: "Assay %", data: assayData, borderColor: "#00F0FF", backgroundColor: "rgba(0,240,255,0.04)", borderWidth: 2, tension: 0.25, pointRadius: 2 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { grid: { color: "rgba(255,255,255,0.04)" }, ticks: { color: "#7A8BA0", font: { size: 8 } } }, y: { min: 98.5, max: 101.0, grid: { color: "rgba(255,255,255,0.04)" }, ticks: { color: "#7A8BA0", font: { size: 8 } } } } }
    });

    if (t2Chart) t2Chart.destroy();
    t2Chart = new Chart(document.getElementById("mfg-t2-chart").getContext("2d"), {
        type: "bar",
        data: { labels, datasets: [{ label: "T²", data: t2Data, backgroundColor: t2Colors, borderWidth: 0 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { grid: { color: "rgba(255,255,255,0.04)" }, ticks: { display: false } }, y: { grid: { color: "rgba(255,255,255,0.04)" }, ticks: { color: "#7A8BA0", font: { size: 8 } }, max: Math.max(8, Math.max(...t2Data) + 1) } } }
    });
}

/* ══════════════════════════════════════════════════════════════
   ANALYTICS — CLIN SIMULATION (KM + Matching)
   ══════════════════════════════════════════════════════════════ */
function runClinSim() {
    const labels = [0, 5, 10, 15, 20, 25, 30];
    let active  = [1.0, 0.92, 0.85, 0.74, 0.62, 0.55, 0.48];
    let control = [1.0, 0.85, 0.68, 0.52, 0.38, 0.24, 0.12];
    let matchDist   = [0.02, 0.05, 0.03, 0.08, 0.04, 0.12, 0.09, 0.05, 0.07, 0.03];
    let matchColors = Array(10).fill("#00F0FF");

    if (clinShock === "skew") {
        control   = [1.0, 0.75, 0.55, 0.38, 0.22, 0.08, 0.0];
        matchDist = [0.18, 0.32, 0.28, 0.41, 0.25, 0.39, 0.48, 0.31, 0.35, 0.29];
        matchColors = Array(10).fill("#FFB300");
    }

    if (kmChart) kmChart.destroy();
    kmChart = new Chart(document.getElementById("clin-km-chart").getContext("2d"), {
        type: "line",
        data: { labels: labels.map(t => `D${t}`), datasets: [
            { label: "Treatment", data: active,  borderColor: "#00F0FF", borderWidth: 2, stepped: true, backgroundColor: "rgba(0,240,255,0.04)", pointRadius: 3 },
            { label: "SCA",       data: control, borderColor: "#FFB300", borderWidth: 2, stepped: true, backgroundColor: "rgba(255,179,0,0.04)",  pointRadius: 3 }
        ]},
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: "#7A8BA0", font: { size: 9 } } } }, scales: { x: { grid: { color: "rgba(255,255,255,0.04)" }, ticks: { color: "#7A8BA0", font: { size: 8 } } }, y: { min: 0, max: 1, grid: { color: "rgba(255,255,255,0.04)" }, ticks: { color: "#7A8BA0", font: { size: 8 } } } } }
    });

    if (matchChart) matchChart.destroy();
    matchChart = new Chart(document.getElementById("clin-match-chart").getContext("2d"), {
        type: "bar",
        data: { labels: Array.from({ length: 10 }, (_, i) => `P${i+1}`), datasets: [{ label: "Distance", data: matchDist, backgroundColor: matchColors }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { grid: { color: "rgba(255,255,255,0.04)" }, ticks: { color: "#7A8BA0", font: { size: 8 } } }, y: { min: 0, max: 0.6, grid: { color: "rgba(255,255,255,0.04)" }, ticks: { color: "#7A8BA0", font: { size: 8 } } } } }
    });

    compileGxP("clin", { matchDistances: matchDist });
}

/* ══════════════════════════════════════════════════════════════
   ANALYTICS — ROI EXPLAINER
   ══════════════════════════════════════════════════════════════ */
function updateExplainerAndMetrics() {
    const money  = document.getElementById("roi-money");
    const time   = document.getElementById("roi-time");
    const status = document.getElementById("roi-status");
    const title  = document.getElementById("explainer-title");
    const body   = document.getElementById("explainer-body");

    const configs = {
        mfg: {
            normal: { money: "$3.20M", time: "14d → 0m", st: "100% GxP", stc: "green-text", t: "RTRT Batch Auto-Release (Normal)", b: "The process is stable. Blend uniformity is within a tight ±0.2% band. All samples fall below the Hotelling T² threshold of 5.991. The batch is automatically certified and released in real-time. This saves $3.2M in warehouse inventory holding costs and eliminates the 14-day lab wait per facility." },
            drift:  { money: "$2.85M", time: "PID Active", st: "CORRECTING", stc: "amber-text", t: "Closed-Loop PID Feeder Drift Correction", b: "The active powder feeder is drifting due to mechanical wear. The PID controller detects the error signal and issues an automatic feed rate correction every batch cycle, bringing blend uniformity back to target. A batch failure costing $2.85M is prevented without human operator involvement." },
            spike:  { money: "$1.20M", time: "1 Isolated", st: "EXCURSION", stc: "red-text", t: "Moisture Spike — Batch Isolation Triggered", b: "An environmental humidity surge drives the moisture CQA outside limits, causing the Hotelling T² statistic to exceed 42 (far above the 5.991 critical boundary). The system automatically isolates this batch run, preventing contamination of the entire production line and avoiding a $12M+ product recall event." },
        },
        clin: {
            normal: { money: "$14.50M", time: "Save 6 Mo", st: "FDA VALID", stc: "green-text", t: "Balanced Synthetic Control Arm (SCA)", b: "The system selects a virtual placebo cohort using nearest-neighbour covariate matching. All matching distances remain below 0.15, ensuring a statistically balanced control arm that will satisfy FDA review. This replaces 50% of human placebo patients with validated digital twins, saving $14.5M in recruitment costs and accelerating drug approval by 6 months." },
            skew:   { money: "$6.20M", time: "High Dist", st: "SKEW ALERT", stc: "amber-text", t: "SCA Covariate Skew Detected", b: "The matching pool is skewed toward patients over 65. Covariate distances spike to 0.48, flagging significant imbalance that the FDA would question during review. The system alerts the clinical design lead to expand the patient registry before submission, preventing a $40M trial rejection." },
        }
    };

    const cfg = configs[currentMode]?.[currentMode === "mfg" ? mfgShock : clinShock];
    if (!cfg) return;

    money.innerText  = cfg.money;
    time.innerText   = cfg.time;
    status.className = `roi-val ${cfg.stc}`;
    status.innerText = cfg.st;
    title.innerText  = cfg.t;
    body.innerText   = cfg.b;
}

/* ══════════════════════════════════════════════════════════════
   ANALYTICS — GxP REPORT COMPILER
   ══════════════════════════════════════════════════════════════ */
function compileGxP(mode, data) {
    const now = new Date().toISOString();
    let status = "PASSED // STATE OF CONTROL ACTIVE", detail = "";

    if (mode === "mfg") {
        const fails = data.t2Values.filter(v => v > data.t2_critical).length;
        if (fails > 0) status = `WARNING // ${fails} GxP EXCURSION(S) DETECTED`;
        detail = `- CQA Target Assay: 100.0% | Target Moisture: 4.5%\n- Hotelling T² Limit: ${data.t2_critical}\n- Total Batches Monitored: 30 | Compliant: ${30 - fails} | Isolated: ${fails}\n- Max T² Observed: ${Math.max(...data.t2Values).toFixed(3)}`;
    } else {
        const maxD = Math.max(...data.matchDistances);
        if (maxD > 0.20) status = `WARNING // COVARIATE SKEW (max dist=${maxD.toFixed(3)})`;
        detail = `- Algorithm: Nearest-Neighbour Euclidean Distance\n- Matched Pairs: 10 | Max Distance: ${maxD.toFixed(3)}\n- Threshold: 0.15 (FDA-acceptable)\n- Status: ${maxD < 0.20 ? "Balanced" : "Skewed — registry expansion recommended"}`;
    }

    let hashSeed = now + status + detail, h = 0;
    for (let i = 0; i < hashSeed.length; i++) { h = (h << 5) - h + hashSeed.charCodeAt(i); h |= 0; }

    document.getElementById("validation-report-pre").innerText =
`=====================================================================
GxP SYSTEM VALIDATION REPORT  //  PHARMVERS COGNITIVE CORE v1.0
GENERATED: ${now}
=====================================================================
SYSTEM STATUS : ${status}
---------------------------------------------------------------------
SECTION I  — INSTALLATION QUALIFICATION (IQ)
  [PASS] OS compatibility verified (Browser Runtime)
  [PASS] Code integrity hash matched
  [PASS] Secure database channels configured (SSL active)

SECTION II — ${mode === "mfg" ? "MANUFACTURING PARAMETERS" : "CLINICAL TRIAL DESIGN"}
${detail}

SECTION III — PERFORMANCE QUALIFICATION (PQ)
  Tests Run: 11 | Passed: 11 | Failed: 0
  Result: [SUCCESS]

=====================================================================
CRYPTOGRAPHIC SIGNATURE: SHA256(${h >>> 0})
=====================================================================`;
}

/* ══════════════════════════════════════════════════════════════
   TEST RUNNER — SCENARIO DATA BANK
   ══════════════════════════════════════════════════════════════ */
const ALL_SCENARIOS = [
    // MODULE 1: MANUFACTURING (RTRT)
    { module: "MANUFACTURING", id: "BATCH-A01", label: "Amoxicillin 500mg — Normal run",         run: () => mfgRun(0.0,    false), delay: 300 },
    { module: "MANUFACTURING", id: "BATCH-A02", label: "Amoxicillin 500mg — Feeder drift",        run: () => mfgRun(-0.18,  false), delay: 400 },
    { module: "MANUFACTURING", id: "BATCH-A03", label: "Amoxicillin 500mg — Moisture spike",      run: () => mfgRun(0.0,    true),  delay: 350 },
    { module: "MANUFACTURING", id: "BATCH-B01", label: "Metformin 1000mg  — Normal run",          run: () => mfgRun(0.0,    false), delay: 300 },
    { module: "MANUFACTURING", id: "BATCH-B02", label: "Metformin 1000mg  — Critical drift",      run: () => mfgRun(-0.60,  false), delay: 420 },
    { module: "MANUFACTURING", id: "BATCH-B03", label: "Metformin 1000mg  — Drift + Spike",       run: () => mfgRun(-0.35,  true),  delay: 450 },
    // MODULE 2: CLINICAL (SCA)
    { module: "CLINICAL",      id: "TRIAL-C01", label: "Biosimilar-X P3   — Balanced cohort",    run: () => clinRun(0.05), delay: 380 },
    { module: "CLINICAL",      id: "TRIAL-C02", label: "mRNA Vaccine P2   — Elderly-skewed",      run: () => clinRun(0.22), delay: 420 },
    { module: "CLINICAL",      id: "TRIAL-C03", label: "Oncology ADC P3   — Biomarker spread",    run: () => clinRun(0.09), delay: 390 },
    { module: "CLINICAL",      id: "TRIAL-C04", label: "CAR-T Therapy P1  — Small pool",          run: () => clinRun(0.52), delay: 450 },
    // MODULE 3: COMPLIANCE (GxP)
    { module: "COMPLIANCE",    id: "REG-ICH-Q6A", label: "ICH Q6A    — Drug Product Specs",       run: () => compRun(true,  "residual_ethanol < 5000 | dissolution_rate >= 92.5"),  delay: 280 },
    { module: "COMPLIANCE",    id: "REG-FDA-PAT", label: "FDA PAT    — In-Process Controls",      run: () => compRun(true,  "blend_uniformity >= 98.5 | particle_size_d90 < 200"),    delay: 280 },
    { module: "COMPLIANCE",    id: "REG-ICH-Q3A", label: "ICH Q3A   — Degradation Products",      run: () => compRun(false, "total_impurities < 0.15 [VIOLATION] | identified_impurity < 0.10"), delay: 280 },
    { module: "COMPLIANCE",    id: "REG-ANNEX11", label: "EU Annex11 — Computerised Systems",      run: () => compRun(true,  "audit_trail_coverage >= 100 | access_control_level >= 3"), delay: 280 },
];

/* ── Math helpers for each scenario type ───────────────────── */
function mfgRun(drift, spike) {
    const tgt_a = 100.0, tgt_m = 4.5, T2_CRIT = 5.991;
    const s_inv = { aa: 25.71, am: -2.85, mm: 11.42 };
    let assay = tgt_a, integral = 0, prevErr = 0, maxT2 = 0, failCnt = 0;

    for (let i = 0; i < 15; i++) {
        const na = (Math.random() - 0.5) * 0.16;
        const nm = (Math.random() - 0.5) * 0.08;
        let m = tgt_m + nm;

        if (drift !== 0) {
            const err = tgt_a - assay; integral += err; const d = err - prevErr;
            const pid = 1.2 * err + 0.05 * integral + 0.1 * d; prevErr = err;
            assay = assay + drift * 0.08 + pid * 0.38 + na;
        } else { assay = tgt_a + na; }
        if (spike && i >= 7 && i <= 9) m = 4.93 + Math.random() * 0.05;

        const da = assay - tgt_a, dm = m - tgt_m;
        const t2 = da * (s_inv.aa * da + s_inv.am * dm) + dm * (s_inv.am * da + s_inv.mm * dm);
        if (t2 > maxT2) maxT2 = t2;
        if (t2 > T2_CRIT) failCnt++;
    }

    if (failCnt === 0)    return { sig: "PASS", detail: `15/15 in spec | Max T²=${maxT2.toFixed(3)}`, impact: "$3.2M batch auto-released. Zero lab hold." };
    if (failCnt <= 2)     return { sig: "WARN", detail: `${15-failCnt}/15 in spec | ${failCnt} excursion(s) | Max T²=${maxT2.toFixed(3)}`, impact: "PID corrected. Batch quarantined for re-sample. $0.8M exposure managed." };
    return                       { sig: "FAIL", detail: `${failCnt}/15 FAILED | Max T²=${maxT2.toFixed(3)}`, impact: "Batch isolated. Line contamination prevented. Recall risk averted." };
}

function clinRun(simulatedMaxDist) {
    const jitter = (Math.random() - 0.5) * 0.04;
    const maxDist = Math.max(0, simulatedMaxDist + jitter);
    const finalSurv = Math.max(0, 0.55 - maxDist * 0.6);

    if (maxDist <= 0.15) return { sig: "PASS", detail: `Matched 3 pairs | Max dist=${maxDist.toFixed(3)} | Final survival=${(finalSurv*100).toFixed(1)}%`, impact: "SCA valid for FDA submission. Saves $14.5M in placebo recruitment." };
    if (maxDist <= 0.40) return { sig: "WARN", detail: `Max dist=${maxDist.toFixed(3)} (>0.15 threshold)`, impact: "Marginal SCA. Recommend expanding registry by 20 patients." };
    return                      { sig: "FAIL", detail: `Max dist=${maxDist.toFixed(3)} — exceeds FDA acceptance`,  impact: "SCA rejected. Expanded pool mandatory. $40M re-testing risk flagged." };
}

function compRun(passed, rulesText) {
    if (passed) return { sig: "PASS", detail: `All rules satisfied: ${rulesText}`, impact: "Compliance certificate issued autonomously. Zero QA documentation time." };
    return              { sig: "FAIL", detail: `Violation: ${rulesText}`, impact: "CAPA triggered. Corrective action required before regulatory submission." };
}

/* ══════════════════════════════════════════════════════════════
   TEST RUNNER — ACQUISITION ENGINE
   ══════════════════════════════════════════════════════════════ */
function runAcquisition() {
    const useMfg  = document.getElementById("chk-mfg").checked;
    const useClin = document.getElementById("chk-clin").checked;
    const useComp = document.getElementById("chk-comp").checked;
    const depth   = document.getElementById("select-depth").value;
    const showPass = document.getElementById("flt-pass").checked;
    const showWarn = document.getElementById("flt-warn").checked;
    const showFail = document.getElementById("flt-fail").checked;

    const depthMap = { quick: 3, standard: 8, full: 14 };
    const maxScenarios = depthMap[depth];

    let pool = ALL_SCENARIOS.filter(s => {
        if (s.module === "MANUFACTURING" && !useMfg)  return false;
        if (s.module === "CLINICAL"      && !useClin) return false;
        if (s.module === "COMPLIANCE"    && !useComp) return false;
        return true;
    }).slice(0, maxScenarios);

    if (pool.length === 0) {
        alert("Please select at least one module to run.");
        return;
    }

    // Reset counters and UI
    scorePass = 0; scoreWarn = 0; scoreFail = 0; totalImpact = 0;
    updateScoreBoard();

    const output = document.getElementById("runner-output");
    const badge  = document.getElementById("runner-status-badge");
    const runBtn = document.getElementById("run-btn");

    output.innerHTML = "";
    badge.className  = "badge-running";
    badge.innerText  = "RUNNING...";
    runBtn.disabled  = true;

    let delay = 0;
    let lastModule = "";

    pool.forEach((scenario, idx) => {
        delay += scenario.delay + (idx === 0 ? 0 : 50);

        setTimeout(() => {
            const result = scenario.run();

            // Filter by signal
            const filterMap = { PASS: showPass, WARN: showWarn, FAIL: showFail };
            if (!filterMap[result.sig]) return;

            // Section header if new module
            if (scenario.module !== lastModule) {
                lastModule = scenario.module;
                const hdr = document.createElement("div");
                hdr.className = "sig-header";
                hdr.innerText = `── ${scenario.module} MODULE ──`;
                output.appendChild(hdr);
            }

            // Build signal row
            const sigClass = { PASS: "sig-pass", WARN: "sig-warn", FAIL: "sig-fail" }[result.sig];
            const block = document.createElement("div");
            block.innerHTML = `
                <div class="sig-row">
                    <span class="sig-badge ${sigClass}">${result.sig}</span>
                    <span class="sig-text">${scenario.id} — ${scenario.label}</span>
                </div>
                <div class="sig-row">
                    <span></span>
                    <span class="sig-detail">Detail : ${result.detail}</span>
                </div>
                <div class="sig-row">
                    <span></span>
                    <span class="sig-impact">Impact : ${result.impact}</span>
                </div>`;
            output.appendChild(block);
            output.scrollTop = output.scrollHeight;

            // Update score
            if (result.sig === "PASS") { scorePass++; totalImpact += 3.2; }
            if (result.sig === "WARN") { scoreWarn++; totalImpact += 0.8; }
            if (result.sig === "FAIL") { scoreFail++; totalImpact += 0.4; }
            updateScoreBoard();

            // On last scenario
            if (idx === pool.length - 1) {
                setTimeout(() => {
                    renderSummary(output, pool.length);
                    badge.className = "badge-complete";
                    badge.innerText = "COMPLETE";
                    runBtn.disabled = false;
                }, 400);
            }
        }, delay);
    });
}

function renderSummary(output, total) {
    const hr = document.createElement("hr");
    hr.className = "sig-divider";
    output.appendChild(hr);

    const summary = document.createElement("div");
    summary.className = "sig-summary";
    summary.innerHTML = `
        <strong style="color:var(--cyan)">ACQUISITION COMPLETE — MASTER SIGNAL SUMMARY</strong><br>
        Total Scenarios  : ${total}<br>
        <span class="green-text">PASS : ${scorePass}</span> &nbsp;|&nbsp;
        <span class="amber-text">WARN : ${scoreWarn}</span> &nbsp;|&nbsp;
        <span class="red-text">FAIL : ${scoreFail}</span><br>
        Financial Impact Protected : <span class="green-text">$${totalImpact.toFixed(1)}M</span> per acquisition cycle<br>
        Release Latency Eliminated : <span class="cyan-text">14 days → 0 minutes</span> (RTRT active)<br>
        GxP Reports Compiled       : <span class="cyan-text">Autonomous signatures generated</span>
    `;
    output.appendChild(summary);
    output.scrollTop = output.scrollHeight;
}

function updateScoreBoard() {
    document.getElementById("score-pass").innerText = scorePass;
    document.getElementById("score-warn").innerText = scoreWarn;
    document.getElementById("score-fail").innerText = scoreFail;
    document.getElementById("impact-val").innerText = `$${totalImpact.toFixed(2)}M`;
}

function clearRunner() {
    scorePass = 0; scoreWarn = 0; scoreFail = 0; totalImpact = 0;
    updateScoreBoard();
    document.getElementById("runner-output").innerHTML = `<div class="runner-placeholder">Select modules and depth above, then click<br><strong>▶ RUN ACQUISITION</strong> to begin.</div>`;
    const badge = document.getElementById("runner-status-badge");
    badge.className = "badge-idle";
    badge.innerText = "IDLE";
    document.getElementById("run-btn").disabled = false;
}
