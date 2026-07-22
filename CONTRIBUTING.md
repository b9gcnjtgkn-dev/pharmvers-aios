# Contributing to PHARMVERS AIOS

Thank you for your interest in contributing to PHARMVERS AIOS. This is a proprietary pharmaceutical intelligence platform. Please read the following guidelines before submitting any contributions.

---

## Code of Conduct

All contributors are expected to maintain a professional, respectful, and constructive environment. Harassment, discrimination, or unprofessional conduct will not be tolerated.

---

## How to Contribute

### Reporting Bugs
1. Open a **GitHub Issue** using the Bug Report template.
2. Provide a **clear, reproducible description** of the issue.
3. Include the **Python version** (`python3 --version`), **OS version**, and the **full error output** from your terminal.

### Requesting Features
1. Open a **GitHub Issue** using the Feature Request template.
2. Describe the **business problem** the feature solves and cite relevant **FDA, ICH, or GxP guidelines** if applicable.

### Submitting Pull Requests
1. **Fork** the repository and create your branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Write or update tests** inside `run_tests.py` for any new mathematical engine functionality.
3. Ensure all **11 existing tests pass** before submitting:
   ```bash
   python3 run_tests.py
   ```
4. Submit a Pull Request with a clear description of what was changed and why.

---

## Development Setup

```bash
# Clone the repository
git clone https://github.com/b9gcnjtgkn-dev/pharmvers-aios.git
cd pharmvers-aios

# Run the test suite (no external dependencies required)
python3 run_tests.py

# Launch the web demo
python3 -m http.server 8000
# Open: http://localhost:8000/demo_website/
```

---

## Coding Standards

- **Zero External Dependencies:** Core engine files (`pharmvers_core/`) must remain executable using only the Python standard library (`math`, `re`, `datetime`, etc.).
- **GxP Auditability:** All new functions that modify system parameters must write entries to the validation log via `ComplianceCompiler`.
- **Clear Naming:** Use full, descriptive variable names (e.g., `hotelling_t2_distance` not `d`).
