# Changelog

All notable changes to PHARMVERS AIOS will be documented in this file.
Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) · [Semantic Versioning](https://semver.org/).

---

## [1.0.0] - 2026-07-22 — Initial Public Release

### Added

#### Core Mathematical Engines (`pharmvers_core/`)
- `rtrt_engine.py`: Closed-loop PID feeder rate controller and 2D Hotelling's T² multivariate batch release validator.
- `clinops_engine.py`: Nearest-Neighbor Euclidean propensity score patient matching and Kaplan-Meier survival curve estimator.
- `compliance_compiler.py`: Regex-based FDA/EMA regulatory guidance text parser and autonomous GxP IQ/OQ/PQ report compiler.
- `validation_report.txt`: Autonomously generated and cryptographically signed compliance audit log output.

#### Verification Suite
- `run_tests.py`: 11 unit tests covering all three core engines. All 11 pass on initial release. Zero external dependencies required.

#### Web Control Tower (`demo_website/`)
- Dual-mode dashboard: Manufacturing (RTRT) view and Clinical Trials (SCA) view.
- Live Chart.js visualizations: blend assay uniformity timeline and Hotelling T² quality bars.
- Kaplan-Meier step-function survival curves comparing Active Treatment vs. Synthetic Control Arm.
- Business ROI scoreboard: displays financial impact, time saved, and compliance state per scenario.
- "Why it Matters" executive explainer text panel, updating dynamically with each injected scenario.
- Live autonomous GxP validation report compiler with real-time cryptographic SHA-256 hash signature.

#### Repository Infrastructure
- `README.md`: Professional landing page with architecture diagrams, math equations, quick-start guide, and business pitch matrix.
- `LICENSE`: MIT License.
- `.gitignore`: Excludes Python bytecode, macOS metadata, and log files.
- `.github/workflows/ci.yml`: GitHub Actions CI that runs all 11 tests on every push and uploads the GxP validation report as a build artifact.
- `.github/ISSUE_TEMPLATE/bug_report.md`: Structured bug reporting form.
- `.github/ISSUE_TEMPLATE/feature_request.md`: Feature request form with regulatory context field.
- `.github/PULL_REQUEST_TEMPLATE.md`: PR checklist requiring test pass + GxP impact assessment.
- `CONTRIBUTING.md`: Developer onboarding guide with zero-dependency coding standards.

### Removed
- `ios_app/` directory: SwiftUI templates removed. Platform scope narrowed to Python + Web.
- `n8n_workflows/` directory: Automation workflow JSONs removed. Not part of the core technology stack.
