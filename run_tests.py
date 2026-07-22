import os
import sys
import functools

# Force unbuffered stdout so test results print instantly
print = functools.partial(print, flush=True)

# Add pharmvers_core folder to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "pharmvers_core"))

from pharmvers_core.rtrt_engine import BioreactorPATController
from pharmvers_core.clinops_engine import SyntheticTrialSimulator
from pharmvers_core.compliance_compiler import RegulatoryVerificationCompiler

def run_all_tests():
    print("======================================================================")
    print("RUNNING PHARMVERS COGNITIVE CORE VERIFICATION SUITE")
    print("======================================================================")
    
    test_suite = {
        "suite_name": "Pharmvers Cognitive Core TestSuite",
        "total": 0,
        "passed": 0,
        "failed": 0,
        "success": True
    }
    
    def log_result(test_name, success, message=""):
        test_suite["total"] += 1
        if success:
            test_suite["passed"] += 1
            print(f"[PASS] {test_name} - {message}")
        else:
            test_suite["failed"] += 1
            test_suite["success"] = False
            print(f"[FAIL] {test_name} - {message}")

    # ----------------------------------------------------------------------
    # TEST 1: Bioreactor RTRT PID & Hotelling T2 Calculations
    # ----------------------------------------------------------------------
    print("\n--- Testing Chapter 1: RTRT & Continuous Manufacturing ---")
    rtrt_controller = BioreactorPATController(target_assay=100.0, target_moisture=4.5)
    
    # 1.1 Test PID adjustment math
    adj = rtrt_controller.calculate_pid_adjustment(current_assay=98.5)
    # Expected: positive adjustment since current assay is below target
    log_result("PID Feeder Adjustment", adj > 0, f"Calculated feed rate adjustment: {adj:.4f}")
    
    # 1.2 Test Hotelling T^2 calculation inside control bounds
    t2_good = rtrt_controller.calculate_hotelling_t2(assay=100.1, moisture=4.52)
    # Expected: low T^2 (should be below t2_critical = 5.991)
    log_result("Hotelling T2 In-Bounds", t2_good <= rtrt_controller.t2_critical, f"Normal sample T^2 value: {t2_good:.4f}")
    
    # 1.3 Test Hotelling T^2 calculation out of bounds
    t2_bad = rtrt_controller.calculate_hotelling_t2(assay=98.8, moisture=4.95)
    # Expected: high T^2 (should exceed 5.991)
    log_result("Hotelling T2 Out-of-Bounds", t2_bad > rtrt_controller.t2_critical, f"Out-of-specification T^2 value: {t2_bad:.4f}")
    
    # 1.4 Test Batch Release check
    good_batch = [
        {"assay": 100.02, "moisture": 4.51},
        {"assay": 99.98, "moisture": 4.49},
        {"assay": 100.05, "moisture": 4.52}
    ]
    released, failed, max_t2 = rtrt_controller.check_rtrt_release(good_batch)
    log_result("Batch RTRT Auto-Release Pass", released == True and failed == 0, f"Batch release status: {released}, Max T^2: {max_t2:.4f}")
    
    bad_batch = [
        {"assay": 100.02, "moisture": 4.51},
        {"assay": 98.20, "moisture": 4.98}, # Out of bounds
        {"assay": 100.05, "moisture": 4.52}
    ]
    released_bad, failed_bad, max_t2_bad = rtrt_controller.check_rtrt_release(bad_batch)
    log_result("Batch RTRT Auto-Release Reject", released_bad == False and failed_bad == 1, f"Batch release status: {released_bad}, Failed samples: {failed_bad}, Max T^2: {max_t2_bad:.4f}")

    # ----------------------------------------------------------------------
    # TEST 2: Clinical Trial Synthetic Control Arm & KM Math
    # ----------------------------------------------------------------------
    print("\n--- Testing Chapter 2: In-Silico Trials & Synthetic Control ---")
    clin_simulator = SyntheticTrialSimulator()
    
    # 2.1 Test Propensity Score Covariate Matching
    treatment = [
        {"id": "T1", "age": 45, "biomarker": 2.4},
        {"id": "T2", "age": 60, "biomarker": 5.1}
    ]
    pool = [
        {"id": "C1", "age": 46, "biomarker": 2.3}, # Match for T1
        {"id": "C2", "age": 30, "biomarker": 1.2},
        {"id": "C3", "age": 59, "biomarker": 5.2}, # Match for T2
        {"id": "C4", "age": 65, "biomarker": 1.8}
    ]
    matched = clin_simulator.match_synthetic_control(treatment, pool)
    matched_ids = [p["id"] for p in matched]
    log_result("Propensity Score Matcher", "C1" in matched_ids and "C3" in matched_ids, f"Matched control IDs: {matched_ids}")
    
    # 2.2 Test Kaplan-Meier survival probability math
    events = [
        (5, 1), # event at day 5
        (10, 0), # censored at day 10
        (15, 1), # event at day 15
        (20, 1) # event at day 20
    ]
    km_curve = clin_simulator.calculate_kaplan_meier(events)
    # Expected survival probabilities:
    # Day 5: 3 remaining, 1 event -> 3/4 = 0.75
    # Day 10: 3 remaining, 0 event (censored) -> 0.75 (step included, no probability change)
    # Day 15: 2 remaining, 1 event -> 0.75 * (1/2) = 0.375
    # Day 20: 1 remaining, 1 event -> 0.375 * 0 = 0.0
    km_passed = len(km_curve) == 4 and km_curve[0]["survival_probability"] == 0.75 and km_curve[2]["survival_probability"] == 0.375
    log_result("Kaplan-Meier Estimator", km_passed, f"KM curves: {[{'time': c['time'], 'prob': c['survival_probability']} for c in km_curve]}")

    # ----------------------------------------------------------------------
    # TEST 3: Self-Upgrading Regulatory Compliance Verification
    # ----------------------------------------------------------------------
    print("\n--- Testing Chapter 3: Self-Upgrading Compliance Parser ---")
    compliance_compiler = RegulatoryVerificationCompiler()
    
    # 3.1 Test parsing of mock FDA draft guidance text
    mock_guidance = """
    # FDA Draft Guidance for Continuous Blend Sourcing 2026
    Due to safety considerations in active compound blend rates:
    - LIMIT: residual_ethanol < 5000.0
    - LIMIT: dissolution_rate >= 92.5
    All manufacturers must validate these parameters prior to RTRT.
    """
    rules = compliance_compiler.parse_guidance_rules(mock_guidance)
    log_result("Regulatory Rule Parser", "residual_ethanol" in rules and "dissolution_rate" in rules, f"Parsed Rules: {rules}")
    
    # 3.2 Test verification of current system parameters
    system_params = {
        "residual_ethanol": 4200.0,  # Complies (< 5000)
        "dissolution_rate": 94.2,     # Complies (>= 92.5)
        "bioreactor_temp": 37.0
    }
    passed_check, failures = compliance_compiler.verify_parameters(system_params, rules)
    log_result("Parameter Compliance Check", passed_check == True and len(failures) == 0, f"Verifying system parameters. Passed: {passed_check}")
    
    # 3.3 Test compliance failure detection
    bad_params = {
        "residual_ethanol": 5500.0,  # Fails (> 5000)
        "dissolution_rate": 90.1      # Fails (< 92.5)
    }
    failed_check, bad_failures = compliance_compiler.verify_parameters(bad_params, rules)
    log_result("Compliance Failure Isolation", failed_check == False and len(bad_failures) == 2, f"Verifying bad parameters. Passed: {failed_check}, Failures logged: {len(bad_failures)}")

    # 3.4 Compile the final GxP Validation Report file
    report_path = "pharmvers_core/validation_report.txt"
    report = compliance_compiler.compile_gxp_validation_report(
        target_filepath=report_path,
        app_name="PHARMVERS COGNITIVE CORE v1.0",
        system_params=system_params,
        parsed_rules=rules,
        test_results=test_suite
    )
    report_created = os.path.exists(report_path)
    log_result("GxP Report Generation", report_created, f"Validation report compiled at: {report_path}")
    
    print("\n======================================================================")
    print("VERIFICATION SUITE COMPLETED")
    print(f"Total Tests Run: {test_suite['total']} | Passed: {test_suite['passed']} | Failed: {test_suite['failed']}")
    print(f"Overall Result: {'SUCCESS' if test_suite['success'] else 'FAILURE'}")
    print("======================================================================")

if __name__ == "__main__":
    run_all_tests()
