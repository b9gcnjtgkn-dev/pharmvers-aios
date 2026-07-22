"""
PHARMVERS AIOS — Multi-Scenario Demo Runner
==============================================
Runs multiple real-world simulation scenarios across:
  - Manufacturing (RTRT): batch quality acquisition runs
  - Clinical Trials (SCA): patient cohort acquisition runs
  - Compliance (GxP): regulatory rule validation runs

Output signals:
  [PASS]  System nominal, auto-release approved
  [WARN]  Anomaly detected, corrective action taken
  [FAIL]  Critical excursion, batch/trial isolated

Run with: python3 demo_runner.py
"""

import math
import random
import datetime
from pharmvers_core.rtrt_engine import BioreactorPATController
from pharmvers_core.clinops_engine import SyntheticTrialSimulator
from pharmvers_core.compliance_compiler import RegulatoryVerificationCompiler

# ─────────────────────────────────────────────────────────────────
# DISPLAY UTILITIES
# ─────────────────────────────────────────────────────────────────

def header(title):
    print("\n" + "=" * 72)
    print(f"  {title}")
    print("=" * 72)

def section(title):
    print(f"\n  >> {title}")

def signal_line(status, label, detail, impact):
    icons = {"PASS": "[OK]", "WARN": "[!!]", "FAIL": "[XX]"}
    icon = icons[status]
    print(f"  {icon} {status}  |  {label}")
    print(f"           Detail : {detail}")
    print(f"           Impact : {impact}")
    print()

def summary_table(results):
    total  = len(results)
    passed = results.count("PASS")
    warned = results.count("WARN")
    failed = results.count("FAIL")
    print(f"  {'─' * 68}")
    print(f"  RESULTS   Total: {total}   [OK] Passed: {passed}   [!!] Warned: {warned}   [XX] Failed: {failed}")
    print(f"  {'─' * 68}")


# ─────────────────────────────────────────────────────────────────
# MODULE 1: MANUFACTURING — RTRT BATCH ACQUISITION RUNS
# check_rtrt_release returns: (is_released, failed_count, max_t2)
# calculate_pid_adjustment returns: float (the adjustment value)
# ─────────────────────────────────────────────────────────────────

def run_manufacturing_module():
    header("MODULE 1 — REAL-TIME RELEASE TESTING (RTRT) | BATCH ACQUISITION RUNS")
    print("  Simulating 6 production batches. Each acquires 15 in-line sensor readings.\n")

    scenarios = [
        {"id": "BATCH-A01", "product": "Amoxicillin 500mg", "desc": "Normal run — all CQAs nominal",          "drift": 0.0,   "spike": False},
        {"id": "BATCH-A02", "product": "Amoxicillin 500mg", "desc": "Minor feeder wear — assay drifting low", "drift": -0.18, "spike": False},
        {"id": "BATCH-A03", "product": "Amoxicillin 500mg", "desc": "Environmental moisture surge at sample 8","drift": 0.0,   "spike": True},
        {"id": "BATCH-B01", "product": "Metformin 1000mg",  "desc": "Normal run — all CQAs nominal",          "drift": 0.0,   "spike": False},
        {"id": "BATCH-B02", "product": "Metformin 1000mg",  "desc": "Severe API blend segregation — critical drift","drift": -0.60,"spike": False},
        {"id": "BATCH-B03", "product": "Metformin 1000mg",  "desc": "Worst case: drift + moisture spike",     "drift": -0.35, "spike": True},
    ]

    all_results = []

    for s in scenarios:
        section(f"{s['id']} | {s['product']} | {s['desc']}")

        engine = BioreactorPATController(target_assay=100.0, target_moisture=4.5)
        batch_measurements = []
        random.seed(s["id"].__hash__() % 1000)

        for i in range(15):
            assay    = 100.0 + (random.random() - 0.5) * 0.16
            moisture = 4.5   + (random.random() - 0.5) * 0.08

            if s["drift"] != 0.0:
                assay += s["drift"] * (i * 0.08)
                pid_adj = engine.calculate_pid_adjustment(assay)
                assay  += pid_adj * 0.35

            if s["spike"] and 7 <= i <= 9:
                moisture = 4.93 + random.random() * 0.05

            batch_measurements.append({
                "sample_id": i + 1,
                "assay":     round(assay, 4),
                "moisture":  round(moisture, 4)
            })

        # Returns tuple: (is_released, failed_count, max_t2)
        is_released, failed_count, max_t2 = engine.check_rtrt_release(batch_measurements)

        if is_released:
            sig    = "PASS"
            detail = f"15/15 samples in spec | Max T²={max_t2:.3f} (limit=5.991)"
            impact = "$3.2M batch auto-released. Zero 14-day lab hold required."
        elif failed_count <= 2:
            sig    = "WARN"
            detail = f"{15-failed_count}/15 in spec | {failed_count} excursion(s) | Max T²={max_t2:.3f}"
            impact = "PID corrected drift. Batch quarantined for re-sampling. $0.8M exposure managed."
        else:
            sig    = "FAIL"
            detail = f"{failed_count}/15 samples FAILED | Max T²={max_t2:.3f} — critical excursion"
            impact = "Batch isolated. Full production line contamination prevented. Recall risk averted."

        signal_line(sig, f"{s['id']} ({s['product']})", detail, impact)
        all_results.append(sig)

    summary_table(all_results)
    return all_results


# ─────────────────────────────────────────────────────────────────
# MODULE 2: CLINICAL TRIALS — PATIENT COHORT ACQUISITION RUNS
# match_synthetic_control returns: list of matched patient dicts (no .distance key)
# calculate_kaplan_meier takes: list of (time, event_int) tuples
# ─────────────────────────────────────────────────────────────────

def run_clinical_module():
    header("MODULE 2 — IN-SILICO CLINICAL TRIALS (SCA) | COHORT ACQUISITION RUNS")
    print("  Simulating 4 patient cohort matching scenarios with Kaplan-Meier curves.\n")

    engine = SyntheticTrialSimulator()

    scenarios = [
        {
            "id": "TRIAL-C01", "drug": "Biosimilar-X Phase 3",
            "desc": "Balanced cohort — equal age and biomarker distribution",
            "treatment": [{"id":"T1","age":45,"biomarker":3.2},{"id":"T2","age":52,"biomarker":4.1},{"id":"T3","age":61,"biomarker":2.8}],
            "pool":      [{"id":"C1","age":44,"biomarker":3.1},{"id":"C2","age":70,"biomarker":6.0},{"id":"C3","age":53,"biomarker":4.3},{"id":"C4","age":60,"biomarker":2.9},{"id":"C5","age":38,"biomarker":1.8}],
            "events":    [(15,1),(20,1),(25,0),(10,1),(5,1),(25,0)],
        },
        {
            "id": "TRIAL-C02", "drug": "mRNA Vaccine Phase 2",
            "desc": "Elderly-skewed cohort — high matching distance expected",
            "treatment": [{"id":"T1","age":72,"biomarker":5.8},{"id":"T2","age":68,"biomarker":6.2},{"id":"T3","age":75,"biomarker":5.5}],
            "pool":      [{"id":"C1","age":35,"biomarker":2.1},{"id":"C2","age":40,"biomarker":2.8},{"id":"C3","age":71,"biomarker":5.9},{"id":"C4","age":30,"biomarker":1.5},{"id":"C5","age":69,"biomarker":6.0}],
            "events":    [(10,1),(20,0),(8,1),(12,1),(7,1)],
        },
        {
            "id": "TRIAL-C03", "drug": "Oncology ADC Phase 3",
            "desc": "Large biomarker spread — critical matching threshold test",
            "treatment": [{"id":"T1","age":55,"biomarker":8.1},{"id":"T2","age":49,"biomarker":7.4},{"id":"T3","age":63,"biomarker":9.0}],
            "pool":      [{"id":"C1","age":54,"biomarker":8.0},{"id":"C2","age":30,"biomarker":1.0},{"id":"C3","age":48,"biomarker":7.5},{"id":"C4","age":20,"biomarker":0.8},{"id":"C5","age":62,"biomarker":8.8}],
            "events":    [(12,1),(18,1),(22,0),(9,1),(14,1),(22,0)],
        },
        {
            "id": "TRIAL-C04", "drug": "CAR-T Therapy Phase 1",
            "desc": "Small pool — limited match candidates available",
            "treatment": [{"id":"T1","age":58,"biomarker":4.5},{"id":"T2","age":61,"biomarker":5.0},{"id":"T3","age":47,"biomarker":3.9}],
            "pool":      [{"id":"C1","age":25,"biomarker":1.1},{"id":"C2","age":80,"biomarker":9.5}],
            "events":    [(8,1),(18,0),(15,1),(5,1),(3,1)],
        },
    ]

    all_results = []

    for s in scenarios:
        section(f"{s['id']} | {s['drug']} | {s['desc']}")

        # match_synthetic_control returns list of patient dicts (no distance key)
        matched = engine.match_synthetic_control(s["treatment"], s["pool"])

        # Compute distance manually using normalized covariates to classify quality
        combined_for_norm = engine.normalize_covariates(s["treatment"] + s["pool"])
        norm_treatment = combined_for_norm[:len(s["treatment"])]
        norm_pool      = combined_for_norm[len(s["treatment"]):]

        distances = []
        used_ids  = set()
        for t in norm_treatment:
            best_dist = float("inf")
            for p in norm_pool:
                if p["id"] in used_ids:
                    continue
                dist = math.sqrt((t["norm_age"] - p["norm_age"])**2 + (t["norm_biomarker"] - p["norm_biomarker"])**2)
                if dist < best_dist:
                    best_dist = dist
                    best_p = p
            if best_dist < float("inf"):
                distances.append(best_dist)
                used_ids.add(best_p["id"])

        max_dist = max(distances) if distances else 1.0

        # calculate_kaplan_meier takes list of (time, event_int) tuples
        km = engine.calculate_kaplan_meier(s["events"])
        final_survival = km[-1]["survival_probability"] if km else 0.0

        if max_dist <= 0.15:
            sig    = "PASS"
            detail = f"Matched {len(matched)} pairs | Max dist={max_dist:.3f} | Final KM survival={final_survival:.1%}"
            impact = f"SCA valid for FDA submission. Saves $14.5M in placebo recruitment for {s['drug']}."
        elif max_dist <= 0.40:
            sig    = "WARN"
            detail = f"Matched {len(matched)} pairs | Max dist={max_dist:.3f} (threshold=0.15)"
            impact = "Marginal SCA. Recommend expanding patient registry by 20 before FDA submission."
        else:
            sig    = "FAIL"
            detail = f"Max covariate dist={max_dist:.3f} — exceeds FDA acceptance threshold"
            impact = "SCA rejected. Pool expansion mandatory. $40M re-testing risk flagged."

        signal_line(sig, f"{s['id']} ({s['drug']})", detail, impact)
        all_results.append(sig)

    summary_table(all_results)
    return all_results


# ─────────────────────────────────────────────────────────────────
# MODULE 3: COMPLIANCE — MULTI-REGULATION ACQUISITION RUNS
# verify_parameters returns: (bool, failures_list)  — a tuple
# ─────────────────────────────────────────────────────────────────

def run_compliance_module():
    header("MODULE 3 — GxP COMPLIANCE COMPILER | REGULATORY ACQUISITION RUNS")
    print("  Parsing 4 FDA/ICH/EMA guidance texts and validating system parameters.\n")

    compiler = RegulatoryVerificationCompiler()

    scenarios = [
        {
            "id": "REG-ICH-Q6A", "standard": "ICH Q6A — Drug Product Specifications",
            "guidance": "LIMIT: residual_ethanol < 5000\nLIMIT: dissolution_rate >= 92.5",
            "params":   {"residual_ethanol": 4200, "dissolution_rate": 94.1},
        },
        {
            "id": "REG-FDA-PAT", "standard": "FDA PAT Guidance — In-Process Controls",
            "guidance": "LIMIT: blend_uniformity >= 98.5\nLIMIT: particle_size_d90 < 200",
            "params":   {"blend_uniformity": 99.2, "particle_size_d90": 185},
        },
        {
            "id": "REG-ICH-Q3A", "standard": "ICH Q3A — Degradation Products",
            "guidance": "LIMIT: total_impurities < 0.15\nLIMIT: identified_impurity < 0.10",
            "params":   {"total_impurities": 0.22, "identified_impurity": 0.09},
        },
        {
            "id": "REG-ANNEX11", "standard": "EU Annex 11 — Computerised Systems",
            "guidance": "LIMIT: audit_trail_coverage >= 100\nLIMIT: access_control_level >= 3",
            "params":   {"audit_trail_coverage": 100, "access_control_level": 4},
        },
    ]

    all_results = []

    for s in scenarios:
        section(f"{s['id']} | {s['standard']}")

        rules = compiler.parse_guidance_rules(s["guidance"])
        # verify_parameters returns a TUPLE: (bool_passed, failures_list)
        passed, failures = compiler.verify_parameters(s["params"], rules)

        if passed:
            sig    = "PASS"
            detail = f"All {len(rules)} rules satisfied | Parameters within regulatory limits"
            impact = "Compliance certificate issued autonomously. Zero manual QA documentation needed."
        else:
            sig    = "FAIL"
            detail = f"{len(failures)} violation(s): {' | '.join(failures)}"
            impact = "CAPA triggered. Corrective action required before regulatory submission."

        signal_line(sig, f"{s['id']}", detail, impact)
        all_results.append(sig)

    summary_table(all_results)
    return all_results


# ─────────────────────────────────────────────────────────────────
# MASTER RUNNER
# ─────────────────────────────────────────────────────────────────

def main():
    print("\n" + "#" * 72)
    print("  PHARMVERS AIOS — MULTI-SCENARIO ACQUISITION & SIGNAL DEMO RUNNER")
    print(f"  Timestamp : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("  Mode      : Executive Presentation Mode")
    print("  Modules   : Manufacturing (RTRT) | Clinical (SCA) | Compliance (GxP)")
    print("#" * 72)

    mfg_results  = run_manufacturing_module()
    clin_results = run_clinical_module()
    comp_results = run_compliance_module()

    all_results = mfg_results + clin_results + comp_results
    total   = len(all_results)
    passed  = all_results.count("PASS")
    warned  = all_results.count("WARN")
    failed  = all_results.count("FAIL")

    savings      = {"PASS": 3.2, "WARN": 0.8, "FAIL": 0.4}
    total_impact = sum(savings[r] for r in all_results)

    print("\n" + "#" * 72)
    print("  MASTER ACQUISITION SUMMARY — ALL MODULES")
    print("#" * 72)
    print(f"  Total Scenarios Run        : {total}")
    print(f"  [OK] Passed (Auto-Released): {passed}  ({passed/total*100:.0f}%)")
    print(f"  [!!] Warned (Managed)      : {warned}")
    print(f"  [XX] Failed (Isolated)     : {failed}")
    print(f"")
    print(f"  FINANCIAL IMPACT PROTECTED : ${total_impact:.1f}M per acquisition cycle")
    print(f"  RELEASE LATENCY ELIMINATED : 14 days  -->  0 minutes  (RTRT active)")
    print(f"  GxP REPORTS COMPILED       : {len(comp_results)} autonomous validation reports")
    print(f"  CLINICAL COST SAVED        : up to $14.5M per SCA-valid trial")
    print("\n" + "#" * 72)
    print("  ALL RUNS COMPLETE. PHARMVERS AIOS READY FOR CLIENT DEMONSTRATION.")
    print("#" * 72 + "\n")

if __name__ == "__main__":
    main()
