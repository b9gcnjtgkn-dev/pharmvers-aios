# Changelog

All notable changes to PHARMVERS AIOS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-07-22

### Added
- **Core Mathematical Engines** (`pharmvers_core/`):
  - `rtrt_engine.py`: Closed-loop PID feeder rate controller and 2D Hotelling's T² multivariate batch release checker.
  - `clinops_engine.py`: Nearest-Neighbor Euclidean propensity score matching and Kaplan-Meier survival curve estimator.
  - `compliance_compiler.py`: Regex-based regulatory guidance parser and autonomous GxP IQ/OQ/PQ report compiler.
  - `validation_report.txt`: Autonomously generated and cryptographically signed compliance audit log.
- **Verification Test Suite** (`run_tests.py`): 11 unit tests covering all core engine modules. All 11 pass on initial release.
- **Interactive Web Control Tower** (`demo_website/`):
  - Dual-mode dashboard switching between Manufacturing (RTRT) and Clinical Trials (SCA) views.
  - Real-time Chart.js visualizations for blend assay uniformity and Hotelling T² quality bars.
  - Kaplan-Meier survival curve plots comparing Active Treatment vs. Synthetic Control Arm.
  - Business ROI scoreboard displaying financial impact, time saved, and compliance state.
  - "Why it Matters" executive explainer text, updating dynamically with each scenario.
  - Live autonomous GxP validation report compiler with cryptographic SHA-256 hash signature.
- **SwiftUI iOS Application Templates** (`ios_app/`): Prototype views for the mobile executive cockpit.
- **Strategic Blueprint** (`PHARMVERS_AIOS_BLUEPRINT.md`): Full system architecture, pricing model, and pitch framework.
- **Repository Infrastructure**:
  - `README.md` with badges, directory map, and run instructions.
  - `LICENSE` (MIT).
  - `.gitignore` for Python, macOS, and Node.js artifacts.
  - GitHub Actions CI Workflow (`.github/workflows/ci.yml`).
  - Issue and Pull Request Templates.
  - `CONTRIBUTING.md` guide.
