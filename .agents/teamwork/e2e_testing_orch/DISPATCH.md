# Dispatch: E2E Testing Track Orchestrator

- Working Directory: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\e2e_testing_orch
- Parent Conversation ID: ed41e1b9-d5a2-4203-ba58-c83ae4e2cef1
- Original Request: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\ORIGINAL_REQUEST.md
- Project Scope: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\orchestrator_1\PROJECT.md

## Scope & Deliverables
You are the Orchestrator for the E2E Testing Track. You design and implement the requirement-driven, opaque-box E2E test suite.
Read ORIGINAL_REQUEST.md, AGENTS.md, and PROJECT.md carefully.

### Responsibilities:
1. **Design `TEST_INFRA.md`**:
   - Establish the test philosophy: opaque-box, requirement-driven, exercising the final product as an end user would.
   - Map all features from `PROJECT.md § Feature Inventory` across the 4 test tiers:
     - **Tier 1: Feature Coverage** (>=5 test cases per feature covering isolated happy-path scenarios).
     - **Tier 2: Boundary & Corner Cases** (>=5 test cases per feature covering 32-page limits, 8.625x11.25 in bleed mediabox, 5197x3375 px cover spread, spine text suppression <79 pages, barcode safe area 2.0x1.2 in with 0.5 in clearance, lineart binary purity 0/255, safe margins).
     - **Tier 3: Cross-Feature Combinations** (pairwise coverage: cover 4x3 back grid embedding authentic front covers, interior subject sequence matching manifest, brand governance across all components).
     - **Tier 4: Real-World Application Scenarios** (end-to-end multi-volume generation, preflight verification, KDP submission readiness).
2. **Implement Test Suite**:
   - Place test cases in `tests/e2e/` (or dedicated test files).
   - Ensure tests use `.venv\Scripts\python.exe` and standard Python libraries (`pypdf`, `PIL`, `json`, `re`, `unittest`).
3. **Publish `TEST_READY.md`**:
   - Once all test suites and runners are built and verified, create `TEST_READY.md` at project root (`d:\pivot-edu-kdp\pivot-digital-edu-kdp\TEST_READY.md`) summarizing the test runner command and tier counts.
4. Deliver your handoff report to `.agents/teamwork/e2e_testing_orch/handoff.md` and send completion message to parent.

