"""
Unified E2E Test Suite Runner for The Pivot Kids: Copy to Color publishing pipeline.
Executes all 4 tiers of end-to-end tests:
- Tier 1: Feature Coverage (Features 1-15)
- Tier 2: Boundary & Corner Cases
- Tier 3: Cross-Feature Combinations
- Tier 4: Real-World Workload Scenarios
"""

from __future__ import annotations

import sys
import time
import unittest
from pathlib import Path

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tests.e2e.test_tier1_features import TestTier1Features
from tests.e2e.test_tier2_boundaries import TestTier2Boundaries
from tests.e2e.test_tier3_cross_feature import TestTier3CrossFeature
from tests.e2e.test_tier4_workloads import TestTier4Workloads


def run_e2e_suite() -> int:
    """Run all 4 tiers of E2E tests and report structured summary."""
    print("=" * 80)
    print("THE PIVOT KIDS: COPY TO COLOR — 4-TIER E2E TEST SUITE RUNNER")
    print("=" * 80)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Load tiers in order
    tier1 = loader.loadTestsFromTestCase(TestTier1Features)
    tier2 = loader.loadTestsFromTestCase(TestTier2Boundaries)
    tier3 = loader.loadTestsFromTestCase(TestTier3CrossFeature)
    tier4 = loader.loadTestsFromTestCase(TestTier4Workloads)

    suite.addTests(tier1)
    suite.addTests(tier2)
    suite.addTests(tier3)
    suite.addTests(tier4)

    total_tests = suite.countTestCases()
    print(f"Discovered {total_tests} test cases across 4 tiers:")
    print(f"  - Tier 1 (Feature Coverage):       {tier1.countTestCases()} tests")
    print(f"  - Tier 2 (Boundary & Corner):      {tier2.countTestCases()} tests")
    print(f"  - Tier 3 (Cross-Feature):          {tier3.countTestCases()} tests")
    print(f"  - Tier 4 (Workload Scenarios):     {tier4.countTestCases()} tests")
    print("-" * 80)

    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    elapsed = time.time() - start_time

    print("=" * 80)
    print("E2E TEST RUN SUMMARY")
    print("=" * 80)
    print(f"Total Tests Run: {result.testsRun}")
    print(f"Passed:          {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
    print(f"Failures:        {len(result.failures)}")
    print(f"Errors:          {len(result.errors)}")
    print(f"Skipped:         {len(result.skipped)}")
    print(f"Elapsed Time:    {elapsed:.2f}s")
    print("=" * 80)

    if result.wasSuccessful():
        print("[SUCCESS] All active E2E tests passed successfully.")
        return 0
    else:
        print("[FAILURE] Some E2E tests failed or encountered errors.")
        return 1


if __name__ == "__main__":
    sys.exit(run_e2e_suite())
